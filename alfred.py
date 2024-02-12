# Imports
import discord
from discord.ext import commands
import json
from datetime import date
from datetime import datetime
from collections import defaultdict
import io
import re
from strip_markdown import strip_markdown
import validators
import asyncio
from discord_pagination import PaginationView
import operator
from discord_secrets import *
import copy
import dotenv

CHARACTER_LIMIT = 3
PP_DEFAULT = 150
PL_DEFAULT = 10
thumbnail = 'https://i.imgur.com/1G3lVC1.png'

lock = asyncio.Lock()
ROSTER = {}

# This should only ever run on initialization
async def load_roster(serverid=SERVERID):
    global ROSTER
    try:
        with open(f'{serverid}.json', 'r') as f:
            ROSTER = json.loads(f.read())
    except FileNotFoundError:
        await save_roster()



async def save_roster(serverid=SERVERID):
    global ROSTER
    async with lock:
        with open(f'{serverid}.json', 'w') as f:
            f.write(json.dumps(ROSTER, indent=2))
    await load_roster()


RANK_TABLE = {
  "-5": {
    "**MASS**": "1.5 lb.",
    "**TIME**": "1/8 second",
    "**DISTANCE**": "6 inches",
    "**VOLUME**": "1/32 cft."
  },
  "-4": {
    "**MASS**": "3 lbs.",
    "**TIME**": "1/4 second",
    "**DISTANCE**": "1 foot",
    "**VOLUME**": "1/16 cft."
  },
  "-3": {
    "**MASS**": "6 lbs.",
    "**TIME**": "1/2 second",
    "**DISTANCE**": "3 feet",
    "**VOLUME**": "1/8 cft."
  },
  "-2": {
    "**MASS**": "12 lbs.",
    "**TIME**": "1 second",
    "**DISTANCE**": "6 feet",
    "**VOLUME**": "1/4 cft."
  },
  "-1": {
    "**MASS**": "25 lbs.",
    "**TIME**": "3 seconds",
    "**DISTANCE**": "15 feet",
    "**VOLUME**": "1/2 cft."
  },
  "0": {
    "**MASS**": "50 lbs.",
    "**TIME**": "6 seconds",
    "**DISTANCE**": "30 feet",
    "**VOLUME**": "1 cft."
  },
  "1": {
    "**MASS**": "100 lbs.",
    "**TIME**": "12 seconds",
    "**DISTANCE**": "60 feet",
    "**VOLUME**": "2 cft."
  },
  "2": {
    "**MASS**": "200 lbs.",
    "**TIME**": "30 seconds",
    "**DISTANCE**": "120 feet",
    "**VOLUME**": "4 cft."
  },
  "3": {
    "**MASS**": "400 lbs.",
    "**TIME**": "1 minute",
    "**DISTANCE**": "250 feet",
    "**VOLUME**": "8 cft."
  },
  "4": {
    "**MASS**": "800 lbs.",
    "**TIME**": "2 minutes",
    "**DISTANCE**": "500 feet",
    "**VOLUME**": "15 cft."
  },
  "5": {
    "**MASS**": "1,600 lbs.",
    "**TIME**": "4 minutes",
    "**DISTANCE**": "900 feet",
    "**VOLUME**": "30 cft."
  },
  "6": {
    "**MASS**": "3,200 lbs.",
    "**TIME**": "8 minutes",
    "**DISTANCE**": "1,800 feet",
    "**VOLUME**": "60 cft."
  },
  "7": {
    "**MASS**": "3 tons",
    "**TIME**": "15 minutes",
    "**DISTANCE**": "1/2 mile",
    "**VOLUME**": "125 cft."
  },
  "8": {
    "**MASS**": "6 tons",
    "**TIME**": "30 minutes",
    "**DISTANCE**": "1 mile",
    "**VOLUME**": "250 cft."
  },
  "9": {
    "**MASS**": "12 tons",
    "**TIME**": "1 hour",
    "**DISTANCE**": "2 miles",
    "**VOLUME**": "500 cft."
  },
  "10": {
    "**MASS**": "25 tons",
    "**TIME**": "2 hours",
    "**DISTANCE**": "4 miles",
    "**VOLUME**": "1,000 cft."
  },
  "11": {
    "**MASS**": "50 tons",
    "**TIME**": "4 hours",
    "**DISTANCE**": "8 miles",
    "**VOLUME**": "2,000 cft."
  },
  "12": {
    "**MASS**": "100 tons",
    "**TIME**": "8 hours",
    "**DISTANCE**": "16 miles",
    "**VOLUME**": "4,000 cft."
  },
  "13": {
    "**MASS**": "200 tons",
    "**TIME**": "16 hours",
    "**DISTANCE**": "30 miles",
    "**VOLUME**": "8,000 cft."
  },
  "14": {
    "**MASS**": "400 tons",
    "**TIME**": "1 day",
    "**DISTANCE**": "60 miles",
    "**VOLUME**": "15,000 cft."
  },
  "15": {
    "**MASS**": "800 tons",
    "**TIME**": "2 days",
    "**DISTANCE**": "120 miles",
    "**VOLUME**": "32,000 cft."
  },
  "16": {
    "**MASS**": "1,600 tons",
    "**TIME**": "4 days",
    "**DISTANCE**": "250 miles",
    "**VOLUME**": "65,000 cft."
  },
  "17": {
    "**MASS**": "3.2 ktons",
    "**TIME**": "1 week",
    "**DISTANCE**": "500 miles",
    "**VOLUME**": "125,000 cft."
  },
  "18": {
    "**MASS**": "6 ktons",
    "**TIME**": "2 weeks",
    "**DISTANCE**": "1,000 miles",
    "**VOLUME**": "250,000 cft."
  },
  "19": {
    "**MASS**": "12 ktons",
    "**TIME**": "1 month",
    "**DISTANCE**": "2,000 miles",
    "**VOLUME**": "500,000 cft."
  },
  "20": {
    "**MASS**": "25 ktons",
    "**TIME**": "2 months",
    "**DISTANCE**": "4,000 miles",
    "**VOLUME**": "1 million cft."
  },
  "21": {
    "**MASS**": "50 ktons",
    "**TIME**": "4 months",
    "**DISTANCE**": "8,000 miles",
    "**VOLUME**": "2 million cft."
  },
  "22": {
    "**MASS**": "100 ktons",
    "**TIME**": "8 months",
    "**DISTANCE**": "16,000 miles",
    "**VOLUME**": "4 million cft."
  },
  "23": {
    "**MASS**": "200 ktons",
    "**TIME**": "1.5 years",
    "**DISTANCE**": "32,000 miles",
    "**VOLUME**": "8 million cft."
  },
  "24": {
    "**MASS**": "400 ktons",
    "**TIME**": "3 years",
    "**DISTANCE**": "64,000 miles",
    "**VOLUME**": "15 million cft."
  },
  "25": {
    "**MASS**": "800 ktons",
    "**TIME**": "6 years",
    "**DISTANCE**": "125,000 miles",
    "**VOLUME**": "32 million cft."
  },
  "26": {
    "**MASS**": "1,600 ktons",
    "**TIME**": "12 years",
    "**DISTANCE**": "250,000 miles",
    "**VOLUME**": "65 million cft."
  },
  "27": {
    "**MASS**": "3,200 ktons",
    "**TIME**": "25 years",
    "**DISTANCE**": "500,000 miles",
    "**VOLUME**": "125 million cft."
  },
  "28": {
    "**MASS**": "6,400 ktons",
    "**TIME**": "50 years",
    "**DISTANCE**": "1 million miles",
    "**VOLUME**": "250 million cft."
  },
  "29": {
    "**MASS**": "12,500 ktons",
    "**TIME**": "100 years",
    "**DISTANCE**": "2 million miles",
    "**VOLUME**": "500 million cft."
  },
  "30": {
    "**MASS**": "25,000 ktons",
    "**TIME**": "200 years",
    "**DISTANCE**": "4 million miles",
    "**VOLUME**": "1 billion cft."
  }
}


