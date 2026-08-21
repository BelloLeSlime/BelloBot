import discord
from discord.ext import commands
import bot_package.custom_func as Cf

class Alarm(commands.Cog):
    """
    Permet de gérer des alarmes, qui envoient un ping dans un salon à une heure précise
    """
    def __init__(self, bot):
        self.bot = bot
        self.days_trad = {
            0: "Lundi",
            1: "Mardi",
            2: "Mercredi",
            3: "Jeudi",
            4: "Vendredi",
            5: "Samedi",
            6: "Dimanche"
        }

    @commands.hybrid_command(name="alarm")
    async def alarm(self, ctx: commands.Context):
        """
        Affiche le panel des alarmes
        :param ctx: Context
        :return:
        """
        config = Cf.get_config(ctx.guild.id)
        if not config["enable_alarm"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais les alarmes ne sont pas activées sur ce serveur !"),
                           ephemeral=True)
            return

        alarms = Cf.get_alarms(ctx.author.id, ctx.guild.id)
        embed = discord.Embed(color=discord.Color.green(), title=f"Alarmes de {ctx.author.display_name}")
        descr = ""

        for alarm in alarms:
            id = alarm
            name = alarms[alarm]["name"]
            time = alarms[alarm]["time"]
            days = alarms[alarm]["days"]
            days_str = ""
            for day in days:
                day_str = self.days_trad[day]
                days_str += day_str + ", "
            days_str.removesuffix(", ")
            one_shot = alarms[alarm]["one_shot"]
            enabled = alarms[alarm]["enabled"]
            descr += f"""
    **{id} : {name}** :
    > Sonne à {time}
    {f"> Se répête {days_str}\n" if not one_shot else ""}{"> Sonne qu'une seule fois\n" if one_shot else ""}{"> Activé" if enabled else "> Désactivé"}

    """
        embed.description = descr
        await ctx.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(name="create_alarm")
    async def create_alarm(self, ctx: commands.Context, name: str, hour: int, minutes: int, repeat: bool = False,
                           enabled: bool = True, lundi: bool = False, mardi: bool = False, mercredi: bool = False,
                           jeudi: bool = False, vendredi: bool = False, samedi: bool = False, dimanche: bool = False):
        """
        Créée une alarme
        :param ctx: Context
        :param name: Nom
        :param hour: Heure
        :param minutes: Minutes
        :param repeat: Répète
        :param enabled: Activé
        :param lundi: Lundi
        :param mardi: Mardi
        :param mercredi: Mercredi
        :param jeudi: Jeudi
        :param vendredi: Vendredi
        :param samedi: Samedi
        :param dimanche: Dimanche
        :return:
        """

        config = Cf.get_config(ctx.guild.id)
        if not config["enable_alarm"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais les alarmes ne sont pas activées sur ce serveur !"),
                           ephemeral=True)
            return

        alarms = Cf.get_alarms(ctx.author.id, ctx.guild.id)
        ints = [int(key) for key in alarms.keys()]
        next_id = max(ints) + 1 if alarms else 0
        if repeat and not (lundi or mardi or mercredi or jeudi or vendredi or samedi or dimanche):
            await ctx.send(
                "Vous devez soit ne pas répéter l'alarme, soit entrer au moins un jour !", ephemeral=True)
            return
        if (hour < 0 or hour > 23) or (minutes < 0 or minutes > 59):
            await ctx.send("Merci d'envoyer une heure valide !", ephemeral=True)
            return
        days = []
        if lundi:
            days.append(0)
        if mardi:
            days.append(1)
        if mercredi:
            days.append(2)
        if jeudi:
            days.append(3)
        if vendredi:
            days.append(4)
        if samedi:
            days.append(5)
        if dimanche:
            days.append(6)

        alarm = {
            "name": name,
            "time": f"{hour:02d}:{minutes:02d}",
            "days": days,
            "one_shot": not repeat,
            "enabled": enabled,
        }

        alarms[next_id] = alarm

        Cf.set_alarms(ctx.author.id, ctx.guild.id, alarms)
        await ctx.send(f"Alarme {name} créée !", ephemeral=True)

    @commands.hybrid_command(name="edit_alarm")
    async def edit_alarm(self, ctx: commands.Context, id: int, name: str = None, hour: int = None, minutes: int = None,
                         repeat: bool = None, enabled: bool = None, lundi: bool = None, mardi: bool = None,
                         mercredi: bool = None, jeudi: bool = None, vendredi: bool = None, samedi: bool = None,
                         dimanche: bool = None):
        """
        Modifie une alarme existante
        :param ctx: Context
        :param id: ID de l'alarme
        :param name: Nom
        :param hour: Heure
        :param minutes: Minutes
        :param repeat: Répète
        :param enabled: Activé
        :param lundi: Lundi
        :param mardi: Mardi
        :param mercredi: Mercredi
        :param jeudi: Jeudi
        :param vendredi: Vendredi
        :param samedi: Samedi
        :param dimanche: Dimanche
        :return:
        """

        config = Cf.get_config(ctx.guild.id)
        if not config["enable_alarm"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais les alarmes ne sont pas activées sur ce serveur !"),
                           ephemeral=True)
            return

        alarms = Cf.get_alarms(ctx.author.id, ctx.guild.id)
        if not str(id) in alarms.keys():
            await ctx.send(f"Vous n'avez aucune alarme avec l'ID {id}.", ephemeral=True)
            return

        alarm = alarms[str(id)]
        if name is None:
            name = alarm["name"]
        if hour is None:
            hour = int(alarm["time"].split(":")[0])
        if minutes is None:
            minutes = int(alarm["time"].split(":")[1])
        if repeat is None:
            repeat = not alarm["one_shot"]
        if enabled is None:
            enabled = alarm["enabled"]
        if lundi is None:
            lundi = 0 in alarm["days"]
        if mardi is None:
            mardi = 1 in alarm["days"]
        if mercredi is None:
            mercredi = 2 in alarm["days"]
        if jeudi is None:
            jeudi = 3 in alarm["days"]
        if vendredi is None:
            vendredi = 4 in alarm["days"]
        if samedi is None:
            samedi = 5 in alarm["days"]
        if dimanche is None:
            dimanche = 6 in alarm["days"]

        if repeat and not (lundi or mardi or mercredi or jeudi or vendredi or samedi or dimanche):
            await ctx.send(
                "Vous devez soit ne pas répéter l'alarme, soit entrer au moins un jour !", ephemeral=True)
            return
        if (hour < 0 or hour > 23) or (minutes < 0 or minutes > 59):
            await ctx.send("Merci d'envoyer une heure valide !", ephemeral=True)
            return
        days = []
        if lundi:
            days.append(0)
        if mardi:
            days.append(1)
        if mercredi:
            days.append(2)
        if jeudi:
            days.append(3)
        if vendredi:
            days.append(4)
        if samedi:
            days.append(5)
        if dimanche:
            days.append(6)

        alarm = {
            "name": name,
            "time": f"{hour:02d}:{minutes:02d}",
            "days": days,
            "one_shot": not repeat,
            "enabled": enabled,
        }

        alarms[str(id)] = alarm

        Cf.set_alarms(ctx.author.id, ctx.guild.id, alarms)
        await ctx.send(f"Alarme {name} éditée !", ephemeral=True)

    @commands.hybrid_command(name="delete_alarm")
    async def delete_alarm(self, ctx: commands.Context, id: int):
        """
        Supprime une alarme
        :param ctx: Context
        :param id: ID de l'alarme
        :return:
        """
        config = Cf.get_config(ctx.guild.id)
        if not config["enable_alarm"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais les alarmes ne sont pas activées sur ce serveur !"),
                           ephemeral=True)
            return

        alarms = Cf.get_alarms(ctx.author.id, ctx.guild.id)
        if str(id) not in alarms.keys():
            await ctx.send(f"Vous n'avez pas d'alarme avec l'ID {id}.", ephemeral=True)
            return
        del alarms[str(id)]
        Cf.set_alarms(ctx.author.id, ctx.guild.id, alarms)
        await ctx.send(f"L'alarme {id} supprimé !", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Alarm(bot))