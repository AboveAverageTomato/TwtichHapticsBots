from playsound import playsound


def play_command_sound(command):

    command_sounds = {
        "!hug": "sounds/error.wav",
        "!pat": "sounds/error.wav",
        "!poke": "sounds/error.wav",
        "!rub": "sounds/error.wav",

    }

    if command in command_sounds:
        playsound(command_sounds[command], False)

    return
