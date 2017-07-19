from discord.ext import commands


def is_owner():
    def pred(ctx):
        return ctx.message.author.id == ctx.bot.owner_id
    return commands.check(pred)
