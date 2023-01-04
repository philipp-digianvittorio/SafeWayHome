import os
import pandas as pd
import numpy as np

base_dir = r"C:/users/philipp/documents/studium/master/4. semester/ds project/safewayhome/model_training/data"

efs = pd.read_csv(os.path.join(base_dir, "efs_list.csv"))
efs = efs.iloc[:,[0,2]]

raw = pd.read_csv(os.path.join(base_dir, "export.txt"), delimiter = "\t")

# -- evaluate mean-squared-error
answers = raw.iloc[:,11:988].replace(-77, np.nan)

scores = (answers.replace(np.nan, 0.0).values).round(0)

mean_score = (answers.mean().values.repeat(len(answers)).reshape(scores.shape[1], scores.shape[0]).transpose()).round(0)
mean_score[scores == 0.0] = 0.0

mean_sq_err = ((mean_score - scores)**2).sum(axis=1)/40
print(mean_sq_err.min())
print(mean_sq_err.mean())

import matplotlib.pyplot as plt

fig = plt.figure(figsize=(12,8))
plt.plot(sorted(mean_sq_err), label=r"\textbf{human MSE}", color="steelblue", linewidth=2)
plt.rc('text', usetex=True)
plt.rc('font', family='serif')
plt.hlines(y=0.31, xmin=0, xmax=1277, colors="darkorange", label=r"\textbf{model MSE}", linewidth=2)
plt.legend()
plt.title(r"\textbf{Mean-squared-error for image classification}")
plt.yticks([x/2 for x in list(range(0,10))])
plt.tight_layout()
plt.show()
fig.savefig("image_classification_mse.pdf", bbox_inches='tight')

model_performance = len(mean_sq_err[mean_sq_err > 0.31])/len(mean_sq_err)



# -- cluster image scores for model training

raw = pd.read_csv(os.path.join(base_dir, "export.txt"), delimiter = "\t")

answers = raw.iloc[:,11:988].replace(-77, np.nan)
norm_scores = (answers - answers.mean()) / answers.std()
l = list()
for idx in norm_scores.index:
    l.append([x for x in norm_scores.iloc[idx, :].values.tolist() if not np.isnan(x)])

arr = np.array(l).mean(axis=1).reshape(-1, 1)


from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

import matplotlib.pyplot as plt
import seaborn as sns
import pickle


# -- class for k-means calculation
class K_Means():

    def __init__(self, X, n_clusters, random_state, normalize_X=False):

        if normalize_X == True:
            self.X = StandardScaler().fit_transform(X)
        else:
            self.X = X

        self.n_clusters = n_clusters
        self.random_state = random_state
        self.model = KMeans(n_clusters=self.n_clusters, random_state=self.random_state).fit(self.X)
        self.y_pred = self.model.predict(self.X)

    def pca_plot(self, y=None):
        self.pca = PCA(n_components=2, random_state=self.random_state).fit(self.X)
        self.x_dim = self.pca.transform(self.X)[:, 0]
        self.y_dim = self.pca.transform(self.X)[:, 1]

        if y is None:
            fig = plt.figure()
            sns.scatterplot(x=self.x_dim, y=self.y_dim, hue=self.y_pred)
        else:
            fig, ax = plt.subplots(1, 2)

            plt.subplot(1, 2, 1)
            sns.scatterplot(x=self.x_dim, y=self.y_dim, hue=self.y_pred)
            # ax[0].set_title("Predicted Clusters")

            plt.subplot(1, 2, 2)
            sns.scatterplot(x=self.x_dim, y=self.y_dim, hue=y)
            # ax[1].set_title("True Clusters")
        plt.show()


# -- cluster normalized scores
km = K_Means(X=arr, n_clusters=5, random_state=42, normalize_X=False)

fig = plt.figure()
sns.scatterplot(y=km.X[:, 0], x=range(len(km.X)), hue=km.y_pred)

pickle.dump(km.model, open(os.path.join(base_dir, "kmeans_model.pkl"), "wb"))
#km_model = pickle.load(open(os.path.join(base_dir, "kmeans_model.pkl"), "rb"))

# -- create dataframes for each score class for model training
answers = raw.iloc[:,8:988]
answers = answers.replace(-77, np.nan)
answers = answers.rename(columns = {'v_51': 'gender', 'v_56': 'Frankfurt','v_67': 'Germany'})
answers["class"] = km.y_pred
answers["class"] = answers["class"].map({0: "negative",
                                         1: "very_positive",
                                         2: "positive",
                                         3: "very_negative",
                                         4: "neutral"})


for cls in answers["class"].unique():
    df = answers[answers["class"]==cls].reset_index(drop=True)

    ratings = pd.DataFrame(columns =['List-ID','image_score','n_ratings','Strassenname'])
    ratings['image_score'] = pd.DataFrame(df.iloc[:,3:988].mean(axis=0))
    ratings['n_ratings'] = pd.DataFrame(df.iloc[:,3:988].count(axis=0))
    ratings['List-ID'] = range(1, 1 + len(ratings))
    ratings = pd.merge(ratings, efs, on='List-ID')
    ratings['Strassenname'] = ratings['Name'].str.replace('.jpeg', '')
    ratings = ratings[~ratings["image_score"].isnull()].reset_index(drop=True)
    print(ratings.shape)
    ratings.to_csv(os.path.join(base_dir, f"ratings/{cls}.csv"), index=False)