header = [
    "playername",
    "discordid",
    'name',
    "pl",
    "pp",
    "threadlink",
    "alignment",
    "lastmofified",
    "affiliation",
    "occupation",
    "realname",
    "identity",
    "age",
    "species",
    'residence',
    "image",
    "thumbnail",
    "blurb"
    ]

alignments = {
    'Hero': {
        'image':'https://i.imgur.com/r7GnfYH.png',
        'color':0x00b0f4,
        'desc': 'A righteous hero joins the story!'
    }, 
    'Villain': {
        'image':'https://i.imgur.com/3mXw8wA.png',
        'color':0x9e0000,
        'desc': 'A nefarious villain joins the story!'

    },
    'Neutral': {
        'image':'https://i.imgur.com/TQbecmK.jpeg',
        'color':0xffdd00,
        'desc': 'A mysterious figure joins the story!'
    }
}
    

async def is_moderator(ctx, send_message=True):
    try:
        for role in ctx.author.roles:
            if role.id == MODERATOR_ROLE:
                return True
    except AttributeError:
        pass
    if send_message:
        await ctx.send("I'm terribly sorry, but you do not have the authority for that command.")
    return False

async def get_character(Name):
    global ROSTER
    if ROSTER == {}:
        return None
    async with lock:
        Name = Name.replace('"', '')
        if (Name.startswith("'") and Name.endswith("'")) or (Name.startswith('"') and Name.endswith('"')):
            Name = Name[1:-1]
        Name = Name.lower()
        for char in ROSTER:
            if ROSTER[char]['name'].lower() == Name:
                return ROSTER[char]
        return None


