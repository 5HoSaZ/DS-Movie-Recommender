import pandas as pd
import numpy as np
from pathlib import Path
import ast

file_path = Path("imdb-movie-scraper\database\movie_entries 2.csv")
if file_path.exists():
    data = pd.read_csv(file_path)
    print('sucess')
else:
    print(f"File not found: {file_path}")




# recommendation will be based on these features only
data = data.loc[:,['ImdbID', 'Name', 'Directors',
       'OriginCountries', 'Languages', 'Genres', 'Rating', 'Plot', 'Cast']]



data['Directors'] = data['Directors'].replace(np.nan, 'unknown')
data['Languages'] = data['Languages'].replace(np.nan, 'unknown')
data['OriginCountries'] = data['OriginCountries'].replace(np.nan, 'unknown')
data['Plot'] = data['Plot'].replace(np.nan, 'unknown')
data['Cast'] = data['Cast'].replace(np.nan, 'unknown')



data['Directors'] = data['Directors'].str.replace('[', ' ').str.replace(']', ' ').str.replace("'", "")
data['OriginCountries'] = data['OriginCountries'].str.replace('[', ' ').str.replace(']', ' ').str.replace("'", "")
data['Languages'] = data['Languages'].str.replace('[', ' ').str.replace(']', ' ').str.replace("'", "")
data['Genres'] = data['Genres'].str.replace('[', ' ').str.replace(']', ' ').str.replace("'", "").str.replace(',', '')
data['Cast'] = data['Cast'].str.replace('[', ' ').str.replace(']', ' ').str.replace("'", "").str.replace(',', '')




data['Genres'] = data['Genres'].map(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else x)

#Now we will have to take out the individual genres like adventure, action, sci-fi, etc. using the following function


def make_genresList(x):
    gen = []
    st = " "
    for i in x:
        if i.get('name') == 'Science Fiction': #am only renaming the "Science Fiction" to "Sci-Fi" to make it the name shorter. Apart from that all other names remain the same.
            scifi = 'Sci-Fi'
            gen.append(scifi)
        else:
            gen.append(i.get('name'))
    if gen == []:
        return np.NaN
    else:
        return (st.join(gen)) #then we will join them together and return the valuse
    
print(data.head())
print(data.dtypes)

data.to_csv('imdb-movie-scraper\database\handel1.csv',index=False)