from enum import Enum, IntEnum, auto


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


class CharID(StrIntEnum):
    CRONO = 0
    MARLE = 1
    LUCCA = 2
    ROBO = 3
    FROG = 4
    AYLA = 5
    MAGUS = 6


class LocID(StrIntEnum):
    # Boss Locations
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
    SUN_PALACE = 0xFB  # Also key item
    REPTITE_LAIR_AZALA_ROOM = 0x121  # Also key item
    TYRANO_LAIR_NIZBEL = 0x130
    BLACK_OMEN_GIGA_MUTANT = 0x143
    BLACK_OMEN_TERRA_MUTANT = 0x145
    ZEAL_PALACE_THRONE_NIGHT = 0x14E
    OCEAN_PALACE_TWIN_GOLEM = 0x19E
    DEATH_PEAK_GUARDIAN_SPAWN = 0x1EF

    # Character Recruitment Locations
    MANORIA_SANCTUARY = 0x81
    GUARDIA_QUEENS_CHAMBER_600 = 0x7A
    PROTO_DOME = 0xE2
    DACTYL_NEST_SUMMIT = 0x127
    FROGS_BURROW = 0x8D

    # Additional Key Item Locations
    MT_WOE_SUMMIT = 0x18D
    FIONAS_SHRINE = 0x39
    ARRIS_DOME = 0xD6
    GENO_DOME_MAINFRAME = 0x10C
    GUARDIA_REAR_STORAGE = 0x1B8
    GUARDIA_THRONEROOM_600 = 0x78
    SNAIL_STOP = 0x35
    CHORAS_CARPENTER_1000 = 0x3D
    LUCCAS_WORKSHOP = 0x04
    
    # Additional Sealed Chest Locations
    NORTHERN_RUINS_ANTECHAMBER = 0x42
    NORTHERN_RUINS_BACK_ROOM = 0x46
    TRUCE_INN_1000 = 0x0C
    TRUCE_INN_600_2F = 0x75
    FOREST_RUINS = 0x2A
    PORRE_ELDER = 0x9A
    PORRE_MAYOR_2F = 33
    GUARDIA_CASTLE_KINGS_TOWER_600 = 0x1E0
    GUARDIA_CASTLE_KINGS_TOWER_1000 = 0x1E6
    GUARDIA_FOREST_600 = 0x77
    GUARDIA_FOREST_DEAD_END = 0x14
    # This map gets split, but the sealed chest is on the original map
    HECKRAN_CAVE_PASSAGEWAYS = 0x2F
    MAGIC_CAVE_INTERIOR = 0xA4

    # Additional Script Chest Locations
    NORTHERN_RUINS_BASEMENT = 0x42

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


# Copied and reformatted from Anguirel's list
class ItemID(StrIntEnum):
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
    TABAN_SUIT = 0x7A
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
    ELIXIR = 0xC3
    HYPERETHER = 0xC4
    MEGAELIXIR = 0xC5
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


