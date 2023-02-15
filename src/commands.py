import random

import settings
from context import Context


def ban_id(context: Context, user_id: int):
    # get message
    message = context.message
    # special case
    if user_id == settings.USER_IDS["Merlin"]:
        await message.reply("https://tenor.com/view/"
                            "you-have-no-power-here-lotr-the-lord-of-the-rings-gandalf-gif-17924404")
        return
    # normal gamble
    if random.randint(0, 6) == 0:
        try:
            # fetch nils
            nils = await message.guild.query_members(user_ids=[user_id])
            nils = nils[0]
            # send dm
            await nils.create_dm()
            await nils.dm_channel.send('https://discord.gg/ZdSQEFfcHw')
            # kick
            reason = ' '.join(context.argv[1:])
            await nils.kick(reason=reason)
            # msg
            kickmsgs: list[str] = [
                "https://tenor.com/view/penguin-hit-head-smack-head-funny-fall-gif-16306739",
                "https://tenor.com/view/moris-cipson-twoj-stary-twoja-stara-minecraft-fortnite"
                "-xd-beka-memy-memes-mem-call-of-duty-warzone-bedoes-gif-20247198"
            ]
            await message.reply(random.choice(kickmsgs))
            return
        except Exception as e:
            print(f'Can not ban Nils: {e}')
            await message.reply("Leider nicht!")
    # send fail
    await message.reply("https://tenor.com/view/supernatural-deanwinchester-cartoon-gun-bang-gif-4867452")


command_mapping: {str: callable(Context)} = {
    "nils": lambda c: ban_id(c, settings.USER_IDS["Nils"]),
    "muha": lambda c: ban_id(c, settings.USER_IDS["Muha"]),
    "emely": lambda c: ban_id(c, settings.USER_IDS["Emely"]),
    "finn": lambda c: ban_id(c, settings.USER_IDS["Finn"]),
    "merlin": lambda c: ban_id(c, settings.USER_IDS["Merlin"]),
}

commands = {command_mapping.keys()}


def call_if_command(context: Context) -> bool:
    command = context.command
    # check if handled
    if command not in commands:
        return False
    # execute method
    command_mapping[command](context)
    # return successful execution
    return True
