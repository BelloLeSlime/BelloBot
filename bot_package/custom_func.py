import json
import os
import discord
from discord.ext import commands
from huggingface_hub import InferenceClient
from bot_package.data import HF_TOKEN, GIPHY_TOKEN, model, system
import io
import requests
import re
from datetime import datetime, UTC, timedelta

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

def ask_ai(messages, model):
        client = InferenceClient(token=HF_TOKEN)
        response = client.chat_completion(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content

def text_to_image(prompt, model, negative_prompt, width=1024, height=1024, steps=30):
        client = InferenceClient(token=HF_TOKEN)
        image = client.text_to_image(prompt=prompt, model=model, negative_prompt=negative_prompt, width=width,
                                     height=height, num_inference_steps=steps)
        return image

def add_item(guild_id: int, user_id: int, item: str):
    data = get_user_data(guild_id, user_id)
    data["items"][item] = data["items"][item] + 1 if item in data["items"] else 1
    set_user_data(guild_id, user_id, data)

def check_has_data_file(user_id, guild_id):
    check_guild_has_presence(guild_id)
    if not str(guild_id) in os.listdir("files/user_info/"):
        os.makedirs(f"files/user_info/{guild_id}")
    try:
        if not str(user_id) + ".json" in os.listdir(f"files/user_info/{guild_id}/"):
            write_json({"xp": 0, "level": 1, "money": 0, "mult_xp": 1, "mult_money": 1, "temp_effects": {}, "items": {}},
                       f"files/user_info/{guild_id}/{user_id}.json")
    except:
        pass
    try:
        if not str(user_id) + ".json" in os.listdir(f"files/alarms/{guild_id}/"):
            write_json({}, f"files/alarms/{guild_id}/{user_id}.json")
    except:
        pass
    if not str(user_id) + ".json" in os.listdir(f"files/slimania_inventory/"):
        write_json({
            "last_roll": 0,
            "inventory": {}
        },
        f"files/slimania_inventory/{user_id}.json")

def check_guild_has_presence(guild_id):
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

async def send_image(ctx: commands.Context, image, text=""):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    file = discord.File(fp=buffer, filename="generated.png")
    await ctx.send(text, file=file)

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

def get_gif(query):
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

def parse_text(text):
    # gif
    pattern = r'/gif\s*"([^"]+)"'

    matches = re.findall(pattern, text)

    for m in matches:
        print(m)
        gif = get_gif(m)
        print(gif)

        if gif:
            text = text.replace(f'/gif "{m}"', gif)

    return text

def get_messages(guild_id, system):
    messages = [
        {"role": "system", "content": system},
    ]
    remembers = get_remembers(guild_id)
    for message in remembers.values():
        messages.append({"role": "system", "content": message})
    for msg in read_file(f"files/messages/{guild_id}.txt"):
        msg = str(msg)
        author = msg.split(" : ")[0]
        messages.append({"role": "user" if not author in ["BelloBot(forbellobot)", "system(forbellobot)"] else {"assistant" if author == "BelloBot(forbellobot)" else "system"},
                         "content": msg if author != "BelloBot(forbellobot)" else msg.removeprefix(
                             "BelloBot(forbellobot) : ")})
    max_messages = read_json(f"files/config/{guild_id}.json")["max_messages_in_memory"]
    messages = messages[-max_messages:]
    return messages

def get_dm(user_id: int, system, user_display_name):
    messages = [
        {"role": "system", "content": system},
        {"role": "system", "content": f"Tu parles ici avec {user_display_name}"},
    ]
    for msg in read_file(f"files/dms/{user_id}.txt"):
        msg = str(msg)
        split = msg.split(" : ")
        author = split[0]
        messages.append({"role": "user" if author != "BelloBot(forbellobot)" else "assistant",
                         "content": split[1]})
        messages = messages[-50:]
        return messages

async def ask_bellobot(message, messages):
    answer = ask_ai(messages, model)
    to_send = parse_text(answer)
    write_file("BelloBot(forbellobot) : " + answer, f"files/messages/{message.guild.id}.txt")
    return to_send

async def ai_process(bot, message):
    content = message.content
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
        if bot.user in message.mentions and message.author != bot.user:
            try:
                answer = await ask_bellobot(message, get_messages(message.guild.id, system))
                await message.reply(answer)
            except:
                pass

async def xp_process(bot, message):
    config = get_config(message.guild.id)
    if config["xp_channel"]:
        user_data_xp = get_user_data(message.guild.id, message.author.id)
        member: discord.Member = await message.guild.fetch_member(message.author.id)

        if user_data_xp["mult_xp"] > 1:
            if datetime.fromisoformat(user_data_xp["temp_effects"]["boost_xp"]) < datetime.now(UTC):
                del user_data_xp["temp_effects"]["boost_xp"]
                user_data_xp["mult_xp"] = 1
                x2_xp_role = await message.guild.fetch_role(
                    config["x2_xp_role"])
                await message.author.remove_roles(x2_xp_role)
        if user_data_xp["mult_money"] > 1:
            if datetime.fromisoformat(user_data_xp["temp_effects"]["boost_money"]) < datetime.now(UTC):
                del user_data_xp["temp_effects"]["boost_money"]
                user_data_xp["mult_money"] = 1
                x2_money_role = await message.guild.fetch_role(
                    config["x2_money_role"])
                await message.author.remove_roles(x2_money_role)

        file_role = await message.guild.fetch_role(config["file_role"])
        soundboard_role = await message.guild.fetch_role(
            config["soundboard_role"])
        game_role = await message.guild.fetch_role(config["game_role"])
        poll_role = await message.guild.fetch_role(config["poll_role"])
        link_role = await message.guild.fetch_role(config["link_role"])
        extern_role = await message.guild.fetch_role(config["extern_role"])
        priority_voice_role = await message.guild.fetch_role(
            config["priority_voice_role"])
        bypass_slow_mode_role = await message.guild.fetch_role(
            config["bypass_slow_mode_role"])
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
        send_message = user_data_xp["xp"] >= 15 * user_data_xp["level"]
        while user_data_xp["xp"] >= 15 * user_data_xp["level"]:
            user_data_xp["xp"] -= 15 * user_data_xp["level"]
            user_data_xp["level"] += 1
            user_data_xp["money"] += 50 * user_data_xp["level"]
        if send_message:
            xp_channel = await message.guild.fetch_channel(
                config["xp_channel"])
            if message.author == bot.user:
                embed = discord.Embed(color=discord.Color.green(),
                              title=f"Moi, {bot.user.display_name}, a passé le niveau {user_data_xp["level"]} ! 🥳🎉 ",
                              description=f"GG à moi-même ༼ つ ಠ◡ಠ ༽つ Je gagne {50 * user_data_xp["level"]}₣ 💰💰💰")
                await xp_channel.send(embed=embed)
            else:
                embed = discord.Embed(color=discord.Color.green(),
                              title=f"GG à {message.author.display_name} pour avoir passé le niveau {user_data_xp["level"]} ! 🥳🎉",
                              description=f"Tu gagnes {50 * user_data_xp["level"]}₣ 💰💰💰 Continue de gagner des niveaux... 🔥🔥🔥")
                await xp_channel.send(f"||{message.author.mention}||", embed=embed)
        set_user_data(message.author.id, message.guild.id, user_data_xp)

async def polls_process(message):
    if message.poll:
        poll = message.poll
        title = poll.question
        answers = poll.answers
        prompt = f"Un nouveau sondage a été publié par {message.author.display_name} : {title} \n Tu as le choix entre : \n"
        for answer in answers:
            prompt += f"-{answer.id} : {answer.emoji if answer.emoji else ""} {answer.text}\n"
        prompt += f"{"Le sondage autorise plusieurs réponse." if poll.multiple else "Le sondage n'autorise qu'une seule réponse."} Décris le pour et le contre de chaque réponse, et dit ton opinion en te basant sur tes souvenirs et ta raison, et emmet un avis objectif de la question, sauf si cette dernière est tout sauf objectif bien entendu."
        messages = get_messages(message.guild.id, system)
        messages.append({"role": "system", "content": prompt})
        ai_answer = ask_ai(messages, model)
        thread: discord.Thread = await message.create_thread(
            name=f"📊 Discussion : {poll.question}",
            auto_archive_duration=1440
        )
        await thread.send(ai_answer)
        write_file("system(forbellobot) : " + prompt, f"files/messages/{message.guild.id}.txt")
        write_file("BelloBot(forbellobot) : " + ai_answer, f"files/messages/{message.guild.id}.txt")

async def dm_process(bot, message: discord.Message):
    content = message.content
    if not message.author == bot.user:
        author = message.author.display_name
        for mention in message.mentions:
            content = content.replace(
                f"<@{mention.id}>",
                f"@{mention.display_name}"
            )

        write_file(author + " : " + content, f"files/dms/{message.author.id}.txt")
        if bot.user in message.mentions and message.author != bot.user:
            try:
                answer = await ask_bellobot(message, get_dm(message.author.id, system, message.author.display_name))
                await message.reply(answer)
            except:
                await warn_no_more_credits(message=message)

async def on_message(bot, message: discord.Message):
    if message.guild is None:
        await dm_process(bot, message)
        return
    check_guild_has_presence(message.guild.id)
    check_has_data_file(message.author.id, message.guild.id)

    # ai
    await ai_process(bot, message)

    # xp
    await xp_process(bot, message)

    # polls
    await polls_process(message)

async def warn_no_more_credits(message = None, ctx = None):
    embed = discord.Embed(color=discord.Color.red(), title="Plus de crédits !", description="Le bot n'a plus de crédits pour remplir pleinement ses fonctions IA. Il y en aura un petit peu le mois prochain. Désolé !")
    if message:
        await message.reply(embed=embed)
    elif ctx:
        await ctx.send(embed=embed)

async def check_alarm(bot):
    # alarm
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