import discord
from discord.ext import commands
from discord import app_commands
import bot_package.custom_func as Cf
import asyncio
import os

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

        config = Cf.get_config(ctx.guild.id)
        if not config["enable_ai"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais l'IA n'est pas activé sur ce serveur !"),
                           ephemeral=True)
            return

        if ctx.guild:
            await ctx.defer()

            Cf.check_guild_has_presence(ctx.guild.id)
            Cf.check_has_data_file(ctx.author.id, ctx.guild.id)
            content = prompt
            author = ctx.author.display_name

            try:
                answer = await Cf.ask_ai(content, ctx.author.display_name, ctx.guild.id)
                to_send = await Cf.parse_text(answer, ctx, False)
                try:
                    await ctx.send(to_send)
                except discord.HTTPException:
                    await ctx.send(to_send[:1975] + "... <message trop long>")
            except:
                await Cf.warn_no_more_credits(ctx=ctx)
                return

            Cf.write_file(author + " : " + content, f"files/messages/{ctx.guild.id}.txt")
            Cf.write_file("BelloBot(forbellobot) : " + to_send, f"files/messages/{ctx.guild.id}.txt")

        else:
            await ctx.defer()

            if not str(ctx.author.id) + ".txt" in os.listdir("files/dms/"):
                Cf.write_file("", "files/dms/" + str(ctx.author.id) + ".txt")

            content = prompt
            author = ctx.author.display_name
            try:
                answer = await Cf.ask_ai(content, ctx.author.display_name, ctx.guild.id, dm=True)
                to_send = await Cf.parse_text(answer, ctx, True)
                try:
                    await ctx.send(to_send)
                except discord.HTTPException:
                    await ctx.send(to_send[:1975] + "... <message trop long>")
            except:
                await Cf.warn_no_more_credits(ctx=ctx)
                return
            Cf.write_file(author + " : " + content, f"files/dms/{ctx.author.id}.txt")
            Cf.write_file("BelloBot(forbellobot) : " + to_send, f"files/dms/{ctx.author.id}.txt")

    @commands.hybrid_command(name="vote_reset_memory")
    async def vote_reset_memory(self, ctx: commands.Context):
        """
        Créé un vote pour réinitialiser la mémoire du bot si ce dernier pert la tête
        :param ctx: Context
        :return:
        """

        config = Cf.get_config(ctx.guild.id)
        if not config["enable_ai"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais l'IA n'est pas activé sur ce serveur !"), ephemeral=True)
            return

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

    @commands.hybrid_command(name="reset_dm_memory")
    async def reset_dm_memory(self, ctx: commands.Context):
        """
        Réinitialise la mémoire du bot dans les messages privés
        :param ctx:
        :return:
        """

        if ctx.guild:
            await ctx.send("Cette commande n'est utilisable que dans des messages privées.", ephemeral=True)

        user_id = ctx.author.id
        with open(f"files/dms/{user_id}.txt", "w", encoding="utf-8") as f:
            f.write("")

        embed = discord.Embed(color=discord.Color.orange(), description="Ma mémoire dans les MP est réinitialisée.")
        await ctx.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(name="ai_ignore_add")
    @commands.has_permissions(administrator=True)
    async def ai_ignore_add(self, ctx: commands.Context, channel: discord.TextChannel):
        """
        ADMIN SEULEMENT - ajoute un salon dans lequel l'IA ne peut pas interagir (voir ou parler)
        :param ctx:
        :param channel: Salon dans lequel l'IA est interdite
        :return:
        """
        config = Cf.get_config(ctx.guild.id)
        if not config["enable_ai"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais l'IA n'est pas activé sur ce serveur !"),
                           ephemeral=True)
            return

        ai_ignore = Cf.get_ai_ignore(ctx.guild.id)
        if not channel.id in ai_ignore["channels"]:
            ai_ignore["channels"].append(channel.id)
            embed = discord.Embed(color=discord.Color.green(), description=f"Désormais, l'IA est désactivée dans {channel.mention}.")
            await ctx.send(embed=embed, ephemeral=True)
            Cf.set_ai_ignore(ctx.guild.id, ai_ignore)
        else:
            embed = discord.Embed(color=discord.Color.red(), description=f"L'IA est déjà désactivée dans {channel.mention}.")
            await ctx.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(name="ai_ignore")
    @commands.has_permissions(administrator=True)
    async def ai_ignore(self, ctx: commands.Context):
        """
        ADMIN SEULEMENT - Permet d'avoir la liste des salons ignorés par l'IA
        :param ctx:
        :return:
        """
        config = Cf.get_config(ctx.guild.id)
        if not config["enable_ai"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais l'IA n'est pas activé sur ce serveur !"),
                           ephemeral=True)
            return

        ai_ignore = Cf.get_ai_ignore(ctx.guild.id)
        embed = discord.Embed(color=discord.Color.blue(), title="Salons AI Ignore du serveur", description=f"")
        for channel_id in ai_ignore["channels"]:
            embed.description += f"- <#{channel_id}>\n"
        embed.description += f"Dans ces salons, l'IA ne pourra ni parler, ni voir quelconque message."
        await ctx.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(name="ai_ignore_remove")
    @commands.has_permissions(administrator=True)
    async def ai_ignore_remove(self, ctx: commands.Context, channel: discord.TextChannel):
        """
        ADMIN SEULEMENT - Enlève l'interdiction à l'IA
        :param ctx:
        :param channel:
        :return:
        """
        config = Cf.get_config(ctx.guild.id)
        if not config["enable_ai"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(), description=f"Désolé, mais l'IA n'est pas activé sur ce serveur !"), ephemeral=True)
            return

        ai_ignore = Cf.get_ai_ignore(ctx.guild.id)
        if not channel.id in ai_ignore["channels"]:
            embed = discord.Embed(color=discord.Color.red(), description=f"Le salon {channel.mention} n'est pas en AI Ignore.")
            await ctx.send(embed=embed, ephemeral=True)
            return
        ai_ignore["channels"].remove(channel.id)
        Cf.set_ai_ignore(ctx.guild.id, ai_ignore)
        embed = discord.Embed(color=discord.Color.green(), description=f"Le salon {channel.mention} n'est plus en AI Ignore.")
        await ctx.send(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Ai(bot))