async def find_chars_from_user(user_id):
    global ROSTER
    res = defaultdict(list)
    if ROSTER == {}:
        return res
    for char in ROSTER:
        res[ROSTER[char]['discordid']].append(ROSTER[char])
    return res[str(user_id)]


async def add_character(character):
    global ROSTER
    ROSTER[character['name']] = character
    await save_roster()


async def update_character(ctx,new_char, field, value, name=False):
    global ROSTER
    if new_char[field.lower()] is None:
        errormsg = f"{field} is not a valid field"
        await ctx.send(errormsg)
        raise Exception(errormsg)
    if name:
        ROSTER[value] = ROSTER[new_char['name']]
        del ROSTER[new_char['name']]
        ROSTER[value]['name'] = value
        print(ROSTER[value])
        print(ROSTER[new_char['name']])
    else:
        ROSTER[new_char['name']][field.lower()] = value
    await save_roster()
    

async def delete_character(name):
    global ROSTER
    del ROSTER[name]
    await save_roster()


# Create bot
intents = discord.Intents.all()
activity=discord.Game(name=f"{PREFIX}help")
client = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None, activity=activity)



# Startup Information
@client.event
async def on_ready():
    await client.wait_until_ready()
    await load_roster()
    print('Connected to bot: {}'.format(client.user.name))
    print('Bot ID: {}'.format(client.user.id))

# Command
@client.command()
async def help(ctx):
    embed = discord.Embed(title="Alfred - Help",
                      description=f"Salutations, {ctx.author.mention} allow me to explain my functionality:",
                      colour=0x1eff00,
                      timestamp=datetime.now())
    embed.add_field(name=f"{PREFIX}help",
                    value="Display this message",
                    inline=False)
    embed.add_field(name=f"{PREFIX}roster",
                    value=f"Display characters.  Type `{PREFIX}roster` for a full list of subcommands",
                    inline=False)
    embed.add_field(name=f"{PREFIX}badge",
                    value=f"Manage a character's display badge.  Type `{PREFIX}badge` for a full list of subcommands",
                    inline=False)
    embed.add_field(name=f"{PREFIX}rank `number`",
                    value="Lookup `number` on the M&M 3e ranks and measures table.  Any value less than -5 or greater than 30 will give you the value at those ranks and a number to multiple or divide them by to get their value.",
                    inline=False)
    embed.add_field(name=f"{PREFIX}dist `time` `speed`",
                    value="Finds out how far you can get in  time rank `time` at speed rank `speed`.",
                    inline=False)
    embed.add_field(name=f"{PREFIX}throw `strength` `mass`",
                    value="Finds out how far Strength rank `strength` can throw an object with mass rank `mass`",
                    inline=False)
    embed.add_field(name=f"{PREFIX}time `speed` `distance`",
                    value="Finds out how long it takes for someone traveling at speed rank `speed` to travel distance rank `distance`",
                    inline=False)
    if await is_moderator(ctx, False):
        mod_embed = copy.deepcopy(embed)
        mod_embed.add_field(name=f"{PREFIX}character",
                        value=f"**Mod Only**.  Manage characters.  Type `{PREFIX}character` for a full list of subcommands",
                        inline=False)
        await ctx.author.send(embed=mod_embed)
    await ctx.send(embed=embed)


@client.event
async def on_command_error(ctx, error):
    print(error)
    await ctx.send("I'm terribly sorry, but I don't know that command.  Here is a list of commands that I know:")
    await help(ctx)


