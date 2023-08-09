import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

# Would be better to use tensorflow instead of sklearn
input_data = pd.read_csv("data/cleaned.csv")

input_data = input_data.drop(columns=["seconds"])


n_clusters = 4
kmeans = KMeans(n_clusters=n_clusters, random_state=0)


data = input_data[3552400:3552700]
kmeans.fit(data)

cluster_labels = kmeans.labels_

data["Cluster"] = cluster_labels



plt.figure(figsize=(10, 6))

for cluster in range(n_clusters):
    cluster_data = data[data["Cluster"] == cluster]
    plt.scatter(cluster_data.index, cluster_data["Cluster"], label=f"Cluster {cluster}", s=1)


plt.xlabel("Time (seconds)")
plt.ylabel("Cluster")
plt.title("Cluster Distribution Over Time")
plt.legend()
plt.show()




