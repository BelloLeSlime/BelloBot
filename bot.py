VERSION = "5.3"

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
intents.members = True

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
    "[{asctime}] [{levelname:<8}] {name}: {message}", "%d/%m/%Y %H:%M:%S", style="{"
)
file_handler.setFormatter(file_handler_formatter)

# Add the handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(intents=intents, command_prefix="§", help_command=None)
        self.logger = logger
        self.version = VERSION
        self.guild_count = 0

    async def load_cogs(self) -> None:
        """
        The code in this function is executed whenever the bot will start.
        """

        self.guild_count = len(self.guilds)
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
        await Cf.check_effect_expiration(self)

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
                description="Il faut être ower pour utiliser cette commande.", color=0xE02B2B
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