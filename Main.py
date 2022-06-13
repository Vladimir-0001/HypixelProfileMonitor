import json
import time
import discord
from discord.ext import commands
import threading
import requests


####################################################################################################################################
# WARNING : using this bot may be against Hypixel's Terms of Service and may result in a api-reset or api-ban use at your own risk.#
####################################################################################################################################
# This bot was made by: Vladimir#0001.#
#######################################


POLLING_RATE = 15 # how long to wait between checking for change in status
HYPIXEL_API_KEY = "" #your hypixel api key get this by doing "/api new" in the hypixel server
UPDATE_CHANNEL_ID = "" # the id of channel to send the update to 
YOUR_ID = "" # your discord id leave blank if you dont want to ping yourself
DISCORD_BOT_TOKEN = "" # your discord bot token
NOTIFY_WHEN_ONLINE = True # if you want to ping yourself when the target goes online
NOTIFY_WHEN_OFFLINE = True # if you want to ping yourself when the target goes offline
NOTIFY_ON_GAMECHANGE = True # if you want to ping yourself when the target changes gamemode's

###########################################################################################
#DO NOT EDIT BELOW THIS LINE UNLESS YOU KNOW WHAT YOU ARE DOING OR YOU WILL BREAK THE BOT.#
###########################################################################################

class Target():
    def __init__(self):
        self.updateTargets()
        self.uuid = None
        self.gameType = None
        self.online = None
        self.mode = None
        self.map = None
        self.name = None
        self.gameTypeMap= {
            "QUAKECRAFT": "Quakecraft",
            "WALLS": "Walls",
            "PAINTBALL": "Paintball",
            "SURVIVAL_GAMES": "Survival Games",
            "TNTGAMES": "TNT Games",
            "VAMPIREZ": "VampireZ",
            "WALLS3": "Walls3",
            "ARCADE": "Arcade",
            "AREANA": "Arena",
            "UHC": "UHC",
            "MCGO": "MCGO",
            "BATTLEGROUND": "Battleground",
            "SUPER_SMASH": "Super Smash",
            "GINGERBREAD": "Gingerbread",
            "HOUSING": "Housing",
            "SKYWARS": "SkyWars",
            "TRUE_COMBAT": "True Combat",
            "SPEED_UHC": "Speed UHC",
            "SKYCLASH": "SkyClash",
            "LEGACY": "Legacy",
            "PROTOTYPE": "Prototype",
            "BEDWARS": "Bed Wars",
            "MURDER_MYSTERY":"Murder Mystery",
            "BUILD_BATTLE":"Build Battle",
            "DUELS":"Duels",
            "SKYBLOCK":"skyblock",
            "PIT":"Pit",
            "REPLAY":"Replay",
            "SMP":"SMP",
            "MAIN":'lobby',
            "WOOL_GAMES":"Wool Games",
        }
    
    def updateTargets(self):
        with open('Targets.json') as data_file:
            self.dataFile = json.load(data_file)
            self.targets = self.dataFile['targets']

    def saveTarget(self, name):
        with open('Targets.json', 'w') as outfile:
            self.dataFile['targets'].update({name: {'uuid': self.uuid, 'gameType': self.gameType, 'mode': self.mode, 'map': self.map, 'online': self.online, 'name': name}})
            json.dump(self.dataFile, outfile, indent=3)
            
    def deleteTarget(self, name):
        self.dataFile['targets'].pop(name)
        with open('Targets.json', 'w') as outfile:
            json.dump(self.dataFile, outfile, indent=3)
            
    def status(self, name):
        req = requests.get('https://api.mojang.com/users/profiles/minecraft/' + name)
        if req.status_code == 204:
            return 
        if req.json()['id'] == None:
            return
        else:
            self.name = req.json()['name']
            req = requests.get('https://api.hypixel.net/status', params={'key': HYPIXEL_API_KEY, 'uuid': req.json()['id']})
            if req.json()['success'] == True:
                try:
                    self.uuid = req.json()['uuid']
                    self.online = req.json()['session']['online']
                    self.gameType = req.json()['session']['gameType'] 
                    self.mode = req.json()['session']['mode']
                    self.map = req.json()['session']['map']
                except:
                    pass
            
                
