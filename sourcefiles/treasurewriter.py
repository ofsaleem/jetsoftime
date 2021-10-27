from __future__ import annotations
from dataclasses import dataclass, field
import struct as st
from typing import ClassVar, Tuple
import random as rand

import ctenums
from ctevent import get_compressed_event_length, get_loc_event_ptr

from ctrom import CTRom
import randoconfig as cfg
import randosettings as rset

TID = ctenums.TreasureID
ItemID = ctenums.ItemID


class TreasureLocTier(ctenums.StrIntEnum):
    LOW = 0
    LOW_MID = 1
    MID = 2
    MID_HIGH = 3
    HIGH_AWESOME = 4
    SEALED = 5


treasure_tiers: dict[TreasureLocTier, list[TID]] = {
    TreasureLocTier.LOW: [
        TID.TRUCE_MAYOR_1F, TID.TRUCE_MAYOR_2F, TID.KINGS_ROOM_1000,
        TID.QUEENS_ROOM_1000, TID.FOREST_RUINS, TID.PORRE_MAYOR_2F,
        TID.TRUCE_CANYON_1, TID.TRUCE_CANYON_2, TID.KINGS_ROOM_600,
        TID.QUEENS_ROOM_600, TID.ROYAL_KITCHEN, TID.CURSED_WOODS_1,
        TID.CURSED_WOODS_2, TID.FROGS_BURROW_RIGHT, TID.FIONAS_HOUSE_1,
        TID.FIONAS_HOUSE_2, TID.QUEENS_TOWER_600, TID.KINGS_TOWER_600,
        TID.KINGS_TOWER_1000, TID.QUEENS_TOWER_1000, TID.GUARDIA_COURT_TOWER,
    ],
    TreasureLocTier.LOW_MID: [
        TID.HECKRAN_CAVE_SIDETRACK, TID.HECKRAN_CAVE_ENTRANCE,
        TID.HECKRAN_CAVE_1, TID.HECKRAN_CAVE_2, TID.GUARDIA_JAIL_FRITZ,
        TID.MANORIA_CATHEDRAL_1, TID.MANORIA_CATHEDRAL_2,
        TID.MANORIA_CATHEDRAL_3, TID.MANORIA_INTERIOR_1,
        TID.MANORIA_INTERIOR_2, TID.MANORIA_INTERIOR_4,
        TID.DENADORO_MTS_SCREEN2_1, TID.DENADORO_MTS_SCREEN2_2,
        TID.DENADORO_MTS_SCREEN2_3, TID.DENADORO_MTS_FINAL_1,
        TID.DENADORO_MTS_FINAL_2, TID.DENADORO_MTS_FINAL_3,
        TID.DENADORO_MTS_WATERFALL_TOP_3, TID.DENADORO_MTS_WATERFALL_TOP_4,
        TID.DENADORO_MTS_WATERFALL_TOP_5, TID.DENADORO_MTS_ENTRANCE_1,
        TID.DENADORO_MTS_ENTRANCE_2, TID.DENADORO_MTS_SCREEN3_1,
        TID.DENADORO_MTS_SCREEN3_2, TID.DENADORO_MTS_SCREEN3_3,
        TID.DENADORO_MTS_SCREEN3_4, TID.DENADORO_MTS_AMBUSH,
        TID.DENADORO_MTS_SAVE_PT, TID.YAKRAS_ROOM,
        TID.MANORIA_SHRINE_SIDEROOM_1, TID.MANORIA_SHRINE_SIDEROOM_2,
        TID.MANORIA_BROMIDE_1, TID.MANORIA_BROMIDE_2,
        TID.MANORIA_BROMIDE_3, TID.MANORIA_SHRINE_MAGUS_1,
        TID.MANORIA_SHRINE_MAGUS_2,
    ],
    TreasureLocTier.MID: [
        TID.GUARDIA_JAIL_FRITZ_STORAGE, TID.GUARDIA_JAIL_CELL,
        TID.GUARDIA_JAIL_OMNICRONE_1, TID.GUARDIA_JAIL_OMNICRONE_2,
        TID.GUARDIA_JAIL_OMNICRONE_3, TID.GUARDIA_JAIL_HOLE_1,
        TID.GUARDIA_JAIL_HOLE_2, TID.GUARDIA_JAIL_OUTER_WALL,
        TID.GUARDIA_JAIL_OMNICRONE_4, TID.GIANTS_CLAW_KINO_CELL,
        TID.GIANTS_CLAW_TRAPS, TID.MANORIA_INTERIOR_3,
        TID.DENADORO_MTS_WATERFALL_TOP_1, TID.DENADORO_MTS_WATERFALL_TOP_2,
        TID.SUNKEN_DESERT_B1_NW, TID.SUNKEN_DESERT_B1_NE,
        TID.SUNKEN_DESERT_B1_SE, TID.SUNKEN_DESERT_B1_SW,
        TID.SUNKEN_DESERT_B2_NW, TID.SUNKEN_DESERT_B2_N,
        TID.SUNKEN_DESERT_B2_W,  TID.SUNKEN_DESERT_B2_SW,
        TID.SUNKEN_DESERT_B2_SE, TID.SUNKEN_DESERT_B2_E,
        TID.SUNKEN_DESERT_B2_CENTER, TID.OZZIES_FORT_GUILLOTINES_1,
        TID.OZZIES_FORT_GUILLOTINES_2, TID.OZZIES_FORT_GUILLOTINES_3,
        TID.OZZIES_FORT_GUILLOTINES_4, TID.OZZIES_FORT_FINAL_1,
        TID.OZZIES_FORT_FINAL_2, TID.GIANTS_CLAW_CAVES_1,
        TID.GIANTS_CLAW_CAVES_2, TID.GIANTS_CLAW_CAVES_3,
        TID.GIANTS_CLAW_CAVES_4, TID.GIANTS_CLAW_CAVES_5,
        TID.MYSTIC_MT_STREAM, TID.FOREST_MAZE_1,
        TID.FOREST_MAZE_2, TID.FOREST_MAZE_3, TID.FOREST_MAZE_4,
        TID.FOREST_MAZE_5, TID.FOREST_MAZE_6, TID.FOREST_MAZE_7,
        TID.FOREST_MAZE_8, TID.FOREST_MAZE_9,
        TID.REPTITE_LAIR_REPTITES_1, TID.REPTITE_LAIR_REPTITES_2,
        TID.DACTYL_NEST_1, TID.DACTYL_NEST_2, TID.DACTYL_NEST_3,
        TID.GIANTS_CLAW_THRONE_1, TID.GIANTS_CLAW_THRONE_2,
        TID.TYRANO_LAIR_KINO_CELL, TID.ARRIS_DOME_FOOD_STORE,
        TID.PRISON_TOWER_1000,
    ],
    # Original had some overlap with lower tiers.  Now removed.
    TreasureLocTier.MID_HIGH: [
        TID.GUARDIA_BASEMENT_1, TID.GUARDIA_BASEMENT_2, TID.GUARDIA_BASEMENT_3,
        TID.MAGUS_CASTLE_RIGHT_HALL, TID.MAGUS_CASTLE_GUILLOTINE_1,
        TID.MAGUS_CASTLE_GUILLOTINE_2, TID.MAGUS_CASTLE_SLASH_ROOM_1,
        TID.MAGUS_CASTLE_SLASH_ROOM_2, TID.MAGUS_CASTLE_STATUE_HALL,
        TID.MAGUS_CASTLE_FOUR_KIDS, TID.MAGUS_CASTLE_OZZIE_1,
        TID.MAGUS_CASTLE_OZZIE_2, TID.MAGUS_CASTLE_ENEMY_ELEVATOR,
        TID.BANGOR_DOME_SEAL_1, TID.BANGOR_DOME_SEAL_2, TID.BANGOR_DOME_SEAL_3,
        TID.TRANN_DOME_SEAL_1, TID.TRANN_DOME_SEAL_2,
        TID.LAB_16_1, TID.LAB_16_2, TID.LAB_16_3, TID.LAB_16_4,
        TID.ARRIS_DOME_RATS, TID.LAB_32_1,
        TID.FACTORY_LEFT_AUX_CONSOLE, TID.FACTORY_LEFT_SECURITY_RIGHT,
        TID.FACTORY_LEFT_SECURITY_LEFT, TID.FACTORY_RIGHT_FLOOR_TOP,
        TID.FACTORY_RIGHT_FLOOR_LEFT, TID.FACTORY_RIGHT_FLOOR_BOTTOM,
        TID.FACTORY_RIGHT_FLOOR_SECRET, TID.FACTORY_RIGHT_CRANE_LOWER,
        TID.FACTORY_RIGHT_CRANE_UPPER, TID.FACTORY_RIGHT_INFO_ARCHIVE,
        TID.FACTORY_RUINS_GENERATOR, TID.SEWERS_1,
        TID.SEWERS_2, TID.SEWERS_3, TID.DEATH_PEAK_SOUTH_FACE_KRAKKER,
        TID.DEATH_PEAK_SOUTH_FACE_SPAWN_SAVE, TID.DEATH_PEAK_SOUTH_FACE_SUMMIT,
        TID.DEATH_PEAK_FIELD, TID.GENO_DOME_1F_1,
        TID.GENO_DOME_1F_2, TID.GENO_DOME_1F_3, TID.GENO_DOME_1F_4,
        TID.GENO_DOME_ROOM_1, TID.GENO_DOME_ROOM_2, TID.GENO_DOME_PROTO4_1,
        TID.GENO_DOME_PROTO4_2, TID.FACTORY_RIGHT_DATA_CORE_1,
        TID.FACTORY_RIGHT_DATA_CORE_2, TID.DEATH_PEAK_KRAKKER_PARADE,
        TID.DEATH_PEAK_CAVES_LEFT, TID.DEATH_PEAK_CAVES_CENTER,
        TID.DEATH_PEAK_CAVES_RIGHT, TID.GENO_DOME_2F_1,
        TID.GENO_DOME_2F_2, TID.GENO_DOME_2F_3, TID.GENO_DOME_2F_4,
        TID.TYRANO_LAIR_TRAPDOOR, TID.TYRANO_LAIR_MAZE_1,
        TID.TYRANO_LAIR_MAZE_2, TID.TYRANO_LAIR_MAZE_3,
        TID.TYRANO_LAIR_MAZE_4, TID.OCEAN_PALACE_MAIN_S,
        TID.OCEAN_PALACE_MAIN_N, TID.OCEAN_PALACE_E_ROOM,
        TID.OCEAN_PALACE_W_ROOM, TID.OCEAN_PALACE_SWITCH_NW,
        TID.OCEAN_PALACE_SWITCH_SW, TID.OCEAN_PALACE_SWITCH_NE,
        TID.GUARDIA_TREASURY_1, TID.GUARDIA_TREASURY_2, TID.GUARDIA_TREASURY_3,
        TID.MAGUS_CASTLE_LEFT_HALL, TID.MAGUS_CASTLE_UNSKIPPABLES,
        TID.MAGUS_CASTLE_PIT_E, TID.MAGUS_CASTLE_PIT_NE,
        TID.MAGUS_CASTLE_PIT_NW, TID.MAGUS_CASTLE_PIT_W,
        # FACTORY_RUINS_UNUSED: 0xE7
    ],
    TreasureLocTier.HIGH_AWESOME: [
        TID.ARRIS_DOME_SEAL_1, TID.ARRIS_DOME_SEAL_2,
        TID.ARRIS_DOME_SEAL_3, TID.ARRIS_DOME_SEAL_4,
        TID.REPTITE_LAIR_SECRET_B2_NE_RIGHT, TID.REPTITE_LAIR_SECRET_B1_SW,
        TID.REPTITE_LAIR_SECRET_B1_NE, TID.REPTITE_LAIR_SECRET_B1_SE,
        TID.REPTITE_LAIR_SECRET_B2_SE_RIGHT,
        TID.REPTITE_LAIR_SECRET_B2_NE_OR_SE_LEFT,
        TID.REPTITE_LAIR_SECRET_B2_SW, TID.BLACK_OMEN_AUX_COMMAND_MID,
        TID.BLACK_OMEN_AUX_COMMAND_NE, TID.BLACK_OMEN_GRAND_HALL,
        TID.BLACK_OMEN_NU_HALL_NW, TID.BLACK_OMEN_NU_HALL_W,
        TID.BLACK_OMEN_NU_HALL_SW, TID.BLACK_OMEN_NU_HALL_NE,
        TID.BLACK_OMEN_NU_HALL_E, TID.BLACK_OMEN_NU_HALL_SE,
        TID.BLACK_OMEN_ROYAL_PATH, TID.BLACK_OMEN_RUMINATOR_PARADE,
        TID.BLACK_OMEN_EYEBALL_HALL, TID.BLACK_OMEN_TUBSTER_FLY,
        TID.BLACK_OMEN_MARTELLO, TID.BLACK_OMEN_ALIEN_SW,
        TID.BLACK_OMEN_ALIEN_NE, TID.BLACK_OMEN_ALIEN_NW,
        TID.BLACK_OMEN_TERRA_W, TID.BLACK_OMEN_TERRA_NE,
        TID.MT_WOE_2ND_SCREEN_1, TID.MT_WOE_2ND_SCREEN_2,
        TID.MT_WOE_2ND_SCREEN_3, TID.MT_WOE_2ND_SCREEN_4,
        TID.MT_WOE_2ND_SCREEN_5, TID.MT_WOE_3RD_SCREEN_1,
        TID.MT_WOE_3RD_SCREEN_2, TID.MT_WOE_3RD_SCREEN_3,
        TID.MT_WOE_3RD_SCREEN_4, TID.MT_WOE_3RD_SCREEN_5,
        TID.MT_WOE_1ST_SCREEN, TID.MT_WOE_FINAL_1,
        TID.MT_WOE_FINAL_2, TID.OCEAN_PALACE_SWITCH_SECRET,
        TID.OCEAN_PALACE_FINAL,
    ],
    # Sealed chests include some script chests from Northern Ruins
    TreasureLocTier.SEALED: [
        TID.NORTHERN_RUINS_ANTECHAMBER_LEFT_600,
        TID.NORTHERN_RUINS_ANTECHAMBER_SEALED_600,
        TID.NORTHERN_RUINS_ANTECHAMBER_LEFT_1000,
        TID.NORTHERN_RUINS_ANTECHAMBER_SEALED_1000,
        TID.NORTHERN_RUINS_BACK_LEFT_SEALED_600,
        TID.NORTHERN_RUINS_BACK_LEFT_SEALED_1000,
        TID.NORTHERN_RUINS_BACK_RIGHT_SEALED_600,
        TID.NORTHERN_RUINS_BACK_RIGHT_SEALED_1000,
        TID.NORTHERN_RUINS_BASEMENT_600,
        TID.NORTHERN_RUINS_BASEMENT_1000,
        TID.TRUCE_INN_SEALED_600, TID.TRUCE_INN_SEALED_1000,
        TID.PORRE_ELDER_SEALED_1, TID.PORRE_ELDER_SEALED_2,
        TID.PORRE_MAYOR_SEALED_1, TID.PORRE_MAYOR_SEALED_2,
        TID.GUARDIA_CASTLE_SEALED_600, TID.GUARDIA_CASTLE_SEALED_1000,
        TID.GUARDIA_FOREST_SEALED_600, TID.GUARDIA_FOREST_SEALED_1000,
        TID.HECKRAN_SEALED_1, TID.HECKRAN_SEALED_2,
        TID.PYRAMID_LEFT, TID.PYRAMID_RIGHT,
        TID.MAGIC_CAVE_SEALED,
    ]
}

