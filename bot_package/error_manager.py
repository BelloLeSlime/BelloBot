import discord
import uuid
import time


async def mk_error_file(error_trace, ctx, command):
    error_info = ("\nError message :"
                  f"\n{error_trace}"
                  "\n"
                  f"\n- Nom d'utilisateur / id : {ctx.author.name}/{ctx.author.id}"
                  f"\n- Heure de l'erreur : {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
                  f"\n- Commande qui a causé l'erreur : {command}")
    file_name = uuid.uuid4()

    with open(f"./files/error/{file_name}.txt", "w", encoding="utf-8") as f:
        f.write(error_info)
    with open(f"./files/error/last.txt", "w", encoding="utf-8") as f:
        f.write(error_info)

    error_embed = discord.Embed(
        title="Il y a eu une erreur...",
        description="Vous pouvez réessayer plus tard, ou transmettre les infos suivantes sur le discord de BelloBot :",
        color=discord.Color.red()
    )
    error_embed.add_field(name="Informations :",
                          value=f"> - Code d'erreur : {file_name}")
    error_embed.add_field(name="Merci de transmettre le code d'erreur dans ce serveur :",
                          value="> https://discord.gg/TYEKnseSTF",
                          inline=False)
    await ctx.send(embed=error_embed)
    return error_info