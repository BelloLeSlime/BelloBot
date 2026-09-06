import discord
from discord.ext import commands
from discord import app_commands
from bot_package import custom_func as Cf
from bot_package.data import config_text_types, counting_config_keys

async def counting_config_key_autocomplete(interaction, current):
    return [app_commands.Choice(name=key, value=key) for key in counting_config_keys]

class Counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="counting_config")
    @commands.has_permissions(administrator=True)
    @app_commands.autocomplete(key=counting_config_key_autocomplete)
    async def counting_config(self, ctx, key: str, value: str):
        """
        ADMIN SEULEMENT - permet de configurer les règles du comptage
        :param ctx:
        :param key: Clé (donc qu'est-ce qui doit être configuré)
        :param value: Valeur (donc ce qui est configuré pour la clé)
        :return:
        """
        await ctx.defer(ephemeral=True)

        if key not in counting_config_keys.keys():
            await ctx.send(f"Veuillez préciser une clé valide !", ephemeral=True)
            return

        value_type = counting_config_keys[key]

        if value.startswith("<#"):
            channel_id = int(value.removeprefix("<#").removesuffix(">"))
            channel = await ctx.guild.fetch_channel(channel_id)
            value = channel
        elif value.startswith("<@&"):
            role_id = int(value.removeprefix("<@&").removesuffix(">"))
            role = await ctx.guild.fetch_role(role_id)
            value = role
        elif value.isdigit():
            value = int(value)
        elif value in ["True", "False", "true", "false", "yes", "no", "Yes", "No"]:
            value = value in ["True", "true", "yes", "Yes"]
        else:
            value = value

        counting_config = Cf.get_counting(ctx.guild.id)

        if not isinstance(value, counting_config_keys[key]):
            embed = discord.Embed(color=discord.Color.red(), description=f"Veuillez indiquer une valeur valide ! Ça doit être : {config_text_types[counting_config_keys[key]]}")
            await ctx.send(embed=embed, ephemeral=True)
            return

        counting_config[key] = value if not type(value) in [discord.TextChannel, discord.Role, discord.CategoryChannel] else value.id

        lcounting_config = counting_config.copy()
        config_text = ""
        for lkey, lvalue in lcounting_config.items():
            if not lkey in counting_config_keys.keys() and not lkey in ["high_score", "number", "last_talked"]:
                del counting_config[lkey]
                continue
            elif not lkey in counting_config_keys.keys():
                continue
            lvalue_type = counting_config_keys[lkey]
            try:
                if (lvalue_type != int) and (lvalue_type != bool) and (lvalue_type != str):
                    if lvalue_type in [discord.TextChannel, discord.CategoryChannel]:
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

        Cf.set_counting(ctx.guild.id, counting_config)

        embed = discord.Embed(color=discord.Color.blue())
        embed.title = "Configuration du comptage du serveur :"
        embed.description = f"La clé {key} a bien pour valeur {value if value_type in [int, bool, str] else value.mention} ! Voici la configuration du comptage à présent : \n{config_text}"

        await ctx.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(name="counting_set")
    @commands.has_permissions(administrator=True)
    async def counting_set(self, ctx: commands.Context, number: int):
        """
        ADMIN SEULEMENT - Met le nombre actuel à un nombre voulu
        :param ctx:
        :param number: Nombre
        :return:
        """
        counting = Cf.get_counting(ctx.guild.id)
        counting["number"] = number
        if counting["number"] > counting["high_score"]:
            counting["high_score"] = counting["number"]
        Cf.set_counting(ctx.guild.id, counting)

        config = Cf.get_config(ctx.guild.id)
        counting_channel = config["counting_channel"]
        counting_channel: discord.TextChannel|None = await ctx.guild.fetch_channel(counting_channel)
        if counting_channel is None:
            embed = discord.Embed(color=discord.Color.red(),
                                  description=f"Aucun salon n'a été sélectionné pour le comptage. Essayez /config !")
            await ctx.send(embed=embed, ephemeral=True)
            return
        embed = discord.Embed(color=discord.Color.yellow(), description=f"Attention, le nombre a été changé par un administrateur. Désormais, le nombre est **{number}**, donc le prochain nombre est **{number+1}**.")
        await counting_channel.send(embed=embed)

        embed = discord.Embed(color=discord.Color.green(),
                              description=f"Le nombre du comptage a bien été mit à **{number}** !")
        await ctx.send(embed=embed, ephemeral=True)


    @commands.hybrid_command(name="counting_high_score")
    async def counting_high_score(self, ctx: commands.Context):
        """
        Permet d'avoir le meilleur score du comptage du serveur
        :param ctx:
        :return:
        """
        counting = Cf.get_counting(ctx.guild.id)
        embed = discord.Embed(color=discord.Color.blue(), description=f"Le meilleur score du serveur au comptage est **{counting["high_score"]}**.")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Counting(bot))