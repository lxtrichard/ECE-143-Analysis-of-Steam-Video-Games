import gzip
from collections import defaultdict

def parse_gzip_helper(f):
    for l in gzip.open(f):
        yield eval(l)

def parse_gzip(filename):
    return list(parse_gzip_helper(filename))

path = './steamrecommand/steam_games.json.gz'
games = parse_gzip(path)
game_list = []
for game in games:
    temp = []
    if 'id' in game:
        temp.append(game['id'])
    else:
        temp.append(0)
    if 'app_name' in game: 
        temp.append(game['app_name'])
    else:
        temp.append('')
    if 'tags' in game:
        temp.append(game['tags'])
    else:
        temp.append([])
    game_list.append(temp)

path = './steamrecommand/australian_users_items.json.gz'
temp1 = parse_gzip(path)

user_list = []
for user in temp1:
    temp = []
    temp.append(user['steam_id'])
    bought_list = []
    for g in user['items']:
        bought_list.append(g['item_id'])
    temp.append(bought_list)
    user_list.append(temp)
    
path = './steamrecommand/bundle_data.json.gz'
bundles = parse_gzip(path)
bundle_list = []
for b in bundles:
    temp = []
    for i in b['items']:
        temp.append(i['item_id'])
    bundle_list.append(temp)
    
numbers = [k[0] for k in game_list]
total = 0
missing_game = 0
for i in bundle_list:
    for k in i:
        total+=1
        if k not in numbers:
            game_list.append([k,'',[]])
            missing_game+=1
print(missing_game/total)

def Jaccard(s1, s2):
    numer = len(s1.intersection(s2))
    denom = len(s1.union(s2))
    if denom == 0:
        return 0
    return numer / denom

userOfGames = defaultdict(set)
gameOfUser = defaultdict(set)
genreOfGames = defaultdict(set)
for u in user_list:
    user_id = u[0]
    for g in u[1]:
        userOfGames[g].add(user_id)
        gameOfUser[user_id].add(g)
for g in game_list:
    game_id = g[0]
    for t in g[2]:
        genreOfGames[game_id].add(t)


def type_sim(game_id):
    sim = []
    for g in game_list:
        if g[0] == game_id:
            sim.append(0)
        else:
            sim.append(Jaccard(genreOfGames[game_id],genreOfGames[g[0]]))
    return sim

def user_sim(game_id):
    sim = []
    for g in game_list:
        if g[0] == game_id:
            sim.append(0)
        else:
            sim.append(Jaccard(userOfGames[game_id],userOfGames[g[0]]))
    return sim

def bundle_bonus(game_id):
    bonus = defaultdict(int)
    for b in bundle_list:
        if game_id not in b:
            continue
        else:
            for g in b:
                if g == game_id:
                    continue
                else:
                    bonus[g]+=0.1
    return bonus

def game_recommender(game_id,top = 10,type_w = 0.4,user_w = 0.4,bund_w = 0.2):
    type_l = type_sim(game_id)
    user_l = user_sim(game_id)
    bonus = bundle_bonus(game_id)
    score_list = []
    for i in range(len(game_list)):
        if game_id == game_list[i][0]:
            print(game_list[i][1])
            continue
        temp = []
        temp.append(type_w*type_l[i]+user_w*user_l[i]+bund_w*bonus[game_list[i][0]])
        temp.append(game_list[i][1])
        score_list.append(temp)
    score_list = sorted(score_list,reverse=True)
    game_name = []
    for i in range(top):
        print(score_list[i][1],score_list[i][0])
        #game_name.append(score_list[i][1])
    #return game_name

game_recommender('768880')