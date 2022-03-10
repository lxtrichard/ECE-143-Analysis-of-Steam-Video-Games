from turtle import color
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Visualization

import matplotlib.pyplot as plt
import seaborn as sns
import re

import itertools

default_color = sns.color_palette('pastel')

df = pd.read_csv("steamstore/steam.csv")
df.head()

# assign new column
df = df.assign(**{'overall_reviews':df.positive_ratings + df.negative_ratings})
df = df.assign(**{'positive_rate':df.positive_ratings / df.overall_reviews})

df = df.assign(**{'has_achievments':df.achievements > 0})
df = df.assign(**{'free':df.price == 0})
df['release_date'] = pd.to_datetime(df['release_date'])

# Total games over years
df['release_year'] = pd.DatetimeIndex(df['release_date']).year
steamYear = df.groupby(['release_year'])['appid'].count()

#Range Year antara 2010 - 2029
steamYearRange = steamYear.loc[2010:2019]

#Membuat plot
colors = sns.color_palette('pastel')
plt.figure(figsize=(16,8))
plt.bar(steamYearRange.index, steamYearRange,color=colors)
plt.xlabel("Year")
plt.ylabel("Total Game")
plt.title("Number of Game Steam Year 2010 - 2019")

plt.show()

# Language Distribution
steamLanguage = df.groupby(['english'])['appid'].count()
#Membuat plot
language_data = list(steamLanguage)
language_lable = ['Other', 'English']
colors = sns.color_palette('pastel')
plt.figure(figsize=(16,8))
plt.pie(language_data, labels=language_lable, colors=colors, autopct='%.0f%%')
plt.show()

# Platform 
operating_systems = ['windows', 'mac', 'linux']

df['windows'], df['mac'], df['linux'] = df['platforms'].apply(lambda x: 'windows' in x),df['platforms'].apply(lambda x: 'mac' in x),df['platforms'].apply(lambda x: 'linux' in x)
system_data = [df[df['windows']].shape[0], df[df['mac']].shape[0], df['linux'].shape[0]]
system_labels = ['windows', 'mac', 'linux']
colors = sns.color_palette('pastel')
plt.figure(figsize=(16,8))
plt.pie(system_data, labels=system_labels, colors=colors, autopct='%.0f%%')
plt.show()

#Gernes
def process_gen_tag(df):    
  gen_cols = ['Action','Adventure','Casual','Indie',
              'Massively Multiplayer','RPG','Racing',
              'Simulation','Sports','Strategy']

  gen_col_names = []

  for col in sorted(gen_cols):
      col_name = col.lower().replace('&', 'and').replace(' ', '_')
      gen_col_names.append(col_name)
      
      df[col_name] = df['genres'].apply(lambda x: 1 if col in x.split(';') else 0)

  gen_sums = df[gen_col_names].sum(axis=1)
  df = df[gen_sums > 0]    
  return df
df = process_gen_tag(df)

genre_cols = ['Action','Adventure','Casual','Indie',
                'Massively Multiplayer','RPG','Racing',
                'Simulation','Sports','Strategy']
gen_cols = df.columns[-10:]
average_owners_per_genre = list(df[gen_cols].sum())

colors = sns.color_palette('pastel')
plt.figure(figsize=(16,8))
plt.pie(average_owners_per_genre, labels=genre_cols, colors=colors, autopct='%.0f%%')
plt.show()

# Price overview and changes
free, not_free = df[df['price'] == 0].shape[0], df[df['price'] != 0].shape[0]

plt.figure(figsize=(16,8))
price_data = [free, not_free]
price_lable = ['free', 'not free']
colors = sns.color_palette('pastel')
plt.pie(price_data, labels=price_lable, colors=colors, autopct='%.0f%%')
plt.show()

