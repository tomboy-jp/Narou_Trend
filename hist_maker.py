import os
import exe_ml
import matplotlib.pyplot as plt

try:
    os.mkdir("result")
except:
    pass

df = exe_ml.read_df()

point = df['point'].value_counts().sort_index()
point.to_csv("result/point_dist.csv")

plt.hist(df['point'].values, bins=100)
plt.savefig("result/point_graph.png")
