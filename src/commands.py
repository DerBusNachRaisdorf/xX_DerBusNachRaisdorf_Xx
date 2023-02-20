import random

from settings import *
from context import Context
from utility.mememail import mememail_send

SERVER_INVITE_LINK: str = 'https://discord.gg/ZdSQEFfcHw'


async def __cmd_ban_id(context: Context, user_id: int):
    async def send_kickmail():
        try:
            raisuser = get_raisdorfuser_by_id(user_id)
            smtp_host = context.settings.email_smtp_host
            sender = context.settings.email_sender
            password = context.settings.email_password
            subject = 'Der Bus rollt an, bitte steigen Sie ein.'
            body = f'Guten Tag {raisuser.name}!\n\nSie wurden von {get_raisdorfuser(context.message.author)} gekickt.\n\n'
            body += f'{get_raisdorfuser(context.message.author)} entschuldigt sich für sein Fehlverhalten und möchte Sie dazu ermutigen, dem Server wieder beizutreten.\n\n'
            body += f'Link: {SERVER_INVITE_LINK}\n\nMit freundlichen Grüßen\nIhr Bus nach Raisdorf\n'
            mememail_send(smtp_host, sender, password, subject, body)
        except Exception as e:
            await message.replay(f'Konnte email nicht senden: {e}.')
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
            # send email if u wish
            if get_raisdorfuser_by_id(user_id).send_mail_on_kick:
                await send_kickmail()
            # send dm if possible
            try:
                await nils.create_dm()
                await nils.dm_channel.send('https://discord.gg/ZdSQEFfcHw')
            except:
                if get_raisdorfuser_by_id(user_id).send_mail_on_kick == False: # jaja, not verwende ich jzt nicht mehr
                    await send_kickmail()
            # kick
            reason = ' '.join(context.argv[1:])
            await nils.kick(reason=reason)
            # msg
            kickmsgs: list[str] = [
                "https://tenor.com/view/penguin-hit-head-smack-head-funny-fall-gif-16306739",
                "https://tenor.com/view/moris-cipson-twoj-stary-twoja-stara-minecraft-fortnite"
                "-xd-beka-memy-memes-mem-call-of-duty-warzone-bedoes-gif-20247198",
                "https://tenor.com/view/metro-itmek-push-gif-19915491",
                "https://tenor.com/view/trap-door-bye-elimination-loser-ellen-degeneres-gif-10498098",
                "https://tenor.com/view/muppets-fozzie-kermit-trap-door-bye-gif-22005102",
                "https://tenor.com/view/chris-rock-gif-25292321"
            ]
            await message.reply(random.choice(kickmsgs))
            return
        except Exception as e:
            print(f'Can not ban Nils: {e}')
            await message.reply("Leider nicht!")
    # send fail
    fails = ["https://tenor.com/view/matrix-dodge-neo-gif-13288848",
             "https://tenor.com/view/supernatural-deanwinchester-cartoon-gun-bang-gif-4867452",
             "https://tenor.com/view/anime-dodge-dancing-gif-9449699",
             "https://tenor.com/view/dodge-the-matrix-swerve-lunge-dive-gif-22197111"
             ]
    await message.reply(random.choice(fails))


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
