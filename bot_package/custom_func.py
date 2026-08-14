#import stuff
import json
import os
import discord
from discord.ext import commands
from google import genai
from google.genai import types
from google.genai import errors
from bot_package.data import AI_TOKEN, GIPHY_TOKEN, model, system, flamcoin_symbol
import io
import requests
import re
from datetime import datetime, UTC, timedelta
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup

#------------------------------------------------------------FILE MANAGEMENT

def write_file(message, path):
    """
    Adds a message to a txt file
    :param message: String message
    :param path: Path to the file
    :return:
    """
    message = message.replace("\n", " ")
    with open(path, "a", encoding="utf-8") as file:
        file.write(message + "\n")

def read_file(path):
    """
    Reads a txt file
    :param path: Path to the file
    :return:
    """
    lines = []
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            lines.append(line)
    return lines

def write_json(data, path):
    """
    Writes a json file
    :param data: Dictionary to write
    :param path: Path to the file
    :return:
    """
    with open(path, "w", encoding="utf-8") as file:
        file.write(json.dumps(data, indent=2))

def read_json(path):
    """
    Reads a json file
    :param path: Path to da file
    :return:
    """
    with open(path, "r", encoding="utf-8") as file:
        data = json.loads(file.read())
        return data

#------------------------------------------------------------AI STUFF

async def ask_ai(prompt: str, user: str = None, guild: int = None, no_memory = False, dm = False) -> str:
    """
    Uses the Google AI Studio API to ask something to an AI model
    :param prompt: Question to ask
    :param user: User's Display Name for better understanding for the AI
    :param guild: Guild ID to read the message file
    :param no_memory: If the memory is disabled
    :param dm: If the chat is in DMs
    :return:
    """
    client = genai.Client(api_key=AI_TOKEN)
    if not no_memory:
        if not dm:
            messages = get_messages(guild)
            if messages[:-1] == prompt:
                messages.pop()
            remembers = get_remembers(guild)
            system_str = system
            for remember in remembers:
                system_str += " \n" + remembers[remember]

            chat = client.chats.create(
                model=model,
                history=messages,
                config=types.GenerateContentConfig(
                    system_instruction=system_str
                )
            )

            response = chat.send_message(f"{user} : {prompt}")
            answer = response.text
            write_file(f"BelloBot(forbellobot) : {answer}", f"files/messages/{guild}.txt")
            return answer
        else:
            messages = get_dm(guild)
            if messages[:-1] == prompt:
                messages.pop()
            system_str = system

            chat = client.chats.create(
                model=model,
                history=messages,
                config=types.GenerateContentConfig(
                    system_instruction=system_str
                )
            )

            response = chat.send_message(f"{user} : {prompt}")
            answer = response.text
            write_file(f"BelloBot(forbellobot) : {answer}", f"files/dms/{guild}.txt")
            return answer

    else:
        chat = client.chats.create(
            model=model,
        )

        response = chat.send_message(prompt)
        answer = response.text
        return answer

def text_to_image(prompt, model, negative_prompt, width=1024, height=1024, steps=30):
    """
    Turns text into image via AI
    :param prompt: Description of the wanted image
    :param model: Model of the AI
    :param negative_prompt: What there isnt in the image
    :param width: Width of the image
    :param height: Height of the image
    :param steps: Steps = quality of the image
    :return:
    """
    pass

#------------------------------------------------------------ECONOMY MANAGEMENT

def add_item(guild_id: int, user_id: int, item: str):
    """
    Adds an item to a user
    :param guild_id: Guild ID
    :param user_id: User ID
    :param item: Item ID to give
    :return:
    """
    data = get_user_data(user_id, guild_id)
    data["items"][item] = data["items"][item] + 1 if item in data["items"] else 1
    set_user_data(user_id, guild_id, data)

#------------------------------------------------------------CHECKS

def check_has_data_file(user_id, guild_id):
    """
    Checks if each file in the user's files is there: if not, creates it
    :param user_id: User ID
    :param guild_id: Guild ID
    :return:
    """
    if not str(guild_id) in os.listdir("files/user_info/"):
        os.makedirs(f"files/user_info/{guild_id}")
    try:
        if not str(user_id) + ".json" in os.listdir(f"files/user_info/{guild_id}/"):
            write_json(read_json("files/user_info/default.json"),
                       f"files/user_info/{guild_id}/{user_id}.json")
    except:
        pass
    try:
        if not str(user_id) + ".json" in os.listdir(f"files/alarms/{guild_id}/"):
            write_json({}, f"files/alarms/{guild_id}/{user_id}.json")
    except:
        pass
    if not str(user_id) + ".json" in os.listdir(f"files/slimania_inventory/{guild_id}/"):
        write_json({
            "last_roll": 0,
            "inventory": {}
        },
        f"files/slimania_inventory/{guild_id}/{user_id}.json")

