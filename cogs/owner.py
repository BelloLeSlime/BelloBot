import discord
from discord.ext import commands

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="shutdown")
    @commands.is_owner()
    async def shutdown(self, ctx):
        """
        OWNER SEULEMENT - Arrête le bot (attention à pouvoir l'allumer après)
        :param ctx:
        :return:
        """
        await ctx.send("Shutting down...")
        await self.bot.close()

async def setup(bot):
    await bot.add_cog(Owner(bot))

