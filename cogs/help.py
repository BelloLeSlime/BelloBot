import discord
from discord.ext import commands
import bot_package.custom_func as Cf
from bot_package.data import flamcoin_symbol

class Help(commands.Cog):
    """
    Commande help
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help")
    async def help(self, ctx: commands.Context):
        """
        Affiche l'aide
        :param ctx: Context
        :return:
        """
        embed = discord.Embed(color=discord.Color.green())
        embed.title = "Bonjour, je suis BelloBot"
        embed.description = f"""
        Je suis un bot discord avec de l'IA, et je vais vous aider à me configurer et à m'utiliser.

        ## COMMENT M'UTILISER
        Pour utiliser la fonctionnalité IA, tu as juste à me ping normalement, comme un vrai utilisateur. Je réponds à tes questions, et je vois également les messages qui ne me sont pas addressé pour plus de contexte.

        ## MES COMMANDES
        J'ai plusieurs commandes :
        
        - IA
        -`/ask <prompt>` : une alternative à simplement me ping, peut être utilisé dans un serveur où l'on peut utiliser des applications externes si l'on m'a ajouté dans ses applications
        -`/generate_image <prompt> (<negative_prompt> <width> <height> <steps>) : ❌Temporairement désactivée : Génère une image qui contient <prompt>, ne contient pas <negative_prompt> et fait <width> par <height>, pour <steps> étapes (en gros qualité). Le prix de la commande s'élève à 500 + <steps> {flamcoin_symbol}.
        -`/vote_reset_memory` : Organise un vote de 1 minute pour réinitialiser la mémoire de BelloBot ou pas (très très pratique quand il pert la tête ma foi)
        
        - STATS
        -`/xp (<user>)` : affiche l'xp et le niveau d'un utilisateur <user>
        -`/wallet (<user>)` : affiche le montant d'argent d'un utilisateur <user>
        -`/stats (<user>)` : affiche les statistiques d'un utilisateur (xp, argent, inventaire, effets temporaires, ect
        -`/gift <user> <what> <amount> : ✨Nouveau : Vous donnez <amount> <what> (XP ou argent) à <user>
        
        - SHOP ET ITEMS
        -`/shop` : affiche le magasin où on peut acheter plusieurs objets
        -`/use <item> (<target_user> <name> <time_in_hour>)` : utilise un objet <item>. <target_user> est utilisé pour le Nametag et le Ban hammer. <name> est utilisé par le Nametag. <time_in_hour> est utilisé par le Ban hammer
        -`/inventory (<user>)` : affiche l'inventaire d'un utilisateur <user>
        
        - ALARMES
        -`/alarm` : ouvre le panel des alarmes, où on peut y retrouver toutes les alarmes de l'utilisateur
        -`/create_alarm <name> <hour> <minutes> (<enabled> = True <repeat> = False <lundi> = False <mardi> = False <mercredi> = False <jeudi> = False <vendredi> = False <samedi> = False <dimanche> = False)` : crée une alarme qui vous ping quand c'est l'heure (et si elle est activée). Pour le système des jours, je sais, c'est shlag, mais Bello ce nœuille a pas réussi à faire un truc mieux que ça donc c'est brainrot.
        -`/edit_alarm <id> (<name> <hour> <minutes> <enabled> <repeat> <lundi> <mardi> <mercredi> <jeudi> <vendredi> <samedi> <dimanche>)` : modifie une alarme selon son ID. Son ID est le numéro qui s'affiche à côté du nom de l'alarme dans le `/alarm`. Chaque argument modifié changement celui d'origine
        -`/delete_alarm <id>` : supprime une alarme selon son ID
        
        - GAMBLING
        -`/gambling <game> <bet> <what>` : ✨Nouveau : Jeu à un jeu <game> pour parier <bet> d'XP ou d'argent (<what>) et que la chance soit entre tes mains !
        -`/gambling_quote` : ✨Nouveau : Affiche une citation de gambling (vient de Gamble with your Friends)

        ## XP ET ARGENT
        L'XP et l'argent se gagnent tous deux en étant simplement actif sur le serveur. 5 XP / msg, et 10{flamcoin_symbol} / msg.
        L'XP ne sert à absolument rien si ce n'est flex devant les gens du serveur.
        L'argent du bot s'appelle le Flamcoin, dit {flamcoin_symbol}, il permet d'acheter des objets au shop.
        """
        await ctx.send(embed=embed)

        embed = discord.Embed(title="", description=
        """
        ## COMMANDES ADMIN
        
        - PRATIQUE
        -`/config <key> <value>` : configure le bot. Il y a différents types de valer attendues. Par exemple, la clé xp_channel (pour le salon où le bot envoie les passages de niveau) n'accepte que les salons texte.
        -`/embed <title> <description> <color>` : fait dire au bot ce que vous voulez dans un embed
        
        - MODÉRATION STATS
        -`/stats_mod <user> <what> <how> <amount>` : ✨Nouveau : Permet de gérer l'XP, les niveaux et l'argent de <user>. <what> correspond à l'XP, au niveau ou à l'argent, et <how> correspond à add (ajouter), remove (enlever), set (mettre), et reset (réinitialiser).
        -`/reset` : reset tout le serveur en XP, niveaux et argent
        
        - IA ET SOUVENIRS
        -`/reset_memory` : supprime la mémoire de l'IA (très pratique quand le bot pert la tête ma foi)
        -`/remembers` : affiche le panel des souvenirs. Un souvenir est un message que je n'oublierai jamais, comme une règle où quelque comme ça
        -`/add_remember <message>` : ajoute un souvenir à ceux du bot
        -`/delete_remember <id>` : supprime un souvenir selon son ID. L'ID est le nombre à côté du message du souvenir dans le `/remembers`
        
        ## À L'AIDE !
        Si le bot a un problème, n'hésitez pas à demander en MP à son crétaeur, bello_leslime, pour qu'il regarde les logs. Le problème est souvent :
        -**Un bug niveau code**
        -**Vous n'avez pas assigné chaque rôle achetable et le salon XP** (demander à un admin de la configurer. Si vous n'en voulez pas, assignez les à des rôles et salons bidons.)
        -**Je n'ai plus de crédits pour l'IA** : étant donné que j'utilise le plan gratuit d'HuggingFace, je n'ai que 10c gratuit / mois, et c'est probable que trop de requêtes ont été faites que l'IA ne puisse pas répondre.
        -**Bello ce chien m'a coupé et a oublié de me rallumer**
        -**Le Raspbberry Pi sur lequel je tourne a cramé à cause de la canicule**, et donc vous ne verrez plus JAMAIS votre argent ou votre XP.

        ## CONTACTER BELLO LE SLIME
        Vous pouvez contacter ce sussy baka sur Discord : bello_leslime, ou via son mail pro : belloleslime@slimepunk.fr
        
        ## LIENS UTILES
        -https://github.com/BelloLeSlime/BelloBot : github
        -https://slimepunk.fr/bello/bellobot : site officiel du bot
        -https://discord.gg/TYEKnseSTF : serveur discord communautaire
        -https://discord.com/oauth2/authorize?client_id=1473356686310768753 : lien d'invitation du bot
        -https://slimepunk.fr/bello/bellobot/html/tos.html : Conditions d'utilisation
        -https://slimepunk.fr/bello/bellobot/html/pp.html : Politique de confidentialité

        > Si vous avez d'autres questions, vous pouvez les poser à Bello le Slime.)
        """, color=discord.Color.green())
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="ping")
    async def ping(self, ctx: commands.Context):
        """
        Dit "Pong !"
        :param ctx: Context
        :return:
        """
        await ctx.send("Pong !")

async def setup(bot):
    await bot.add_cog(Help(bot))