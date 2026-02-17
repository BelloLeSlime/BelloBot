import os
import json
from random import choice
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
hg_token = os.getenv('HG_TOKEN')
from discord import *
from datetime import datetime, timedelta, UTC
from typing import Literal

#---------------------------------SET UP-----------------------------------------

intents = Intents.default()
intents.message_content = True

class MyClient(Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

bot = MyClient()

#----------------------------------CLASSES------------------------------------------

class ShopSelect(ui.Select):
    def __init__(self):
        options = [
            SelectOption(
                label="Petite Potion d'Expérience",
                description="Double l'XP reçu pendant 1h • 1000₣",
                value="small_xp_potion",
                emoji="🧪"
            ),
            SelectOption(
                label="Petite Potion de Cupidité",
                description="Double l'argent reçu pendant 1h • 2000₣",
                value="small_money_potion",
                emoji="🧪"
            ),
            SelectOption(
                label="Back Door",
                description="Vous permet d'uploader des fichiers pendant 1 mois • 5000₣",
                value="back_door",
                emoji="🚪"
            ),
            SelectOption(
                label="Audacity",
                description="Vous permet d'utiliser des soundboards et d'envoyer des messages vocaux pendant 1 mois • 6000₣",
                value="audacity",
                emoji="🎧"
            ),
            SelectOption(
                label="Nintendo Switch 17",
                description="Permet de lancer une activité dans un vocal pendant 1 mois • 7000₣",
                value="nintendo_switch_17",
                emoji="🎮"
            ),
            SelectOption(
                label="Partenariat avec l'IFOP",
                description="Permet de créer des sondages pendant 1 mois • 7000₣",
                value="ifop",
                emoji="🎤"
            ),
            SelectOption(
                label="Site web",
                description="Permet d'intégrer des liens pendant 1 mois • 7000₣",
                value="site_web",
                emoji="🌐"
            ),
            SelectOption(
                label="External Plexus",
                description="Vous permet d'utiliser des emojis, des autocollants, etc externes pendant 1 mois • 3000₣",
                value="external_plexus",
                emoji="🌐"
            ),
            SelectOption(
                label="Microphone",
                description="Donne la voix prioritaire en vocal pendant 1 mois • 7000₣",
                value="microphone",
                emoji="🎤"
            ),
            SelectOption(
                label="Formule 1",
                description="Permet d'ignorer le mode lent pendant 1 mois • 9000₣",
                value="formule_1",
                emoji="🏎️"
            ),
            SelectOption(
                label="Name Tag",
                description="Permet de renommer quelqu'un une fois (attention, punition si jugé humiliant) • 10000₣",
                value="name_tag",
                emoji="🏷️"
            ),
            SelectOption(
                label="Ban Hammer",
                description="Permet de bannir quelqu'un pendant une durée inférieure à 1 mois • 100000₣",
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

    async def callback(self, interaction):
        item = self.values[0]
        prices = {
            "small_xp_potion": 1000,
            "small_money_potion": 2000,
            "back_door": 5000,
            "audacity": 6000,
            "nintendo_switch_17": 7000,
            "ifop": 7000,
            "site_web": 7000,
            "external_plexus": 3000,
            "microphone": 7000,
            "formule_1": 9000,
            "name_tag": 10000,
            "ban_hammer": 100000,
        }
        price = prices[item]
        user = interaction.user
        user_data = read_json(f"xp/{user.id}.json")
        wallet = user_data["money"]
        if wallet > price:
            add_item(user.id, item)
            await interaction.response.send_message("Merci pour votre achat !")
        else:
            await interaction.response.send_message("Tu n'a pas assez pour acheter ça.\nBah alors, on est pauvre ? ༼ つ XD ༽つ")

class ShopView(ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(ShopSelect())

#---------------------------------FUNCTIONS-----------------------------------------

def ask_ai(messages, model):
    client = InferenceClient(token=hg_token)
    response = client.chat_completion(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content

def log(type, message):
    to_write = f"{type} - {message} - {datetime.now()}"
    print(to_write)
    with open("log.txt", "a", encoding="utf-8") as file:
        file.write(to_write + "\n")

def write_file(message, path):
    message = message.replace("\n", " ")
    with open(path, "a", encoding="utf-8") as file:
        file.write(message + "\n")

def read_file(path):
    lines = []
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            lines.append(line)
    return lines

def write_json(data, path):
    with open(path, "w", encoding="utf-8") as file:
        file.write(json.dumps(data, indent=2))

def read_json(path):
    with open(path, "r", encoding="utf-8") as file:
        data = json.loads(file.read())
        return data

def add_item(user_id: int, item: str):
    data = read_json(f"xp/{user_id}.json")
    data["items"][item] = data["items"][item] + 1 if item in data["items"] else 1
    write_json(data, f"xp/{user_id}.json")

def check_has_data_file(user_id):
    if not str(user_id)+".json" in os.listdir("./xp/"):
        write_json({"xp": 0, "level": 1, "money": 0, "mult_xp": 1, "mult_money": 1, "temp_effects": {}, "items": {}}, "xp/" + str(user_id) + ".json")

#---------------------------------VARIABLES------------------------------------------

system = "Tu es BelloBot, un bot Discord. Utilise du vocabulaire de discord, utilise des émoticônes comme ;( >:) ¯\\_( ͡° ͜ʖ ͡°)_/¯ ༼ つ ◕_◕ ༽つ ಠ_ಠ :p XD et d'autre. Tu aura au début du message de l'utilisateur son nom. Il n'est pas dans ce qu'il a dit réellement, donc ne mets pas BelloBot: ou <Nom>: au début, car cela sera sans rapport."
model = "meta-llama/Llama-3.1-8B-Instruct"
guild_id: int = int(os.getenv("GUILD_ID"))
guild: Guild|None = None
xp_channel: TextChannel|None = None
x2_xp_role_id = read_json("config.json")["x2_xp_role"]
x2_xp_role: Role|None = None
x2_money_role_id = read_json("config.json")["x2_money_role"]
x2_money_role: Role|None = None
file_role_id = read_json("config.json")["file_role"]
file_role: Role|None = None
soundboard_role_id = read_json("config.json")["soundboard_role"]
soundboard_role: Role|None = None
game_role_id = read_json("config.json")["game_role"]
game_role: Role|None = None
poll_role_id = read_json("config.json")["poll_role"]
poll_role: Role|None = None
link_role_id = read_json("config.json")["link_role"]
link_role: Role|None = None
extern_role_id = read_json("config.json")["extern_role"]
extern_role: Role|None = None
priority_voice_role_id = read_json("config.json")["priority_voice_role"]
priority_voice_role: Role|None = None
bypass_slow_mode_role_id = read_json("config.json")["bypass_slow_mode_role"]
bypass_slow_mode_role: Role|None = None

#---------------------------------EVENTS---------------------------------------------

@bot.event
async def on_ready():
    global guild
    global xp_channel
    global x2_xp_role
    global x2_money_role
    global file_role
    global soundboard_role
    global game_role
    global poll_role
    global link_role
    global extern_role
    global priority_voice_role
    global bypass_slow_mode_role
    log("connected", bot.user.name)
    states = [
        "rien, je suis une IA :p",
        "Peak car c'est incrr",
        "NEVER GONNA GIVE YOU UP",
        "une minute de plus dans ce jacuzzi et je me transforme en William Afton.",
        "avec vos données >:3",
        "v2.1 ༼ つ ◕_◕ ༽つ",
    ]
    await bot.change_presence(
        activity=Activity(
            type=ActivityType.playing,
            name=choice(states)
        )
    )
    guild = await bot.fetch_guild(guild_id)
    xp_channel_id = read_json("config.json")["xp_channel"]
    xp_channel = await guild.fetch_channel(xp_channel_id)
    x2_xp_role = guild.get_role(x2_xp_role_id)
    x2_money_role = guild.get_role(x2_money_role_id)
    file_role = guild.get_role(file_role_id)
    soundboard_role = guild.get_role(soundboard_role_id)
    game_role = guild.get_role(game_role_id)
    poll_role = guild.get_role(poll_role_id)
    link_role = guild.get_role(link_role_id)
    extern_role = guild.get_role(extern_role_id)
    priority_voice_role = guild.get_role(priority_voice_role_id)
    bypass_slow_mode_role = guild.get_role(bypass_slow_mode_role_id)

@bot.event
async def on_message(message: Message):
    content = message.content
    #ai
    if not content == "":
        author = message.author.display_name
        for mention in message.mentions:
            content = content.replace(
                f"<@{mention.id}>",
                f"@{mention.display_name}"
            )
        for channel in message.channel_mentions:
            content = content.replace(
                f"<#{channel.id}>",
                f"#{channel.name}"
            )

        for role in message.role_mentions:
            content = content.replace(
                f"<@&{role.id}>",
                f"@{role.name}"
            )
        write_file(author + " : " + content, "messages.txt")
        log("message", author + " : " + content)
        if bot.user in message.mentions and message.author != bot.user:
            try:
                messages = [
                    {"role": "system", "content": system},
                ]
                for msg in read_file("messages.txt"):
                    msg = str(msg)
                    author = msg.split(" : ")[0]
                    messages.append({"role": "user" if author != "BelloBot" else "assistant", "content":msg if author != "BelloBot" else msg.removeprefix("BelloBot : ")})
                answer = ask_ai(messages, model)
                await message.reply(answer)
            except Exception as e:
                print(e)
                await message.channel.send("<Erreur !>")
                log("error", str(e))
    #xp

    check_has_data_file(message.author.id)

    user_data_xp = read_json(f"xp/{str(message.author.id) + ".json"}")
    member: Member = await message.guild.fetch_member(message.author.id)

    if user_data_xp["mult_xp"] > 1:
        if datetime.fromisoformat(user_data_xp["temp_effects"]["boost_xp"]) < datetime.now(UTC):
            del user_data_xp["temp_effects"]["boost_xp"]
            user_data_xp["mult_xp"] = 1
            await message.author.remove_roles(x2_xp_role)
    if user_data_xp["mult_money"] > 1:
        if datetime.fromisoformat(user_data_xp["temp_effects"]["boost_money"]) < datetime.now(UTC):
            del user_data_xp["temp_effects"]["boost_money"]
            user_data_xp["mult_money"] = 1
            await message.author.remove_roles(x2_money_role)
    if file_role in member.roles:
        if datetime.fromisoformat(user_data_xp["temp_effects"]["file"]) < datetime.now(UTC):
            del user_data_xp["temp_effects"]["file"]
            await message.author.remove_roles(file_role)
    if soundboard_role in member.roles:
        if datetime.fromisoformat(user_data_xp["temp_effects"]["soundboard"]) < datetime.now(UTC):
            del user_data_xp["temp_effects"]["soundboard"]
            await message.author.remove_roles(soundboard_role)
    if game_role in member.roles:
        if datetime.fromisoformat(user_data_xp["temp_effects"]["game"]) < datetime.now(UTC):
            del user_data_xp["temp_effects"]["game"]
            await message.author.remove_roles(game_role)
    if poll_role in member.roles:
        if datetime.fromisoformat(user_data_xp["temp_effects"]["poll"]) < datetime.now(UTC):
            del user_data_xp["temp_effects"]["poll"]
            await message.author.remove_roles(poll_role)
    if link_role in member.roles:
        if datetime.fromisoformat(user_data_xp["temp_effects"]["link"]) < datetime.now(UTC):
            del user_data_xp["temp_effects"]["link"]
            await message.author.remove_roles(link_role)
    if extern_role in member.roles:
        if datetime.fromisoformat(user_data_xp["temp_effects"]["extern"]) < datetime.now(UTC):
            del user_data_xp["temp_effects"]["extern"]
            await message.author.remove_roles(extern_role)
    if priority_voice_role in member.roles:
        if datetime.fromisoformat(user_data_xp["temp_effects"]["priority_voice"]) < datetime.now(UTC):
            del user_data_xp["temp_effects"]["priority_voice"]
            await message.author.remove_roles(priority_voice_role)
    if bypass_slow_mode_role in member.roles:
        if datetime.fromisoformat(user_data_xp["temp_effects"]["bypass_slow_mode"]) < datetime.now(UTC):
            del user_data_xp["temp_effects"]["bypass_slow_mode"]
            await message.author.remove_roles(bypass_slow_mode_role)

    user_data_xp["xp"] += 5 * user_data_xp["mult_xp"]
    user_data_xp["money"] += 10 * user_data_xp["mult_money"]
    if user_data_xp["xp"] >= 15 * user_data_xp["level"]:
        user_data_xp["xp"] -= 15 * user_data_xp["level"]
        user_data_xp["level"] += 1
        user_data_xp["money"] += 50 * user_data_xp["level"]
        if message.author == bot.user:
            await xp_channel.send(f"Moi, {bot.user.mention}, a passé le niveau {user_data_xp["level"]} ! 🥳🎉 GG à moi-même ༼ つ ಠ◡ಠ ༽つ Je gagne {50 * user_data_xp["level"]}₣ 💰💰💰")
        else:
            await xp_channel.send(f"GG à {message.author.mention} pour avoir passé le niveau {user_data_xp["level"]} ! 🥳🎉 Tu gagnes {50 * user_data_xp["level"]}₣ 💰💰💰 Continue de gagner des niveaux... 🔥🔥🔥")
    write_json(user_data_xp, f"xp/{str(message.author.id) + ".json"}")

#----------------------------------BOT COMMANDS----------------------------------------

@bot.tree.command(name="attribute_xp_channel", description="Attribue un salon pour anoncer le gain de niveau.")
@app_commands.describe(channel="channel")
@app_commands.checks.has_permissions(administrator=True)
async def attribute_xp_channel(interaction: Interaction, channel:TextChannel):
    global xp_channel
    if channel:
        data = read_json("config.json")
        data["xp_channel"] = channel.id
        write_json(data, "config.json")
        xp_channel = channel
        await interaction.response.send_message(f"Salon XP définie sur {channel.mention}", ephemeral=True)
    else:
        await interaction.response.send_message(f"Salon invalide !", ephemeral=True)

@bot.tree.command(name="xp", description="Affiche le nombre d'xp")
@app_commands.describe(user="user")
async def xp(interaction: Interaction, user:User = None):
    if user is None:
        user = interaction.user
    check_has_data_file(user.id)
    user_data_xp = read_json(f"xp/{str(user.id)}.json")
    self = user == interaction.user
    if user == bot.user:
        await interaction.response.send_message(f"Je suis au niveau {user_data_xp['level']}, j'ai {user_data_xp['xp']} xp et il me manque {user_data_xp["level"] * 15 - user_data_xp['xp']} xp pour passer au niveau {user_data_xp['level'] + 1} ༼ つ ◕_◕ ༽つ")
    elif self:
        await interaction.response.send_message(f"Tu es au niveau {user_data_xp['level']}, tu as {user_data_xp['xp']} xp et il te manque {user_data_xp["level"] * 15 - user_data_xp['xp']} xp pour passer au niveau {user_data_xp['level']+1} :p")
    else:
        await interaction.response.send_message(f"{user.display_name} est au niveau {user_data_xp['level']}, il a {user_data_xp['xp']} xp et il lui manque {user_data_xp["level"] * 15 - user_data_xp['xp']} xp pour passer au niveau {user_data_xp['level'] + 1} :p")

@bot.tree.command(name="wallet", description="Affiche le nombre de Flamcoins")
@app_commands.describe(user="user")
async def wallet(interaction: Interaction, user:User = None):
    if user is None:
        user = interaction.user
    check_has_data_file(user.id)
    user_data_xp = read_json(f"xp/{str(user.id)}.json")
    money = user_data_xp["money"]
    self = user == interaction.user
    if user == bot.user:
        await interaction.response.send_message(f"J'ai actuellement {money}₣.")
    elif self:
        await interaction.response.send_message(f"Tu as actuellement {money}₣.")
    else:
        await interaction.response.send_message(f"{user.display_name} a actuellement {money}₣.")

@bot.tree.command(name="shop", description="Affiche le magasin")
async def shop(interaction: Interaction):
    embed = Embed(
        title="🛒 SHOP",
        description="Bienvenue au Shop.\nSélectionne un objet ci-dessous.",
        color=Color.gold()
    )
    await interaction.response.send_message(
        embed=embed,
        view=ShopView()
    )

@bot.tree.command(name="give_xp", description="Donne un nombre d'xp à un membre")
@app_commands.describe(amount="amount", user="user")
@app_commands.checks.has_permissions(administrator=True)
async def give_xp(interaction: Interaction, amount: int, user: User = None):
    if user is None:
        user = interaction.user
    check_has_data_file(user.id)
    user_data_xp = read_json(f"xp/{str(user.id)}.json")
    user_data_xp["xp"] += amount
    write_json(user_data_xp, f"xp/{str(user.id)}.json")
    await interaction.response.send_message(f"Vous avez bien ajouté {amount} xp à {user.display_name}. Il a maintenant {user_data_xp['xp']} xp.", ephemeral=True)

@bot.tree.command(name="set_xp", description="Met un à membre un nombre d'xp")
@app_commands.describe(amount="amount", user="user")
@app_commands.checks.has_permissions(administrator=True)
async def set_xp(interaction: Interaction, amount: int, user: User = None):
    if user is None:
        user = interaction.user
    check_has_data_file(user.id)
    user_data_xp = read_json(f"xp/{str(user.id)}.json")
    user_data_xp["xp"] = amount
    write_json(user_data_xp, f"xp/{str(user.id)}.json")
    await interaction.response.send_message(f"Vous avez bien mit {amount} xp à {user.display_name}.", ephemeral=True)

@bot.tree.command(name="give_money", description="Donne un nombre d'argent à un membre")
@app_commands.describe(amount="amount", user="user")
@app_commands.checks.has_permissions(administrator=True)
async def give_money(interaction: Interaction, amount: int, user: User = None):
    if user is None:
        user = interaction.user
    check_has_data_file(user.id)
    user_data_xp = read_json(f"xp/{str(user.id)}.json")
    user_data_xp["money"] += amount
    write_json(user_data_xp, f"xp/{str(user.id)}.json")
    await interaction.response.send_message(f"Vous avez bien ajouté {amount}₣ à {user.display_name}. Il a maintenant {user_data_xp['money']}₣.", ephemeral=True)

@bot.tree.command(name="set_money", description="Met un à membre un nombre d'argent")
@app_commands.describe(amount="amount", user="user")
@app_commands.checks.has_permissions(administrator=True)
async def set_money(interaction: Interaction, amount: int, user: User = None):
    if user is None:
        user = interaction.user
    check_has_data_file(user.id)
    user_data_xp = read_json(f"xp/{str(user.id)}.json")
    user_data_xp["xp"] = amount
    write_json(user_data_xp, f"xp/{str(user.id)}.json")
    await interaction.response.send_message(f"Vous avez bien mit {amount}₣ à {user.display_name}.", ephemeral=True)

@bot.tree.command(name="give_level", description="Donne un nombre de niveaux à un membre")
@app_commands.describe(amount="amount", user="user")
@app_commands.checks.has_permissions(administrator=True)
async def give_level(interaction: Interaction, amount: int, user: User = None):
    if user is None:
        user = interaction.user
    check_has_data_file(user.id)
    user_data_xp = read_json(f"xp/{str(user.id)}.json")
    user_data_xp["level"] += amount
    write_json(user_data_xp, f"xp/{str(user.id)}.json")
    await interaction.response.send_message(f"Vous avez bien ajouté {amount} niveaux à {user.display_name}. Il a maintenant niveau {user_data_xp['level']}.", ephemeral=True)

@bot.tree.command(name="set_level", description="Met un à membre un nombre de niveaux")
@app_commands.describe(amount="amount", user="user")
@app_commands.checks.has_permissions(administrator=True)
async def set_level(interaction: Interaction, amount: int, user: User = None):
    if user is None:
        user = interaction.user
    check_has_data_file(user.id)
    user_data_xp = read_json(f"xp/{str(user.id)}.json")
    user_data_xp["level"] = amount
    write_json(user_data_xp, f"xp/{str(user.id)}.json")
    await interaction.response.send_message(f"Vous avez bien mit {amount} niveaux à {user.display_name}.", ephemeral=True)

@bot.tree.command(name="reset", description="Remet tout le serveur au niveau 1, avec 0 argent et 0 xp")
@app_commands.checks.has_permissions(administrator=True)
async def reset(interaction: Interaction):
    for file in os.listdir("./xp/"):
        user_data_xp = read_json(f"xp/{file}")
        user_data_xp["xp"] = 0
        user_data_xp["money"] = 0
        user_data_xp["level"] = 1
        user_data_xp["mult_xp"] = 1
        user_data_xp["mult_money"] = 1
        user_data_xp["temp_effects"] = {}
        user_data_xp["items"]={}
        write_json(user_data_xp, f"xp/{file}")
    await interaction.response.send_message(f"Vous avez bien remit le serveur à 0.", ephemeral=True)

@bot.tree.command(name="use", description="Utilise un item dans l'inventaire")
@app_commands.describe(item="item", target_user="user", name="name", time_in_hours="time")
async def use(interaction: Interaction, item: Literal["Petite Potion d'Expérience", "Petite Potion de Cupidité", "Back Door", "Audacity", "Nintendo Switch 17", "Partenariat avec l'IFOP", "Site Web", "External Plexus", "Microphone", "Formule 1", "Name Tag",  "Ban Hammer"], target_user: User|None = None, name: str|None = None, time_in_hours: int|None = None ):
    check_has_data_file(interaction.user.id)
    item_trad = {
        "Petite Potion d'Expérience": "small_xp_potion",
        "Petite Potion de Cupidité": "small_money_potion",
        "Back Door": "back_door",
        "Audacity": "audacity",
        "Nintendo Switch 17": "nintendo_switch_17",
        "Partenariat avec l'IFOP": "ifop",
        "Site Web": "site_web",
        "External Plexus": "external_plexus",
        "Microphone": "microphone",
        "Formule 1": "formule_1",
        "Name Tag": "name_tag",
        "Ban Hammer": "ban_hammer",
    }
    item = item_trad[item]
    user = interaction.user
    data = read_json(f"xp/{str(user.id)}.json")
    if item in data["items"]:
        if data["items"][item] > 0:
            data["items"][item] -= 1
            if item == "small_xp_potion":
                user = interaction.user
                user_data = read_json(f"xp/{user.id}.json")
                user_data["mult_xp"] = 2
                user_data["temp_effects"]["boost_money"] = (datetime.now(UTC) + timedelta(hours=1)).isoformat()
                write_json(user_data, f"xp/{user.id}.json")
                await interaction.user.add_roles(x2_xp_role)
                await interaction.response.send_message("X2 XP pendant 1 heure !", ephemeral=True)

            elif item == "small_money_potion":
                user = interaction.user
                user_data = read_json(f"xp/{user.id}.json")
                user_data["mult_money"] = 2
                user_data["temp_effects"]["boost_money"] = (datetime.now(UTC) + timedelta(hours=1)).isoformat()
                write_json(user_data, f"xp/{user.id}.json")
                await interaction.user.add_roles(x2_money_role)
                await interaction.response.send_message("X2 Argent pendant 1 heure !", ephemeral=True)

            elif item == "back_door":
                user = interaction.user
                user_data = read_json(f"xp/{user.id}.json")
                user_data["temp_effects"]["file"] = (datetime.now(UTC) + timedelta(days=31)).isoformat()
                await user.add_roles(file_role)
                write_json(user_data, f"xp/{user.id}.json")
                await interaction.response.send_message("Vous pouvez maintenant envoyer des fichiers !", ephemeral=True)

            elif item == "audacity ":
                user = interaction.user
                user_data = read_json(f"xp/{user.id}.json")
                user_data["temp_effects"]["soundboard"] = (datetime.now(UTC) + timedelta(days=31)).isoformat()
                await user.add_roles(soundboard_role)
                write_json(user_data, f"xp/{user.id}.json")
                await interaction.response.send_message("Vous pouvez maintenant utiliser le soundborad !", ephemeral=True)

            elif item == "nintendo_switch_17":
                user = interaction.user
                user_data = read_json(f"xp/{user.id}.json")
                user_data["temp_effects"]["game"] = (datetime.now(UTC) + timedelta(days=31)).isoformat()
                await user.add_roles(game_role)
                write_json(user_data, f"xp/{user.id}.json")
                await interaction.response.send_message("Vous pouvez maintenant utiliser les applications !",ephemeral=True)

            elif item == "ifop":
                user = interaction.user
                user_data = read_json(f"xp/{user.id}.json")
                user_data["temp_effects"]["poll"] = (datetime.now(UTC) + timedelta(days=31)).isoformat()
                await user.add_roles(poll_role)
                write_json(user_data, f"xp/{user.id}.json")
                await interaction.response.send_message("Vous pouvez maintenant créer des sondages !", ephemeral=True)

            elif item == "site_web":
                user = interaction.user
                user_data = read_json(f"xp/{user.id}.json")
                user_data["temp_effects"]["link"] = (datetime.now(UTC) + timedelta(days=31)).isoformat()
                await user.add_roles(link_role)
                write_json(user_data, f"xp/{user.id}.json")
                await interaction.response.send_message("Vous pouvez maintenant intégrer des liens !", ephemeral=True)

            elif item == "external_plexus":
                user = interaction.user
                user_data = read_json(f"xp/{user.id}.json")
                user_data["temp_effects"]["extern"] = (datetime.now(UTC) + timedelta(days=31)).isoformat()
                await user.add_roles(extern_role)
                write_json(user_data, f"xp/{user.id}.json")
                await interaction.response.send_message("Vous pouvez maintenant utiliser des emojis, autocollants, soundborads et applications externes !", ephemeral=True)

            elif item == "microphone":
                user = interaction.user
                user_data = read_json(f"xp/{user.id}.json")
                user_data["temp_effects"]["priority_voice"] = (datetime.now(UTC) + timedelta(days=31)).isoformat()
                await user.add_roles(priority_voice_role)
                write_json(user_data, f"xp/{user.id}.json")
                await interaction.response.send_message("Vous avez maintenant la voix prioritaire en vocal !", ephemeral=True)

            elif item == "formule_1":
                user = interaction.user
                user_data = read_json(f"xp/{user.id}.json")
                user_data["temp_effects"]["bypass_slow_mode"] = (datetime.now(UTC) + timedelta(days=31)).isoformat()
                await user.add_roles(bypass_slow_mode_role)
                write_json(user_data, f"xp/{user.id}.json")
                await interaction.response.send_message("Vous pouvez maintenant contourner le mode lent !", ephemeral=True)

            elif item == "name_tag":
                if target_user:
                    if name:
                        await target_user.edit(nick=name)
                        await interaction.response.send_message(f"Le pseudo de {target_user.mention} a bien été renommé ! ○( ＾皿＾)っ Hehehe…")
                    else:
                        await interaction.response.send_message(f"Veuillez indiquer un nom.", ephemeral=True)
                        if "name_tag" in data["items"]:
                            data["items"]["name_tag"] += 1
                        else:
                            data["items"]["name_tag"] = 1
                else:
                    await interaction.response.send_message(f"Veuillez indiquer un utilisateur.", ephemeral=True)
                    if "name_tag" in data["items"]:
                        data["items"]["name_tag"] += 1
                    else:
                        data["items"]["name_tag"] = 1

            elif item == "ban_hammer":
                if target_user:
                    member = await interaction.guild.fetch_member(target_user.id)
                    if 0.16666666666666667 < time_in_hours < 24:
                        await member.timeout(timedelta(hours=time_in_hours), reason="Ban hammer")
                        await interaction.response.send_message(f"Vous avez bien mute {target_user.mention} pendant {time_in_hours} heures ! Baha noob")
                    else:
                        await interaction.response.send_message(f"Le temps doit être entre 10min et 1h", ephemeral=True)
                else:
                    await interaction.response.send_message(f"Veuillez indiquer un utilisateur.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Vous n'avez pas cet item :p\n Vous pouvez l'acheter au shop avec /shop", ephemeral=True)
    else:
        await interaction.response.send_message(f"Vous n'avez pas cet item :p\n Vous pouvez l'acheter au shop avec /shop", ephemeral=True)

@bot.tree.command(name="inventory", description="Affiche l'inventaire")
@app_commands.describe(user="user")
async def inventory(interaction: Interaction, user: User|None = None):
    if user is None:
        user = interaction.user
    check_has_data_file(user.id)
    user_data = read_json(f"xp/{user.id}.json")
    inventory = user_data["items"]
    item_trad = {
        "small_xp_potion": "Petite Potion d'Expérience",
        "small_money_potion": "Petite Potion de Cupidité",
        "back_door": "Back Door",
        "audacity": "Audacity",
        "nintendo_switch_17": "Nintendo Switch 17",
        "ifop": "Partenariat avec l'IFOP",
        "site_web": "Site Web",
        "external_plexus": "External Plexus",
        "microphone": "Microphone",
        "formule_1": "Formule 1",
        "name_tag": "Name Tag",
        "ban_hammer": "Ban Hammer",
    }
    description = ""
    for item_type in inventory:
        if inventory[item_type] > 0:
            description += f"{item_trad[item_type]} : {inventory[item_type]}\n"
    embed = Embed(title=f" Inventaire de {user.display_name} :", description=description, color=Color.green())
    await interaction.response.send_message(embed=embed)

#--------------------------------------RUN---------------------------------------------

try:
    bot.run(token)
except Exception as e:
    log("critical error", str(e))
finally:
    log("exiting", bot.user.name)