def check_guild_has_presence(guild_id):
    """
    Checks if each file in the guild's files is there: if not, creates it
    :param guild_id: Guild ID
    :return:
    """
    if not str(guild_id) + ".json" in os.listdir(f"./files/config/"):
        write_json(read_json(f"files/config/default_config.json"), f"files/config/{guild_id}.json")
    if not str(guild_id) + ".txt" in os.listdir(f"./files/messages/"):
        write_file("", f"files/messages/{guild_id}.txt")
    if not str(guild_id) + ".json" in os.listdir(f"./files/remembers/"):
        write_json({}, f"files/remembers/{guild_id}.json")
    if not str(guild_id) in os.listdir("./files/user_info/"):
        os.makedirs(f"./files/user_info/{guild_id}/", exist_ok=True)
    if not str(guild_id) in os.listdir(f"./files/alarms/"):
        os.makedirs(f"./files/alarms/{guild_id}/", exist_ok=True)
    if not str(guild_id) in os.listdir(f"./files/slimania_inventory/"):
        os.makedirs(f"./files/slimania_inventory/{guild_id}/", exist_ok=True)
    if not str(guild_id) + ".json" in os.listdir(f"./files/shop/"):
        write_json(read_json(f"files/shop/default.json"), f"files/shop/{guild_id}.json")

#------------------------------------------------------------GET AND SET DATA

def get_user_data(user_id, guild_id):
    check_guild_has_presence(guild_id)
    check_has_data_file(user_id, guild_id)
    return read_json(f"files/user_info/{guild_id}/{user_id}.json")

def set_user_data(user_id, guild_id, data):
    check_guild_has_presence(guild_id)
    check_has_data_file(user_id, guild_id)
    write_json(data, f"files/user_info/{guild_id}/{user_id}.json")

def get_config(guild_id):
    check_guild_has_presence(guild_id)
    return read_json(f"files/config/{guild_id}.json")

def set_config(guild_id, data):
    check_guild_has_presence(guild_id)
    write_json(data, f"files/config/{guild_id}.json")

def get_alarms(user_id, guild_id):
    check_guild_has_presence(guild_id)
    check_has_data_file(user_id, guild_id)
    return read_json(f"files/alarms/{guild_id}/{user_id}.json")

def set_alarms(user_id, guild_id, data):
    check_guild_has_presence(guild_id)
    check_has_data_file(user_id, guild_id)
    write_json(data, f"files/alarms/{guild_id}/{user_id}.json")

def get_remembers(guild_id):
    check_guild_has_presence(guild_id)
    return read_json(f"files/remembers/{guild_id}.json")

def set_remembers(guild_id, data):
    check_guild_has_presence(guild_id)
    write_json(data, f"files/remembers/{guild_id}.json")

def get_slime_list():
    return read_json("files/slime_list.json")

def get_slime_per_rank():
    return read_json("files/slime_per_rank.json")

def get_slimania_inventory(user_id, guild_id):
    check_guild_has_presence(guild_id)
    check_has_data_file(user_id, guild_id)
    return read_json(f"files/slimania_inventory/{guild_id}/{user_id}.json")

def set_slimania_inventory(user_id, guild_id, data):
    check_guild_has_presence(guild_id)
    check_has_data_file(user_id, guild_id)
    write_json(data, f"files/slimania_inventory/{guild_id}/{user_id}.json")

def get_messages(guild_id):
    messages = []
    for msg in read_file(f"files/messages/{guild_id}.txt"):
        msg = str(msg)
        author = msg.split(" : ")[0]
        messages.append({"role": "user" if author != "BelloBot(forbellobot)" else "model",
                         "parts": [{"text": msg if author != "BelloBot(forbellobot)" else msg.removeprefix(
                             "BelloBot(forbellobot) : ")}]})
    max_messages = read_json(f"files/config/{guild_id}.json")["max_messages_in_memory"]
    messages = messages[-max_messages:]
    return messages

def get_dm(user_id: int):
    messages = []
    for msg in read_file(f"files/dms/{user_id}.txt"):
        if msg == "\n":
            continue
        split = msg.split(" : ")
        author = split[0]
        messages.append({"role": "user" if author != "BelloBot(forbellobot)" else "model",
                         "parts": [{"text": split[1]}]})
        messages = messages[-50:]
    return messages