@client.group(name="character", invoke_without_command=True)
async def character(ctx):
    if not await is_moderator(ctx):
        return
    await ctx.send(f"{ctx.author.mention}, I have sent the documentation via direct message.")
    embed = discord.Embed(title="Alfred - Help (Character Manager)",
                      description=f"Salutations, {ctx.author.mention} allow me to explain my functionality:",
                      colour=0x1eff00,
                      timestamp=datetime.now())

    embed.add_field(name=f"{PREFIX}character",
                    value="Display this message",
                    inline=False)
    embed.add_field(name=f"{PREFIX}character create",
                    value="Creates a character from their submission in  https://discord.com/channels/1062472091401728071/1062569370427064351\nCharacter names are unique, so two characters cannot have the same name.",
                    inline=False)
    embed.add_field(name=f"{PREFIX}character addpp `NAME` `PP`",
                    value="Adds `PP` PP to `character`.  Prefer this over `{PREFIX}badge update CHARACTER PP NUMBER`, as this will add the given PP to the character, whereas the latter simply sets the total PP of a character to the specified value.",
                    inline=False)
    embed.add_field(name=f"{PREFIX}character delete `CHARACTER`",
                    value="Deletes `CHARACTER`.  This is a destructive action, and cannot be reversed.  This does not delete their submission in https://discord.com/channels/1062472091401728071/1062569370427064351, so the character can be recreated if that still remains.",
                    inline=False)

    await ctx.author.send(embed=embed)


@client.group(name="roster", invoke_without_command=True)
async def roster(ctx):
    embed = discord.Embed(title="Alfred - Help (Character Roster)",
                      description=f"Salutations, {ctx.author.mention} allow me to explain my functionality:",
                      colour=0x1eff00,
                      timestamp=datetime.now())
    embed.add_field(name=f"{PREFIX}roster me",
                    value="Display all of your characters.",
                    inline=False)
    embed.add_field(name=f"{PREFIX}roster `filter` `sort`",
                    value="Display a roster based on a given filter and optional sort mode.\n\n**Valid Filters (cense-sensitive)**\n**all**\n**hero**\n**neutral**\n**villain**\n\n**Sort modes**\n**pp** - Sort by pp descending\n**alpha** sort by name ascending",
                    inline=False)

    await ctx.send(embed=embed)


@roster.command()
async def me(ctx):
    embed=discord.Embed(title=f"{ctx.author.name}'s Characters", color=0x00ff1e)
    for char in await find_chars_from_user(ctx.author.id):
        embed.add_field(name=char['name'], value=char['threadlink'], inline=True)
        embed.add_field(name="PP", value=char['pp'], inline=True)
        embed.add_field(name = "Alignment", value = char['alignment'])
    await ctx.send(embed=embed)



async def get_roster_data(sort=None, filter=None):
    data = []
    for char in ROSTER:
        if filter in ["Hero", "Villain", "Neutral"]:
            if ROSTER[char]['alignment'] != filter:
                continue
        temp = {}
        temp['name'] = ROSTER[char]['name']
        temp["Profile"] = ROSTER[char]['threadlink']
        temp["Alignment"] = ROSTER[char]['alignment']
        temp["PP"] = str(ROSTER[char]['pp'])
        data.append(temp)
    if sort == "alpha":
        data = sorted(data, key=operator.itemgetter('name'))
    if sort == "pp":
        data = sorted(data, key=operator.itemgetter('PP'), reverse=True)
    return data


@roster.command()
async def hero(ctx, sort=None):
    data = await get_roster_data(sort, "Hero")
    pagination_view = PaginationView(timeout=None)
    pagination_view.data = data
    pagination_view.title = 'All Heroes'
    await pagination_view.send(ctx)


@roster.command()
async def villain(ctx, sort=None):
    data = await get_roster_data(sort, "Villain")
    pagination_view = PaginationView(timeout=None)
    pagination_view.data = data
    pagination_view.title = 'All Villains'
    await pagination_view.send(ctx)


@roster.command()
async def neutral(ctx, sort=None):
    data = await get_roster_data(sort, "Neutral")
    pagination_view = PaginationView(timeout=None)
    pagination_view.data = data
    pagination_view.title = 'All Neutrals'
    await pagination_view.send(ctx)


