from collections import namedtuple
import discord

RaisdorfUser = namedtuple("Raisdorfuser", "id name role isadmin mail send_mail_on_kick")

__USER_DATA: list[RaisdorfUser] = [
    RaisdorfUser(224037892387766272, 'Nils', 'Gebannt',                               False, 'stu235273@mail.uni-kiel.de', True),
    RaisdorfUser(397130478907293707, 'Muha', 'Raisdorfbusenjoyer & ÖPNV-Connaisseur', False, 'stu235892@mail.uni-kiel.de', True),
    RaisdorfUser(373093304767873044, 'Finn', 'Q',                                     True,  'stu236925@mail.uni-kiel.de', True),
    RaisdorfUser(696336485846220803, 'Emely', None,                                   False, 'stu240369@mail.uni-kiel.de', True),
    RaisdorfUser(330701572118151169, 'Merlin', 'Q',                                   True,  'stu235271@mail.uni-kiel.de', True),
    RaisdorfUser(1041448820258635906, 'Merlin2', 'Q',                                 True,  'merliin3007@gmail.com', True)
]
__USER_DATA_NAMEKEY: dict[str, RaisdorfUser] = { user.name : user for user in __USER_DATA }
__USER_DATA_IDKEY: dict[int, RaisdorfUser] = { user.id : user for user in __USER_DATA }


def get_raisdorfuser_by_name(name: str, default=None) -> RaisdorfUser:
    """ finds a user by their name """
    return __USER_DATA_NAMEKEY.get(name, default)


def get_raisdorfuser_by_id(user_id: int, default=None) -> RaisdorfUser:
    """ finds a user by their discord user-id """
    return __USER_DATA_IDKEY.get(user_id, default)


def get_raisdorfuser(discord_user: discord.Member, default=None) -> RaisdorfUser:
    """ finds a user by their discord member object """
    return get_raisdorfuser_by_id(discord_user.id, default)


def member_is_admin(discord_user: discord.Member) -> bool:
    """ finds wheter user is an admin or not """
    user = get_raisdorfuser(discord_user)
    return user.isadmin if user else False


# ids to name (obsolete - use get_raisdorfuser_by_id(id).name instead)
USER_ALIASES = {user.id : user.name for user in __USER_DATA}

# name to id (obsolete - use get_raisdorfuser_by_name(name).id instead)
USER_IDS = {user.name : user.id for user in __USER_DATA}

# will become obsolete soo
ADMIN_USER_IDS: list[int] = [330701572118151169, 373093304767873044]

# TODO MERLIN MACH DAS WEG!!! jaja... bald
REVILUM_ID = USER_IDS["Nils"]

class Settings:
    def __init__(self):
        self.admin_channel_id: int = 985262849775525998
        self.advert_channel_id: int = 985262936291430470
        self.broadcast_messages: list[str] = [
            'Es gibt eine Menge gute IDEs!\nDiese sind super leicht zu installieren und zu nutzen!\nHier ist eine: '
            '\nhttps://code.visualstudio.com/',
            'Es gibt eine Menge gute IDEs!\nDiese sind super leicht zu installieren und zu nutzen!\nHier ist eine: '
            '\nhttps://www.jetbrains.com/de-de/idea/',
            'Es gibt eine Menge gute IDEs!\nDiese sind super leicht zu installieren und zu nutzen!\nHier ist eine: '
            '\nhttps://www.eclipse.org/downloads/',
            'Erstellen Sie sich jetzt einen GitHub account!\nhttps://github.com/signup',
            'Git ist super! Installieren Sie Git jetzt!\nhttps://git-scm.com/',
            'Es gibt viele IDEs, die speziell für Java geeignet sind. Einen Überblick finden Sie hier:\n '
            'https://www.programmierenlernenhq.de/java-programmieren-lernen-die-besten-java-entwicklungsumgebungen/',
            'Der Windows Editor war gestern!\nInstallieren Sie jetzt eine komfortable IDE Ihrer Wahl!',
            'Veränderen Sie die Welt!\nhttps://chng.it/zYD5T2Fc'
        ]
        self.kunst_channel_ids: list[int] = [1051567423083532358, 1067251515066159224, 1052004758451392662]
        self.pizza = []

        self.email_sender: str = 'example@example.com'
        self.email_password: str = 'password'
        self.email_smtp_host: str = 'smtp.example.com'

        # { id : (errors, words) }
        self.fehlerqouten: dict[int, list[int, int]] = {}

    def to_dict(self) -> dict:
        return {
            'admin_channel_id': self.admin_channel_id,
            'advert_channel_id': self.advert_channel_id,
            'broadcast_messages': self.broadcast_messages,
            'pizza': self.pizza,

            'email_sender': self.email_sender,
            'email_password': self.email_password,
            'email_smtp_host': self.email_smtp_host
        }

    def from_dict(self, d: dict):
        if 'admin_channel_id' in d:
            self.admin_channel_id = d['admin_channel_id']
        if 'advert_channel_id' in d:
            self.advert_channel_id = d['advert_channel_id']
        if 'broadcast_messages' in d:
            self.broadcast_messages = d['broadcast_messages']
        if 'pizza' in d:
            self.pizza = d['pizza']
        if 'email_sender' in d:
            self.email_sender = d['email_sender']
        if 'email_password' in d:
            self.email_password = d['email_password']
        if 'email_smtp_host' in d:
            self.email_smtp_host = d['email_smtp_host']
