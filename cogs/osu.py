import time
from ext import glob
from ext.glob import bot
from objects import Score
from discord import Embed
from objects import Player
from objects import Server
from objects import OsuCard
from objects import Beatmap
from helpers import TWELVEHOURS
from discord.ext import commands
from discord.message import Message
from discord.ext.commands import Context

arrows = ('⬅️', '➡️')

@bot.command()
async def connect(ctx: Context) -> None:
    server = Server.Bancho
    msg: list[str] = ctx.message.content.split()[1:]
    
    if '-akatsuki' in msg:
        msg.remove('-akatsuki')
        server = Server.Akatsuki
    
    user = glob.db.find_one({'_id': ctx.author.id})

    name = ' '.join(msg)
    if not name:
        await ctx.send("Please provide a name.")
        return
    
    if server == Server.Akatsuki:
        p = await Player.from_akatsuki(
            user = name,
        )
    else:
        p = await Player.from_bancho(
            user = name
        )
    
    if not p:
        await ctx.send("User could not be found!")
    
    server_name = server.name.lower()
    if user is None:
        post = {
            "_id": ctx.author.id,
            server_name: p.id
        }
        glob.db.insert_one(post)
    else:
        new_values = {
            "$set": {
                server_name: p.id
            }
        }
        glob.db.update_one(user, new_values)

    e = Embed(
        colour = ctx.author.color
    )

    e.set_author(
        name = f'{p.name} was connected to your discord account!',
        url = bot.user.avatar_url
    )

    e.set_image(
        url = p.avatar
    )

    await ctx.send(embed=e)
    return

@bot.command(aliases=['c'])
async def compare(ctx: Context) -> None:
    if ctx.message.channel.id not in glob.cache.channel_beatmaps:
        await ctx.send("No map was found.")
        return

    bmap: Beatmap = glob.cache.channel_beatmaps[ctx.message.channel.id][0]

    bid = bmap.id
    if bid not in glob.cache.beatmaps:
        glob.cache.beatmaps[bid] = bmap
    
    relax = mode = index = 0
    server = Server.Bancho
    msg: list[str] = ctx.message.content.lower().split()[1:]
    
    if '-p' in msg:
        index = msg[msg.index('-p') + 1]
        msg.remove('-p')
        msg.remove(index)
        if not index.isdecimal():
            await ctx.send(
                'Please provide a number for `-p`'
            )
            return

        index = int(index)
        index = index - 1 if index > 0 else index

    if '-std' in msg:
        msg.remove('-std')
        mode = 0
    elif '-taiko' in msg:
        msg.remove('-taiko')
        mode = 1
    elif '-ctb' in msg:
        msg.remove('-ctb')
        mode = 2
    elif '-mania' in msg:
        msg.remove('-mania')
        mode = 3

    if '-rx' in msg:
        msg.remove('-rx')
        server = Server.Akatsuki
        relax = 1
    
    if '-akatsuki' in msg:
        msg.remove('-akatsuki')
        server = Server.Akatsuki

    name = ' '.join(msg)

    server_name = server.name.lower()

    if ctx.message.mentions:
        mentioned = ctx.message.mentions[0]
        user = glob.db.find_one({"_id": mentioned.id})
        if not user or server_name not in user:
            await ctx.send(
                "User couldn't be found in our database! "
                f"{mentioned.name}, Try connecting a user "
                "to our database by doing `;connect (your username)`"
            )
            return
        
        name = user[server_name]

    elif not name:
        user = glob.db.find_one({"_id": ctx.author.id})
        if not user or server_name not in user:
            await ctx.send(
                "User couldn't be found in our database! "
                "Try connecting a user to our database"
                "by doing `;connect (your username)`"
            )
            return
        
        name = user[server_name]
    
    else:
        pass

    if server == Server.Akatsuki:
        s = await Score.from_akatsuki(
            user = name,
            mode = mode,
            index = index,
            relax = relax,
            bmap = bmap
        )
    else:
        s = await Score.from_bancho(
            user = name,
            mode = mode,
            index = index,
            bmap = bmap
        )
    
    if not s:
        await ctx.send("Score or Player couldn't be found!")
        return

    glob.cache.scores[s.player.id] = (s, 'c')

    e = s.embed
    e.colour = ctx.author.color
    msg: Message = await ctx.send(embed=e)

    for emoji in arrows:
        await msg.add_reaction(emoji)
    return

