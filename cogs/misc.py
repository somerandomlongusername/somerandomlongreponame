import discord
from discord.ext import commands
import random
import asyncio
import time
import json
import unicodedata
from .utils import checks, funcs
import pyfiglet


class Misc:
    def __init__(self, bot):
        self.bot = bot
        self.file_path = '{}misc.json'.format(self.bot.my_data_files)

        try:
            with open(self.file_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {'game': 'absolutely nothing', 'gamestream': False}
            self.write_config()

    def write_config(self):
        with open(self.file_path, 'w+') as f:
            json.dump(self.config, f, indent=4)

    async def on_ready(self):
        if self.config['gamestream']:
            await self.bot.change_presence(game=discord.Game(name=self.config['game'], url='http://www.twitch.tv/wat', type=1))
        else:
            await self.bot.change_presence(game=discord.Game(name=self.config['game']))

    @commands.command()
    @checks.is_owner()
    async def game(self, ctx, streaming: bool, *, game: str):
        """Sets the bot's Playing status"""
        self.config['game'] = game
        self.config['gamestream'] = streaming
        self.write_config()
        if self.config['gamestream']:
            await self.bot.change_presence(game=discord.Game(name=self.config['game'], url='http://www.twitch.tv/clever_the_bot', type=1))
        else:
            await self.bot.change_presence(game=discord.Game(name=self.config['game']))
        await ctx.send('Aye \N{OK HAND SIGN}')

    # @commands.command()
    # async def info(self, ctx):
    #   total_members = sum(len(s.members) for s in self.bot.guilds)
    #   total_online  = sum(1 for m in self.bot.get_all_members() if m.status != discord.Status.offline)
    #   unique_members = set(self.bot.get_all_members())
    #   unique_online = sum(1 for m in unique_members if m.status != discord.Status.offline)

    #   text_chans = len([chan for chan in self.bot.get_all_channels() if isinstance(chan, discord.TextChannel)])
    #   voice_chans = len([chan for chan in self.bot.get_all_channels() if isinstance(chan, discord.VoiceChannel)])
    #   total_chans = text_chans+voice_chans

    #   text = '''Please PM me (spy) for more information about the bot.\nHosted on an OrangePi Zero privately.'''
    #   em = discord.Embed(description=text, colour=7506394)
    #   owner = await self.bot.get_user_info(self.bot.owner_id)
    #   em.set_author(name='{}'.format(owner), icon_url=owner.avatar_url)

    #   members = '%s total\n%s online\n%s unique\n%s unique online' % (total_members, total_online, len(unique_members), unique_online)
    #   em.add_field(name='Members', value=members)
    #   em.add_field(name='Guilds', value=len(self.bot.guilds))
    #   em.add_field(name='Channels', value='{} total\n{} text\n{} voice'.format(total_chans, text_chans, voice_chans))
    #   em.set_footer(text='Made with discord.py version 0.16.8, python 3.6.1', icon_url='http://i.imgur.com/5BFecvA.png')
    #   await ctx.send(embed=em)

    @commands.command()
    async def quote(self, ctx, id: int, chan: int = None, guil: int = None):
        """Quotes a message by id"""
        if guil is None:
            guil = ctx.guild
        else:
            guil = self.bot.get_guild(guil)
        if chan is None:
            chan = ctx.channel
        else:
            chan = guil.get_channel(chan)

        if self.bot.user.bot:
            m = await chan.get_message(id)
        else:
            m = await funcs.fast_get_message(chan, id)

        t = time.strftime("%H:%M:%S %a %d %b %Y", m.created_at.timetuple())
        em = discord.Embed(description=m.content)
        em.set_author(name=m.author.name, icon_url=m.author.avatar_url)
        em.set_footer(text=t)
        em.add_field(name=guil.name, value=chan.mention, inline=True)
        await ctx.send(embed=em)

    @commands.command(pass_context=True)
    async def ping(self, ctx):
        """Replies with a pong!"""
        before = time.monotonic()
        msg = await ctx.send('Pong!')
        after = time.monotonic()
        time_taken = after - before
        time_taken *= 1000
        time_taken = int(time_taken)
        em = discord.Embed(title='Pong', type='rich', description='\U0001f3d3 {0}ms'.format(time_taken),
                           colour=discord.Colour(int('FF0000', 16)))
        await msg.edit(content='', embed=em)

    @commands.command(hidden=True)
    async def lenny(self, ctx):
        """Displays a random lenny face"""
        lenny = random.choice([
            "( ͡° ͜ʖ ͡°)", "( ͠° ͟ʖ ͡°)", "ᕦ( ͡° ͜ʖ ͡°)ᕤ", "( ͡~ ͜ʖ ͡°)",
            "( ͡o ͜ʖ ͡o)", "͡(° ͜ʖ ͡ -)", "( ͡͡ ° ͜ ʖ ͡ °)﻿", "(ง ͠° ͟ل͜ ͡°)ง",
            "ヽ༼ຈل͜ຈ༽ﾉ", "( ͡°( ͡° ͜ʖ( ͡° ͜ʖ ͡°)ʖ ͡°) ͡°)", "/\╲/\\╭( ͡° ͡° ͜ʖ ͡° ͡°)╮/\\╱\\"
        ])
        await ctx.send(lenny)

    @commands.command(hidden=True)
    async def shrug(self, ctx):
        """Displays a random shrug"""
        shrug = random.choice([
            "¯\\\\_(ツ)_/¯", "¯\\\\(ツ)/¯", "ʅ(ツ)ʃ", "乁(ツ)ㄏ",
            "¯\\\\_(シ)_/¯", "ʅ(°_°)ʃ", "ʅ(°‿°)ʃ", "¯\\\\_(°_°)_/¯",
            "¯\\\\_(°ᴥ°)_/¯", "¯\\\\_(ಠ_ಠ)_/¯"
        ])
        await ctx.send(shrug)

    @commands.command(pass_context=True, hidden=True)
    async def rip(self, ctx, *, name: str):
        """Displays a tombstone with a person's name"""
        tomb = """```
                  _  /)
                 mo / )
                 |/)\)
                  /\_
                  \__|=
                 (  )
                 __)(__
           _____/     \_____
          |  _   ___   _   ||
          | | \  |   | \  ||
          | |  |    |   |  | ||
          | |_/  |   |_/  ||
          | | \  |   |  ||
          | |  \    |   |   ||
          | |   \. _|_. | .  ||
          |               ||
          |{}||
          |               ||
  *    | *   ** * **   |**    **
   \))ejm97/.,(//,,..,,\||(,,.,\\,.((//```"""
        # 18 spaces for name
        spaces = (18 - len(name)) / 2
        if ((spaces * 10) % 10 != 0):
            name = ' ' * int(spaces) + name + ' ' * int(spaces + 0.5)
        else:
            spaces = int(spaces)
            name = ' ' * spaces + name + ' ' * spaces
        await ctx.send(tomb.format(name))
        await ctx.message.delete()

    @commands.command()
    async def choose(self, ctx, *choices):
        """Chooses between several choices"""
        await ctx.send(random.choice(choices))

    @commands.command()
    @checks.is_owner()
    async def say(self, ctx, *, message: str):
        """Says what you tell it to say"""
        await ctx.message.delete()
        await ctx.send(message)

    @commands.command()
    @checks.is_owner()
    async def bsay(self, ctx, *, text: str):
        """Says something in regional indicators"""
        letters = {'a': '\N{REGIONAL INDICATOR SYMBOL LETTER A}', 'b': '\N{REGIONAL INDICATOR SYMBOL LETTER B}',
                   'c': '\N{REGIONAL INDICATOR SYMBOL LETTER C}', 'd': '\N{REGIONAL INDICATOR SYMBOL LETTER D}',
                   'e': '\N{REGIONAL INDICATOR SYMBOL LETTER E}', 'f': '\N{REGIONAL INDICATOR SYMBOL LETTER F}',
                   'g': '\N{REGIONAL INDICATOR SYMBOL LETTER G}', 'h': '\N{REGIONAL INDICATOR SYMBOL LETTER H}',
                   'i': '\N{REGIONAL INDICATOR SYMBOL LETTER I}', 'j': '\N{REGIONAL INDICATOR SYMBOL LETTER J}',
                   'k': '\N{REGIONAL INDICATOR SYMBOL LETTER K}', 'l': '\N{REGIONAL INDICATOR SYMBOL LETTER L}',
                   'm': '\N{REGIONAL INDICATOR SYMBOL LETTER M}', 'n': '\N{REGIONAL INDICATOR SYMBOL LETTER N}',
                   'o': '\N{REGIONAL INDICATOR SYMBOL LETTER O}', 'p': '\N{REGIONAL INDICATOR SYMBOL LETTER P}',
                   'q': '\N{REGIONAL INDICATOR SYMBOL LETTER Q}', 'r': '\N{REGIONAL INDICATOR SYMBOL LETTER R}',
                   's': '\N{REGIONAL INDICATOR SYMBOL LETTER S}', 't': '\N{REGIONAL INDICATOR SYMBOL LETTER T}',
                   'u': '\N{REGIONAL INDICATOR SYMBOL LETTER U}', 'v': '\N{REGIONAL INDICATOR SYMBOL LETTER V}',
                   'w': '\N{REGIONAL INDICATOR SYMBOL LETTER W}', 'x': '\N{REGIONAL INDICATOR SYMBOL LETTER X}',
                   'y': '\N{REGIONAL INDICATOR SYMBOL LETTER Y}', 'z': '\N{REGIONAL INDICATOR SYMBOL LETTER Z}'}
        message = []
        for char in text:
            if char.isalpha():
                emote = u'{}'.format(letters[char.lower()])
            elif char.isdigit():
                emote = u'{}\N{COMBINING ENCLOSING KEYCAP}'.format(char)
            elif char == ' ':
                emote = u'\N{BLACK LARGE SQUARE}'
            else:
                emote = char
            message.append(emote)
        await ctx.message.delete()
        await ctx.send(' '.join(message))

    @commands.command(hidden=True)
    @checks.is_owner()
    async def repeat(self, ctx, num: int, *, message: str):
        """Repeats a message multiple times"""
        await ctx.message.delete()
        for i in range(num):
            await asyncio.sleep(0.25)
            await self.bot.say(message)

    @commands.command()
    async def spoken(self, ctx, number: int = 50, poop: discord.Member = None, ch: discord.TextChannel = None):
        """How many times has a given user spoken in a given channel?"""
        if not poop:
            poop = ctx.author
        if not ch:
            ch = ctx.channel
        counter = 0
        async for message in ch.history(limit=number):
            if message.author == poop:
                counter += 1
        await ctx.send(f'{poop} is the author of {counter} out of {number} past messsages in channel {ch.mention}')

    @commands.command()
    async def charinfo(self, ctx, *, characters: str):
        """Shows you information about a number of characters."""
        if len(characters) > 20:
            error = f'Too many characters ({len(characters)}/20)'
            await ctx.send(error)
            return
        fmt = '\\U{0:>08}: {1} - \\{2} <http://www.fileformat.info/info/unicode/char/{0}>'

        def to_string(c):
            digit = format(ord(c), 'x')
            name = unicodedata.name(c, 'Name not found.')
            return fmt.format(digit, name, c)
        result = '\n'.join(map(to_string, characters))
        if ctx.channel.permissions_for(ctx.me).embed_links is False:
            await ctx.send(result)
        else:
            msg = discord.Embed(description=result, color=discord.Color(0xFF00D1))
            await ctx.send(embed=msg)

    @commands.command(hidden=True)
    @checks.is_owner()
    async def ascii(self, ctx, *, message: str):
        """Says a message in ascii"""
        await ctx.message.delete()
        try:
            await ctx.send(f'```http\n{pyfiglet.figlet_format(message)}\n```')
        except discord.HTTPException:
            await ctx.send('Message too long to say!')

    @commands.command(hidden=True)
    @checks.is_owner()
    async def lascii(self, ctx, lang: str, font: str, *, message: str):
        """Says a message in ascii with the desired lang and font"""
        await ctx.message.delete()
        try:
            await ctx.send(f'```{lang}\n{pyfiglet.figlet_format(message, font=font)}\n```')
        except discord.HTTPException:
            await ctx.send('Message too long to say!')


def setup(bot):
    bot.add_cog(Misc(bot))
