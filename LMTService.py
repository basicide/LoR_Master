#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from sentry_sdk.integrations.flask import FlaskIntegration
import sentry_sdk
import threading
import time
from Models import leaderboard
from Models.leaderboard import Leaderboard
from Models.setting import Setting
from Models.local import Local
from Models.riot import Riot
from Models.network import Network
from Models.player import Player
from Models.setting import Server
from Models.cache import Cache
from Models import master
from Models.process import readLog
from Models.heroku import Heroku
import json
from flask import Flask, jsonify, redirect
import io
import sys
import os
import constants
import argparse
from waitress import serve
import requests

argParser = argparse.ArgumentParser()
argParser.add_argument('--port', action='store', type=int, default=26531)
argParser.add_argument('--status', action='store', type=str, default='dev')
args = argParser.parse_args()
print('args: ', args)

isDebug = False

if args.status == 'dev':
    isDebug = True


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')
print('utf8 string test: ', '卡尼能布恩', '째남모')

sentry_sdk.init(
    "https://1138a186a6384b00a20a6196273c3009@o958702.ingest.sentry.io/5907306",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True,
    debug=isDebug,
    release=constants.VERSION_NUM
)

sentry_sdk.set_context("info", {
    "version": constants.VERSION_NUM
})

master.startMasterWorker()
leaderboardModel = Leaderboard()
cacheModel = Cache()
herokuModel = Heroku(leaderboardModel)

settingTrack = Setting()
localTrack = Local(settingTrack, cacheModel)


class FlaskApp(Flask):
    def __init__(self, *args, **kwargs):
        super(FlaskApp, self).__init__(*args, **kwargs)
        self.processWork()
        self.leaderboardsWork()

    def processWork(self):
        def run_work():
            while True:
                readLog(settingTrack)
                time.sleep(3)
        work = threading.Thread(target=run_work)
        work.daemon = True
        work.start()

    def leaderboardsWork(self):
        def run_work():
            while True:
                leaderboardModel.updateAll()
                time.sleep(600)
        work = threading.Thread(target=run_work)
        work.daemon = True
        work.start()


app = FlaskApp(__name__)




@app.route("/process", methods=['get'])
def process():
    process_info = {}
    process_info['server'] = settingTrack.riotServer
    process_info['port'] = settingTrack.port
    return jsonify(process_info)


@app.route("/track", methods=['get'])
def track():
    return jsonify(localTrack.updateStatusFlask())


@app.route("/history/<string:server>/<string:name>/<string:tag>", methods=['get'])
def history(server, name, tag):
    return redirect("https://lormaster.herokuapp.com/history/" + server + '/' + name + '/' + tag)


@app.route("/name/<string:server>/<string:playername>", methods=['get'])
def get_names(server, playername):
    # # to-do move functions to master model
    # playernames = set()
    # nameListPath = constants.getCacheFilePath(server.lower() + '.json')
    # if not os.path.isfile(nameListPath):
    #     nameListPath = 'Resource/' + server.lower() + '.json'
    # try:
    #     with open(nameListPath, 'r', encoding='utf-8') as fp:
    #         names = json.load(fp)
    #         for name in names.items():
    #             playernames.add(name[0] + '#' + name[1])
    # except Exception as e:
    #     print('updatePlayernames', e)
    # playerList = set()
    # for name in playernames:
    #     if name[0:len(playername)].lower() == playername.lower():
    #         playerList.add(name)
    # returnList = jsonify(list(playerList))
    # return returnList
    return redirect("https://lormaster.herokuapp.com/name/" + server + '/' + playername)

@app.route("/search/<string:server>/<string:name>/<string:tag>", methods=['get'])
def search(name, tag, server):
    return redirect("https://lormaster.herokuapp.com/search/" + server + '/' + name + '/' + tag)


def saveMatchIdsInCache(server, name, tag, matchIds):
    uniqueName = name + tag + server
    matchIdsCache = cacheModel.matches.get(uniqueName)
    if matchIdsCache is not None:
        new = matchIds + list(set(matchIdsCache) - set(matchIds))
        cacheModel.matches[uniqueName] = new
    else:
        cacheModel.matches[uniqueName] = matchIds
    cacheModel.save()

@app.route("/leaderboard/<string:server>", methods=['get'])
def get_leaderboard(server):
    return redirect("https://lormaster.herokuapp.com/leaderboard/" + server)


@app.route("/opInfo", methods=['get'])
def opInfo():
    opInfo = {}
    opInfo['name'] = localTrack.opponentName
    # will break here if opponentName is None
    if localTrack.opponentName.startswith('deckname_') or localTrack.opponentName.startswith('decks_'):
        opInfo['name'] = 'AI'
    opInfo['tag'] = 'S'
    opInfo['rank'], opInfo['lp'] = leaderboardModel.checkRank(
        localTrack.opponentName, settingTrack.riotServer)
    return jsonify(opInfo)


@app.route("/status", methods=['get'])
def get_status():
    status = {}
    status['playerId'] = settingTrack.playerId
    status['port'] = settingTrack.port
    status['server'] = settingTrack.riotServer
    status['language'] = settingTrack.language
    status['lorRunning'] = settingTrack.isLorRunning
    # isLocalApiEnable is updated by track api
    status['isLocalApiEnable'] = settingTrack.isLocalApiEnable
    return jsonify(status)


@app.route("/local", methods=['get'])
def get_local():
    if settingTrack.playerId in cacheModel.localMatches:
        for detail in cacheModel.localMatches[settingTrack.playerId]:
            detail['opponentRank'], detail['opponentLp'] = leaderboardModel.checkRank(
                detail['opponentName'], settingTrack.riotServer)
    return jsonify(cacheModel.localMatches)


@app.route("/report/<string:message>", methods=['get'])
def report(message):
    sentry_sdk.capture_message(message)
    return jsonify('OK')

if isDebug:
    app.run(port=args.port, debug=True, use_reloader=False)
else:
    serve(app, host='0.0.0.0', port=args.port)
