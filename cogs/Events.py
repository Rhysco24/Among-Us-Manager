import random
import discord
from discord.ext import commands

import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from objects import *

class Events(commands.Cog):

    def __init__(self, client):
        self.client = client

    """
        EVENTS: on_ready
                on_guild_leave
                on_reaction_add
                on_command_error
    """


    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="am.help"))
        print('Bot is ready.')

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        #Make sure reaction isn't from bot
        if user == self.client.user:
            return

        reaction = str(reaction)

        #Make sure reaction is releated to the game
        if reaction != '☠' and reaction != '📢' and reaction != '🔇' and reaction != '⏮':
            return

        #Variables needed
        try:
            voiceChannel = user.voice.channel
        except:
            return

        member = user

        gamecommand = self.client.get_cog('GameCommands')

        #Dead reaction
        if reaction == '☠':
            await gamecommand.changeDead(member, voiceChannel)

        #Meeting reaction
        elif reaction == '📢':
            await gamecommand.changeStage(member, voiceChannel, Stage.Meeting)

        #Mute reaction
        elif reaction == '🔇':
            await gamecommand.changeStage(member, voiceChannel, Stage.Round)

        #Meeting reaction
        elif reaction == '⏮':
            await gamecommand.changeStage(member, voiceChannel, Stage.Lobby)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        permissionString = 'Missing permissions.\nReinvite bot to regain bot permissions or check text channel permissions. Use `am.info` to get invite link.'

        #This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return

        # This prevents any cogs with an overwritten cog_command_error being handled here.
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound, )

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        #BAD ARGUMENT
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Invalid member! Use @user or member#ID")

        #MISSING PERMISSIONS
        elif 'Missing Permissions' in str(error):
            try:
                channel = ctx.author.dm_channel()
            except:
                channel = await ctx.author.create_dm()

            guild = ctx.guild.name

            try:
                await channel.send(permissionString)
            except discord.Forbidden:
                try:
                    await ctx.send(permissionString)
                except:
                    print('test')

        #UNKNOWN MESSAGE (USUALLY INTERFACE)
        elif 'Unknown Message' in str(error):
            manage = self.client.get_cog('ManagementCommands')
            await manage.update(ctx)

        #UNKNOWN CHANNEL
        elif 'Unknown Channel' in str(error):
            await ctx.send('Error: Game text channel deleted.')
            cmd = self.client.get_cog('StartCommands')
            await cmd.endgame(ctx)

        #MISSING REQUIRED ARGUMENTS
        elif isinstance(error, commands.MissingRequiredArgument):
            command = str(ctx.command)

            try:
                await ctx.send('am.' + command + ' is missing an extra part. Check `am.help` for commands.')
            except Exception as e:
                if 'Missing Permissions' in str(e):
                    try:
                        channel = ctx.author.dm_channel()
                    except:
                        channel = await ctx.author.create_dm()

                    guild = ctx.guild.name

                    await channel.send(permissionString)

        #UNKNOWN ERRORS
        else:
            print(str(ctx.command) + ": " + str(error))
            return



def setup(bot):
    bot.add_cog(Events(bot))
