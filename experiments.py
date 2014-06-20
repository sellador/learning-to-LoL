# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 00:17:30 2014

@author: Seve
"""
import json, requests
import numpy as np

# First experiment with making requests

# Need a summoner ID. For now I'm just grabbing a random number.
bad_id = 1
while bad_id == 1:
#    summoner_id = np.random.randint(2,9999)
    summoner_id = [66430]
    region = 'na'
    key = 'ab05b3cc-5c2e-43d2-b6cd-a1ae38875d87'
    
    url = 'https://{}.api.pvp.net/api/lol/{}/v1.3/game/by-summoner/{}/recent?api_key={}'.format(region,region,summoner_id,key)
    
    req = requests.get(url)
    
    if req.status_code == 200:
        bad_id = 0
    elif req.status_code == 429:
        print 'Rate limit exceeded!'
        break
    elif req.status_code == 404:
        print 'Bad summonerId'

content = req.content
game_stats = json.loads(content)

for game in game_stats['games']:
    for player in game['fellowPlayers']:
        if player['summonerId'] not in summoner_id:
            summoner_id.append(player['summonerId'])