low_lvl_items: list[ItemID] = [
    ItemID.BANDANA, ItemID.DEFENDER, ItemID.MAGICSCARF, ItemID.POWERGLOVE,
    ItemID.RIBBON, ItemID.SIGHTSCOPE, ItemID.IRON_BLADE, ItemID.STEELSABER,
    ItemID.IRON_BOW, ItemID.LODE_BOW, ItemID.DART_GUN, ItemID.AUTO_GUN,
    ItemID.HAMMER_ARM, ItemID.MIRAGEHAND, ItemID.IRON_SWORD, ItemID.IRON_HELM,
    ItemID.BERET, ItemID.GOLD_HELM, ItemID.KARATE_GI, ItemID.BRONZEMAIL,
    ItemID.MAIDENSUIT, ItemID.IRON_SUIT, ItemID.TITAN_VEST, ItemID.GOLD_SUIT,
]

low_lvl_consumables: list[ItemID] = [
    ItemID.TONIC, ItemID.MID_TONIC, ItemID.HEAL, ItemID.REVIVE,
    ItemID.SHELTER, ItemID.POWER_MEAL,
]

passable_lvl_items: list[ItemID] = [
    ItemID.BERSERKER, ItemID.RAGE_BAND, ItemID.HIT_RING, ItemID.MUSCLERING,
    ItemID.POWERSCARF, ItemID.LODE_SWORD, ItemID.RED_KATANA, ItemID.BOLT_SWORD,
    ItemID.SERAPHSONG, ItemID.ROBIN_BOW, ItemID.PICOMAGNUM, ItemID.PLASMA_GUN,
    ItemID.STONE_ARM, ItemID.ROCK_HELM, ItemID.CERATOPPER, ItemID.RUBY_VEST,
    ItemID.DARK_MAIL, ItemID.MIST_ROBE, ItemID.MESO_MAIL,
]

