import asyncio
import os
import random
import json
from sys import stderr
import subprocess
import random

import discord
from discord.utils import get

import image_gen
import utility.markdown
from utility.proc import run_proc

SETTINGS_FILE: str = '/home/shared/botsettings.json'
BACKGROUND_TIMER_INTERVAL_SEC: int = 10
BROADCAST_TIMER_INTERVAL_SEC: int = 15 * 60
TARGET_USER_ID: int = 373093304767873044
REVILUM: str = "Revilum"
ADMIN_USER_IDS: list[int] = [330701572118151169, 373093304767873044]
USER_ALIASES: dict[int, str] = {
    224037892387766272: 'Nils',
    397130478907293707: 'Muha',
    373093304767873044: 'Finn',
    696336485846220803: 'Emely',
    330701572118151169: 'Merlin'
}


""" commands """
CMD_ADD_ADVERT: str = '!add_advert'
CMD_REMOVE_ADVERT: str = '!remove_advert'
CMD_PRINT_ADVERTS: str = '!print_adverts'
CMD_MEME: str = '!meme'
CMD_OFFEND: str = '!offend'
CMD_RESTART: str = '!restart'
CMD_INFO: str = '!info'
CMD_EXEC: str = '!exec'
CMD_EXEC_DASH: str = '!dash'
CMD_EXEC_BASH: str = '!bash'
CMD_WHOAMI: str = '!whoami'
CMD_CHANGE_STATUS: str = '!status'

INFO_STR: str = 'undefined'
MAX_EXEC_LENGTH: int = 800


def shorten_str(s: str, to: int) -> str:
    if len(s) >= to:
        return s[0:to]
    else:
        return s


def shorten_str_lines(s: str, to: int) -> str:
    lines: list[str] = s.splitlines()
    if len(lines) <= to:
        return s
    else:
        return ''.join(lines[0:to])


def is_whitespace(c) -> bool:
    return c == ' ' or c == '\t'


def tokenize_argv(cmd: str) -> list[str]:
    argv: list[str] = []
    cur_token: str = ''
    is_str: bool = False
    is_esc: bool = False
    for c in cmd:
        if c == '"' and not is_esc:
            is_str = not is_str
        elif c == '\\' and not is_esc:
            is_esc = True
        elif is_whitespace(c) and not is_str and not is_esc and cur_token != '':
            argv.append(cur_token)
            cur_token = ''
        else:
            cur_token += c
            is_esc = False
    if cur_token != '':
        argv.append(cur_token)
    return argv


def make_str_literal(s: str) -> str:
    res: str = ''
    for c in s:
        if c == '"':
            res += '\\"'
        else:
            res += c
    return res


def user_get_name(discord_user) -> str:
    if discord_user.id in USER_ALIASES:
        return USER_ALIASES[discord_user.id]
    else:
        return discord_user.name


class Settings:
    def __init__(self):
        self.admin_channel_id: int = 985262849775525998
        self.advert_channel_id: int = 985262936291430470
        self.broadcast_messages: list[str] = [
            'Es gibt eine Menge gute IDEs!\nDiese sind super leicht zu installieren und zu nutzen!\nHier ist eine: \nhttps://code.visualstudio.com/',
            'Es gibt eine Menge gute IDEs!\nDiese sind super leicht zu installieren und zu nutzen!\nHier ist eine: \nhttps://www.jetbrains.com/de-de/idea/',
            'Es gibt eine Menge gute IDEs!\nDiese sind super leicht zu installieren und zu nutzen!\nHier ist eine: \nhttps://www.eclipse.org/downloads/',
            'Erstellen Sie sich jetzt einen GitHub account!\nhttps://github.com/signup',
            'Git ist super! Installieren Sie Git jetzt!\nhttps://git-scm.com/',
            'Es gibt viele IDEs, die speziell für Java geeignet sind. Einen Überblick finden Sie hier:\n https://www.programmierenlernenhq.de/java-programmieren-lernen-die-besten-java-entwicklungsumgebungen/',
            'Der Windows Editor war gestern!\nInstallieren Sie jetzt eine komfortable IDE Ihrer Wahl!',
            'Veränderen Sie die Welt!\nhttps://chng.it/zYD5T2Fc'
        ]
        self.kunst_channel_ids: int = [1051567423083532358, 1067251515066159224, 1052004758451392662]

    def to_dict(self) -> dict:
        return {
            'admin_channel_id': self.admin_channel_id,
            'advert_channel_id': self.advert_channel_id,
            'broadcast_messages': self.broadcast_messages
        }

    def from_dict(self, d: dict):
        if 'admin_channel_id' in d:
            self.admin_channel_id = d['admin_channel_id']
        if 'advert_channel_id' in d:
            self.advert_channel_id = d['advert_channel_id']
        if 'broadcast_messages' in d:
            self.broadcast_messages = d['broadcast_messages']


