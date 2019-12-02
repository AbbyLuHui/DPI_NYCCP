import numpy as np
import pandas as pd
# import seaborn as sns
# import matplotlib.pyplot as plt


data = pd.read_csv('dummy1.csv')
print(data)

data = data[['uid', 'iid', 'rating']]


from surprise import Reader, Dataset
reader = Reader()
data = Dataset.load_from_df(data[['uid', 'iid', 'rating']], reader)

from surprise.model_selection import train_test_split
trainset, testset = train_test_split(data, test_size=0.25)


from surprise import SVD, accuracy
algo = SVD()
output = algo.fit(trainset)
predictions = algo.test(testset)



from surprise import accuracy
accuracy.rmse(predictions)



pred = algo.predict(uid = '3', iid='10')
score = pred.est
print(score)


# https://blog.cambridgespark.com/tutorial-practical-introduction-to-recommender-systems-dbe22848392b
# https://towardsdatascience.com/building-and-testing-recommender-systems-with-surprise-step-by-step-d4ba702ef80b
# https://medium.com/hacktive-devs/recommender-system-made-easy-with-scikit-surprise-569cbb689824
