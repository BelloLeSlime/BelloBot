import discord
from discord.ext import commands
from discord import app_commands
import bot_package.custom_func as Cf
import random
from bot_package.data import flamcoin_symbol, gambling_quotes

class ReplayButton(discord.ui.View):
    def __init__(self, game_function, ctx, bet, what, arg=None, no_loss=False):
        super().__init__()
        self.game_function = game_function
        self.ctx = ctx
        self.bet = bet
        self.what = what
        self.arg = arg
        self.no_loss = no_loss

    @discord.ui.button(label="Rejouer", style=discord.ButtonStyle.green)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.no_loss:
            user_data = Cf.get_user_data(interaction.user.id, interaction.guild_id)
            if user_data[self.what] < self.bet:
                await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(),
                                                   description=f"Désolé, mais vous n'avez pas assez d'{"XP" if self.what == "xp" else "argent"} !"))
                return
            user_data[self.what] -= self.bet
            Cf.set_user_data(interaction.user.id, interaction.guild.id, user_data)
        await interaction.response.defer()
        if self.arg:
            await self.game_function(self.ctx, self.bet, self.what, self.arg)
        else:
            await self.game_function(self.ctx, self.bet, self.what)

class MultChoice(discord.ui.View):
    def __init__(self, callback, ctx, bet, what):
        super().__init__()
        self.callback = callback
        self.ctx = ctx
        self.bet = bet
        self.what = what

    @discord.ui.button(label="X2", style=discord.ButtonStyle.green)
    async def button_2_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.callback(self.ctx, self.bet, self.what, choice=2)
        await interaction.response.defer()

    @discord.ui.button(label="X3", style=discord.ButtonStyle.primary)
    async def button_3_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.callback(self.ctx, self.bet, self.what, choice=3)
        await interaction.response.defer()

    @discord.ui.button(label="X5", style=discord.ButtonStyle.red)
    async def button_5_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.callback(self.ctx, self.bet, self.what, choice=5)
        await interaction.response.defer()

    @discord.ui.button(label="X10", style=discord.ButtonStyle.grey)
    async def button_10_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.callback(self.ctx, self.bet, self.what, choice=10)
        await interaction.response.defer()

class DuckChoice(discord.ui.View):
    def __init__(self, callback, ctx, bet, what):
        super().__init__()
        self.callback = callback
        self.ctx = ctx
        self.bet = bet
        self.what = what

    @discord.ui.button(label="Donald", style=discord.ButtonStyle.green)
    async def donald_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.callback(self.ctx, self.bet, self.what, choice="Donald")
        await interaction.response.defer()

    @discord.ui.button(label="Daffy", style=discord.ButtonStyle.green)
    async def daffy_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.callback(self.ctx, self.bet, self.what, choice="Daffy")
        await interaction.response.defer()

    @discord.ui.button(label="Yarl", style=discord.ButtonStyle.green)
    async def yarl_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.callback(self.ctx, self.bet, self.what, choice="Yarl")
        await interaction.response.defer()

    @discord.ui.button(label="Picsou", style=discord.ButtonStyle.green)
    async def picsou_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.callback(self.ctx, self.bet, self.what, choice="Picsou")
        await interaction.response.defer()

class BlackjackChoice(discord.ui.View):
    def __init__(self, callback, ctx, bet, what, game_info):
        super().__init__()
        self.callback = callback
        self.ctx = ctx
        self.bet = bet
        self.what = what
        self.game_info = game_info

    @discord.ui.button(label="Tirer", style=discord.ButtonStyle.green)
    async def draw_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.game_info["choice"] = "draw"
        await self.callback(self.ctx, self.bet, self.what, self.game_info)
        await interaction.response.defer()

    @discord.ui.button(label="Rester", style=discord.ButtonStyle.blurple)
    async def stand_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.game_info["choice"] = "stand"
        await self.callback(self.ctx, self.bet, self.what, self.game_info)
        await interaction.response.defer()

    @discord.ui.button(label="Doubler", style=discord.ButtonStyle.red)
    async def double_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.game_info["choice"] = "double"
        await self.callback(self.ctx, self.bet, self.what, self.game_info)
        await interaction.response.defer()

class StreetCrapsRoll(discord.ui.View):
    def __init__(self, callback, ctx, bet, what, game_info):
        super().__init__()
        self.callback = callback
        self.ctx = ctx
        self.bet = bet
        self.what = what
        self.game_info = game_info

    @discord.ui.button(label="Lancer", style=discord.ButtonStyle.blurple)
    async def roll_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.callback(self.ctx, self.bet, self.what, self.game_info)
        await interaction.response.defer()

class RouletteChoice(discord.ui.View):
    def __init__(self, callback, ctx, bet, what):
        super().__init__()
        self.callback = callback
        self.ctx = ctx
        self.bet = bet
        self.what = what

    @discord.ui.button(label="Rouge", style=discord.ButtonStyle.red)
    async def red_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.callback(self.ctx, self.bet, self.what, "red")
        await interaction.response.defer()

    @discord.ui.button(label="Noir", style=discord.ButtonStyle.grey)
    async def black_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.callback(self.ctx, self.bet, self.what, "black")
        await interaction.response.defer()

    @discord.ui.button(label="Vert", style=discord.ButtonStyle.green)
    async def green_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.callback(self.ctx, self.bet, self.what, "green")
        await interaction.response.defer()

class PeguinCrossChoice(discord.ui.View):
    def __init__(self, callback, ctx, bet, what, turn):
        super().__init__()
        self.callback = callback
        self.ctx = ctx
        self.bet = bet
        self.what = what
        self.turn = turn

    @discord.ui.button(label="Avancer", style=discord.ButtonStyle.green)
    async def step_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.callback(self.ctx, self.bet, self.what, "step", self.turn)
        await interaction.response.defer()

    @discord.ui.button(label="Cash-Out", style=discord.ButtonStyle.blurple)
    async def cashout_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.callback(self.ctx, self.bet, self.what, "cashout", self.turn)
        await interaction.response.defer()

