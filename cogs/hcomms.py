import discord
from discord.ext import commands
import asyncio
import re as reg


class HComms:
    def __init__(self, bot):
        self.bot = bot

        self.winners_worth = 2  # calculations, how much winners are worth
        self.losers_worth = 1  # calculations, how much losers are worth
        self.pay_sleep = 1  # the amount of seconds between bank transfers (can be a float)
        self.debug = False

        self.channel_listen = None
        self.winners = None
        self.crew = None
        self.losers = None
        self.crew_list = {}
        self.payment_msg = '!bank transfer "{0}" {1}'
        self.heistremember = r"^(?:([\S\w ]+?) dropped out of the game.)"
        self.heistrecrew = r"(\d\d?\d?) members."
        self.heistreplayers = r"""
            \n([\S\w ]+?) # looks for a newline and the name
            (?=[ ]{5,}) # but only if followed by 5+ spaces"""
        self.heistrecreds = r"\b([0-9]+)\b"
        self.rehmember = reg.compile(self.heistremember, reg.M | reg.U)
        self.rehplayers = reg.compile(self.heistreplayers, reg.X | reg.M)
        self.rehcreds = reg.compile(self.heistrecreds, reg.M)
        self.rehcrew = reg.compile(self.heistrecrew, reg.M)

    def calculator(self, total_players: int, total_winners: int, winnings_per: int):
        total_losers = total_players - total_winners
        total_winnings = int(total_winners) * int(winnings_per)

        avg_winning = total_winnings / ((self.winners_worth * total_winners) + (self.losers_worth * total_losers))
        winners_win = self.winners_worth * avg_winning
        losers_win = self.losers_worth * int(avg_winning)
        winners_pay = winnings_per - int(winners_win)
        print('{} {}'.format(winners_pay, losers_win))
        return winners_pay, losers_win

    async def on_message(self, message):
        if not message.guild:
            return
        if message.channel != self.channel_listen:
            return
        if not message.author.bot:
            return
        if 'The credits collected from the vault was split among the winners:' in message.content:
            msg = message.content.replace('```', '')
            msg = '\n'.join(msg.split('\n')[2:])
            self.winners = self.rehplayers.findall(msg)
            self.losers = self.crew - len(self.winners)
            self.winnings = int(self.rehcreds.search(msg).group(1))
            if self.debug:
                await message.channel.send('heist over')
        if 'has joined the crew' in message.content:
            self.crew = int(self.rehcrew.search(message.content).group(1))
            # if self.debug:
            #     await message.channel.send('{} peeps in the crew now'.format(self.crew))

    @commands.command(name='liststart')
    async def _list_start(self, ctx):
        """Starts recording the list & heist. Do before first heist play"""
        self.list_message = ctx.message
        self.channel_listen = ctx.message.channel
        await ctx.message.edit(content=f'Now listening for heists in channel {ctx.channel}')

    @commands.command(name='liststop')
    async def _list_stop(self, ctx):
        """Clears the list and stops listening"""
        self.channel_listen = None
        await ctx.message.edit(content=f'No longer listening for heists in channel {ctx.channel}.')

    @commands.command(name='list')
    async def _list(self, ctx, print_list=True):
        """Sends the list"""
        self.crew_list = {}
        logs = ctx.channel.history(after=self.list_message, limit=500)
        await ctx.message.delete()

        counter = 0
        if self.debug:
            print('List of peeps who spoke:')
            print('------------------------')
        async for message in logs:
            counter += 1
            if message.author not in self.crew_list:
                self.crew_list[message.author] = False
                if self.debug:
                    print(message.author.name)

        if self.debug:
            print('List of "dropped out" names')
            print('------------------------')
        logs = ctx.channel.history(after=self.list_message, limit=500)
        async for message in logs:
            if 'dropped' in message.content:
                if self.debug:
                    print('\n=======')
                if message.author.bot:
                    msg = message.content.split('```')[1]
                    name = self.rehmember.search(msg).group(1)
                    if self.debug:
                        print(msg)
                        print(name)
                    if name:
                        if name in self.crew_list:
                            self.crew_list[name] = True
                            if self.debug:
                                print(f'{name}')
                if self.debug:
                    print('=======\n')
            # if 'has joined the crew.' in message.content:
            #     if message.author.bot:
            #         name = self.rehmember.search(message.content).groups()
            #         if name:
            #             for member in self.crew_list:
            #                 if member.name == name[0] or member.name == name[1]:
            #                     self.crew_list[member] = True
            #                     break
        if self.debug:
            print(self.crew_list)
            print(counter)
        if print_list:
            msg = '```http\nList: '
            for i in self.crew_list:
                if self.crew_list[i]:
                    msg += '"{0}" '.format(i)
            msg += '```'
            await ctx.send(msg)

    # @commands.command(name='winners')
    # async def _winners(self, ctx):
    #     """Sends the list of winners"""
    #     await self.bot.delete_message(ctx.message)
    #     winners_paid = {}
    #     async for message in self.bot.logs_from(ctx.message.channel, after=self.list_message):
    #         if message.author.name in self.winners:
    #             winners_paid[message.author] = False
    #     async for message in self.bot.logs_from(ctx.message.channel, after=self.list_message):
    #         if (('!pay' in message.content) or ('!bank transfer' in message.content)) and ('Spy727#3109' in message.content):
    #             for member in self.winners_paid:
    #                 if member == message.author:
    #                     winners_paid[member] = True
    #                     break
    #     msg = '```Winners: '
    #     msg2 = '```Winners left to pay: '
    #     for i in self.winners:
    #         msg += '"{0}" '.format(i)
    #         if not winners_paid[i]:
    #             msg2 += '"{0}" '.format(i)
    #     msg += '```'
    #     msg2 += '```'
    #     await self.bot.say(msg)
    #     await self.bot.say(msg2)

    @commands.command()
    async def payout(self, ctx):
        """Pays an amount to all members in the recorded list"""
        await ctx.message.delete()
        await ctx.invoke(self._list, False)
        _, num = self.calculator(self.crew, len(self.winners), self.winnings)
        for member in self.crew_list:
            if self.crew_list[member]:
                msg = self.payment_msg.format(member, num)
                await self.bot.say(msg)
                await asyncio.sleep(self.pay_sleep)

    @commands.command()
    async def calculate(self, ctx, total_players: int, total_winners: int, winnings_per: int):
        """Calculates payouts"""
        winners_pay, losers_win = self.calculator(total_players, total_winners, winnings_per)
        await self.bot.say((f'```Each winner should pay {winners_pay} to the splitter.\n'
                            f'The splitter should pay {losers_win} to each loser.```'))

    @commands.command()
    async def manualpay(self, ctx, amount: int, *members: discord.Member):
        """Pays an amount to all members in the given list (amount, member_list)"""
        await ctx.message.delete()
        for member in members:
            msg = self.payment_msg.format(member, amount)
            await ctx.send(msg)
            await asyncio.sleep(self.pay_sleep)

    # @commands.command()
    # async def hvar(self, ctx):
    #     """Shows the winners list, and the values for payouts"""
    #     await self.bot.delete_message(ctx.message)
    #     if self.debug:
    #         await self.bot.say('```Crew of {}, {} winners, each got {}```'.format(self.crew, len(self.winners), self.winnings))
    #     msg = '```Winners were: "{}"'.format(self.winners[0])
    #     for winner in self.winners[1:]:
    #         msg += ', "{}"'.format(winner)
    #     msg = msg + '```'
    #     await self.bot.say(msg)

    #     a, b = self.calculator(self.crew, len(self.winners), self.winnings)
    #     await self.bot.say('```Each winner pay me {}, and I shall pay each loser {}```'.format(a, b))

    # @commands.command()
    # async def muteall(self, ctx):
    #     """Denies the @everyone role from sending messages"""
    #     everyone_perms = ctx.message.channel.overwrites_for(ctx.message.server.default_role)
    #     everyone_perms.send_messages = False
    #     await self.bot.edit_channel_permissions(ctx.message.channel, ctx.message.server.default_role, everyone_perms)
    #     await self.bot.add_reaction(ctx.message, '\u2705')

    # @commands.command()
    # async def unmuteall(self, ctx):
    #     """Allows the @everyone role to send messages"""
    #     everyone_perms = ctx.message.channel.overwrites_for(ctx.message.server.default_role)
    #     everyone_perms.send_messages = True
    #     await self.bot.edit_channel_permissions(ctx.message.channel, ctx.message.server.default_role, everyone_perms)
    #     await self.bot.add_reaction(ctx.message, '\u2705')


def setup(bot):
    bot.add_cog(HComms(bot))
