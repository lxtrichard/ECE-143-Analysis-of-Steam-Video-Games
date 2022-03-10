import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

games = pd.read_csv('./steamstore/steam.csv')

games.head()

def DataPreProcessing(games):
    
    '''
    games is a pd.DataFrame object with all infomation,
    only keep the year infor of  the release_date and take the middle
    value of the range of the number of owners
    :param games: pd.DataFrame
    :return: None
    '''
    
    assert isinstance(games,pd.DataFrame)
    
    games['release_date'] = pd.to_datetime(games['release_date']).dt.year
    
    users= games['owners'].str.split(r"-",expand = True)
    users = users.astype(int)
    games['owners'] = (users[0]+users[1])//2
    
#Reformat release_date and owner values
DataPreProcessing(games)
games.head()

def categories_count(games,col):
    '''
    games is a pd.DataFrame object with all infomation,
    extract either the genres or category column to know how many games in each catergory
    values in each contains semicolon, separate values by comma and count their occurence
    and output as a pd.dataframe
    :param x: pd.DataFrame
    :return: pd.DataFrame
    '''
    
    assert isinstance(games,pd.DataFrame)
    assert isinstance(col,str)
    assert col == 'categories' or col == 'genres'
    x = games[col]
    assert isinstance(x, pd.Series)

    s= x.str.split(r";",expand = True)
    vals = s.apply(pd.value_counts).sum(axis=1,).sort_values(ascending=True).to_frame()
    vals.columns = ["Num of Games"]
    vals.index.name = col

    return vals

games[['name','genres','positive_ratings','negative_ratings','average_playtime','price','owners']].head()

all_cat = categories_count(games,'categories')
all_cat

#plot the games distribution over differnet categories

cat_name = list(all_cat.index)[-13:]
print(cat_name)
sums = 0

for val in cat_name:
    sums+=all_cat['Num of Games'][val]

cat_name.append('others')

cat_vals = list(all_cat['Num of Games'])[-13:]
cat_vals.append(all_cat.sum()-sums)

colors = sns.color_palette('pastel')
plt.figure(figsize=(16,16))
plt.title = 'Percentage of Games belong to each category'
plt.pie(cat_vals, labels=cat_name, colors=colors, autopct='%.0f%%',textprops={'fontsize': 15})
plt.show()

#plot the games distribution over differnet genres

all_gen = categories_count(games,'genres')

gen_name = list(all_gen.index)[-13:]
sums = 0

for val in gen_name:
    sums+=all_gen['Num of Games'][val]

gen_vals = list(all_gen['Num of Games'])[-13:]
gen_vals.append(all_gen.sum()-sums)

gen_name.append('others')
colors = sns.color_palette('pastel')
plt.figure(figsize=(16,16))
plt.pie(gen_vals, labels=gen_name, colors=colors, autopct='%.0f%%',textprops={'fontsize': 15})
plt.show()

def average_rating(game,col):
    
    '''
    games is a pd.DataFrame object with all infomation,
    extract either the genres or category column to know how averagge games, positive ratings,
    neggative ratings, prices, and owners, in each catergory
    categories/genere data semicolon, separate values by comma and count their occurence,
    
    :param x: pd.DataFrame
    :param col: str, either categorize data base on genres or categories
    :return: pd.DataFrame
    '''
    
    assert isinstance(game,pd.DataFrame)
    assert isinstance(col,str)
    assert col == 'categories' or col == 'genres'
    x = game[col]
    assert isinstance(x, pd.Series)
    
    games = game.copy()
    columns = ['positive_ratings','negative_ratings','average_playtime','price','owners']
    
    s= games[col].str.split(r";",expand = True)
    vals = s.apply(pd.value_counts).sum(axis=1,).sort_values(ascending=True).to_frame()
    vals.columns = ["Num of Games"]
    vals.index.name = col
    
    for column in columns:
        temp = games[column].astype(int)
        counts = dict.fromkeys(list(vals.index),0)
        
        for i in list(s.columns):
            
            for key in counts.keys():
                tempInfo = temp[s[i]== key]
                counts[key]+=tempInfo.sum()
            
            
        vals[column]=vals.index.map(counts)/vals['Num of Games']
    
    return vals


#correlation Matrix based on each game info
game_feature = games[['positive_ratings','negative_ratings','average_playtime','price','owners']]
game_feature.corr()

ax = plt.axes()
colors = sns.color_palette('pastel')
sns.heatmap(game_feature.corr(), annot=True,cmap = colors)
ax.set_title('Original Correlation Matrix')

#Group games by genres and sum all features values and divided by number of games in each genres 
#to obtain new data, and determine the correlation matrix
info = average_rating(games,'genres')
info_corr = info.corr()
# plt.figure(figsize = (15,15))
colors = sns.color_palette('light:#5A9',as_cmap=True)

ax = plt.axes()
sns.heatmap(info_corr, annot=True,cmap = colors)
ax.set_title('Group Games by Genres')
                                         
                                         

#Group games by categories and sum all features values and divided by number of games in each categories 
#to obtain new data, and determine the correlation matrix

info_cat = average_rating(games,'categories')

ax = plt.axes()
sns.heatmap(info_cat.corr(), annot=True,cmap = colors)
ax.set_title('Group Games by Categories')