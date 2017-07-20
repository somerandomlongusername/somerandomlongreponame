from discord.ext import commands


def is_owner():
    def pred(ctx):
        if not ctx.author.bot and not ctx.bot.user.bot:
            return True
        return ctx.author.id == ctx.bot.owner_id
    return commands.check(pred)
