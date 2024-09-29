# Copyright 2024 Toma-Ioan Dumitrescu

#!./.venv/bin/python

import discord      # base discord module
import code         # code.interact
import os           # environment variables
import inspect      # call stack inspection
import random       # random number generator

from discord.ext import commands    # Bot class and utils

############################### Helper Functions ###############################

# log_msg - pretty format print
#   @msg   : string to print
#   @level : log level from {'debug', 'info', 'warning', 'error'}
def log_msg(msg: str, level: str):
	# user selectable display config (prompt symbol, color)
	dsp_sel = {
		'debug'   : ('\033[34m', '-'),
		'info'    : ('\033[32m', '*'),
		'warning' : ('\033[33m', '?'),
		'error'   : ('\033[31m', '!'),
	}

	# internal ansi codes
	_extra_ansi = {
		'critical' : '\033[35m',
		'bold'     : '\033[1m',
		'unbold'   : '\033[2m',
		'clear'    : '\033[0m',
	}

	# get information about call site
	caller = inspect.stack()[1]

	# input sanity check
	if level not in dsp_sel:
		print('%s%s[@] %s:%d %sBad log level: "%s"%s' % \
			(_extra_ansi['critical'], _extra_ansi['bold'],
			caller.function, caller.lineno,
			_extra_ansi['unbold'], level, _extra_ansi['clear']))
		return

	# print the damn message already
	print('%s%s[%s] %s:%d %s%s%s' % \
		(_extra_ansi['bold'], *dsp_sel[level],
		caller.function, caller.lineno,
		_extra_ansi['unbold'], msg, _extra_ansi['clear']))

############################## Bot Implementation ##############################

# bot instantiation
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
channel_id = 1175193291004846203

# on_ready - called after connection to server is established
@bot.event
async def on_ready():
	log_msg('logged on as <%s>' % bot.user, 'info')

# on_message - called when a new message is posted to the server
#   @msg : discord.message.Message
@bot.event
async def on_message(msg):
	# filter out our own messages
	if msg.author == bot.user:
		return

	log_msg('message from <%s>: "%s"' % (msg.author, msg.content), 'debug')
	# overriding the default on_message handler blocks commands from executing
	# manually call the bot's command processor on given message
	await bot.process_commands(msg)

# roll - rng chat command
#   @ctx     : command invocation context
#   @max_val : upper bound for number generation (must be at least 1)
@bot.command(brief='Generate random number between 1 and <arg>')
async def roll(ctx, max_val: int):
	# argument sanity check
	if max_val < 1:
		raise Exception('argument <max_val> must be at least 1')

	await ctx.send(random.randint(1, max_val))

# roll_error - error handler for the <roll> command
#   @ctx     : command that crashed invocation context
#   @error   : ...
@roll.error
async def roll_error(ctx, error):
	await ctx.send(str(error))

# play - song chat command
#   @ctx    : command invocation context
#   @song   : song name that should be installed locally
@bot.command(brief='Connect to the voice channel and play <song>')
async def play(ctx, song: str):
	channel = ctx.author.voice.channel
	if channel == None:
		raise Exception('A voice channel must be open')

	op_channel = await channel.connect()
	path = r"C:\Users\User\Desktop\discord_bot\songs\\" + song
	if not os.path.exists(path):
		raise Exception('The song name is not correct')

	op_channel.play(
		discord.FFmpegPCMAudio(
			executable = r"C:\Users\User\scoop\shims\ffmpeg.exe",
			source = path,
		)
	)

	await ctx.send(f"Playing a song on {channel.name}")

# play_error - error handler for the <play> command
#   @ctx     : command that crashed invocation context
#   @error   : ...
@play.error
async def play_error(ctx, error):
	await ctx.send(str(error))

# list chat command
#   @ctx     : command invocation context
@bot.command(brief='Lists available songs')
async def list(ctx):
	songs = r"C:\Users\User\Desktop\discord_bot\songs\\"
	song_list = ""
	for song in os.listdir(songs):
		song_list = song_list + song + "\n"

	await ctx.send(song_list)

# scram chat command
#   @ctx     : command invocation context
@bot.command(brief='Leave the voice channel instantly')
async def scram(ctx):
	channel = ctx.voice_client
	if channel == None:
		raise Exception('A voice channel must be open')

	await channel.disconnect()
	await ctx.send(f"Sam left the voice channel")

# scram - error handler for the <scram> command
#   @ctx     : command that crashed invocation context
#   @error   : ...
@scram.error
async def scram_error(ctx, error):
	await ctx.send(str(error))

# on_voice_state_update - called when the bot is left alone on the voice channel
#   @member		: member whose voice states changed
#   @before		: voice state prior to the changes
#   @after		: voice state after the changes
@bot.event
async def on_voice_state_update(member, before, after):
	if before.channel == None:
		return

	members = before.channel.members
	bot_left_alone = len(members) == 1 and members[0].name == bot.user.name
	if bot_left_alone:
		await bot.voice_clients[0].disconnect()

# on_member_join - called when the a member joins the server
#   @member		: member when joining the server
@bot.event
async def on_member_join(member):
	channel = bot.get_channel(channel_id)
	reply = random.randint(1, 5)
	greets = ""

	match reply:
		case 1:
			greets = "You made it, " + member.name + "!"
		case 2:
			greets = "Nice to meet you, " + member.name + "!"
		case 3:
			greets = "Welcome to the server, " + member.name + "!"
		case 4:
			greets = "Have fun, " + member.name + "!"
		case _:
			greets = "Hello, " + member.name + "!"

	await channel.send(greets)

############################# Program Entry Point ##############################

if __name__ == '__main__':
	# check that token exists in environment
	if 'BOT_TOKEN' not in os.environ:
		log_msg('save your token in the BOT_TOKEN env variable!', 'error')
		exit(-1)

	# launch bot (blocking operation)
	bot.run(os.environ['BOT_TOKEN'])
