import discord
import os
client = discord.Client()


@client.event
async def on_ready():
    # when bot is ready
    print(f"we have logged in as {client.user}")


@client.event
async def on_message(message):
    # when a message is received
    if message.author == client.user:
        return
    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")
    # TODO implement check etf holdings
    # TODO check latest update of all etfs


client.run(os.getenv("TOKEN"))
