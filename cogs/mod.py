import discord
from discord.ext import commands
import pyfiglet


class Mod:
    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx, error):
        if ctx.cog != self.bot.get_cog('Mod'):
            return
        if isinstance(error, commands.errors.BadArgument):
            await ctx.send('\N{HEAVY EXCLAMATION MARK SYMBOL} Invalid member passed!')

    async def answer_done(self, ctx):
        try:
            await ctx.message.add_reaction('\u2705')
        except discord.Forbidden:
            await ctx.send('Done')

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def muteall(self, ctx):
        """Denies the @everyone role from sending messages"""
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await self.answer_done(ctx)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def unmuteall(self, ctx):
        """Allows the @everyone role to send messages"""
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=None)
        await self.answer_done(ctx)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def mute(self, ctx, user: discord.Member):
        """Denies someone from sending messages"""
        await ctx.channel.set_permissions(user, send_messages=False)
        await self.answer_done(ctx)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def unmute(self, ctx, user: discord.Member):
        """Allows someone to send messages"""
        perms = ctx.channel.overwrites_for(user)
        perms.send_messages = None
        if not perms.is_empty():
            await ctx.channel.set_permissions(user, send_messages=None)
        else:
            await ctx.channel.set_permissions(user, overwrite=None)
        await self.answer_done(ctx)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def block(self, ctx, user: discord.Member):
        """Denies someone from viewing the channel"""
        await ctx.channel.set_permissions(user, read_messages=False)
        await self.answer_done(ctx)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def unblock(self, ctx, user: discord.Member):
        """Allows someone to view the channel"""
        perms = ctx.channel.overwrites_for(user)
        perms.read_messages = None
        if not perms.is_empty():
            await ctx.channel.set_permissions(user, read_messages=None)
        else:
            await ctx.channel.set_permissions(user, overwrite=None)
        await self.answer_done(ctx)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ben(self, ctx, user: discord.Member = None):
        """Bens a member"""
        await ctx.send(f'```http\n{pyfiglet.figlet_format("404: hammer not found")}```')

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, days: str, *, reason: str):
        """Bans a member and deletes the last X days of messages."""
        try:
            days = int(days)
            if days > 7:
                days = 7
            elif days < 0:
                days = 0
        except Exception as e:
            reason = ' '.join([days, reason])
            days = 0
        await ctx.guild.ban(user, reason=reason, delete_message_days=days)


def setup(bot):
    bot.add_cog(Mod(bot))
