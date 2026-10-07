import discord
from discord import Interaction
from discord.app_commands import guild_only
from discord.ext import commands
import bot_package.custom_func as Cf
from random import choice, randint

class AlarmCreation(discord.ui.Modal, title="Création d'une alarme"):
    name = discord.ui.TextInput(label="Nom", placeholder=choice(
        ["Réveille toi feignasse", "Piano", "Dentiste", "Va dormir sale bot", "C'EST L'HEURE DU DUDUDUDUDUDUDU DUEL",
         "Ah, c'est l'heure d'aller me faire enculer"]), style=discord.TextStyle.short)
    hours = discord.ui.TextInput(label="Heures", placeholder=str(randint(0, 23)), style=discord.TextStyle.short)
    minutes = discord.ui.TextInput(label="Minutes", placeholder=str(randint(0, 59)), style=discord.TextStyle.short)
    repeat = discord.ui.Label(
        text="Répéter l'alarme",
        component=discord.ui.Checkbox()
    )
    days = discord.ui.Label(
        text="Sélectionne les jours",
        component=discord.ui.CheckboxGroup(
            required=False,
            min_values=0,
            max_values=7,
            options=[
                discord.CheckboxGroupOption(label="Lundi", value="monday", ),
                discord.CheckboxGroupOption(label="Mardi", value="tuesday", ),
                discord.CheckboxGroupOption(label="Mercredi",value="wednesday",),
                discord.CheckboxGroupOption(label="Jeudi",value="thursday",),
                discord.CheckboxGroupOption(label="Vendredi",value="friday",),
                discord.CheckboxGroupOption(label="Samedi",value="saturday",),
                discord.CheckboxGroupOption(label="Dimanche",value="sunday",)
            ]
        )
    )

    def __init__(self):
        super().__init__()
        self.days_trad = {
            0: "Lundi",
            1: "Mardi",
            2: "Mercredi",
            3: "Jeudi",
            4: "Vendredi",
            5: "Samedi",
            6: "Dimanche"
        }

    async def on_submit(self, interaction: discord.Interaction):
        name = self.name.value
        hour = int(self.hours.value)
        minutes = int(self.minutes.value)
        repeat = self.repeat.component.value
        lundi = "monday" in self.days.component.values
        mardi = "tuesday" in self.days.component.values
        mercredi = "wednesday" in self.days.component.values
        jeudi = "thursday" in self.days.component.values
        vendredi = "friday" in self.days.component.values
        samedi = "saturday" in self.days.component.values
        dimanche = "sunday" in self.days.component.values
        enabled = True

        alarms = Cf.get_alarms(interaction.user.id, interaction.guild.id)
        ints = [int(key) for key in alarms.keys()]
        next_id = max(ints) + 1 if alarms else 0
        if repeat and not (lundi or mardi or mercredi or jeudi or vendredi or samedi or dimanche):
            await interaction.response.send_message(
                "Vous devez soit ne pas répéter l'alarme, soit entrer au moins un jour !", ephemeral=True)
            return
        if (hour < 0 or hour > 23) or (minutes < 0 or minutes > 59):
            await interaction.response.send_message("Merci d'envoyer une heure valide !", ephemeral=True)
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

        Cf.set_alarms(interaction.user.id, interaction.guild.id, alarms)

        embed = discord.Embed(color=discord.Color.green(), title=f"Alarmes de {interaction.user.display_name}")

        for alarm in alarms:
            name = alarms[alarm]["name"]
            time = alarms[alarm]["time"]
            days = alarms[alarm]["days"]
            days_str = ""
            for day in days:
                day_str = self.days_trad[day]
                days_str += day_str + ", "
            days_str = days_str.removesuffix(", ")
            one_shot = alarms[alarm]["one_shot"]
            enabled = alarms[alarm]["enabled"]
            embed.add_field(name=name, value=f"""
            > Sonne à {time}
            {f"> Se répête {days_str}\n" if not one_shot else ""}{"> Sonne qu'une seule fois\n" if one_shot else ""}{"> Activé" if enabled else "> Désactivé"}

            """)
        await interaction.response.send_message(embed=embed, view=AlarmPanel(), ephemeral=True)