class client(discord.Client):
    async def on_ready(self):
        print("Logged on as", self.user)
        

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content.lower().startswith('!addtarget'):
            name = message.content.split(' ')[1]
            target = Target()
            target.status(name)
            target.saveTarget(name)
            await message.channel.send('Target added!')
        if message.content.startswith("!removetarget"):
            name = message.content.lower().split(' ')[1]
            target = Target()
            target.deleteTarget(name)
            await message.channel.send('Target Removed!')
        if message.content.lower().startswith("!status"):
            name = message.content.lower().split(' ')[1]
            target = Target()
            target.status(name)
            embed=discord.Embed(title="Target Status", description="**"+target.name+"**", color=0x2b9b44)
            embed.add_field(name="UUID: ", value=target.uuid, inline=False)
            embed.add_field(name="Online", value=target.online, inline=False)
            embed.set_thumbnail(url=f'https://crafatar.com/avatars/{target.uuid}?size=200')
            try:
                gt = target.gameTypeMap[target.gameType]
            except KeyError:
                gt = None 
            embed.add_field(name="Game", value=gt, inline=False)
            embed.add_field(name="Mode", value=target.mode, inline=False)
            embed.add_field(name="Map", value=target.map, inline=False)
            await message.channel.send(embed=embed)
            
    def checkStatusUpdate(self):
        #check for a update in uuid,online,mode,map of every target
        while True:
            for i in Target().targets:
                target = Target()
                target.status(i)
                if target.dataFile['targets'][i]['online'] != target.online:
                    if target.online == True and NOTIFY_WHEN_ONLINE == True:
                        headers = {'authorization': f'Bot {DISCORD_BOT_TOKEN}','content-type': 'application/json'}
                        embed = {
                            "content": f'<@{YOUR_ID}>',
                            "embeds": [
                                {
                                "title": "Target Status Update",
                                "description": f"{target.name} Changed Status to Online",
                                "color": 65392,
                                "thumbnail": {
                                    "url": f"https://crafatar.com/avatars/{target.uuid}?size=150"
                                }
                                }
                            ],
                            "attachments": []
                            }
                        response = json.dumps(embed)
                        r = requests.post(f"https://discord.com/api/v9/channels/{UPDATE_CHANNEL_ID}/messages", headers = headers, data = response)
                    if target.online == False and NOTIFY_WHEN_OFFLINE == True:
                        headers = {'authorization': f'Bot {DISCORD_BOT_TOKEN}','content-type': 'application/json'}
                        embed = {
                            "content": f'<@{YOUR_ID}>',
                            "embeds": [
                                {
                                "title": "Target Status Update",
                                "description": f"{target.name} Changed Status to Offline",
                                "color": 16716800,
                                "thumbnail": {
                                    "url": f"https://crafatar.com/avatars/{target.uuid}?size=150"
                                }
                                }
                            ],
                            "attachments": []
                            }
                        response = json.dumps(embed)
                        r = requests.post(f"https://discord.com/api/v9/channels/{UPDATE_CHANNEL_ID}/messages", headers = headers, data = response)
                        target.saveTarget(i)
                        break
                if target.dataFile['targets'][i]['gameType'] != target.gameType:
                    if target.dataFile['targets'][i]['gameType'] == None and target.gameType != None and NOTIFY_ON_GAMECHANGE == True:
                        headers = {'authorization': f'Bot {DISCORD_BOT_TOKEN}','content-type': 'application/json'}
                        embed = {
                            "content": f'<@{YOUR_ID}>',
                            "embeds": [
                                {
                                "title": "Target Game Type Update",
                                "description": f"{target.name} Started playing {target.gameTypeMap[target.gameType]}",
                                "color": 26367,
                                "thumbnail": {
                                    "url": f"https://crafatar.com/avatars/{target.uuid}?size=150"
                                }
                                }
                            ],
                            "attachments": []
                            }
                        response = json.dumps(embed)
                        r = requests.post(f"https://discord.com/api/v9/channels/{UPDATE_CHANNEL_ID}/messages", headers = headers, data = response)
                    if target.dataFile['targets'][i]['gameType'] != None and target.gameType == None and NOTIFY_ON_GAMECHANGE == True:
                        headers = {'authorization': f'Bot {DISCORD_BOT_TOKEN}','content-type': 'application/json'}
                        embed = {
                            "content": f'<@{YOUR_ID}>',
                            "embeds": [
                                {
                                "title": "Target Game Type Update",
                                "description": f"{target.name} Stopped playing {target.dataFile['targets'][i]['gameType']}",
                                "color": 26367,
                                "thumbnail": {
                                    "url": f"https://crafatar.com/avatars/{target.uuid}?size=150"
                                }
                                }
                            ],
                            "attachments": []
                            }
                        response = json.dumps(embed)
                        r = requests.post(f"https://discord.com/api/v9/channels/{UPDATE_CHANNEL_ID}/messages", headers = headers, data = response)
                    if target.dataFile['targets'][i]['gameType'] != None and target.gameType != None and NOTIFY_ON_GAMECHANGE == True:
                        headers = {'authorization': f'Bot {DISCORD_BOT_TOKEN}','content-type': 'application/json'}
                        embed = {
                            "content": f'<@{YOUR_ID}>',
                            "embeds": [
                                {
                                "title": "Target Game Type Update",
                                "description": f"{target.name} switched from {target.gameTypeMap[target.dataFile['targets'][i]['gameType']]} to {target.gameTypeMap[target.gameType]}",
                                "color": 26367,
                                "thumbnail": {
                                    "url": f"https://crafatar.com/avatars/{target.uuid}?size=150"
                                }
                                }
                            ],
                            "attachments": []
                            }
                        response = json.dumps(embed)
                        r = requests.post(f"https://discord.com/api/v9/channels/{UPDATE_CHANNEL_ID}/messages", headers = headers, data = response)
                    target.saveTarget(i)
                    target.updateTargets()
            time.sleep(POLLING_RATE)



if __name__ == '__main__':
    #run checkStatusUpdate every POLLING_RATE seconds in a different thread
    threading.Timer(0, client.checkStatusUpdate,[client]).start()
    client = client()
    client.run(DISCORD_BOT_TOKEN)