passable_lvl_consumables: list[ItemID] = [
    ItemID.MID_TONIC, ItemID.ETHER
]

mid_lvl_items: list[ItemID] = [
    ItemID.THIRD_EYE, ItemID.WALLET, ItemID.SILVERERNG, ItemID.FRENZYBAND,
    ItemID.POWER_RING, ItemID.MAGIC_RING, ItemID.WALL_RING, ItemID.FLINT_EDGE,
    ItemID.DARK_SABER, ItemID.AEON_BLADE, ItemID.SAGE_BOW, ItemID.DREAM_BOW,
    ItemID.RUBY_GUN, ItemID.DREAM_GUN, ItemID.DOOMFINGER, ItemID.MAGMA_HAND,
    ItemID.MEGATONARM, ItemID.FLASHBLADE, ItemID.PEARL_EDGE, ItemID.HURRICANE,
    ItemID.GLOW_HELM, ItemID.LODE_HELM, ItemID.TABAN_HELM, ItemID.LUMIN_ROBE,
    ItemID.FLASH_MAIL, ItemID.WHITE_VEST, ItemID.BLACK_VEST, ItemID.BLUE_VEST,
    ItemID.RED_VEST, ItemID.TABAN_VEST,
]

mid_lvl_consumables: list[ItemID] = [
    ItemID.FULL_TONIC, ItemID.MID_ETHER, ItemID.LAPIS, ItemID.BARRIER,
    ItemID.SHIELD,
]