@bot.command(aliases=['t'])
async def top(ctx: Context) -> None:
    relax = mode = index = 0
    server = Server.Bancho
    msg: list[str] = ctx.message.content.lower().split()[1:]
    
    if '-p' in msg:
        index = msg[msg.index('-p') + 1]
        msg.remove('-p')
        msg.remove(index)
        if not index.isdecimal():
            await ctx.send(
                'Please provide a number for `-p`'
            )
            return

        index = int(index)
        index = index - 1 if index > 0 else index

    if '-std' in msg:
        msg.remove('-std')
        mode = 0
    elif '-taiko' in msg:
        msg.remove('-taiko')
        mode = 1
    elif '-ctb' in msg:
        msg.remove('-ctb')
        mode = 2
    elif '-mania' in msg:
        msg.remove('-mania')
        mode = 3

    if '-rx' in msg:
        msg.remove('-rx')
        server = Server.Akatsuki
        relax = 1
    
    if '-akatsuki' in msg:
        msg.remove('-akatsuki')
        server = Server.Akatsuki

    name = ' '.join(msg)

    server_name = server.name.lower()

    if ctx.message.mentions:
        mentioned = ctx.message.mentions[0]
        user = glob.db.find_one({"_id": mentioned.id})
        if not user or server_name not in user:
            await ctx.send(
                "User couldn't be found in our database! "
                f"{mentioned.name}, Try connecting a user "
                "to our database by doing `;connect (your username)`"
            )
            return
        
        name = user[server_name]

    elif not name:
        user = glob.db.find_one({"_id": ctx.author.id})
        if not user or server_name not in user:
            await ctx.send(
                "User couldn't be found in our database! "
                "Try connecting a user to our database"
                "by doing `;connect (your username)`"
            )
            return
        
        name = user[server_name]
    
    else:
        pass
    
    if server == Server.Akatsuki:
        s = await Score.from_akatsuki_top(
            user = name,
            mode = mode,
            index = index,
            relax = relax
        )
    else:
        s = await Score.from_bancho_top(
            user = name,
            mode = mode,
            index = index
        ) 
    
    if not s:
        await ctx.send("Score or Player couldn't be found!")
        return
    
    msg_id = ctx.message.channel.id
    glob.cache.channel_beatmaps[msg_id] = (
        s.bmap, time.time() + TWELVEHOURS
    )

    bid = s.bmap.id
    if bid not in glob.cache.beatmaps:
        glob.cache.beatmaps[bid] = s.bmap

    glob.cache.scores[s.player.id] = (s, 't')

    e = s.embed
    e.colour = ctx.author.color
    msg: Message = await ctx.send(embed=e)

    for emoji in arrows:
        await msg.add_reaction(emoji)
    
    return

@bot.command(aliases=['r', 'rs', 'rc'])
async def recent(ctx: Context) -> None:
    relax = mode = index = 0
    server = Server.Bancho
    msg: list[str] = ctx.message.content.lower().split()[1:]
    
    if '-p' in msg:
        index = msg[msg.index('-p') + 1]
        msg.remove('-p')
        msg.remove(index)
        if not index.isdecimal():
            await ctx.send(
                'Please provide a number for `-p`'
            )
            return

        index = int(index)
        index = index - 1 if index > 0 else index

    if '-std' in msg:
        msg.remove('-std')
        mode = 0
    elif '-taiko' in msg:
        msg.remove('-taiko')
        mode = 1
    elif '-ctb' in msg:
        msg.remove('-ctb')
        mode = 2
    elif '-mania' in msg:
        msg.remove('-mania')
        mode = 3

    if '-rx' in msg:
        msg.remove('-rx')
        server = Server.Akatsuki
        relax = 1
    
    if '-akatsuki' in msg:
        msg.remove('-akatsuki')
        server = Server.Akatsuki

    name = ' '.join(msg)

    server_name = server.name.lower()

    if ctx.message.mentions:
        mentioned = ctx.message.mentions[0]
        user = glob.db.find_one({"_id": mentioned.id})
        if not user or server_name not in user:
            await ctx.send(
                "User couldn't be found in our database! "
                f"{mentioned.name}, Try connecting a user "
                "to our database by doing `;connect (your username)`"
            )
            return
        
        name = user[server_name]

    elif not name:
        user = glob.db.find_one({"_id": ctx.author.id})
        if not user or server_name not in user:
            await ctx.send(
                "User couldn't be found in our database! "
                "Try connecting a user to our database"
                "by doing `;connect (your username)`"
            )
            return
        
        name = user[server_name]
    
    else:
        pass
    
    if server == Server.Akatsuki:
        s = await Score.from_akatsuki_recent(
            user = name,
            mode = mode,
            index = index,
            relax = relax
        )
    else:
        s = await Score.from_bancho_recent(
            user = name,
            mode = mode,
            index = index
        ) 
    
    if not s:
        await ctx.send("Score or Player couldn't be found from the last 24 hours.")
        return
    
    msg_id = ctx.message.channel.id
    glob.cache.channel_beatmaps[msg_id] = (
        s.bmap, time.time() + TWELVEHOURS
    )

    bid = s.bmap.id
    if bid not in glob.cache.beatmaps:
        glob.cache.beatmaps[bid] = s.bmap
    
    glob.cache.scores[s.player.id] = (s, 'r')

    e = s.embed
    e.colour = ctx.author.color
    msg: Message = await ctx.send(embed=e)

    for emoji in arrows:
        await msg.add_reaction(emoji)
    
    return