free_df, not_free_df = df[df['price'] == 0], df[df['price'] != 0]
def process_gen_tag_bar(df):
  df = process_gen_tag(df)
  genre_cols = ['Action','Adventure','Casual','Indie',
                'Massively Multiplayer','RPG','Racing',
                'Simulation','Sports','Strategy']
  gen_cols = df.columns[-10:]
  average_owners_per_genre = list(df[gen_cols].sum())
  norm = [float(i)/sum(average_owners_per_genre) for i in average_owners_per_genre]
  new_d = dict(zip(gen_cols,norm))
  large = {k: v for k, v in sorted(new_d.items(), key=lambda item: item[1],reverse=True)[:4]}
  small = {k: v for k, v in sorted(new_d.items(), key=lambda item: item[1],reverse=True)[4:]}
  ratios = list(large.values())+[sum(small.values())]
  legends = list(large.keys())+['others']
  return ratios[::-1], legends[::-1]

from matplotlib.patches import ConnectionPatch
# make figure and assign axis objects
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 7))
fig.subplots_adjust(wspace=0)

# pie chart parameters
explode = [0.1, 0]
price_data = [free, not_free]
price_lable = ['free', 'not free']
colors = sns.color_palette('pastel')
# rotate so that first wedge is split by the x-axis
angle = -180 * price_data[0]
ax1.pie(price_data, labels=price_lable, colors=colors, autopct='%.0f%%', explode=explode)

# bar chart parameters

xpos = 0
bottom = 0
r1,l1 = process_gen_tag_bar(free_df)
width = .2
colors = sns.color_palette('pastel')

for j in range(len(r1)):
    height = r1[j]
    ax2.bar(xpos, height, width, bottom=bottom, color=colors[j])
    ypos = bottom + ax2.patches[j].get_height() / 2
    bottom += height
    ax2.text(xpos, ypos, "%d%%" % (ax2.patches[j].get_height() * 100),
             ha='center')

ax2.set_title('genres')
ax2.legend(l1)
ax2.axis('off')
ax2.set_xlim(- 2.5 * width, 2.5 * width)

theta1, theta2 = ax1.patches[0].theta1, ax1.patches[0].theta2
center, r = ax1.patches[0].center, ax1.patches[0].r
bar_height = sum([item.get_height() for item in ax2.patches])

x = r * np.cos(np.pi / 180 * theta2) + center[0]
y = r * np.sin(np.pi / 180 * theta2) + center[1]
con = ConnectionPatch(xyA=(-width / 2, bar_height), coordsA=ax2.transData,
                      xyB=(x, y), coordsB=ax1.transData)
con.set_color([0, 0, 0])
con.set_linewidth(2)
ax2.add_artist(con)

x = r * np.cos(np.pi / 180 * theta1) + center[0]
y = r * np.sin(np.pi / 180 * theta1) + center[1]
con = ConnectionPatch(xyA=(-width / 2, 0), coordsA=ax2.transData,
                      xyB=(x, y), coordsB=ax1.transData)
con.set_color([0, 0, 0])
ax2.add_artist(con)
con.set_linewidth(2)

plt.show()

import matplotlib.image as image
def get_year(s):
  return int(s.split('-')[0])

df_year = df[['release_year', 'price']].copy()
df_year = df_year[df_year['release_year'].between(2010, 2019)]

sns.set_theme(style="whitegrid")
cmap = sns.cubehelix_palette(rot=-.2, as_cmap=True)
g = sns.relplot(
    data=df_year,
    x="release_year", y="price",
    palette=cmap, height=8, aspect=2,
  )
g.ax.xaxis.grid(True, "minor", linewidth=1)
g.ax.yaxis.grid(True, "minor", linewidth=.25)
g.despine(left=True, bottom=True)
plt.show()

df_year = df[['release_date', 'price']].copy()
df_year['year'] = df_year['release_date'].apply(lambda x: x.year)
df_year = df_year[df_year['year'].between(2010, 2019)]
data_year_price = df_year.groupby(['year'])['price'].mean()
df_year_price = pd.DataFrame({'year': data_year_price.index, 'price': data_year_price.values})

plt.figure(figsize=(16,8))
sns.set_theme()
sns.lineplot(x='year', y='price', data=df_year_price)
plt.show()

df_year_price['num'] = list(steamYearRange)