def get_shop(guild_id):
    check_guild_has_presence(guild_id)
    return read_json(f"files/shop/{guild_id}.json")

def set_shop(guild_id, data):
    check_guild_has_presence(guild_id)
    write_json(data, f"files/shop/{guild_id}.json")

#------------------------------------------------------------MISC

async def send_image(ctx: commands.Context, image, text=""):
    """
    Sends an image
    :param ctx:
    :param image:
    :param text:
    :return:
    """
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    file = discord.File(fp=buffer, filename="generated.png")
    await ctx.send(text, file=file)

def get_gif(query):
    """
    Researches a gif on Giphy
    :param query: Key word for the search
    :return:
    """
    url = "https://api.giphy.com/v1/gifs/search"

    params = {
        "api_key": GIPHY_TOKEN,
        "q": query,
        "limit": 1
    }

    r = requests.get(url, params=params).json()

    if not r["data"]:
        return None

    return r["data"][0]["images"]["original"]["url"]

def search(query: str):
    """
    Researches links in DuckDuckGo
    :param query: Key word for the search
    :return:
    """
    urls = ""
    for i in range(5):
        urls = ""
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)

            for r in results:
                urls += r["href"] + "\n"
        if urls :
            break

    if urls:
        return f"Résultat de la recherche (5 liens les plus pertinents) : \n{urls}"
    else:
        return "Erreur lors de la recherche. Essayez de réaranger un peu les mots clés (DuckDuckGo a du mal)"

