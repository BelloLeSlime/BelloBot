import discord
from discord.ext import commands
from discord import app_commands
import bot_package.custom_func as Cf
from bot_package.data import flamcoin_symbol
from datetime import datetime

class Stats(commands.Cog):
    """
    Permet de voir et gérer les statistiques niveau XP et argent
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="xp")
    async def xp(self, ctx: commands.Context, user: discord.User = None):
        """
        Permet de regarder le nombre d'XP d'utilisateur
        :param ctx: Context
        :param user: Utilisateur
        :return:
        """
        if user is None:
            user = ctx.author
        user_data_xp = Cf.get_user_data(user.id, ctx.guild.id)
        embed = discord.Embed(color=discord.Color.blue(), title=f"Niveau et XP de {user.display_name}")
        if user == self.bot.user:
            embed.description = f"Je suis au niveau {user_data_xp['level']}, j'ai {user_data_xp['xp']} xp et il me manque {user_data_xp["level"] * 15 - user_data_xp['xp']} xp pour passer au niveau {user_data_xp['level'] + 1} ༼ つ ◕_◕ ༽つ"
        elif user == ctx.author:
            embed.description = f"Tu es au niveau {user_data_xp['level']}, tu as {user_data_xp['xp']} xp et il te manque {user_data_xp["level"] * 15 - user_data_xp['xp']} xp pour passer au niveau {user_data_xp['level'] + 1} :p"
        else:
            embed.description = f"{user.display_name} est au niveau {user_data_xp['level']}, il a {user_data_xp['xp']} xp et il lui manque {user_data_xp["level"] * 15 - user_data_xp['xp']} xp pour passer au niveau {user_data_xp['level'] + 1} :p"
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="wallet")
    async def wallet(self, ctx: commands.Context, user: discord.User = None):
        """
        Permet de regarder le niveau d'argent d'un utilisateur
        :param ctx: Context
        :param user: Utilisateur
        :return:
        """
        if user is None:
            user = ctx.author
        user_data_xp = Cf.get_user_data(user.id, ctx.guild.id)
        money = user_data_xp["money"]
        embed = discord.Embed(color=discord.Color.green(), title=f"Porte-feuilles de {user.display_name}")
        if user == self.bot.user:
            embed.description = f"J'ai actuellement {money}₣."
        elif user == ctx.author:
            embed.description = f"Tu as actuellement {money}₣."
        else:
            embed.description = f"{user.display_name} a actuellement {money}₣."
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="inventory")
    async def inventory(self, ctx: commands.Context, user: discord.User | None = None):
        """
        Affiche l'inventaire d'un utilisateur
        :param ctx: Context
        :param user: Utilisateur
        :return:
        """
        if user is None:
            user = ctx.author
        user_data = Cf.get_user_data(user.id, ctx.guild.id)
        shop = Cf.get_shop(ctx.guild.id)
        inventory = user_data["items"].copy()
        description = ""
        for item in inventory:
            if not item in shop.keys():
                del user_data["items"][item]
                Cf.set_user_data(user.id, ctx.guild.id, user_data)
                continue
            name = shop[item]["name"]
            description += f"**{shop[item]["emoji"]} {name}** : {inventory[item]} - {shop[item]["description"]}\n"
        embed = discord.Embed(title=f" Inventaire de {user.display_name} :", description=description, color=discord.Color.green())
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="stats")
    async def stats(self, ctx: commands.Context, user: discord.User | None = None):
        """
        Affiche les statistiques d'un utilisateur (XP, argent, effets temporaires, inventaire)
        :param ctx: Context
        :param user: Utilisateur
        :return:
        """
        user = ctx.author if user == None else user
        user_data = Cf.get_user_data(user.id, ctx.guild.id)
        level = user_data["level"]
        xp = user_data["xp"]
        money = user_data["money"]
        effects = user_data["temp_effects"].copy()
        inventory = user_data["items"].copy()
        shop = Cf.get_shop(ctx.guild.id)

        embed = discord.Embed(title = f"Stats de {user.display_name} :", color = discord.Color.green())
        descr = ""
        descr += f"**Niveau** : **{level}**\n"
        descr += f"**XP** : **{xp}**/**{level * 15}** (il manque **{level * 15 - xp}** pour le prochain niveau)\n"
        descr += f"**Argent** : **{money}₣**\n"
        descr += f"**Effets temporaires** : \n"
        for effect in effects.keys():
            if not effect in shop.keys():
                del user_data["temp_effects"][effect]
                Cf.set_user_data(user.id, ctx.guild.id, user_data)
                continue
            dt = datetime.fromisoformat(effects[effect])
            expires_at = dt.strftime("%d/%m/%Y à %H:%M")
            name = shop[effect]["name"]
            descr += f">  -**{name}** : expire le {expires_at}\n"
        descr += f"**Inventaire** : \n"
        for item in inventory.keys():
            if not item in shop.keys():
                del user_data["items"][item]
                Cf.set_user_data(user.id, ctx.guild.id, user_data)
                continue
            name = shop[item]["name"]
            descr += f">  **{shop[item]["emoji"]}{name}** : {inventory[item]} - {shop[item]["description"]}\n"

        embed.description = descr

        await ctx.send(embed=embed)

    async def gift_what_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name="xp", value="xp"),
            app_commands.Choice(name="money", value="money"),
        ]

    @commands.hybrid_command(name="gift")
    @app_commands.autocomplete(what=gift_what_autocomplete)
    async def gift(self, ctx: commands.Context, user: discord.User, what: str, amount: int):
        """
        Permet de donner de l'XP ou de l'argent à un autre utilisateur
        :param ctx: Context
        :param user: Utilisateur qui reçoit le cadeau
        :param what: XP ou argent
        :param amount: Combien d'XP ou d'argent donner ?
        :return:
        """

        if amount < 0:
            embed = discord.Embed(color=discord.Color.red(), description=f"Bien tenté, mais vous ne pouvez pas voler {user.display_name} !")
            await ctx.send(embed=embed)
            return

        user_1 = ctx.author
        user_2 = user

        user_1_data = Cf.get_user_data(user_1.id, ctx.guild.id)
        if user_1_data[what] < amount:
            embed = discord.Embed(color=discord.Color.red(), description=f"Vous n'avez pas assez d'{"XP" if what == "xp" else "argent"} à donner :/")
            await ctx.send(embed=embed)
        else:
            user_2_data = Cf.get_user_data(user_2.id, ctx.guild.id)
            user_1_data[what] -= amount
            user_2_data[what] += amount
            Cf.set_user_data(user_1.id, ctx.guild.id, user_1_data)
            Cf.set_user_data(user_2.id, ctx.guild.id, user_2_data)

            embed = discord.Embed(color=discord.Color.green(), description=f"Vous avez bien envoyé {amount}{"XP" if what == "xp" else flamcoin_symbol} à {user_2.display_name} !")
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Stats(bot))
