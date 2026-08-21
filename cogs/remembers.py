import discord
from discord.ext import commands
import bot_package.custom_func as Cf

class Remembers(commands.Cog):
    """
    Permet de gérer les souvenirs du bot, qui sont des messages que le bot n'oubliera pas, comme des règles ou des trucs comme ça
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="add_remember")
    @commands.has_permissions(administrator=True)
    async def add_remember(self, ctx: commands.Context, message: str):
        """
        ADMIN SEULEMENT - Ajoute un souvenir que le bot n'oubliera pas
        :param ctx: Context
        :param message: Contenu du souvenir
        :return:
        """
        config = Cf.get_config(ctx.guild.id)
        if not config["enable_ai"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais l'IA n'est pas activé sur ce serveur !"),
                           ephemeral=True)
            return

        message = message.replace("\\n", "\n")
        remembers = Cf.get_remembers(ctx.guild.id)
        ints = [int(key) for key in remembers.keys()]
        next_id = max(ints) + 1 if remembers else 0
        remembers[next_id] = message
        Cf.set_remembers(ctx.guild.id, remembers)
        await ctx.send(f"Votre souvenir \"*{message}*\" a bien été enregistré !", ephemeral=True)

    @commands.hybrid_command(name="remembers")
    @commands.has_permissions(administrator=True)
    async def remembers(self, ctx: commands.Context):
        """
        ADMIN SEULEMENT - Affiche le panel des souvenirs
        :param ctx: Context
        :return:
        """
        config = Cf.get_config(ctx.guild.id)
        if not config["enable_ai"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais l'IA n'est pas activé sur ce serveur !"),
                           ephemeral=True)
            return

        remembers = Cf.get_remembers(ctx.guild.id)
        embed = discord.Embed(title="Souvenirs du bot", color=discord.Color.orange())
        descr = ""
        for key in remembers.keys():
            message = remembers[key]
            descr += key + " - **" + message + "**\n\n"
        descr = descr.strip()
        embed.description = descr
        await ctx.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(name="delete_remember")
    @commands.has_permissions(administrator=True)
    async def delete_remember(self, ctx: commands.Context, id: int):
        """
        ADMIN SEULEMENT - Supprime un souvenir
        :param ctx: Context
        :param id: ID du souvenir
        :return:
        """
        config = Cf.get_config(ctx.guild.id)
        if not config["enable_ai"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais l'IA n'est pas activé sur ce serveur !"),
                           ephemeral=True)
            return

        remembers = Cf.get_remembers(ctx.guild.id)
        if str(id) not in remembers.keys():
            await ctx.send(f"Vous n'avez pas de souvenir avec l'ID {id}.", ephemeral=True)
            return
        del remembers[str(id)]
        Cf.set_remembers(ctx.guild.id, remembers)
        await ctx.send(f"Le souvenir {id} supprimé !", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Remembers(bot))