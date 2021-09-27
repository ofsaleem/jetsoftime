from enum import IntEnum, auto


class StrIntEnum(IntEnum):

    def __str__(self):
        x = self.__repr__().split('.')[1].split(':')[0].lower().title()
        x = x.replace('_', ' ')
        return x

    @classmethod
    def str_dict(cls) -> dict:
        return dict((x, str(x)) for x in list(cls))

    @classmethod
    def inv_str_dict(cls) -> dict:
        return dict((str(x), x) for x in list(cls))


class BossID(StrIntEnum):
    ATROPOS_XR = auto()
    DALTON_PLUS = auto()
    ELDER_SPAWN = auto()
    FLEA = auto()
    FLEA_PLUS = auto()
    GIGA_MUTANT = auto()
    GOLEM = auto()
    GOLEM_BOSS = auto()
    HECKRAN = auto()
    LAVOS_SPAWN = auto()
    MASA_MUNE = auto()
    MEGA_MUTANT = auto()
    NIZBEL = auto()
    NIZBEL_2 = auto()
    RETINITE = auto()
    RUST_TYRANO = auto()
    SLASH_SWORD = auto()
    SUPER_SLASH = auto()
    SON_OF_SUN = auto()
    TERRA_MUTANT = auto()
    TWIN_GOLEM = auto()
    YAKRA = auto()
    YAKRA_XIII = auto()
    ZOMBOR = auto()

    @classmethod
    def get_extra_bosses(cls):
        return (
            cls.ATROPOS_XR,
            cls.DALTON_PLUS,
            cls.GOLEM_BOSS
        )

    @classmethod
    def get_one_part_bosses(cls):
        return [
            cls.ATROPOS_XR,
            cls.DALTON_PLUS,
            cls.FLEA,
            cls.FLEA_PLUS,
            cls.GOLEM,
            cls.GOLEM_BOSS,
            cls.HECKRAN,
            cls.MASA_MUNE,
            cls.NIZBEL,
            cls.NIZBEL_2,
            cls.RUST_TYRANO,
            cls.SLASH_SWORD,
            cls.SUPER_SLASH,
            cls.YAKRA,
            cls.YAKRA_XIII
        ]

    @classmethod
    def get_two_part_bosses(cls):
        return [
            cls.ELDER_SPAWN,
            cls.GIGA_MUTANT, cls.LAVOS_SPAWN, cls.MEGA_MUTANT,
            cls.TERRA_MUTANT, cls.ZOMBOR, cls.TWIN_GOLEM
        ]

    @classmethod
    def get_multi_part_bosses(cls):
        return cls.SON_OF_SUN, cls.RETINITE


class LocID(StrIntEnum):
    BLACK_OMEN_ELDER_SPAWN = 0x60
    ZENAN_BRIDGE = 0x87
    CAVE_OF_MASAMUNE = 0x97
    SUNKEN_DESERT_DEVOURER = 0xA1
    MAGUS_CASTLE_SLASH = 0xA9
    MAGUS_CASTLE_FLEA = 0xAD
    OZZIES_FORT_FLEA_PLUS = 0xB7
    OZZIES_FORT_SUPER_SLASH = 0xB8
    HECKRAN_CAVE_NEW = 0xC0
    KINGS_TRIAL_NEW = 0xC1
    GIANTS_CLAW_TYRANO = 0xC5
    MANORIA_COMMAND = 0xC6
    SUN_PALACE = 0xFB
    REPTITE_LAIR_AZALA_ROOM = 0x121
    TYRANO_LAIR_NIZBEL = 0x130
    BLACK_OMEN_GIGA_MUTANT = 0x143
    BLACK_OMEN_TERRA_MUTANT = 0x145
    ZEAL_PALACE_THRONE_NIGHT = 0x14E
    OCEAN_PALACE_TWIN_GOLEM = 0x19E
    DEATH_PEAK_GUARDIAN_SPAWN = 0x1EF

    @classmethod
    def get_boss_locations(cls):
        return [
            cls.BLACK_OMEN_ELDER_SPAWN,
            cls.ZENAN_BRIDGE,
            cls.CAVE_OF_MASAMUNE,
            cls.SUNKEN_DESERT_DEVOURER,
            cls.MAGUS_CASTLE_SLASH,
            cls.MAGUS_CASTLE_FLEA,
            cls.OZZIES_FORT_FLEA_PLUS,
            cls.OZZIES_FORT_SUPER_SLASH,
            cls.HECKRAN_CAVE_NEW,
            cls.KINGS_TRIAL_NEW,
            cls.GIANTS_CLAW_TYRANO,
            cls.MANORIA_COMMAND,
            cls.SUN_PALACE,
            cls.REPTITE_LAIR_AZALA_ROOM,
            cls.TYRANO_LAIR_NIZBEL,
            cls.BLACK_OMEN_GIGA_MUTANT,
            cls.BLACK_OMEN_TERRA_MUTANT,
            cls.ZEAL_PALACE_THRONE_NIGHT,
            cls.OCEAN_PALACE_TWIN_GOLEM,
            cls.DEATH_PEAK_GUARDIAN_SPAWN
        ]