class DragonTowerChoice(discord.ui.View):
    def __init__(self, callback, ctx, bet, what, game_info):
        super().__init__()
        self.callback = callback
        self.ctx = ctx
        self.bet = bet
        self.what = what
        self.game_info = game_info

    @discord.ui.button(label="1", style=discord.ButtonStyle.green)
    async def one_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.callback(self.ctx, self.bet, self.what, self.game_info, "1")
        await interaction.response.defer()

    @discord.ui.button(label="2", style=discord.ButtonStyle.green)
    async def two_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.callback(self.ctx, self.bet, self.what, self.game_info, "2")
        await interaction.response.defer()

    @discord.ui.button(label="3", style=discord.ButtonStyle.green)
    async def three_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.callback(self.ctx, self.bet, self.what, self.game_info, "3")
        await interaction.response.defer()

    @discord.ui.button(label="4", style=discord.ButtonStyle.green)
    async def four_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.callback(self.ctx, self.bet, self.what, self.game_info, "4")
        await interaction.response.defer()

    @discord.ui.button(label="Cash-Out", style=discord.ButtonStyle.blurple)
    async def cashout_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.callback(self.ctx, self.bet, self.what, self.game_info, "cashout")
        await interaction.response.defer()

class Gamebling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def gambling_game_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name="wheel of fortune", value="wheel of fortune"),
            app_commands.Choice(name="money wheel", value="money wheel"),
            app_commands.Choice(name="slots", value="slots"),
            app_commands.Choice(name="duck race", value="duck race"),
            app_commands.Choice(name="blackjack", value="blackjack"),
            app_commands.Choice(name="street craps", value="street craps"),
            app_commands.Choice(name="roulette", value="roulette"),
            app_commands.Choice(name="peguin cross", value="peguin cross"),
            app_commands.Choice(name="dragon tower", value="dragon tower"),
        ]

    async def gambling_what_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name="xp", value="xp"),
            app_commands.Choice(name="money", value="money"),
        ]

    @commands.hybrid_command(name="gambling")
    @app_commands.autocomplete(game=gambling_game_autocomplete, what=gambling_what_autocomplete)
    async def gambling(self, ctx: commands.Context, game: str, bet: int, what: str):
        """
        Permet de parier de l'xp ou de l'argent et de jouer à un jeu et en gagner plus
        :param ctx: Context
        :param game: Jeu (il y en a 9 !)
        :param bet: Mise (10XP et 10 flamcoins minimum !)
        :param what: Miser sur l'XP ou l'argent
        :return:
        """
        if bet < 10:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(), description=f"Désolé, la mise minimum est de 10{"XP" if what == "xp" else flamcoin_symbol} !"))
            return
        user_data = Cf.get_user_data(ctx.author.id, ctx.guild.id)
        if user_data[what] < bet:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(), description=f"Désolé, mais vous n'avez pas assez d'{"XP" if what == "xp" else "argent"} !"))
            return
        user_data[what] -= bet
        Cf.set_user_data(ctx.author.id, ctx.guild.id, user_data)
        if game == "wheel of fortune":
            await self.wheel_of_fortune(ctx, bet, what)
        elif game == "money wheel":
            await self.money_wheel(ctx, bet, what)
        elif game == "slots":
            await self.slots(ctx, bet, what)
        elif game == "duck race":
            await self.duck_race(ctx, bet, what)
        elif game == "blackjack":
            await self.blackjack(ctx, bet, what)
        elif game == "street craps":
            await self.street_craps(ctx, bet, what)
        elif game == "roulette":
            await self.roulette(ctx, bet, what)
        elif game == "peguin cross":
            await self.peguin_cross(ctx, bet, what)
        elif game == "dragon tower":
            await self.dragon_tower(ctx, bet, what)

    async def wheel_of_fortune(self, ctx, bet, what):
        choices = [-1, 3, 0.1, 0.5, 0.25, 5, 0.1, 0.25, 2, 0.1, -1, 3, 0.5, 0.1, 0.25, 0, 0.5, 0.1, 2, 0.25]
        mult = random.choice(choices)
        if mult==-1:
            embed = discord.Embed(color=discord.Color.blue(),
                                  title=f"WHEEL OF FORTUNE - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}", description=
                                  f"""
                        Vous êtes tombé sur...

                        Un tour en plus gratuit !
                        
                        Retente ta chance gratuitement dès maintenant !
            """)
            await ctx.send(embed=embed, view=ReplayButton(self.wheel_of_fortune, ctx, bet, what, no_loss=True))

        else:
            win = int(bet*mult)
            user_data = Cf.get_user_data(ctx.author.id, ctx.guild.id)
            user_data[what] += win
            Cf.set_user_data(ctx.author.id, ctx.guild.id, user_data)
            embed = discord.Embed(color=discord.Color.red() if mult < 1 else discord.Color.green(), title=f"WHEEL OF FORTUNE - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}", description=
            f"""
            Vous êtes tombé sur...
            
            X{mult}{"..." if mult < 1 else " !"}
            
            {"Dommage... Vous pouvez toujours tenter votre chance, il ne faut pas s'arrêter sur une défaite." if mult < 1 else "Bien joué ! Vous pouvez rejouer, pour votre streak de victoires !"}
            Vous remportez {win}{"XP" if what == "xp" else flamcoin_symbol} sur les {bet} que vous avez misé"
""")
            await ctx.send(embed=embed, view=ReplayButton(self.wheel_of_fortune, ctx, bet, what))

    async def money_wheel(self, ctx, bet, what, choice=0):
        if choice == 0:
            embed = discord.Embed(color=discord.Color.blue(), title=f"MONEY WHEEL - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}", description=f"""
            Veuillez choisir le gain possible
            
            Les probabilités sont les suivantes :
            > X2 : 14/37
            > X3 : 10/37
            > X5 : 8/37
            > X10 : 5/37
""")
            await ctx.send(embed=embed, view=MultChoice(self.money_wheel, ctx, bet, what))
        else:
            choices = [2, 3, 5, 10]
            weights = [14, 10, 8, 5]
            dropped = random.choices(choices, weights=weights)[0]
            if dropped == choice:
                win = int(bet*dropped)
            else:
                win = 0
            user_data = Cf.get_user_data(ctx.author.id, ctx.guild.id)
            user_data[what] += win
            Cf.set_user_data(ctx.author.id, ctx.guild.id, user_data)
            embed = discord.Embed(color=discord.Color.green() if win else discord.Color.red(), title=f"MONEY WHEEL - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}", description=
            f"""
            Vous choisissez X{choice} et vous tombez sur...
            
            X{dropped}{" !" if win else "..."}
            
            {f"Dommage, vous ne gagnez rien. Vous pouvez toujours retenter pour X{choice}..." if not win else f"Bien joué ! Vous multipliez votre mise par {choice} ! Vous remportez {win}{"XP" if what == "xp" else flamcoin_symbol} sur les {bet} que vous avez parié."}
""")
            await ctx.send(embed=embed, view=ReplayButton(self.money_wheel, ctx, bet, what, arg=choice))

    async def slots(self, ctx, bet, what):
        choices = ["🍎", "🍊", "🍋", "🍉"]

        dropped = []
        for _i in range(3):
            line = []
            for _j in range(3):
                line.append(random.choice(choices))
            dropped.append(line)

        mult = 0
        values = {
            "🍎": 0.5,
            "🍊": 1.5,
            "🍋": 2.5,
            "🍉": 3.5
        }
        lines = []

        lines.extend(dropped)
        for col in range(3):
            lines.append([
                dropped[0][col],
                dropped[1][col],
                dropped[2][col]
            ])
        lines.append([
            dropped[0][0],
            dropped[1][1],
            dropped[2][2]
        ])
        lines.append([
            dropped[0][2],
            dropped[1][1],
            dropped[2][0]
        ])

        for line in lines:
            if line[0] == line[1] == line[2]:
                mult += values[line[0]]

        dropped_str = ""
        for i in dropped:
            for j in i:
                dropped_str += j
            dropped_str += "\n"

        win = int(bet * mult)
        user_data = Cf.get_user_data(ctx.author.id, ctx.guild.id)
        user_data[what] += win
        Cf.set_user_data(ctx.author.id, ctx.guild.id, user_data)

        embed = discord.Embed(color=discord.Color.green() if mult else discord.Color.red(), title=f"SLOTS - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}", description=
        f"""
        {dropped_str}
        Vous multipliez votre mise par...
        
        {mult}{" !" if mult else "..."}
        
        {"Bien joué ! Vous pouvez rejouer pour gagner encore plus !" if mult else "Dommage... Vous pouvez toujours retenter !"}
        Vous remportez {win}{"XP" if what == "xp" else flamcoin_symbol} sur les {bet} que vous avez parié{" !" if win else "..."}
""")
        await ctx.send(embed=embed, view=ReplayButton(self.slots, ctx, bet, what))

    async def duck_race(self, ctx, bet, what, choice=""):
        if choice == "":
            embed = discord.Embed(color=discord.Color.blue(), title=f"DUCK RACE - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}", description=
            f"""
            Veuillez choisir votre canard favori
            
            🍔🍟🌭🪙
            
            
            🏁🏁🏁🏁
            
            
            
            
            🧢👒🎓🎩
            🦆🦆🦆🦆
            
            > Conseil de pro : choisissez Yarl, toujours Yarl
""")
            await ctx.send(embed=embed, view=DuckChoice(self.duck_race, ctx, bet, what))
        else:
            names = ["Donald", "Daffy", "Yarl", "Picsou"]
            weights = [1, 1, 1.1, 1]
            winner = random.choices(names, weights=weights)[0]
            if winner == choice:
                win = 4 * bet
            else:
                win = 0
            embed = discord.Embed(color=discord.Color.green() if win else discord.Color.red(), title=f"DUCK RACE - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}", description=
            f"""
            {"""🍔🍟🌭🪙
            🧢
            🦆
            🏁🏁🏁🏁
            ⚫👒🎓🎩
            ⚫🦆🦆🦆
            
            
                     
                     """ if winner == "Donald" else 
            """🍔🍟🌭🪙
            ⚫👒
            ⚫🦆
            🏁🏁🏁🏁
            🧢⚫🎓🎩
            🦆⚫🦆🦆
            
            
                     
                     """ if winner == "Daffy" else 
            """🍔🍟🌭🪙
            ⚫⚫🎓
            ⚫⚫🦆
            🏁🏁🏁🏁
            🧢👒⚫🎩
            🦆🦆⚫🦆
            
            
                     
                     """ if winner == "Yarl" else 
            """🍔🍟🌭🪙
            ⚫⚫⚫🎩
            ⚫⚫⚫🦆
            🏁🏁🏁🏁
            🧢👒🎓
            🦆🦆🦆
            
            
                     
                     """}
        {winner} a gagné{" !" if win else "..."}
        {f"Bien joué ! Vous pouvez retenter votre chance sur {winner}, il vient juste de faire ses preuves !" if win else f"Dommage... {"J'avais dit de parier sur Yarl ! " if winner == "Yarl" else ""}Vous pouvez toujours retenter votre chance sur {choice} !"}
        Vous remportez {win}{"XP" if what == "xp" else flamcoin_symbol} sur les {bet} que vous avez parié{" !" if win else "..."}
            
""")
            await ctx.send(embed=embed, view=ReplayButton(self.duck_race, ctx, bet, what, arg=choice))

    def get_random_card(self, already_dropped) -> str:
        cards_value = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        cards_types = ["♠️", "♦️", "♣️", "♥️"]
        random_card = random.choice(cards_value) + random.choice(cards_types)
        while random_card in already_dropped:
            random_card = random.choice(cards_value) + random.choice(cards_types)
        return random_card.strip()

    def get_already_dropped(self, game_info):
        return game_info["user_cards"] + game_info["gm_cards"]

    async def blackjack(self, ctx, bet, what, game_info=None):
        card_values = {
            "A": 11,
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
            "9": 9,
            "10": 10,
            "J": 10,
            "Q": 10,
            "K": 10,
        }

        if not game_info:
            game_info = {
                "user_cards": [],
                "user_points": 0,
                "gm_cards": [],
                "gm_points": 0,
                "choice": None
            }
            game_info["user_cards"].append(self.get_random_card(self.get_already_dropped(game_info)))
            game_info["gm_cards"].append(self.get_random_card(self.get_already_dropped(game_info)))
            game_info["user_cards"].append(self.get_random_card(self.get_already_dropped(game_info)))

            for card in game_info["user_cards"]:
                game_info["user_points"] += card_values[card[:-2]] if card[:-2] != "A" else 11 if game_info["user_points"] + 11 <= 21 else 1
            game_info["gm_points"] += card_values[game_info["gm_cards"][0][:-2]]

            if game_info["user_points"] == 21:
                user_cards_str = ""
                for card in game_info["user_cards"]:
                    user_cards_str += card + " "
                gm_cards_str = ""
                for card in game_info["gm_cards"]:
                    gm_cards_str += card + " "
                embed = discord.Embed(color=discord.Color.green(), title=f"BLACKJACK - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}", description=
                f"""
                BLACKJACK !
                
                Votre main : {game_info["user_points"]}
                {user_cards_str}
                
                La main du croupier (BelloBot en costar cravate) : {game_info["gm_points"]}
                {gm_cards_str}
                
                Vous triplez votre mise de {bet}{"XP" if what == "xp" else flamcoin_symbol}"
                
""")
                await ctx.send(embed=embed, view=ReplayButton(self.blackjack, ctx, bet, what))
                return


        if game_info["choice"] == "draw":
            game_info["user_cards"].append(self.get_random_card(self.get_already_dropped(game_info)))
            game_info["user_points"] += card_values[game_info["user_cards"][-1][:-2]] if game_info["user_cards"][-1][:-2] != "A" else card_values[game_info["user_cards"][-1][:-2]] if game_info["user_points"] + 11 <= 21 else 1
            bust = game_info["user_points"] > 21
            user_cards_str = ""
            for card in game_info["user_cards"]:
                user_cards_str += card + " "
            gm_cards_str = ""
            for card in game_info["gm_cards"]:
                gm_cards_str += card + " "
            embed = discord.Embed(color=discord.Color.blue() if not bust else discord.Color.red(), title=f"BLACKJACK - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}", description=
            f"""
            {f"""Votre main : {game_info["user_points"]}
            {user_cards_str}
            
            La main du croupier (BelloBot en costar cravate) : {game_info["gm_points"]}
            {gm_cards_str}""" if not bust else 
            f"""
            BUST !
            
            Votre main : {game_info["user_points"]}
            {user_cards_str}
            
            La main du croupier (BelloBot en costar cravate) : {game_info["gm_points"]}
            {gm_cards_str}
            
            Vous perdez votre mise de {bet}{"XP" if what == "xp" else flamcoin_symbol}... Vous pouvez retenter votre chance !"""}
""")
            if not bust:
                await ctx.send(embed=embed, view=BlackjackChoice(self.blackjack, ctx, bet, what, game_info=game_info))
            else:
                await ctx.send(embed=embed, view=ReplayButton(self.blackjack, ctx, bet, what))

        elif game_info["choice"] == "stand":
            while game_info["gm_points"] < 17:
                game_info["gm_cards"].append(self.get_random_card(self.get_already_dropped(game_info)))
                game_info["gm_points"] += card_values[game_info["gm_cards"][-1][:-2]] if game_info["gm_cards"][-1][:-2] != "A" else card_values[game_info["gm_cards"][-1][:-2]] if game_info["gm_points"] + 11 <= 21 else 1
            user_cards_str = ""
            for card in game_info["user_cards"]:
                user_cards_str += card + " "
            gm_cards_str = ""
            for card in game_info["gm_cards"]:
                gm_cards_str += card + " "
            if game_info["gm_points"] > 21:
                user_data = Cf.get_user_data(ctx.author.id, ctx.guild.id)
                user_data[what] += int(bet * 2)
                Cf.set_user_data(ctx.author.id, ctx.guild.id, user_data)
                embed = discord.Embed(color=discord.Color.green(),
                                      title=f"BLACKJACK - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}", description=
                                      f"""
                                BUST !

                                Votre main : {game_info["user_points"]}
                                {user_cards_str}

                                La main du croupier (BelloBot en costar cravate) : {game_info["gm_points"]}
                                {gm_cards_str}

                                Vous doublez votre mise de {bet}{"XP" if what == "xp" else flamcoin_symbol} !""")
                await ctx.send(embed=embed, view=ReplayButton(self.blackjack, ctx, bet, what))

            elif game_info["user_points"] > game_info["gm_points"]:
                user_data = Cf.get_user_data(ctx.author.id, ctx.guild.id)
                user_data[what] += int(bet*2)
                Cf.set_user_data(ctx.author.id, ctx.guild.id, user_data)
                embed = discord.Embed(color=discord.Color.green(), title=f"BLACKJACK - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}", description=
                f"""
                Vous gagnez !
                
                Votre main : {game_info["user_points"]}
                {user_cards_str}
                
                La main du croupier (BelloBot en costar cravate) : {game_info["gm_points"]}
                {gm_cards_str}
                
                Vous doublez votre mise de {bet}{"XP" if what == "xp" else flamcoin_symbol} !
""")
                await ctx.send(embed=embed, view=ReplayButton(self.blackjack, ctx, bet, what))

            elif game_info["user_points"] < game_info["gm_points"]:
                embed = discord.Embed(color=discord.Color.red(),
                                      title=f"BLACKJACK - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}", description=
                                      f"""
                                Vous perdez...

                                Votre main : {game_info["user_points"]}
                                {user_cards_str}

                                La main du croupier (BelloBot en costar cravate) : {game_info["gm_points"]}
                                {gm_cards_str}

                                Vous perdez votre mise de {bet}{"XP" if what == "xp" else flamcoin_symbol}...
                """)
                await ctx.send(embed=embed, view=ReplayButton(self.blackjack, ctx, bet, what))

            elif game_info["user_points"] == game_info["gm_points"]:
                user_data = Cf.get_user_data(ctx.author.id, ctx.guild.id)
                user_data[what] += int(bet)
                Cf.set_user_data(ctx.author.id, ctx.guild.id, user_data)
                embed = discord.Embed(color=discord.Color.gold(),
                                      title=f"BLACKJACK - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}", description=
                                      f"""
                                                Égalité !

                                                Votre main : {game_info["user_points"]}
                                                {user_cards_str}

                                                La main du croupier (BelloBot en costar cravate) : {game_info["gm_points"]}
                                                {gm_cards_str}

                                                Vous vous faîtes rembourser votre mise de {bet}{"XP" if what == "xp" else flamcoin_symbol}.
                                """)
                await ctx.send(embed=embed, view=ReplayButton(self.blackjack, ctx, bet, what))

        elif game_info["choice"] == "double":
            game_info["user_cards"].append(self.get_random_card(self.get_already_dropped(game_info)))
            game_info["user_points"] += card_values[game_info["user_cards"][-1][:-2]] if game_info["user_cards"][-1][
                                                                                             :-2] != "A" else \
            card_values[game_info["user_cards"][-1][:-2]] if game_info["user_points"] + 11 <= 21 else 1
            bust = game_info["user_points"] > 21
            user_cards_str = ""
            for card in game_info["user_cards"]:
                user_cards_str += card + " "
            gm_cards_str = ""
            for card in game_info["gm_cards"]:
                gm_cards_str += card + " "
            if bust:
                embed = discord.Embed(color=discord.Color.red(), title=f"BLACKJACK - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}", description=
                f"""
                BUST !
                
                Votre main : {game_info["user_points"]}
                {user_cards_str}
                
                La main du croupier (BelloBot en costar cravate) : {game_info["gm_points"]}
                {gm_cards_str}
                
                Vous perdez votre mise de {bet}{"XP" if what == "xp" else flamcoin_symbol}... Vous pouvez retenter votre chance !
""")
                await ctx.send(embed=embed, view=ReplayButton(self.blackjack, ctx, bet, what))
            else:
                while game_info["gm_points"] < 17:
                    game_info["gm_cards"].append(self.get_random_card(self.get_already_dropped(game_info)))
                    game_info["gm_points"] += card_values[game_info["gm_cards"][-2][:-2]] if game_info["gm_cards"][-2][
                                                                                                 :-2] != "A" else \
                    card_values[game_info["gm_cards"][-2][:-2]] if game_info["gm_cards"] + 11 <= 21 else 1
                user_cards_str = ""
                for card in game_info["user_cards"]:
                    user_cards_str += card + " "
                gm_cards_str = ""
                for card in game_info["gm_cards"]:
                    gm_cards_str += card + " "
                if game_info["gm_points"] > 21:
                    user_data = Cf.get_user_data(ctx.author.id, ctx.guild.id)
                    user_data[what] += int(bet * 3)
                    Cf.set_user_data(ctx.author.id, ctx.guild.id, user_data)
                    embed = discord.Embed(color=discord.Color.green(),
                                          title=f"BLACKJACK - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}",
                                          description=
                                          f"""
                                                BUST !

                                                Votre main : {game_info["user_points"]}
                                                {user_cards_str}

                                                La main du croupier (BelloBot en costar cravate) : {game_info["gm_points"]}
                                                {gm_cards_str}

                                                Vous triplez votre mise de {bet}{"XP" if what == "xp" else flamcoin_symbol} !""")
                    await ctx.send(embed=embed, view=ReplayButton(self.blackjack, ctx, bet, what))

                elif game_info["user_points"] > game_info["gm_points"]:
                    user_data = Cf.get_user_data(ctx.author.id, ctx.guild.id)
                    user_data[what] += int(bet * 3)
                    Cf.set_user_data(ctx.author.id, ctx.guild.id, user_data)
                    embed = discord.Embed(color=discord.Color.green(),
                                          title=f"BLACKJACK - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}",
                                          description=
                                          f"""
                                Vous gagnez !

                                Votre main : {game_info["user_points"]}
                                {user_cards_str}

                                La main du croupier (BelloBot en costar cravate) : {game_info["gm_points"]}
                                {gm_cards_str}

                                Vous triplez votre mise de {bet}{"XP" if what == "xp" else flamcoin_symbol} !
                """)
                    await ctx.send(embed=embed, view=ReplayButton(self.blackjack, ctx, bet, what))

                elif game_info["user_points"] < game_info["gm_points"]:
                    embed = discord.Embed(color=discord.Color.red(),
                                          title=f"BLACKJACK - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}",
                                          description=
                                          f"""
                                                Vous perdez...

                                                Votre main : {game_info["user_points"]}
                                                {user_cards_str}

                                                La main du croupier (BelloBot en costar cravate) : {game_info["gm_points"]}
                                                {gm_cards_str}

                                                Vous perdez votre mise de {bet}{"XP" if what == "xp" else flamcoin_symbol}...
                                """)
                    await ctx.send(embed=embed, view=ReplayButton(self.blackjack, ctx, bet, what))

                elif game_info["user_points"] == game_info["gm_points"]:
                    user_data = Cf.get_user_data(ctx.author.id, ctx.guild.id)
                    user_data[what] += int(bet)
                    Cf.set_user_data(ctx.author.id, ctx.guild.id, user_data)
                    embed = discord.Embed(color=discord.Color.yellow(),
                                          title=f"BLACKJACK - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}",
                                          description=
                                          f"""
                                                                Égalité !

                                                                Votre main : {game_info["user_points"]}
                                                                {user_cards_str}

                                                                La main du croupier (BelloBot en costar cravate) : {game_info["gm_points"]}
                                                                {gm_cards_str}

                                                                Vous vous faîtes rembourser votre mise de {bet}{"XP" if what == "xp" else flamcoin_symbol}.
                                                """)
                    await ctx.send(embed=embed, view=ReplayButton(self.blackjack, ctx, bet, what))

        else:
            user_cards_str = ""
            for card in game_info["user_cards"]:
                user_cards_str += card + " "
            gm_cards_str = ""
            for card in game_info["gm_cards"]:
                gm_cards_str += card + " "
            embed = discord.Embed(color=discord.Color.blue(), title=f"BLACKJACK - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}", description=
            f"""
            Votre main : {game_info["user_points"]}
            {user_cards_str}

            La main du croupier (BelloBot en costar cravate) : {game_info["gm_points"]}
            {gm_cards_str}
""")
            await ctx.send(embed=embed, view=BlackjackChoice(self.blackjack, ctx, bet, what, game_info))

    def roll_dices(self, dices_count):
        result = []
        for i in range(dices_count):
            result.append(random.randint(1, 6))
        return result

    async def street_craps(self, ctx, bet, what, game_info=None):
        if game_info is None:
            game_info = {
                "rolls": [],
                "turn": 1
            }
            embed = discord.Embed(color=discord.Color.blue(), title=f"STREET CRAPS - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}", description=
            f"""
            Victoire (X2) : 7, 11
            Défaite (X0) : 2, 3, 12
            
            Dés : 1 1 (2)
            
            Commencez à lancer les dés !
""")
            await ctx.send(embed=embed, view=StreetCrapsRoll(self.street_craps, ctx, bet, what, game_info))

        elif game_info["turn"] == 1:
            game_info["turn"] += 1
            dices = self.roll_dices(2)
            result = sum(dices)
            game_info["rolls"].append(result)
            if result in [7, 11]:
                user_data = Cf.get_user_data(ctx.author.id, ctx.guild.id)
                user_data[what] += int(2*bet)
                Cf.set_user_data(ctx.author.id, ctx.guild.id, user_data)
                embed = discord.Embed(color=discord.Color.green(), title=f"STREET CRAPS - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}", description=
                f"""
                Vous avez gagné !
                
                Dés : {dices[0]} {dices[1]} ({result})
                
                Vous doublez votre mise de {bet}{"XP" if what == "xp" else flamcoin_symbol} !
""")
                await ctx.send(embed=embed, view=ReplayButton(self.street_craps, ctx, bet, what))
            elif result in [2, 3, 12]:
                embed = discord.Embed(color=discord.Color.red(),
                                      title=f"STREET CRAPS - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}",
                                      description=
                                      f"""
                                Vous avez predu...

                                Dés : {dices[0]} {dices[1]} ({result})

                                Vous perdez votre mise de {bet}{"XP" if what == "xp" else flamcoin_symbol}...
                                Vous pouvez toujours réessayer !
                """)
                await ctx.send(embed=embed, view=ReplayButton(self.street_craps, ctx, bet, what))
            else:
                embed = discord.Embed(color=discord.Color.blue(), title=f"STREET CRAPS - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}", description=
                f"""
                Victoire (X4) : {game_info["rolls"][0]}
                Défaite (X0) : 7
                
                Dés : {dices[0]} {dices[1]} ({result})
                
                Relancez les dés !
""")
                await ctx.send(embed=embed, view=StreetCrapsRoll(self.street_craps, ctx, bet, what, game_info))
        elif game_info["turn"] in [2, 3, 4]:
            game_info["turn"] += 1
            dices = self.roll_dices(2)
            result = sum(dices)
            game_info["rolls"].append(result)
            if result == 7:
                embed = discord.Embed(color=discord.Color.red(),
                                      title=f"STREET CRAPS - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}",
                                      description=
                                      f"""
                                                Vous avez predu...

                                                Dés : {dices[0]} {dices[1]} ({result})

                                                Vous perdez votre mise de {bet}{"XP" if what == "xp" else flamcoin_symbol}...
                                                Vous pouvez toujours réessayer !
                                """)
                await ctx.send(embed=embed, view=ReplayButton(self.street_craps, ctx, bet, what))
            elif result == game_info["rolls"][0]:
                user_data = Cf.get_user_data(ctx.author.id, ctx.guild.id)
                user_data[what] += int(4 * bet)
                Cf.set_user_data(ctx.author.id, ctx.guild.id, user_data)
                embed = discord.Embed(color=discord.Color.green(),
                                      title=f"STREET CRAPS - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}",
                                      description=
                                      f"""
                                Vous avez gagné !

                                Dés : {dices[0]} {dices[1]} ({result})

                                Vous quadruplez votre mise de {bet}{"XP" if what == "xp" else flamcoin_symbol} !
""")
                await ctx.send(embed=embed, view=ReplayButton(self.street_craps, ctx, bet, what))
            else:
                embed = discord.Embed(color=discord.Color.blue(),
                                      title=f"STREET CRAPS - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}",
                                      description=
                                      f"""
                                Victoire (X4) : {game_info["rolls"][0]}
                                Défaite (X0) : 7

                                Dés : {dices[0]} {dices[1]} ({result})

                                Relancez les dés !
                """)
                await ctx.send(embed=embed, view=StreetCrapsRoll(self.street_craps, ctx, bet, what, game_info))
        elif game_info["turn"] == 5:
            dices = self.roll_dices(2)
            result = sum(dices)
            game_info["rolls"].append(result)
            if result == 7:
                embed = discord.Embed(color=discord.Color.red(),
                                      title=f"STREET CRAPS - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}",
                                      description=
                                      f"""
                                                            Vous avez predu...

                                                            Dés : {dices[0]} {dices[1]} ({result})

                                                            Vous perdez votre mise de {bet}{"XP" if what == "xp" else flamcoin_symbol}...
                                                            Vous pouvez toujours réessayer !
                                            """)
                await ctx.send(embed=embed, view=ReplayButton(self.street_craps, ctx, bet, what))
            elif result == game_info["rolls"][0]:
                user_data = Cf.get_user_data(ctx.author.id, ctx.guild.id)
                user_data[what] += int(4 * bet)
                Cf.set_user_data(ctx.author.id, ctx.guild.id, user_data)
                embed = discord.Embed(color=discord.Color.green(),
                                      title=f"STREET CRAPS - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}",
                                      description=
                                      f"""
                                            Vous avez gagné !

                                            Dés : {dices[0]} {dices[1]} ({result})

                                            Vous quadruplez votre mise de {bet}{"XP" if what == "xp" else flamcoin_symbol} !
            """)
                await ctx.send(embed=embed, view=ReplayButton(self.street_craps, ctx, bet, what))
            else:
                user_data = Cf.get_user_data(ctx.author.id, ctx.guild.id)
                user_data[what] += int(bet)
                Cf.set_user_data(ctx.author.id, ctx.guild.id, user_data)
                embed = discord.Embed(color=discord.Color.gold(),
                                      title=f"STREET CRAPS - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}",
                                      description=
                                      f"""
                                            Vous vous faîtes rembourser

                                            Dés : {dices[0]} {dices[1]} ({result})

                                            Relancez une partie !
                            """)
                await ctx.send(embed=embed, view=ReplayButton(self.street_craps, ctx, bet, what))

    async def roulette(self, ctx, bet, what, choice=None):
        if choice == None:
            embed = discord.Embed(color=discord.Color.blue(), title=f"ROULETTE - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}", description=
            f"""
            Veuillez parier sur une couleur ci-dessous
            (Oui, on peut pas parier sur les nombres)
""")
            await ctx.send(embed=embed, view=RouletteChoice(self.roulette, ctx, bet, what))
        else:
            choices = ["red", "black", "green"]
            weights = [18, 18, 1]

            result = random.choices(choices, weights=weights)[0]
            if result == choice:
                mult = 35 if result == choice == "green" else 2
                user_data = Cf.get_user_data(ctx.author.id, ctx.guild.id)
                user_data[what] += int(mult * bet)
                Cf.set_user_data(ctx.author.id, ctx.guild.id, user_data)

            embed = discord.Embed(color=discord.Color.green() if result == choice else discord.Color.red(), title=f"ROULETTE - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}", description=
            f"""
            {"Vous gagnez !" if result == choice else "Vous perdez..."}
            {"Vous avez prié sur le vert ! Félicitations ! Votre mise est multipliée par 35 !" if result == choice == "green" else "Votre mise est doublée !" if result == choice else "Vous perdez votre mise..."}
            
            Résulat : {"🔴" if result == "red" else "⚫" if result == "black" else "🟢"}
            
            {f"Bien joué ! Vous pouvez reparier sur le {"rouge" if choice == "red" else "noir" if choice == "black" else "vert"} !" if result == choice else f"Dommage... Vous pouvez toujours reparier sur le {"rouge" if choice == "red" else "noir" if choice == "black" else "vert"} !"}
""")
            await ctx.send(embed=embed, view=ReplayButton(self.roulette, ctx, bet, what, arg=choice))

    async def peguin_cross(self, ctx, bet, what, choice=None, turn=None):
        mults = [1, 1.2, 1.5, 2, 3, 5, 10, 25, 75, 250, 1000]
        if choice == None:
            turn = 0
        elif choice == "step":
            if random.choices([True, False], weights=[3, 1])[0]:
                turn += 1
            else:
                space_str = ""
                for i in range(turn * 2):
                    space_str += "🟡"
                embed = discord.Embed(color=discord.Color.blue(),
                                      title=f"PEGUIN CROSS - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}",
                                      description=
                                      f"""
                        X0

                        🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🏁🏁🏁
                        {space_str+"🟡"}☠️
                        🧊🌊🧊🌊🧊🌊🧊🌊🧊🌊🧊🌊🧊🌊🧊🌊🧊🌊🧊🌊🧊🧊🧊
                        
                        Vous avez perdu... Vous perdez votre mise de {bet}{"XP" if what == "xp" else flamcoin_symbol}
                        Vous pouvez réessayer !
                """)
                await ctx.send(embed=embed, view=ReplayButton(self.peguin_cross, ctx, bet, what))
                return
        elif choice == "cashout" or turn == 10:
            user_data = Cf.get_user_data(ctx.author.id, ctx.guild.id)
            user_data[what] += int(bet * mults[turn])
            Cf.set_user_data(ctx.author.id, ctx.guild.id, user_data)
            space_str = ""
            for i in range(turn * 2):
                space_str += "🟡"
            embed = discord.Embed(color=discord.Color.blue(),
                                  title=f"PEGUIN CROSS - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}",
                                  description=
                                  f"""
                                    X{mults[turn]}

                                    🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🏁🏁🏁
                                    {space_str}🐧👍
                                    🧊🌊🧊🌊🧊🌊🧊🌊🧊🌊🧊🌊🧊🌊🧊🌊🧊🌊🧊🌊🧊🧊🧊

                                    Vous multipliez votre mise par {mults[turn]} !
                                    Vous pouvez réessayer !
                            """)
            await ctx.send(embed=embed, view=ReplayButton(self.peguin_cross, ctx, bet, what))
            return

        space_str = ""
        for i in range(turn*2):
            space_str += "🟡"
        embed = discord.Embed(color=discord.Color.blue(), title=f"PEGUIN CROSS - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}", description=
        f"""
        X{mults[turn]}
        
        🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🟰🏁🏁🏁
        {space_str}🐧
        🧊🌊🧊🌊🧊🌊🧊🌊🧊🌊🧊🌊🧊🌊🧊🌊🧊🌊🧊🌊🧊🧊🧊
""")
        await ctx.send(embed=embed, view=PeguinCrossChoice(self.peguin_cross, ctx, bet, what, turn))

    def get_map_str(self, game_info, lose=False):
        map_str = ""
        if not lose:
            for i in range(6):
                if i == len(game_info["played_map"]):
                    map_str += "⬜⬜⬜⬜\n"
                elif i > len(game_info["played_map"]):
                    map_str += "⬛⬛⬛⬛\n"
                else:
                    if game_info["played_map"][i] == 0:
                        map_str += "🟩⬛⬛⬛\n"
                    elif game_info["played_map"][i] == 1:
                        map_str += "⬛🟩⬛⬛\n"
                    elif game_info["played_map"][i] == 2:
                        map_str += "⬛⬛🟩⬛\n"
                    elif game_info["played_map"][i] == 3:
                        map_str += "⬛⬛⬛🟩\n"
        else:
            for i in range(6):
                if game_info["bombs_map"][i] == 0:
                    map_str += "🟥⬛⬛⬛\n"
                elif game_info["bombs_map"][i] == 1:
                    map_str += "⬛🟥⬛⬛\n"
                elif game_info["bombs_map"][i] == 2:
                    map_str += "⬛⬛🟥⬛\n"
                elif game_info["bombs_map"][i] == 3:
                    map_str += "⬛⬛⬛🟥\n"
        return map_str

    async def dragon_tower(self, ctx, bet, what, game_info=None, choice=None):
        mults = [1, 1.5, 2, 2.5, 3, 4, 5]
        if game_info == None:
            game_info = {
                "bombs_map": [],
                "played_map": [],
            }
            for i in range(7):
                game_info["bombs_map"].append(random.randint(0, 3))

        elif choice in ["1", "2", "3", "4"]:
            choice = int(choice) - 1
            if game_info["bombs_map"][len(game_info["played_map"])] == choice:
                embed = discord.Embed(color=discord.Color.red(),
                                      title=f"DRAGON TOWER - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}",
                                      description=
                                      f"""
                        {self.get_map_str(game_info, lose=True)}
                        1️⃣2️⃣3️⃣4️⃣     X0

                        Vous avez perdez... Dommage, vous pouvez toujours retenter !
                """)
                await ctx.send(embed=embed, view=ReplayButton(self.dragon_tower, ctx, bet, what))
                return
            else:
                game_info["played_map"].append(choice)

        if choice == "cashout" or len(game_info["played_map"]) == 6:
            user_data = Cf.get_user_data(ctx.author.id, ctx.guild.id)
            user_data[what] += int(bet * mults[len(game_info["played_map"])])
            Cf.set_user_data(ctx.author.id, ctx.guild.id, user_data)
            embed = discord.Embed(color=discord.Color.green(),
                                  title=f"DRAGON TOWER - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}",
                                  description=
                                  f"""
                    {self.get_map_str(game_info)}
                    1️⃣2️⃣3️⃣4️⃣     X{mults[len(game_info["played_map"])]}

                    Vous remportez {bet*mults[len(game_info["played_map"])]}{"XP" if what == "xp" else flamcoin_symbol} sur les {bet} que vous avez misé !
            """)
            await ctx.send(embed=embed, view=ReplayButton(self.dragon_tower, ctx, bet, what))
            return


        embed = discord.Embed(color=discord.Color.blue(), title=f"DRAGON TOWER - MISE : {bet}{"XP" if what == "xp" else flamcoin_symbol} - {ctx.author.display_name.upper()}", description=
        f"""
        {self.get_map_str(game_info)}
        1️⃣2️⃣3️⃣4️⃣     X{mults[len(game_info["played_map"])]}
        
        Choisissez une colonne ou chast-out.
""")
        await ctx.send(embed=embed, view=DragonTowerChoice(self.dragon_tower, ctx, bet, what, game_info))


    @commands.hybrid_command(name="gambling_quote")
    async def gambling_quote(self, ctx: commands.Context):
        """
        Envoie une citation de gambling aléatoire (vient de Gamble with your Friends)
        :param ctx: Context
        :return:
        """
        quote = random.choice(gambling_quotes)
        await ctx.send(quote)


async def setup(bot):
    await bot.add_cog(Gamebling(bot))