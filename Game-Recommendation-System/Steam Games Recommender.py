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

def data_prep():
    #Load the dataset
    headers = ['user_id', 'game', 'behavior', 'play_time', '0']
    steam_data = pd.read_csv('steam-200k.csv', sep=',', names=headers)
    steam_data = steam_data.drop(['0'],axis=1)
    steam_data = steam_data.sort_values(by=['behavior'])
    # steam_data.set_index(range(0,steam_data.shape[0],1))
    steam_data.reset_index(drop=True, inplace=True)
    steam_data.head()
    steam_data_play = steam_data.loc[steam_data.behavior=='play']

    steam_data_purchase = steam_data.loc[steam_data.behavior=='purchase']
    games_names = steam_data_purchase['game'].unique().tolist()
    unique_ids = steam_data_purchase['user_id'].unique().tolist()
    user_id_groups = steam_data_purchase.groupby("user_id")
    user_id_groups_play = steam_data_play.groupby("user_id")
    beautiful_df = pd.DataFrame(0, index=unique_ids, columns=games_names)
    try:
        with open('beautiful_df.pkl','rb') as f:
            beautiful_df = pickle.load(f)
    except:
        for i in tqdm(range(0, len(unique_ids),1)):
            user_id = unique_ids[i]
            user_group = user_id_groups.get_group(user_id)
            for game_name in user_group['game']:
                beautiful_df[game_name][user_id] = 1
        with open('beautiful_df.pkl', 'wb') as f:
            pickle.dump(beautiful_df, f)    

    # Some Statistics
    average_games_played = np.mean(beautiful_df.sum(axis=1).values)
    mean_hours_played = steam_data_play['play_time'].mean()

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
            test_user_games = np.unique(user_id_groups.get_group(test_user_id)['game'].values)
            if test_user_games.shape[0] > 10:
                if test_user_id not in test_users:
                    test_users.append(test_user_id)
                    n+=1
                    pbar.update(1)
        pbar.close()
        with open('test_users.pkl', 'wb') as f:
            pickle.dump(test_users, f)


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



def redecompose(sparsed_s,sparsed_u,sparsed_vt):
    all_user_predicted_purchases = np.dot(np.dot(sparsed_u, sparsed_s), sparsed_vt)
    predictions = pd.DataFrame(all_user_predicted_purchases, columns = beautiful_df.columns, index = beautiful_df.index)
    return predictions





def recommend_games(user_id, num_recommendations, predictions, user_id_groups):
    
    # Get and sort the user's predictions
    sorted_user_predictions = predictions.loc[user_id].sort_values(ascending=False)
    
    # Get list of purchased games
    purchased_games = user_id_groups.get_group(user_id)['game'].unique().tolist()
    
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


#Load the dataset

    
headers = ['user_id', 'game', 'behavior', 'play_time', '0']
#pd.read_csv(csvFilePath, encoding='utf-8-sig', sep='\s*,\s*', engine='python')


steam_data = pd.read_csv('steam-200k.csv', encoding='utf-8-sig', sep=',', engine='python', names=headers)
steam_data.columns = steam_data.columns.str.strip()

steam_data = steam_data.drop(['0'],axis=1)
steam_data = steam_data.sort_values(by=['behavior'])
# steam_data.set_index(range(0,steam_data.shape[0],1))
steam_data.reset_index(drop=True, inplace=True)
steam_data.head()
steam_data_play = steam_data.loc[steam_data.behavior=='play']

steam_data_purchase = steam_data.loc[steam_data.behavior=='purchase']
steam_data_purchase.columns = steam_data_purchase.columns.str.strip()
steam_data_play.columns = steam_data_play.columns.str.strip()
games_names = steam_data_purchase['game'].unique().tolist()
unique_ids = steam_data_purchase['user_id'].unique().tolist()
user_id_groups = steam_data_purchase.groupby("user_id")
#user_id_groups_play =steam_data_play.groupby("user_id")
beautiful_df = pd.DataFrame(0, index=unique_ids, columns=games_names)
try:
    with open('beautiful_df.pkl','rb') as f:
        beautiful_df = pickle.load(f)
except:
    for i in tqdm(range(0, len(unique_ids),1)):
        user_id = unique_ids[i]
        user_group = user_id_groups.get_group(user_id)
        for game_name in user_group['game']:
            beautiful_df[game_name][user_id] = 1
    with open('beautiful_df.pkl', 'wb') as f:
        pickle.dump(beautiful_df, f)    

# Some Statistics
average_games_played = np.mean(beautiful_df.sum(axis=1).values)
mean_hours_played = steam_data_play['play_time'].mean()

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
        test_user_games = np.unique(user_id_groups.get_group(test_user_id)['game'].values)
        if test_user_games.shape[0] > 10:
            if test_user_id not in test_users:
                test_users.append(test_user_id)
                n+=1
                pbar.update(1)
    pbar.close()
    with open('test_users.pkl', 'wb') as f:
        pickle.dump(test_users, f)
games_altered = alterData(beautiful_df, test_users, 2, user_id_groups)
matrix = np.array(beautiful_df.values)

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
sparsed_s, sparsed_vt, sparsed_u = sparsify(s,u,vt)
predictions = redecompose(sparsed_s,sparsed_u,sparsed_vt)
recommendations1 = recommend_games(128470551, 5, predictions, user_id_groups)
recommendations2 = recommend_games(43955374, 5, predictions, user_id_groups)
recommendations3 = recommend_games(32126281, 5, predictions, user_id_groups)
recommendations4 = recommend_games(11731710, 5, predictions, user_id_groups)


#recommendations = recommend_games(43955374, 5, predictions)#, user_id_groups)

print('We are recommending following game: '+ (", ").join(recommendations1))
print('We are recommending following game: '+ (", ").join(recommendations2))
print('We are recommending following game: '+ (", ").join(recommendations3))
print('We are recommending following game: '+ (", ").join(recommendations4))