@roster.command()
async def all(ctx, sort=None):
    data = await get_roster_data(sort)
    pagination_view = PaginationView(timeout=None)
    pagination_view.data = data
    pagination_view.title = 'All Characters'
    await pagination_view.send(ctx)




@client.group(name="badge", invoke_without_command=True) 
async def badge(ctx, name=None, character=None):
    global ROSTER
    if name is None and character is None:
        embed = discord.Embed(title="Alfred - Help (Badge Manager)",
                      description=f"Salutations, {ctx.author.mention} allow me to explain my functionality:",
                      colour=0x1eff00,
                      timestamp=datetime.now())

        embed.add_field(name=f"{PREFIX}badge",
                        value="Display this message",
                        inline=False)
        embed.add_field(name=f"{PREFIX}badge `Character`",
                        value="Displays the badge for `Character`",
                        inline=False)
        embed.add_field(name=f"{PREFIX}badge update `Character` `field` `value`",
                        value="Updates the `field` on `Character`'s entry to be `value`\n\nValid fields are as follows:\n**name** - the character's name.  Names are unique and this will fail if another character already exists with the specified name.\n**Affiliation** - The character's affiliation.\n**occupation** - the character's listed occupation\n**realname** The character's real name\n**identity** The status of the character's identity, generally either `Secret` or `Public`\n**age** - the character's age\n**residence** - where the character resides\n**image** - The large image at the bottom of the character's badge.  Generally, this should be a picture of the character.\n**thumbnail** - The thumbnail at the top right of the character's badge.  Perhaps an emblem?\n**blurb** - The text that displays underneath the character's name",
                        inline=False)
        if is_moderator(ctx, False):
            mod_embed = copy.deepcopy(embed)
            mod_embed.add_field(name="Mod Commands",
                value=f"`{PREFIX}badge update` has a few mod-only commands as well.  \nThe following fields can be updated if invoked by someone with the moderator role.\n\n**pp** - Sets the character's PP.\nGenerally you should be using `{PREFIX}character addpp CHARACTER PP`, but this is available in case you do the final calculations manually.\n**pl** - Sets the character's Power Level.\n**alignment** - Sets the character's alignment.  This should only ever be `Hero`, `Neutral`, or `Villain`",
                inline=False)
            await ctx.author.send(embed=mod_embed)
        await ctx.send(embed=embed)
        return
    if character is None:
        character = await get_character(name)
        if character is None:
            await ctx.send('Unable to find character.')
    embed = discord.Embed(title=f"{character['name']} ({character['realname']})",
                          url=character['threadlink'],
                          description=character['blurb'],
                          colour=alignments[character['alignment']]['color'],
                          timestamp=datetime.now())
    embed.add_field(name="Age",
                value=character['age'],
                inline=True)
    embed.add_field(name="Species",
                value=character['species'],
                inline=True)
    embed.add_field(name="Identity Status",
                value=character['identity'],
                inline=True)
    embed.add_field(name="Alignment",
                    value=character['alignment'],
                    inline=True)
    embed.add_field(name="Power Level",
                    value=character['pl'],
                    inline=True)
    embed.add_field(name="PP",
                    value=character['pp'],
                    inline=True)
    embed.add_field(name="Affiliation",
                value=character['affiliation'],
                inline=True)
    embed.add_field(name="Residence",
                value=character['residence'],
                inline=True)
    embed.add_field(name="Occupation",
                value=character['occupation'],
                inline=True)
    embed.set_image(url=character['image'])
    embed.set_thumbnail(url=character['thumbnail'])
    await ctx.send(embed=embed)



@badge.group(name="update", invoke_without_command=True)
async def update(ctx, character=None, field=None, value=None):
    if any(elem is None for elem in [character, field, value]):
        await badge(ctx)
        return
    upd_char = await get_character(character)
    if str(ctx.author.id) != str(upd_char['discordid']) and await is_moderator(ctx, False) == False:
        await ctx.send("You do not have permission to edit this character.")
        return
    if upd_char == None:
        await ctx.send(f'Unable to find character {character}')
        return
    if field.lower() not in upd_char.keys():
        await ctx.send(f"{field} is not a valid field")
        return
    # Disallow
    if (field.lower() == 'playername' or field.lower() == 'discordid' or
       field.lower() == 'threadlink' or
       field.lower() == 'lastmodified'):
        await ctx.send("I'm terribly sorry, but that is not something that I can change.")
        return
    # Mods Only
    if field.lower() == 'pp' or field.lower() == 'pl' or field.lower() == 'alignment':
        if await is_moderator(ctx) == False:
            return
        if field.lower() == 'alignment' and value.lower() not in ["hero", "villain", "neutral"]:
            await ctx.send(f"Invalid alignment: {value}")
            return
    if field.lower() == 'imaage' or field.lower() == 'thumbnail':
        value = value.replace('"', '')
        value = value.replace("'", "")
        if not validators.url(value):
            await ctx.send(f'Invalid URL specified: `{value}`')
            return
    isname=False
    if field.lower() == 'name':
        if await get_character(value) != None:
            await ctx.send(f"A character named {value} already exists.")
            return
        character = value
        isname=True
    try:
        await update_character(ctx,upd_char, field, value, name=isname)
        await badge(ctx, character)
    except Exception as e:
        print(e)
        return


