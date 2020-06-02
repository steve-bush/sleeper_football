import json

players = {}
with open("nfl.json") as fp:
    players = json.load(fp)