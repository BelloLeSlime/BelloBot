import discord
from bot_package import custom_func as Cf
from discord.ext import commands
from simpleeval import simple_eval

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="math")
    async def math(self, ctx: commands.Context, expression: str):
        """
        Calcule une expression
        :param ctx:
        :param expression: Expression mathématique
        :return:
        """
        try:
            result = simple_eval(expression)
            await ctx.send(f"`{expression}` = `{result}`", ephemeral=True)
        except:
            await ctx.send("Expression invalide", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Misc(bot))