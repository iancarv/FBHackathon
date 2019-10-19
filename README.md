# FBHackathon - giggly - Game Recommendation System

## Problem statement

How can we combat the loss of stimulation and empathy that may occur when children become hospitalized, and how do we ensure that their ties with the social world remain intact during their stay at the hospital?

## Business value 

### Social Good through Entertainment

Children are always asked the classic question: "What do you want to be when you grow up?" The only thing that our society promises children is their future. We continously draw the younger generation's focus towards what they will be capable of when they reach adulthood, and thus nurture their expectations and dreams about how thrilling their future is going to be. What is society obliged to do, then, when a medical obstacle threatens to not only deter, but uproot those dreams?

The struggle of long-term treatment is enough of a burden without the unforeseen stings. Having to place a child outside of the social and psychological community of society, into the confined walls of a hospital room, can have tremendous long-term effects on their wellbeing, personality and worldview. How do we ensure that children stay confident of their own place and importance within society even if they're physically removed from the scene?

This is where the core power of Giggly lies: it draws strength from one of the most basic human desires - the need to feel safe and at home. Crafting that belonging for children who are hospitalized may appear harder, but Giggly is a kid-friendly platform for them to not only bring their hobbies into their temporary living space but also maintain daily interaction with their friends, family and larger online community. Giggly is capable of deciphering the patient's speech - in accordance with its vision to strive to be accessible! - and play content from websites like Netflix, Spotify, Twitch and Disney+, depending on what the kid prefers at that very moment.

Giggly enables child patients across hospitals to keep up with their favorite online trends by enabling them to access platforms, make selections and even comment on live streamings - all from the comfort of their hospital bed. Through implementing Giggly, Facebook will be the catalyst in one of the most crucial periods of affected childrens’ lives. Being at the center of their road to recovery, Facebook will be associated with magically positive memories for years to come. Moreover, this project will launch Facebook to the forefront of the social good revolution, setting a striking example of how giant corporations can and should use their power for good and real human impact.

## System components - Implementation Details
![Technical Architecture Diagram](FBHackathon.png)
1. Messenger Bot
    * Interactions:
        * Text Messages:
            - One of ways of interacting with Messenger platform is by setting webhooks so Facebook requests it whenever a new message is received. Our backend received and uses a set of rules to set the context and decide the appropriate response, whether it's to show a video, send a message to the streaming twitcher.
        * Postback:
            - We use postback to simplify the interaction to a single tap. By showing the available next steps, we make it easier to kids to use our bot. 
    * Voice:
            - In hospital environments, a lot of times children have movement limitations. Adding a voice interface, makes the apple more accessible. Also, everything you do with text can be also done by using the voice.
    * Submiting/Displaying Media:
            - One of Facebook key features is the hability to interact with dinamic media such as videos and music. We leverage the Facebook platform to allow children to see a series of videos curated exclusively for kids. Also, the kid can submit videos and pictures using Facebook AR filters. In the future, when Spark AR reaches open beta for Messenger, exclusive effects could be used 
    * Twitch / WebSockets:
            - Gaming is big with children and many of then follow streamers frequently. By allowing then to interact with Twitcher using their Messenger app is a innovative feature. The kid can load twitch streams for game and it will dinamically show on our website. In the future, we are planning to build even more integrations bringing more content and integrationg with SmartTVs.  
2. Recommendation System (SVD Model): 

3. UI

## Dataset

Steam is the world's most popular PC Gaming hub. With a massive collection that includes everything from AAA blockbusters to small indie titles, great discovery tools can be super valuable for Steam. How can we make them better? This dataset is a list of user behaviors, with columns: user-id, game-title, behavior-name, value. The behaviors included are 'purchase' and 'play'. The value indicates the degree to which the behavior was performed - in the case of 'purchase' the value is always 1, and in the case of 'play' the value represents the number of hours the user has played the game.

https://www.kaggle.com/tamber/steam-video-games

![A peek into the data](game_play.png)
![A peek into the data](data.png)

This dataset is a list of 200,000 user behaviors, with columns: user-id, game-title, behavior-name and play_time.. The behaviors are divided into 'purchase' and 'play', which indicates if the record constitutes to a purchase receipt or user interaction with the game. The play_time feature indicates the degree to which the behavior was performed - in the case of 'purchase' the value is always 1, and in the case of 'play' the value represents the number of hours the user has played the game. There are total 12393 unique user ids and 5155 games. On average Steam purchases 10 games and plays each games at least 48 hours.

The motivation behind using this dataset is twofold.

1. We could access it from Kaggle.
2. Since this datset is about the number of hours of playing particular game and purchase behavior, it can help giggly to recomend videos according to user's most played games.

## Model

We mapped the data to a joint latent factor space of dimensionality d*n, such that the user-item interactions are modeled as inner products in the space. Each user is associated with a vector pu Rd and each item is associated with a vector qiRn. For a given game i, the elements of qi measure the extent to which a game was played by users pu. Similarly, for a given user u, the elements of pu measure the extent of interest the user has in the game (in this case we have a binary value: 1 for purchase, 0 for not purchased). The resulting dot product qiTpu captures the interaction between the user u and the game i. We get an approximation of the user u’s rating of a game i which is denoted by: r^ui= qiTpu (1)

The model closely represents Singular Value Decomposition. At a high level, SVD is an algorithm that decomposes a matrix M into into two unitary matrices (U and Vt) and a diagonal matrix S: M=USVT (2) where M is user-game purchases matrix, U is the basis matrix, S is the diagonal matrix of singular values (essentially weights), and VT is the “features” matrix. U represents how much users “like” each feature and VT represents how relevant each game is to the user. A sparsification technique is then applied to approximate the rank of matrix M, namely the authors utilized thresholding by parameter “k” on the diagonal matrix S to remove not-meaningful representations. Furthermore the authors tuned the parameter “k” to increase or decrease the number of r user-havioral groups. Then authors recomposed M utilizing equation (2) to obtain final recommendation matrix R.