class AlarmEdition(discord.ui.Modal, title="Modification d'une alarme"):
    def __init__(self, interaction: discord.Interaction, alarm_id: int):
        super().__init__()
        alarms = Cf.get_alarms(interaction.user.id, interaction.guild.id)
        alarm = alarms[str(alarm_id)]

        self.alarm_id = alarm_id
        self.days_trad = {
            0: "Lundi",
            1: "Mardi",
            2: "Mercredi",
            3: "Jeudi",
            4: "Vendredi",
            5: "Samedi",
            6: "Dimanche"
        }

        self.name = discord.ui.TextInput(label="Nom", placeholder=alarm["name"], style=discord.TextStyle.short, required=False)
        self.hours = discord.ui.TextInput(label="Heures", placeholder=alarm["time"][0:2], style=discord.TextStyle.short, required=False)
        self.minutes = discord.ui.TextInput(label="Minutes", placeholder=alarm["time"][3:5], style=discord.TextStyle.short, required=False)
        self.repeat = discord.ui.Label(
            text="Répéter l'alarme",
            component=discord.ui.Checkbox(default=not alarm["one_shot"])
        )
        self.days = discord.ui.Label(
            text="Sélectionne les jours",
            component=discord.ui.CheckboxGroup(
                required=False,
                min_values=0,
                max_values=7,
                options=[
                    discord.CheckboxGroupOption(label="Lundi", value="monday", default=0 in alarm["days"]),
                    discord.CheckboxGroupOption(label="Mardi", value="tuesday", default=1 in alarm["days"]),
                    discord.CheckboxGroupOption(label="Mercredi", value="wednesday", default=2 in alarm["days"]),
                    discord.CheckboxGroupOption(label="Jeudi", value="thursday", default=3 in alarm["days"]),
                    discord.CheckboxGroupOption(label="Vendredi", value="friday", default=4 in alarm["days"]),
                    discord.CheckboxGroupOption(label="Samedi", value="saturday", default=5 in alarm["days"]),
                    discord.CheckboxGroupOption(label="Dimanche", value="sunday", default=6 in alarm["days"])
                ]
            )
        )

        self.add_item(self.name)
        self.add_item(self.hours)
        self.add_item(self.minutes)
        self.add_item(self.repeat)
        self.add_item(self.days)

    async def on_submit(self, interaction: Interaction) -> None:
        alarms = Cf.get_alarms(interaction.user.id, interaction.guild.id)
        alarm = alarms[str(self.alarm_id)]

        name = self.name.value if self.name.value != "" else alarm["name"]
        hour = int(self.hours.value) if self.hours.value != "" else int(alarm["time"][0:2])
        minutes = int(self.minutes.value) if self.minutes.value != "" else int(alarm["time"][3:5])
        repeat = self.repeat.component.value
        lundi = "monday" in self.days.component.values
        mardi = "tuesday" in self.days.component.values
        mercredi = "wednesday" in self.days.component.values
        jeudi = "thursday" in self.days.component.values
        vendredi = "friday" in self.days.component.values
        samedi = "saturday" in self.days.component.values
        dimanche = "sunday" in self.days.component.values
        enabled = alarm["enabled"]

        if repeat and not (lundi or mardi or mercredi or jeudi or vendredi or samedi or dimanche):
            await interaction.response.send_message(
                "Vous devez soit ne pas répéter l'alarme, soit entrer au moins un jour !", ephemeral=True)
            return
        if (hour < 0 or hour > 23) or (minutes < 0 or minutes > 59):
            await interaction.response.send_message("Merci d'envoyer une heure valide !", ephemeral=True)
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

        alarms[str(self.alarm_id)] = alarm

        Cf.set_alarms(interaction.user.id, interaction.guild.id, alarms)

        embed = discord.Embed(color=discord.Color.green(), title=f"Alarmes de {interaction.user.display_name}")

        for alarm in alarms:
            name = alarms[alarm]["name"]
            time = alarms[alarm]["time"]
            days = alarms[alarm]["days"]
            days_str = ""
            for day in days:
                day_str = self.days_trad[day]
                days_str += day_str + ", "
            days_str = days_str.removesuffix(", ")
            one_shot = alarms[alarm]["one_shot"]
            enabled = alarms[alarm]["enabled"]
            embed.add_field(name=name, value=f"""
                    > Sonne à {time}
                    {f"> Se répête {days_str}\n" if not one_shot else ""}{"> Sonne qu'une seule fois\n" if one_shot else ""}{"> Activé" if enabled else "> Désactivé"}

                    """)
        await interaction.response.send_message(embed=embed, view=AlarmPanel(), ephemeral=True)

