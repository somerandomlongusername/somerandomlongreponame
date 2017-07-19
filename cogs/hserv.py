from discord.ext import commands
import asyncio


class HServ:
    def __init__(self, bot):
        self.bot = bot

        self.winners_worth = 2  # calculations, how much winners are worth
        self.losers_worth = 1  # calculations, how much losers are worth

    def calculator(self, total_players: int, total_winners: int, winnings_per: int):
        total_losers = total_players - total_winners
        total_winnings = int(total_winners) * int(winnings_per)

        avg_winning = total_winnings / ((self.winners_worth * total_winners) + (self.losers_worth * total_losers))
        winners_win = self.winners_worth * avg_winning
        losers_win = self.losers_worth * int(avg_winning)
        winners_pay = winnings_per - int(winners_win)
        return winners_pay, losers_win

    @commands.command()
    async def calculate(self, ctx, total_players: int, total_winners: int, winnings_per: int):
        """Calculates payouts"""
        winners_pay, losers_win = self.calculator(total_players, total_winners, winnings_per)
        await ctx.send(f'{ctx.author.mention}, here you go:```http\nEach winner should pay {winners_pay} to the splitter.\nThe splitter should pay {losers_win} to each loser.```')

    @commands.command()
    async def calc(self, ctx):
        """Interactively calculates payouts"""
        def check(msg):
            qual = True
            if msg.channel != ctx.channel:
                qual = False
            if msg.author != ctx.author:
                qual = False
            try:
                int(msg.content)
            except ValueError:
                qual = False
            return qual

        try:
            await ctx.send('```http\nTotal players in the heist:```')
            a = await self.bot.wait_for('message', check=check, timeout=10)
            await ctx.send('```http\nTotal winners in the heist:```')
            b = await self.bot.wait_for('message', check=check, timeout=10)
            await ctx.send('```http\nAmount of winnings per each winner:```')
            c = await self.bot.wait_for('message', check=check, timeout=10)
        except asyncio.TimeoutError:
            await ctx.send(f'Cancelling calculator for {ctx.author.mention}, you took too long.')
            return

        total_players = int(a.content)
        total_winners = int(b.content)
        winnings_per = int(c.content)

        winners_pay, losers_win = self.calculator(total_players, total_winners, winnings_per)
        await ctx.send(f'{ctx.author.mention}, here you go:```http\nEach winner should pay {winners_pay} to the splitter.\nThe splitter should pay {losers_win} to each loser.```')

    @commands.command()
    async def rcalc(self, ctx):
        """Calculates payouts using reactions as input"""
        async def get_input(text, msg=None):
            res = ''
            nums = ['1\u20e3', '2\u20e3', '3\u20e3', '4\u20e3', '5\u20e3', '6\u20e3', '7\u20e3', '8\u20e3', '9\u20e3', '0\u20e3', '\u25c0', '\u23ed']
            # 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, back, enter

            if msg is None:
                msg = await ctx.send(f'```http\n{text}: {res}```')
                for n in nums:
                    await msg.add_reaction(n)
            else:
                await msg.edit(content=f'```http\n{text}: {res}```')

            def check(reaction, user):
                return reaction.message.id == msg.id and reaction.emoji in nums and user == ctx.author

            while True:
                try:
                    r, __ = await self.bot.wait_for("reaction_add", check=check, timeout=10)
                except asyncio.TimeoutError:
                    await ctx.send(f'Cancelling calculator for {ctx.author.mention}, you took too long.')
                    await msg.delete()
                    raise(commands.CommandError)
                await msg.remove_reaction(r.emoji, ctx.author)
                if r.emoji == '\u23ed':
                    break
                if r.emoji == '\u25c0':
                    res = res[:-1]
                else:
                    res += r.emoji[0]
                await msg.edit(content=f'```http\n{text}: {res}```')
            return int(res), msg

        total_players, the_msg = await get_input('Total players in the heist')

        total_winners, __ = await get_input('Total winners in the heist', the_msg)

        winnings_per, __ = await get_input('Amount of winnings per each winner', the_msg)

        winners_pay, losers_win = self.calculator(total_players, total_winners, winnings_per)

        await the_msg.clear_reactions()
        t = '{}, here you go:```http\nInput: crew of {}, {} winners, {} per each winner.\nEach winner should pay {} to the splitter.\nThe splitter should pay {} to each loser.```'
        await the_msg.edit(content=t.format(ctx.message.author.mention, total_players, total_winners, winnings_per, winners_pay, losers_win))


def setup(bot):
    bot.add_cog(HServ(bot))
