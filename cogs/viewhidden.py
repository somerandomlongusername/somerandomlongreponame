import discord
from discord.ext import commands


class ViewHidden():
    def __init__(self, bot):
        self.bot = bot
        self.channel_dump = []
        self.role_dump = []
        self.role_member_dump = []

    async def __local_check(self, ctx):
        if ctx.bot.user.bot:
            return await ctx.bot.is_owner(ctx.author)
        else:
            return True

    @commands.command()
    async def channels(self, ctx, id: int):
        """Sends a list of the given guild's channels"""
        guild = self.bot.get_guild(id)
        l = sorted([c for c in guild.channels if isinstance(c.type, discord.TextChannel)], key=lambda c: c.position)
        my_str = []
        for i in l:
            my_str .append(f'{i.id}: #{i.name}\n')
        await ctx.send('```http\n{}```'.format("\n".join(my_str)))

    @commands.command()
    async def roles(self, ctx, id: int):
        """Sends a list of the given guild's roles"""
        guild = self.bot.get_guild(id)
        l = sorted(guild.roles, key=lambda r: r.position)
        my_str = []
        for i in l:
            my_str .append(f'{i.id}: @{i.name}\n')
        await ctx.send('```http\n{}```'.format("\n".join(my_str)))

    @commands.command(pass_context=True)
    async def bans(self, ctx, id: int, which: str = 'amount'):
        """Send the amount or list of people banned in a given guild"""
        guild = self.bot.get_guild(id)
        if not guild.me.guild_permissions.ban_members:
            await ctx.send('No perms!')
            return
        if which == 'list':
            bans = await guild.bans()
            l = []
            for ban in bans:
                if ban[0] is None:
                    l.append(f'{ban[1]} was banned with no reason given')
                else:
                    l.append(f'{ban[1]} was {ban[0][0].lower() + ban[0][1:]}')
            await ctx.send('```http\n{}```'.format('\n'.join(l)))
        else:
            amount = len([b for b in await guild.bans()])
            await ctx.send(f'There are {amount} users banned in guild {guild.name}')

    @commands.command(pass_context=True)
    async def role(self, ctx, id: int, role: discord.Role, which: str = 'amount'):
        guild = self.bot.get_guild(id)
        role_members = [m for m in guild.members if role in m.roles]
        if which == 'list':
            await ctx.send('```http\n{}```'.format("\n".join(role_members)))
        else:
            await ctx.send(f'There are {len(role_members)} users with the role {role} in guild {guild}')

    @commands.command()
    async def emote(self, ctx, e: discord.Emoji):
        await ctx.send(e.guild)


def setup(bot):
    bot.add_cog(ViewHidden(bot))