boss_loc_dict = {
    LocID.BLACK_OMEN_ELDER_SPAWN: BossID.ELDER_SPAWN,
    LocID.ZENAN_BRIDGE: BossID.ZOMBOR,
    LocID.CAVE_OF_MASAMUNE: BossID.MASA_MUNE,
    LocID.SUNKEN_DESERT_DEVOURER: BossID.RETINITE,
    LocID.MAGUS_CASTLE_SLASH: BossID.SLASH_SWORD,
    LocID.MAGUS_CASTLE_FLEA: BossID.FLEA,
    LocID.OZZIES_FORT_FLEA_PLUS: BossID.FLEA_PLUS,
    LocID.OZZIES_FORT_SUPER_SLASH: BossID.SUPER_SLASH,
    LocID.HECKRAN_CAVE_NEW: BossID.HECKRAN,
    LocID.KINGS_TRIAL_NEW: BossID.YAKRA_XIII,
    LocID.GIANTS_CLAW_TYRANO: BossID.RUST_TYRANO,
    LocID.MANORIA_COMMAND: BossID.YAKRA,
    LocID.SUN_PALACE: BossID.SON_OF_SUN,
    LocID.REPTITE_LAIR_AZALA_ROOM: BossID.NIZBEL,
    LocID.TYRANO_LAIR_NIZBEL: BossID.NIZBEL_2,
    LocID.BLACK_OMEN_GIGA_MUTANT: BossID.GIGA_MUTANT,
    LocID.BLACK_OMEN_TERRA_MUTANT: BossID.TERRA_MUTANT,
    LocID.ZEAL_PALACE_THRONE_NIGHT: BossID.GOLEM,
    LocID.OCEAN_PALACE_TWIN_GOLEM: BossID.TWIN_GOLEM,
    LocID.DEATH_PEAK_GUARDIAN_SPAWN: BossID.LAVOS_SPAWN
}


