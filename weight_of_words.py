import os
import pickle
import pandas as pd
import matplotlib.pyplot as plt

with open("models/ridge_model.pickle", "rb") as f:
    model = pickle.load(f)

with open("models/vectorizer.pickle", "rb") as f:
    vectorizer = pickle.load(f)

df = pd.DataFrame(columns=['term', 'weight'])

df['term'] = [term for term in vectorizer.get_feature_names()]
df['weight'] = [x for x in model.coef_]

df = df.sort_values(by='weight', ascending=False)

try:
    os.mkdir("result")
except:
    pass

# 保存。
df.to_csv("result/coefficients.csv", index=False)
