import discord
from discord.app_commands import autocomplete
from discord.ext import commands
import bot_package.custom_func as Cf
from discord import app_commands
from bot_package.data import item_trad
from datetime import datetime, timedelta, UTC

class ShopSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Petite Potion d'Expérience",
                description="Double l'XP reçu pendant 1 jour • 500",
                value="small_xp_potion",
                emoji="🧪"
            ),
            discord.SelectOption(
                label="Petite Potion de Cupidité",
                description="Double l'argent reçu pendant 1 jour • 1000",
                value="small_money_potion",
                emoji="🧪"
            ),
            discord.SelectOption(
                label="Back Door",
                description="Vous permet d'uploader des fichiers pendant 3 mois • 1000₣",
                value="back_door",
                emoji="🚪"
            ),
            discord.SelectOption(
                label="Audacity",
                description="Vous permet d'utiliser des soundboards et d'envoyer des messages vocaux pendant 3 mois • 1000₣",
                value="audacity",
                emoji="🎧"
            ),
            discord.SelectOption(
                label="Nintendo Switch 17",
                description="Permet de lancer une activité dans un vocal pendant 3 mois • 2000₣",
                value="nintendo_switch_17",
                emoji="🎮"
            ),
            discord.SelectOption(
                label="Partenariat avec l'IFOP",
                description="Permet de créer des sondages pendant 3 mois • 1000₣",
                value="ifop",
                emoji="🎤"
            ),
            discord.SelectOption(
                label="Site web",
                description="Permet d'intégrer des liens pendant 3 mois • 500₣",
                value="site_web",
                emoji="🌐"
            ),
            discord.SelectOption(
                label="External Plexus",
                description="Vous permet d'utiliser des emojis, des autocollants, etc externes pendant 3 mois • 250₣",
                value="external_plexus",
                emoji="🌐"
            ),
            discord.SelectOption(
                label="Microphone",
                description="Donne la voix prioritaire en vocal pendant 3 mois • 4000₣",
                value="microphone",
                emoji="🎤"
            ),
            discord.SelectOption(
                label="Formule 1",
                description="Permet d'ignorer le mode lent pendant 3 mois • 5000₣",
                value="formule_1",
                emoji="🏎️"
            ),
            discord.SelectOption(
                label="Name Tag",
                description="Permet de renommer quelqu'un une fois (attention, punition si jugé humiliant) • 8000₣",
                value="name_tag",
                emoji="🏷️"
            ),
            discord.SelectOption(
                label="Ban Hammer",
                description="Permet de bannir quelqu'un pendant une durée inférieure à 1 jour • 50 000₣",
                value="ban_hammer",
                emoji="🔨"
            ),
        ]

        super().__init__(
            placeholder="Choisis un objet à acheter...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        item = self.values[0]
        prices = {
            "small_xp_potion": 500,
            "small_money_potion": 1000,
            "back_door": 1000,
            "audacity": 1000,
            "nintendo_switch_17": 2000,
            "ifop": 1000,
            "site_web": 5000,
            "external_plexus": 250,
            "microphone": 4000,
            "formule_1": 5000,
            "name_tag": 8000,
            "ban_hammer": 50000,
        }
        price = prices[item]
        user = interaction.user
        user_data = Cf.read_json(f"files/user_info/{interaction.guild.id}/{user.id}.json")
        wallet = user_data["money"]
        if wallet > price:
            user_data["money"] -= price
            Cf.write_json(user_data, f"files/user_info/{interaction.guild.id}/{user.id}.json")
            Cf.add_item(interaction.guild.id, user.id, item)
            embed = discord.Embed(color=discord.Color.blue(), title="Merci pour votre achat !", description="Revenez plus tard !")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(color=discord.Color.red(), title="Vous n'avez pas assez d'argent pour acheter ça",
                          description="Bah alors ? On est pauvre ? ༼ つ XD ༽つ")
            await interaction.response.send_message(embed=embed, ephemeral=True)

class ShopView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(ShopSelect())

async def use_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=item_trad[item], value=item) for item in item_trad
    ]

