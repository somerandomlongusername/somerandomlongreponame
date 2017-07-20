import discord
from discord.ext import commands
import json
import asyncio


class Brawl:
    def __init__(self, bot):
        self.bot = bot
        self.file_path = '{}brawl.json'.format(self.bot.my_data_files)

        self.no_join = discord.PermissionOverwrite(connect=False, speak=False)
        self.join = discord.PermissionOverwrite(connect=True, speak=True)

        try:
            with open(self.file_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {'channels': {}}
            self.write_config()

    def write_config(self):
        with open(self.file_path, 'w+') as f:
            json.dump(self.config, f, indent=4)

    @commands.group(name='brawl', invoke_without_command=True)
    async def brawl(self, ctx, *users: discord.Member):
        """
        Creates and manages brawl voice channels
        Mention your friends after this group to create a voice channel for you and them.
        Incorrect usage shows this help command.
        """
        if users == ():
            raise commands.CommandError
        if ctx.author.id not in self.config['channels']:
            overwrites = {
                ctx.guild.default_role: self.no_join,
                ctx.author: self.join,
            }
            overwrites.update({u: self.join for u in users})
            ch = await ctx.guild.create_voice_channel(
                f'\N{MICROPHONE} {ctx.author.name}',
                overwrites=overwrites,
                reason='Brawl voice channel')

            self.config['channels'][ctx.author.id] = ch.id
            self.write_config()
            link = await ch.create_invite(reason='Brawl vc invite')
            await ctx.send((
                f'{ctx.author.mention}, your voice channel has been created!\n'
                f'Manage it with `{ctx.prefix}brawl` and use the following link to join it:\n\n{link}'))

        else:
            ch = ctx.guild.get_channel(self.config['channels'][ctx.author.id])
            link = ch.create_invite(reason='Brawl vc invite', unique=False)
            await ctx.send((
                f'Sorry, but you can only have one voice channel at a time, '
                f'{ctx.author.mention}. Here\'s a link to your current channel:\n{link}'))

    @brawl.error
    async def brawl_error(self, ctx, error):
        """Sends help for brawl command on error"""
        for page in await self.bot.formatter.format_help_for(ctx, ctx.command):
            await ctx.send(page)

    @brawl.command()
    async def delete(self, ctx):
        """Deletes your voice channel"""
        id = self.config['channels'].get(ctx.author.id)
        if id is None:
            await ctx.send(f'{ctx.author.mention}, you do not *have* a voice channel I can delete!')
            return

        def check(msg):
            if msg.author != ctx.author:
                return False
            if msg.channel != ctx.channel:
                return False
            return True

        await ctx.send(f'Are you sure you want to delete your voice channel {ctx.author.mention}?')
        try:
            ret = await self.bot.wait_for("message", check=check, timeout=10)
        except asyncio.TimeoutError:
            ctx.send(f'{ctx.author.mention}, you took too long. Cancelling channel deletion.')
            return
        if ret.content.startswith('y'):
            ch = ctx.guild.get_channel(id)
            await ch.delete()
            await ctx.send('Channel successfully deleted!')
            self.config['channels'].pop(ctx.author.id)
            self.write_config()
        else:
            await ctx.send('Cancelling channel deletion.')

    @brawl.command()
    @commands.has_permissions(manage_channels=True)
    async def fdelete(self, ctx, user: discord.Member=None):
        """Forcefully deletes someone's channel"""
        id = self.config['channels'].get(user.id)
        if id is None:
            await ctx.send(f'{user.name} does not have a voice channel to delete')
            return
        ch = ctx.guild.get_channel(id)
        await ch.delete()
        await ctx.send('Channel successfully deleted!')
        self.config['channels'].pop(user.id)
        self.write_config()

    @brawl.command()
    async def allow(self, ctx, *users: discord.Member):
        """Allows the specified users to join your voice channel"""
        id = self.config['channels'].get(ctx.author.id)
        if id is None:
            await ctx.send(f'{ctx.author.mention}, you do not *have* a voice channel I can allow people into')
            return
        ch = ctx.guild.get_channel(id)
        for u in users:
            await ch.set_permissions(u, overwrite=self.join)
        link = await ch.create_invite(reason='Brawl vc link', unique=False)
        await ctx.send(f'Done. Here\'s a link to join the channel:\n\n{link}')

    @brawl.command()
    async def deny(self, ctx, *users: discord.Member):
        """Denies the specified users from joining your voice channel"""
        id = self.config['channels'].get(ctx.author.id)
        if id is None:
            await ctx.send(f'{ctx.author.mention}, you do not *have* a voice channel I can allow people into')
            return
        ch = ctx.guild.get_channel(id)
        for u in users:
            await ch.set_permissions(u, overwrite=self.no_join)
        await ctx.send('Done.')


def setup(bot):
    bot.add_cog(Brawl(bot))
