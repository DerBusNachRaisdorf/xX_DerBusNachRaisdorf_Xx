import random

from settings import *
from context import Context


async def __cmd_ban_id(context: Context, user_id: int):
    # get message
    message = context.message
    # special case
    if user_id == get_raisdorfuser_by_name('Merlin').id:
        await message.reply("https://tenor.com/view/"
                            "you-have-no-power-here-lotr-the-lord-of-the-rings-gandalf-gif-17924404")
        return
    # normal gamble
    if random.randint(0, 5) == 0:
        try:
            # fetch nils
            nils = await message.guild.query_members(user_ids=[user_id])
            nils = nils[0]
            # send dm if possible
            try:
                await nils.create_dm()
                await nils.dm_channel.send('https://discord.gg/ZdSQEFfcHw')
            except:
                pass
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


async def __cmd_get_raisdorfuser_by_name(ctx: Context):
    if len(ctx.argv) < 2:
        await ctx.message.reply('not enough arguments')
        return

    for usr_name in ctx.argv[1:]:
        raisdorf_usr = get_raisdorfuser_by_name(usr_name)
        response: str = 'unknown user' if raisdorf_usr == None else str(raisdorf_usr)
        await ctx.message.reply(response)


command_mapping: dict[str: callable(Context)] = {
    # bann commands
    "nils"  : lambda c: __cmd_ban_id(c, get_raisdorfuser_by_name("Nils").id),
    "muha"  : lambda c: __cmd_ban_id(c, get_raisdorfuser_by_name("Muha").id),
    "emely" : lambda c: __cmd_ban_id(c, get_raisdorfuser_by_name("Emely").id),
    "finn"  : lambda c: __cmd_ban_id(c, get_raisdorfuser_by_name("Finn").id),
    "merlin": lambda c: __cmd_ban_id(c, get_raisdorfuser_by_name("Merlin").id),
    "merlin2": lambda c: __cmd_ban_id(c, get_raisdorfuser_by_name("Merlin2").id),
    # utility commands
    "get_raisdorfuser_by_name" : __cmd_get_raisdorfuser_by_name
}


commands = {*command_mapping.keys()}


async def call_if_command(context: Context) -> bool:
    command = context.command
    # check if handled
    if command not in commands:
        return False
    # execute method
    await command_mapping[command](context)
    # return successful execution
    return True
