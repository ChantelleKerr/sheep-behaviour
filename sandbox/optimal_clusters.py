import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

input_data = pd.read_csv("data/cleaned.csv")

input_data = input_data.drop(columns=["seconds"])

data = input_data[3542400:3628800] # select a subset from dataframe


inertia_values = []
# This takes time
for n_clusters in range(1, 10):
    print(n_clusters)
    kmeans = KMeans(n_clusters=n_clusters, random_state=0)
    kmeans.fit(data)
    inertia_values.append(kmeans.inertia_)
    

# Plot the Elbow curve
plt.figure(figsize=(8, 6))
plt.plot(range(1, 20), inertia_values, marker='o')
plt.xlabel("Number of Clusters")
plt.ylabel("Inertia")
plt.title("Elbow Method for Optimal Number of Clusters")
plt.show()