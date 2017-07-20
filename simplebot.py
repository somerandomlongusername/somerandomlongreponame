from discord.ext import commands
import logging
import json
import time

with open('configsimple.json', 'r') as f:
    config = json.load(f)

level = logging.INFO if config['INFOLOG'] else logging.WARNING
logging.basicConfig(level=level)

prefix = config['PREFIX']
token = config['TOKEN']
startup_extensions = config['EXTENSIONS']
description = '''A simple bot'''
bot = commands.Bot(command_prefix=prefix, description=description, owner_id=config['OWNER'])
bot.my_data_files = 'data/clever/'


@bot.event
async def on_ready():
    end_time = int(round(time.time() * 1000))
    time_taken = end_time - start_time
    print('---------------------')
    print('Logged in succesfully! Info:')
    print('Time taken: {}ms'.format(time_taken))
    print('User: {}'.format(bot.user.name))
    print('ID: {}'.format(bot.user.id))
    print('Prefix: {}'.format(bot.command_prefix))
    print('{} guilds'.format(len(bot.guilds)))
    print('{} DMs'.format(len(bot.private_channels)))
    print('---------------------')
    bot.test_channel = bot.get_channel(config['CHANNEL'])

if __name__ == "__main__":
    start_time = int(round(time.time() * 1000))
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
            print('Loaded extension {} successfully'.format(extension))
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

    bot.run(token)