def surf(url):
    """
    Get the web page from an URL
    :param url: Web page's URL
    :return:
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Supprime les éléments non visibles
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)

        return "Résultat du surf : " + text
    except:
        return "Résultat du surf : Erreur lors du surf. Peut être URL non valide ou inexistante ?"

async def parse_text(text, message, dm):
    """
    Executes the AI's commands, such as /gif or /search
    :param text:
    :param message:
    :param dm:
    :return:
    """

    # gif
    pattern = r'/gif\s*"([^"]+)"'

    matches = re.findall(pattern, text)

    for m in matches:
        gif = get_gif(m) #get the GIF

        if gif:
            text = text.replace(f'/gif "{m}"', gif)

    #search
    pattern = r'/search\s*"([^"]+)"'
    matches = re.findall(pattern, text)

    for m in matches:
        print("search - " + m)
        results = search(m) #search
        write_file(results, f"files/messages/{message.guild.id}.txt")
        ai_answer = await ask_ai(results, message.author.display_name, message.guild.id, dm=dm) #ask the ai what to do / say now he has got the links
        text = ai_answer
        text = await parse_text(text, message, dm)

    #surf
    pattern = r'/surf\s*"([^"]+)"'
    matches = re.findall(pattern, text)

    for m in matches:
        print("surf - " + m)
        page = surf(m) #get the page

        write_file(page, f"files/messages/{message.guild.id}.txt")
        ai_answer = await ask_ai(page, message.author.display_name, message.guild.id, dm=dm) #ask the ai what to do / say now he has got the page
        text = ai_answer
        text = await parse_text(text, message, dm)

    return text

#------------------------------------------------------------ON MESSAGE PROCESS

async def ai_process(bot, message):
    """
    The AI part of the on_message function
    :param bot: The bot itself
    :param message: The user's message
    :return:
    """
    content = message.content
    if not message.author == bot.user and content != "":
        author = message.author.display_name
        for mention in message.mentions: #translate mentions
            content = content.replace(
                f"<@{mention.id}>",
                f"@{mention.display_name}"
            )
        for channel in message.channel_mentions: #translate channel mentions
            content = content.replace(
                f"<#{channel.id}>",
                f"#{channel.name}"
            )
        for role in message.role_mentions: #translate role mentions
            content = content.replace(
                f"<@&{role.id}>",
                f"@{role.name}"
            )

        write_file(author + " : " + content, f"files/messages/{message.guild.id}.txt")
        if bot.user in message.mentions and message.author != bot.user: #if the bot is mentionned
            try:
                async with message.channel.typing():
                    answer = await ask_ai(content, message.author.display_name, message.guild.id)
                    to_send = await parse_text(answer, message, False)
                    try:
                        await message.reply(to_send)
                    except discord.HTTPException:
                        await message.reply(to_send[:1975] + "... <message trop long>")

            except errors.ClientError:
                await warn_no_more_credits(message)
                write_file("BelloBot(forbellobot) : Désolé, plus de crédits pour l'IA (réessayez demain !)", f"files/messages/{message.guild.id}.txt")
            except errors.ServerError:
                await message.channel.send(f"Désolé, mais le serveur de Google peine en ce moment... Veuillez réessayer plus tard !")
                write_file("BelloBot(forbellobot) : Problème avec le serveur de Google, réessayez plus tard !",f"files/messages/{message.guild.id}.txt")

async def xp_process(bot, message):
        """
        The XP and money part of the on_message function
        :param bot: The bot itself
        :param message: The user's message
        :return:
        """
        user = message.author
        guild = message.guild
        user_data = get_user_data(user.id, guild.id)
        user_data["xp"] += int(5 * user_data["mult_xp"])
        user_data["money"] += int(10 * user_data["mult_money"])

        #checks if the xp has reached the xp goal
        leveluped = False
        xp_goal = user_data["level"] * 15 #xp goal formula
        levelup = user_data["xp"] >= xp_goal
        money_bonus = 0
        while levelup: #level ups until the xp is less than the xp goal
            leveluped = True
            user_data["xp"] -= xp_goal
            user_data["level"] += 1
            money_bonus += xp_goal * 10

            xp_goal = user_data["level"] * 15
            levelup = user_data["xp"] >= xp_goal

        set_user_data(user.id, guild.id, user_data)

        if leveluped: #send the level up message
            embed = discord.Embed(color=discord.Color.green(), title="Passage de niveau !", description=f"GG à {user.mention} pour avoir passé le niveau {user_data["level"]} !🔥 Tu gagnes {money_bonus}{flamcoin_symbol} 🫰💰🪙 Continue de gagner des niveaux..." if user != bot.user else f"GG à moi (BelloBot) pour avoir passé le niveau {user_data["level"]} ! 🔥 Je gagne {money_bonus}{flamcoin_symbol} 🫰💰🪙")
            config = get_config(guild.id)
            if config["xp_channel"]:
                channel = await guild.fetch_channel(config["xp_channel"])
            else:
                channel = guild.text_channels[0]
            await channel.send(f"{user.mention}",embed=embed)

async def polls_process(message):
    """
    The polls part of the on_message function, executed when a poll is created
    :param message: Message
    :return:
    """
    if message.poll:
        poll = message.poll
        title = poll.question
        answers = poll.answers

        prompt = f"Un nouveau sondage a été publié par {message.author.display_name} : {title} \n Tu as le choix entre : \n"
        for answer in answers:
            prompt += f"-{answer.id} : {answer.emoji if answer.emoji else ""} {answer.text}\n"
        prompt += f"{"Le sondage autorise plusieurs réponse." if poll.multiple else "Le sondage n'autorise qu'une seule réponse."} Décris le pour et le contre de chaque réponse, et dit ton opinion en te basant sur tes souvenirs et ta raison, et emmet un avis objectif de la question, sauf si cette dernière est tout sauf objectif bien entendu, et ne dépasse pas les 2000 caractères."

        try:
            thread: discord.Thread = await message.create_thread(
                name=f"📊 Discussion : {poll.question}",
                auto_archive_duration=1440
            )
        except discord.HTTPException: #the thread name is too long
            thread: discord.Thread = await message.create_thread(
                name=f"📊 Discussion",
                auto_archive_duration=1440
            )

        write_file(f"{message.author.display_name} : " + prompt, f"files/messages/{message.guild.id}.txt")

        ai_answer = await ask_ai(prompt, message.author.display_name, message.guild.id)
        try:
            await thread.send(ai_answer)
        except discord.HTTPException:
            await thread.send(ai_answer[:1975] + "... <message trop long>")

async def dm_process(bot, message: discord.Message):
    """
    Executed if the message comes from DM
    :param bot: The bot itself
    :param message: Message
    :return:
    """
    content = message.content
    if not message.author == bot.user:
        if not str(message.author.id) + ".txt" in os.listdir("files/dms/"):
            write_file("", "files/dms/" + str(message.author.id) + ".txt")
        author = message.author.display_name
        for mention in message.mentions:
            content = content.replace(
                f"<@{mention.id}>",
                f"@{mention.display_name}"
            )

        write_file(author + " : " + content, f"files/dms/{message.author.id}.txt")
        try:
            async with message.channel.typing():
                answer = await ask_ai(content, message.author.display_name, message.author.id, dm = True)
                to_send = await parse_text(answer, message, True)
                try:
                    await message.reply(to_send)
                except discord.HTTPException:
                    await message.reply(to_send[:1975] + "... <message trop long>")
        except errors.ClientError:
            await warn_no_more_credits(message=message)

#------------------------------------------------------------ON MESSAGE FUNCTION

async def on_message(bot, message: discord.Message):
    if message.guild is None:
        await dm_process(bot, message) #if the message comes from DM
        return
    # check if the user and guild have files
    check_guild_has_presence(message.guild.id)
    check_has_data_file(message.author.id, message.guild.id)

    await ai_process(bot, message) #ask something to the AI if mentionned

    await xp_process(bot, message) #add XP and money to the user and eventualy level up

    await polls_process(message) #answer to polls

#------------------------------------------------------------WARN NO MORE CREDITS

async def warn_no_more_credits(message = None, ctx = None):
    """
    This code is executed when the bot doesnt have credits anymore
    :param message: Message (if the user was typing to the bot)
    :param ctx: Context (if the user was using a command)
    :return:
    """
    embed = discord.Embed(color=discord.Color.red(), title="Plus de crédits !", description="Le bot n'a plus de crédits pour remplir pleinement ses fonctions IA. Il y en aura de nouveau demain. Désolé !")
    if message:
        await message.reply(embed=embed)
    elif ctx:
        await ctx.send(embed=embed)

#------------------------------------------------------------CHECK LOOP

async def check_alarm(bot):
    """
    Checks if any alarm is set to now
    :param bot: The bot itself
    :return:
    """
    for alarm_guild_id in os.listdir("files/alarms/"):
        if alarm_guild_id == ".gitignore":
            continue
        for alarm_user_id in os.listdir(f"files/alarms/{alarm_guild_id}/"):
            alarm_user_id = alarm_user_id.removesuffix(".json")
            alarms = get_alarms(alarm_user_id, alarm_guild_id)
            for alarm_id in alarms:
                alarm = alarms[alarm_id]
                day = datetime.now().weekday()
                if (day in alarm["days"] or alarm["one_shot"]) and alarm["enabled"]:
                    target = datetime.strptime(alarm["time"], "%H:%M")
                    now = datetime.now()

                    start = target.replace(year=now.year, month=now.month, day=now.day)
                    end = start + timedelta(seconds=29)

                    if start <= now <= end:
                        alarm_channel_id = get_config(alarm_guild_id)["alarm_channel"]
                        alarm_guild = await bot.fetch_guild(int(alarm_guild_id))
                        if alarm_guild is None:
                            continue
                        alarm_channel = await alarm_guild.fetch_channel(alarm_channel_id)
                        if alarm_channel is None:
                            continue
                        embed = discord.Embed(color=discord.Color.blurple(), title=f"C'est l'heure : Alarme {alarm_id}",
                                      description=f"{alarm["name"]}")
                        await alarm_channel.send(f"{alarm["name"]} <@{alarm_user_id.removesuffix(".json")}>",
                                                 embed=embed)
                        if alarm["one_shot"]:
                            alarm["enabled"] = False
                            alarms[alarm_id] = alarm
                            set_alarms(alarm_user_id, alarm_guild_id, alarms)

async def check_effect_expiration(bot):
    """
    For every effect of every user, checks if the effect is out dated, if so, remove it and the potential role
    :param bot:
    :return:
    """
    for guild in bot.guilds:
        for user in guild.members:
            user_data = get_user_data(user.id, guild.id)
            shop = get_shop(guild.id)
            effects = user_data["temp_effects"].copy()
            for effect in effects:
                if not effect in shop:
                    del user_data["temp_effects"][effect]
                    continue

                now = datetime.now(UTC)
                expiration = datetime.fromisoformat(effects[effect])
                if expiration < now:
                    del user_data["temp_effects"][effect]

                    type = shop[effect]["use"]["type"]
                    if type == "mult_xp":
                        user_data["mult_xp"] = 1
                    elif type == "mult_money":
                        user_data["mult_money"] = 1

                    role_id = shop[effect]["use"]["role"]
                    role = await guild.fetch_role(role_id)
                    if role in user.roles:
                        await user.remove_roles(role)

                    set_user_data(user.id, guild.id, user_data)

                    embed = discord.Embed(color=discord.Color.red(), title="Expiration d'un effet", description=f"Désolé {user.mention}, mais vous n'avez plus l'effet {shop[effect]["name"]}. Je vous retire le rôle {role.mention}...")
                    config = get_config(guild.id)
                    if config["xp_channel"]:
                        channel = await guild.fetch_channel(config["xp_channel"])
                    else:
                        channel = guild.text_channels[0]
                    await channel.send(f"{user.mention}", embed=embed)