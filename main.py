import os
from random import choice
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
hg_token = os.getenv('HG_TOKEN')
from discord import *

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

#---------------------------------EVENTS---------------------------------------------

system = "Tu es BelloBot, un bot Discord. Utilise du vocabulaire de discord, utilise des émoticônes comme ;( >:) ¯\\_( ͡° ͜ʖ ͡°)_/¯ ༼ つ ◕_◕ ༽つ ಠ_ಠ :p XD et d'autre. Tu aura au début du message de l'utilisateur son nom. Il n'est pas dans ce qu'il a dit réellement, donc ne mets pas BelloBot: ou <Nom>: au début, car cela sera sans rapport."
model = "meta-llama/Llama-3.1-8B-Instruct"

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")
    log("connected", bot.user.name)
    states = [
        "rien, je suis une IA :p",
        "Peak car c'est incrr",
        "NEVER GONNA GIVE YOU UP",
        "une minute de plus dans ce jacuzzi et je me transforme en William Afton.",
        "avec vos données >:3",
        "v2.0 ༼ つ ◕_◕ ༽つ",
    ]
    await bot.change_presence(
        activity=Activity(
            type=ActivityType.playing,
            name=choice(states)
        )
    )

@bot.event
async def on_message(message: Message):
    global message_count
    content = message.content
    author = message.author.display_name
    write_file(author + "|/:!§!:/|" + content, "messages.txt")
    log("message", author + "|/:!§!:/|" + content)
    if bot.user in message.mentions and message.author.name != "BelloBot":
        try:
            messages = [
                {"role": "system", "content": system},
            ]
            for msg in read_file("messages.txt"):
                split = msg.split("|/:!§!:/|")
                messages.append({"role": "user" if author != "BelloBot" else "assistant", "content":split[0] + ": " + split[1]})
            answer = ask_ai(messages, model)
            await message.reply(answer)
        except Exception as e:
            print(e)
            await message.channel.send("<Erreur !>")
            log("error", str(e))

#--------------------------------------RUN---------------------------------------------

try:
    bot.run(token)
except Exception as e:
    log("critical error", str(e))
finally:
    log("exiting", bot.user.name)



