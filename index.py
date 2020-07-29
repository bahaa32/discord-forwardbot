from io import BytesIO
import discord
import aiohttp
import asyncio

# Secrets, webhook URL and client token
secret_url = "YOUR_WEBHOOK_URL"
secret_token = "YOUR_SECRET_TOKEN"

# Initialize client before functions so I can use decorators
client = discord.Client()


# Log when client login occurs
@client.event
async def on_ready():
    global webhook
    global session
    print('Logged in as {0.user}'.format(client))
    # Create new aiohttp session
    session = aiohttp.ClientSession()
    # Initialize webhook
    webhook = discord.Webhook.from_url(secret_url, adapter=discord.AsyncWebhookAdapter(session))

# Listen to all messages
@client.event
async def on_message(message):
    if message.author == client.user or message.webhook_id != None:
        return
    await forward_message(message)

# Take message object, forward it to webhook
async def forward_message(message):
    global webhook
    global session
    # Pick first 4 attachments if there are more than 4 attachments in a message
    if len(message.attachments) > 4:
        del message.attachments[4:]
    # Iterate through attachments in message
    for idx, attachment in enumerate(message.attachments):
        # Ignore files larger than 100 megabytes
        if attachment.size > 100 * (1024 ^ 2):
            # Delete attachment
            del message.attachments[idx]
            continue
        # Download attachment and cast to a buffer
        async with session.get(attachment.url) as resp:
            # Repurpose attachments list (perhaps not a good idea)
            message.attachments[idx] = discord.File(fp=BytesIO(await resp.read()), filename=attachment.filename, spoiler=attachment.is_spoiler())
    # Send message through webhook
    await webhook.send(content=f"`#{message.channel.name}` " + message.clean_content, username=message.author.display_name, avatar_url=message.author.avatar_url, files=message.attachments, embeds=message.embeds)

# TODO: Exit gracefully and end aiohttp session

# Let's go :)
client.run(secret_token)
