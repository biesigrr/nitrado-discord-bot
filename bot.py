import os
import discord
import requests

from dotenv import load_dotenv

load_dotenv()
NITRADO_TOKEN = os.getenv('NITRADO_TOKEN')
NITRADO_SERVICE_ID = os.getenv('NITRADO_SERVICE_ID')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
AUTHORIZED_DISCORD_IDS = os.getenv("AUTHORIZED_DISCORD_IDS").split(',')

client = discord.Client()


def get(endpoint):
    return requests.get('https://api.nitrado.net/{0}'.format(endpoint),
                        headers={"Authorization": "Bearer {0}".format(NITRADO_TOKEN)})


def post(endpoint, params):
    return requests.post('https://api.nitrado.net/{0}'.format(endpoint),
                         headers={"Authorization": "Bearer {0}".format(
                             NITRADO_TOKEN)},
                         data=params)


def stop(message):
    return post('services/{0}/gameservers/stop'.format(NITRADO_SERVICE_ID), {"message": message, "stop_message": message})


def start(message):
    return post('services/{0}/gameservers/restart'.format(NITRADO_SERVICE_ID), {"message": message, "restart_message": message})


def get_details():
    return get('services/{0}/gameservers'.format(NITRADO_SERVICE_ID))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if str(message.author.id) not in AUTHORIZED_DISCORD_IDS:
        return

    if message.content == "server stop":
        req = stop('Discord user \'{0}\' requested server stop'.format(
            message.author.name))

        if req.status_code != 200:
            await message.channel.send('Request to NitrAPI failed: {0}'.format(req.status_code))
        else:
            json = req.json()
            await message.channel.send('[{0}]: {1}'.format(json['status'], json['message']))

    if message.content == "server start":
        req = start('Discord user \'{0}\' requested server start'.format(
            message.author.name))

        if req.status_code != 200:
            await message.channel.send('Request to NitrAPI failed: {0}'.format(req.status_code))
        else:
            json = req.json()
            await message.channel.send('[{0}]: {1}'.format(json['status'], json['message']))

    if message.content == "server status":
        req = get_details()

        if req.status_code != 200:
            await message.channel.send('Request to NitrAPI failed: {0}'.format(req.status_code))
        else:
            json = req.json()
            await message.channel.send('[{0}]: {1}'.format(json['status'], json['data']['gameserver']['status']))

client.run(DISCORD_TOKEN)
