ADMIN_USER_IDS: list[int] = [330701572118151169, 373093304767873044]

USER_DATA = [
    (224037892387766272, 'Nils'),
    (397130478907293707, 'Muha'),
    (373093304767873044, 'Finn'),
    (696336485846220803, 'Emely'),
    (330701572118151169, 'Merlin')
]

# ids to name
USER_ALIASES = {user_tuple[0]: user_tuple[1] for user_tuple in USER_DATA}


# name to id
USER_IDS = {user_tuple[1]: user_tuple[0] for user_tuple in USER_DATA}
# TODO MERLIN MACH DAS WEG!!!
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
        self.kunst_channel_ids: [int] = [1051567423083532358, 1067251515066159224, 1052004758451392662]
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