class AlarmPanel(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Nouvelle alarme", style=discord.ButtonStyle.green)
    async def create_alarm(self, interaction: discord.Interaction, item):
        await interaction.response.send_modal(AlarmCreation())

    @discord.ui.button(label="Modifier une alarme", style=discord.ButtonStyle.blurple)
    async def edit_alarm(self, interaction: discord.Interaction, item):
        alarms = Cf.get_alarms(interaction.user.id, interaction.guild.id)
        if alarms == {}:
            await interaction.response.send_message("Vous n'avez pas d'alarme à modifer, créez-en une avec le `/alarm` !", ephemeral=True)
            return
        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.blue(), description="Veuillez choisir une alarme à modifier"), view=EditAlarm(interaction), ephemeral=True)

    @discord.ui.button(label="Supprimer une alarme", style=discord.ButtonStyle.red)
    async def delete_alarm(self, interaction: discord.Interaction, item):
        alarms = Cf.get_alarms(interaction.user.id, interaction.guild.id)
        if alarms == {}:
            await interaction.response.send_message(
                "Vous n'avez pas d'alarme à supprimer, créez-en une avec le `/alarm` !", ephemeral=True)
            return
        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.blue(), description="Veuillez choisir une alarme à supprimer"), view=RemoveAlarm(interaction), ephemeral=True)

    @discord.ui.button(label="Activer/Désactiver une alarme", style=discord.ButtonStyle.gray)
    async def toggle_alarm(self, interaction: discord.Interaction, item):
        alarms = Cf.get_alarms(interaction.user.id, interaction.guild.id)
        if alarms == {}:
            await interaction.response.send_message(
                "Vous n'avez pas d'alarme à supprimer, créez-en une avec le `/alarm` !", ephemeral=True)
            return
        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.blue(), description="Veuillez choisir une alarme à activer/désactiver"), view=ToggleAlarm(interaction), ephemeral=True)

class EditAlarmSelect(discord.ui.Select):
    def __init__(self, interaction: discord.Interaction):
        options = [discord.SelectOption(label=alarm["name"], value=id) for id, alarm in Cf.get_alarms(interaction.user.id, interaction.guild.id).items()]
        super().__init__(
            placeholder="Choisis une alarme à modifier",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(AlarmEdition(interaction, int(self.values[0])))

class EditAlarm(discord.ui.View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.add_item(EditAlarmSelect(interaction))

class RemoveAlarmSelect(discord.ui.Select):
    def __init__(self, interaction: discord.Interaction):
        options = [discord.SelectOption(label=alarm["name"], value=id) for id, alarm in Cf.get_alarms(interaction.user.id, interaction.guild.id).items()]
        super().__init__(
            placeholder="Choisis une alarme à supprimer",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        alarms = Cf.get_alarms(interaction.user.id, interaction.guild.id)
        name = alarms[self.values[0]]["name"]
        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description=f"Voulez-vous vraiment supprimer l'alarme **{name}** ?"), view=RemoveAlarmConfirm(self.values[0]), ephemeral=True)

class RemoveAlarm(discord.ui.View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.add_item(RemoveAlarmSelect(interaction))

class RemoveAlarmConfirm(discord.ui.View):
    def __init__(self, alarm_id):
        super().__init__()
        self.alarm_id = alarm_id

    @discord.ui.button(label="Supprimer l'alarme", style=discord.ButtonStyle.red)
    async def delete_alarm(self, interaction: discord.Interaction, item):
        alarms = Cf.get_alarms(interaction.user.id, interaction.guild.id)
        name = alarms[self.alarm_id]["name"]
        del alarms[self.alarm_id]
        Cf.set_alarms(interaction.user.id, interaction.guild.id, alarms)
        await interaction.response.send_message(f"L'alarme **{name}** a bien été supprimée.", ephemeral=True)

class ToggleAlarmSelect(discord.ui.Select):
    def __init__(self, interaction: discord.Interaction):
        options = [discord.SelectOption(label=alarm["name"], value=id) for id, alarm in Cf.get_alarms(interaction.user.id, interaction.guild.id).items()]
        super().__init__(
            placeholder="Choisis une alarme à activer/désactiver",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        alarms = Cf.get_alarms(interaction.user.id, interaction.guild.id)
        alarms[self.values[0]]["enabled"] = not alarms[self.values[0]]["enabled"]
        Cf.set_alarms(interaction.user.id, interaction.guild.id, alarms)
        await interaction.response.send_message(f"L'alarme **{alarms[self.values[0]]["name"]}** a bien été {"activée" if alarms[self.values[0]]["enabled"] else "désactivée"}.", ephemeral=True)

class ToggleAlarm(discord.ui.View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.add_item(ToggleAlarmSelect(interaction))

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

    @guild_only
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

        for alarm in alarms:
            name = alarms[alarm]["name"]
            time = alarms[alarm]["time"]
            days = alarms[alarm]["days"]
            days_str = ""
            for day in days:
                day_str = self.days_trad[day]
                days_str += day_str + ", "
            days_str = days_str.removesuffix(", ")
            one_shot = alarms[alarm]["one_shot"]
            enabled = alarms[alarm]["enabled"]
            embed.add_field(name=name, value=f"""
            > Sonne à {time}
            {f"> Se répête {days_str}\n" if not one_shot else ""}{"> Sonne qu'une seule fois\n" if one_shot else ""}{"> Activé" if enabled else "> Désactivé"}

            """)
        await ctx.send(embed=embed, view=AlarmPanel(), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Alarm(bot))