good_lvl_items: list[ItemID] = [
    ItemID.SPEED_BELT, ItemID.FLEA_VEST, ItemID.MAGIC_SEAL, ItemID.POWER_SEAL,
    ItemID.GOLD_ERNG, ItemID.SILVERSTUD, ItemID.GREENDREAM, ItemID.DEMON_EDGE,
    ItemID.ALLOYBLADE, ItemID.SLASHER, ItemID.COMETARROW, ItemID.SONICARROW,
    ItemID.MEGABLAST, ItemID.GRAEDUS, ItemID.BIG_HAND, ItemID.KAISER_ARM,
    ItemID.RUNE_BLADE, ItemID.DEMON_HIT, ItemID.STARSCYTHE, ItemID.AEON_HELM,
    ItemID.DARK_HELM, ItemID.RBOW_HELM, ItemID.MERMAIDCAP, ItemID.LODE_VEST,
    ItemID.AEON_SUIT, ItemID.WHITE_MAIL, ItemID.BLACK_MAIL, ItemID.BLUE_MAIL,
    ItemID.RED_MAIL,
]

good_lvl_consumables: list[ItemID] = [
    ItemID.FULL_TONIC, ItemID.FULL_ETHER, ItemID.HYPERETHER,
]

high_lvl_items: list[ItemID] = [
    ItemID.AMULET, ItemID.DASH_RING, ItemID.GOLD_STUD, ItemID.SUN_SHADES,
    ItemID.STAR_SWORD, ItemID.VEDICBLADE, ItemID.KALI_BLADE, ItemID.VALKERYE,
    ItemID.SIREN, ItemID.SHOCK_WAVE, ItemID.GIGA_ARM, ItemID.TERRA_ARM,
    ItemID.BRAVESWORD, ItemID.DOOMSICKLE, ItemID.GLOOM_HELM, ItemID.SAFE_HELM,
    ItemID.SIGHT_CAP, ItemID.MEMORY_CAP, ItemID.TIME_HAT, ItemID.ZODIACCAPE,
    ItemID.RUBY_ARMOR, ItemID.GLOOM_CAPE,
]

high_lvl_consumables: list[ItemID] = [
    ItemID.ELIXIR, ItemID.HYPERETHER, ItemID.POWER_TAB, ItemID.MAGIC_TAB,
    ItemID.SPEED_TAB,
]

awesome_lvl_items: list[ItemID] = [
    ItemID.PRISMSPECS, ItemID.SHIVA_EDGE, ItemID.SWALLOW, ItemID.SLASHER_2,
    ItemID.RAINBOW, ItemID.WONDERSHOT, ItemID.CRISIS_ARM, ItemID.HASTE_HELM,
    ItemID.PRISM_HELM, ItemID.VIGIL_HAT, ItemID.PRISMDRESS, ItemID.TABAN_SUIT,
    ItemID.MOON_ARMOR, ItemID.NOVA_ARMOR,
]

awesome_lvl_consumables: list[ItemID] = [
    ItemID.ELIXIR, ItemID.MEGAELIXIR
]

