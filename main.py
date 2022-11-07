import os
import cv2
from datetime import datetime as d
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from discord import File
from telethon import TelegramClient, events
from config import config
from os import getcwd
from modules.logger import Logger
from modules.imageManip import add_watermark

TELEGRAM_API_ID = config.get('TELEGRAM_API_ID')
TELEGRAM_API_HASH = config.get('TELEGRAM_API_HASH')
DISCORD_TOKEN = config.get('DISCORD_TOKEN')
GUILD_ID = int(config.get('GUILD_ID'))
FORWARD = config.get('FORWARD')
BLACK_LISTED_KEYWORDS = list(config.get("BLACK_LISTED_KEYWORDS"))

MESSAGE_SEPARATOR = config.get('MESSAGE_SEPARATOR')
FILTER_KEYWORDS = config.get('FILTER_KEYWORDS')

telegram_client = TelegramClient('test', TELEGRAM_API_ID, TELEGRAM_API_HASH)
telegram_logger = Logger('TELEGRAM')

discord_client = commands.Bot(command_prefix='!')
discord_logger = Logger('DISCORD')


@discord_client.event
async def on_ready():
    global d
    discord_logger.info(f'Logged in as {discord_client.user}')

@discord_client.command(    )
@has_permissions(administrator=True)
async def restart(ctx):
    await ctx.send(f"{ctx.author} Restarting...")
    os.system("./restart.sh")


@telegram_client.on(events.NewMessage())
async def my_event_handler(event):
    if not discord_client.is_ready():
        return telegram_logger.info('Discord Client is not ready.')

    stripped_channel_id = str(event.chat_id)[4:]

    # Check if the channel is in the forward list
    if stripped_channel_id not in FORWARD:
        return telegram_logger.info(f'{stripped_channel_id} is not enabled to be forwarded.')

    telegram_logger.info(f'Message received from {event.chat_id}')

    message = event.message.message

    for keyword in FILTER_KEYWORDS:
        if keyword in message:
            message = message.replace(keyword, '')

    # Check if the message contains blacklisted keywords from this particular channel
    for keyword in FORWARD[stripped_channel_id]['FILTER_KEYWORDS']:
        if keyword in message:
            message = message.replace(keyword, '')

    # check if the message contains blacklisted keywords
    if any(x in message for x in FORWARD[stripped_channel_id]['BLACK_LISTED_KEYWORDS']):
        return telegram_logger.info('Message contains blacklisted keywords.')

    forward_data = FORWARD[stripped_channel_id]
    guild = discord_client.get_guild(int(GUILD_ID))
    header = forward_data['header']
    channel = guild.get_channel(int(forward_data['channel_id']))

    last_message = ""
    async for x in channel.history(limit=1):
        last_message = x

    if not str(last_message) == str(message):


        media_path = await event.message.download_media()

        if forward_data["send_pictures"] == "True" and forward_data["black_list"] == "True" and not any(x in message for x in BLACK_LISTED_KEYWORDS) or forward_data["send_pictures"] == "True" and forward_data["black_list"] == "False":

            if message and media_path and "https://" in str(message) or message and not media_path:
                await channel.send(header)
                await channel.send(message)

            elif media_path and not "https://" in str(message):
                await channel.send(header)
                try:
                    await channel.send(message)
                except:
                    pass
                image = cv2.imread(getcwd() + "/" + media_path)
                new_image_with_watermark = add_watermark(image)
                cv2.imwrite(getcwd() + "/" + media_path, new_image_with_watermark)
                await channel.send(file=File(media_path))

        elif forward_data["send_pictures"] == "False" and forward_data["black_list"] == "True" and not any(x in message for x in BLACK_LISTED_KEYWORDS) or forward_data["send_pictures"] == "False" and forward_data["black_list"] == "False":
            if message and media_path and "https://" in str(message) or message and not media_path:
                link_less = message.split(" ")
                link_less = [word + " " for word in link_less if not "https://" in word]

                temp_string = ""

                for x in link_less:
                    temp_string += x

                message = str(temp_string)

                abc = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

                if any(x in message for x in abc):
                    await channel.send(header)
                    await channel.send(message)

            elif media_path and not "https://" in str(message):
                await channel.send(header)
                try:
                    await channel.send(message)
                except:
                    pass

        try:
            os.remove(getcwd() + "/" + media_path)
        except:
            pass

        try:
            await channel.send(MESSAGE_SEPARATOR)
        except:
            pass

        log_channel = guild.get_channel(869952469516570694)
        # log_channel = guild.get_channel(928287311836364802)     # rootz testing
        await log_channel.send(f'- A message was forwarded from `{event.chat_id}` to `{channel}` (`{channel.id}`)')
        telegram_logger.info(f'A message was forwarded from {event.chat_id} to {channel}({channel.id})')


with telegram_client as tc:
    tc.loop.create_task(tc.connect())
    tc.loop.create_task(discord_client.start(DISCORD_TOKEN))
    tc.loop.run_forever()
