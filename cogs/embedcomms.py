import discord
from discord.ext import commands
import random
import json


class EmbedComms():
    def __init__(self, bot):
        self.bot = bot
        self.file_path = '{}embedcomms.json'.format(self.bot.my_data_files)
        self.time_format = '%d %b %Y %H:%M'

        try:
            with open(self.file_path, 'r') as f:
                self.config = json.load(f)
            if self.config == {}:
                self.config = {'colour': 0}
                self.write_config()
        except FileNotFoundError:
            self.config = {'colour': 0}
            self.write_config()

    def write_config(self):
        with open(self.file_path, 'w+') as f:
            json.dump(self.config, f, indent=4)

    def random_colour(self):
        return random.randint(0, 16777215)

    @commands.command()
    async def randcolour(self, ctx):
        """Shows a random colour"""
        await ctx.invoke(self.showcolour, self.random_colour())

    @commands.command()
    async def showcolour(self, ctx, colour: str):
        """Shows a sample of the colour (hex) you give to it"""
        this_colour = self.config['colours'].get(colour)
        if this_colour is None:
            this_colour = colour
        try:
            this_colour = discord.Colour(int(this_colour))
        except ValueError:
            this_colour = discord.Colour(int(this_colour, 16))
        em = discord.Embed(type='rich', description='Hex: {0} | RGB: {1.r},{1.g},{1.b}'.format(str(this_colour), this_colour), colour=this_colour)
        await ctx.send(embed=em)

    @commands.command()
    @commands.is_owner()
    async def setcolour(self, ctx, *, colour: str):
        """Sets embed colour for emsay"""
        this_colour = self.config['colours'].get(colour)
        if this_colour is None:
            this_colour = colour
        try:
            this_colour = int(this_colour)
        except ValueError:
            this_colour = int(this_colour, 16)
        self.config['colour'] = this_colour
        self.write_config()

    @commands.command()
    @commands.is_owner()
    async def col(self, ctx, name: str, colour: str):
        """Sets a name for a colour"""
        c = 0
        try:
            c = int(colour)
        except ValueError:
            c = int(colour, 16)
        self.config['colours'][name] = c
        self.write_config()

    @commands.command()
    async def collist(self, ctx):
        """Lists available named colours"""
        msg = []
        for colour in self.config['colours']:
            msg.append(colour)
        em = discord.Embed(title=f'Available colours. add with `{ctx.prefix}col`', description='\n'.join(msg), colour=discord.Colour(self.config['colour']))
        await ctx.send(embed=em)

    @commands.command()
    @commands.is_owner()
    async def emsay(self, ctx, title: str, *, content: str = ''):
        """Says something as an embed."""
        em = discord.Embed(title=title, type='rich', description=content, colour=discord.Colour(self.config['colour']))
        em.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        try:
            await ctx.message.edit(content='', embed=em)
        except discord.HTTPException:
            try:
                await ctx.send(embed=em)
            except discord.Forbidden:
                print('No perms for embedsay :(')

    @commands.command()
    async def gi(self, ctx):
        """Shows guild info"""
        my_colour = discord.Colour(self.random_colour())
        online_peeps = len([m for m in ctx.guild.members if m.status == discord.Status.online])

        guild_em = discord.Embed(title=f'{ctx.guild.name}', type='rich', description=f'Since {ctx.guild.created_at.strftime(self.time_format)}', colour=my_colour)
        guild_em.set_thumbnail(url=ctx.guild.icon_url)
        guild_em.add_field(name='Region', value=f'{ctx.guild.region}')
        guild_em.add_field(name='Users', value=f'{online_peeps}/{ctx.guild.member_count}')
        guild_em.add_field(name='Text channels', value=f'{len(ctx.guild.text_channels)}')
        guild_em.add_field(name='Voice channels', value=f'{len(ctx.guild.voice_channels)}')
        guild_em.add_field(name='Roles', value=f'{len(ctx.guild.roles)}')
        guild_em.add_field(name='Owner', value=f'{ctx.guild.owner}')
        guild_em.set_footer(text=f'Guild ID: {ctx.guild.id}')

        await ctx.send(embed=guild_em)

    @commands.command()
    async def ui(self, ctx, *, user: discord.Member=None):
        """Shows users's informations"""
        if user is None:
            user = ctx.author
        roles = [x for x in user.roles if x.name != "@everyone"]
        joined_at = user.joined_at
        since_created = (ctx.message.created_at - user.created_at).days
        since_joined = (ctx.message.created_at - joined_at).days
        user_joined = joined_at.strftime(self.time_format)
        user_created = user.created_at.strftime(self.time_format)
        member_number = sorted(ctx.guild.members,
                               key=lambda m: m.joined_at).index(user) + 1
        created_on = f'{user_created}\n({since_created} days ago)'
        joined_on = f'{user_joined}\n({since_joined} days ago)'
        if user.game is None:
            game = f'Chilling in {user.status} status'
        elif user.game.url is None:
            game = f'Playing {user.game}'
        else:
            game = f'Streaming: [{user.game}]({user.game.url})'

        if roles:
            roles = [r.name for r in sorted(roles, key=lambda r: r.position, reverse=True)]
            roles = ", ".join(roles)
        else:
            roles = "None"

        em = discord.Embed(description=game, colour=user.colour)
        em.add_field(name='Joined Discord on', value=created_on)
        em.add_field(name='Joined this guild on', value=joined_on)
        em.add_field(name='Roles', value=roles, inline=False)
        em.set_footer(text=f'Member #{member_number} | User ID:{user.id}')
        name = " ~ ".join((str(user), user.nick)) if user.nick else str(user)
        em.set_author(name=name, url=user.avatar_url)
        em.set_thumbnail(url=user.avatar_url)

        try:
            await ctx.send(embed=em)
        except discord.HTTPException:
            await ctx.send('I need the `Embed links` permission to send this')


def setup(bot):
    bot.add_cog(EmbedComms(bot))
