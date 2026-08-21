import discord
from discord.ext import commands
import bot_package.custom_func as Cf
import yt_dlp

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="join")
    async def join(self, ctx: commands.Context, channel: discord.VoiceChannel = None):
        """
        Rejoin un salon vocal
        :param ctx:
        :param channel: Salon vocal à rejoindre
        :return:
        """
        if channel is None:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
            else:
                embed = discord.Embed(color=discord.Color.red(), description="Veuillez rejoindre un salon vocal ou en indiquer un !")
                await ctx.send(embed=embed)
                return
        else:
            channel = channel

        if ctx.voice_client:
            if ctx.voice_client.channel == channel:
                embed = discord.Embed(color=discord.Color.red(), description="Je suis déjà connecté à ce salon !")
                await ctx.send(embed=embed)
                return
            else:
                await ctx.voice_client.disconnect(force=False)

        await channel.connect()
        embed = discord.Embed(color=discord.Color.green(), description="Je suis connecté !")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="leave")
    async def leave(self, ctx: commands.Context):
        """
        Quitte un salon vocal
        :param ctx:
        :return:
        """
        if ctx.voice_client:
            await ctx.voice_client.disconnect(force=False)
        else:
            embed = discord.Embed(color=discord.Color.red(), description="Je ne suis pas dans un salon vocal")
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(color=discord.Color.green(), description="J'ai bien quitté le salon vocal !")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="music_play")
    async def music_play(self, ctx: commands.Context, music: str):
        """
        Joue une musique dans un salon vocal
        :param ctx:
        :param music: Musique (titre ou url)
        :return:
        """
        config = Cf.get_config(ctx.guild.id)
        if not config["enable_music"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais la musique n'est pas activée sur ce serveur !"),
                           ephemeral=True)
            return

        await ctx.defer()

        if ctx.author.voice:
            channel = ctx.author.voice.channel
        else:
            embed = discord.Embed(color=discord.Color.red(),
                                  description="Veuillez rejoindre un salon vocal !")
            await ctx.send(embed=embed)
            return

        if not ctx.voice_client:
            voice_client = await channel.connect()

        elif ctx.voice_client.channel != channel:
            voice_client = await channel.connect()
        else:
            voice_client = ctx.voice_client


        if music.startswith(("http://", "https://")):
            search = music
        else:
            search = f"ytsearch1:{music}"

        ydl_options = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "quiet": True,
        }


        with yt_dlp.YoutubeDL(ydl_options) as ydl:
            info = ydl.extract_info(search, download=False)

            if "entries" in info:
                info = info["entries"][0]

            audio_url = info["url"]
            title = info.get("title", music)


        if voice_client.is_playing():
            voice_client.stop()

        ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }

        source = discord.FFmpegPCMAudio(
            audio_url,
            **ffmpeg_options
        )

        voice_client.play(source)

        await ctx.send(
            f"▶️ Lecture de **{title}**"
        )

        user_data = Cf.get_user_data(ctx.author.id, ctx.guild.id)
        if not "music_stats" in user_data:
            user_data["music_stats"] = {}

        if not title in user_data["music_stats"]:
            user_data["music_stats"][title] = 0

        user_data["music_stats"][title] += 1
        Cf.set_user_data(ctx.author.id, ctx.guild.id, user_data)

    @commands.hybrid_command(name="music_stop")
    async def music_stop(self, ctx: commands.Context):
        """
        Stop une musique
        :param ctx:
        :return:
        """
        config = Cf.get_config(ctx.guild.id)
        if not config["enable_music"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais la musique n'est pas activée sur ce serveur !"),
                           ephemeral=True)
            return

        if ctx.voice_client:
            voice_client = ctx.voice_client
            if voice_client.is_playing():
                voice_client.stop()
                await ctx.send("Musique arrêtée")
                return

        await ctx.send("Aucune musique en cours")

    @commands.hybrid_command(name="music_stats")
    async def music_stats(self, ctx: commands.Context, user: discord.User = None):
        """
        Permet de voir les morceaux qu'un utilisateur écoute
        :param ctx:
        :param user: Utilisateur
        :return:
        """
        config = Cf.get_config(ctx.guild.id)
        if not config["enable_music"]:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(),
                                               description=f"Désolé, mais la musique n'est pas activée sur ce serveur !"),
                           ephemeral=True)
            return

        if user is None:
            user = ctx.author

        user_data = Cf.get_user_data(user.id, ctx.guild.id)
        if not "music_stats" in user_data:
            user_data["music_stats"] = {}

        music_stats = user_data["music_stats"]
        music_stats = sorted(music_stats.items(), key=lambda item: item[1], reverse=True)
        music_str = ""
        for (music, amount) in music_stats:
            music_str += f"**{music}** - Écouté {amount} fois\n"
        if music_str == "":
            music_str = "Vide..."

        embed = discord.Embed(color=discord.Color.green(), description=music_str, title=f"Musiques écoutées par {user.display_name}")
        await ctx.send(embed=embed)



async def setup(bot):
    await bot.add_cog(Voice(bot))