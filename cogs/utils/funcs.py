import discord


async def fast_get_message(channel: discord.TextChannel, id: int):
    o = discord.Object(id=id + 1)
    m = None
    async for mess in channel.history(limit=1, before=o):
        if mess.id == id:
            m = mess
            break
    return m
