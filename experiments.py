# -*- coding: utf-8 -*-
"""
Created on Tue Jun 24 01:21:08 2014

@author: Seve
"""

"""
Created on Thu Jun 19 00:17:30 2014

@author: Seve
"""
import json, requests, time, os, pickle
import pandas as pd
from pandas import DataFrame
from pandas import Series
import numpy as np

import matplotlib
matplotlib.use('Agg')
from matplotlib import pylab
from matplotlib import pyplot as plt

os.chdir(r'C:\Users\Seve\Documents\learning-to-LoL')
# First experiment with making requests

# Need a summoner ID. For now I'm just grabbing a random number.
guess = 21584654

def get_valid_summoner_id(guess=0,key = 'fe3ea9e4-c55c-4726-b71d-178643c29464',region='na'):
    bad_id = 1
    while bad_id == 1:
        if guess == 0:
            summoner_id = np.random.randint(2,9999)
        else:
            summoner_id = guess
            
        url = 'https://{}.api.pvp.net/api/lol/{}/v1.4/summoner/{}/?api_key={}'.format(region,region,summoner_id,key)
        
        req = requests.get(url)

        if req.status_code == 200:
            bad_id = 0
        elif req.status_code == 429:
            print 'Rate limit exceeded!'
            break
        elif req.status_code == 404:
            print 'Bad summonerId'
        guess = 0
    
    return summoner_id
    
def get_some_game_data(key = 'fe3ea9e4-c55c-4726-b71d-178643c29464',region='na',game_stats=[],summoner_id = 21584654, time_out=10,out_file='game_stats'):
    # Now that we've got some summonerIDs we can really start to make requests
    if summoner_id == 0:
        summoner_id = [get_valid_summoner_id(key=key, region=region)]
        
    else:
        summoner_id = [summoner_id]
    
    count = 0    
    for sid in summoner_id:
        url = 'https://{}.api.pvp.net/api/lol/{}/v1.3/game/by-summoner/{}/recent?api_key={}'.format(region,region,sid,key)
        
        req = requests.get(url)
        
        if req.status_code == 200:
            content = req.content
            game_stats.append(json.loads(content))

        else:
            print req.status_code

        for game in game_stats[count]['games']:
            if 'fellowPlayers' in game.keys():
                for player in game['fellowPlayers']:
                    if player['summonerId'] not in summoner_id:
                        summoner_id.append(player['summonerId'])
                    
        time.sleep(1.2)
        if count >= time_out:
            pickle.dump(game_stats, open('{}.p'.format(out_file),'wb'))
            return 1
        count = count + 1
        
        
    
#I want a single instance to be all the stats for a single game...
# i.e. I want a list of dicts, each dict will have keys corresponding to every stat in the game.
    


def get_stats(game_stats):
    game_list = []
    for game in range(len(game_stats['games'])):
        game_list = game_list + [{'summonerId': game_stats['summonerId']}]
        game_list[game]['teamId'] = game_stats['games'][game]['teamId']
        for s in game_stats['games'][game].keys():

            if s != 'stats' and s != 'fellowPlayers':
                game_list[game][s] = game_stats['games'][game][s]
            for t in game_stats['games'][game]['stats']:
                
                game_list[game][t] = game_stats['games'][game]['stats'][t]
            if 'fellowPlayers' not in game_stats['games'][game].keys():
                game_list[game]['SOLO'] = True 
                    
            else:
                ally = 0
                foe = 0
                game_list[game]['SOLO'] = False  
                for t in range(len(game_stats['games'][game]['fellowPlayers'])):
                    if game_stats['games'][game]['fellowPlayers'][t]['teamId'] == game_list[game]['teamId']:
                    
                        game_list[game]['ally{}_summonerId'.format(ally)] = game_stats['games'][game]['fellowPlayers'][t]['summonerId'] 
                        game_list[game]['ally{}_championId'.format(ally)] = game_stats['games'][game]['fellowPlayers'][t]['championId'] 
                        ally = ally + 1
                    else:
                        game_list[game]['foe{}_summonerId'.format(foe)] = game_stats['games'][game]['fellowPlayers'][t]['summonerId']
                        game_list[game]['foe{}_championId'.format(foe)] = game_stats['games'][game]['fellowPlayers'][t]['championId']
                        foe = foe + 1
                    
        
    return game_list
       
def get_champ_deaths_by_foe(df,save_plot=0,save_dir = r'C:\Users\Seve\Documents\learning-to-LoL\figures\champ_deaths_by_foe'):
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)
    os.chdir(save_dir)
    champ_list = Series(df.championId).dropna().unique()
    foe_list = Series(df[['foe0_championId', 'foe1_championId', 'foe2_championId', 'foe3_championId', 'foe4_championId']].values.ravel()).dropna().unique()
    champ_deaths_by_foe = DataFrame(index = champ_list, columns = foe_list)
    
    for champ in champ_list:
        champ_deaths_by_foe.ix[champ] = (df.ix[df.championId==champ].numDeaths.groupby(df['foe0_championId']).mean() + df.ix[df.championId==champ].numDeaths.groupby(df['foe1_championId']).mean() + df.ix[df.championId==champ].numDeaths.groupby(df['foe2_championId']).mean() + df.ix[df.championId==champ].numDeaths.groupby(df['foe3_championId']).mean() + df.ix[df.championId==champ].numDeaths.groupby(df['foe4_championId']).mean())/5.0
        
        if save_plot:
            fig = plt.figure()
            plt.bar(range(len(foe_list)), champ_deaths_by_foe.ix[champ])
            plt.title('champID: {} deaths by foe'.format(champ))
            plt.xticks(range(len(foe_list)), foe_list)
            #champ_deaths_by_foe.ix[champ].plot(kind='bar', title='champID: {} deaths by foe'.format(champ))
            plt.tight_layout()
            pylab.savefig('champ{}DeathsByFoe.png'.format(champ))
            plt.close(fig)
            
    return champ_deaths_by_foe
    
game_list = pickle.load(open('game_list_0.p'))
df = DataFrame(game_list)

cdbf = get_champ_deaths_by_foe(df=df,save_plot=1)
#death_df = DataFrame(game_list, columns=['championId', 'numDeaths', 'foe0_championId', 'foe1_championId', 'foe2_championId', 'foe3_championId', 'foe4_championId'])
#
#death_df = death_df.drop_duplicates()
#champ_list = Series(death_df.championId).dropna().unique()
#foe_list = Series(df[['foe0_championId', 'foe1_championId', 'foe2_championId', 'foe3_championId', 'foe4_championId']].values.ravel()).dropna().unique()
#
#mean_deaths_by_champ = death_df.numDeaths.groupby(death_df['championId']).mean()
#mean_deaths_by_champ.plot(kind='bar')
#
#mean_kills_by_champ = df.championsKilled.groupby(df.championId).mean()
#mean_kills_by_champ.plot(kind='bar')
#
#mean_kd_ratio = mean_kills_by_champ/mean_deaths_by_champ
#mean_kd_ratio.plot(kind='bar')






    