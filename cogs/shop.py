import discord
from discord.ext import commands
import bot_package.custom_func as Cf
from discord import app_commands
from bot_package.data import flamcoin_symbol
import re
from datetime import datetime, timedelta, UTC

class ShopSelect(discord.ui.Select):
    def __init__(self, guild_id):
        options = []
        self.guild_id = guild_id
        shop = Cf.get_shop(self.guild_id)
        for item in shop:
            options.append(discord.SelectOption(
                label=shop[item]["name"],
                value=item,
                emoji=shop[item]["emoji"],
                description=shop[item]["description"] + " - " + str(shop[item]["price"]) + flamcoin_symbol,
            ))

        super().__init__(
            placeholder="Choisis un objet à acheter...",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        item = self.values[0]
        id = item
        item = Cf.get_shop(self.guild_id)[item]
        price = item["price"]
        user = interaction.user
        user_data = Cf.get_user_data(user.id, self.guild_id)
        wallet = user_data["money"]
        if wallet > price:
            user_data["money"] -= price
            Cf.set_user_data(user.id, self.guild_id, user_data)
            Cf.add_item(interaction.guild.id, user.id, id)
            embed = discord.Embed(color=discord.Color.blue(), title="Merci pour votre achat !", description="Revenez plus tard ! Utilisez votre nouvel objet avec /use !")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(color=discord.Color.red(), title="Vous n'avez pas assez d'argent pour acheter ça",
                          description=f"Cet objet coûte {price}{flamcoin_symbol} mais vous n'en avez que {wallet}.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

class ShopView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__()
        self.add_item(ShopSelect(guild_id))

async def use_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    shop = Cf.get_shop(interaction.guild_id)
    return [
        app_commands.Choice(name=shop[item]["name"], value=item) for item in shop
    ]

def parse_duration(duration: str) -> datetime:
    match = re.fullmatch(r"(\d+)(min|h|d|w)", duration.lower())
    if match is None:
        raise ValueError("Durée invalide")

    amount = int(match.group(1))
    unit = match.group(2)

    now = datetime.now(UTC)

    if unit == "min":
        return now + timedelta(minutes=amount)
    elif unit == "h":
        return now + timedelta(hours=amount)
    elif unit == "d":
        return now + timedelta(days=amount)
    elif unit == "w":
        return now + timedelta(weeks=amount)
    return now

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
        config = Cf.get_config(ctx.guild.id)
        if not config["enable_xp"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais l'économie n'est pas activée sur ce serveur !"),
                           ephemeral=True)
            return

        if not config["enable_shop"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais le shop n'est pas activée sur ce serveur !"),
                           ephemeral=True)
            return

        shop = Cf.get_shop(ctx.guild.id)
        if shop == {}:
            embed = discord.Embed(color=discord.Color.red(), description=f"Désolé, mais il n'y a rien à vendre ici !")
            await ctx.send(embed=embed)
            return
        embed = discord.Embed(
            title="🛒 SHOP",
            description="Bienvenue au Shop.\nSélectionne un objet ci-dessous.",
            color=discord.Color.gold()
        )
        await ctx.send(
            embed=embed,
            view=ShopView(ctx.guild.id)
        )

    @commands.hybrid_command(name="use")
    @app_commands.autocomplete(item=use_autocomplete)
    async def use(self, ctx: commands.Context, item: str, target_user: discord.User | None = None, name: str | None = None):
        """
        Permet d'utiliser un objet.
        :param ctx:
        :param item: Objet à utiliser
        :param target_user: Utilisateur ciblé (si l'objet le nécéssite)
        :param name: Nom à donner (si l'objet le nécéssite)
        :return:
        """

        config = Cf.get_config(ctx.guild.id)
        if not config["enable_xp"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais l'économie n'est pas activée sur ce serveur !"),
                           ephemeral=True)
            return

        if not config["enable_shop"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais le shop n'est pas activée sur ce serveur !"),
                           ephemeral=True)
            return

        user = ctx.author
        user_data = Cf.get_user_data(user.id, ctx.guild.id)
        shop = Cf.get_shop(ctx.guild.id)

        if not item in shop:
            embed = discord.Embed(color=discord.Color.red(), description=f"Désolé, cet objet n'existe pas")
            await ctx.send(embed=embed)
            return

        if not item in user_data["items"].keys():
            embed = discord.Embed(color=discord.Color.red(), description="Vous n'avez pas cet objet. Utilisez /shop pour l'acheter !")
            await ctx.send(embed=embed)
            return


        item_id = item
        item = shop[item]
        type = item["use"]["type"]

        if type == "add_role":
            role_id = item["use"]["role"]
            role = await ctx.guild.fetch_role(role_id)
            await ctx.author.add_roles(role)
            expiration = parse_duration(item["use"]["time"])
            user_data["temp_effects"][item_id] = expiration.isoformat()


        elif type == "mult_xp":
            role_id = item["use"]["role"]
            role = await ctx.guild.fetch_role(role_id)
            await ctx.author.add_roles(role)
            user_data["mult_xp"] = item["use"]["mult"]
            expiration = parse_duration(item["use"]["time"])
            user_data["temp_effects"][item_id] = expiration.isoformat()

        elif type == "mult_money":
            role_id = item["use"]["role"]
            role = await ctx.guild.fetch_role(role_id)
            await ctx.author.add_roles(role)
            user_data["mult_money"] = item["use"]["mult"]
            expiration = parse_duration(item["use"]["time"])
            user_data["temp_effects"][item_id] = expiration.isoformat()

        elif type == "add_xp":
            user_data["xp"] += item["use"]["amount"]

        elif type == "rename":
            member = await ctx.guild.fetch_member(target_user.id)
            await member.edit(nick=name)


        if user_data["items"][item_id] == 1:
             del user_data["items"][item_id]
        else:
            user_data["items"][item_id] -= 1
        Cf.set_user_data(user.id, ctx.guild.id, user_data)

        embed = discord.Embed(color=discord.Color.blue(), description=item["use"]["description"])
        await ctx.send(embed=embed)

    async def shop_add_type_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name="add_role", value="add_role"),
            app_commands.Choice(name="mult_xp", value="mult_xp"),
            app_commands.Choice(name="mult_money", value="mult_money"),
            app_commands.Choice(name="add_xp", value="add_xp"),
            app_commands.Choice(name="rename", value="rename"),
        ]

    @commands.hybrid_command(name="shop_add")
    @app_commands.autocomplete(type=shop_add_type_autocomplete)
    @commands.has_permissions(administrator=True)
    async def shop_add(self, ctx: commands.Context, name: str, emoji: str, description: str, price: int, type: str, use_description: str, role: discord.Role = None, time: str = None, mult: int = None, amount: int = None):
        """
        Ajoute un objet dans le shop
        :param ctx: Context
        :param name: Nom de l'objet
        :param emoji: Emoji de l'objet
        :param description: Description de l'objet dans le shop
        :param price: Prix de l'objet en ₣
        :param type: Type d'objet (ajouter un role, multiplier l'XP ou l'argent, ajouter de l'XP ou rename quelqu'un
        :param use_description: Description de l'objet au moment de l'utilisation
        :param role: Rôle à attribuer (si type est add_role, mult_xp ou mult_money)
        :param time: Durée de l'utilisation (si type est add_role, mult_xp ou mult_money)
        :param mult: Multiplication de l'XP ou de l'argent (si type est mult_xp ou mult_money)
        :param amount: XP à ajouter (si type est add_xp)
        :return:
        """

        config = Cf.get_config(ctx.guild.id)
        if not config["enable_xp"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais l'économie n'est pas activée sur ce serveur !"),
                           ephemeral=True)
            return

        if not config["enable_shop"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais le shop n'est pas activée sur ce serveur !"),
                           ephemeral=True)
            return

        shop = Cf.get_shop(ctx.guild.id)
        last_id = 0
        for item in shop:
            if int(item) > last_id:
                last_id = int(item)
        id = str(last_id + 1)

        shop[id] = {
            "name": name,
            "description": description,
            "emoji": emoji,
            "price": price,
            "use": {
                "type": type,
                "description": use_description,
            }
        }

        if type in ["add_role", "mult_xp", "mult_money"]:
            if not time:
                embed = discord.Embed(color=discord.Color.red(), description="Veuillez indiquer une durée (time)")
                await ctx.send(embed=embed)
                return
            match = re.fullmatch(r"(\d+)(min|h|d|w)", time.lower())
            if match is None:
                embed = discord.Embed(color=discord.Color.red(), description="Veuillez indiquer une durée valide (nombre + min, h, d ou w)")
                await ctx.send(embed=embed)
                return
            shop[id]["use"]["time"] = time
            if not role:
                embed = discord.Embed(color=discord.Color.red(), description="Veuillez indiquer un rôle (role)")
                await ctx.send(embed=embed)
                return
            shop[id]["use"]["role"] = role.id

        if type in ["mult_xp", "mult_money"]:
            if not mult:
                embed = discord.Embed(color=discord.Color.red(), description="Veuillez indiquer un multiplicateur (mult)")
                await ctx.send(embed=embed)
                return
            shop[id]["use"]["mult"] = mult

        if type == "add_xp":
            if not amount:
                embed = discord.Embed(color=discord.Color.red(), description="Veuillez indiquer un nombre d'XP (amount)")
                await ctx.send(embed=embed)
                return
            shop[id]["use"]["amount"] = amount

        Cf.set_shop(ctx.guild.id, shop)

        embed = discord.Embed(color=discord.Color.blue(), description=f"Vous avez bien rajouté **{emoji} {name}** au shop ! Faîtes /shop pour le voir !")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="shop_view")
    @app_commands.autocomplete()
    @commands.has_permissions(administrator=True)
    async def shop_view(self, ctx: commands.Context):
        """
        Permet de voir les items du shop ainsi que leurs effets
        :param ctx:
        :return:
        """
        config = Cf.get_config(ctx.guild.id)
        if not config["enable_xp"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais l'économie n'est pas activée sur ce serveur !"),
                           ephemeral=True)
            return

        if not config["enable_shop"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais le shop n'est pas activée sur ce serveur !"),
                           ephemeral=True)
            return

        shop = Cf.get_shop(ctx.guild.id)
        embed = discord.Embed(color=discord.Color.green(), title="Objets achetables au shop", description=f"")
        for item_id, item in shop.items():
            embed.description += f"""
            - Objet {item_id} : **{item["emoji"]}{item["name"]}**
            > *{item["description"]}*
            > Prix : {item["price"]}{flamcoin_symbol}
            Utilisation :
            > Type : {item["use"]["type"]}
            > Description : {item["use"]["description"]}
            {f"> Rôle : {await ctx.guild.fetch_role(item["use"].get("role"))}\n" if item["use"].get("role") else ""}{f"> Temps : {item["use"].get("time")}\n" if item["use"].get("time") else ""}{f"> Nombre : {item["use"].get("amount")}\n" if item["use"].get("amount") else ""}{f"> Multiplicateur  : {item["use"].get("mult")}\n" if item["use"].get("mult") else ""}
"""
        await ctx.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(name="shop_delete")
    @app_commands.autocomplete(item=use_autocomplete)
    @commands.has_permissions(administrator=True)
    async def shop_delete(self, ctx: commands.Context, item: str):
        """
        Retire un objet du shop et des inventaires
        :param ctx: Context
        :param item: Objet à retirer
        :return:
        """
        config = Cf.get_config(ctx.guild.id)
        if not config["enable_xp"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais l'économie n'est pas activée sur ce serveur !"),
                           ephemeral=True)
            return

        if not config["enable_shop"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais le shop n'est pas activée sur ce serveur !"),
                           ephemeral=True)
            return

        shop = Cf.get_shop(ctx.guild.id)
        name = shop[item]["name"]
        del shop[item]
        Cf.set_shop(ctx.guild.id, shop)

        embed = discord.Embed(color=discord.Color.green(), description=f"L'objet {name} n'existe plus.")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Shop(bot))