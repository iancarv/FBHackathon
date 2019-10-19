#!/usr/bin/env python
# coding: utf-8

# # Game Recommendation System 

# In[101]:


#Importin packages
import csv
import pandas as pd
import numpy as np
import matplotlib as plt
from tqdm import tqdm
import pickle
import random 


# ## 1. Data Preparation

# In[102]:


#Load the dataset
headers = ['user_id', 'game', 'behavior', 'play_time', '0']
steam_data = pd.read_csv('steam-200k.csv', sep=',', names=headers)

steam_data = steam_data.drop(['0'],axis=1)

steam_data = steam_data.sort_values(by=['behavior'])
# steam_data.set_index(range(0,steam_data.shape[0],1))
steam_data.head()


# In[103]:


steam_data.shape


# In[104]:


steam_data.reset_index(drop=True, inplace=True)
steam_data.head()


# In[105]:


steam_data_play = steam_data.loc[steam_data.behavior=='play']

steam_data_purchase = steam_data.loc[steam_data.behavior=='purchase']
games_names = steam_data_purchase['game'].unique().tolist()
unique_ids = steam_data_purchase['user_id'].unique().tolist()


# In[106]:


user_id_groups = steam_data_purchase.groupby("user_id")
user_id_groups_play = steam_data_play.groupby("user_id")


# In[107]:


print(user_id_groups_play.get_group(43955374))


# In[108]:


beautiful_df = pd.DataFrame(0, index=unique_ids, columns=games_names)


# In[109]:


beautiful_df.head(50)


# In[110]:


try:
    with open('beautiful_df.pkl','rb') as f:
        beautiful_df = pickle.load(f)
except:
    for i in tqdm(range(0, len(unique_ids),1)):
        user_id = unique_ids[i]
        user_group = user_id_groups_play.get_group(user_id)
        for game_name in user_group['game']:
            beautiful_df[game_name][user_id] = 1
    with open('beautiful_df.pkl', 'wb') as f:
        pickle.dump(beautiful_df, f)    


# In[111]:


# Some Statistics
average_games_played = np.mean(beautiful_df.sum(axis=1).values)
print(average_games_played)

mean_hours_played = steam_data_play['play_time'].mean()
print(mean_hours_played)


# ####  Selecting test sets

# In[112]:


try:
    with open('test_users.pkl','rb') as f:
        test_users = pickle.load(f)
except:
    n = 0
    test_users = []
    num_test_users = 1000
    pbar = tqdm(total = num_test_users)
    while(n < num_test_users):
        sample = np.random.choice(len(unique_ids),1, replace=False)
        test_user_id = beautiful_df.index[sample][0]
        test_user_games = np.unique(user_id_groups_play.get_group(test_user_id)['game'].values)
        if test_user_games.shape[0] > 10:
            if test_user_id not in test_users:
                test_users.append(test_user_id)
                n+=1
                pbar.update(1)
    pbar.close()
    with open('test_users.pkl', 'wb') as f:
        pickle.dump(test_users, f)


# In[113]:


assert len(test_users)==np.unique(test_users).shape[0] # Check for duplicates


# In[114]:


def alterData(data, test_users, hidden, user_id_groups):
    games_altered = []
    for i in tqdm(range(0, len(test_users),1)):
        test_user_id = test_users[i]
        test_games_purchased = np.unique(user_id_groups.get_group(test_user_id)['game'].values)
        picked_games = np.random.choice(len(test_games_purchased), min(len(test_games_purchased),hidden), replace=False)
        games = []
        for game in picked_games:
            if data[test_games_purchased[game]][test_user_id] == 1:
                data[test_games_purchased[game]][test_user_id] = 0
                games.append(test_games_purchased[game])
            else:
                print(data[test_games_purchased[game]][test_user_id])
                print(test_games_purchased[game],test_user_id, picked_games)
                raise Exception('This game should be purchased. Try recomputing beautiful_df')
        games_altered.append(games)
    return games_altered 


