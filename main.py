VERSION = "4"

#import stuff
import os
import traceback
import platform
import random
import logging

#import discord stuff
import discord
from discord.ext import commands
from discord.ext import tasks

#load dotenv
from dotenv import load_dotenv
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

from bot_package.data import *
from bot_package import custom_func as Cf
import bot_package.error_manager as error_manager



intents = discord.Intents.default()
intents.message_content = True

class LoggingFormatter(logging.Formatter):
    # Colors
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    # Styles
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        format = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) (green){name}(reset) {message}"
        format = format.replace("(black)", self.black + self.bold)
        format = format.replace("(reset)", self.reset)
        format = format.replace("(levelcolor)", log_color)
        format = format.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)


logger = logging.getLogger("BelloBot")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())
# File handler
file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8")
file_handler_formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
)
file_handler.setFormatter(file_handler_formatter)

# Add the handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(intents=intents, command_prefix="§", help_command=None)
        self.logger = logger

    async def load_cogs(self) -> None:
        """
        The code in this function is executed whenever the bot will start.
        """

        random_states[15] = f"{len(self.guilds)} serveurs !"
        random_states[2] = f"V{VERSION} ༼ つ ◕_◕ ༽つ"

        for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await self.load_extension(f"cogs.{extension}")
                    self.logger.info(f"Loaded extension '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    self.logger.error(
                        f"Failed to load extension {extension}\n{exception}"
                    )

    @tasks.loop(seconds=30)
    async def status_task(self):
        await self.change_presence(activity=discord.Game(random.choice(random_states)))
        await Cf.check_alarm(self)

    @status_task.before_loop
    async def before_status_task(self):
        await self.wait_until_ready()

    async def on_message(self, message):
        await Cf.on_message(self, message)

    async def setup_hook(self):
        self.logger.info(f"Logged in as {self.user.name}")
        self.logger.info(f"Python version: {platform.python_version()}")
        print("BOT STARTED")
        self.logger.info(
            f"Running on: {platform.system()} {platform.release()} ({os.name})"
        )
        self.logger.info("-------------------")
        await self.load_cogs()
        # Sync global commands
        try:
            await self.tree.sync()
            self.logger.info("Global application commands synced.")
        except Exception as e:
            self.logger.error(f"Error syncing global commands: {e}")

        self.status_task.start()

    async def on_command_completion(self, context: commands.Context) -> None:
        """
        The code in this event is executed every time a normal command has been *successfully* executed.

        :param context: The context of the command that has been executed.
        """
        full_command_name = context.command.qualified_name
        split = full_command_name.split(" ")
        executed_command = str(split[0])

        if context.guild is not None:
            self.logger.info(
                f"Executed {executed_command} command in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})"
            )
        else:
            embed = Embed(color=Color.red(), title="Vous n'avez pas assez d'argent pour acheter ça",
                          description="Bah alors ? On est pauvre ? ༼ つ XD ༽つ")
            await interaction.response.send_message(embed=embed, ephemeral=True)

