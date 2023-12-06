# Importujemy bibliotekę PCA-magic, która implementuje PPCA
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

mps_url = "https://api.sejm.gov.pl/sejm/term8/MP"
mps = pd.read_json(mps_url)


mps_clubs = mps['club']

# TODO nazwy klubów doklejone mądrzej niż po kolei i liczyć że jest to samo co tam
votings_df=pd.read_csv("voting_dfVIII.csv")

print(set(mps_clubs))
mps_clubs.replace(np.nan, 'nan', inplace=True)

# size of dot proportional to square of attendance
sizes=[]
for mp in votings_df.columns[2:]:
    percentage = (votings_df[mp] == -0.01).mean()
    sizes.append(((1-percentage)**2)*50)

votings_df.drop(votings_df.columns[:2], axis=1, inplace=True)
votings_df=votings_df.T

pca = PCA(n_components=2)

pca.fit(votings_df)

# Transform to 2D
df_pca = pca.transform(votings_df)

# X
# club_colors = {
#     'PiS': 'blue',
#     'KO': 'orange',
#     'PSL-TD': 'green',
#     'Polska2050-TD': 'yellow',
#     'Konfederacja': 'navy',
#     'Kukiz15': 'black',
#     'Lewica': 'red'
# }

# IX
# club_colors = {
#     'PiS': 'blue',
#     'KO': 'orange',
#     'KP': 'green',
#     'Polska2050': 'yellow',
#     'Konfederacja': 'navy',
#     'Kukiz15': 'black',
#     'Lewica': 'red',
#     'LD': 'pink',
#     'niez.': 'gray',
#     'PS': 'brown'
# }

# #VIII
# club_colors = {
#     'PiS': 'blue',
#     'PO-KO': 'orange',
#     'PSL-KP': 'green',
#     'Konfederacja': 'navy',
#     'Kukiz15': 'black',
#     'PP': 'red',
#     'UPR': 'pink',
#     'PSL-UED': 'cyan',
#     'niez.': 'gray',
#     'TERAZ!':'brown',
#     'WiS': 'lime',
#     'PO':'yellow',
#     'nan':'darkgray'
# }


print(len(sizes))

# scatter plot
plt.figure(figsize=(10,10))
for i, club in enumerate(mps_clubs):
    color = club_colors[club]
    plt.scatter(df_pca[i, 0], df_pca[i, 1], c=color, s=sizes[i], label=club)

# annotations
for i in range(len(df_pca)):
    plt.annotate(str(i), (df_pca[i, 0], df_pca[i, 1]), size=5)


plt.show()