sns.set_theme(style="white")
fig, ax1 = plt.subplots(figsize=(16,8))
ax2 = ax1.twinx()
sns.barplot(x="year", y="num", data=df_year_price, ax=ax2, alpha=.5)
sns.lineplot(x=np.arange(0,len(df_year_price)), y="price", data=df_year_price, ax=ax1)

fig.tight_layout()  # otherwise the right y-label is slightly clipped

plt.title('2010 to 2019 Announcements')

# Publishers
top=10
plt.figure(figsize=(16,8))
plt.title(f'Top {top} publishers with most games')

colors = sns.color_palette('pastel')
sns.countplot(y="publisher", data=df,
        order=df.publisher.value_counts().iloc[:top].index,
        palette='pastel')

plt.show()

# Developers
top=10
plt.figure(figsize=(16,8))
plt.title(f'Top {top} developers with most games')
sns.countplot(y='developer', data=df, order=df.developer.value_counts().iloc[:10].index, palette='pastel')
plt.show()

agg_developers = df.groupby('developer').agg({'overall_reviews': ['min', 'max', 'median'], 'name':'count', 'positive_rate': 'mean', 'price':'mean'})

plt.figure(figsize=(16,8))

g = sns.histplot(agg_developers[('price', 'mean')].value_counts(), kde=False,bins=500)
g.set_yscale('log')
plt.xlim((0,100))
plt.xlabel('Mean price of developer')
plt.show()

# Average playtime
plt.figure(figsize=(16,8))

g = sns.histplot(df.average_playtime, kde=False)
g.set_yscale('log')

plt.ylabel("Count")
plt.xlabel("Average playtime")

# Rating
plt.figure(figsize=(16,8))
plt.title('Positive Rate - Price')
g = sns.scatterplot(x="price", y="positive_rate", data=df[(df.price <= 100) & (df.overall_reviews > 100)])

vals = g.get_yticks()
_ = g.set_yticklabels(['{:,.0%}'.format(x) for x in vals])
plt.show()

positiveMessage = df.sort_values(by='positive_ratings', ascending=False).iloc[:10]
positiveRating = positiveMessage['positive_ratings']
positiveName = positiveMessage['name']

plotFigure, plotRating = plt.subplots(figsize=(16, 8))
colors = sns.color_palette('pastel')
plotRating.barh(positiveName, positiveRating, color=colors)
plotRating.invert_yaxis()
plotFigure.suptitle('Top 10 Games with Positive Rating')

plt.show()

# Various categories
categories_set = set()
for i in df.categories.str.split(';'):
    categories_set.update(i)
categories_set

d = dict()
category_set = df.categories.str.split(';').apply(set)
for category in categories_set:
    d[category] = category_set.apply(lambda row: category in row)
df = df.assign(**d)

trunc_year = 2010
truncated_df = df[df.release_date.dt.year>trunc_year]
palette = sns.color_palette('pastel')
def over_the_years(df, column_name, palette=palette, rate_lim=None):

    fig = plt.figure(figsize=(24, 12))
    
    yearly = df.groupby(df.release_date.dt.year.rename('release_year'))\
        .agg('count').appid.rename('count')
    p = df.groupby(df.release_date.dt.year)[column_name].mean()
    
    plt.subplot(121)
    g = sns.barplot(x=yearly.index, y=yearly, color=palette[1],label="Overall")
    g2 = sns.barplot(x=yearly.index, y=yearly * p, color=palette[2], label=f"{column_name} games")
    plt.legend()
    plt.xticks(rotation=45)
    plt.title(f'{column_name} over the years')
    plt.xlabel('Release year')
    
    plt.subplot(122)
    g3 = sns.barplot(x=p.index, y=p, color=palette[2])
    plt.xticks(rotation=45)
    plt.xlabel('Release year')
    plt.ylabel(f'{column_name} rate')
    if rate_lim:
        g3.set_ylim(rate_lim)
    vals = g3.get_yticks()
    g3.set_yticklabels(['{:,.0%}'.format(x) for x in vals])

over_the_years(truncated_df, 'Steam Trading Cards')
over_the_years(truncated_df, 'Single-player', rate_lim=(0.8,1.0))
over_the_years(truncated_df, 'free')