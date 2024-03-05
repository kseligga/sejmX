# Importujemy bibliotekę PCA-magic, która implementuje PPCA
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde
from sklearn.decomposition import PCA
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


term=10
votings_df=pd.read_csv("voting_dfX_full.csv")

mps_url = "https://api.sejm.gov.pl/sejm/term"+str(term)+"/MP"
mps = pd.read_json(mps_url)

mps_clubs = mps['club']

# TODO nazwy klubów doklejone mądrzej niż po kolei i liczyć że jest to samo co tam


votings_df.drop(votings_df.columns[:2], axis=1, inplace=True)
votings_df=votings_df.dropna(axis=0, how='all')
#votings_df=votings_df.dropna(axis=1, how='all')
votings_df=votings_df.fillna(0.001)


print(len(votings_df))

print(set(mps_clubs))
mps_clubs.replace(np.nan, 'nan', inplace=True)

# size of dot proportional to square of attendance
sizes=[]
for mp in votings_df.columns:
    percentage = (votings_df[mp] == 0.001).mean() # do poprawy
    sizes.append(((1-percentage)**2)*50)

print(sizes)
votings_df=votings_df.T

pca = PCA(n_components=2)

pca.fit(votings_df)

# Transform to 2D
df_pca = pca.transform(votings_df)

# X
# TODO put this in different file
Xclub_colors = {
    'PiS': 'blue',
    'KO': 'orange',
    'PSL-TD': 'green',
    'Polska2050-TD': 'yellow',
    'Konfederacja': 'navy',
    'Kukiz15': 'black',
    'Lewica': 'red'
}

# IX
IXclub_colors = {
    'PiS': 'blue',
    'KO': 'orange',
    'KP': 'green',
    'Polska2050': 'yellow',
    'Konfederacja': 'navy',
    'Kukiz15': 'black',
    'Lewica': 'red',
    'LD': 'pink',
    'niez.': 'gray',
    'PS': 'brown'
}

# #VIII
VIIIclub_colors = {
    'PiS': 'blue',
    'PO-KO': 'orange',
    'PSL-KP': 'green',
    'Konfederacja': 'navy',
    'Kukiz15': 'black',
    'PP': 'red',
    'UPR': 'pink',
    'PSL-UED': 'cyan',
    'niez.': 'gray',
    'TERAZ!':'brown',
    'WiS': 'lime',
    'PO':'yellow',
    'nan':'darkgray'
}

club_colors_dict = {#'7': VIIclub_colors,
                 '8': VIIIclub_colors,
                 '9': IXclub_colors,
                 '10': Xclub_colors}
club_colors = club_colors_dict[str(term)]

print(len(sizes))

sigma = 0.01
mu =0

# generate normally distributed samples
noisex = sigma * np.random.randn(len(df_pca)) + mu
noisey = sigma * np.random.randn(len(df_pca)) + mu

xy = np.vstack([df_pca[:, 0]+noisex, df_pca[:, 1]+noisey])
z = list(gaussian_kde(xy)(xy))
print(xy)

# scatter plot
plt.figure(figsize=(10,10))
#print(mps_clubs[0:459])
for i, club in enumerate(mps_clubs[0:460]):
    color = club_colors[club]
    plt.scatter(df_pca[i, 0]+noisex[i], df_pca[i, 1]+noisey[i], c=z[i], s=sizes[i], label=club)
    plt.scatter(df_pca[i, 0], df_pca[i, 1], c=z[i], s=sizes[i], label=club)

# annotations
# for i in range(len(df_pca)):
#     plt.annotate(str(i+1), (df_pca[i, 0]+noisex[i], df_pca[i, 1]+noisey[i]), size=5)

plt.savefig('pca1.png', bbox_inches='tight')
plt.show()
