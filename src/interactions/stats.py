from plugins.statevograph import statevograph
import discord

def execute(build):
    buf = statevograph(build)
    file = discord.File(buf, filename="evo_plot.png")
    embed = discord.Embed(
        title = "Stat Evolution",
        color=discord.Color.blurple()
    )
    embed.set_image(url="attachment://evo_plot.png")
    return embed, file