sealed_treasures: list[ItemID] = [
    ItemID.THIRD_EYE, ItemID.WALLET, ItemID.SILVERERNG, ItemID.FRENZYBAND,
    ItemID.POWER_RING, ItemID.MAGIC_RING, ItemID.WALL_RING, ItemID.FLINT_EDGE,
    ItemID.DARK_SABER, ItemID.AEON_BLADE, ItemID.SAGE_BOW, ItemID.DREAM_BOW,
    ItemID.RUBY_GUN, ItemID.DREAM_GUN, ItemID.DOOMFINGER, ItemID.MAGMA_HAND,
    ItemID.MEGATONARM, ItemID.FLASHBLADE, ItemID.PEARL_EDGE, ItemID.HURRICANE,
    ItemID.GLOW_HELM, ItemID.LODE_HELM, ItemID.TABAN_HELM, ItemID.LUMIN_ROBE,
    ItemID.FLASH_MAIL, ItemID.WHITE_VEST, ItemID.BLACK_VEST, ItemID.BLUE_VEST,
    ItemID.RED_VEST, ItemID.TABAN_VEST, ItemID.AMULET, ItemID.SPEED_BELT,
    ItemID.FLEA_VEST, ItemID.MAGIC_SEAL, ItemID.POWER_SEAL, ItemID.GOLD_ERNG,
    ItemID.SILVERSTUD, ItemID.GREENDREAM, ItemID.DEMON_EDGE, ItemID.ALLOYBLADE,
    ItemID.SLASHER, ItemID.COMETARROW, ItemID.SONICARROW, ItemID.MEGABLAST,
    ItemID.GRAEDUS, ItemID.BIG_HAND, ItemID.KAISER_ARM, ItemID.RUNE_BLADE,
    ItemID.DEMON_HIT, ItemID.STARSCYTHE, ItemID.AEON_HELM, ItemID.DARK_HELM,
    ItemID.RBOW_HELM, ItemID.MERMAIDCAP, ItemID.LODE_VEST, ItemID.AEON_SUIT,
    ItemID.WHITE_MAIL, ItemID.BLACK_MAIL, ItemID.BLUE_MAIL, ItemID.RED_MAIL,
    ItemID.DASH_RING, ItemID.GOLD_STUD, ItemID.SUN_SHADES, ItemID.STAR_SWORD,
    ItemID.VEDICBLADE, ItemID.KALI_BLADE, ItemID.VALKERYE, ItemID.SIREN,
    ItemID.SHOCK_WAVE, ItemID.GIGA_ARM, ItemID.TERRA_ARM, ItemID.BRAVESWORD,
    ItemID.DOOMSICKLE, ItemID.GLOOM_HELM, ItemID.SAFE_HELM, ItemID.SIGHT_CAP,
    ItemID.MEMORY_CAP, ItemID.TIME_HAT, ItemID.ZODIACCAPE, ItemID.RUBY_ARMOR,
    ItemID.GLOOM_CAPE, ItemID.PRISMSPECS, ItemID.SHIVA_EDGE, ItemID.SWALLOW,
    ItemID.SLASHER_2, ItemID.RAINBOW, ItemID.WONDERSHOT, ItemID.CRISIS_ARM,
    ItemID.HASTE_HELM, ItemID.PRISM_HELM, ItemID.VIGIL_HAT, ItemID.PRISMDRESS,
    ItemID.TABAN_SUIT, ItemID.MOON_ARMOR, ItemID.NOVA_ARMOR, ItemID.FULL_TONIC,
    ItemID.MID_ETHER, ItemID.LAPIS, ItemID.BARRIER, ItemID.SHIELD,
    ItemID.FULL_ETHER, ItemID.HYPERETHER, ItemID.ELIXIR, ItemID.MEGAELIXIR,
    ItemID.POWER_TAB, ItemID.MAGIC_TAB, ItemID.SPEED_TAB,
]

taban_helm_gifts: list[ItemID] = [
    ItemID.TABAN_HELM, ItemID.TIME_HAT, ItemID.GLOOM_HELM, ItemID.RBOW_HELM,
    ItemID.MERMAIDCAP, ItemID.OZZIEPANTS, ItemID.SAFE_HELM, ItemID.HASTE_HELM,
    ItemID.PRISM_HELM, ItemID.VIGIL_HAT,
]

taban_weapon_gifts: list[ItemID] = [
    ItemID.VEDICBLADE, ItemID.KALI_BLADE, ItemID.SWALLOW, ItemID.SLASHER_2,
    ItemID.SONICARROW, ItemID.SIREN, ItemID.SHOCK_WAVE, ItemID.KAISER_ARM,
    ItemID.GIGA_ARM, ItemID.RUNE_BLADE, ItemID.BRAVESWORD, ItemID.DEMON_HIT,
    ItemID.STARSCYTHE, ItemID.SHIVA_EDGE, ItemID.RAINBOW, ItemID.VALKERYE,
    ItemID.WONDERSHOT, ItemID.TERRA_ARM, ItemID.CRISIS_ARM, ItemID.DOOMSICKLE,
]

# Doomsickle is in the original.  Removed.
trade_ranged: list[ItemID] = [
    ItemID.VALKERYE, ItemID.SHOCK_WAVE, # ItemID.DOOMSICKLE
]
trade_accessory: list[ItemID] = [
    ItemID.GOLD_ERNG, ItemID.GOLD_STUD, ItemID.PRISMSPECS, ItemID.AMULET,
    ItemID.DASH_RING
]
trade_tabs: list[ItemID] = [
    ItemID.POWER_TAB, ItemID.MAGIC_TAB, ItemID.SPEED_TAB
]
trade_melee: list[ItemID] = [
    ItemID.RAINBOW, ItemID.TERRA_ARM, ItemID.BRAVESWORD,
]
trade_armors: list[ItemID] = [
    ItemID.GLOOM_CAPE, ItemID.TABAN_SUIT, ItemID.ZODIACCAPE,
    ItemID.NOVA_ARMOR, ItemID.MOON_ARMOR, ItemID.PRISMDRESS,
]
trade_helms: list[ItemID] = [
    ItemID.TABAN_HELM, ItemID.DARK_HELM, ItemID.RBOW_HELM,
    ItemID.MERMAIDCAP, ItemID.SAFE_HELM, ItemID.HASTE_HELM, ItemID.PRISM_HELM,
]

jerky_rewards: list[ItemID] = [
    ItemID.PRISMSPECS, ItemID.SHIVA_EDGE, ItemID.SWALLOW, ItemID.SLASHER_2,
    ItemID.RAINBOW, ItemID.WONDERSHOT, ItemID.CRISIS_ARM, ItemID.HASTE_HELM,
    ItemID.PRISM_HELM, ItemID.VIGIL_HAT, ItemID.PRISMDRESS, ItemID.TABAN_SUIT,
    ItemID.MOON_ARMOR, ItemID.NOVA_ARMOR,
]


# distribution uses relative frequencies instead of float probabilities
# for precision.
class TreasureDist:

    def __init__(self, *weight_item_pairs: Tuple[int, list[ItemID]]):
        # print(weight_item_pairs)
        # input()
        self.weight_item_pairs = weight_item_pairs

    def get_random_item(self) -> ItemID:
        target = rand.randrange(0, self.__total_weight)

        value = 0
        for x in self.__weight_item_pairs:
            value += x[0]

            if value > target:
                return rand.choice(x[1])

        print("Error, no selection")
        exit()

    @property
    def weight_item_pairs(self):
        return self.__weight_item_pairs

    @weight_item_pairs.setter
    def weight_item_pairs(self, new_pairs: list[Tuple[int, list[ItemID]]]):
        self.__weight_item_pairs = new_pairs
        self.__total_weight = sum(x[0] for x in new_pairs)


