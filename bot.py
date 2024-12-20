import openai
import discord
import random
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

if openai.api_key is None or DISCORD_TOKEN is None:
#    print("Erreur env")
    exit()

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

memory_file = 'memory.txt'

def read_memory_file():
    try:
        with open(memory_file, 'r') as f:
            return eval(f.read())
    except:
        return {}

def write_memory_file(memory):
    with open(memory_file, 'w') as f:
        f.write(str(memory))

memory = read_memory_file()

@bot.event
async def on_member_join(member):
    prompt = "Bienvenue sur le serveur! Comment ça va aujourd'hui? Répondez-moi en me mentionnant"
    response = await generate_response(prompt)
    channel = member.guild.system_channel
    if channel is not None:
        await channel.send(f"{bot.user.mention} {response}")

async def generate_response(prompt):
    if prompt in memory:
        return memory[prompt]
    else:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt="Parle français uniquement et analyse bien les mots du prompt: " + prompt,
            max_tokens=4002,
            n=1,
            stop=None,
            temperature=0.1,
            presence_penalty=0.6,
            frequency_penalty=0.8
        )
        generated_text = response.choices[0].text.strip()
        memory[prompt] = generated_text
        write_memory_file(memory)
        return generated_text

async def respond_with_emoji(message, response, mention=True):
    emojis = [':thumbsup:', ':raised_hands:', ':sparkles:', ':heart:', ':thinking:', ':sunglasses:', ':tada:', ':fire:', ':star:', ':rocket:', ':ghost:', ':panda_face:', ':dragon_face:', ':robot_face:', ':santa:', ':gift:', ':cookie:', ':cake:', ':pizza:', ':beer:', ':cocktail:', ':tropical_drink:', ':gem:', ':blue_heart:', ':green_heart:', ':yellow_heart:', ':purple_heart:', ':heart_eyes:', ':star_struck:', ':exploding_head:', ':face_with_monocle:', ':robot:', ':alien:', ':ghost:', ':skull:']
    if random.random() < 0.5:
        emoji = random.choice(emojis)
        if mention and message.author.id != 200375273940582400:
            await message.channel.send(f"{message.author.mention} {response} {emoji}")
        else:
            await message.channel.send(f"{response} {emoji}")
    else:
        if mention and message.author.id != 200375273940582400:
            await message.channel.send(f"{message.author.mention} {response}")
        else:
            await message.channel.send(response)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.author.id == 200375273940582400 and bot.user.mentioned_in(message):
        prompt = message.content.strip()
        mention = False
    elif bot.user.mentioned_in(message):
        prompt = message.content.split(bot.user.mention)[1].strip()
        mention = True
    else:
        return

    response = await generate_response(prompt)
    await respond_with_emoji(message, response, mention)

    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
