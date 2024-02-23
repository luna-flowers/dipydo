import discord
import os
import time
import asyncio
import datetime as dt


from discord.commands import Option
from discord.ext import tasks, commands
from dotenv import load_dotenv

# import logging
# logging.basicConfig(level=logging.DEBUG)

bot = commands.Bot()


class Pomodoro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    focus_description = "Duration (in minutes) of focus phase"
    break_description = "Duration (in minutes) of break phase"
    focus_ph_description = "Number of focus phases"

    active_sessions = {}  # Key: user, Value: (start_time,focus_phases)

    @commands.slash_command()
    async def pomo(
        self,
        ctx: discord.ApplicationContext,
        focus_length: Option(int, focus_description, default=25),
        break_length: Option(int, break_description, default=5),
        focus_phases: Option(int, focus_ph_description, default=2),
    ):
        author = ctx.author.mention

        focus_min = focus_length * 60
        break_min = break_length * 60

        if author in self.active_sessions:
            await ctx.respond(f"{author} already has an active session", ephemeral=True)

        # Logical start of pomodoro session
        self.active_sessions[author] = (time.time(), focus_phases)
        max_focus = focus_phases

        @tasks.loop(seconds=focus_min + break_min, count=focus_phases)
        async def focus(self):
            nonlocal focus_phases
            nonlocal max_focus

            if author not in self.active_sessions:
                raise Exception(f"{author}'s session has been canceled")

            focus_end = dt.datetime.now() + dt.timedelta(minutes=focus_length)
            focus_end_time = focus_end.strftime("%I:%M %p")

            if focus_phases == max_focus:
                await ctx.respond(f"{author} Begin focus! End at {focus_end_time}")
            else:
                await ctx.send(f"{author} Begin focus! End at {focus_end_time}")

            focus_phases -= 1
            await asyncio.sleep(focus_min)

            if author not in self.active_sessions:
                raise Exception(f"{author}'s session has been canceled")

            if focus_phases >= 1:
                break_end = dt.datetime.now() + dt.timedelta(minutes=break_length)
                break_end_time = break_end.strftime("%I:%M %p")

                await ctx.send(f"{author} Break time! End at {break_end_time}")

                await asyncio.sleep(break_min)
            elif focus_phases == 0:
                await ctx.send(f"{author} Session complete. You're free now!")
                del self.active_sessions[author]

        focus.start(self)

    @commands.slash_command()
    async def end(self, ctx: discord.ApplicationContext):
        author = ctx.author.mention

        if author in self.active_sessions:
            del self.active_sessions[author]
            await ctx.respond("Your active session has been ended")
        else:
            await ctx.respond("You don't have an active session to end", ephemeral=True)


load_dotenv()
bot.add_cog(Pomodoro(bot))
bot.run(os.getenv("TOKEN"))
