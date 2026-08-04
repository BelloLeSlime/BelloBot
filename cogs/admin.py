import discord
from discord import app_commands
from discord.ext import commands
import bot_package.custom_func as Cf
from bot_package.data import config_keys, config_value_types, config_text_types, flamcoin_symbol
import os

async def config_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=key, value=key) for key in config_keys
    ]

class Admin(commands.Cog):
    """
    Toutes les commandes admin, donc réservés aux administrateurs de serveur.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="config_view")
    @commands.has_permissions(administrator=True)
    async def config_view(self, ctx: commands.Context):
        """
        ADMIN SEULEMENT - Permet de voir la configuration actuelle du serveur
        :param ctx: Context
        :return:
        """

        bot_config = Cf.get_config(ctx.guild.id)
        lbot_config = bot_config.copy()

        config_text = ""
        for lkey, lvalue in lbot_config.items():
            if not lkey in config_keys:
                del bot_config[lkey]
                continue
            lvalue_type = config_value_types[lkey]
            try:
                if (not lvalue_type == int) or (not lvalue_type == bool):
                    if lvalue_type == discord.TextChannel:
                        channel_id = lvalue
                        channel = await ctx.guild.fetch_channel(channel_id)
                        lvalue = channel.mention
                    elif lvalue_type == discord.Role:
                        role_id = lvalue
                        role = await ctx.guild.fetch_role(role_id)
                        lvalue = role.mention

            except Exception:
                lvalue = "Rien"
            config_text += f"\n {lkey} : {lvalue}"

        Cf.set_config(ctx.guild.id, bot_config)

        embed = discord.Embed(color=discord.Color.blue())
        embed.title = "Configuration du bot par serveur :"
        embed.description = f"Voici la configuration actuelle de ce serveur : \n{config_text}"

        await ctx.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(name="config")
    @commands.has_permissions(administrator=True)
    @app_commands.autocomplete(key=config_autocomplete)
    async def config(self, ctx: commands.Context, key: str, value: str):
        """
        ADMIN SEULEMENT - Configure le bot
        :param ctx: Context
        :param key: Clé (donc qu'est-ce qui doit être configuré)
        :param value: Valeur (donc ce qui est configuré pour la clé)
        :return:
        """
        await ctx.defer(ephemeral=True)

        if key not in config_value_types.keys():
            await ctx.send(f"Veuillez préciser une clé valide !", ephemeral=True)
            return


        value_type = config_value_types[key]

        if value.startswith("<#"):
            channel_id = int(value.removeprefix("<#").removesuffix(">"))
            channel = await ctx.guild.fetch_channel(channel_id)
            value = channel
        elif value.isdigit():
            value = int(value)
        else:
            text_type = config_text_types[config_value_types[key]]
            await ctx.send(f"Veuillez préciser une valeur valide ! Ça doit être : {text_type}", ephemeral=True)
            return

        bot_config = Cf.get_config(ctx.guild.id)
        bot_config[key] = value if not type(value) in [discord.TextChannel, discord.Role] else value.id


        lbot_config = bot_config.copy()
        config_text = ""
        for lkey, lvalue in lbot_config.items():
            if not lkey in config_keys:
                del bot_config[lkey]
                continue
            lvalue_type = config_value_types[lkey]
            try:
                if (not lvalue_type == int) or (not lvalue_type == bool):
                    if lvalue_type == discord.TextChannel:
                        channel_id = lvalue
                        channel = await ctx.guild.fetch_channel(channel_id)
                        lvalue = channel.mention
                    elif lvalue_type == discord.Role:
                        role_id = lvalue
                        role = await ctx.guild.fetch_role(role_id)
                        lvalue = role.mention

            except Exception:
                lvalue = "Rien"
            config_text += f"\n {lkey} : {lvalue}"

        Cf.set_config(ctx.guild.id, bot_config)

        embed = discord.Embed(color=discord.Color.blue())
        embed.title = "Configuration du bot par serveur :"
        embed.description = f"La clé {key} a bien pour valeur {value if value_type in [int, bool] else value.mention} ! Voici la configuration du bot à présent : \n{config_text}"

        await ctx.send(embed=embed, ephemeral=True)
        if key == "max_messages_in_memory" and not Cf.read_json(f"files/config/{ctx.guild.id}.json")[
            "disable_warning_messages"]:
            if value > 50:
                embed = discord.Embed(color=discord.Color.red())
                embed.title = "ATTENTION"
                embed.description = "Le nombre de messages maximum est recommendé de rester sous la barre des 50 messages : le bot pourrait être surchargé."
                await ctx.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(name="reset_memory")
    @commands.has_permissions(administrator=True)
    async def reset_memory(self, ctx: commands.Context):
        """
        ADMIN SEULEMENT - Supprime la mémoire du bot
        :param ctx:
        :return:
        """
        with open(f"files/messages/{ctx.guild.id}.txt", "w", encoding="utf-8") as f:
            f.write("")
        await ctx.send(f"Ma mémoire a bien été réinitialisée !", ephemeral=True)

    @commands.hybrid_command(name="reset")
    @commands.has_permissions(administrator=True)
    async def reset(self, ctx: commands.Context):
        """
        ADMIN SEULEMENT - Remet le serveur à 0 niveau XP, argent, inventaire et effets
        :param ctx:
        :return:
        """
        for file in os.listdir("./files/user_info/{interaction.guild.id}/"):
            user_data_xp = Cf.read_json(f"files/user_info/{ctx.guild.id}/{file}")
            user_data_xp["xp"] = 0
            user_data_xp["money"] = 0
            user_data_xp["level"] = 1
            user_data_xp["mult_xp"] = 1
            user_data_xp["mult_money"] = 1
            user_data_xp["temp_effects"] = {}
            user_data_xp["items"] = {}
            Cf.write_json(user_data_xp, f"files/user_info/{ctx.guild.id}/{file}")
        await ctx.send(f"Vous avez bien remit le serveur à 0.", ephemeral=True)

    async def stats_mod_what_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name="xp", value="xp"),
            app_commands.Choice(name="level", value="level"),
            app_commands.Choice(name="money", value="money"),
        ]

    async def stats_mod_how_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name="add", value="add"),
            app_commands.Choice(name="remove", value="remove"),
            app_commands.Choice(name="set", value="set"),
            app_commands.Choice(name="reset", value="reset"),
        ]

    @commands.hybrid_command(name="stats_mod")
    @commands.has_permissions(administrator=True)
    @app_commands.autocomplete(what=stats_mod_what_autocomplete, how=stats_mod_how_autocomplete)
    async def stats_mod(self, ctx: commands.Context, user: discord.User, what: str, how: str, amount: int):
        """
        ADMIN SEULEMENT - Permet de gérer l'XP et l'argent d'un utilisateur
        :param ctx: Context
        :param user: Utilisateur
        :param what: Que gérer ? XP, niveau ou argent ?
        :param how: Comment ? Ajouter ? Retirer ? Mettre ?
        :param amount: Combien ?
        :return:
        """
        user_data = Cf.get_user_data(user.id, ctx.guild.id)
        embed = discord.Embed(title=f"Modification faite", color=discord.Color.green())
        if what == "xp":
            if how == "add":
                user_data["xp"] += amount
                embed.description = f"Vous avez bien ajouté {amount} XP à {user.display_name}"
            elif how == "remove":
                user_data["xp"] -= amount
                embed.description = f"Vous avez bien retiré {amount} XP à {user.display_name}"
            elif how == "set":
                user_data["xp"] = amount
                embed.description = f"Vous avez bien mit l'XP de {user.display_name} à {amount} XP"
            elif how == "reset":
                user_data["xp"] = 0
                embed.description = f"Vous avez bien réinitialisé l'XP de {user.display_name}"
        elif what == "level":
            if how == "add":
                user_data["level"] += amount
                embed.description = f"Vous avez bien ajouté {amount} niveaux à {user.display_name}"
            elif how == "remove":
                user_data["level"] -= amount
                embed.description = f"Vous avez bien retiré {amount} niveaux à {user.display_name}"
            elif how == "set":
                user_data["level"] = amount
                embed.description = f"Vous avez bien mit {user.display_name} au niveau {amount}"
            elif how == "reset":
                user_data["level"] = 1
                embed.description = f"Vous avez bien réinitialisé le niveau de {user.display_name}"
        elif what == "money":
            if how == "add":
                user_data["money"] += amount
                embed.description = f"Vous avez bien ajouté {amount}{flamcoin_symbol} à {user.display_name}"
            elif how == "remove":
                user_data["money"] -= amount
                embed.description = f"Vous avez bien retiré {amount}{flamcoin_symbol} à {user.display_name}"
            elif how == "set":
                user_data["money"] = amount
                embed.description = f"Vous avez bien mit l'argent de {user.display_name} à {amount}{flamcoin_symbol}"
            elif how == "reset":
                user_data["money"] = 1
                embed.description = f"Vous avez bien réinitialisé l'argent de {user.display_name}"

        Cf.set_user_data(user.id, ctx.guild.id, user_data)
        await ctx.send(embed=embed, ephemeral=True)

    async def embed_color_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name="green", value="green"),
            app_commands.Choice(name="blue", value="blue"),
            app_commands.Choice(name="red", value="red"),
            app_commands.Choice(name="gold", value="gold"),
            app_commands.Choice(name="orange", value="orange"),
            app_commands.Choice(name="fuchsia", value="fuchsia"),
        ]

    @commands.hybrid_command(name="embed")
    @commands.has_permissions(administrator=True)
    @app_commands.autocomplete(color=embed_color_autocomplete)
    async def embed(self, ctx: commands.Context, title: str, description: str, color: str):
        """
        ADMIN SEULEMENT - Envoie un message embed
        :param ctx: Context
        :param title: Titre
        :param description: Contenu
        :param color: Couleur
        :return:
        """
        color_dict = {
            "green": discord.Color.green(),
            "blue": discord.Color.blue(),
            "red": discord.Color.red(),
            "gold": discord.Color.gold(),
            "orange": discord.Color.orange(),
            "fuchsia": discord.Color.fuchsia()
        }
        color = color_dict[color]
        description = description.replace("\\n", "\n")
        embed = discord.Embed(title=title, description=description, color=color)
        await ctx.channel.send(embed=embed)
        await ctx.send("Votre Embed a bien été envoyé", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))