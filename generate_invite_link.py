"""
[I am an idiot and i need this too invite the bot]

Script to generate the bot's Discord invite link.
Run this and copy the link that appears.
"""
import os
from dotenv import load_dotenv
import base64

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Extract Application ID from the token
app_id = base64.b64decode(BOT_TOKEN.split('.')[0] + '==').decode('utf-8')

permissions = 380104722496

# Generate invite URL
invite_url = f"https://discord.com/api/oauth2/authorize?client_id={app_id}&permissions={permissions}&scope=bot"

print("=" * 80)
print("🤖 BOT INVITE LINK")
print("=" * 80)
print()
print("Copy this link and open it in your browser:")
print()
print(invite_url)
print()
print("=" * 80)
print()
print("Instructions:")
print("1. Copy the link above")
print("2. Paste it into your browser")
print("3. Select the server where you want to add the bot")
print("4. Click 'Authorize'")
print("5. Complete the captcha if it appears")
print()
print("Permissions included:")
print("  ⚡ ADMINISTRATOR (all permissions)")
print()
print("⚠️  WARNING: The bot will have full access to the server.")
print("   Only use this if you fully trust the bot.")
print()
print("=" * 80)
