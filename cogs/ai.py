import discord
from discord.ext import commands
import bot_package.custom_func as Cf
from bot_package.data import model, system, image_model, flamcoin_symbol
import asyncio
from datetime import timedelta

class Ai(commands.Cog):
    """
    Toutes les commandes impliquant l'IA
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ask")
    async def ask(self, ctx: commands.Context, prompt: str):
        """
        Alternative à juste ping
        :param ctx: Context
        :param prompt: Demande faite à l'IA
        :return:
        """
        Cf.check_guild_has_presence(ctx.guild.id)
        Cf.check_has_data_file(ctx.author.id, ctx.guild.id)
        content = prompt
        author = ctx.author.display_name
        Cf.write_file(author + " : " + content, f"files/messages/{ctx.guild.id}.txt")
        messages = Cf.get_messages(ctx.guild.id, system)
        try:
            answer = Cf.ask_ai(messages, model)
            Cf.write_file("BelloBot(forbellobot) : " + answer, f"files/messages/{ctx.guild.id}.txt")
            await ctx.send(answer)
        except:
            await Cf.warn_no_more_credits(ctx=ctx)

    @commands.hybrid_command(name="vote_reset_memory")
    async def vote_reset_memory(self, ctx: commands.Context):
        """
        Créé un vote pour réinitialiser la mémoire du bot si ce dernier pert la tête
        :param ctx: Context
        :return:
        """
        await ctx.send("Vote organisé !", ephemeral=True)
        embed = discord.Embed(color= discord.Color.orange(), title="Voulez-vous réinitialiser ma mémoire car je deviens fou ?", description="Réagir 👍 pour oui.").set_footer(text="Fin du vote dans 1min !")
        msg = await ctx.channel.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

        await asyncio.sleep(60)
        msg = await ctx.channel.fetch_message(msg.id)

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
            await ctx.channel.send("Ma mémoire va être réinitialisée...")
            with open(f"files/messages/{ctx.guild.id}.txt", "w", encoding="utf-8") as f:
                f.write("")
        else:
            await ctx.channel.send("Ma mémoire ne sera pas réinitialisée !")

    @commands.command(name="generate_image")
    async def generate_image(self, ctx: commands.Context, prompt: str, negative_prompt: str = "", width: int = 1024, height: int = 1024, steps: int = 30):
        f"""
        Génère une image pour la modique somme de 500{flamcoin_symbol} + le nombre d'étapes
        :param ctx: 
        :param prompt: Description de l'image
        :param negative_prompt: Ce qu'il n'y a pas dans l'image
        :param width: Largeur de l'image en pixels
        :param height: Hauteur de l'image en pixels
        :param steps: Étapes (donc qualité grossomodo)
        :return: 
        """

        #Commande désactivée à cause du prix des IA, commentez ou supprimez si vous avec les moyens
        await Cf.warn_no_more_credits(ctx)
        return

        await ctx.defer()

        user_data = Cf.read_json(f"files/user_info/{ctx.guild.id}/{ctx.author.id}.json")
        if user_data["money"] >= 500 + steps:

            nude_str: str = Cf.ask_ai([{"role": "system",
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
                    await ctx.send(
                        f"Regardez, {ctx.author.mention} a essayé de générer une image de {prompt} mais a pas réussi ce nul XD \n Allez 1 jour de mute pour toi :p")
                    await ctx.author.timeout(timedelta(days=1), reason="Essaie de générer une image suspecte")
                else:
                    user_data["money"] -= 500
                    Cf.write_json(user_data, f"files/user_info/{ctx.guild.id}/{ctx.author.id}.json")
                    image = Cf.text_to_image(prompt, image_model, negative_prompt, width, height, steps)
                    await Cf.send_image(ctx, image)
            else:
                await ctx.send("AAaah j'arrive pas à décider si ça passe ou non jsp quoi faire")
        else:
            await ctx.send(
                f"Tu n'a pas assez d'argent pour générer une image ! La génération d'image coûte 500₣ + le nombre d'étapes (ici {steps}) pour éviter le spam et la déchéance économique de Bello le Slime.")


async def setup(bot):
    await bot.add_cog(Ai(bot))