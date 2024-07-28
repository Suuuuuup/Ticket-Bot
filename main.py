import discord
from discord.ext import commands
from discord.ui import Select, View, Button
import io

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="+", intents=intents)

# ID du rôle de modérateur (modifiez cette valeur avec l'ID de votre rôle de modérateur)
MOD_ROLE_ID = 1267183290184372326  # Remplacez par l'ID de votre rôle de modérateur

# Emebed Pour le ticket
ticket_embed = discord.Embed(
    title="Support !",
    description="Sélectionnez le type de ticket que vous souhaitez créer:", #A toi de mettre le message que tu veut !
    color=0x00ff00
)

# Dropdown menu pour la sélection de ticket
class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Support Technique", description="Créer un ticket pour un support technique"),
            discord.SelectOption(label="Question Générale", description="Créer un ticket pour une question générale"),
            discord.SelectOption(label="Signalement de Bug", description="Créer un ticket pour signaler un bug"),
            #discord.SelectOption(label="Change", description="Change"),
            #discord.SelectOption(label="Change", description="Change"),
            #discord.SelectOption(label="Change", description="Change"),
            #discord.SelectOption(label="Change", description="Change"),
            #discord.SelectOption(label="Change", description="Change") # c'est pour ajouté d'autre raison de ticket ta juste a retiré le # et remplace les " change " par se que tu veut
        ] 
        super().__init__(placeholder="Sélectionnez une option...", min_values=1, max_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        category_name = self.values[0]
        guild = interaction.guild

        # Trouver ou créer la catégorie 'Tickets'
        category = discord.utils.get(guild.categories, name="Tickets")
        if category is None:
            category = await guild.create_category("Tickets")

        # Créer un nouveau salon textuel sous la catégorie 'Tickets'
        channel = await category.create_text_channel(f"ticket-{interaction.user.name}")

        # Embed pour le salon de ticket
        ticket_channel_embed = discord.Embed(
            title="Ticket",
            description=f"{interaction.user.mention} a créé un ticket pour {category_name}.",
            color=0x00ff00
        )

        # Vue avec des boutons
        view = TicketChannelView()

        # Envoyer l'embed et la vue dans le salon de ticket
        await channel.send(embed=ticket_channel_embed, view=view)

        # Répondre à l'interaction
        await interaction.response.send_message(f"Votre ticket pour '{category_name}' a été créé : {channel.mention}", ephemeral=True)

# Vue qui contient le dropdown menu
class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class TicketChannelView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CloseButton())
        self.add_item(TranscriptButton())
        self.add_item(ClaimButton())

class CloseButton(Button):
    def __init__(self):
        super().__init__(label="Close Ticket", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        # Vérifie si l'utilisateur a le rôle de modérateur
        if MOD_ROLE_ID in [role.id for role in interaction.user.roles]:
            await interaction.channel.delete()
        else:
            await interaction.response.send_message("Vous n'avez pas la permission de fermer ce ticket.", ephemeral=True)

class TranscriptButton(Button):
    def __init__(self):
        super().__init__(label="Send Transcript", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        # Vérifie si l'utilisateur a le rôle de modérateur
        if MOD_ROLE_ID in [role.id for role in interaction.user.roles]:
            messages = []
            async for message in interaction.channel.history(limit=200):
                messages.append(message)

            transcript = ""
            for message in messages:
                transcript += f"{message.author.name}: {message.content}\n"

            transcript_file = discord.File(io.BytesIO(transcript.encode()), filename="transcript.txt")
            await interaction.user.send(file=transcript_file)
            await interaction.response.send_message("La transcription a été envoyée en message privé.", ephemeral=True)
        else:
            await interaction.response.send_message("Vous n'avez pas la permission d'envoyer la transcription.", ephemeral=True)

class ClaimButton(Button):
    def __init__(self):
        super().__init__(label="Claim Ticket", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction):
        # Vérifie si l'utilisateur a le rôle de modérateur
        if MOD_ROLE_ID in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message(f"{interaction.user.mention} a pris en charge ce ticket.", ephemeral=False)
        else:
            await interaction.response.send_message("Vous n'avez pas la permission de prendre en charge ce ticket.", ephemeral=True)

@bot.event
async def on_ready():
    print(f'{bot.user} est connecté!')
    bot.status = discord.Status.dnd
    activity = discord.Activity(type=discord.ActivityType.streaming, url="https://www.twitch.tv/suuuuup_", name="Ticket Bot") # Change avec t'es info :)
    await bot.change_presence(activity=activity)

@bot.command()
@commands.has_permissions(administrator=True)
async def ticket(ctx):
    view = TicketView()
    await ctx.send(embed=ticket_embed, view=view)


bot.run("") #Token de ton bot