# Extracted from Anguirel's Chronosanity code
# Non-Chronosanity chests checked vs frankin's (?) spreadsheet at
# https://docs.google.com/spreadsheets/
#   d/19-CgUeYJrHJ8A1jJJWN1gvGaiFyvM5_aoE15POjW8YQ/edit#gid=1968430651
class TreasureID(StrIntEnum):
    MT_WOE_1ST_SCREEN = auto()
    MT_WOE_2ND_SCREEN_1 = auto()
    MT_WOE_2ND_SCREEN_2 = auto()
    MT_WOE_2ND_SCREEN_3 = auto()
    MT_WOE_2ND_SCREEN_4 = auto()
    MT_WOE_2ND_SCREEN_5 = auto()
    MT_WOE_3RD_SCREEN_1 = auto()
    MT_WOE_3RD_SCREEN_2 = auto()
    MT_WOE_3RD_SCREEN_3 = auto()
    MT_WOE_3RD_SCREEN_4 = auto()
    MT_WOE_3RD_SCREEN_5 = auto()
    MT_WOE_FINAL_1 = auto()
    MT_WOE_FINAL_2 = auto()
    MT_WOE_KEY = auto()
    FIONA_KEY = auto()
    ARRIS_DOME_RATS = auto()
    ARRIS_DOME_FOOD_STORE = auto()
    ARRIS_DOME_KEY = auto()
    SUN_PALACE_KEY = auto()
    SEWERS_1 = auto()
    SEWERS_2 = auto()
    SEWERS_3 = auto()
    LAB_16_1 = auto()
    LAB_16_2 = auto()
    LAB_16_3 = auto()
    LAB_16_4 = auto()
    LAB_32_1 = auto()
    PRISON_TOWER_1000 = auto()
    GENO_DOME_1F_1 = auto()
    GENO_DOME_1F_2 = auto()
    GENO_DOME_1F_3 = auto()
    GENO_DOME_1F_4 = auto()
    GENO_DOME_ROOM_1 = auto()
    GENO_DOME_ROOM_2 = auto()
    GENO_DOME_PROTO4_1 = auto()
    GENO_DOME_PROTO4_2 = auto()
    GENO_DOME_2F_1 = auto()
    GENO_DOME_2F_2 = auto()
    GENO_DOME_2F_3 = auto()
    GENO_DOME_2F_4 = auto()
    GENO_DOME_KEY = auto()
    FACTORY_LEFT_AUX_CONSOLE = auto()
    FACTORY_LEFT_SECURITY_RIGHT = auto()
    FACTORY_LEFT_SECURITY_LEFT = auto()
    FACTORY_RIGHT_DATA_CORE_1 = auto()
    FACTORY_RIGHT_DATA_CORE_2 = auto()
    FACTORY_RIGHT_FLOOR_TOP = auto()
    FACTORY_RIGHT_FLOOR_LEFT = auto()
    FACTORY_RIGHT_FLOOR_BOTTOM = auto()
    FACTORY_RIGHT_FLOOR_SECRET = auto()
    FACTORY_RIGHT_CRANE_LOWER = auto()
    FACTORY_RIGHT_CRANE_UPPER = auto()
    FACTORY_RIGHT_INFO_ARCHIVE = auto()
    # Inaccessible Robot storage chest omitted -- would be 0xE7
    GIANTS_CLAW_KINO_CELL = auto()
    GIANTS_CLAW_TRAPS = auto()
    GIANTS_CLAW_CAVES_1 = auto()
    GIANTS_CLAW_CAVES_2 = auto()
    GIANTS_CLAW_CAVES_3 = auto()
    GIANTS_CLAW_CAVES_4 = auto()
    GIANTS_CLAW_CAVES_5 = auto()
    GIANTS_CLAW_ROCK = auto()
    GIANTS_CLAW_KEY = auto()
    # Weirdness with Northern Ruins.  There's a variable set, only for these
    # locations indicating whether you're in the 600 or 1000 version
    #   0x7F10A3 & 0x10 ->  600
    #   0x7F10A3 & 0x20 -> 1000
    # On 0x44 Northern Ruins Antechamber
    NORTHERN_RUINS_ANTECHAMBER_LEFT_600 = auto()
    NORTHERN_RUINS_ANTECHAMBER_SEALED_600 = auto()
    NORTHERN_RUINS_ANTECHAMBER_LEFT_1000 = auto()
    NORTHERN_RUINS_ANTECHAMBER_SEALED_1000 = auto()
    # On 0x46 Northern Ruins Back Room
    NORTHERN_RUINS_BACK_LEFT_SEALED_600 = auto()
    NORTHERN_RUINS_BACK_RIGHT_SEALED_600 = auto()
    NORTHERN_RUINS_BACK_LEFT_SEALED_1000 = auto()
    NORTHERN_RUINS_BACK_RIGHT_1000 = auto()
    # On 0x42 Northern Ruins Basement Corridor
    NORTHERN_RUINS_BASEMENT_600 = auto()
    # Frog locked one
    NORTHERN_RUINS_BASEMENT_1000 = auto()
    GUARDIA_BASEMENT_1 = auto()
    GUARDIA_BASEMENT_2 = auto()
    GUARDIA_BASEMENT_3 = auto()
    GUARDIA_TREASURY_1 = auto()
    GUARDIA_TREASURY_2 = auto()
    GUARDIA_TREASURY_3 = auto()
    KINGS_TRIAL_KEY = auto()
    OZZIES_FORT_GUILLOTINES_1 = auto()
    OZZIES_FORT_GUILLOTINES_2 = auto()
    OZZIES_FORT_GUILLOTINES_3 = auto()
    OZZIES_FORT_GUILLOTINES_4 = auto()
    OZZIES_FORT_FINAL_1 = auto()
    OZZIES_FORT_FINAL_2 = auto()
    TRUCE_MAYOR_1F = auto()
    TRUCE_MAYOR_2F = auto()
    FOREST_RUINS = auto()
    PORRE_MAYOR_2F = auto()
    TRUCE_CANYON_1 = auto()
    TRUCE_CANYON_2 = auto()
    FIONAS_HOUSE_1 = auto()
    FIONAS_HOUSE_2 = auto()
    CURSED_WOODS_1 = auto()
    CURSED_WOODS_2 = auto()
    FROGS_BURROW_RIGHT = auto()
    ZENAN_BRIDGE_KEY = auto()
    SNAIL_STOP_KEY = auto()
    LAZY_CARPENTER = auto()
    HECKRAN_CAVE_SIDETRACK = auto()
    HECKRAN_CAVE_ENTRANCE = auto()
    HECKRAN_CAVE_1 = auto()
    HECKRAN_CAVE_2 = auto()
    # Taban items are weird, but the first one can be a normal ScriptTreasure
    # Maybe the rest can be too!
    TABAN_KEY = auto()
    KINGS_ROOM_1000 = auto()
    QUEENS_ROOM_1000 = auto()
    KINGS_ROOM_600 = auto()
    QUEENS_ROOM_600 = auto()
    ROYAL_KITCHEN = auto()
    QUEENS_TOWER_600 = auto()
    KINGS_TOWER_600 = auto()
    KINGS_TOWER_1000 = auto()
    QUEENS_TOWER_1000 = auto()
    GUARDIA_COURT_TOWER = auto()
    MANORIA_CATHEDRAL_1 = auto()
    MANORIA_CATHEDRAL_2 = auto()
    MANORIA_CATHEDRAL_3 = auto()
    MANORIA_INTERIOR_1 = auto()
    MANORIA_INTERIOR_2 = auto()
    MANORIA_INTERIOR_3 = auto()
    MANORIA_INTERIOR_4 = auto()
    MANORIA_SHRINE_SIDEROOM_1 = auto()
    MANORIA_SHRINE_SIDEROOM_2 = auto()
    MANORIA_BROMIDE_1 = auto()
    MANORIA_BROMIDE_2 = auto()
    MANORIA_BROMIDE_3 = auto()
    MANORIA_SHRINE_MAGUS_1 = auto()
    MANORIA_SHRINE_MAGUS_2 = auto()
    YAKRAS_ROOM = auto()
    DENADORO_MTS_SCREEN2_1 = auto()
    DENADORO_MTS_SCREEN2_2 = auto()
    DENADORO_MTS_SCREEN2_3 = auto()
    DENADORO_MTS_FINAL_1 = auto()
    DENADORO_MTS_FINAL_2 = auto()
    DENADORO_MTS_FINAL_3 = auto()
    DENADORO_MTS_WATERFALL_TOP_1 = auto()
    DENADORO_MTS_WATERFALL_TOP_2 = auto()
    DENADORO_MTS_WATERFALL_TOP_3 = auto()
    DENADORO_MTS_WATERFALL_TOP_4 = auto()
    DENADORO_MTS_WATERFALL_TOP_5 = auto()
    DENADORO_MTS_ENTRANCE_1 = auto()
    DENADORO_MTS_ENTRANCE_2 = auto()
    DENADORO_MTS_SCREEN3_1 = auto()
    DENADORO_MTS_SCREEN3_2 = auto()
    DENADORO_MTS_SCREEN3_3 = auto()
    DENADORO_MTS_SCREEN3_4 = auto()
    DENADORO_MTS_AMBUSH = auto()
    DENADORO_MTS_SAVE_PT = auto()
    DENADORO_MTS_KEY = auto()
    BANGOR_DOME_SEAL_1 = auto()
    BANGOR_DOME_SEAL_2 = auto()
    BANGOR_DOME_SEAL_3 = auto()
    TRANN_DOME_SEAL_1 = auto()
    TRANN_DOME_SEAL_2 = auto()
    ARRIS_DOME_SEAL_1 = auto()
    ARRIS_DOME_SEAL_2 = auto()
    ARRIS_DOME_SEAL_3 = auto()
    ARRIS_DOME_SEAL_4 = auto()
    TRUCE_INN_SEALED_600 = auto()
    PORRE_ELDER_SEALED_1 = auto()
    PORRE_ELDER_SEALED_2 = auto()
    GUARDIA_CASTLE_SEALED_600 = auto()
    GUARDIA_FOREST_SEALED_600 = auto()
    TRUCE_INN_SEALED_1000 = auto()
    PORRE_MAYOR_SEALED_1 = auto()
    PORRE_MAYOR_SEALED_2 = auto()
    GUARDIA_FOREST_SEALED_1000 = auto()
    GUARDIA_CASTLE_SEALED_1000 = auto()
    HECKRAN_SEALED_1 = auto()
    HECKRAN_SEALED_2 = auto()
    PYRAMID_LEFT = auto()
    PYRAMID_RIGHT = auto()
    MAGIC_CAVE_SEALED = auto()
    MYSTIC_MT_STREAM = auto()
    FOREST_MAZE_1 = auto()
    FOREST_MAZE_2 = auto()
    FOREST_MAZE_3 = auto()
    FOREST_MAZE_4 = auto()
    FOREST_MAZE_5 = auto()
    FOREST_MAZE_6 = auto()
    FOREST_MAZE_7 = auto()
    FOREST_MAZE_8 = auto()
    FOREST_MAZE_9 = auto()
    REPTITE_LAIR_REPTITES_1 = auto()
    REPTITE_LAIR_REPTITES_2 = auto()
    REPTITE_LAIR_KEY = auto()
    DACTYL_NEST_1 = auto()
    DACTYL_NEST_2 = auto()
    DACTYL_NEST_3 = auto()
    MELCHIOR_KEY = auto()
    FROGS_BURROW_LEFT = auto()
    # Tabs later if they're going to be randomized
    GUARDIA_FOREST_POWER_TAB_600 = auto()
    GUARDIA_FOREST_POWER_TAB_1000 = auto()
    SUN_KEEP_POWER_TAB_600 = auto()
    MEDINA_ELDER_SPEED_TAB = auto()
    MEDINA_ELDER_MAGIC_TAB = auto()
    # Non-Chronosanity chests:
    GUARDIA_JAIL_FRITZ_STORAGE = auto()
    GUARDIA_JAIL_CELL = auto()
    GUARDIA_JAIL_OMNICRONE_1 = auto()
    GUARDIA_JAIL_OMNICRONE_2 = auto()
    GUARDIA_JAIL_OMNICRONE_3 = auto()
    GUARDIA_JAIL_HOLE_1 = auto()
    GUARDIA_JAIL_HOLE_2 = auto()
    GUARDIA_JAIL_OUTER_WALL = auto()
    GUARDIA_JAIL_OMNICRONE_4 = auto()
    GUARDIA_JAIL_FRITZ = auto()
    MAGUS_CASTLE_RIGHT_HALL = auto()
    SUNKEN_DESERT_B1_NW = auto()
    SUNKEN_DESERT_B1_NE = auto()
    SUNKEN_DESERT_B1_SE = auto()
    SUNKEN_DESERT_B1_SW = auto()
    SUNKEN_DESERT_B2_NW = auto()
    SUNKEN_DESERT_B2_N = auto()
    SUNKEN_DESERT_B2_W = auto()
    SUNKEN_DESERT_B2_SW = auto()
    SUNKEN_DESERT_B2_SE = auto()
    SUNKEN_DESERT_B2_E = auto()
    SUNKEN_DESERT_B2_CENTER = auto()
    MAGUS_CASTLE_GUILLOTINE_1 = auto()
    MAGUS_CASTLE_GUILLOTINE_2 = auto()
    MAGUS_CASTLE_SLASH_ROOM_1 = auto()
    MAGUS_CASTLE_SLASH_ROOM_2 = auto()
    MAGUS_CASTLE_STATUE_HALL = auto()
    MAGUS_CASTLE_FOUR_KIDS = auto()
    MAGUS_CASTLE_OZZIE_1 = auto()
    MAGUS_CASTLE_OZZIE_2 = auto()
    MAGUS_CASTLE_ENEMY_ELEVATOR = auto()
    REPTITE_LAIR_SECRET_B2_NE_RIGHT = auto()
    LAB_32_RACE_LOG = auto()
    FACTORY_RUINS_GENERATOR = auto()
    DEATH_PEAK_SOUTH_FACE_KRAKKER = auto()
    DEATH_PEAK_SOUTH_FACE_SPAWN_SAVE = auto()
    DEATH_PEAK_SOUTH_FACE_SUMMIT = auto()
    DEATH_PEAK_FIELD = auto()
    DEATH_PEAK_KRAKKER_PARADE = auto()
    DEATH_PEAK_CAVES_LEFT = auto()
    DEATH_PEAK_CAVES_CENTER = auto()
    DEATH_PEAK_CAVES_RIGHT = auto()
    REPTITE_LAIR_SECRET_B1_SW = auto()
    REPTITE_LAIR_SECRET_B1_NE = auto()
    REPTITE_LAIR_SECRET_B1_SE = auto()
    REPTITE_LAIR_SECRET_B2_SE_RIGHT = auto()
    REPTITE_LAIR_SECRET_B2_NE_OR_SE_LEFT = auto()
    REPTITE_LAIR_SECRET_B2_SW = auto()
    GIANTS_CLAW_THRONE_1 = auto()
    GIANTS_CLAW_THRONE_2 = auto()
    # TYRANO_LAIR_THRONE Unused
    TYRANO_LAIR_TRAPDOOR = auto()
    TYRANO_LAIR_KINO_CELL = auto()
    # TYRANO_LAIR Unused? : 0xB7
    TYRANO_LAIR_MAZE_1 = auto()
    TYRANO_LAIR_MAZE_2 = auto()
    TYRANO_LAIR_MAZE_3 = auto()
    TYRANO_LAIR_MAZE_4 = auto()
    # 0xBC - 0xCF - BLACK_OMEN
    BLACK_OMEN_AUX_COMMAND_MID = auto()
    BLACK_OMEN_AUX_COMMAND_NE = auto()
    BLACK_OMEN_GRAND_HALL = auto()
    BLACK_OMEN_NU_HALL_NW = auto()
    BLACK_OMEN_NU_HALL_W = auto()
    BLACK_OMEN_NU_HALL_SW = auto()
    BLACK_OMEN_NU_HALL_NE = auto()
    BLACK_OMEN_NU_HALL_E = auto()
    BLACK_OMEN_NU_HALL_SE = auto()
    BLACK_OMEN_ROYAL_PATH = auto()
    BLACK_OMEN_RUMINATOR_PARADE = auto()
    BLACK_OMEN_EYEBALL_HALL = auto()
    BLACK_OMEN_TUBSTER_FLY = auto()
    BLACK_OMEN_MARTELLO = auto()
    BLACK_OMEN_ALIEN_SW = auto()
    BLACK_OMEN_ALIEN_NE = auto()
    BLACK_OMEN_ALIEN_NW = auto()
    BLACK_OMEN_TERRA_W = auto()
    BLACK_OMEN_TERRA_ROCK = auto()
    BLACK_OMEN_TERRA_NE = auto()
    OCEAN_PALACE_MAIN_S = auto()
    OCEAN_PALACE_MAIN_N = auto()
    OCEAN_PALACE_E_ROOM = auto()
    OCEAN_PALACE_W_ROOM = auto()
    OCEAN_PALACE_SWITCH_NW = auto()
    OCEAN_PALACE_SWITCH_SW = auto()
    OCEAN_PALACE_SWITCH_NE = auto()
    OCEAN_PALACE_SWITCH_SECRET = auto()
    OCEAN_PALACE_FINAL = auto()
    # FACTORY_RUINS_UNUSED: 0xE7
    MAGUS_CASTLE_LEFT_HALL = auto()
    MAGUS_CASTLE_UNSKIPPABLES = auto()
    MAGUS_CASTLE_PIT_E = auto()
    MAGUS_CASTLE_PIT_NE = auto()
    MAGUS_CASTLE_PIT_NW = auto()
    MAGUS_CASTLE_PIT_W = auto()
    # GIANTS_CLAW_MAZE Unused: 0xF7
    # DEATH_PEAK_CLIFF Unused: 0xF8
