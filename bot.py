import discord
import requests
import os
import time
from discord.ext import commands

# Set your bot token and VirusTotal API key here
BOT_TOKEN = 'SET_DISCORD_TOKEN_HERE'
VT_API_KEY = 'SEND_ME_CAT_PICS'
ZIP_PASSWORD = 'infected'  # Password for encrypted zip files

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.tree.command(name="vt_download", description="Create a ZIP file from VirusTotal samples")
async def vt_download(interaction: discord.Interaction, hashes: str):
    
    hash_list = [h.strip() for h in hashes.split(',')]
    print(f"Hashes received: {hash_list}")

    payload = {
        "data": {
            "password": ZIP_PASSWORD,
            "hashes": hash_list
        }
    }

    create_zip_url = "https://www.virustotal.com/api/v3/intelligence/zip_files"
    headers = {
        'x-apikey': VT_API_KEY,
        'Content-Type': 'application/json'
    }
    
    print(f"Creating ZIP file with URL: {create_zip_url}")
    response = requests.post(create_zip_url, json=payload, headers=headers)
    
    if response.status_code == 200:
        zip_data = response.json()
        zip_id = zip_data['data']['id']
        print(f"ZIP file creation request successful, ID: {zip_id}")

        await interaction.response.send_message("ZIP file creation in progress... Please wait.")

        time.sleep(30) # Maybe increase if your internet sucks or samples are chonky.

        download_url = f"https://www.virustotal.com/api/v3/intelligence/zip_files/{zip_id}/download"
        print(f"Downloading ZIP file with URL: {download_url}")
        download_response = requests.get(download_url, headers=headers)
        
        if download_response.status_code == 200:
            zip_file_path = f"vt_sample_{zip_id}.zip"
            with open(zip_file_path, 'wb') as f:
                f.write(download_response.content)

            await interaction.followup.send(file=discord.File(zip_file_path))

            os.remove(zip_file_path)
            print("ZIP file uploaded and cleaned up.")
        else:
            print(f"Failed to download ZIP file, HTTP status code: {download_response.status_code}")
            await interaction.followup.send("Failed to download the ZIP file.")
    else:
        print(f"Failed to create ZIP file, HTTP status code: {response.status_code}")
        await interaction.response.send_message("Failed to create the ZIP file. Please check the hashes.")

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user}!')

bot.run(BOT_TOKEN)
