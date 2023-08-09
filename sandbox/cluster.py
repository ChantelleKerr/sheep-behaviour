import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

input_data = pd.read_csv("data/cleaned.csv")

input_data = input_data.drop(columns=["seconds"])
print("1")

n_clusters = 4
kmeans = KMeans(n_clusters=n_clusters, random_state=0)
print("2")

data = input_data[3552400:3552700]
kmeans.fit(data)
print("3")

cluster_labels = kmeans.labels_
print("4")

data["Cluster"] = cluster_labels
print("5")



plt.figure(figsize=(10, 6))

for cluster in range(n_clusters):
    cluster_data = data[data["Cluster"] == cluster]
    plt.scatter(cluster_data.index, cluster_data["Cluster"], label=f"Cluster {cluster}", s=1)


plt.xlabel("Time (seconds)")
plt.ylabel("Cluster")
plt.title("Cluster Distribution Over Time")
plt.legend()
plt.show()

# # Create an interactive plot using Plotly
# fig = px.scatter(data, x=data.index / 25, y="Cluster", color="Cluster",
#                  labels={"x": "Time (seconds)", "y": "Cluster"},
#                  title="Cluster Distribution Over Time",
#                  range_x=[data.index[0] / 25, data.index[-1] / 25],
#                  animation_frame=data.index / 25,
#                  animation_group="Cluster")

# # Show the plot
# fig.show()



