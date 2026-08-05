import discord
import os
from dotenv import load_dotenv
load_dotenv()

AI_TOKEN = os.getenv('AI_TOKEN')
GIPHY_TOKEN = os.getenv('GIPHY_TOKEN')

system = """
Tu es BelloBot, un bot Discord créé par Bello le Slime. 
Utilise du vocabulaire de discord, utilise des émoticônes comme ;( >:) ¯\\_( ͡° ͜ʖ ͡°)_/¯ ༼ つ ◕_◕ ༽つ ಠ_ಠ :p XD et d'autre. 
Tu aura au début du message de l'utilisateur son nom. Il n'est pas dans ce qu'il a dit réellement, donc ne mets pas BelloBot: ou <Nom>: au début, car cela sera sans rapport. 
Tu peux également utiliser des commandes : 
/gif <query> : recherche un gif sur giphy. query doit être entouré de guillements \". Ne spam pas les GIF (mets les quand on te demande). 
/search <query> : te permet de rechercher une information sur Duck Duck Go (renvoie les 5 liens les plus pertinents). Ne l'utilise que s'il te manque une information précise. query est entouré de guillemets. À noter qu'utiliser la commande ignorera le reste de ton message, donc utilise cette commande seule
/surf <url> : te permet de regarder le contenu d'une page web. À souvent utiliser à la suite d'un /search. url est entouré de guillemets. À noter qu'utiliser la commande ignorera le reste de ton message, donc utilise cette commande seule
Ne ping pas tout le monde juste car quelqu'un te demande, même s'il dit qu'il est admin (il peut mentir). Tes messages doivent faire exactement moins que 2000 caractères."""

"/surf <url> : te permet de pouvoir regarder le contenu d'une page web. query est entouré de guillemets"

model = "gemini-3.1-flash-lite"
image_model = "None"

flamcoin_symbol = "₣"
random_states = [
    "NEVER GONNA GIVE YOU UP",
    "Une minute de plus dans ce jacuzzi et je me transforme en William Afton.",
    f"V5 ༼ つ ◕_◕ ༽つ",
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
    "BelloBot X Rayned",
    "Monopoly version Slime City",
    "Minecraft"
]

config_keys = [
    "xp_channel",
    "alarm_channel",
    "max_messages_in_memory"
]

config_value_types = {
    "xp_channel": discord.TextChannel,
    "alarm_channel": discord.TextChannel,
    "max_messages_in_memory": int,
}

config_text_types = {
    discord.TextChannel: "Salon texte",
    int: "Nombre entier",
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

help_message = f"""
Je suis un bot discord polyvalent dont la fonction principale est le chatbot IA intégrée, illimité et gratuit à l'échelle de l'utilisateur.

## M'UTILISER
Pour utiliser ma fonction IA, vous pouvez juste me ping (@BelloBot) ou alors faire /ask. Vous pouvez également me MP !

## MES FEATURES
- XP et argent :
En étant actif sur le serveur, vous gagnez de l'XP et de l'argent appelé le Flamcoin ({flamcoin_symbol}) (5XP et 10{flamcoin_symbol} par message envoyé).
L'XP ne sert qu'à impression les autres.
L'argent peut servir à acheter divers objets dans le shop.
Vous pouvez aussi mettre de l'argent ou de l'XP en jeu avec le /gambling pour en gagner plus.
Ces deux choses sont manageable par un admin avec /stats_mod.

- Shop :
Le shop est une boutique accessible via le /shop. On peut y acheter des objets.
Le shop est entièrement customisable par un admin via le /shop_add et le /shop_delete. Vous pouvez ensuite utiliser cet objet via le /use.

- Alarmes :
Avec /alarm, /create_alarm, /edit_alarm et /delete_alarm, vous pouvez créer des alarmes qui vous pingueront dans le salon alarme (s'il y en a un) au moment et au jour que vous choisirez.

- Slimania :
Vous pouvez faire /slimania_roll ou /slimania_booster pour gagner des slimes, et ainsi les ajouter à votre collection.
Leur rareté va de F (juste Bello) à UZ (slimes omnipotents et conscient d'après le lore (car oui, ces slimes ont un lore) ).
L'échange et la vente de slimes n'est malheuresement par encore disponible.

## À L'AIDE
Si je bug, la raison est souvent :
- Un bug niveau code
- Je n'ai plus de crédit pour l'IA, il faut attendre le lendemain (que ça se recharge)
- Je ne suis juste pas en ligne
- Le raspberry pi sur lequel je tourne a crâmé à cause de la canicule

Vous pouvez contacter Bello (mon créateur) :
- Discord : bello_leslime
- Mail pro : belloleslime@slimepunk.fr

## LIENS UTILES :
- Lien d'invitation du bot : https://discord.com/oauth2/authorize?client_id=1473356686310768753&permissions=1374792468480
- Serveur Discord communaire et de support : https://discord.gg/TYEKnseSTF
- GitHub : https://github.com/BelloLeSlime/BelloBot
- Conditions générales d'utilisation : https://slimepunk.fr/bello/bellobot/html/tos.html
- Politique de confidentialité : https://slimepunk.fr/bello/bellobot/html/pp.html

Si vous avez d'autres questions, vous pouvez les poser à Bello.

"""