class ItemID(IntEnum):
    WOOD_SWORD = 0x01
    IRON_BLADE = 0x02
    STEELSABER = 0x03
    LODE_SWORD = 0x04
    RED_KATANA = 0x05
    FLINT_EDGE = 0x06
    DARK_SABER = 0x07
    AEON_BLADE = 0x08
    DEMON_EDGE = 0x09
    ALLOYBLADE = 0x0A
    STAR_SWORD = 0x0B
    VEDICBLADE = 0x0C
    KALI_BLADE = 0x0D
    SHIVA_EDGE = 0x0E
    BOLT_SWORD = 0x0F
    SLASHER = 0x10
    BRONZE_BOW = 0x11
    IRON_BOW = 0x12
    LODE_BOW = 0x13
    ROBIN_BOW = 0x14
    SAGE_BOW = 0x15
    DREAM_BOW = 0x16
    COMETARROW = 0x17
    SONICARROW = 0x18
    VALKERYE = 0x19
    SIREN = 0x1A
    AIR_GUN = 0x1F
    DART_GUN = 0x20
    AUTO_GUN = 0x21
    PICOMAGNUM = 0x22
    PLASMA_GUN = 0x23
    RUBY_GUN = 0x24
    DREAM_GUN = 0x25
    MEGABLAST = 0x26
    SHOCK_WAVE = 0x27
    WONDERSHOT = 0x28
    GRAEDUS = 0x29
    TIN_ARM = 0x2E
    HAMMER_ARM = 0x2F
    MIRAGEHAND = 0x30
    STONE_ARM = 0x31
    DOOMFINGER = 0x32
    MAGMA_HAND = 0x33
    MEGATONARM = 0x34
    BIG_HAND = 0x35
    KAISER_ARM = 0x36
    GIGA_ARM = 0x37
    TERRA_ARM = 0x38
    CRISIS_ARM = 0x39
    BRONZEEDGE = 0x3B
    IRON_SWORD = 0x3C
    MASAMUNE_1 = 0x3D
    FLASHBLADE = 0x3E
    PEARL_EDGE = 0x3F
    RUNE_BLADE = 0x40
    BRAVESWORD = 0x41
    MASAMUNE_2 = 0x42
    DEMON_HIT = 0x43
    FIST = 0x44
    FIST_2 = 0x45
    FIST_3 = 0x46
    IRON_FIST = 0x47
    BRONZEFIST = 0x48
    DARKSCYTHE = 0x4B
    HURRICANE = 0x4C
    STARSCYTHE = 0x4D
    DOOMSICKLE = 0x4E
    MOP = 0x4F
    BENT_SWORD = 0x50
    BENT_HILT = 0x51
    MASAMUNE_0_ATK = 0x52
    SWALLOW = 0x53
    SLASHER_2 = 0x54
    RAINBOW = 0x55
    HIDE_TUNIC = 0x5B
    KARATE_GI = 0x5C
    BRONZEMAIL = 0x5D
    MAIDENSUIT = 0x5E
    IRON_SUIT = 0x5F
    TITAN_VEST = 0x60
    GOLD_SUIT = 0x61
    RUBY_VEST = 0x62
    DARK_MAIL = 0x63
    MIST_ROBE = 0x64
    MESO_MAIL = 0x65
    LUMIN_ROBE = 0x66
    FLASH_MAIL = 0x67
    LODE_VEST = 0x68
    AEON_SUIT = 0x69
    ZODIACCAPE = 0x6A
    NOVA_ARMOR = 0x6B
    PRISMDRESS = 0x6C
    MOON_ARMOR = 0x6D
    RUBY_ARMOR = 0x6E
    RAVENARMOR = 0x6F
    GLOOM_CAPE = 0x70
    WHITE_MAIL = 0x71
    BLACK_MAIL = 0x72
    BLUE_MAIL = 0x73
    RED_MAIL = 0x74
    WHITE_VEST = 0x75
    BLACK_VEST = 0x76
    BLUE_VEST = 0x77
    RED_VEST = 0x78
    TABAN_VEST = 0x79
    TABAM_SUIT = 0x7A
    HIDE_CAP = 0x7C
    BRONZEHELM = 0x7D
    IRON_HELM = 0x7E
    BERET = 0x7F
    GOLD_HELM = 0x80
    ROCK_HELM = 0x81
    CERATOPPER = 0x82
    GLOW_HELM = 0x83
    LODE_HELM = 0x84
    AEON_HELM = 0x85
    PRISM_HELM = 0x86
    DOOM_HELM = 0x87
    DARK_HELM = 0x88
    GLOOM_HELM = 0x89
    SAFE_HELM = 0x8A
    TABAN_HELM = 0x8B
    SIGHT_CAP = 0x8C
    MEMORY_CAP = 0x8D
    TIME_HAT = 0x8E
    VIGIL_HAT = 0x8F
    OZZIEPANTS = 0x90
    HASTE_HELM = 0x91
    RBOW_HELM = 0x92
    MERMAIDCAP = 0x93
    BANDANA = 0x95
    RIBBON = 0x96
    POWERGLOVE = 0x97
    DEFENDER = 0x98
    MAGICSCARF = 0x99
    AMULET = 0x9A
    DASH_RING = 0x9B
    HIT_RING = 0x9C
    POWER_RING = 0x9D
    MAGIC_RING = 0x9E
    WALL_RING = 0x9F
    SILVERERNG = 0xA0
    GOLD_ERNG = 0xA1
    SILVERSTUD = 0xA2
    GOLD_STUD = 0xA3
    SIGHTSCOPE = 0xA4
    CHARM_TOP = 0xA5
    RAGE_BAND = 0xA6
    FRENZYBAND = 0xA7
    THIRD_EYE = 0xA8
    WALLET = 0xA9
    GREENDREAM = 0xAA
    BERSERKER = 0xAB
    POWERSCARF = 0xAC
    SPEED_BELT = 0xAD
    BLACK_ROCK = 0xAE
    BLUE_ROCK = 0xAF
    SILVERROCK = 0xB0
    WHITE_ROCK = 0xB1
    GOLD_ROCK = 0xB2
    HERO_MEDAL = 0xB3
    MUSCLERING = 0xB4
    FLEA_VEST = 0xB5
    MAGIC_SEAL = 0xB6
    POWER_SEAL = 0xB7
    RELIC = 0xB8
    SERAPHSONG = 0xB9
    SUN_SHADES = 0xBA
    PRISMSPECS = 0xBB
    TONIC = 0xBD
    MID_TONIC = 0xBE
    FULL_TONIC = 0xBF
    ETHER = 0xC0
    MID_ETHER = 0xC1
    FULL_ETHER = 0xC2
    ELIXER = 0xC3
    HYPERETHER = 0xC4
    MEGAELIXER = 0xC5
    HEAL = 0xC6
    REVIVE = 0xC7
    SHELTER = 0xC8
    POWER_MEAL = 0xC9
    LAPIS = 0xCA
    BARRIER = 0xCB
    SHIELD = 0xCC
    POWER_TAB = 0xCD
    MAGIC_TAB = 0xCE
    SPEED_TAB = 0xCF
    PETAL = 0xD0
    FANG = 0xD1
    HORN = 0xD2
    FEATHER = 0xD3
    SEED = 0xD4
    BIKE_KEY = 0xD5
    PENDANT = 0xD6
    GATE_KEY = 0xD7
    PRISMSHARD = 0xD8
    C_TRIGGER = 0xD9
    TOOLS = 0xDA
    JERKY = 0xDB
    DREAMSTONE = 0xDC
    RACE_LOG = 0xDD
    MOON_STONE = 0xDE
    SUN_STONE = 0xDF
    RUBY_KNIFE = 0xE0
    YAKRA_KEY = 0xE1
    CLONE = 0xE2
    TOMAS_POP = 0xE3
    PETALS_2 = 0xE4
    FANGS_2 = 0xE5
    HORNS_2 = 0xE6
    FEATHERS_2 = 0xE7