class Shop(commands.Cog):
    """
    Permet d'acheter et d'utiliser des items donnant des effets sur l'XP et l'argent ou des permissions
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="shop")
    async def shop(self, ctx: commands.Context):
        """
        Affiche le shop, où l'on peut acheter toutes sortes d'objets...
        :param ctx:
        :return:
        """
        embed = discord.Embed(
            title="🛒 SHOP",
            description="Bienvenue au Shop.\nSélectionne un objet ci-dessous.",
            color=discord.Color.gold()
        )
        await ctx.send(
            embed=embed,
            view=ShopView()
        )

    @commands.hybrid_command(name="use")
    @app_commands.autocomplete(item=use_autocomplete)
    async def use(self, ctx: commands.Context, item: str, target_user: discord.User | None = None, name: str | None = None, time_in_hours: int | None = None):
        """
        Permet d'utiliser un objet.
        :param ctx:
        :param item: Objet à utiliser
        :param target_user: Utilisateur ciblé (pour le Name Tag et le Ban Hammer)
        :param name: Nom à donner (pour le Name Tag)
        :param time_in_hours: Temps banni en heures (pour le Ban Hammer)
        :return:
        """
        user = ctx.author
        data = Cf.get_user_data(user.id, ctx.guild.id)
        if item in data["items"]:
            if data["items"][item] > 0:
                data["items"][item] -= 1
                config = Cf.get_config(ctx.guild.id)
                x2_xp_role = await ctx.guild.fetch_role(
                    config["x2_xp_role"])
                x2_money_role = await ctx.guild.fetch_role(
                    config["x2_money_role"])
                file_role = await ctx.guild.fetch_role(
                    config["file_role"])
                soundboard_role = await ctx.guild.fetch_role(
                    config["soundboard_role"])
                game_role = await ctx.guild.fetch_role(
                    config["game_role"])
                poll_role = await ctx.guild.fetch_role(
                    config["poll_role"])
                link_role = await ctx.guild.fetch_role(
                    config["link_role"])
                extern_role = await ctx.guild.fetch_role(
                    config["extern_role"])
                priority_voice_role = await ctx.guild.fetch_role(
                    config["priority_voice_role"])
                bypass_slow_mode_role = await ctx.guild.fetch_role(
                    config["bypass_slow_mode_role"])
                if item == "small_xp_potion":
                    data["mult_xp"] = 2
                    data["temp_effects"]["boost_xp"] = (datetime.now(UTC) + timedelta(days=1)).isoformat()
                    await user.add_roles(x2_xp_role)
                    await ctx.send("X2 XP pendant 1 jour !", ephemeral=True)

                elif item == "small_money_potion":
                    data["mult_money"] = 2
                    data["temp_effects"]["boost_money"] = (datetime.now(UTC) + timedelta(days=1)).isoformat()
                    await user.add_roles(x2_money_role)
                    await ctx.send("X2 Argent pendant 1 jour !", ephemeral=True)

                elif item == "back_door":
                    data["temp_effects"]["file"] = (datetime.now(UTC) + timedelta(days=31 * 3)).isoformat()
                    await user.add_roles(file_role)
                    await ctx.send("Vous pouvez maintenant envoyer des fichiers !",
                                                            ephemeral=True)

                elif item == "audacity ":
                    data["temp_effects"]["soundboard"] = (datetime.now(UTC) + timedelta(days=31 * 3)).isoformat()
                    await user.add_roles(soundboard_role)
                    await ctx.send("Vous pouvez maintenant utiliser le soundborad !",
                                                            ephemeral=True)

                elif item == "nintendo_switch_17":
                    data["temp_effects"]["game"] = (datetime.now(UTC) + timedelta(days=31 * 3)).isoformat()
                    await user.add_roles(game_role)
                    await ctx.send("Vous pouvez maintenant utiliser les applications !",
                                                            ephemeral=True)

                elif item == "ifop":
                    data["temp_effects"]["poll"] = (datetime.now(UTC) + timedelta(days=31 * 3)).isoformat()
                    await user.add_roles(poll_role)
                    await ctx.send("Vous pouvez maintenant créer des sondages !",
                                                            ephemeral=True)

                elif item == "site_web":
                    data["temp_effects"]["link"] = (datetime.now(UTC) + timedelta(days=31 * 3)).isoformat()
                    await user.add_roles(link_role)
                    await ctx.send("Vous pouvez maintenant intégrer des liens !",
                                                            ephemeral=True)

                elif item == "external_plexus":
                    data["temp_effects"]["extern"] = (datetime.now(UTC) + timedelta(days=31 * 3)).isoformat()
                    await user.add_roles(extern_role)
                    await ctx.send(
                        "Vous pouvez maintenant utiliser des emojis, autocollants, soundborads et applications externes !",
                        ephemeral=True)

                elif item == "microphone":
                    data["temp_effects"]["priority_voice"] = (datetime.now(UTC) + timedelta(days=31 * 3)).isoformat()
                    await user.add_roles(priority_voice_role)
                    await ctx.send("Vous avez maintenant la voix prioritaire en vocal !",
                                                            ephemeral=True)

                elif item == "formule_1":
                    data["temp_effects"]["bypass_slow_mode"] = (datetime.now(UTC) + timedelta(days=31 * 3)).isoformat()
                    await user.add_roles(bypass_slow_mode_role)
                    await ctx.send("Vous pouvez maintenant contourner le mode lent !",
                                                            ephemeral=True)

                elif item == "name_tag":
                    if target_user:
                        if name:
                            await target_user.edit(nick=name)
                            await ctx.send(
                                f"Le pseudo de {target_user.mention} a bien été renommé ! ○( ＾皿＾)っ Hehehe…")
                        else:
                            await ctx.send(f"Veuillez indiquer un nom.", ephemeral=True)
                            if "name_tag" in data["items"]:
                                data["items"]["name_tag"] += 1
                            else:
                                data["items"]["name_tag"] = 1
                    else:
                        await ctx.send(f"Veuillez indiquer un utilisateur.", ephemeral=True)
                        if "name_tag" in data["items"]:
                            data["items"]["name_tag"] += 1
                        else:
                            data["items"]["name_tag"] = 1

                elif item == "ban_hammer":
                    if target_user:
                        member = await ctx.guild.fetch_member(target_user.id)
                        if 0.16666666666666667777777777777777 < time_in_hours < 24:
                            await member.timeout(timedelta(hours=time_in_hours), reason="Ban hammer")
                            await ctx.send(
                                f"Vous avez bien mute {target_user.mention} pendant {time_in_hours} heures ! Baha noob")
                        else:
                            await ctx.send(f"Le temps doit être entre 10min et 24h",
                                                                    ephemeral=True)
                    else:
                        await ctx.send(f"Veuillez indiquer un utilisateur.", ephemeral=True)
                Cf.set_user_data(user.id, ctx.guild.id, data)
            else:
                await ctx.send(
                    f"Vous n'avez pas cet item :p\n Vous pouvez l'acheter au shop avec /shop", ephemeral=True)
        else:
            await ctx.send(
                f"Vous n'avez pas cet item :p\n Vous pouvez l'acheter au shop avec /shop", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Shop(bot))