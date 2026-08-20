import discord
from discord.ext import commands
import sys
import subprocess
import os

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
        await ctx.send("Arrêt du bot...")
        await self.bot.close()

    @commands.hybrid_command(name="restart")
    @commands.is_owner()
    async def restart(self, ctx):
        """
        OWNER SEULEMENT - Redémarre le bot
        :param ctx:
        :return:
        """
        await ctx.send("Redémarrage...")
        await self.bot.close()
        sys.exit(42)

    @commands.hybrid_command(name="update")
    @commands.is_owner()
    async def update(self, ctx):
        """
        OWNER SEULEMENT - Update le bot depuis le github
        :param ctx:
        :return:
        """

        message = await ctx.send("Mise à jour en cours...", ephemeral=True)


        result_stash = subprocess.run(
            ["git", "stash"],
            capture_output=True,
            text=True
        )

        if result_stash.returncode != 0:
            await message.edit(
                f"Mise à jour en cours...\nErreur git lors du stash :\n{result_stash.stderr}",
                ephemeral=True
            )
            return

        result_pip = subprocess.run(
            ["pip", "install", "-r", "requirements.txt"],
            capture_output=True,
            text=True
        )

        if result_pip.returncode != 0:
            await message.edit(
                f"Mise à jour en cours...\nErreur PIP lors de l'installation :\n{result_pip.stderr}",
                ephemeral=True
            )
            return

        result_pull = subprocess.run(
            ["git", "pull"],
            capture_output=True,
            text=True
        )

        if result_pull.returncode != 0:
            await message.edit(
                f"Mise à jour en cours...\nErreur git lors du pull :\n{result_pull.stderr}",
                ephemeral=True
            )
            return

        await message.edit("Mise à jour en cours...\nMise à jour terminée ! Redémarrage...", ephemeral=True)
        await self.bot.close()
        sys.exit(42)

    @commands.hybrid_command(name="get_logs")
    @commands.is_owner()
    async def get_logs(self, ctx):
        """
        OWNER SEULEMENT - Permet d'obtenir les logs du bot
        :param ctx:
        :return:
        """
        await ctx.send(file=discord.File("discord.log"), ephemeral=True)

    @commands.hybrid_command(name="get_last_error")
    @commands.is_owner()
    async def get_last_error(self, ctx):
        """
        OWNER SEULEMENT - Permet d'obtenir la dernière erreur du bot
        :param ctx:
        :return:
        """
        if "last.txt" in os.listdir("./files/error/"):
            await ctx.send(file=discord.File("files/error/last.txt"), ephemeral=True)
        else:
            await ctx.send("Il n'y a pas d'erreur !", ephemeral=True)

    @commands.hybrid_command(name="get_error")
    @commands.is_owner()
    async def get_error(self, ctx, error_code:str):
        """
        OWNER SEULEMENT - Permet d'avoir n'importe quelle erreur du bot
        :param ctx:
        :param error_code: Code d'erreur
        :return:
        """
        if error_code + ".txt" in os.listdir("./files/error/"):
            await ctx.send(file=discord.File(f"files/error/{error_code}.txt"), ephemeral=True)
        else:
            await ctx.send(f"Il n'y a pas d'erreur {error_code} !", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Owner(bot))

