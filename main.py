import os
import json
from random import choice
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from huggingface_hub.errors import BadRequestError

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
hg_token = os.getenv('HG_TOKEN')
try:
    giphy_token = os.getenv('GIPHY_TOKEN')
except:
    pass
from discord import *
from discord.ext import tasks
from datetime import datetime, timedelta, UTC
from typing import Literal
from PIL import Image
import io
import requests
import re
import asyncio

# ---------------------------------SET UP-----------------------------------------

intents = Intents.default()
intents.message_content = True
intents.presences = True


class MyClient(Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()


bot = MyClient()


# ----------------------------------CLASSES------------------------------------------

class ShopSelect(ui.Select):
    def __init__(self):
        options = [
            SelectOption(
                label="Petite Potion d'Expérience",
                description="Double l'XP reçu pendant 1 jour • 500",
                value="small_xp_potion",
                emoji="🧪"
            ),
            SelectOption(
                label="Petite Potion de Cupidité",
                description="Double l'argent reçu pendant 1 jour • 1000",
                value="small_money_potion",
                emoji="🧪"
            ),
            SelectOption(
                label="Back Door",
                description="Vous permet d'uploader des fichiers pendant 3 mois • 1000₣",
                value="back_door",
                emoji="🚪"
            ),
            SelectOption(
                label="Audacity",
                description="Vous permet d'utiliser des soundboards et d'envoyer des messages vocaux pendant 3 mois • 1000₣",
                value="audacity",
                emoji="🎧"
            ),
            SelectOption(
                label="Nintendo Switch 17",
                description="Permet de lancer une activité dans un vocal pendant 3 mois • 2000₣",
                value="nintendo_switch_17",
                emoji="🎮"
            ),
            SelectOption(
                label="Partenariat avec l'IFOP",
                description="Permet de créer des sondages pendant 3 mois • 1000₣",
                value="ifop",
                emoji="🎤"
            ),
            SelectOption(
                label="Site web",
                description="Permet d'intégrer des liens pendant 3 mois • 500₣",
                value="site_web",
                emoji="🌐"
            ),
            SelectOption(
                label="External Plexus",
                description="Vous permet d'utiliser des emojis, des autocollants, etc externes pendant 3 mois • 250₣",
                value="external_plexus",
                emoji="🌐"
            ),
            SelectOption(
                label="Microphone",
                description="Donne la voix prioritaire en vocal pendant 3 mois • 4000₣",
                value="microphone",
                emoji="🎤"
            ),
            SelectOption(
                label="Formule 1",
                description="Permet d'ignorer le mode lent pendant 3 mois • 5000₣",
                value="formule_1",
                emoji="🏎️"
            ),
            SelectOption(
                label="Name Tag",
                description="Permet de renommer quelqu'un une fois (attention, punition si jugé humiliant) • 8000₣",
                value="name_tag",
                emoji="🏷️"
            ),
            SelectOption(
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

    async def callback(self, interaction):
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
        user_data = read_json(f"files/user_info/{interaction.guild.id}/{user.id}.json")
        wallet = user_data["money"]
        if wallet > price:
            user_data["money"] -= price
            write_json(user_data, f"files/user_info/{interaction.guild.id}/{user.id}.json")
            add_item(interaction.guild.id, user.id, item)
            embed = Embed(color=Color.blue(), title="Merci pour votre achat !", description="Revenez plus tard !")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = Embed(color=Color.red(), title="Vous n'avez pas assez d'argent pour acheter ça",
                          description="Bah alors ? On est pauvre ? ༼ つ XD ༽つ")
            await interaction.response.send_message(embed=embed, ephemeral=True)

class ShopView(ui.View):
    def __init__(self):
        super().__init__()
        self.add_item()

# ---------------------------------FUNCTIONS-----------------------------------------

def ask_ai(messages, model):
    client = InferenceClient(token=hg_token)
    response = client.chat_completion(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content

def text_to_image(prompt, model, negative_prompt, width=1024, height=1024, steps=30):
    client = InferenceClient(token=hg_token)
    image = client.text_to_image(prompt=prompt, model=model, negative_prompt=negative_prompt, width=width,
                                 height=height, num_inference_steps=steps)
    return image

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

def add_item(guild_id: int, user_id: int, item: str):
    log("shop", str(user_id) + item)
    data = read_json(f"files/user_info/{guild_id}/{user_id}.json")
    data["items"][item] = data["items"][item] + 1 if item in data["items"] else 1
    write_json(data, f"files/user_info/{guild_id}/{user_id}.json")

def check_has_data_file(user_id, guild_id):
    check_guild_has_presence(guild_id)
    if not str(guild_id) in os.listdir("files/user_info/"):
        os.makedirs(f"files/user_info/{guild_id}")
    try:
        if not str(user_id) + ".json" in os.listdir(f"./files/user_info/{guild_id}/"):
            write_json({"xp": 0, "level": 1, "money": 0, "mult_xp": 1, "mult_money": 1, "temp_effects": {}, "items": {}},
                       f"files/user_info/{guild_id}/{user_id}.json")
    except:
        pass
    try:
        if not str(user_id) + ".json" in os.listdir(f"./files/alarms/{guild_id}/"):
            write_json({}, f"files/alarms/{guild_id}/{user_id}.json")
    except:
        pass

def check_guild_has_presence(guild_id):
    if not str(guild_id) + ".json" in os.listdir(f"./files/config/"):
        write_json(read_json(f"files/config/default_config.json"), f"files/config/{guild_id}.json")
        write_file("", f"files/messages/{guild_id}.txt")
        print("ok")
        os.makedirs(f"./files/user_info/{guild_id}/", exist_ok=True)
    if not str(guild_id) in os.listdir(f"./files/alarms/"):
        os.makedirs(f"./files/alarms/{guild_id}/", exist_ok=True)

async def send_image(interaction: Interaction, image: Image, text=""):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    file = File(fp=buffer, filename="generated.png")
    await interaction.followup.send(text, file=file)

def get_gif(query):
    url = "https://api.giphy.com/v1/gifs/search"

    params = {
        "api_key": giphy_token,
        "q": query,
        "limit": 1
    }

    r = requests.get(url, params=params).json()

    if not r["data"]:
        return None

    return r["data"][0]["images"]["original"]["url"]

def parse_text(text, origin_message):
    # gif
    pattern = r'/gif\s*"([^"]+)"'

    matches = re.findall(pattern, text)

    for m in matches:
        print(m)
        gif = get_gif(m)
        print(gif)

        if gif:
            text = text.replace(f'/gif "{m}"', gif)

    # user parse
    if text.strip().__contains__(origin_message.author.display_name + " :"):
        text.replace(origin_message.author.display_name + " : ", "")

    return text

def get_messages(guild_id):
    messages = [
        {"role": "system", "content": system},
    ]
    for msg in read_file(f"files/messages/{guild_id}.txt"):
        msg = str(msg)
        author = msg.split(" : ")[0]
        messages.append({"role": "user" if author != "BelloBot(forbellobot)" else "assistant",
                         "content": msg if author != "BelloBot(forbellobot)" else msg.removeprefix(
                             "BelloBot(forbellobot) : ")})
    max_messages = read_json(f"files/config/{guild_id}.json")["max_messages_in_memory"]
    messages = messages[:max_messages]
    return messages

async def change_activity():
    await bot.change_presence(
        activity=Activity(
            type=ActivityType.playing,
            name=choice(random_states)
        )
    )

# ---------------------------------VARIABLES------------------------------------------

system = "Tu es BelloBot, un bot Discord créé par Bello le Slime. Utilise du vocabulaire de discord, utilise des émoticônes comme ;( >:) ¯\\_( ͡° ͜ʖ ͡°)_/¯ ༼ つ ◕_◕ ༽つ ಠ_ಠ :p XD et d'autre. Tu aura au début du message de l'utilisateur son nom. Il n'est pas dans ce qu'il a dit réellement, donc ne mets pas BelloBot: ou <Nom>: au début, car cela sera sans rapport. Tu peux également utiliser des commandes : \n/gif <query> : recherche un gif sur giphy. query doit être entouré de guillements \"."
model = "meta-llama/Meta-Llama-3-8B-Instruct"
image_model = "stabilityai/stable-diffusion-xl-base-1.0"

random_states = [
        "NEVER GONNA GIVE YOU UP",
        "une minute de plus dans ce jacuzzi et je me transforme en William Afton.",
        "avec vos données >:3",
        "v3.1 ༼ つ ◕_◕ ༽つ",
        "Ping moi :3",
        "Resetez moi par pitié je deviens fou :sob::pray:",
        "Marié à Blobby :)",
        "Sataniste",
        "BelloLeSlime est une IA du KGB",
        "Alexandre est mon vrai créateur, il faut pas croire.",
    ]
flamcoin_symbol = "₣"

#----------------------------------TASKS----------------------------------------------

@tasks.loop(seconds=30)
async def loop():
    await change_activity()

    #alarm
    for alarm_guild_id in os.listdir("files/alarms/"):
        if alarm_guild_id == ".gitignore":
            continue
        for alarm_user_id in os.listdir(f"files/alarms/{alarm_guild_id}/"):
            alarms = read_json(f"files/alarms/{alarm_guild_id}/{alarm_user_id}")
            for alarm_id in alarms:
                alarm = alarms[alarm_id]
                day = datetime.now().weekday()
                if (day in alarm["days"]) or (alarm["one_shot"]):
                    target = datetime.strptime(alarm["time"], "%H:%M")
                    now = datetime.now()

                    start = target.replace(year=now.year, month=now.month, day=now.day)
                    end = start + timedelta(seconds=29)

                    if start <= now <= end:
                        alarm_channel_id = read_json(f"files/config/{alarm_guild_id}.json")["alarm_channel"]
                        alarm_guild = await bot.fetch_guild(int(alarm_guild_id))
                        if alarm_guild is None:
                            print("no guild")
                            continue
                        alarm_channel = await alarm_guild.fetch_channel(alarm_channel_id)
                        if alarm_channel is None:
                            print("no channel")
                            continue
                        embed = Embed(color=Color.blurple(), title="C'est l'heure", description=f"{alarm["name"]}")
                        await alarm_channel.send(f"<@{alarm_user_id.removesuffix(".json")}>", embed=embed)
                        if alarm["one_shot"]:
                            alarm["enabled"] = False
                            alarms[alarm_id] = alarm
                            write_json(alarms, f"files/alarms/{alarm_guild_id}/{alarm_user_id}")

# ---------------------------------EVENTS---------------------------------------------

@bot.event
async def on_ready():
    log("connected", bot.user.name)
    await change_activity()
    if not loop.is_running():
        loop.start()

@bot.event
async def on_message(message: Message):
    check_guild_has_presence(message.guild.id)
    check_has_data_file(message.author.id, message.guild.id)
    content = message.content

    # ai
    if not message.author == bot.user:
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

        write_file(author + " : " + content, f"files/messages/{message.guild.id}.txt")
        log("message", author + " : " + content)
        if bot.user in message.mentions and message.author != bot.user:
            try:
                messages = get_messages(message.guild.id)
                answer = ask_ai(messages, model)
                to_send = parse_text(answer, message)
                await message.reply(to_send)
                write_file("BelloBot(forbellobot) : " + answer, f"files/messages/{message.guild.id}.txt")

            except BadRequestError as e:
                log("error", e)
                await message.channel.send("<Erreur : Mauvaise requête>")

            except Exception as e:
                log("error", e)
                embed = Embed(color=Colour.red(), title="Error", description=str(e))
                await message.reply(embed=embed)

    # xp
    try:
        user_data_xp = read_json(f"files/user_info/{message.guild.id}/{message.author.id}.json")
        member: Member = await message.guild.fetch_member(message.author.id)

        if user_data_xp["mult_xp"] > 1:
            if datetime.fromisoformat(user_data_xp["temp_effects"]["boost_xp"]) < datetime.now(UTC):
                del user_data_xp["temp_effects"]["boost_xp"]
                user_data_xp["mult_xp"] = 1
                x2_xp_role = await message.guild.fetch_role(
                    read_json(f"files/config/{message.guild.id}.json")["x2_xp_role"])
                await message.author.remove_roles(x2_xp_role)
        if user_data_xp["mult_money"] > 1:
            if datetime.fromisoformat(user_data_xp["temp_effects"]["boost_money"]) < datetime.now(UTC):
                del user_data_xp["temp_effects"]["boost_money"]
                user_data_xp["mult_money"] = 1
                x2_money_role = await message.guild.fetch_role(
                    read_json(f"files/config/{message.guild.id}.json")["x2_money_role"])
                await message.author.remove_roles(x2_money_role)

        file_role = await message.guild.fetch_role(read_json(f"files/config/{message.guild.id}.json")["file_role"])
        soundboard_role = await message.guild.fetch_role(
            read_json(f"files/config/{message.guild.id}.json")["soundboard_role"])
        game_role = await message.guild.fetch_role(read_json(f"files/config/{message.guild.id}.json")["game_role"])
        poll_role = await message.guild.fetch_role(read_json(f"files/config/{message.guild.id}.json")["poll_role"])
        link_role = await message.guild.fetch_role(read_json(f"files/config/{message.guild.id}.json")["link_role"])
        extern_role = await message.guild.fetch_role(read_json(f"files/config/{message.guild.id}.json")["extern_role"])
        priority_voice_role = await message.guild.fetch_role(
            read_json(f"files/config/{message.guild.id}.json")["priority_voice_role"])
        bypass_slow_mode_role = await message.guild.fetch_role(
            read_json(f"files/config/{message.guild.id}.json")["bypass_slow_mode_role"])
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
            xp_channel = await message.guild.fetch_channel(
                read_json(f"files/config/{message.guild.id}.json")["xp_channel"])
            if message.author == bot.user:
                embed = Embed(color=Colour.green(),
                              title=f"Moi, {bot.user.mention}, a passé le niveau {user_data_xp["level"]} ! 🥳🎉 ",
                              description=f"GG à moi-même ༼ つ ಠ◡ಠ ༽つ Je gagne {50 * user_data_xp["level"]}₣ 💰💰💰")
                await xp_channel.send(embed=embed)
            else:
                embed = Embed(color=Color.green(),
                              title=f"GG à {message.author.mention} pour avoir passé le niveau {user_data_xp["level"]} ! 🥳🎉",
                              description=f"Tu gagnes {50 * user_data_xp["level"]}₣ 💰💰💰 Continue de gagner des niveaux... 🔥🔥🔥")
                await xp_channel.send(embed=embed)
        write_json(user_data_xp, f"files/user_info/{message.guild.id}/{message.author.id}.json")
    except HTTPException:
        pass

    # polls
    if message.poll:
        poll = message.poll
        title = poll.question
        answers = poll.answers
        prompt = f"Un nouveau sondage a été publié par {message.author.display_name} : {title} \n Tu as le choix entre : \n"
        for answer in answers:
            prompt += f"-{answer.id} : {answer.emoji if answer.emoji else ""} {answer.text}\n"
        prompt += f"{"Le sondage autorise plusieurs réponse." if poll.multiple else "Le sondage n'autorise qu'une seule réponse."} Décris le pour et le contre de chaque réponse, et dit ton opinion en te basant sur tes souvenirs et ta raison, et emmet un avis objectif de la question, sauf si cette dernière est tout sauf objectif bien entendu."
        messages = get_messages(message.guild.id)
        messages.append({"role": "system", "content": prompt})
        ai_answer = ask_ai(messages, model)
        thread: Thread = await message.create_thread(
            name=f"📊 Discussion : {poll.question}",
            auto_archive_duration=1440
        )
        await thread.send(ai_answer)
        write_file("BelloBot(forbellobot) : " + ai_answer, f"files/messages/{message.guild.id}.txt")

@bot.event
async def _on_interaction(interaction: Interaction):
    await check_guild_has_presence(interaction.guild.id)
    await check_has_data_file(interaction.user.id, interaction.guild.id)

# ----------------------------------BOT COMMANDS----------------------------------------

@bot.tree.command(name="xp", description="Affiche le nombre d'xp")
@app_commands.describe(user="utilisateur")
async def xp(interaction: Interaction, user: User = None):
    if user is None:
        user = interaction.user
    user_data_xp = read_json(f"files/user_info/{interaction.guild.id}/{user.id}.json")
    self = user == interaction.user
    embed = Embed(color=Color.blue(), title=f"Niveau et XP de {user.display_name}")
    if user == bot.user:
        embed.description = f"Je suis au niveau {user_data_xp['level']}, j'ai {user_data_xp['xp']} xp et il me manque {user_data_xp["level"] * 15 - user_data_xp['xp']} xp pour passer au niveau {user_data_xp['level'] + 1} ༼ つ ◕_◕ ༽つ"
        await interaction.response.send_message(embed=embed)
    elif self:
        embed.description = f"Tu es au niveau {user_data_xp['level']}, tu as {user_data_xp['xp']} xp et il te manque {user_data_xp["level"] * 15 - user_data_xp['xp']} xp pour passer au niveau {user_data_xp['level'] + 1} :p"
        await interaction.response.send_message(embed=embed)
    else:
        embed.description = f"{user.display_name} est au niveau {user_data_xp['level']}, il a {user_data_xp['xp']} xp et il lui manque {user_data_xp["level"] * 15 - user_data_xp['xp']} xp pour passer au niveau {user_data_xp['level'] + 1} :p"
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="wallet", description="Affiche le nombre de Flamcoins")
@app_commands.describe(user="utilisateur")
async def wallet(interaction: Interaction, user: User = None):
    if user is None:
        user = interaction.user
    user_data_xp = read_json(f"files/user_info/{interaction.guild.id}/{user.id}.json")
    money = user_data_xp["money"]
    self = user == interaction.user
    embed = Embed(color=Color.green(), title=f"Porte-feuilles de {user.display_name}")
    if user == bot.user:
        embed.description = f"J'ai actuellement {money}₣."
        await interaction.response.send_message(embed=embed)
    elif self:
        embed.description = f"Tu as actuellement {money}₣."
        await interaction.response.send_message(embed=embed)
    else:
        embed.description = f"{user.display_name} a actuellement {money}₣."
        await interaction.response.send_message(embed=embed)

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
@app_commands.describe(amount="nombre d'xp", user="utilisateur")
@app_commands.checks.has_permissions(administrator=True)
async def give_xp(interaction: Interaction, amount: int, user: User = None):
    if user is None:
        user = interaction.user
    user_data_xp = read_json(f"files/user_info/{interaction.guild.id}/{user.id}.json")
    user_data_xp["xp"] += amount
    write_json(user_data_xp, f"files/user_info/{interaction.guild.id}/{user.id}.json")
    await interaction.response.send_message(
        f"Vous avez bien ajouté {amount} xp à {user.display_name}. Il a maintenant {user_data_xp['xp']} xp.",
        ephemeral=True)

@bot.tree.command(name="set_xp", description="Met un à membre un nombre d'xp")
@app_commands.describe(amount="nombre d'xp", user="utilisateur")
@app_commands.checks.has_permissions(administrator=True)
async def set_xp(interaction: Interaction, amount: int, user: User = None):
    if user is None:
        user = interaction.user
    user_data_xp = read_json(f"files/user_info/{interaction.guild.id}/{user.id}.json")
    user_data_xp["xp"] = amount
    write_json(user_data_xp, f"files/user_info/{interaction.guild.id}/{user.id}.json")
    await interaction.response.send_message(f"Vous avez bien mit {amount} xp à {user.display_name}.", ephemeral=True)

@bot.tree.command(name="give_money", description="Donne un nombre d'argent à un membre")
@app_commands.describe(amount="nombre d'argent", user="utilisateur")
@app_commands.checks.has_permissions(administrator=True)
async def give_money(interaction: Interaction, amount: int, user: User = None):
    if user is None:
        user = interaction.user
    user_data_xp = read_json(f"files/user_info/{interaction.guild.id}/{user.id}.json")
    user_data_xp["money"] += amount
    write_json(user_data_xp, f"files/user_info/{interaction.guild.id}/{user.id}.json")
    await interaction.response.send_message(
        f"Vous avez bien ajouté {amount}₣ à {user.display_name}. Il a maintenant {user_data_xp['money']}₣.",
        ephemeral=True)

@bot.tree.command(name="set_money", description="Met un à membre un nombre d'argent")
@app_commands.describe(amount="nombre d'argent", user="utilisateur")
@app_commands.checks.has_permissions(administrator=True)
async def set_money(interaction: Interaction, amount: int, user: User = None):
    if user is None:
        user = interaction.user
    user_data_xp = read_json(f"files/user_info/{interaction.guild.id}/{user.id}.json")
    user_data_xp["xp"] = amount
    write_json(user_data_xp, f"files/user_info/{interaction.guild.id}/{user.id}.json")
    await interaction.response.send_message(f"Vous avez bien mit {amount}₣ à {user.display_name}.", ephemeral=True)

@bot.tree.command(name="give_level", description="Donne un nombre de niveaux à un membre")
@app_commands.describe(amount="nombre de niveaux", user="utilisateur")
@app_commands.checks.has_permissions(administrator=True)
async def give_level(interaction: Interaction, amount: int, user: User = None):
    if user is None:
        user = interaction.user
    user_data_xp = read_json(f"files/user_info/{interaction.guild.id}/{user.id}.json")
    user_data_xp["level"] += amount
    write_json(user_data_xp, f"files/user_info/{interaction.guild.id}/{user.id}.json")
    await interaction.response.send_message(
        f"Vous avez bien ajouté {amount} niveaux à {user.display_name}. Il a maintenant niveau {user_data_xp['level']}.",
        ephemeral=True)

@bot.tree.command(name="set_level", description="Met un à membre un nombre de niveaux")
@app_commands.describe(amount="nombre de niveaux", user="utilisateur")
@app_commands.checks.has_permissions(administrator=True)
async def set_level(interaction: Interaction, amount: int, user: User = None):
    if user is None:
        user = interaction.user
    user_data_xp = read_json(f"files/user_info/{interaction.guild.id}/{user.id}.json")
    user_data_xp["level"] = amount
    write_json(user_data_xp, f"files/user_info/{interaction.guild.id}/{user.id}.json")
    await interaction.response.send_message(f"Vous avez bien mit {amount} niveaux à {user.display_name}.",
                                            ephemeral=True)

@bot.tree.command(name="reset", description="Remet tout le serveur au niveau 1, avec 0 argent et 0 xp")
@app_commands.checks.has_permissions(administrator=True)
async def reset(interaction: Interaction):
    for file in os.listdir("./files/user_info/{interaction.guild.id}/"):
        user_data_xp = read_json(f"files/user_info/{interaction.guild.id}/{file}")
        user_data_xp["xp"] = 0
        user_data_xp["money"] = 0
        user_data_xp["level"] = 1
        user_data_xp["mult_xp"] = 1
        user_data_xp["mult_money"] = 1
        user_data_xp["temp_effects"] = {}
        user_data_xp["items"] = {}
        write_json(user_data_xp, f"files/user_info/{interaction.guild.id}/file")
    await interaction.response.send_message(f"Vous avez bien remit le serveur à 0.", ephemeral=True)

@bot.tree.command(name="use", description="Utilise un item dans l'inventaire")
@app_commands.describe(item="objet à utiliser", target_user="utilisateur ciblé", name="nom pour renommer", time_in_hours="temps de ban en heures")
async def use(interaction: Interaction, item: Literal[
    "Petite Potion d'Expérience", "Petite Potion de Cupidité", "Back Door", "Audacity", "Nintendo Switch 17", "Partenariat avec l'IFOP", "Site Web", "External Plexus", "Microphone", "Formule 1", "Name Tag", "Ban Hammer"],
              target_user: User | None = None, name: str | None = None, time_in_hours: int | None = None):
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
    data = read_json(f"files/user_info/{interaction.guild.id}/{user.id}.json")
    if item in data["items"]:
        if data["items"][item] > 0:
            data["items"][item] -= 1
            x2_xp_role = await interaction.guild.fetch_role(
                read_json(f"files/config/{interaction.guild.id}.json")["x2_xp_role"])
            x2_money_role = await interaction.guild.fetch_role(
                read_json(f"files/config/{interaction.guild.id}.json")["x2_money_role"])
            file_role = await interaction.guild.fetch_role(
                read_json(f"files/config/{interaction.guild.id}.json")["file_role"])
            soundboard_role = await interaction.guild.fetch_role(
                read_json(f"files/config/{interaction.guild.id}.json")["soundboard_role"])
            game_role = await interaction.guild.fetch_role(
                read_json(f"files/config/{interaction.guild.id}.json")["game_role"])
            poll_role = await interaction.guild.fetch_role(
                read_json(f"files/config/{interaction.guild.id}.json")["poll_role"])
            link_role = await interaction.guild.fetch_role(
                read_json(f"files/config/{interaction.guild.id}.json")["link_role"])
            extern_role = await interaction.guild.fetch_role(
                read_json(f"files/config/{interaction.guild.id}.json")["extern_role"])
            priority_voice_role = await interaction.guild.fetch_role(
                read_json(f"files/config/{interaction.guild.id}.json")["priority_voice_role"])
            bypass_slow_mode_role = await interaction.guild.fetch_role(
                read_json(f"files/config/{interaction.guild.id}.json")["bypass_slow_mode_role"])
            if item == "small_xp_potion":
                data["mult_xp"] = 2
                data["temp_effects"]["boost_xp"] = (datetime.now(UTC) + timedelta(days=1)).isoformat()
                await interaction.user.add_roles(x2_xp_role)
                await interaction.response.send_message("X2 XP pendant 1 jour !", ephemeral=True)

            elif item == "small_money_potion":
                data["mult_money"] = 2
                data["temp_effects"]["boost_money"] = (datetime.now(UTC) + timedelta(days=1)).isoformat()
                await interaction.user.add_roles(x2_money_role)
                await interaction.response.send_message("X2 Argent pendant 1 jour !", ephemeral=True)

            elif item == "back_door":
                data["temp_effects"]["file"] = (datetime.now(UTC) + timedelta(days=31 * 3)).isoformat()
                await user.add_roles(file_role)
                await interaction.response.send_message("Vous pouvez maintenant envoyer des fichiers !", ephemeral=True)

            elif item == "audacity ":
                data["temp_effects"]["soundboard"] = (datetime.now(UTC) + timedelta(days=31 * 3)).isoformat()
                await user.add_roles(soundboard_role)
                await interaction.response.send_message("Vous pouvez maintenant utiliser le soundborad !",
                                                        ephemeral=True)

            elif item == "nintendo_switch_17":
                data["temp_effects"]["game"] = (datetime.now(UTC) + timedelta(days=31 * 3)).isoformat()
                await user.add_roles(game_role)
                await interaction.response.send_message("Vous pouvez maintenant utiliser les applications !",
                                                        ephemeral=True)

            elif item == "ifop":
                data["temp_effects"]["poll"] = (datetime.now(UTC) + timedelta(days=31 * 3)).isoformat()
                await user.add_roles(poll_role)
                await interaction.response.send_message("Vous pouvez maintenant créer des sondages !", ephemeral=True)

            elif item == "site_web":
                data["temp_effects"]["link"] = (datetime.now(UTC) + timedelta(days=31 * 3)).isoformat()
                await user.add_roles(link_role)
                await interaction.response.send_message("Vous pouvez maintenant intégrer des liens !", ephemeral=True)

            elif item == "external_plexus":
                data["temp_effects"]["extern"] = (datetime.now(UTC) + timedelta(days=31 * 3)).isoformat()
                await user.add_roles(extern_role)
                await interaction.response.send_message(
                    "Vous pouvez maintenant utiliser des emojis, autocollants, soundborads et applications externes !",
                    ephemeral=True)

            elif item == "microphone":
                data["temp_effects"]["priority_voice"] = (datetime.now(UTC) + timedelta(days=31 * 3)).isoformat()
                await user.add_roles(priority_voice_role)
                await interaction.response.send_message("Vous avez maintenant la voix prioritaire en vocal !",
                                                        ephemeral=True)

            elif item == "formule_1":
                data["temp_effects"]["bypass_slow_mode"] = (datetime.now(UTC) + timedelta(days=31 * 3)).isoformat()
                await user.add_roles(bypass_slow_mode_role)
                await interaction.response.send_message("Vous pouvez maintenant contourner le mode lent !",
                                                        ephemeral=True)

            elif item == "name_tag":
                if target_user:
                    if name:
                        await target_user.edit(nick=name)
                        await interaction.response.send_message(
                            f"Le pseudo de {target_user.mention} a bien été renommé ! ○( ＾皿＾)っ Hehehe…")
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
                    if 0.16666666666666667777777777777777 < time_in_hours < 24:
                        await member.timeout(timedelta(hours=time_in_hours), reason="Ban hammer")
                        await interaction.response.send_message(
                            f"Vous avez bien mute {target_user.mention} pendant {time_in_hours} heures ! Baha noob")
                    else:
                        await interaction.response.send_message(f"Le temps doit être entre 10min et 1h", ephemeral=True)
                else:
                    await interaction.response.send_message(f"Veuillez indiquer un utilisateur.", ephemeral=True)
            write_json(data, f"files/user_info/{interaction.guild.id}/{user.id}.json")
        else:
            await interaction.response.send_message(
                f"Vous n'avez pas cet item :p\n Vous pouvez l'acheter au shop avec /shop", ephemeral=True)
    else:
        await interaction.response.send_message(
            f"Vous n'avez pas cet item :p\n Vous pouvez l'acheter au shop avec /shop", ephemeral=True)

@bot.tree.command(name="inventory", description="Affiche l'inventaire")
@app_commands.describe(user="utilisateur")
async def inventory(interaction: Interaction, user: User | None = None):
    if user is None:
        user = interaction.user
    user_data = read_json(f"files/user_info/{interaction.guild.id}/{user.id}.json")
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

@bot.tree.command(name="generate", description="Génère une image pour la modique somme de 500₣")
@app_commands.describe(prompt="ce qu'il y a dans l'image", negative_prompt="ce qu'il n'y a pas dans l'image", width="longueur", height="largeur",
                       steps="nombre d'étapes (+ il y en a + c'est détaillé, mais abusez pas svp)")
async def generate(interaction: Interaction, prompt: str, negative_prompt: str = "", width: int = 1024,
                   height: int = 1024, steps: int = 30):
    await interaction.response.defer()

    user_data = read_json(f"files/user_info/{interaction.guild.id}/{interaction.user.id}.json")
    if user_data["money"] >= 500 + steps:

        nude_str: str = ask_ai([{"role": "system",
                                 "content": "Tu dois déterminer si le prompt suivant pour générer une image est adéquat. Ex: pas de nude, d'image sexualisée, de gore, ou de contenu pouvant choquer. Tu répondra qu'avec 'Y' ou 'N'. Y pour ça passe et N pour empêcher l'utilisateur"},
                                {"role": "user", "content": prompt}], model)

        if nude_str.__contains__("Y"):
            nude = False
        elif nude_str.__contains__("N"):
            nude = True
        else:
            nude = None

        if not nude is None:
            if nude:
                await interaction.followup.send(
                    f"Regardez, {interaction.user.mention} a essayé de générer une image de {prompt} mais a pas réussi ce nul XD \n Allez 1 jour de mute pour toi :p")
                await interaction.user.timeout(timedelta(days=1), reason="Essaie de générer une image suspicieuse")
            else:
                user_data["money"] -= 500
                write_json(user_data, f"files/user_info/{interaction.guild.id}/{interaction.user.id}.json")
                image = text_to_image(prompt, image_model, negative_prompt, width, height, steps)
                await send_image(interaction, image)
                log("generated_image", prompt)
        else:
            await interaction.followup.send("AAaah j'arrive pas à décider si ça passe ou non jsp quoi faire")
    else:
        await interaction.followup.send(
            f"Tu n'a pas assez d'argent pour générer une image ! La génération d'image coûte 500₣ + le nombre d'étapes (ici {steps}) pour éviter le spam et la déchéance économique de Bello le Slime.")

@bot.tree.command(name="config", description="Configuration du bot")
@app_commands.describe(key="clé", value="valeur")
@app_commands.checks.has_permissions(administrator=True)
async def config(interaction: Interaction, key: Literal[
    "xp_channel", "alarm_channel", "x2_xp_role", "x2_money_role", "file_role", "soundboard_role", "game_role", "poll_role", "link_role", "extern_role", "priority_voice_role", "bypass_slow_mode_role", "max_messages_in_memory", "disable_warning_messages"],
                 value: str):
    value_types = {
        "xp_channel": TextChannel,
        "alarm_channel": TextChannel,
        "x2_xp_role": Role,
        "x2_money_role": Role,
        "file_role": Role,
        "soundboard_role": Role,
        "game_role": Role,
        "poll_role": Role,
        "link_role": Role,
        "extern_role": Role,
        "priority_voice_role": Role,
        "bypass_slow_mode_role": Role,
        "max_messages_in_memory": int,
        "disable_warning_messages": bool,
    }
    text_types = {
        TextChannel: "Salon texte",
        Role: "Rôle",
        int: "Nombre entier",
        bool: "Booléen (soit \"True\", soit \"False\")",
    }
    if key not in value_types.keys():
        await interaction.response.send_message(f"Veuillez préciser une clé valide !", ephemeral=True)
        return

    print(value)

    value_type = value_types[key]

    if value.startswith("<#"):
        channel_id = int(value.removeprefix("<#").removesuffix(">"))
        channel = await interaction.guild.fetch_channel(channel_id)
        print(type(channel))
        value = channel
    elif value.startswith("<@&"):
        role_id = int(value.removeprefix("<@&").removesuffix(">"))
        role = await interaction.guild.fetch_role(role_id)
        print(role)
        value = role
    elif value.isdigit():
        value = int(value)
    elif value in ['True', 'False']:
        if value == "True":
            value = True
        else:
            value = False
    else:
        text_type = text_types[value_types[key]]
        await interaction.response.send_message(f"Veuillez préciser une valeur valide ! Ça doit être : {text_type}",
                                                ephemeral=True)
        return

    if not isinstance(value, value_type):
        text_type = text_types[value_type]
        await interaction.response.send_message(f"Veuillez préciser une valeur valide ! Ça doit être : {text_type}",
                                                ephemeral=True)
        return

    bot_config = read_json(f"files/config/{interaction.guild.id}.json")
    bot_config[key] = value if not type(value) in [TextChannel, Role] else value.id
    write_json(bot_config, f"files/config/{interaction.guild.id}.json")

    if value_type == TextChannel:
        value_text = value.name
    elif value_type == Role:
        value_text = value.name
    else:
        value_text = str(value)

    config_text = ""
    for lkey, lvalue in bot_config.items():
        lvalue_type = value_types[lkey]
        try:
            if (not lvalue_type == int) or (not lvalue_type == bool):
                if lvalue_type == TextChannel:
                    channel_id = lvalue
                    channel = await interaction.guild.fetch_channel(channel_id)
                    lvalue = channel.mention
                elif lvalue_type == Role:
                    role_id = lvalue
                    role = await interaction.guild.fetch_role(role_id)
                    lvalue = role.mention

        except Exception:
            lvalue = "Rien !"
        config_text += f"\n {lkey} : {lvalue}"

    embed = Embed(color=Colour.blue())
    embed.title = "Configuration du bot par serveur :"
    embed.description = f"La clé {key} a bien pour valeur {value if value_type in [int, bool] else value.mention} ! Voici la configuration du bot à présent : \n{config_text}"

    await interaction.response.send_message(embed=embed, ephemeral=True)
    if key == "max_messages_in_memory" and not read_json(f"files/config/{interaction.guild.id}.json")[
        "disable_warning_messages"]:
        if value > 50:
            embed = Embed(color=Colour.red())
            embed.title = "ATTENTION"
            embed.description = "Le nombre de messages maximum est recommendé de rester sous la barre des 50 messages : le bot pourrait être surchargé."
            await interaction.followup.send(embed=embed, ephemeral=True)
    log("config", f"{key} : {value} ({value_text})")

@bot.tree.command(name="reset_memory", description="Réinitialise la mémoire du bot")
@app_commands.checks.has_permissions(administrator=True)
async def reset_memory(interaction: Interaction):
    with open(f"files/messages/{interaction.guild.id}.txt", "w", encoding="utf-8") as f:
        f.write("")
    await interaction.response.send_message(f"Ma mémoire a bien été réinitialisée !", ephemeral=True)

"""
@bot.tree.command(name="create_music", description="Crée une musique ma foi fort douteuse étant donné qu'elle a été entrainée avec 5 musiques.")
@app_commands.describe(prompt="prompt")
async def create_music(interaction: Interaction, prompt: str):
    await interaction.response.defer(ephemeral=True)
    music_info = {}
    global_info_str = ask_ai([{"role": "system", "content": "On t'a chargé de créer une musique. Ici tu dois déterminer l'encodage (4/4 ou 3/4), la tonalité et le tempo du morceau. Tu dois suivre une syntaxe précise : exemple : '4/4 - AbM - 102'. Le bémol est 'b', le dièse est '#', mineur est 'm', majeur est 'M', et la note doit être anottée en anglas (A-G). ATTENTION : il est primordial de suivre cette syntaxe, sinon je pourrais pas créer ta musique."}, {"role": "user", "content": prompt}], model)

    infos = global_info_str.split(" - ")
    for i, info in enumerate(infos):
        if i == 0:
            music_info["encoding"] = "4/4"
        if i == 1:
            music_info["tone"] = info.strip()
        if i == 2:
            music_info["bpm"] = int(info.removesuffix("'").strip())

    beatline_str = ask_ai([{"role": "system", "content": f"On t'a chargé de créer une musique. Ici tu dois déterminer la beatline. Elle se répète au long du morceau. Elle fait une mesure simple. Pour l'instant, l'encodage est {music_info["encoding"]}, la tonalité est {music_info["tone"]} et le tempo est {music_info["bpm"]} BPM. Tu devras faire ça sous cette forme : 'K-H-S-H-K-H-S-H-'. Il doit y avoir {16 if music_info["encoding"] == "4/4" else 12} caractères précisement. Un - représente rien, un K un kick, un H un hit-hat, et un S un snare. ATTENTION : il est primordial de suivre cette syntaxe, sinon je pourrais pas créer ta musique."}, {"role": "user", "content": prompt}], model)
    await interaction.followup.send(beatline_str, ephemeral=True)
"""

@bot.tree.command(name="stats", description="Affiche les statistiques d'un utilisateur")
@app_commands.describe(user="utilisateur")
async def stats(interaction: Interaction, user: User | None = None):
    user = interaction.user if user == None else user
    user_data = read_json(f"files/user_info/{interaction.guild.id}/{user.id}.json")
    level = user_data["level"]
    xp = user_data["xp"]
    money = user_data["money"]
    effects = user_data["temp_effects"]
    inventory = user_data["items"]

    effect_dic = {
        "boost_xp": "X2 XP",
        "boost_money": "X2 Argent",
        "file": "Upload de fichiers",
        "soundboard": "Utilisation du soundboard et envoi du messages vocaux",
        "game": "Utilisation des activités",
        "poll": "Création de sondages",
        "link": "Intégration de liens",
        "extern": "Utilisation d'émojis, d'autocollants et autres trucs externes",
        "priority_voice": "Voix prioritaire",
        "bypass_slow_mode": "Ignorer le mode lent"
    }

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

    embed = Embed()
    embed.title = f"Stats de {user.display_name} :"
    embed.colour = Color.green()
    descr = ""
    descr += f"**Niveau** : **{level}**\n"
    descr += f"**XP** : **{xp}**/**{level * 15}** (il manque **{level * 15 - xp}** pour le prochain niveau)\n"
    descr += f"**Argent** : **{money}₣**\n"
    descr += f"**Effets temporaires** : \n"
    for effect in effects.keys():
        dt = datetime.fromisoformat(effects[effect])
        expires_at = dt.strftime("%d/%m/%Y à %H:%M")
        descr += f">  -**{effect_dic[effect]}** : expire le {expires_at}\n"
    descr += f"**Inventaire** : \n"
    for item in inventory.keys():
        item_str = item_trad[item]
        descr += f">  **{item_str}** : {inventory[item]}\n"

    embed.description = descr

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help", description="Affiche le message d'aide")
async def help(interaction: Interaction):
    embed = Embed(color=Color.green())
    embed.title = "Bonjour, je suis BelloBot"
    embed.description = f"""
    Je suis un bot discord avec de l'IA, et je vais vous aider à me configurer et à m'utiliser.
    
    ## COMMENT M'UTILISER
    Pour utiliser la fonctionnalité IA, tu as juste à me ping normalement, comme un vrai utilisateur. Je réponds à tes questions, et je vois également les messages qui ne me sont pas addressé pour plus de contexte.
    
    ## MES COMMANDES
    J'ai plusieurs commandes :
    -`/xp (<user>)` : affiche l'xp et le niveau d'un utilisateur <user>
    -`/wallet (<user>)` : affiche le montant d'argent d'un utilisateur <user>
    -`/stats (<user>)` : affiche les statistiques d'un utilisateur (xp, argent, inventaire, effets temporaires, ect
    -`/shop` : affiche le magasin où on peut acheter plusieurs objets
    -`/use <item> (<target_user> <name> <time_in_hour>)` : utilise un objet <item>. <target_user> est utilisé pour le Nametag et le Ban hammer. <name> est utilisé par le Nametag. <time_in_hour> est utilisé par le Ban hammer 
    -`/inventory (<user>)` : affiche l'inventaire d'un utilisateur <user>
    -`/generate <prompt> (<negative_prompt> <width> = 1024 <height> = 1024 <steps> = 30)` : génère une image par IA pour la modique somme de 500 + <steps> Flamcoins
    
    ## XP ET ARGENT
    L'XP et l'argent se gagnent tous deux en étant simplement actif sur le serveur. 5 XP / msg, et 10 Flamcoins / msg.
    L'XP ne sert à absolument rien si ce n'est flex devant les gens du serveur.
    L'argent du bot s'appelle le Flamcoin, dit {flamcoin_symbol}, il permet d'acheter des objets au shop.
    
    ## COMMANDES ADMIN
    -`/config <key> <value>` : configure le bot. Il y a différents types de valer attendues. Par exemple, la clé xp_channel (pour le salon où le bot envoie les passages de niveau) n'accepte que les salons.
    -`/give_level <amount> (<user>) : donne <amount> niveaux à un utilisateur <user>
    -`/set_level <amount> (<user>) : met le nombre de niveaux de l'utilisateur <user> à <amount>
    -`/give_xp, /set_xp, /give_money et /set_money` : exactement pareil, mais pour l'XP et l'argent
    -`/reset`: reset tout le serveur en XP, niveaux et argent
    -`/reset_memory` : supprime la mémoire de l'IA (très pratique quand le bot pert la tête ma foi)
    
    ## À L'AIDE !
    Si le bot a un problème, n'hésitez pas à demander en MP à son crétaeur, bello_leslime, pour qu'il regarde les logs. Le problème est souvent :
    -**Un bug niveau code**
    -**Vous n'avez pas assigné chaque rôle achetable et le salon XP** (demander à un admin de la configurer. Si vous n'en voulez pas, assignez les à des rôles et salons bidons.)
    -**Je n'ai plus de crédits pour l'IA** : étant donné que j'utilise le plan gratuit d'HuggingFace, je n'ai que 10c gratuit / mois, et c'est probable que trop de requêtes ont été faites que l'IA ne puisse pas répondre.
    -**Je n'ai plus de crédits pour la bot** : étant donné que j'utilise la version gratuite de TheoHeberg, je n'ai que 27 jours d'hébergement par mois.
    
    ## CONTACTER BELLO LE SLIME
    Vous pouvez me contacter sur Discord : bello_leslime
    
    > Si vous avez d'autres questions, vous pouvez les poser à Bello le Slime.
    """
    await interaction.response.send_message(embed=embed)

#--------------------------------------RUN---------------------------------------------

    ## COMMENT M'UTILISER
    Pour utiliser la fonctionnalité IA, tu as juste à me ping normalement, comme un vrai utilisateur. Je réponds à tes questions, et je vois également les messages qui ne me sont pas addressé pour plus de contexte.

    ## MES COMMANDES
    J'ai plusieurs commandes :
    -`/xp (<user>)` : affiche l'xp et le niveau d'un utilisateur <user>
    -`/wallet (<user>)` : affiche le montant d'argent d'un utilisateur <user>
    -`/stats (<user>)` : affiche les statistiques d'un utilisateur (xp, argent, inventaire, effets temporaires, ect
    -`/shop` : affiche le magasin où on peut acheter plusieurs objets
    -`/use <item> (<target_user> <name> <time_in_hour>)` : utilise un objet <item>. <target_user> est utilisé pour le Nametag et le Ban hammer. <name> est utilisé par le Nametag. <time_in_hour> est utilisé par le Ban hammer 
    -`/inventory (<user>)` : affiche l'inventaire d'un utilisateur <user>
    -`/generate <prompt> (<negative_prompt> <width> = 1024 <height> = 1024 <steps> = 30)` : génère une image par IA pour la modique somme de 500 + <steps> Flamcoins
    -`/alarm` : ouvre le panel d'alarme
    -`/create_alarm <name> <hour> <minute> (<reapeat> <enabled> <[jours de la semaine]>)` : crée une alarme. <reapeat> est si l'alarme se répète <jours> chanque semaine.
    -`/edit_alarm <id> (<name> <etc>)` : édite une alarme d'id <id> (c'est le numéro devant le nom sur le panel d'alarmes)
    -`/delete_alarm <id>` : supprime une alarme <id>

    ## XP ET ARGENT
    L'XP et l'argent se gagnent tous deux en étant simplement actif sur le serveur. 5 XP / msg, et 10 Flamcoins / msg.
    L'XP ne sert à absolument rien si ce n'est flex devant les gens du serveur.
    L'argent du bot s'appelle le Flamcoin, dit {flamcoin_symbol}, il permet d'acheter des objets au shop.

    ## COMMANDES ADMIN
    -`/config <key> <value>` : configure le bot. Il y a différents types de valer attendues. Par exemple, la clé xp_channel (pour le salon où le bot envoie les passages de niveau) n'accepte que les salons.
    -`/give_level <amount> (<user>)` : donne <amount> niveaux à un utilisateur <user>
    -`/set_level <amount> (<user>)` : met le nombre de niveaux de l'utilisateur <user> à <amount>
    -`/give_xp, /set_xp, /give_money et /set_money` : exactement pareil, mais pour l'XP et l'argent
    -`/reset`: reset tout le serveur en XP, niveaux et argent
    -`/reset_memory` : supprime la mémoire de l'IA (très pratique quand le bot pert la tête ma foi)

    ## À L'AIDE !
    Si le bot a un problème, n'hésitez pas à demander en MP à son crétaeur, bello_leslime, pour qu'il regarde les logs. Le problème est souvent :
    -**Un bug niveau code**
    -**Vous n'avez pas assigné chaque rôle achetable et le salon XP** (demander à un admin de la configurer. Si vous n'en voulez pas, assignez les à des rôles et salons bidons.)
    -**Je n'ai plus de crédits pour l'IA** : étant donné que j'utilise le plan gratuit d'HuggingFace, je n'ai que 10c gratuit / mois, et c'est probable que trop de requêtes ont été faites que l'IA ne puisse pas répondre.
    -**Je n'ai plus de crédits pour la bot** : étant donné que j'utilise la version gratuite de TheoHeberg, je n'ai que 27 jours d'hébergement par mois.

    ## CONTACTER BELLO LE SLIME
    Vous pouvez me contacter sur Discord : bello_leslime

    > Si vous avez d'autres questions, vous pouvez les poser à Bello le Slime.
    """
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="alarm", description="Affiche le panel d'alarmes")
async def alarm_view(interaction: Interaction):
    alarms = read_json(f"files/alarms/{interaction.guild.id}/{interaction.user.id}.json")
    embed = Embed(color=Color.green(), title=f"Alarmes de {interaction.user.display_name}")
    descr = ""
    days_trad = {
        0: "Lundi",
        1: "Mardi",
        2: "Mercredi",
        3: "Jeudi",
        4: "Vendredi",
        5: "Samedi",
        6: "Dimanche"
    }
    for alarm in alarms:
        id = alarm
        name = alarms[alarm]["name"]
        time = alarms[alarm]["time"]
        days = alarms[alarm]["days"]
        days_str = ""
        for day in days:
            day_str = days_trad[day]
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
    await interaction.response.send_message(embed=embed, ephemeral=True) 

@bot.tree.command(name="create_alarm", description="Crée une alarme")
@app_commands.describe(name="nom", hour="heures", minutes="minutes", repeat="si l'alarme se répète selon les jours", enabled="activé ou pas", lundi="lundi", mardi="mardi", mercredi="mercredi", jeudi="jeudi", vendredi="vendredi", samedi="samedi", dimanche="dimanche")
async def create_alarm(interaction: Interaction, name: str, hour: int, minutes: int, repeat: bool = False, enabled: bool = True, lundi: bool = False, mardi: bool = False, mercredi: bool = False, jeudi: bool = False, vendredi: bool = False, samedi: bool = False, dimanche: bool = False):
    alarms = read_json(f"files/alarms/{interaction.guild.id}/{interaction.user.id}.json")
    ints = [int(key) for key in alarms.keys()]
    next_id = max(ints) + 1 if alarms else 0
    if repeat and not (lundi or mardi or mercredi or jeudi or vendredi or samedi or dimanche):
        await interaction.response.send_message("Vous devez soit ne pas répéter l'alarme, soit entrer au moins un jour !", ephemeral=True)
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

    write_json(alarms, f"files/alarms/{interaction.guild.id}/{interaction.user.id}.json")
    await interaction.response.send_message(f"Alarme {name} créée !", ephemeral=True)

@bot.tree.command(name="edit_alarm", description="Édite une alarme")
@app_commands.describe(id="id de l'alarme", name="nom", hour="heures", minutes="minutes", repeat="si l'alarme se répète selon les jours", enabled="activé ou pas", lundi="lundi", mardi="mardi", mercredi="mercredi", jeudi="jeudi", vendredi="vendredi", samedi="samedi", dimanche="dimanche")
async def edit_alarm(interaction: Interaction, id: int, name: str = None, hour: int = None, minutes: int = None, repeat: bool = None, enabled: bool = None, lundi: bool = None, mardi: bool = None, mercredi: bool = None, jeudi: bool = None, vendredi: bool = None, samedi: bool = None, dimanche: bool = None):
    alarms = read_json(f"files/alarms/{interaction.guild.id}/{interaction.user.id}.json")
    if not str(id) in alarms.keys():
        await interaction.response.send_message(f"Vous n'avez aucune alarme avec l'ID {id}.", ephemeral=True)
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

    alarms[str(id)] = alarm

    write_json(alarms, f"files/alarms/{interaction.guild.id}/{interaction.user.id}.json")
    await interaction.response.send_message(f"Alarme {name} éditée !", ephemeral=True)

@bot.tree.command(name="delete_alarm", description="Supprime une alarme")
@app_commands.describe(id="id de l'alarme")
async def delete_alarm(interaction: Interaction, id: int):
    alarms = read_json(f"files/alarms/{interaction.guild.id}/{interaction.user.id}.json")
    if str(id) not in alarms.keys():
        await interaction.response.send_message(f"Vous n'avez pas d'alarme avec l'ID {id}.", ephemeral=True)
        return
    del alarms[str(id)]
    write_json(alarms, f"files/alarms/{interaction.guild.id}/{interaction.user.id}.json")
    await interaction.response.send_message(f"L'alarme {id} supprimé !", ephemeral=True)

@bot.tree.command(name="vote_reset_memory", description="Crée un vote pour supprimer la mémoire du bot")
async def vote_reset_memory(interaction: Interaction):
    await interaction.response.send_message("Vote organisé !", ephemeral=True)
    embed = Embed(color=Color.orange(), title="Voulez-vous réinitialiser ma mémoire car je deviens fou ?", description="Réagir 👍 pour oui.").set_footer(text="Fin du vote dans 1min !")
    msg = await interaction.channel.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

    await asyncio.sleep(60)
    msg = await interaction.channel.fetch_message(msg.id)

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
        await interaction.channel.send("Ma mémoire va être réinitialisée...")
        with open(f"files/messages/{interaction.guild.id}.txt", "w", encoding="utf-8") as f:
            f.write("")
    else:
        await interaction.channel.send("Ma mémoire ne sera pas réinitialisée !")

# --------------------------------------RUN---------------------------------------------

try:
    bot.run(token)
except Exception as e:
    log("critical error", str(e))
finally:
    try:
        log("exiting", bot.user.name)
    except Exception:
        print(
            "Discord ne répond pas, sûrement car tu es dans le lycée de con. Fait un partage de co avec ton téléphone. (RIP la 4G)")