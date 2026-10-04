import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import guild_only
from discord import ForumChannel, Thread
import bot_package.custom_func as Cf
from bot_package.data import flamcoin_symbol

class Quests(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @guild_only
    @commands.hybrid_command(name="create_quest")
    @commands.has_permissions(administrator=True)
    async def create_quest(self, ctx: commands.Context, name: str, description: str, xp: int = 0, money: int = 0, type: str = None):
        """
        ADMIN SEULEMENT - Crée une nouvelle quête
        :param ctx:
        :param name: Nom de la quête
        :param description: Description de la quête (ce qu'il faut faire précisement)
        :param xp: XP gagné à la finition de la quête
        :param money: Argent gagné à la finition de la quête
        :param type: Type de la quête (Unique, Commune, ce que vous voulez)
        :return:
        """
        config = Cf.get_config(ctx.guild.id)
        if config["quests_channel"] is None:
            await ctx.send("Aucun salon n'a été attribué en tant que salon forum des quêtes. Attribuez-en un avec /config !", ephemeral=True)

        quests = Cf.get_quests(ctx.guild.id)
        quests_channel: ForumChannel = await ctx.guild.fetch_channel(config["quests_channel"])
        thread: ThreadWithMessage = await quests_channel.create_thread(name=name, content=f"""
        # {name}
        Quête postée par {ctx.author.mention}
        **{description}**
        {f"Type: **{type}**\n" if type else ""}{"Récompense :\n" if xp or money else "Aucune récompense à la clé."}{f"- **{xp}XP**\n" if xp else ""}{f"- **{money}{flamcoin_symbol}**\n" if money else ""}
        *Bonne chance !*
        
        
        > Vous valider une quête, veuillez mettre un fichier ou un lien ci-dessous. Vous ne pouvez pas valider une quête 2 fois. Un modérateur peut révoquer votre validation s'il décrète qu'elle est invalide, retirant ainsi votre récompense.
""")
        thread_id = thread.thread.id
        quests[str(thread_id)] = {
            "name": name,
            "description": description,
            "xp": xp,
            "money": money,
            "type": type,
            "validations": [],
        }
        Cf.set_quests(ctx.guild.id, quests)

        await ctx.send("Votre quête a bien été postée !", ephemeral=True)

    async def revoke_validation_quest_autocomplete(self, interaction: discord.Interaction, current: str):
        quests = Cf.get_quests(interaction.guild.id)
        return [app_commands.Choice(name=quest["name"], value=id) for id, quest in quests.items()]

    @guild_only
    @commands.hybrid_command(name="revoke_validation")
    @commands.has_permissions(administrator=True)
    @app_commands.autocomplete(quest=revoke_validation_quest_autocomplete)
    async def revoke_validation(self, ctx: commands.Context, quest: str, user: discord.User):
        """
        ADMIN SEULEMENT - Révoque une validation d'une quête pour un utilisateur
        :param ctx:
        :param quest: Quête dans laquelle révoquer la validation
        :param user: Utilisateur ayant mal validé la quête
        :return:
        """
        quests = Cf.get_quests(ctx.guild.id)
        if quest not in quests:
            await ctx.send("Cette quête n'existe pas, désolé !", ephemeral=True)
            return

        if not user.id in quests[quest]["validations"]:
            await ctx.send("Cet utilisateur n'a pas encore validé sa quête.", ephemeral=True)
            return

        quest_thread: Thread = await ctx.guild.fetch_channel(int(quest))
        await quest_thread.send(f"{user.mention}, votre validation a été désignée comme invalide, veuillez réessayer avec une validation qui respècte les règles de la quête.")
        quests[quest]["validations"].remove(user.id)
        Cf.set_quests(ctx.guild.id, quests)
        user_data = Cf.get_user_data(user.id, ctx.guild.id)
        user_data["xp"] -= quests[quest]["xp"]
        user_data["money"] -= quests[quest]["money"]
        Cf.set_user_data(user.id, ctx.guild.id, user_data)

        await ctx.send(f"La validation de {user.display_name} a bien été révoquée.", ephemeral=True)

    @guild_only
    @commands.hybrid_command(name="close_quest")
    @commands.has_permissions(administrator=True)
    @app_commands.autocomplete(quest=revoke_validation_quest_autocomplete)
    async def close_quest(self, ctx: commands.Context, quest: str):
        """
        ADMIN SEULEMENT - Ferme une quête
        :param ctx:
        :param quest: Quête à fermer
        :return:
        """
        quests = Cf.get_quests(ctx.guild.id)
        if quest not in quests:
            await ctx.send("Cette quête n'existe pas.", ephemeral=True)
            return

        channel: Thread = await ctx.guild.fetch_channel(int(quest))
        await channel.send("# ⚠️ La quête n'est plus disponible")
        await channel.edit(locked=True)

        del quests[quest]
        Cf.set_quests(ctx.guild.id, quests)

        await ctx.send("La quête a bien été fermée.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Quests(bot))