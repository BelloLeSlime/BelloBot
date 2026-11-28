import discord
from discord.app_commands import guild_only
from discord import app_commands
from discord.ext import commands
import bot_package.custom_func as Cf
from bot_package.data import automatic_message
import asyncio
from datetime import datetime
from google.genai import errors


async def profile_autocomplete(interaction: discord.Interaction, current: str):
    return [app_commands.Choice(name=profile, value=profile) for profile in Cf.get_profiles(interaction.guild.id)]


async def profile_plus_bellobot_autocomplete(interaction: discord.Interaction, current: str):
    return [app_commands.Choice(name="BelloBot", value="BelloBot")]+[app_commands.Choice(name=profile, value=profile) for profile in Cf.get_profiles(interaction.guild.id)]


class Ai(commands.Cog):
    """
    Toutes les commandes impliquant l'IA
    """
    def __init__(self, bot):
        self.bot = bot

    @guild_only
    @commands.hybrid_command(name="ask")
    @app_commands.autocomplete(profile=profile_plus_bellobot_autocomplete)
    async def ask(self, ctx: commands.Context, prompt: str, profile: str="BelloBot"):
        """
        Alternative à juste ping
        :param ctx: Context
        :param prompt: Demande faite à l'IA
        :param profile: Profil
        :return:
        """

        config = Cf.get_config(ctx.guild.id)
        if not config["enable_ai"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais l'IA n'est pas activé sur ce serveur !"),
                           ephemeral=True)
            return

        usernames = Cf.read_json("files/usernames.json")
        usernames[str(ctx.author.id)] = ctx.author.display_name
        Cf.write_json(usernames, "files/usernames.json")

        profiles = Cf.get_profiles(ctx.guild.id)

        content = prompt
        try:
            async with ctx.channel.typing():
                answer = await Cf.ask_ai(
                    str({
                        "author": f"{ctx.author.display_name} (id: {ctx.author.id})",
                        "content": content,
                        "channel": ctx.channel.name,
                        "time": datetime.now().strftime(
                            "%d/%m/%Y/ %H:%M:%S"
                        )
                    }),
                    ctx.author.display_name,
                    ctx.guild.id,
                    emojis=await ctx.guild.fetch_emojis(),
                    guild_name=ctx.guild.name,
                    guild_description=ctx.guild.description,
                    bot=self.bot,
                    usernames=usernames,
                    profile=profile
                )
                to_send = await Cf.parse_text(
                    self.bot,
                    answer,
                    ctx,
                    False,
                    profile
                )
                if profile == "BelloBot":
                    await ctx.send(to_send)
                else:
                    profile_data = profiles[profile]
                    await Cf.send_as_profile(
                        name=profile,
                        pp_url=profile_data["pp_url"],
                        guild_id=ctx.guild.id,
                        content=to_send,
                        bot=self.bot,
                    )
        except errors.ServerError:
            await ctx.send(
                f"{automatic_message}Désolé, mais le serveur de Google peine "
                "en ce moment, ou il n'y a plus de crédits. "
                "Veuillez réessayer plus tard !", ephemeral=True
            )

        Cf.add_message(
            ctx.guild.id,
            ctx.author.id,
            content,
            ctx.channel.name,
            datetime.now().isoformat()
        )

    @guild_only
    @commands.hybrid_command(name="vote_reset_memory")
    async def vote_reset_memory(self, ctx: commands.Context):
        """
        Créé un vote pour réinitialiser la mémoire du bot si ce dernier pert la tête
        :param ctx: Context
        :return:
        """

        config = Cf.get_config(ctx.guild.id)
        if not config["enable_ai"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais l'IA n'est pas activé sur ce serveur !"), ephemeral=True)
            return

        await ctx.send("Vote organisé !", ephemeral=True)
        embed = discord.Embed(color= discord.Color.orange(), title="Voulez-vous réinitialiser ma mémoire car je deviens fou ?", description="Réagir 👍 pour oui.").set_footer(text="Fin du vote dans 1min !")
        msg = await ctx.channel.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

        await asyncio.sleep(60)
        msg = await ctx.channel.fetch_message(msg.id)

        yes_users = set()
        no_users = set()
        for reaction in msg.reactions:
            print(f"Reaction: {reaction.emoji}, count: {reaction.count}")
            if str(reaction.emoji) == "👍":
                async for user in reaction.users():
                    if not user.bot:
                        yes_users.add(user.id)
            elif str(reaction.emoji) == "👎":
                async for user in reaction.users():
                    if not user.bot:
                        no_users.add(user.id)

        yes_count = len(yes_users)
        no_count = len(no_users)

        print(f"👍: {yes_count}, 👎: {no_count}")

        if yes_count > no_count:
            await ctx.channel.send(f"{automatic_message}Ma mémoire va être réinitialisée...")
            with open(f"files/messages/{ctx.guild.id}.json", "w", encoding="utf-8") as f:
                f.write('{"messages":[]}')
        else:
            await ctx.channel.send(f"{automatic_message}Ma mémoire ne sera pas réinitialisée !")

    @commands.hybrid_command(name="reset_dm_memory")
    async def reset_dm_memory(self, ctx: commands.Context):
        """
        Réinitialise la mémoire du bot dans les messages privés
        :param ctx:
        :return:
        """

        if ctx.guild:
            await ctx.send("Cette commande n'est utilisable que dans des messages privées.", ephemeral=True)
            return

        user_id = ctx.author.id
        with open(f"files/dms/{user_id}.json", "w", encoding="utf-8") as f:
            f.write('{"messages": []}')

        embed = discord.Embed(color=discord.Color.orange(), description="Ma mémoire dans les MP est réinitialisée.")
        await ctx.send(embed=embed, ephemeral=True)

    @guild_only
    @commands.hybrid_command(name="ai_ignore_add")
    @commands.has_permissions(administrator=True)
    async def ai_ignore_add(self, ctx: commands.Context, channel: discord.TextChannel):
        """
        ADMIN SEULEMENT - ajoute un salon dans lequel l'IA ne peut pas interagir (voir ou parler)
        :param ctx:
        :param channel: Salon dans lequel l'IA est interdite
        :return:
        """
        config = Cf.get_config(ctx.guild.id)
        if not config["enable_ai"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais l'IA n'est pas activé sur ce serveur !"),
                           ephemeral=True)
            return

        ai_ignore = Cf.get_ai_ignore(ctx.guild.id)
        if not channel.id in ai_ignore["channels"]:
            ai_ignore["channels"].append(channel.id)
            embed = discord.Embed(color=discord.Color.green(), description=f"Désormais, l'IA est désactivée dans {channel.mention}.")
            await ctx.send(embed=embed, ephemeral=True)
            Cf.set_ai_ignore(ctx.guild.id, ai_ignore)
        else:
            embed = discord.Embed(color=discord.Color.red(), description=f"L'IA est déjà désactivée dans {channel.mention}.")
            await ctx.send(embed=embed, ephemeral=True)

    @guild_only
    @commands.hybrid_command(name="ai_ignore")
    @commands.has_permissions(administrator=True)
    async def ai_ignore(self, ctx: commands.Context):
        """
        ADMIN SEULEMENT - Permet d'avoir la liste des salons ignorés par l'IA
        :param ctx:
        :return:
        """
        config = Cf.get_config(ctx.guild.id)
        if not config["enable_ai"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais l'IA n'est pas activé sur ce serveur !"),
                           ephemeral=True)
            return

        ai_ignore = Cf.get_ai_ignore(ctx.guild.id)
        embed = discord.Embed(color=discord.Color.blue(), title="Salons AI Ignore du serveur", description=f"")
        for channel_id in ai_ignore["channels"]:
            embed.description += f"- <#{channel_id}>\n"
        embed.description += f"Dans ces salons, l'IA ne pourra ni parler, ni voir quelconque message."
        await ctx.send(embed=embed, ephemeral=True)

    @guild_only
    @commands.hybrid_command(name="ai_ignore_remove")
    @commands.has_permissions(administrator=True)
    async def ai_ignore_remove(self, ctx: commands.Context, channel: discord.TextChannel):
        """
        ADMIN SEULEMENT - Enlève l'interdiction à l'IA
        :param ctx:
        :param channel:
        :return:
        """
        config = Cf.get_config(ctx.guild.id)
        if not config["enable_ai"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(), description=f"Désolé, mais l'IA n'est pas activé sur ce serveur !"), ephemeral=True)
            return

        ai_ignore = Cf.get_ai_ignore(ctx.guild.id)
        if not channel.id in ai_ignore["channels"]:
            embed = discord.Embed(color=discord.Color.red(), description=f"Le salon {channel.mention} n'est pas en AI Ignore.")
            await ctx.send(embed=embed, ephemeral=True)
            return
        ai_ignore["channels"].remove(channel.id)
        Cf.set_ai_ignore(ctx.guild.id, ai_ignore)
        embed = discord.Embed(color=discord.Color.green(), description=f"Le salon {channel.mention} n'est plus en AI Ignore.")
        await ctx.send(embed=embed, ephemeral=True)

    @guild_only
    @commands.hybrid_command(name="profile_add")
    @commands.has_permissions(administrator=True)
    async def profile_add(self, ctx: commands.Context, name: str, avatar_url: str, keyword: str):
        """
        ADMIN SEULEMENT - Ajoute un profil au bot (keyword est comme le ping mais c'est pas un ping discord)
        :param ctx:
        :param name: Nom du profil
        :param avatar_url: URL de l'image de l'avatar du profil
        :param keyword: Pour le ping
        :return:
        """
        config = Cf.get_config(ctx.guild.id)
        if not config["enable_ai"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),description=f"Désolé, mais l'IA n'est pas activé sur ce serveur !"),ephemeral=True)
            return

        profiles = Cf.get_profiles(ctx.guild.id)
        if name in profiles:
            await ctx.send(f"Le profil que vous voulez créer existe déjà. Voulez-vous le modifier ou le supprimer ? Essayez `/profile_edit` ou `/profile_delete`.", ephemeral=True)
            return
        if name == "BelloBot":
            await ctx.send(f"Vous ne pouvez pas utiliser BelloBot comme nom de profil.", ephemeral=True)
            return
        webhook = await ctx.channel.create_webhook(name=name)
        profiles[name] = {"pp_url": avatar_url, "keyword": keyword, "webhook_id": webhook.id}
        Cf.set_profiles(ctx.guild.id, profiles)

        await ctx.send(f"Vous avez bien créé un profil au nom de **{name}**. Donnez lui des règles et du lore avec `/remembers_add`.", ephemeral=True)

    @guild_only
    @commands.hybrid_command(name="profile_edit")
    @commands.has_permissions(administrator=True)
    @app_commands.autocomplete(profile=profile_autocomplete)
    async def profile_edit(self, ctx: commands.Context, profile: str, name: str="", avatar_url: str="", keyword: str=""):
        """
        ADMIN SEULEMENT - Modifie un profil
        :param ctx:
        :param profile: Profil à modifier
        :param name: Nouveau nom du profil
        :param avatar_url: Nouvelle URL de l'image de l'avatar du profil
        :param keyword: Nouveau mot pour le ping
        :return:
        """
        config = Cf.get_config(ctx.guild.id)
        if not config["enable_ai"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais l'IA n'est pas activé sur ce serveur !"),
                           ephemeral=True)
            return

        profiles = Cf.get_profiles(ctx.guild.id)
        if not profile in profiles:
            await ctx.send(
                f"Le profil que vous voulez modifier n'existe pas. Voulez-vous le créer ? Essayez `/profile_add`.",
                ephemeral=True)
            return
        if name == "BelloBot":
            await ctx.send(f"Vous ne pouvez pas utiliser BelloBot comme nom de profil.", ephemeral=True)
            return

        if name != "":
            profiles[name] = profiles[profile]
            del profiles[profile]

            remembers = Cf.get_remembers(ctx.guild.id)
            if profile in remembers:
                remembers[name] = remembers[profile]
                del remembers[profile]
                Cf.set_remembers(ctx.guild.id, remembers)

            profile = name
        if avatar_url != "":
            profiles[profile]["pp_url"] = avatar_url
        if keyword != "":
            profiles[profile]["keyword"] = keyword

        Cf.set_profiles(ctx.guild.id, profiles)
        await ctx.send(f"Vous avez bien modifié le profil de **{profile}**.", ephemeral=True)

    @guild_only
    @commands.hybrid_command(name="profile_delete")
    @commands.has_permissions(administrator=True)
    @app_commands.autocomplete(profile=profile_autocomplete)
    async def profile_delete(self, ctx: commands.Context, profile: str):
        """
        ADMIN SEULEMENT - Supprime un profil (les remembers ne sont pas supprimés)
        :param ctx:
        :param profile: Profil à supprimer
        :return:
        """
        config = Cf.get_config(ctx.guild.id)
        if not config["enable_ai"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais l'IA n'est pas activé sur ce serveur !"),
                           ephemeral=True)
            return

        profiles = Cf.get_profiles(ctx.guild.id)
        if not profile in profiles:
            await ctx.send(
                f"Le profil que vous voulez supprimer n'existe pas. Tant mieux !",
                ephemeral=True)
            return
        if profile == "BelloBot":
            await ctx.send(f"Vous ne pouvez pas supprimer BelloBot zebi", ephemeral=True)
            return

        del profiles[profile]
        Cf.set_profiles(ctx.guild.id, profiles)

        await ctx.send(f"Vous bien avez supprimé le profil de **{profile}**. Il est ded 💀", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Ai(bot))