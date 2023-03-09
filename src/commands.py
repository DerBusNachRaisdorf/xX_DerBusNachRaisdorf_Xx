import random

from settings import *
from context import Context
from collections import namedtuple
from utility.mememail import mememail_send

SERVER_INVITE_LINK: str = 'https://discord.gg/ZdSQEFfcHw'


RaisdorfCommand = namedtuple("RaisdorfCommand", "callable admins_only")


async def __cmd_ban_id(context: Context, user_id: int):
    async def send_kickmail():
        try:
            raisuser = get_raisdorfuser_by_id(user_id)
            smtp_host = context.settings.email_smtp_host
            sender = context.settings.email_sender
            password = context.settings.email_password
            subject = 'Der Bus rollt an, bitte steigen Sie ein.'
            body = f'Guten Tag {raisuser.name}!\n\nSie wurden von {get_raisdorfuser(context.message.author).name} gekickt.\n\n'
            body += f'{get_raisdorfuser(context.message.author).name} entschuldigt sich für sein Fehlverhalten und möchte Sie dazu ermutigen, dem Server wieder beizutreten.\n\n'
            body += f'Link: {SERVER_INVITE_LINK}\n\nMit freundlichen Grüßen\nIhr Bus nach Raisdorf\n'
            mememail_send(smtp_host, sender, password, raisuser.mail, subject, body)
        except Exception as e:
            await message.reply(f'Konnte email nicht senden: {e}.')
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
            await message.reply(f"Leider nicht!: {e} : {nils}")
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


async def __cmd_rechtschreibfehler(ctx: Context):
    for id, data in ctx.settings.fehlerqouten.items():
        data: list[int] = data
        name: str = get_raisdorfuser_by_id(id).name
        errors: int = data[0]
        words: int = data[1]
        await ctx.message.reply(f'***{name}***: **{(errors/words) * 100.0}% falsch** ({errors}/{words})')


async def __cmd_reset_rechtschreibfehler(ctx: Context):
    ctx.settings.fehlerqouten = {}
    await ctx.message.reply('done.')


async def __cmd_add_word(ctx: Context):
    if len(ctx.argv) != 2:
        await ctx.message.reply('Ich will bitte genau ein Argument haben.')
        return
    ctx.deutschlehrer.write('add_word')
    ctx.deutschlehrer.write(ctx.argv[1])
    result: str = ctx.deutschlehrer.read()
    await ctx.message.reply(result)


async def __cmd_raisdorfgpt_system(ctx: Context):
    if len(ctx.argv) < 2:
        await ctx.message.reply('Nein bitte mehr Argumente!!!!')
        return
    message: str = ' '.join(ctx.argv[1:])
    ctx.raisdorf_gpt.chatgpt.add_system_message(message)
    await ctx.message.reply('JAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')


#command_mapping: dict[str: callable(Context)] = {
command_mapping: dict[str: RaisdorfCommand] = {
    # bann commands
    "nils"  :   RaisdorfCommand(lambda c: __cmd_ban_id(c, get_raisdorfuser_by_name("Nils").id), False),
    "muha"  :   RaisdorfCommand(lambda c: __cmd_ban_id(c, get_raisdorfuser_by_name("Muha").id), False),
    "emely" :   RaisdorfCommand(lambda c: __cmd_ban_id(c, get_raisdorfuser_by_name("Emely").id), False),
    "finn"  :   RaisdorfCommand(lambda c: __cmd_ban_id(c, get_raisdorfuser_by_name("Finn").id), False),
    "merlin":   RaisdorfCommand(lambda c: __cmd_ban_id(c, get_raisdorfuser_by_name("Merlin").id), False),
    "merlin2":  RaisdorfCommand(lambda c: __cmd_ban_id(c, get_raisdorfuser_by_name("Merlin2").id), False),
    # DerDeutschlehrer
    "rechtschreibfehler" : RaisdorfCommand(__cmd_rechtschreibfehler, False),
    "reset_rechtschreibfehler" : RaisdorfCommand(__cmd_reset_rechtschreibfehler, True),
    "add_word" : RaisdorfCommand(__cmd_add_word, True),
    # RaisdorfGPT
    "raisdorfgpt_system": RaisdorfCommand(__cmd_raisdorfgpt_system, True),
    # utility commands
    "get_raisdorfuser_by_name" : RaisdorfCommand(__cmd_get_raisdorfuser_by_name, False)
}


commands = {*command_mapping.keys()}


async def call_if_command(context: Context) -> bool:
    command = context.command
    # check if handled
    if command not in commands:
        return False
    # execute method
    if command_mapping[command].admins_only and not member_is_admin(context.message.author):
        await context.message.reply(f'Finger weg, {get_raisdorfuser(context.message.author).name}!')
    else:
        try:
            await command_mapping[command].callable(context)
        except Exception as e:
            await context.message.reply(f'Fehler: {e}')
    # return successful execution
    return True
