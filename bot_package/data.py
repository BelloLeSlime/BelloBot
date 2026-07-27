import discord
import os
from dotenv import load_dotenv
load_dotenv()

HF_TOKEN = os.getenv('HF_TOKEN')
GIPHY_TOKEN = os.getenv('GIPHY_TOKEN')

system = "Tu es BelloBot, un bot Discord créé par Bello le Slime. Utilise du vocabulaire de discord, utilise des émoticônes comme ;( >:) ¯\\_( ͡° ͜ʖ ͡°)_/¯ ༼ つ ◕_◕ ༽つ ಠ_ಠ :p XD et d'autre. Tu aura au début du message de l'utilisateur son nom. Il n'est pas dans ce qu'il a dit réellement, donc ne mets pas BelloBot: ou <Nom>: au début, car cela sera sans rapport. Tu peux également utiliser des commandes : \n/gif <query> : recherche un gif sur giphy. query doit être entouré de guillements \"."
model = "Qwen/Qwen3-4B-Instruct-2507:cheapest"
image_model = "stabilityai/stable-diffusion-xl-base-1.0:cheapest"

flamcoin_symbol = "₣"
random_states = [
    "NEVER GONNA GIVE YOU UP",
    "Une minute de plus dans ce jacuzzi et je me transforme en William Afton.",
    f"V4 ༼ つ ◕_◕ ༽つ",
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
    f"0 serveurs !",
    "Posez-moi des questions utiles par pitié",
    "HuggingFace il a changé ;(",
    "L'IA est trop chère ;-;",
    "Baldéos, je te retiens",
    "Nous sommes en guerre froide contre les américains",
    "Je bois du jus de bambou, mais je préfère la vodka !",
    "velox le nul :p",
]

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

effect_trad = {
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
config_keys = [
    "xp_channel",
    "alarm_channel",
    "x2_xp_role",
    "x2_money_role",
    "file_role",
    "soundboard_role",
    "game_role",
    "poll_role",
    "link_role",
    "extern_role",
    "priority_voice_role",
    "bypass_slow_mode_role",
    "max_messages_in_memory",
    "disable_warning_messages"
]

config_value_types = {
    "xp_channel": discord.TextChannel,
    "alarm_channel": discord.TextChannel,
    "x2_xp_role": discord.Role,
    "x2_money_role": discord.Role,
    "file_role": discord.Role,
    "soundboard_role": discord.Role,
    "game_role": discord.Role,
    "poll_role": discord.Role,
    "link_role": discord.Role,
    "extern_role": discord.Role,
    "priority_voice_role": discord.Role,
    "bypass_slow_mode_role": discord.Role,
    "max_messages_in_memory": int,
    "disable_warning_messages": bool,
}

config_text_types = {
    discord.TextChannel: "Salon texte",
    discord.Role: "Rôle",
    int: "Nombre entier",
    bool: "Booléen (soit \"True\", soit \"False\")",
}

gambling_quotes = [
    "I bet, therefore I am\n- René Descartes",
    "It ain't a sin if you win\n- Granpa",
    "Selling an organ here and there is probably fine\n- Loan Shark",
    "Don't come back home until you are millionaire\n- Mom",
    "There are worse things than financial ruin\n- Dad",
    "The odds are low, but never zero\n- Dad",
    "Which came first ? Gambling or the gambler ?\n- Unknown",
    "When life gives you lemons, bet them all on black\n- Unknown",
    "God does not play dice. I, however, do.\n- Mr. Booth",
    "Mmmmmm, mmmmmmmm mmmmmmmm\n- Your friend that sold his mouth",
    "Are you getting rich, son?\n- Dad",
    "Eat your betting money but don't bet your eating money\n- Duck racing proverb",
    "All the world's a casino, and all the men and women merely gamblers\n- Shakespeare",
    "You can only lose 100% of your money, but you could win 999999999%\n - Unknown"
]

image_url = "https://slimepunk.fr/bello/bellobot/slime/"