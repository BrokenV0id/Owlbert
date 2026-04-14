# ========= LIBRARIES =========
import numpy as np
from sentence_transformers import SentenceTransformer

import discord
from discord.ext import commands
import asyncio

import requests
import random
import json


#==============================================================





# ========= VARIABLES =========
command_model = SentenceTransformer("models/minilm")

with open("commands.json", "r") as file:
    data = json.load(file)
known_commands = list(data.keys()) + ["can you reload known commands"]

command_vectors = command_model.encode(known_commands)
command_vectors = command_vectors / np.linalg.norm(command_vectors, axis=1, keepdims=True)

BOT_TOKEN = "" # Bot token goes here
OWNER_ID = 0 # Owner ID goes here

intents = discord.Intents.default()
intents.messages = True
intents.dm_messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

#==============================================================






# ========= FUNCTIONS =========
def extract_number(message):
    finished_number = ""
    for char in message:
        if char in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]:
            finished_number += char

    print(finished_number)
    return finished_number
    
def refresh_known_commands():
    global data, known_commands, command_vectors
    with open("commands.json", "r") as file:
        data = json.load(file)
    known_commands = list(data.keys()) + ["can you reload known commands"]
    
    command_vectors = command_model.encode(known_commands)
    command_vectors = command_vectors / np.linalg.norm(command_vectors, axis=1, keepdims=True)

def send_http_request(url, header):
    response = requests.get(url, headers=header).text
    if response:
        return 0, response
    else:
        return 1, ""
    
def send_request(url):
    response = requests.get(url)
    
def input_to_command(text):
    vector = command_model.encode([text])[0]
    vector = vector / np.linalg.norm(vector)
    scores = np.dot(command_vectors, vector)

    best_index = np.argmax(scores)
    best_score = scores[best_index]

    confidence = round(float(best_score), 2)

    command = known_commands[best_index]
    return command, confidence
    
@bot.event
async def on_ready():
    print("Bot conntection complted.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.author.id != OWNER_ID:
        return
    if not isinstance(message.channel, discord.DMChannel):
        return
    
    command_to_run, confidence = input_to_command(message.content.lower())
    reply = f"Sorry, I don't know that one."
    if confidence > 0.5:
        if command_to_run == "can you reload known commands":
            refresh_known_commands()
            reply = f"Sure! Updating known commands. **[{confidence}]**"
        else:
            url = data[command_to_run]["url"]
            header = data[command_to_run]["headers"]
            include_number = data[command_to_run]["include_number"]

            if include_number == True:
                url += extract_number(message.content.lower())
                
            response_type, response = send_http_request(url, header)
            if response_type == 0: # no error
                reply = f"{response} **[{confidence}]**"
            elif response_type == 1: # error found
                reply = f"{random.choice(data[command_to_run]["error_messages"])} **[{response}, {confidence}]**"

    await message.channel.send(reply)

bot.run(BOT_TOKEN)
