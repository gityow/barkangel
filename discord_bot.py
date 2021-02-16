import discord
from discord import Webhook, RequestsWebhookAdapter, File

def get_discord_bot():
    
    WEBHOOK_ID="811006407406649345"
    WEBHOOK_TOKEN="OET0N1DeQxtgynVQyXJMCa3ERnDzahONqskjrHB-EafO4Os7pYWbJojVWjqkGH5ghlX7"

    # Create webhook
    webhook = Webhook.partial(WEBHOOK_ID, WEBHOOK_TOKEN, adapter=RequestsWebhookAdapter())
    
    return webhook