# Set up a big lookup table for distributions.
# Insert a difficulty and a chest type.  Get a distribution.
treasure_dists: list[TreasureDist] = [
    [None for x in list(TreasureLocTier) if x != TreasureLocTier.SEALED]
    for i in list(rset.Difficulty)]

treasure_dists[rset.Difficulty.EASY][TreasureLocTier.LOW] = \
    TreasureDist(
        (5, passable_lvl_consumables+mid_lvl_consumables),
        (6, passable_lvl_items+mid_lvl_items)
    )
treasure_dists[rset.Difficulty.EASY][TreasureLocTier.LOW_MID] = \
    TreasureDist(
        (50, mid_lvl_consumables+good_lvl_consumables),
        (15, good_lvl_items),
        (45, mid_lvl_items)
    )
treasure_dists[rset.Difficulty.EASY][TreasureLocTier.MID] = \
    TreasureDist(
        (50, good_lvl_consumables + high_lvl_consumables),
        (3, awesome_lvl_items),
        (12, high_lvl_items),
        (45, good_lvl_items)
    )
treasure_dists[rset.Difficulty.EASY][TreasureLocTier.MID_HIGH] = \
    TreasureDist(
        (50, good_lvl_consumables + high_lvl_consumables),
        (3, awesome_lvl_items),
        (12, high_lvl_items),
        (45, good_lvl_items)
    )
treasure_dists[rset.Difficulty.EASY][TreasureLocTier.HIGH_AWESOME] = \
    TreasureDist(
        (50, good_lvl_consumables+high_lvl_consumables),
        (3, awesome_lvl_items),
        (12, high_lvl_items),
        (45, good_lvl_items)
    )
treasure_dists[rset.Difficulty.NORMAL][TreasureLocTier.LOW] = \
    TreasureDist(
        (50, low_lvl_consumables),
        (60, low_lvl_items)
    )
treasure_dists[rset.Difficulty.NORMAL][TreasureLocTier.LOW_MID] = \
    TreasureDist(
        (50, low_lvl_consumables + passable_lvl_consumables),
        (15, mid_lvl_items),
        (45, passable_lvl_items)
    )
treasure_dists[rset.Difficulty.NORMAL][TreasureLocTier.MID] = \
    TreasureDist(
        (50, passable_lvl_consumables + mid_lvl_consumables),
        (3, high_lvl_items),
        (12, good_lvl_items),
        (45, mid_lvl_items)
    )
treasure_dists[rset.Difficulty.NORMAL][TreasureLocTier.MID_HIGH] = \
    TreasureDist(
        (50, mid_lvl_consumables + good_lvl_consumables),
        (3, awesome_lvl_items),
        (12, high_lvl_items),
        (45, good_lvl_items)
    )
treasure_dists[rset.Difficulty.NORMAL][TreasureLocTier.HIGH_AWESOME] = \
    TreasureDist(
        (400, (good_lvl_consumables + high_lvl_consumables +
               awesome_lvl_consumables)),
        (175, awesome_lvl_items),
        (525, good_lvl_items + high_lvl_items)
    )
treasure_dists[rset.Difficulty.HARD][TreasureLocTier.LOW] = \
    TreasureDist(
        (5, low_lvl_consumables),
        (6, low_lvl_items)
    )
treasure_dists[rset.Difficulty.HARD][TreasureLocTier.LOW_MID] = \
    TreasureDist(
        (5, low_lvl_consumables+passable_lvl_consumables),
        (6, passable_lvl_items)
    )
treasure_dists[rset.Difficulty.HARD][TreasureLocTier.MID] = \
    TreasureDist(
        (5, passable_lvl_consumables + mid_lvl_consumables),
        (6, mid_lvl_items)
    )
treasure_dists[rset.Difficulty.HARD][TreasureLocTier.MID_HIGH] = \
    TreasureDist(
        (5, mid_lvl_consumables + good_lvl_consumables),
        (6, mid_lvl_items + good_lvl_items)
    )
treasure_dists[rset.Difficulty.HARD][TreasureLocTier.HIGH_AWESOME] = \
    TreasureDist(
        (400, (mid_lvl_consumables + good_lvl_consumables +
               high_lvl_consumables + awesome_lvl_consumables)),
        (175, awesome_lvl_items),
        (525, mid_lvl_items + good_lvl_items + high_lvl_items)
    )

# Fixed a bug in tab distribution, was 1, 10, 9
tab_dist = TreasureDist(
    (1, [ItemID.SPEED_TAB]),
    (10, [ItemID.POWER_TAB]),
    (10, [ItemID.MAGIC_TAB])
)

sealed_dist = TreasureDist(
    (1, sealed_treasures)
)

# End of giant mass of distribution definitions


def get_treasure_distribution(settings: rset.Settings,
                              treasure_tier: TreasureLocTier):

    # Save some keystrokes with aliases.
    Tier = TreasureLocTier
    flags = settings.gameflags

    if rset.GameFlags.TAB_TREASURES in flags:
        return tab_dist
    elif treasure_tier == Tier.SEALED:
        return sealed_dist
    else:
        return treasure_dists[settings.item_difficulty][treasure_tier]


