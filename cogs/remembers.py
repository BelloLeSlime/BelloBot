import discord
from discord.app_commands import guild_only
from discord.ext import commands
import bot_package.custom_func as Cf
from discord import app_commands
from bot_package.data import automatic_message

class Remembers(commands.Cog):
    """
    Permet de gérer les souvenirs du bot, qui sont des messages que le bot n'oubliera pas, comme des règles ou des trucs comme ça
    """
    def __init__(self, bot):
        self.bot = bot

    async def profile_autocomplete(self, interaction: discord.Interaction, current: str):
        return ([app_commands.Choice(name="BelloBot", value="BelloBot"),] +
                [app_commands.Choice(name=profile, value=profile) for profile in Cf.get_profiles(interaction.guild.id)])

    @guild_only
    @commands.hybrid_command(name="add_remember")
    @commands.has_permissions(administrator=True)
    @app_commands.autocomplete(profile=profile_autocomplete)
    async def add_remember(self, ctx: commands.Context, message: str, profile: str="BelloBot"):
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

        profiles = Cf.get_profiles(ctx.guild.id)
        if not profile in profiles and profile != "BelloBot":
            await ctx.send(f"Aucun profil n'est nommé **{profile}**", ephemeral=True)
            return

        message = message.replace("\\n", "\n")
        remembers = Cf.get_remembers(ctx.guild.id)
        if not profile in remembers:
            remembers[profile] = {}
        remembersp = remembers[profile]
        ints = [int(key) for key in remembersp.keys()]
        next_id = max(ints) + 1 if remembersp else 0
        remembersp[next_id] = message
        Cf.set_remembers(ctx.guild.id, remembers)
        await ctx.send(f"Votre souvenir \"*{message}*\" a bien été enregistré ! ID : {next_id}", ephemeral=True)

    @guild_only
    @commands.hybrid_command(name="remembers")
    @commands.has_permissions(administrator=True)
    @app_commands.autocomplete(profile=profile_autocomplete)
    async def remembers(self, ctx: commands.Context, profile: str="BelloBot"):
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

        profiles = Cf.get_profiles(ctx.guild.id)
        if not profile in profiles and profile != "BelloBot":
            await ctx.send(f"Aucun profil n'est nommé **{profile}**", ephemeral=True)
            return

        remembers = Cf.get_remembers(ctx.guild.id)
        if not profile in remembers:
            remembers[profile] = {}
        remembersp = remembers[profile]
        embed = discord.Embed(title="Souvenirs du bot", color=discord.Color.orange())
        descr = ""
        for key in remembersp.keys():
            message = remembersp[key]
            descr += key + " - **" + message + "**\n\n"
        descr = descr.strip()
        embed.description = descr
        await ctx.send(embed=embed, ephemeral=True)

    @guild_only
    @commands.hybrid_command(name="delete_remember")
    @commands.has_permissions(administrator=True)
    @app_commands.autocomplete(profile=profile_autocomplete)
    async def delete_remember(self, ctx: commands.Context, id: int, profile: str="BelloBot"):
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

        profiles = Cf.get_profiles(ctx.guild.id)
        if not profile in profiles and profile != "BelloBot":
            await ctx.send(f"Aucun profil n'est nommé **{profile}**", ephemeral=True)
            return

        remembers = Cf.get_remembers(ctx.guild.id)
        if not profile in remembers:
            remembers[profile] = {}
        remembersp = remembers[profile]
        if str(id) not in remembersp.keys():
            await ctx.send(f"Vous n'avez pas de souvenir avec l'ID {id}.", ephemeral=True)
            return
        del remembersp[str(id)]
        Cf.set_remembers(ctx.guild.id, remembers)
        await ctx.send(f"Le souvenir {id} supprimé !", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Remembers(bot))