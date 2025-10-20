import discord

def execute(message):
    embed = discord.Embed(
        title="Help Menu",
        description="Explore all commands for equipment lookup and analytics!",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="Lookup Commands",
        value=(
            "`.equipment <name>` — Lookup Equipment details\n"
            "`.talent <name>` — Lookup Talent details\n"
            "`.weapon <name>` — Lookup Weapon details\n"
            "`.outfit <name>` — Lookup Outfit details\n"
            "`.mantra <name>` — Lookup Mantra details\n"
        ),
        inline=False
    )

    embed.add_field(
        name="Analytics Commands",
        value=(
            "`ehp` — Calculates Effective Health Points of a full Phys and HP kit (Reply to Build Link)\n"
            "`stats` — Displays the Stat Evolution diagram for optimisation (Reply to Build Link)\n"
        ),
        inline=False
    )

    embed.set_footer(text="Use .<command> [name] or reply to a Deepwoken build link for analytics!")
    return embed