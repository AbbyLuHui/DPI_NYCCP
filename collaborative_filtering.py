import numpy as np
import pandas as pd
import math
# import seaborn as sns
# import matplotlib.pyplot as plt


# mysql -pdpi -udpi -h 129.236.209.244

def cofi(evs,myid):
    print(evs)
    data = pd.read_csv('dummy1.csv')
    #print(data)
    myrating = data[data['uid'] == myid]['init_rating'].tolist()
    eventseq = data[data['uid'] == myid]['eid'].tolist()
    #print(eventseq)

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
    for i in range (1,27):
        #print(eventseq[i-1])
        pred = algo.predict(uid = myid, iid = eventseq[i-1])
        # print(pred)
        score = pred.est + 1.2*myrating[i-1]
        rateList.append(score)

    copyList = rateList.copy()    #rating of events 17, 18, 19,...26, 1, 2, 3..,16
    rateList.sort(reverse = True)

    print(copyList)
    #print(rateList)

    ranking = []
    rec = []
    for i in range (0,26):
        curev = eventseq[copyList.index(rateList[i])]
        ranking.append(curev)
        if (curev in evs):
            rec.append(curev)
    print(ranking)
    print(rec)
    if (len(rec) == 0):
        return ranking[0:4]
    return rec[0:4]

 
#evs = [20,21,22,24,25,14]
#cofi(evs,14)


# https://blog.cambridgespark.com/tutorial-practical-introduction-to-recommender-systems-dbe22848392b
# https://towardsdatascience.com/building-and-testing-recommender-systems-with-surprise-step-by-step-d4ba702ef80b
# https://medium.com/hacktive-devs/recommender-system-made-easy-with-scikit-surprise-569cbb689824
