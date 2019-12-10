import numpy as np
import pandas as pd
import math
# import seaborn as sns
# import matplotlib.pyplot as plt


# mysql -pdpi -udpi -h 129.236.209.244

data = pd.read_csv('dummy1.csv')
#print(data)
myid = 16
myrating = data[data['uid'] == myid]['init_rating'].tolist()
#print(myrating)

data = data[['uid', 'eid', 'init_rating']]


from surprise import Reader, Dataset
reader = Reader()
data = Dataset.load_from_df(data[['uid', 'eid', 'init_rating']], reader)

from surprise.model_selection import train_test_split
trainset, testset = train_test_split(data, test_size=0.2)


from surprise import SVD, accuracy
algo = SVD()
output = algo.fit(trainset)
predictions = algo.test(testset)

from surprise import accuracy
accuracy.rmse(predictions)



rateList = []
for i in range (1,11):
    pred = algo.predict(uid = myid, iid = i)
    score = pred.est + math.sqrt(myrating[i-1])
    rateList.append(score)
copyList = rateList.copy()
rateList.sort(reverse = True)

#print(copyList)
#print(rateList)


rec = []
for i in range (0,4):
    rec.append(copyList.index(rateList[i])+1)
#print(rec)




# https://blog.cambridgespark.com/tutorial-practical-introduction-to-recommender-systems-dbe22848392b
# https://towardsdatascience.com/building-and-testing-recommender-systems-with-surprise-step-by-step-d4ba702ef80b
# https://medium.com/hacktive-devs/recommender-system-made-easy-with-scikit-surprise-569cbb689824
