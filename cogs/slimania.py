import discord
from discord.ext import commands
from discord import app_commands
import bot_package.custom_func as Cf
from bot_package.data import image_url
from datetime import datetime, timedelta, UTC
import random

class InventoryView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(InventorySelect())

class InventorySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="F",
                value="F",
            ),
            discord.SelectOption(
                label="E",
                value="E",
            ),
            discord.SelectOption(
                label="D",
                value="D",
            ),
            discord.SelectOption(
                label="C",
                value="C",
            ),
            discord.SelectOption(
                label="B",
                value="B",
            ),
            discord.SelectOption(
                label="A",
                value="A",
            ),
            discord.SelectOption(
                label="S",
                value="S",
            ),
            discord.SelectOption(
                label="Z",
                value="Z",
            ),
            discord.SelectOption(
                label="UZ",
                value="UZ",
            ),
        ]
        super().__init__(
            placeholder="Choisissez un rang à afficher",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        rank = self.values[0]

        inv = Cf.get_slimania_inventory(interaction.user.id, interaction.guild.id)
        slime_list = Cf.get_slime_list()
        slimes = {}
        for slime in inv["inventory"]:
            slime_rank = slime_list[slime]["rank"]
            if slime_rank == rank:
                slimes[slime] = inv["inventory"][slime]

        slime_names = {}
        for slime in slimes:
            name = slime_list[slime]["name"]
            slime_names[slime] = name

        string = ""
        for slime in slimes:
            string += f"**{slime_names[slime]}** : **{slimes[slime]}**\n"
        embed = discord.Embed(
            color=discord.Color.green(),
            title=f"Inventaire Slimania de {interaction.user.name}",
            description=
            f"""
            Voici vos slimes de rang {rank} :
            {string}
"""
        )
        await interaction.response.send_message(embed=embed, view=InventoryView())


class Slimania(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="slimania_roll")
    async def slimania_roll(self, ctx: commands.Context):
        """
        Permet de gagner un slime aléatoire (disponible toutes les heures)
        :param ctx: Context
        :return:
        """
        inv = Cf.get_slimania_inventory(ctx.author.id, ctx.guild.id)
        last_roll = inv["last_roll"]
        if last_roll != 0:
            last_roll = datetime.fromisoformat(last_roll)
        if last_roll == 0:
            last_roll = datetime.now(UTC) - timedelta(hours=1)
        if datetime.now(UTC) - last_roll < timedelta(hours=1) and not str(ctx.author.id) in Cf.read_file("files/slimania_no_cooldown.txt"):
            minutes = ((last_roll + timedelta(hours=1)) - datetime.now(UTC)).seconds // 60
            embed = discord.Embed(color=discord.Color.red(), title="Vous ne pouvez pas tirer de slime :/", description=f"Vous pourrez réutiliser la commande dans {minutes} minutes.")
            await ctx.send(embed=embed)
            return

        ranks = ["F", "E", "D", "C", "B", "A", "S", "Z", "UZ"]
        weights = [50, 80, 50, 30, 20, 5, 2, 1, 0.25]
        rank = random.choices(ranks, weights)[0]

        slime_choices = Cf.get_slime_per_rank()[rank]
        slime = random.choice(slime_choices)

        if slime in inv["inventory"]:
            inv["inventory"][slime] += 1
            new = False
        else:
            inv["inventory"][slime] = 1
            new = True

        inv["last_roll"] = datetime.isoformat(datetime.now(UTC))
        Cf.set_slimania_inventory(ctx.author.id, ctx.guild.id, inv)

        name = Cf.get_slime_list()[slime]["name"]

        embed = discord.Embed(color=discord.Color.green() if rank in ["F", "E", "D", "C", "B", "A"] else discord.Color.gold() if rank in ["S", "Z"] else discord.Color.purple(), title="Slimania Roll", description=
        f"""
        Vous avez obtenu {name} ! Il est de rang {rank}.
        {"✨ Nouveau ! Vous ne l'aviez pas avant" if new else f"Vous l'avez déjà eu, maintenant vous en avez {inv["inventory"][slime]}."}
        Faîtes /slimania_inventory pour le voir !
""")
        embed.set_image(url=image_url + slime + ".png")

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="slimania_booster")
    async def slimania_booster(self, ctx: commands.Context):
        """
        Achète un booster pour la somme de 1000₣. Disponible toutes les heures
        :param ctx:
        :return:
        """
        inv = Cf.get_slimania_inventory(ctx.author.id, ctx.guild.id)
        last_roll = inv["last_roll"]
        if last_roll != 0:
            last_roll = datetime.fromisoformat(last_roll)
        if last_roll == 0:
            last_roll = datetime.now(UTC) - timedelta(hours=1)
        if datetime.now(UTC) - last_roll < timedelta(hours=1) and not str(ctx.author.id) in Cf.read_file(
                "files/slimania_no_cooldown.txt"):
            minutes = ((last_roll + timedelta(hours=1)) - datetime.now(UTC)).seconds // 60
            embed = discord.Embed(color=discord.Color.red(), title="Vous ne pouvez pas acheter de booster :/",
                                  description=f"Vous pourrez réutiliser la commande dans {minutes} minutes.")
            await ctx.send(embed=embed)
            return

        user_data = Cf.get_user_data(ctx.author.id, ctx.guild.id)
        if user_data["money"] < 1000:
            embed = discord.Embed(color=discord.Color.red(), title="Vous ne pouvez pas acheter de booster :/",
                                  description=f"Vous n'avez pas assez d'argent pour acheter un booster")
            await ctx.send(embed=embed)
            return

        for i in range(6):
            ranks = ["F", "E", "D", "C", "B", "A", "S", "Z", "UZ"]
            weights = [30, 80, 50, 30, 20, 5, 2, 1, 0.25] if i != 5 else [0.25, 0, 0, 0, 0, 5, 2, 1, 0.25]
            rank = random.choices(ranks, weights)[0]

            slime_choices = Cf.get_slime_per_rank()[rank]
            slime = random.choice(slime_choices)

            if slime in inv["inventory"]:
                inv["inventory"][slime] += 1
                new = False
            else:
                inv["inventory"][slime] = 1
                new = True



            name = Cf.get_slime_list()[slime]["name"]

            embed = discord.Embed(color=discord.Color.green() if rank in ["F", "E", "D", "C", "B",
                                                                          "A"] else discord.Color.gold() if rank in [
                "S", "Z"] else discord.Color.purple(), title=f"Slimania Booster : carte {i + 1} sur 6", description=
                                  f"""
                    Vous avez obtenu {name} ! Il est de rang {rank}.
                    {"✨ Nouveau ! Vous ne l'aviez pas avant" if new else f"Vous l'avez déjà eu, maintenant vous en avez {inv["inventory"][slime]}."}
                    Faîtes /slimania_inventory pour le voir !
            """)
            embed.set_image(url=image_url + slime + ".png")

            await ctx.send(embed=embed)

        user_data["money"] -= 1000
        Cf.set_user_data(ctx.author.id, ctx.guild.id, user_data)
        inv["last_roll"] = datetime.isoformat(datetime.now(UTC))
        Cf.set_slimania_inventory(ctx.author.id, ctx.guild.id, inv)

    @commands.hybrid_command(name="slimania_inventory")
    async def slimania_inventory(self, ctx: commands.Context, user: discord.User = None):
        """
        Permet de voir l'inventaire slimania d'un utilisateur
        :param ctx:
        :param user: Utilisateur
        :return:
        """
        if user == None:
            user = ctx.author

        inv = Cf.get_slimania_inventory(user.id, ctx.guild.id)
        slime_list = Cf.get_slime_list()
        amount_per_rank = {
            "F": 0,
            "E": 0,
            "D": 0,
            "C": 0,
            "B": 0,
            "A": 0,
            "S": 0,
            "Z": 0,
            "UZ": 0,
        }
        for slime in inv["inventory"]:
            rank = slime_list[slime]["rank"]
            if not rank in amount_per_rank.keys():
                continue
            amount_per_rank[rank] += 1

        slime_per_rank = Cf.get_slime_per_rank()
        amount_max_per_rank = {
            "F": len(slime_per_rank["F"]),
            "E": len(slime_per_rank["E"]),
            "D": len(slime_per_rank["D"]),
            "C": len(slime_per_rank["C"]),
            "B": len(slime_per_rank["B"]),
            "A": len(slime_per_rank["A"]),
            "S": len(slime_per_rank["S"]),
            "Z": len(slime_per_rank["Z"]),
            "UZ": len(slime_per_rank["UZ"]),
        }

        amount = len(inv["inventory"])
        amount_max = len(slime_list)

        embed = discord.Embed(color=discord.Color.blue(), title=f"Inventaire Slimania de {user.display_name}", description=
        f"""
        Vous avez {amount}/{amount_max} slimes.
        
        Répartition des rangs :
        F : {amount_per_rank["F"]}/{amount_max_per_rank["F"]}
        E : {amount_per_rank["E"]}/{amount_max_per_rank["E"]}
        D : {amount_per_rank["D"]}/{amount_max_per_rank["D"]}
        C : {amount_per_rank["C"]}/{amount_max_per_rank["C"]}
        B : {amount_per_rank["B"]}/{amount_max_per_rank["B"]}
        A : {amount_per_rank["A"]}/{amount_max_per_rank["A"]}
        S : {amount_per_rank["S"]}/{amount_max_per_rank["S"]}
        Z : {amount_per_rank["Z"]}/{amount_max_per_rank["Z"]}
        UZ : {amount_per_rank["UZ"]}/{amount_max_per_rank["UZ"]}
        
        Sélectionnez le rang que vous voulez afficher.
""")
        await ctx.send(embed=embed, view=InventoryView())

    async def rank_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name="F", value="F"),
            app_commands.Choice(name="E", value="E"),
            app_commands.Choice(name="D", value="D"),
            app_commands.Choice(name="C", value="C"),
            app_commands.Choice(name="B", value="B"),
            app_commands.Choice(name="A", value="A"),
            app_commands.Choice(name="S", value="S"),
            app_commands.Choice(name="Z", value="Z"),
            app_commands.Choice(name="UZ", value="UZ"),
        ]

    @commands.hybrid_command(name="slimania_add")
    @app_commands.autocomplete(rank=rank_autocomplete)
    @commands.is_owner()
    async def slimania_add(self, ctx: commands.Context, name: str, rank: str):
        """
        OWNER SEULEMENT - Ajoute un nouveau slime à slimania
        :param ctx: Context
        :param name: Nom du slime
        :param rank: Rang du slime
        :return:
        """
        slime_list = Cf.get_slime_list()
        last_id = 0
        for slime in slime_list:
            if int(slime) > last_id:
                last_id = int(slime)
        next_id = str(last_id+1)
        slime_list[next_id] = {
            "name": name,
            "rank": rank
        }
        Cf.write_json(slime_list, "files/slime_list.json")
        slime_per_rank = {
            "F": [],
            "E": [],
            "D": [],
            "C": [],
            "B": [],
            "A": [],
            "S": [],
            "Z": [],
            "UZ": [],
        }
        for slime in slime_list:
            rank = slime_list[slime]["rank"]
            if not rank in slime_per_rank.keys():
                continue
            slime_per_rank[rank].append(slime)
        Cf.write_json(slime_per_rank, "files/slime_per_rank.json")

        embed = discord.Embed(
            color=discord.Color.blue(),
            title=name,
            description=f"Vous avez bien ajouté {name} de rang {rank} (ID : {next_id})",
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="slimania_search")
    @app_commands.autocomplete(rank=rank_autocomplete)
    async def slimania_search(self, ctx: commands.Context, query: str=None, rank:str=None):
        """
        Permet de rechercher un slime précis ou un rang
        :param ctx:
        :param query: Nom du slime recherché
        :param rank: Rang (regroupement de slimes)
        :return:
        """
        if not (query or rank):
            await ctx.send(embed=discord.Embed(
                color=discord.Color.red(),
                description="Merci de préciser un slime ou un rang"
            ))
            return

        if query and rank:
            await ctx.send(embed=discord.Embed(
                color=discord.Color.red(),
                description="Merci de préciser soit un slime, soit un rang (pas les deux !)"
            ))
            return

        if query:
            slime_list = Cf.get_slime_list()
            slime_names = {}
            for slime in slime_list:
                name = slime_list[slime]["name"]
                slime_names[name] = slime

            if not query in slime_names:
                await ctx.send(embed=discord.Embed(
                    color=discord.Color.red(),
                    description="Désolé, mais ce slime n'existe pas"
                ))
                return

            slime = slime_names[query]

            embed = discord.Embed(
                color=discord.Color.blue(),
                title=query,
                description=
                f"Le slime {query} est de rang {slime_list[slime]["rank"]}."
            )
            embed.set_image(url=image_url + slime + ".png")
            await ctx.send(embed=embed)

        elif rank:
            slime_list = Cf.get_slime_list()
            slime_per_rank = Cf.get_slime_per_rank()
            rank_slimes = []
            for slime in slime_per_rank[rank]:
                rank_slimes.append(slime)
            slimes_str = ""
            for slime in rank_slimes:
                slimes_str += slime_list[slime]["name"] + "\n"

            embed = discord.Embed(
                color=discord.Color.blue(),
                title=f"Slimes de rang {rank} :",
                description=slimes_str
            )
            await ctx.send(embed=embed)

async def setup(bot):
    slime_list = Cf.get_slime_list()
    slime_per_rank = {
        "F": [],
        "E": [],
        "D": [],
        "C": [],
        "B": [],
        "A": [],
        "S": [],
        "Z": [],
        "UZ": [],
    }
    for slime in slime_list:
        rank = slime_list[slime]["rank"]
        if not rank in slime_per_rank.keys():
            continue
        slime_per_rank[rank].append(slime)
    Cf.write_json(slime_per_rank, "files/slime_per_rank.json")

    await bot.add_cog(Slimania(bot))