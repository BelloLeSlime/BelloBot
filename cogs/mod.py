import discord
from discord.ext import commands

class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, reason=None):
        """
        Permet de banir un membre
        :param ctx:
        :param member: Membre à bannir
        :param reason: Raison du bannissement
        :return:
        """
        await member.ban(reason=reason)
        await ctx.send(f"Vous avez bien banni {member.mention}.", ephemeral=True)

    @commands.hybrid_command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, reason=None):
        """
        Permet d'expulser un membre
        :param ctx:
        :param member: Membre à expulser
        :param reason: Raison de l'expulsion
        :return:
        """
        await member.kick(reason=reason)
        await ctx.send(f"Vous avez bien expulsé {member.mention}.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Mod(bot))