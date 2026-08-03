import discord
from discord.ext import commands

class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ban")
    async def ban(self, ctx, member: discord.Member, reason=None):
        await member.ban(reason=reason)

    @commands.hybrid_command(name="kick")
    async def kick(self, ctx, member: discord.Member, reason=None):
        await member.kick(reason=reason)

async def setup(bot):
    await bot.add_cog(Mod(bot))