import discord
from discord.ext import commands
import sys
import subprocess

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

        await ctx.send("Mise à jour en cours...")

        result_pip = subprocess.run(
            ["pip", "install", "-r", "requirements.txt"],
            capture_output=True,
            text=True
        )

        if result_pip.returncode != 0:
            await ctx.send(
                f"Erreur PIP lors de l'installation :\n{result_pip.stderr}",
                ephemeral=True
            )
            return

        result_stash = subprocess.run(
            ["git", "stash"],
            capture_output=True,
            text=True
        )

        if result_stash.returncode != 0:
            await ctx.send(
                f"Erreur git lors du stash :\n{result_stash.stderr}",
                ephemeral=True
            )
            return

        result_pull = subprocess.run(
            ["git", "pull"],
            capture_output=True,
            text=True
        )

        if result_pull.returncode != 0:
            await ctx.send(
                f"Erreur git lors du pull :\n{result_pull.stderr}",
                ephemeral=True
            )
            return

        await ctx.send("Mise à jour terminée ! Redémarrage...")
        await self.bot.close()
        sys.exit(42)


async def setup(bot):
    await bot.add_cog(Owner(bot))

