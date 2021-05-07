import asyncio
import http.client
import boto3
from haptic_player import *
from twitchio.ext import commands
from sound_player import play_command_sound


streamer_id = "41138521"
channel_name = "aboveaveragetomato"
client_id = ""
client_secret = ""
irc_token = ""


def get_secrets():
    global client_id, client_secret, irc_token, channel_name
    ssm = boto3.client('ssm')

    client_id = ssm.get_parameter(Name='TwitchClientIdProd', WithDecryption=True)['Parameter']['Value']
    client_secret = ssm.get_parameter(Name='TwitchSecretProd', WithDecryption=True)['Parameter']['Value']
    irc_token = ssm.get_parameter(Name='TwitchOauthProd', WithDecryption=True)['Parameter']['Value']
    return


def bhaps_register_all():
    try:
        print("Registering Hug.Tact...")
        bhaps_player.register("Hug", "tacts/Hug.tact")
        print("Registering BackPat.Tact...")
        bhaps_player.register("Pat", "tacts/BackPat.tact")
        print("Registering Rubadubdub.Tact...")
        bhaps_player.register("Rubadubdub", "tacts/Rubadubdub.tact")
        print("Registering TiddyTwister.Tact...")
        bhaps_player.register("TiddyTwister", "tacts/TiddyTwister.tact")  # Rename to tiddytwister
        print("Registering FrontSmack.Tact...")
        bhaps_player.register("FrontSmack", "tacts/FrontSmack.tact")
        print("Registering BackSmack.Tact...")
        bhaps_player.register("BackSmack", "tacts/BackSmack.tact")
        print("Registering Zorro.Tact...")
        bhaps_player.register("Zorro", "tacts/Zorro.tact")
        print("Registering CutieCatScratch.Tact...")
        bhaps_player.register("CutieCatScratch", "tacts/CutieCatScratch.tact")
    except Exception as e:
        print(e)


def haptics_chat_play(command):
    global bhaps_player
    command_paths = {
        "!poke": {
            "Position": "VestBack",
            "PathPoints": [
                {
                    "X": "1",
                    "Y": "1",
                    "Intensity": 100
                },
                {
                    "X": "0.9",
                    "Y": "0.9",
                    "Intensity": 100
                },
                {
                    "X": "0.8",
                    "Y": "0.8",
                    "Intensity": 100
                },
            ],
            "DurationMillis": 800
        },
        "!hug": 'bhaps_player.submit_registered("Hug")',
        "!pat": 'bhaps_player.submit_registered("Pat")',
        "!rubadubdub": 'bhaps_player.submit_registered("Rubadubdub")',
        "!tiddytwister": 'bhaps_player.submit_registered("TiddyTwister")',
        "!frontSmack": 'bhaps_player.submit_registered("FrontSmack")',
        "!backSmack": 'bhaps_player.submit_registered("BackSmack")',
        "!zorro": 'bhaps_player.submit_registered("Zorro")',
        "!cutiecatscratch": 'bhaps_player.submit_registered("CutieCatScratch")',
    }

    if type(command_paths[command]) == dict:
        try:
            play_command_sound(command)
            bhaps_player.submit("pathPoint", command_paths[command])
        except Exception as e1:
            print(f"Haptics failed:\n{e1}")
    else:
        try:
            exec(command_paths[command])
        except Exception as e2:
            print(f"Haptics failed:\n{e2}")