@character.command()
async def create(ctx):
    if await is_moderator(ctx) == False:
        return
    global ROSTER

    # Check character limits
    ccount = await find_chars_from_user(ctx.channel.owner.id)
    if len(ccount) == CHARACTER_LIMIT:
        await ctx.send(f"Error: You currently have {len(ccount)} characters which the server limit of **{CHARACTER_LIMIT}**")
        return
    elif len(ccount) > CHARACTER_LIMIT:
        await ctx.send(f"Error: You currently have {len(ccount)} characters which is more than the server limit of **{CHARACTER_LIMIT}**")
        return

    # Ensure this is being run as a thread in the proper channel
    try:
        if ctx.channel.parent_id != CHARACTER_CHANNEL_ID:
            await ctx.send('Error: This is not a character thread.')
            return
    except AttributeError:
        await ctx.send('Error: This is not a character thread.')

    # Get info from thread
    name = ctx.channel.name

    # Search the name for conflicts
    char = await get_character(name)
    if char is not None:
        await ctx.send(f"Error: A character named {name} already exists: {char['thread link']}")
        return
    
    alignment = ctx.channel.applied_tags[-1].name

    # Get first message
    first_msg = None
    async for msg in ctx.channel.history(limit=1, oldest_first=True):
        first_msg = msg
        break

    image = None
    try:
        image = first_msg.attachments[0].url
    except IndexError:
        image = alignments[alignment]['image']

    first_msg = strip_markdown(first_msg.clean_content)
    aff = res = spec = age = id_status = r_name = occ = None

    # Parse the first discord message
    for line in first_msg.split('\n'):
        if line.startswith('Affiliations'):
            aff = line.split(":")[1].strip().strip()
        if line.startswith('Place of Residence'):
            line.split(":")
            res = line.split(":")[1].strip()
            continue
        if line.startswith('Species'):
            line.split(":")
            spec = line.split(":")[1].strip()
            continue
        if line.startswith('Age'):
            line.split(":")
            age = line.split(":")[1].strip()
            continue
        if line.startswith('Identity'):
            line.split(":")
            id_status = line.split(":")[1].strip()
            continue
        if line.startswith('Real Name'):
            line.split(":")
            r_name = line.split(":")[1].strip()
            continue
        if line.startswith('Occupation'):
            line.split(":")
            occ = line.split(":")[1].strip()
            continue
    link = ctx.channel.jump_url

    new_char = [
        str(ctx.channel.owner),
        str(ctx.channel.owner.id),
        name,
        PL_DEFAULT,
        PP_DEFAULT,
        link,
        alignment,
        datetime.now().strftime("%m/%d/%y"),
        aff,
        occ,
        r_name,
        id_status,
        age,
        spec,
        res,
        image,
        thumbnail,
        alignments[alignment]['desc']
    ]
    new_char=dict(zip(header,new_char))
    await add_character(new_char)
    await badge(ctx, character=ROSTER[new_char['name']])


@character.command()
async def delete(ctx, character=None):
    if await is_moderator(ctx) == False:
        return
    if character == None:
        await ctx.send(f"Usage: `{PREFIX}character delete CHARACTER_NAME`")
        return
    global ROSTER
    del_char = await get_character(character)
    if del_char is None:
        await ctx.send(f"I'm terribly sorry, but I could not find {character}")
    await ctx.send(f'Are you sure you want to delete {del_char["name"]}?')
    await ctx.send(f'To confirm, please type `{del_char["name"]}`')
    def check(m):
        return m.channel == ctx.channel
    try:
        msg = await client.wait_for('message', timeout=15, check=check)
        if (msg.content != del_char["name"]):
            await ctx.send("Incorrect name.")
            return
        await delete_character(character)
        await ctx.send(f"Deleted {del_char['name']}")
    except asyncio.TimeoutError:
        await ctx.send("Request timed out")
    


