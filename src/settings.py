from collections import namedtuple
import discord

RaisdorfUser = namedtuple("Raisdorfuser", "id name role isadmin")

__USER_DATA: list[RaisdorfUser] = [
    RaisdorfUser(224037892387766272, 'Nils', 'Gebannt', False),
    RaisdorfUser(397130478907293707, 'Muha', 'Raisdorfbusenjoyer & ÖPNV-Connaisseur', False),
    RaisdorfUser(373093304767873044, 'Finn', 'Q', True),
    RaisdorfUser(696336485846220803, 'Emely', None, False),
    RaisdorfUser(330701572118151169, 'Merlin', 'Q', True),
    RaisdorfUser(1041448820258635906, 'Merlin2', 'test', True)
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

    def to_dict(self) -> dict:
        return {
            'admin_channel_id': self.admin_channel_id,
            'advert_channel_id': self.advert_channel_id,
            'broadcast_messages': self.broadcast_messages,
            'pizza': self.pizza
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
