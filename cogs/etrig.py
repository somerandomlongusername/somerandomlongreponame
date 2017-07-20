import discord
from discord.ext import commands
import json
from .utils import checks


class ETrig:
    def __init__(self, bot):
        self.bot = bot
        self.file_path = '{}etrigs.json'.format(self.bot.my_data_files)

        try:
            with open(self.file_path, 'r') as f:
                self.etrigs = json.load(f)
        except FileNotFoundError:
            self.etrigs = {'channels': [], 'etrigs': {}}
            self.write_config()

    def write_config(self):
        with open(self.file_path, 'w+') as f:
            json.dump(self.etrigs, f, indent=4)

    async def on_message(self, message):
        # if message.channel is None:
        #     return
        if isinstance(message.channel, discord.abc.PrivateChannel):
            return
        if message.author.bot:
            return
        if message.channel.id not in self.etrigs['channels']:
            return

        for etrig in self.etrigs['etrigs']:
            if etrig.lower() in message.content.lower():
                if self.etrigs['etrigs'][etrig]['before'] > 0:
                    async for mess in message.channel.history(limit=self.etrigs['etrigs'][etrig]['before'], before=message, reverse=True):
                        m = mess
                        break
                else:
                    m = message
                if self.etrigs['etrigs'][etrig]['strict'] and (len(etrig) < len(message.content)):
                    continue
                if self.etrigs['etrigs'][etrig]['strict'] and (etrig not in message.content):
                    continue

                try:
                    for e in self.etrigs['etrigs'][etrig]['value']:
                        try:
                            if len(e) >= 6 and ':' in e:
                                await m.add_reaction(e[2:-1])
                            else:
                                await m.add_reaction(e)
                        except discord.HTTPException:
                            pass
                except discord.Forbidden:
                    print('No reaction perms :(')

    @commands.group(invoke_without_command=True)
    async def etrig(self, ctx):
        """Etrig command group"""
        if ctx.invoked_subcommand is None:
            for page in self.bot.formatter.format_help_for(ctx, ctx.command):
                await ctx.send(page)

    @etrig.command(name='set')
    @checks.is_owner()
    async def _set(self, ctx, key, value, strict: bool = True, before: int = 0):
        """Sets the value of an etrig"""
        self.etrigs['etrigs'][key] = {'value': value.split(' '), 'strict': strict, 'before': before}
        self.write_config()
        await ctx.message.add_reaction('\u2705')

    @etrig.command(name='toggle')
    @checks.is_owner()
    async def _toggle(self, ctx, id: int = None):
        """Toggles protection of a channel from etrigs"""
        if id is None:
            id = ctx.channel.id
        if id in self.etrigs['channels']:
            self.etrigs['channels'].remove(id)
        else:
            self.etrigs['channels'].append(id)
        self.write_config()
        await ctx.message.add_reaction('\u2705')

    @etrig.command(name='listening')
    @checks.is_owner()
    async def is_listened(self, ctx, id: int = None):
        """Is the given channel listened to?"""
        if id is None:
            id = ctx.channel.id
        if id in self.etrigs['channels']:
            await ctx.send(f'Channel {self.bot.get_channel(id).mention} *is* being listened to for etriggers')
        else:
            await ctx.send(f'Channel {self.bot.get_channel(id).mention} *is **not*** being listened to for etriggers')

    @etrig.command()
    @checks.is_owner()
    async def delete(self, ctx, *, key: str):
        """Deletes an etrig"""
        del self.etrigs['etrigs'][key.strip(' `')]
        self.write_config()
        await ctx.message.add_reaction('\u2705')

    @etrig.command()
    @checks.is_owner()
    async def clear(self, ctx, *, confirmation=None):
        """Deletes every single etrig. Cannot be undone"""
        if confirmation == 'yes seriously I wish to clear it':
            self.etrigs['etrigs'] = {}
            self.write_config()
            await ctx.message.add_reaction('\u2705')
        else:
            await ctx.send('To clear please append `yes seriously I wish to clear it` to the clear command')

    @etrig.command()
    async def list(self, ctx):
        """Lists every available etrig"""
        message = '\n'.join(sorted(self.etrigs['etrigs'].keys(), key=str.lower))
        message = '```http\n{}\n```'.format(message)
        await ctx.send(message)

    # @tag.command()
    # async def search(self, *, terms: str):
        # """Lists every tag with (search terms) in it"""
        # message = '\n'.join(sorted([key for key in self.etrigs.keys() if terms in key], key=str.lower))
        # message = '```http\n{}\n```'.format(message)
        # await self.bot.say(message)


def setup(bot):
    bot.add_cog(ETrig(bot))