@character.command()
async def addpp(ctx, char=None, pp=None):
    if await is_moderator(ctx) == False:
        return
    global ROSTER
    if pp is None:
        await ctx.send(f"Usage: `{PREFIX}character addpp NAME PP`")
        return
    try:
        pp = int(pp)
    except ValueError:
        await ctx.send("PP must be an integer.")
        return
    entry = await get_character(char)
    if entry is None:
        await ctx.send(f"Unable to find {char}")
        return
    try:
        await update_character(ctx,entry, 'pp', int(entry['pp']) + pp)
        await ctx.send(f"I have updated character: {entry['name']}")
    except Exception as e:
        print(e)
        return


async def rank_compare(ctx, rank, key=None, embed=None):
    try:
        int(rank)
    except ValueError:
        await ctx.send(f"I'm terribly sorry, but {rank} must be an integer.")
        return
    if int(rank) < -5:
        await ctx.send("Apologies, but I cannot handle ranks below -5.")
        await ctx.send(f"You may divide the following values by {2*(int(rank) + -5)} to get the appropriate value:")
        rank = -5
    if int(rank) > 30:
        await ctx.send("Apologies, but I cannot handle ranks above 30.")
        await ctx.send(f"You may multiply the following values by {2*(int(rank) - 30)} to get the appropriate value:")
        rank = 30
    if embed == None:
        embed = discord.Embed(title=f"{key} Rank {rank}",
                              url='https://www.d20herosrd.com/home/ranks-and-measures/')
    embed.add_field(name=key,
            value=RANK_TABLE[str(rank)][f"**{key.upper()}**"],
            inline=False)
    return embed



@client.command()
async def rank(ctx, rank=None):
    if rank == None:
        await ctx.send("Usage: `~rank NUMBER`")
        return
    try:
        int(rank)
    except ValueError:
        await ctx.send(f"I'm terribly sorry, but {rank} must be an integer.")
        return
    if int(rank) < -5:
        await ctx.send("Apologies, but I cannot handle ranks below -5.")
        await ctx.send(f"You may divide the following values by {2*(int(rank) + -5)} to get the appropriate value:")
        rank = -5
    if int(rank) > 30:
        await ctx.send("Apologies, but I cannot handle ranks above 30.")
        await ctx.send(f"You Smay multiply the following values by {2*(int(rank) - 30)} to get the appropriate value:")
        rank = 30
    embed = discord.Embed(title=f"Rank {rank}",
                          url='https://www.d20herosrd.com/home/ranks-and-measures/')
    for x in ["Mass", "Time", "Distance", "Volume"]:
        embed = await rank_compare(ctx, str(rank), x, embed)
    await ctx.send(embed=embed)


@client.command()
async def time(ctx, dist=None, spd=None):
    if spd == None:
        await ctx.send(f"Usage: `{PREFIX}time DISTANCE SPEED`")
        return
    try:
        int(dist)
        int(spd)
    except ValueError:
        await ctx.send(f"I'm terribly sorry, but {dist} & {spd} must be integers.")
        return
    await ctx.send(embed=await rank_compare(ctx,str(int(dist) -int(spd)), "Time"))
    

@client.command()
async def throw(ctx, stren=None, mass=None):
    if mass == None:
        await ctx.send(f"Usage: `{PREFIX}throw STRENGTH MASS`")
        return
    try:
        int(stren)
        int(mass)
    except ValueError:
        await ctx.send(f"I'm terribly sorry, but {stren} & {mass} must be integers.")
        return
    await ctx.send(embed=await rank_compare(ctx,str(int(stren) -int(mass)), "Distance"))
    

@client.command()
async def dist(ctx, time=None, spd=None):
    if spd == None:
        await ctx.send(f"Usage: `{PREFIX}dist TIME SPEED`")
        return
    try:
        int(time)
        int(spd)
    except ValueError:
        await ctx.send(f"I'm terribly sorry, but {time} & {spd} must be integers.")
        return
    await ctx.send(embed=await rank_compare(ctx,str(int(time) +int(spd)), "Distance"))
    

# Run the bot
client.run(TOKEN)