# noinspection PyAbstractClass
class Bot(commands.Bot):
    def __init__(self):
        global client_id, irc_token, channel_name

        super().__init__(irc_token=irc_token,
                         client_id=client_id,
                         nick=channel_name,
                         prefix='!',
                         initial_channels=[channel_name])

    @staticmethod
    def get_oauth_token(self) -> str:
        """
        This function is absolute trash and should be rewritten to not grab a new token every call.
        :param self:
        :return: Oauth Token as string
        """
        global client_id, client_secret

        conn = http.client.HTTPSConnection("id.twitch.tv")
        payload = ''
        headers = {}
        conn.request("POST",
                     f"/oauth2/token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials",
                     payload, headers)
        res = conn.getresponse()
        data = res.read()
        data_dict = json.loads(data.decode("utf-8"))
        token = f"Bearer {data_dict['access_token']}"
        return token

    @staticmethod
    def is_follower(self, userId: str or int) -> bool:
        """
        Check if the user is following the sub user id.
        This function is absolute trash and should be rewritten to not grab a new token every call
        :param self: Bot instance
        :param userId: str or int
        :return: Boolean
        """
        global streamer_id, client_id

        # Check if it's the streamer:
        if int(userId) == int(streamer_id):
            return True

        token = Bot.get_oauth_token(self)

        conn = http.client.HTTPSConnection("api.twitch.tv")
        payload = ''
        headers = {
            'Authorization': token,
            'client-id': client_id
        }
        conn.request("GET", f"/helix/users/follows?to_id={streamer_id}", payload, headers)
        res = conn.getresponse()
        data = res.read()
        follower_dict = json.loads(data.decode("utf-8"))

        for follower in follower_dict['data']:
            if str(userId) == follower['from_id']:
                return True
        return False

    @staticmethod
    def check_phrases(self, message, author: str):
        # Check for any special phrases in the message text
        global channel_name
        phrases = {
            "Hipple Dipple He Ain't Got No Nipples": f"🍅🍅🍅 Ha {author.capitalize()}! You found a secret. 🍅🍅🍅",
            "hello tomato": f"Hi {author}!🍅",
            "hi guys": f"Hi {author}!🍅",
            "hello everyone": f"Hi {author}!🍅",
            "hey everyone": f"Hi {author}!🍅",
            "hey tomato": f"Hi {author}!🍅",
            "🍅🍅🍅": "MOAR TOMATO! 🍅🍅🍅🍅🍅🍅🍅🍅🍅🍅🍅🍅",
        }
        for phrase in phrases:
            # print(f"checking if {phrase.lower()=} is in {message.content.lower()=}")
            if phrase.lower() in message.content.lower():
                print(f"Found {phrase=} in {message.content=}")
                CHANNEL = bot.get_channel(channel_name)
                LOOP = asyncio.get_event_loop()
                LOOP.create_task(CHANNEL.send(phrases[phrase]))
                # reply_task = LOOP.create_task(CHANNEL.send(phrases[phrase]))
                # LOOP.run_until_complete(reply_task)

                # Break after first match to avoid accidental multi-messaging
                return True
        return False

    # On Bot Ready:
    # Events don't need decorators when subclassed
    async def event_ready(self):
        global channel_name
        print(f'Ready | BotName: {self.nick} | Channel: {channel_name}')

    # Main Message Processing Logic:
    async def event_message(self, message):
        print(f"({message.author.id}){message.author.name}: {message.content}")

        # Don't talk to yourself:
        if message.author.id == 0:
            return

        # Check for special phrases:
        author = message.author.name
        if self.check_phrases(self, message, author):
            # Then we are done and don't need to keep checking for admins or commands
            return

        # Check if it is a ! command
        await self.handle_commands(message)

    # Parse through Commands:
    # Commands use a decorator...
    # Most of these use haptics, but you change it to call your custom logic inside of these functions. This is what will exec if
    # someone in chat types in "!poke"
    @commands.command(name='poke')
    async def poke(self, ctx):
        # Are they a follower?
        follower = self.is_follower(self, ctx.author.id)
        if follower:
            try:
                haptics_chat_play("!poke")
            except Exception:
                await ctx.send(
                    f'Rut Roh. Something went wrong with the poke haptics. {ctx.author.name.capitalize()}, could you let AboveAverageTomato know?')
            else:
                await ctx.send(f'ARRRRRRRRGHHHH. Why you do this {ctx.author.name.capitalize()}??')
        else:
            await ctx.send(f'Sorry, {ctx.author.name} This command is only for followers and subscribers.')

    @commands.command(name='hug')
    async def hug(self, ctx):
        follower = self.is_follower(self, ctx.author.id)
        if follower:
            try:
                haptics_chat_play("!hug")
            except Exception:
                await ctx.send(
                    f'Rut Roh. Something went wrong with the poke haptics. {ctx.author.name.capitalize()}, could you let AboveAverageTomato know?')
            else:
                await ctx.send(f'♥♥♥ Thanks for the hug {ctx.author.name.capitalize()}!')
        else:
            await ctx.send(f'Sorry, {ctx.author.name.capitalize()} This command is only for followers and subscribers.')

    @commands.command(name='pat')
    async def pat(self, ctx):
        follower = self.is_follower(self, ctx.author.id)
        if follower:
            try:
                haptics_chat_play("!pat")
            except Exception:
                await ctx.send(
                    f'Rut Roh. Something went wrong with the poke haptics. {ctx.author.name.capitalize()}, could you let AboveAverageTomato know?')
            else:
                await ctx.send(f'Thanks. {ctx.author.name.capitalize()}.')
        else:
            await ctx.send(f'Sorry, {ctx.author.name.capitalize()} This command is only for followers and subscribers.')

    @commands.command(name='rubadubdub')
    async def rubadubdub(self, ctx):
        follower = self.is_follower(self, ctx.author.id)
        if follower:
            try:
                haptics_chat_play("!rubadubdub")
            except Exception:
                await ctx.send(
                    f'Rut Roh. Something went wrong with the poke haptics. {ctx.author.name.capitalize()}, could you let AboveAverageTomato know?')
            else:
                await ctx.send(f'Uh. Thanks? {ctx.author.name.capitalize()}.')
        else:
            await ctx.send(f'Sorry, {ctx.author.name.capitalize()} This command is only for followers and subscribers.')

    @commands.command(name='tiddytwister')
    async def rubNipples(self, ctx):
        follower = self.is_follower(self, ctx.author.id)
        if follower:
            try:
                haptics_chat_play("!tiddytwister")
            except Exception:
                await ctx.send(
                    f'Rut Roh. Something went wrong with the poke haptics. {ctx.author.name.capitalize()}, could you let AboveAverageTomato know?')
            else:
                await ctx.send(f'Why. {ctx.author.name.capitalize()}. WHY??')
        else:
            await ctx.send(f'Sorry, {ctx.author.name.capitalize()} This command is only for followers and subscribers.')

    @commands.command(name='backsmack')
    async def frontSmack(self, ctx):
        follower = self.is_follower(self, ctx.author.id)
        if follower:
            try:
                haptics_chat_play("!backsmack")
            except Exception:
                await ctx.send(
                    f'Rut Roh. Something went wrong with the poke haptics. {ctx.author.name.capitalize()}, could you let AboveAverageTomato know?')
            else:
                await ctx.send(f'Why. {ctx.author.name.capitalize()}. WHY??')
        else:
            await ctx.send(
                f'Sorry, {ctx.author.name.capitalize()} This command is only for followers and subscribers.')

    @commands.command(name='frontsmack')
    async def backSmack(self, ctx):
        follower = self.is_follower(self, ctx.author.id)
        if follower:
            try:
                haptics_chat_play("!frontsmack")
            except Exception:
                await ctx.send(
                    f'Rut Roh. Something went wrong with the poke haptics. {ctx.author.name.capitalize()}, could you let AboveAverageTomato know?')
            else:
                await ctx.send(f"It'll grow hair on your chest {channel_name.capitalize()}")
        else:
            await ctx.send(
                f'Sorry, {ctx.author.name.capitalize()} This command is only for followers and subscribers.')

    @commands.command(name='zorro')
    async def zorro(self, ctx):
        follower = self.is_follower(self, ctx.author.id)
        if follower:
            try:
                haptics_chat_play("!zorro")
            except Exception:
                await ctx.send(
                    f'Rut Roh. Something went wrong with the poke haptics. {ctx.author.name.capitalize()}, could you let AboveAverageTomato know?')
            else:
                await ctx.send(f'Only {ctx.author.name.capitalize()} can call my dreams stupid.')
        else:
            await ctx.send(
                f'Sorry, {ctx.author.name.capitalize()} This command is only for followers and subscribers.')

    @commands.command(name='cutiecatscratch')
    async def cutiecatscratch(self, ctx):
        follower = self.is_follower(self, ctx.author.id)
        if follower:
            try:
                haptics_chat_play("!cutiecatscratch")
            except Exception:
                await ctx.send(
                    f'Rut Roh. Something went wrong with the poke haptics. {ctx.author.name.capitalize()}, could you let AboveAverageTomato know?')
            else:
                await ctx.send(f'Meeeroow {ctx.author.name.capitalize()}')
        else:
            await ctx.send(
                f'Sorry, {ctx.author.name.capitalize()} This command is only for followers and subscribers.')


if __name__ == "__main__":
    # Get Twitch creds:
    get_secrets()

    # Run bot:
    bot = Bot()
    bot.run()