def write_treasures_to_config(settings: rset.Settings,
                              config: cfg.RandoConfig):

    assign = config.treasure_assign_dict

    # Do standard treasure chests
    for tier in TreasureLocTier:
        treasures = treasure_tiers[tier]
        dist = get_treasure_distribution(settings, tier)

        for treasure in treasures:
            assign[treasure].held_item = dist.get_random_item()

    # Now do special treasures.  These don't have complicated distributions.
    specials = [
        TID.TABAN_GIFT_HELM, TID.TABAN_GIFT_WEAPON,
        TID.TRADING_POST_ARMOR, TID.TRADING_POST_HELM,
        TID.TRADING_POST_ACCESSORY,
        TID.TRADING_POST_MELEE_WEAPON,
        TID.TRADING_POST_RANGED_WEAPON,
        TID.TRADING_POST_TAB,
        TID.JERKY_GIFT
    ]
    item_lists = [
        taban_helm_gifts, taban_weapon_gifts,
        trade_armors, trade_helms,
        trade_accessory,
        trade_melee,
        trade_ranged,
        trade_tabs,
        jerky_rewards
    ]

    for i in range(len(specials)):
        treasure = specials[i]
        items = item_lists[i]
        assign[treasure].held_item = rand.choice(items)

    # finally rocks
    rock_tids = [TID.DENADORO_ROCK, TID.GIANTS_CLAW_ROCK,
                 TID.LARUBA_ROCK, TID.KAJAR_ROCK, TID.BLACK_OMEN_TERRA_ROCK]

    rocks = [ItemID.GOLD_ROCK, ItemID.BLUE_ROCK,
             ItemID.SILVERROCK, ItemID.BLACK_ROCK, ItemID.WHITE_ROCK]
    rand.shuffle(rocks)

    for ind, tid in enumerate(rock_tids):
        assign[tid].held_item = rocks[ind]


def choose_item(pointer,difficulty,tab_treasures):
    rand_num = rand.randrange(0,11,1)
    if tab_treasures == "Y":
        rand_num = rand.randrange(0,20,1) # choose number from 0 to 20 inclusive.
        if rand_num == 0: # 4.8% chance of a speed tab
            writeitem = 0xCF;
        elif rand_num > 10: # 47.6% chance of a magic tab
            writeitem = 0xCE;
        else: # 47.6% chance of a power tab
            writeitem = 0xCD;
    elif difficulty == "easy":
        if pointer in lowlvlchests:
            if rand_num > 5:
                writeitem = rand.choice(plvlconsumables+mlvlconsumables)
            else: 
                writeitem = rand.choice(plvlitems+mlvlitems)
        elif pointer in lmidlvlchests:
            if rand_num > 5:
                writeitem = rand.choice(mlvlconsumables+glvlconsumables)
            else:
                rand_num = rand.randrange(0,100,1)
                if rand_num > 74:
                    writeitem = rand.choice(glvlitems)
                else:
                    writeitem = rand.choice(mlvlitems)
        elif pointer in midlvlchests or mhighlvlchests:
            if rand_num > 5:
                writeitem = rand.choice(glvlconsumables + hlvlconsumables)
            else:
                rand_num = rand.randrange(0,100,1)
                if rand_num > 74:
                   if rand_num > 94:
                       writeitem = rand.choice(alvlitems)
                   else:
                       writeitem = rand.choice(hlvlitems)
                else:
                    writeitem = rand.choice(glvlitems)
        elif pointer in hawelvlchests:
            if rand_num > 6:
                writeitem = rand.choice(glvlconsumables + hlvlconsumables + alvlconsumables)
            else:
                rand_num = rand.randrange(0,100,1)
                if rand_num > 74:
                    writeitem = rand.choice(alvlitems)
                else:
                    writeitem = rand.choice(glvlitems + hlvlitems)
    elif difficulty == "hard":
        if pointer in lowlvlchests:
            if rand_num > 5:
                writeitem = rand.choice(llvlconsumables)
            else: 
                writeitem = rand.choice(llvlitems)
        elif pointer in lmidlvlchests:
            if rand_num > 5:
                writeitem = rand.choice(llvlconsumables+plvlconsumables)
            else:
                writeitem = rand.choice(plvlitems)
        elif pointer in midlvlchests:
            if rand_num > 5:
                writeitem = rand.choice(plvlconsumables + mlvlconsumables)
            else:
                writeitem = rand.choice(mlvlitems)
        elif pointer in mhighlvlchests:
            if rand_num > 5:
                writeitem = rand.choice(mlvlconsumables + glvlconsumables)
            else:
                writeitem = rand.choice(mlvlitems+glvlitems)
        elif pointer in hawelvlchests:
            if rand_num > 6:
                writeitem = rand.choice(mlvlconsumables + glvlconsumables + hlvlconsumables + alvlconsumables)
            else:
                rand_num = rand.randrange(0,100,1)
                if rand_num > 74:
                    writeitem = rand.choice(alvlitems)
                else:
                    writeitem = rand.choice(mlvlitems + glvlitems + hlvlitems)
    else:
        if pointer in lowlvlchests:
            if rand_num > 5:
                writeitem = rand.choice(llvlconsumables)
            else: 
                writeitem = rand.choice(llvlitems)
        elif pointer in lmidlvlchests:
            if rand_num > 5:
                writeitem = rand.choice(llvlconsumables+plvlconsumables)
            else:
                rand_num = rand.randrange(0,100,1)
                if rand_num > 74:
                    writeitem = rand.choice(mlvlitems)
                else:
                    writeitem = rand.choice(plvlitems)
        elif pointer in midlvlchests:
            if rand_num > 5:
                writeitem = rand.choice(plvlconsumables + mlvlconsumables)
            else:
                rand_num = rand.randrange(0,100,1)
                if rand_num > 74:
                    if rand_num > 94:
                        writeitem = rand.choice(hlvlitems)
                    else:
                        writeitem = rand.choice(glvlitems)
                else:
                    writeitem = rand.choice(mlvlitems)
        elif pointer in mhighlvlchests:
            if rand_num > 5:
                writeitem = rand.choice(mlvlconsumables + glvlconsumables)
            else:
                rand_num = rand.randrange(0,100,1)
                if rand_num > 74:
                    if rand_num > 94:
                        writeitem = rand.choice(alvlitems)
                    else:
                        writeitem = rand.choice(hlvlitems)
                else:
                    writeitem = rand.choice(glvlitems)
        elif pointer in hawelvlchests:
            if rand_num > 6:
                writeitem = rand.choice(glvlconsumables + hlvlconsumables + alvlconsumables)
            else:
                rand_num = rand.randrange(0,100,1)
                if rand_num > 74:
                    writeitem = rand.choice(alvlitems)
                else:
                    writeitem = rand.choice(glvlitems + hlvlitems)
    return writeitem