@bot.command(aliases=['p', 'osu'])
async def profile(ctx: Context) -> None:
    relax = mode = 0
    server = Server.Bancho
    msg: list[str] = ctx.message.content.lower().split()[1:]
    
    if '-std' in msg:
        msg.remove('-std')
        mode = 0
    elif '-taiko' in msg:
        msg.remove('-taiko')
        mode = 1
    elif '-ctb' in msg:
        msg.remove('-ctb')
        mode = 2
    elif '-mania' in msg:
        msg.remove('-mania')
        mode = 3

    if '-rx' in msg:
        msg.remove('-rx')
        server = Server.Akatsuki
        relax = 1
    
    if '-akatsuki' in msg:
        msg.remove('-akatsuki')
        server = Server.Akatsuki

    name = ' '.join(msg)
    server_name = server.name.lower()

    if ctx.message.mentions:
        mentioned = ctx.message.mentions[0]
        user = glob.db.find_one({"_id": mentioned.id})
        if not user or server_name not in user:
            await ctx.send(
                "User couldn't be found in our database! "
                f"{mentioned.name}, Try connecting a user "
                "to our database by doing `;connect (your username)`"
            )
            return
        
        name = user[server_name]

    elif not name:
        user = glob.db.find_one({"_id": ctx.author.id})
        if not user or server_name not in user:
            await ctx.send(
                "User couldn't be found in our database! "
                "Try connecting a user to our database"
                "by doing `;connect (your username)`"
            )
            return
        
        name = user[server_name]
    
    else:
        pass
    
    if server == Server.Akatsuki:
        p = await Player.from_akatsuki(
            user = name,
            mode = mode,
            relax = relax
        )
    else:
        p = await Player.from_bancho(
            user = name,
            mode = mode,
        ) 
    
    if not p:
        await ctx.send("User couldn't be found!")
        return
    
    e = p.embed
    e.colour = ctx.author.color
    await ctx.send(embed=e)
    return

@bot.command(aliases=['oc', 'card'])
@commands.cooldown(1, 10, commands.BucketType.user)
async def osucard(ctx: Context) -> None:
    relax = mode = 0
    server = Server.Bancho
    msg: list[str] = ctx.message.content.lower().split()[1:]
    
    if '-std' in msg:
        msg.remove('-std')
        mode = 0
    elif '-taiko' in msg:
        msg.remove('-taiko')
        mode = 1
    elif '-ctb' in msg:
        msg.remove('-ctb')
        mode = 2
    elif '-mania' in msg:
        msg.remove('-mania')
        mode = 3

    if '-rx' in msg:
        msg.remove('-rx')
        server = Server.Akatsuki
        relax = 1
    
    if '-akatsuki' in msg:
        msg.remove('-akatsuki')
        server = Server.Akatsuki

    name = ' '.join(msg)
    server_name = server.name.lower()

    if ctx.message.mentions:
        mentioned = ctx.message.mentions[0]
        user = glob.db.find_one({"_id": mentioned.id})
        if not user or server_name not in user:
            await ctx.send(
                "User couldn't be found in our database! "
                f"{mentioned.name}, Try connecting a user "
                "to our database by doing `;connect (your username)`"
            )
            return
        
        name = user[server_name]

    elif not name:
        user = glob.db.find_one({"_id": ctx.author.id})
        if not user or server_name not in user:
            await ctx.send(
                "User couldn't be found in our database! "
                "Try connecting a user to our database"
                "by doing `;connect (your username)`"
            )
            return
        
        name = user[server_name]
    
    else:
        pass

    m: Message = await ctx.send(
        'Running Calculations! This may take up to a minute.'
    )

    st = time.time()
    if server == Server.Akatsuki:
        ...
    else:
        card = await OsuCard.from_bancho(
            user = name,
            mode = mode
        )
    
    if not card:
        await ctx.send(
            "User wasn't found or an error occured during calculations."
        )
        return

    e = card.embed
    e.colour = ctx.author.color
    await m.edit(
        content = f'Done! {time.time()-st:.2f}s', 
        embed = e
    )
    return