class DerBusNachRaisdorfClient(discord.Client):

    greetings: list[str] = [
        'Moin!',
        'Hallo',
        'Guten Tag!'
    ]

    async def load_settings(self):
        self.settings = Settings()
        try:
            with open(SETTINGS_FILE, 'r') as f:
                self.settings.from_dict(json.loads(f.read()))
        except Exception as e:
            print('Can not load settings file.', file=stderr)
            await self.get_channel(self.settings.admin_channel_id).send(f'Can not load settings: {e}!')

    async def save_settings(self):
        try:
            json_string: str = json.dumps(self.settings.to_dict())
            with open(SETTINGS_FILE, "w") as f:
                f.write(json_string)
        except Exception as e:
            print('Can not save settings file.', file=stderr)
            await self.get_channel(self.settings.admin_channel_id).send(f'Can not save settings: {e}!')

    async def on_ready(self):
        await self.load_settings()
        self.loop.create_task(self.background_timer())
        self.loop.create_task(self.broadcast_timer())
        print(f'{self.user.name} is nun da!')

    async def on_member_join(self, member):
        """ greet new members... """
        await member.create_dm()
        await member.dm_channel.send(
            f'Hi {member.name}, ja, der Bus fährt nach Raisdorf!'
        )

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            """ this bot won't respond to its own messages. """
            return

        if not message.guild:
            """ this bot can respond to dms! """
            if message.content == '!subscribe':
                pass
            return

        if 'xD' in message.content or 'XD' in message.content:
            await message.reply('xD' + ''.join(['D' if random.randint(0, 1000) > 5 else ' rofl lulululul lul xD' for i in range(random.randint(0, 50))]))
        elif 'hallo' in message.content.lower():
            """ this bot is quite polite """
            response = random.choice(self.greetings)
            await message.reply(response)
        elif ' ide ' in message.content.lower() or message.content.lower()[0:3] == 'ide':
            """ this bot will recommend u an ide. """
            response: str = 'Es gibt eine Menge gute IDEs!\nDiese sind super leicht zu installieren und zu nutzen!\nHier ein paar links: \nhttps://code.visualstudio.com/\nhttps://www.jetbrains.com/de-de/idea/\nhttps://www.eclipse.org/downloads/'
            await message.channel.send(response)
        elif 'github' in message.content.lower():
            """ this bot will annoy u to create a github account """
            response: str = 'Erstellen Sie sich jetzt einen GitHub account!\nhttps://github.com/signup'
            await message.channel.send(response)
        elif 'git' in message.content.lower():
            """ this bot will annoy u to install git """
            response: str = 'Git ist super! Installieren Sie Git jetzt!\nhttps://git-scm.com/'
            await message.channel.send(response)
        elif message.channel.id in self.settings.kunst_channel_ids and len(message.attachments) != 0:
            responses: list[list[str]] = [
                ['uiiiiiiiii'],
                ['feinstens'],
                ['eiiiiiiiii'],
                ['picasso'],
                ['sheeeeeeeeesh'],
                ['schöööööööööööööööön'],
                ['sahne'],
                ['feine marmelade'],
                ['Die Kunst, die vor uns liegt, ist ein Meisterwerk der visuellen Ausdruckskraft und der emotionalen Tiefe. Der Künstler hat es verstanden, die Essenz des menschlichen Daseins auf eine Weise darzustellen, die uns tief berührt und zum Nachdenken anregt. Das Bild ist von einer bemerkenswerten kompositorischen Klarheit, die uns die Aufmerksamkeit auf die wesentlichen Elemente lenkt und uns die Möglichkeit gibt, die tiefere Bedeutung des Werks zu erfassen. Der Einsatz von Farbe und Licht ist von großer Meisterschaft und trägt dazu bei, die Stimmung und Atmosphäre des Werks zu verstärken.' , 'Die Darstellung der Figuren und Objekte im Bild ist von einer erstaunlichen Lebendigkeit und emotionalen Tiefe. Jede einzelne Figur scheint eine eigene Geschichte zu erzählen und trägt zur Gesamtaussage des Werks bei. Die Interaktion der Figuren untereinander und mit ihrer Umgebung ist von einer beeindruckenden Intelligenz und Sensibilität.','Insgesamt ist das hier vorliegende Werk ein triumphales Beispiel für die Kraft der Kunst, uns zum Nachdenken anzuregen und uns emotional zu berühren. Es ist ein unvergessliches Erlebnis und ein unbestreitbares Meisterwerk, das für die Ewigkeit bestehen wird.'],
                ['Es ist unbestreitbar, dass das betrachtete Designelement eine tiefgründige und ästhetisch ansprechende Darstellung von Kunst darstellt. Der Schöpfer des Designs hat offensichtlich große Sorgfalt und Aufmerksamkeit auf jedes Detail verwendet, um sicherzustellen, dass jeder Aspekt des Elements visuell ansprechend und kommunikativ ist.', 'Das Farbschema des Elements ist von außerordentlicher Brillanz und subtiler Nuancierung, was zu einer harmonischen Zusammensetzung beiträgt, die die Aufmerksamkeit des Betrachters auf sich zieht. Es gibt eine klare Verwendung von Kontrasten, die dazu beiträgt, die visuelle Wirkung des Elements zu verstärken und es lebendiger und dynamischer zu machen.', 'Die Formen und Linien, die im Design verwendet werden, sind von erstaunlicher Präzision und Eleganz. Sie tragen dazu bei, die visuelle Struktur des Elements zu stärken und zu definieren, wodurch die Botschaft, die es vermitteln möchte, noch deutlicher wird. Es gibt auch eine klare Verwendung von Symbolik und metaphorischen Elementen, die dazu beitragen, die tiefere Bedeutung des Designs zu vermitteln.', 'Insgesamt ist das betrachtete Designelement ein Meisterwerk der visuellen Kunst, das sowohl in seiner Schönheit als auch in seiner Botschaft beeindruckt. Es ist ein klares Beispiel dafür, wie Design und Kunst miteinander verschmelzen können, um etwas zu schaffen, das sowohl visuell als auch inhaltlich ansprechend ist.'],
                ['Das betrachtete Designelement ist ein bemerkenswertes Beispiel für die komplexen dynamischen Zusammenhänge, die in der visuellen Kunst vorherrschen. Es demonstriert eine Meisterschaft in der Anwendung von Farbtheorie, Formenlehre und Linienführung, die für eine erfolgreiche Gestaltung von entscheidender Bedeutung sind.', 'Der Schöpfer des Designs hat offensichtlich ein tiefes Verständnis für die psychologischen Auswirkungen von Farben und Formen auf den Betrachter und hat diese Elemente geschickt eingesetzt, um eine bestimmte emotionale Wirkung zu erzielen. Auch die Verwendung von Symbolik und metaphorischen Elementen trägt dazu bei, die tiefere Bedeutung des Designs zu vermitteln und eine Verbindung zwischen dem Betrachter und dem Element herzustellen.', 'Insgesamt ist das betrachtete Designelement ein beeindruckendes Beispiel für die kunstwissenschaftlichen Prinzipien, die in der visuellen Kunst Anwendung finden. Es ist ein klares Beispiel dafür, wie die Anwendung von kunstwissenschaftlichen Methoden und Techniken dazu beitragen kann, ein erfolgreiches und aussagekräftiges Design zu schaffen.'],
                ['Das betrachtete Designelement ist ein beispielhaftes Manifest der kunsthistorischen und ästhetischen Konzepte, die in der visuellen Kunst von essenzieller Bedeutung sind. Es ist ein Paradebeispiel für die Meisterschaft der Anwendung von harmonischen Farbschemata, präzisen Formen und Linienführungen sowie der Verwendung von Symbolik und metaphorischen Elementen, die zusammenwirken, um ein visuelles Meisterwerk zu schaffen.', 'Der Schöpfer des Designs hat offensichtlich ein tiefes Verständnis für die komplexen kunsthistorischen Zusammenhänge, die in der Gestaltung von elementarer Bedeutung sind, und hat diese Kenntnisse gekonnt angewendet, um eine visuelle Sprache zu schaffen, die sowohl in ihrer Schönheit als auch in ihrer Aussagekraft beeindruckend ist.', 'Auch die Verwendung von Symbolik und metaphorischen Elementen trägt dazu bei, die tiefere Bedeutung des Designs zu vermitteln und eine Verbindung zwischen dem Betrachter und dem Element herzustellen. Es ist ein deutliches Beispiel dafür, wie die Anwendung von kunsthistorischen Konzepten und Techniken dazu beitragen kann, ein erfolgreiches und aussagekräftiges Design zu schaffen, das sowohl in seiner Schönheit als auch in seiner tieferen Bedeutung beeindruckt.', 'Insgesamt ist das betrachtete Designelement ein triumphales Beispiel für die Vielfalt und die Schönheit der visuellen Kunst und ein klares Zeugnis dafür, dass der Schöpfer ein Meister seines Fachs ist.'],
                ['Das betrachtete visuelle Symbol ist ein beispielhaftes Manifest der kunsthistorischen und ästhetischen Konzepte, die in der visuellen Kunst von essenzieller Bedeutung sind. Es ist ein Paradebeispiel für die Meisterschaft der Anwendung von harmonischen Farbschemata, präzisen Formen und Linienführungen sowie der Verwendung von Symbolik und metaphorischen Elementen, die zusammenwirken, um ein visuelles Meisterwerk zu schaffen.', 'Der Schöpfer des visuellen Symbols hat offensichtlich ein tiefes Verständnis für die komplexen kunsthistorischen Zusammenhänge, die in der Gestaltung von elementarer Bedeutung sind, und hat diese Kenntnisse gekonnt angewendet, um eine visuelle Sprache zu schaffen, die sowohl in ihrer Schönheit als auch in ihrer Aussagekraft beeindruckend ist.', 'Auch die Verwendung von Symbolik und metaphorischen Elementen trägt dazu bei, die tiefere Bedeutung des visuellen Symbols zu vermitteln und eine Verbindung zwischen dem Betrachter und dem Symbol herzustellen. Es ist ein deutliches Beispiel dafür, wie die Anwendung von kunsthistorischen Konzepten und Techniken dazu beitragen kann, ein erfolgreiches und aussagekräftiges visuelles Symbol zu schaffen, das sowohl in seiner Schönheit als auch in seiner tieferen Bedeutung beeindruckt.', 'Insgesamt ist das betrachtete visuelle Symbol ein triumphales Beispiel für die Vielfalt und die Schönheit der visuellen Kunst und ein klares Zeugnis dafür, dass der Schöpfer ein Meister seines Fachs ist.', 'Es ist durchaus möglich, dass das betrachtete visuelle Symbol von dem berühmten Künstler MrSubidubi geschaffen wurde. MrSubidubi ist bekannt für seine Meisterschaft in der Anwendung von harmonischen Farbschemata und präzisen Formen und Linienführungen, die in diesem visuellen Symbol deutlich zu erkennen sind. Auch seine Verwendung von Symbolik und metaphorischen Elementen ist ein Markenzeichen seiner Arbeit und trägt dazu bei, die tiefere Bedeutung des Symbols zu vermitteln.', 
                 'MrSubidubi hat in der Vergangenheit mehrere Auszeichnungen für seine Arbeit erhalten, darunter den prestigeträchtigen "Kunstpreis der Stadt" und den "Internationalen Preis für visuelle Gestaltung". Er hat auch mehrere Ausstellungen seiner Arbeiten in renommierten Galerien und Museen auf der ganzen Welt gehabt.',
                 'Es ist jedoch zu beachten, dass dies lediglich Vermutungen sind und ohne offizielle Bestätigung durch den Künstler oder das betreffende Museum oder Galerie nicht als Tatsache betrachtet werden sollten.'],
                ['Es ist eine unbestreitbare Wahrheit, dass die Schönheit und Aussagekraft der Kunst die Seele des Betrachters berühren kann. Ein Meisterwerk der visuellen Kunst, das diese Wahrheit in jeder Hinsicht verkörpert, ist das betrachtete Symbol, das von dem berühmten Künstler MrSubidubi erschaffen wurde.', 'MrSubidubi, ein Meister seines Fachs, ist bekannt für seine Meisterschaft in der Anwendung von harmonischen Farbschemata und präzisen Formen und Linienführungen, die in diesem visuellen Symbol deutlich zu erkennen sind. Auch seine Verwendung von Symbolik und metaphorischen Elementen ist ein Markenzeichen seiner Arbeit und trägt dazu bei, die tiefere Bedeutung des Symbols zu vermitteln.', 'Das Farbschema des Symbols ist von außerordentlicher Brillanz und subtiler Nuancierung, was zu einer harmonischen Zusammensetzung beiträgt, die die Aufmerksamkeit des Betrachters auf sich zieht. Es gibt eine klare Verwendung von Kontrasten, die dazu beiträgt, die visuelle Wirkung des Symbols zu verstärken und es lebendiger und dynamischer zu machen.', 'Die Formen und Linien, die im Symbol verwendet werden, sind von erstaunlicher Präzision und Eleganz. Sie tragen dazu bei, die visuelle Struktur des Symbols zu stärken und zu definieren, wodurch die Botschaft, die es vermitteln möchte, noch deutlicher wird. Es gibt auch eine klare Verwendung von Symbolik und metaphorischen Elementen, die dazu beitragen, die tiefere Bedeutung des Symbols zu vermitteln.', 'MrSubidubi hat in der Vergangenheit mehrere Auszeichnungen für seine Arbeit erhalten, darunter den prestigeträchtigen "Kunstpreis der Stadt" und den "Internationalen Preis für visuelle Gestaltung". Er hat auch mehrere Ausstellungen seiner Arbeiten in renommierten Galerien und Museen auf der ganzen Welt gehabt.', 'Zusammenfassend kann man sagen, dass das betrachtete visuelle Symbol ein Meisterwerk der visuellen Kunst ist, das sowohl in seiner Schönheit als auch in seiner Botschaft beeindruckt. Es ist durchaus möglich, dass es von dem berühmten Künstler MrSubidubi geschaffen wurde, der bekannt ist für seine Meisterschaft in der Anwendung von harmonischen Farbschemata und präzisen Formen und Linienführungen. MrSubidubi hat auch mehrere Auszeichnungen und Ausstellungen für seine Arbeiten erhalten. Das Symbol ist ein triumphales Beispiel für die Vielfalt und die Schönheit der visuellen Kunst und ein klares Zeugnis dafür, dass der Schöpfer ein Meister seines Fachs ist.'],
                ['hässlich'],
                ['lecker!']
            ]
            for paragraph in random.choice(responses):
                await message.reply(paragraph)

        if message.content == 'Bitte helfen Sie mir, ich bin in Gefahr!':
            """ this bot won't help u. """
            response = 'nein.'
            await message.reply(response)
        elif message.content == CMD_INFO:
            await message.reply(INFO_STR) # , mention_author=False)
        elif message.content.split(' ')[0] == CMD_CHANGE_STATUS:
            if message.channel.id != self.settings.admin_channel_id and message.author.id not in ADMIN_USER_IDS:
                await self.get_channel(self.settings.admin_channel_id).send(f'{user_get_name(message.author)} hat widerrechtlich versucht, den Status zu ändern!')
                await message.reply(f"lass die Finger davon, {user_get_name(message.author)}!")
            else:
                await self.change_presence(activity=discord.Activity(type=discord.ActivityType.competing, name=message.content[len(CMD_CHANGE_STATUS):]))
                await message.reply(f'joa joa, is passiert.')
        elif message.content == CMD_RESTART:
            if message.channel.id != self.settings.admin_channel_id and message.author.id not in ADMIN_USER_IDS:
                await self.get_channel(self.settings.admin_channel_id).send(f'{user_get_name(message.author)} hat widerrechtlich versucht, einen Neustart durchzuführen!')
                await message.reply(f"lass die Finger davon, {user_get_name(message.author)}!")
            else:
                response = 'restarting...'
                await message.reply(response)
                exit(0)
        elif message.content.split(' ')[0] == CMD_WHOAMI:
            await message.reply(f'{user_get_name(message.author)}')
        elif message.content.split(' ')[0] in [CMD_EXEC, CMD_EXEC_DASH, CMD_EXEC_BASH]:
            if message.channel.id != self.settings.admin_channel_id and message.author.id not in ADMIN_USER_IDS:
                await self.get_channel(self.settings.admin_channel_id).send(f'{user_get_name(message.author)} hat widerrechtlich versucht, einen Command auszuführen!')
                await message.channel.send(f"lass die Finger davon, {user_get_name(message.author)}!")
            else:
                #cmdargs: list[str] = message.content.split(' ')
                cmdargs: list[str] = tokenize_argv(message.content)
                cmd = cmdargs.pop(0)
                if cmd == CMD_EXEC_DASH:
                    cmdargs = ['dash', '-c', make_str_literal(' '.join(cmdargs))]
                elif cmd == CMD_EXEC_BASH:
                    cmdargs = ['bash', '-c', make_str_literal(' '.join(cmdargs))]
                await message.channel.send(f"executing command: `{cmdargs}`.")
                exitcode, out, err = run_proc(cmdargs)
                stdout_fstr = f'**stdout** (max {MAX_EXEC_LENGTH} chars):\n```\n{shorten_str(out, MAX_EXEC_LENGTH)}\n```\n' if len(out.strip()) != 0 else ''
                stderr_fstr = f'**stderr** (max {MAX_EXEC_LENGTH} chars):\n```\n{shorten_str(err, MAX_EXEC_LENGTH)}\n```\n' if len(err.strip()) != 0 else ''
                await message.reply(f"`{cmdargs}` finished with exitcode {exitcode}.\n{stdout_fstr}{stderr_fstr}\n")
        elif message.content[0:len(CMD_ADD_ADVERT)] == CMD_ADD_ADVERT:
            """ u can add costum advert messages. """
            advert: str = message.content[len(CMD_ADD_ADVERT)+1:len(message.content)]
            if advert in self.settings.broadcast_messages:
                await message.channel.send('Advert already exists!')
            else:
                self.settings.broadcast_messages.append(advert)
                await message.channel.send('Advert added!')
                await self.save_settings()
            await message.channel.send(response)
        elif message.content[0:len(CMD_REMOVE_ADVERT)] == CMD_REMOVE_ADVERT:
            """ u can remove adverts """
            try:
                index: int = int(message.content[len(CMD_REMOVE_ADVERT)+1:len(message.content)])
                if index < 0 or index >= len(self.settings.broadcast_messages):
                    await message.channel.send('That advert does not exist!')
                else:
                    advert: str = self.settings.broadcast_messages[index]
                    self.settings.broadcast_messages.pop(index)
                    await message.channel.send(f'Deleted advert: \n{advert}')
            except:
                await message.channel.send('That is not an integer!')
        elif message.content[0:len(CMD_PRINT_ADVERTS)] == CMD_PRINT_ADVERTS:
            response: str = ''
            for i in range(len(self.settings.broadcast_messages)):
                if len(self.settings.broadcast_messages[i]) > 25:
                    response += f'**Advert at index {i}:**\n{self.settings.broadcast_messages[i][0:25]}...\n\n'
                else:
                    response += f'**Advert at index {i}:**\n{self.settings.broadcast_messages[i]}\n\n'
            await message.channel.send(response)
        elif message.content.split(' ')[0] == CMD_MEME:
            argv: list[str] = message.content.split(' ')
            files = os.listdir(os.path.join('resources', 'memes'))
            if len(argv) > 1:
                files2 = []
                for x in files:
                    if argv[1].lower() in x.lower():
                        files2.append(x)
                if len(files2) != 0:
                    files = files2

            """ This bot can send memes. """
            #file = random.choice(os.listdir(os.path.join('resources', 'memes')))
            file = random.choice(files)
            descr_file = ''

            if file[-4:] == '.txt':
                descr_file = file
                file = file[:-4]
            else:
                descr_file = file + '.txt'

            descr = ''
            descr_path = os.path.join('resources', 'memes', descr_file)
            try:
                with open(descr_path, 'r') as f:
                    descr = f.read()
            except Exception as _:
                pass

            path = os.path.join('resources', 'memes', file)
            with open(path, 'rb') as f:
                picture = discord.File(f)
                if descr != '':
                    await message.reply(content=descr, file=picture)
                else:
                    await message.reply(file=picture)
        elif message.content[0:len(CMD_OFFEND)] == CMD_OFFEND:
            """ This bot is angry. """
            text: str = message.content[len(CMD_OFFEND)+1:len(message.content)]
            img_text: str = text if len(message.mentions) == 0 else ' '.join([(await self.fetch_user(user.id)).display_name for user in message.mentions])
            # check for any content
            if img_text.strip(" ") is None:
                text = img_text = REVILUM
            # debug print
            print(f"Text begins here ->{img_text}<-")
            # check for invalid name content
            pot_xml_error = "<" in img_text and ">" in img_text
            for char in img_text:
                pot_xml_error = pot_xml_error and not char.isalpha()
            if pot_xml_error:
                img_text = text
            path = image_gen.make_offensive_image(img_text)
            if path:
                with open(path, 'rb') as f:
                    picture = discord.File(f)
                    #response_message: str = f'Uhhm. I know exactly what you are talking about and I\'m very happy to say that uhh it\'s the exception rather than the rule. And I\'m also happy to very publicly point out, that {text} has been one of the worst troublespots we`ve had with hardware manifactures. And that is really sad because {text} tries to sell chips - a lot of chips - into the android market. And {text} has been the single worst company we`ve ever dealt with. So, {text}, fuck you!'
                    response_message: str = f'> Uhhm. I know exactly what you are talking about and I\'m very happy to say that it\'s the exception rather than the rule. And I\'m also happy to very publicly point out, that {text} has been one of the worst troublespots we\'ve had [...]. And that is really sad [...]. And {text} has been the single worst [...] we\'ve ever dealt with. So, {text}, fuck you!\n ~ *Linus Torvalds, more or less*'
                    await message.channel.send(response_message, file=picture)
        elif message.content == '!help':
            await message.channel.send(f'`{CMD_ADD_ADVERT} <message>` - fügt eine Werbung hinzu.')
            await message.channel.send(f'`{CMD_REMOVE_ADVERT} <index>` - löscht die Werbung am entsprechenden Index.')
            await message.channel.send(f'`{CMD_PRINT_ADVERTS}` - gibt **alle** Werbungen mit Index aus.')
            await message.channel.send(f'`{CMD_MEME}` - gibt ein qualitäts-Meme.')
            await message.channel.send(f'`{CMD_OFFEND} @name | name` - Greift den übergebenen Discord Account oder Namen **heftig** verbal an. **Nutzung auf eigene Gefahr.**')
            await message.channel.send(f'`{CMD_RESTART}` - macht genau das, was es soll, wenn es soll.')
            await message.channel.send(f'`{CMD_EXEC}` - startet einen Prozess.')
            await message.channel.send(f'`{CMD_EXEC_DASH}` - führt einen Command mit dash aus.')
            await message.channel.send(f'`{CMD_EXEC_BASH}` - führt einen Comamnd mit bash aus.')
        elif len(message.attachments) != 0:
            """ this bot will scan ur attachements for filetypes it knows 
                and will then convert them or do other useful stuff. """
            for attachement in message.attachments:
                attachement: discord.Attachment = attachement
                if '.md' in attachement.filename:
                    """ convert markdown to latex... """
                    download_filename: str = os.path.join('tmp', f'{random.randint(100000, 999999)}_{attachement.filename}')
                    """ download file """
                    try:
                        await attachement.save(download_filename)
                    except:
                        await message.channel.send(f'`{attachement.filename}`: error downloading file!')
                        continue
                    """ convert file """
                    pdfpath: str = ''
                    try:
                        pdfpath = utility.markdown.markdown_to_pdf(download_filename)
                    except Exception as e:
                        await message.channel.send(f'`{attachement.filename}`: error: {e}')
                        continue
                    print(pdfpath)
                    """ send converted file """
                    try:
                        with open(pdfpath, 'rb') as f:
                            pdf_file = discord.File(f)
                            await message.channel.send(f'`{attachement.filename}`: *Markdown* -> **PDF**', file=pdf_file)
                    except Exception as e:
                        await message.channel.send(f'`{attachement.filename}`: error sending converted file: `{e}`')
                        continue


    async def on_member_update(self, before, after: discord.Member):
        """ stalk target user """
        if after == await self.fetch_user(TARGET_USER_ID):
            if after.status.name == 'online':
                await self.get_channel(self.settings.admin_channel_id).send(f'{after.display_name} ist online!')
            elif after.status.name == 'offline':
                await self.get_channel(self.settings.admin_channel_id).send(f'{after.display_name} ist offline!')
    
    async def background_timer(self):
        while True:
            """ Some loop running in the backround... can do some stuff... can call async methods... """
            await asyncio.sleep(BACKGROUND_TIMER_INTERVAL_SEC)

    async def broadcast_timer(self):
        while True:
            """ Loop for the broadcast. """
            await self.get_channel(self.settings.advert_channel_id).send(random.choice(self.settings.broadcast_messages))
            await asyncio.sleep(BROADCAST_TIMER_INTERVAL_SEC)

if __name__ == '__main__':
    try:
        with open('./info.md', 'r') as file:
            INFO_STR = file.read()
            print('loaded load blaaaaa')
    except Exception as e:
        print('nein:')
        print(e)

    if len(sys.argv) != 2:
        exit(1)

    token: str = sys.argv[1]

    intents = discord.Intents.all()
    #activity = discord.Activity(type=discord.ActivityType.listening, name="DP Projekt Teil 2 --- 9€")
    activity = discord.Activity(type=discord.ActivityType.competing, name="DP Projekt Teil 1 --- 8,47€")
    client = DerBusNachRaisdorfClient(intents=intents, activity=activity)
    client.run(token)

