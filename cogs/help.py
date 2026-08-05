import discord
from discord.ext import commands
from discord import app_commands
from bot_package.data import help_message


class Help(commands.Cog):
    """
    Commande help
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help")
    async def help(self, ctx: commands.Context, command: str = None):
        """
        Affiche l'aide
        :param ctx: Context
        :param command: Commande à rechercher
        :return:
        """
        bot_commands = self.bot.commands
        names = [cmd.name for cmd in bot_commands]
        if not command in names and command:
            embed = discord.Embed(color=discord.Color.red(), description="Cette commande n'existe pas")
            await ctx.send(embed=embed)
            return

        if command:
            cmd = None
            for cd in bot_commands:
                if cd.name == command:
                    cmd = cd.app_command
                    break

            arguments_str = ""
            for param in cmd.parameters:
                arguments_str += f"- {param.name} : {param.description} {"(non requis)" if not param.required else ""}\n"


            embed = discord.Embed(color=discord.Color.green(), title=f"Aide de la commande /{command}", description=
            f"""
            /{cmd.name} :
            {cmd.description}
            
            Arguments :
            {arguments_str}
""")
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(color=discord.Color.green(), title="Bonjour, je suis BelloBot", description=help_message)
        await ctx.send(embed=embed)


    @commands.hybrid_command(name="ping")
    async def ping(self, ctx: commands.Context):
        """
        Dit "Pong !"
        :param ctx: Context
        :return:
        """
        await ctx.send("Pong !")

    @commands.hybrid_command(name="bellobot_info")
    async def bellobot_info(self, ctx: commands.Context):
        """
        Montre les infos du bot
        :param ctx:
        :return:
        """
        embed = discord.Embed(color=discord.Color.green(), title="Infos du bot", description=
        f"""
        Nom : {self.bot.user.name}
        ID : {self.bot.user.id}
        Verison : {self.bot.version}
        Serveurs : {self.bot.guild_count}
""").set_image(url="https://slimepunk.fr/img/BelloBot.png")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))