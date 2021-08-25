from flask import Flask, jsonify
import json
from Models.setting import Server
from Models.player import Player
from Models.network import Network
from Models.riot import Riot
from Models.local import Local
from Models.setting import Setting
from Models.leaderboard import checkRank


app = Flask(__name__)

jsonText = {"DeckCode": "CIBQCAICBQBQEAQDAUDAKAYJBENSGM6XAEBACAQCBEBQGCJIFFKQIAICAIEACAYCCQAQGCITAIAQEARR", "CardsInDeck": {"01IO012": 3, "02IO003": 3, "02IO005": 3, "02IO006": 3, "03MT009": 3, "03MT027": 3, "03MT035": 3, "03MT051": 3, "03MT215": 3, "02IO009": 2, "03MT040": 2, "03MT041": 2, "03MT085": 2, "02IO008": 1, "03IO020": 
1, "03MT019": 1, "01IO002": 1, "01IO049": 1}, "CurrentDeckCode": "CEBQCAICBQBQEAQDAUDAKAYJBENSGM6XAEBACAQCBEBQGCJIFFKQIAICAIEACAYCCQAQGCITAIAQEARR"}

settingInspect = Setting()
networkInspect = Network(settingInspect)
riotInspect = Riot(networkInspect)
playerInspect = Player(riotInspect)
localInspect = Local(settingInspect)
#localInspect.updatePlayernames()

print(localInspect.playernames)

def processMatchDetail(detail):
    try:
        playerPuuids = detail['metadata']['participants']
    except Exception as e:
        print('processMatchDetail error:', e)
        return detail
    playernames = []
    player_info = []
    for puuid in playerPuuids:
        name, tag = riotInspect.getPlayerName(puuid)
        rank, lp = checkRank(name, Server.NA.value)
        playernames.append(name + '#' + tag)
        player_info.append({'name':name, 'tag':tag, 'rank':rank, 'lp':lp})
    detail['playernames'] = playernames
    detail['player_info'] = player_info
    return detail

@app.route("/code", methods = ['get'])
def get_code():
    return jsonText


@app.route("/name/<string:server>/<string:playername>", methods = ['get'])
def get_names(server, playername):
    settingInspect.setServer(Server._value2member_map_[server])
    localInspect.updatePlayernames()
    playerList = set()
    for name in localInspect.playernames:
        if name[0:len(playername)].lower() == playername.lower():
            playerList.add(name)

    returnList = jsonify(list(playerList))
    print(returnList)
    return returnList

@app.route("/search/<string:server>/<string:name>/<string:tag>", methods = ['get'])
def search(name, tag, server):
    settingInspect.setServer(Server._value2member_map_[server])
    allMatches = []
    try:
        puuid = riotInspect.getPlayerPUUID(name, tag)
        matchIds = riotInspect.getMatches(puuid)
        print(matchIds)
        for matchId in matchIds:
            allMatches.append(processMatchDetail(riotInspect.getDetail(matchId, 5)))
    except Exception as e:
        print(e)
        return 'Error'
    return jsonify(allMatches)

    
app.run(host='0.0.0.0', port=6123)