# In[115]:


games_altered = alterData(beautiful_df, test_users, 2, user_id_groups)


# In[116]:


matrix = np.array(beautiful_df.values)


# ## 2. Matrix Complition

# In[117]:


# Obtaining SVD values of the user-item matrix
try:
    with open('s.pkl','rb') as f:
        s = pickle.load(f)
    with open('u.pkl','rb') as f:
        u = pickle.load(f)
    with open('vt.pkl','rb') as f:
        vt = pickle.load(f)
except:
    u, s, vt = np.linalg.svd(matrix, full_matrices=False)
    with open('s.pkl', 'wb') as f:
        pickle.dump(s, f)
    with open('u.pkl', 'wb') as f:
        pickle.dump(u, f)
    with open('vt.pkl', 'wb') as f:
        pickle.dump(vt, f)


# #### Sparsifying thorugh thresholding

# In[118]:


def sparsify(s,u,vt):
    thresholdCheck = list(np.around(s,0) < 101)
    thresholdIndex = thresholdCheck.index(True)
    print(thresholdIndex)
    sparsed_s = np.diag(s[:thresholdIndex])
    sparsed_vt = vt[:thresholdIndex,:]
    sparsed_u = u [:,:thresholdIndex]
    return sparsed_s, sparsed_vt, sparsed_u


# In[119]:


sparsed_s, sparsed_vt, sparsed_u = sparsify(s,u,vt)


# In[120]:


def redecompose(sparsed_s,sparsed_u,sparsed_vt):
    all_user_predicted_purchases = np.dot(np.dot(sparsed_u, sparsed_s), sparsed_vt)
    predictions = pd.DataFrame(all_user_predicted_purchases, columns = beautiful_df.columns, index = beautiful_df.index)
    return predictions


# In[121]:


predictions = redecompose(sparsed_s,sparsed_u,sparsed_vt)


# In[122]:


predictions


# ## 3. Predictions

# In[123]:


def recommend_games(user_id, num_recommendations, predictions, user_id_groups_play):
    
    # Get and sort the user's predictions
    sorted_user_predictions = predictions.loc[user_id].sort_values(ascending=False)
    
    # Get list of purchased games
    purchased_games = user_id_groups_play.get_group(user_id)['game'].unique().tolist()
    
    # Recommend the highest predicted rating movies that the user hasn't seen yet.
    count_games = 0 
    recommendations = []
    for i in range(0,sorted_user_predictions.shape[0],1):
        predicted_game_score = sorted_user_predictions[i]
        predicted_game_name = sorted_user_predictions.index[i]
        if predicted_game_name not in purchased_games:
            count_games+=1
            recommendations.append(predicted_game_name)
        if count_games >= num_recommendations:
            break

    return recommendations


# In[125]:


recommendations = recommend_games(43955374, 5, predictions, user_id_groups)
#recommendations = recommend_games(43955374, 5, predictions)#, user_id_groups)

print('We are recommending following game: '+ (", ").join(recommendations))


# ## 4. Testing
# #### Compute Recall

# In[ ]:


assert len(test_users)==len(games_altered)


# In[ ]:


def getRecall(games_altered, test_users, data, num_recommendations, predictions, user_id_groups_play):
    recalls = []
    for i in tqdm(range(0, len(test_users),1)):
        matches = 0
        test_user_id = test_users[i]
        recommendations = recommend_games(user_id, num_recommendations, predictions, user_id_groups_play)
#         print(games_altered[i],recommendations)
#         break
        for game in games_altered[i]:
            if game in recommendations:
                matches+=1
        recall = matches/len(games_altered[i])*100
        recalls.append(recall)
    return np.mean(recalls)


# In[ ]:


print(getRecall(games_altered, test_users, beautiful_df, 100, predictions,user_id_groups))


# In[ ]:





# In[ ]:

if __name__ == '__main__':
    recommend_games(43955374, 5, predictions, user_id_groups)


