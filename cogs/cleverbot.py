import discord
from discord.ext import commands
from .utils import checks
import json

from collections import deque
from hashlib import md5
from urllib.parse import quote, urlencode

import requests

BASE_URI = 'https://www.cleverbot.com/webservicemin'


class Cleverbot:
    def __init__(self):
        self.session = requests.Session()
        self.sessionid = ''
        self.defaults = {}
        self.history = deque(maxlen=20)
        self.last_id = ''
        self.count = 1
        self.session.get('https://www.cleverbot.com')
        self.session.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                                'like Gecko) Chrome/59.0.3071.115 Safari/537.36'}

    def _format_stimulus(self, stimulus):
        stimulus = 'stimulus=' + quote(stimulus)
        if self.history:
            count = 1
            for i in self.history:
                count += 1
                stimulus += '&vText{}={}'.format(count, quote(i))
        stimulus += '&cb_settings_language=en&cb_settings_scripting=no'
        if self.sessionid:
            stimulus += '&sessionid=' + self.sessionid
        stimulus += '&islearning=1&icognoid=wsf&icognocheck='
        stimulus += md5(stimulus[7:33].encode()).hexdigest()
        return stimulus

    def _format_uri(self, stimulus=None, ignore_out=False):
        uri = 'uc=UseOfficialCleverbotAPI'
        if stimulus is None:
            return uri
        uri += '&out='
        if self.history and not ignore_out:
            uri += quote(self.history[0])
        data = {
            'in': stimulus,
            'bot': 'c',
            'cbsid': self.sessionid,
            'ns': self.count,
            'al': '',
            'dl': '',
            'flag': '',
            'user': '',
            'mode': '1',
            'alt': '0',
            'reac': '',
            'emo': '',
            'sou': 'website',
            'xed': ''
        }
        xai = self.session.cookies.get('XAI')
        if xai is not None:
            self.xai = xai
        else:
            xai = self.xai
        if self.last_id:
            xai += ',' + self.last_id
        data['xai'] = xai
        uri += '&' + urlencode(data, quote_via=quote, safe=',')
        return '?' + uri

    def _parse_response(self, resp, query):
        assert resp.status_code == 200, 'API returned non-200 status code'
        lines = resp.text.split('\r')
        self.history.appendleft(query)
        self.history.appendleft(lines[0])
        self.sessionid = lines[1]
        self.last_id = lines[2]
        self.session.get(BASE_URI + self._format_uri(ignore_out=True))
        self.count += 1
        return lines[0]

    def ask(self, query):
        if not self.history:
            resp = self.session.post(BASE_URI + self._format_uri(), data=self._format_stimulus(query))
            return self._parse_response(resp, query)
        resp = self.session.post(BASE_URI + self._format_uri(query), data=self._format_stimulus(query))
        return self._parse_response(resp, query)


class Clever:
    def __init__(self, bot):
        self.bot = bot
        self.clevers = {}

        self.file_path = '{}clever.json'.format(self.bot.my_data_files)

    async def on_ready(self):
        try:
            with open(self.file_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print([s for s in self.bot.guilds])
            self.config = {str(s.id): None for s in self.bot.guilds}
            self.write_config()

    def write_config(self):
        with open(self.file_path, 'w+') as f:
            json.dump(self.config, f, indent=4)

    @commands.command()
    @checks.is_owner()
    async def cleverlock(self, ctx, *channels: discord.TextChannel):
        self.config[str(ctx.guild.id)] = [c.id for c in channels]
        self.write_config()

    @commands.command()
    async def creset(self, ctx):
        self.clevers[ctx.channel.id].history = deque(maxlen=20)
        em = discord.Embed(description='This question/inquiry has been fully answered.\nPlease do not reply to it after this message.\n(A.k.a. the bot has been reset)', type='rich', colour=0x7289DA)
        em.set_footer(text='Abuse of this command may get cleverbot indefinitely shut down.')
        await ctx.send(embed=em)

    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if isinstance(message.channel, discord.abc.PrivateChannel):
            return
        if str(message.guild.id) not in self.config:
            self.config[str(message.guild.id)] = []
        if message.channel.id not in self.clevers:
            self.clevers[message.channel.id] = Cleverbot()
        if message.channel.id in self.config[str(message.guild.id)]:
            if not message.content.startswith('#'):
                return
            async with message.channel.typing():
                cl = self.clevers[message.channel.id]
                reply = cl.ask(message.content[1:].strip())
                em = discord.Embed(description=reply, type='rich', colour=0x7289DA)
                await message.channel.send(embed=em)


def setup(bot):
    bot.add_cog(Clever(bot))