def randomize_treasures(outfile,difficulty,tab_treasures):
   f = open(outfile,"r+b")
   for p in allpointers:
      f.seek(p-3)
      f.write(st.pack("B",0x00))
      writeitem = choose_item(p,difficulty,tab_treasures)
      f.seek(p)
      f.write(st.pack("B",writeitem))
   f.close()


def ptr_to_enum(ptr_list):
    # Turn old-style pointer lists into enum lists
    treasuretier = ptr_list
    chestid = set([(x-0x35f404)//4 for x in treasuretier])
    print(' '.join(f"{x:02X}" for x in chestid))

    config = cfg.RandoConfig()
    tdict = config.treasure_assign_dict

    treasureids = [x for x in tdict.keys()
                   if type(tdict[x]) == cfg.ChestTreasure
                   and tdict[x].chest_index in chestid]

    used_ids = [tdict[x].chest_index for x in treasureids]
    unused_ids = [x for x in chestid if x not in used_ids]

    # print(' '.join(f"{x:02X}" for x in used_ids))
    print(' '.join(f"{x:02X}" for x in unused_ids))
    input()

    for x in treasureids:
        y = repr(x)
        y = y.split(':')[0].replace('<', '').replace('TreasureID', 'TID')

        print(f"{y},")

    print(len(chestid), len(treasureids))


def item_num_to_enum(item_list):
    # Turn int list to ItemID list

    enum_list = []
    
    for x in item_list:
        y = ctenums.ItemID(x)
        enum_list.append(y)

    for x in enum_list:
        y = repr(x).split(':')[0].replace('<', '')
        print(f"{y},")


def find_script_ptrs(ptr_list):

    for ptr in ptr_list:
        chest_index = (ptr-0x35f404)//4
        if 0 > chest_index or chest_index > 0xF8:
            print(f"{ptr:06X}")


def main():

    # find_script_ptrs(mhighlvlchests)

    # items = []
    # item_num_to_enum(items)

    '''
    dist = TreasureDist(
        (1, awesome_lvl_consumables),
        (3, awesome_lvl_items)
    )

    for i in range(20):
        print(dist.get_random_item())
    '''

    '''
    sealed_ptrs = [0xC3328, 0xC332C,    # 0 Truce 1000
                   0x1BA717, 0x1BA72B,  # 2 Unknown
                   0x1BAB33, 0x1BAB35,  # 4 left pyramid
                   0x1BAB62, 0x1BAB64,  # 6 right pyramid
                   0x1BACD6, 0x1BACD8,  # 8 porre mayor 1
                   0x1BACF7, 0x1BACF9,  # 10 porre mayor 2
                   0x393D0, 0x393DE,    # 12 0x44 Northern Ruins Ante
                   0x393F8, 0x393FF,    # 14 hero's grave 3
                   0x1B03A4, 0x1B03B1,  # 16 0x46 NoRuins Back Room
                   0x1B03CD, 0x1B03D0,  # 18 hero's grave 1
                   0x1B03EF, 0x1B03F2,  # 20 0x46 NoRuins Back Room
                   0x1B0401, 0x1B0404,  # 22 hero's grave 2
                   0x19FE7C, 0x19FE83,  # 24 truce inn 600
                   0x30FBE9, 0x30FBEC,  # 26 unknown
                   0x1B90EA, 0x1B90F2,  # 28 porre elder 1
                   0x1B9123, 0x1B9126,  # 30 porre elder 2
                   0x1B31C7, 0x1B31CA,  # 32 magic cave
                   0x3AED24, 0x3AED26,  # 34 guardia castle 600
                   0x3AEF65, 0x3AEF67,  # 36 guardia castle 1000
                   0x1BAEF4, 0x1BAEF9,  # 38 northern ruins basement 1000
                   0x1BAF0A, 0x1BAF0F,  # 40 northern ruins basement 600
                   0x392FD, 0x39303,    # 42 northern ruins upstairs 1000
                   0x39313, 0x39319,    # 44 northern ruins upstairs 600
                   0x24EC29, 0x24EC2B,  # 46 Heckran's sealed 1
                   0x24EC3B, 0x24EC3D,  # 48 Heckran's sealed 2
                   0x3908B5, 0x3908C9,  # 50 Guardia forest 1000
                   0x39633B, 0x39633D]  # 52 Guardia forest 600

    print(len(sealed_ptrs)//2)
    print(len(sealed_chests))

    with open('./roms/jets_test.sfc', 'rb') as infile:
        rom = bytearray(infile.read())

    found_ptrs = [False for x in range(len(sealed_ptrs))]

    print(f"{len(rom):06X}")
    for loc in range(0, 0x1F0):
        start = get_loc_event_ptr(rom, int(loc))
        end = start + get_compressed_event_length(rom, loc)
        for ptr in sealed_ptrs:
            if start <= ptr < end:
                ind = sealed_ptrs.index(ptr)
                found_ptrs[ind] = True
                print(f"{ptr:06X} ({sealed_ptrs.index(ptr)}) "
                      f"in {loc:04X}")

    print([x for x in range(len(found_ptrs)) if not found_ptrs[x]])
    '''

    '''
    copy = high_awesome_lvl_chests[:]
    for x in copy:
        if x in low_mid_lvl_chests + low_lvl_chests \
           + mid_lvl_chests + mid_high_lvl_chests:
            print(x)
            # mid_high_lvl_chests.remove(x)
    '''
    # print revised list
    '''
    for x in mid_high_lvl_chests:
        y = repr(x)
        y = y.split(':')[0].replace('<', '').replace('TreasureID', 'TID')

        print(f"{y},")
    '''

if __name__ == "__main__":
    # randomize_treasures("Techwriter.sfc")
    main()