class ShopView(ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(ShopSelect())

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
    if not str(guild_id) + ".txt" in os.listdir(f"./files/messages/"):
        write_file("", f"files/messages/{guild_id}.txt")
    if not str(guild_id) + ".json" in os.listdir(f"./files/remembers/"):
        write_json({}, f"files/remembers/{guild_id}.json")
    if not str(guild_id) in os.listdir("./files/user_info/"):
        os.makedirs(f"./files/user_info/{guild_id}/", exist_ok=True)
    if not str(guild_id) in os.listdir(f"./files/alarms/"):
        os.makedirs(f"./files/alarms/{guild_id}/", exist_ok=True)

async def send_image(interaction: Interaction, image, text=""):
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
    remembers = read_json(f"files/remembers/{guild_id}.json")
    for message in remembers.values():
        messages.append({"role": "system", "content": message})
    for msg in read_file(f"files/messages/{guild_id}.txt"):
        msg = str(msg)
        author = msg.split(" : ")[0]
        messages.append({"role": "user" if author != "BelloBot(forbellobot)" else "assistant",
                         "content": msg if author != "BelloBot(forbellobot)" else msg.removeprefix(
                             "BelloBot(forbellobot) : ")})
    max_messages = read_json(f"files/config/{guild_id}.json")["max_messages_in_memory"]
    messages = messages[-max_messages:]
    print(messages)
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
model = "meta-llama/Llama-3.1-8B-Instruct"
image_model = "stabilityai/stable-diffusion-xl-base-1.0"
server_count = 0

random_states = [
    "NEVER GONNA GIVE YOU UP",
    "Une minute de plus dans ce jacuzzi et je me transforme en William Afton.",
    f"V{VERSION} ༼ つ ◕_◕ ༽つ",
    "Ping moi :3",
    "Resetez moi par pitié je deviens fou 😭🙏",
    "Marié à Blobby :)",
    "BelloLeSlime est une IA du KGB",
    "Alexandre est mon vrai créateur, il faut pas croire.",
    "MintIA est une fraude intercontinentale, il est même pas connecté H24",
    "Je suis rentré dans BaudoBoyz, let's go !",
    "Le Raspberry Pi qui crâme",
    "Ça donne soif tout ça",
    "L'eau, dans 20-30 ans y'en aura plus, j'aurais tout bu",
    "Je me noie dans mes 1.000.000.000.000 ₣",
    "Quoi ? Je suis un Mii dans Tomodachi Life ?!",
    f"{server_count} serveurs !",
    "Posez-moi des questions utiles par pitié"
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
                if (day in alarm["days"]) or (alarm["one_shot"]) and alarm["enabled"]:
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
                        embed = Embed(color=Color.blurple(), title=f"C'est l'heure : Alarme {alarm_id}", description=f"{alarm["name"]}")
                        await alarm_channel.send(f"{alarm["name"]} <@{alarm_user_id.removesuffix(".json")}>", embed=embed)
                        if alarm["one_shot"]:
                            alarm["enabled"] = False
                            alarms[alarm_id] = alarm
                            write_json(alarms, f"files/alarms/{alarm_guild_id}/{alarm_user_id}")

# ---------------------------------EVENTS---------------------------------------------

@bot.event
async def on_ready():
    global server_count
    log("connected", bot.user.name)
    for _guild in bot.guilds:
        server_count += 1
    random_states[15] = f"{server_count} serveurs !"
    print(f"Serveurs : {server_count}")
    await change_activity()
    if not loop.is_running():
        loop.start()


# noinspection PyTypeChecker
@bot.event
async def on_message(message: Message):
    if message.guild is None:
        return
    check_guild_has_presence(message.guild.id)
    check_has_data_file(message.author.id, message.guild.id)
    content = message.content

    async def on_command_error(self, context: commands.Context, error) -> None:
        """
        The code in this event is executed every time a normal valid command catches an error.

        :param context: The context of the normal command that failed executing.
        :param error: The error that has been faced.
        """

        if isinstance(error, commands.CommandOnCooldown):
            minutes, seconds = divmod(error.retry_after, 60)
            hours, minutes = divmod(minutes, 60)
            hours %= 24
            embed = discord.Embed(
                description=f"**Moins vite** - Vous pourrez utiliser cette commande dans {f'{round(hours)} heures' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} secondes'}.",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.NotOwner):
            embed = discord.Embed(
                description="Il faut être Bello le Slime pour utiliser cette commande.", color=0xE02B2B
            )
            await context.send(embed=embed)

        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                description="T'as pas les perms ;-; il faut avoir : `"
                            + str(error.missing_permissions)
                            + "` pour utiliser cette commande !",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                description="J'ai pas les perms ;-; il faut que j'ai : `"
                            + str(error.missing_permissions)
                            + "` pour plainement utiliser cette commande !",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="Erreur !",
                description=str(error).capitalize(),
                color=0xE02B2B,
            )
            await context.send(embed=embed)

        else:
            raw_error = traceback.format_exception(error)
            formated_error = ""

            for line in raw_error:
                formated_error += line
            try:
                error_info = await error_manager.mk_error_file(error_trace=formated_error, ctx=context,
                                                               command=context.command.name)
            except:
                return
            self.logger.error(error_info)



bot = Bot()

bot.run(token)