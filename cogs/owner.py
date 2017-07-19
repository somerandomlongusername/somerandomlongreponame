import discord
from discord.ext import commands
import asyncio
from .utils import checks


class Owner:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @checks.is_owner()
    async def load(self, ctx, extension_name: str):
        """Loads an extension"""
        try:
            self.bot.load_extension(extension_name)
        except(AttributeError, ImportError) as e:
            await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
            return
        await ctx.send("{} loaded.".format(extension_name))

    @commands.command(hidden=True)
    @checks.is_owner()
    async def unload(self, ctx, extension_name: str):
        """Unloads an extension"""
        self.bot.unload_extension(extension_name)
        await ctx.send("{} unloaded.".format(extension_name))

    @commands.command(hidden=True)
    @checks.is_owner()
    async def reload(self, ctx, extension_name: str):
        """Reloads an extension"""
        await ctx.invoke(self.unload, extension_name)
        await ctx.invoke(self.load, extension_name)

    @commands.command(hidden=True)
    @checks.is_owner()
    async def off(self, ctx):
        """turns the bot off"""
        await self.bot.logout()


def setup(bot):
    bot.add_cog(Owner(bot))
