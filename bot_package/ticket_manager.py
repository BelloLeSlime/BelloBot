import discord
import bot_package.custom_func as Cf
import os
from datetime import datetime, UTC

class TicketClose(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Fermer le ticket", style=discord.ButtonStyle.green)
    async def close(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.defer()
        await close_ticket(interaction.user, interaction.guild, interaction.channel)


class TicketCreate(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Créer un ticket", style=discord.ButtonStyle.green, emoji="🎟️")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.defer()
        await create_ticket(interaction.guild, interaction.user)

def get_tickets(guild_id):
    if not f"{guild_id}.json" in os.listdir("files/tickets"):
        Cf.write_json({}, f"files/tickets/{guild_id}.json")
        return {}
    return Cf.read_json(f"files/tickets/{guild_id}.json")

def set_tickets(guild_id, tickets):
    Cf.write_json(tickets, f"files/tickets/{guild_id}.json")

async def create_ticket(guild: discord.Guild, user):
    tickets = get_tickets(guild.id)
    last_id = -1
    for ticket_id in tickets.keys():
        if int(ticket_id) > int(last_id):
            last_id = ticket_id

    id = int(last_id) + 1
    channel_name = f"ticket-{id}"

    config = Cf.get_config(guild.id)
    ticket_role = await guild.fetch_role(config["ticket_role"])

    if config["ticket_category"]:
        category = await guild.fetch_channel(config["ticket_category"])
        channel = await guild.create_text_channel(channel_name, category=category, overwrites={
        guild.default_role: discord.PermissionOverwrite(
            view_channel=False
        ),
        user: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True
        ),
        ticket_role: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True
        )
    })

    else:
        channel = await guild.create_text_channel(channel_name, overwrites={
        guild.default_role: discord.PermissionOverwrite(
            view_channel=False
        ),
        user: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True
        ),
        ticket_role: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True
        )
    })

    tickets[id] = channel.id
    set_tickets(guild.id, tickets)

    embed = discord.Embed(title=f"Ticket créé par {user.display_name}", color=discord.Color.green(), description=f"Dit ce pourquoi tu a créé un ticket !")
    await channel.send(f"{ticket_role.mention} - {user.mention}", embed=embed, view=TicketClose())

    ticket_logs_channel = await guild.fetch_channel(config["ticket_logs_channel"])
    now = datetime.now(UTC)
    now_str = now.strftime("%d/%m/%Y à %H:%M:%S")
    embed = discord.Embed(color=discord.Color.blue(), title=f"Création d'un ticket", description=
    f"""
    Créateur du ticket : {user.mention}
    Salon : {channel.mention}
    Date de création : {now_str}
""")
    await ticket_logs_channel.send(embed=embed)

async def close_ticket(user: discord.User, guild: discord.Guild, channel: discord.TextChannel):
    config = Cf.get_config(guild.id)
    role = await guild.fetch_role(config["ticket_role"])
    member: discord.Member = await guild.fetch_member(user.id)
    if not role in member.roles:
        await channel.send(
            f"Vous n'avez pas les permissions de fermer ce ticket ! Il faut avoir le rôle {role.mention}")
        return

    tickets = get_tickets(guild.id)
    ticket_id = -1
    for ticket in tickets:
        if tickets[ticket] == channel.id:
            ticket_id = ticket
            break

    del tickets[ticket_id]
    set_tickets(guild.id, tickets)

    await channel.delete()

    ticket_logs_channel = await guild.fetch_channel(config["ticket_logs_channel"])
    now = datetime.now(UTC)
    now_str = now.strftime("%d/%m/%Y à %H:%M:%S")
    embed = discord.Embed(color=discord.Color.blue(), title=f"Fermeture d'un ticket", description=
    f"""
                Personne ayant fermé le ticket : {user.mention}
                Salon : {channel.name}
                Date de fermeture : {now_str}
            """)
    await ticket_logs_channel.send(embed=embed)