from __future__ import annotations
from enum import Enum, auto
import random

from ctenums import ItemID, EnemyID

from ctrom import CTRom
import randoconfig as cfg
import randosettings as rset

import treasurewriter as tw
import enemywriter as ew


class RewardGroup(Enum):
    COMMON_ENEMY = auto()
    UNCOMMON_ENEMY = auto()
    RARE_ENEMY = auto()
    RAREST_ENEMY = auto()
    EARLY_BOSS = auto()
    MIDGAME_BOSS = auto()
    LATE_BOSS = auto()


# The existing item distribution all works as follows:
#   1) Choose a drop from some distribution
#   2) Either use the drop as the charm or choose a charm from another dist
#   3) Eliminate the drop with some probability
# This gives rise to three parameters: drop_dist, charm_dist, and drop_rate.
# Treasure assignment then works as follows:
#   1) Get a drop from drop_dist
#   2) if charm_dist is None, charm=drop else get charm from charm_dist
#   3) Set drop to 0 (ItemID.NONE) with probability 1-drop_rate
# So get_distributions returns drop_dist, charm_dist, drop_rate
def get_distributions(enemy_group: RewardGroup,
                      difficulty: rset.Difficulty) -> (tw.TreasureDist,
                                                       tw.TreasureDist,
                                                       float):

    if enemy_group == RewardGroup.COMMON_ENEMY:
        if difficulty == rset.Difficulty.NORMAL or \
           difficulty == rset.Difficulty.EASY:

            drop_dist = tw.TreasureDist(
                (2, tw.passable_lvl_items + tw.low_lvl_items),
                (8, (tw.passable_lvl_consumables +
                     tw.passable_lvl_consumables)),
            )
            charm_dist = None
            drop_rate = 0.5
        elif difficulty == rset.Difficulty.HARD:
            drop_dist = tw.TreasureDist((1, [ItemID.NONE]))
            charm_dist = drop_dist
            drop_rate = 0
        else:
            exit()
    elif enemy_group == RewardGroup.UNCOMMON_ENEMY:
        if difficulty in (rset.Difficulty.NORMAL, rset.Difficulty.EASY):
            drop_dist = tw.TreasureDist(
                (2, tw.mid_lvl_items+tw.good_lvl_items),
                (8, tw.mid_lvl_consumables+tw.good_lvl_consumables)
            )

            charm_dist = None
            drop_rate = 0.4
        elif difficulty == rset.Difficulty.HARD:
            drop_dist = tw.TreasureDist((1, [ItemID.NONE]))
            charm_dist = tw.TreasureDist(
                (1, tw.mid_lvl_consumables+tw.good_lvl_consumables)
            )
            drop_rate = 0
        else:
            exit()
    elif enemy_group == RewardGroup.RARE_ENEMY:
        if difficulty in (rset.Difficulty.NORMAL, rset.Difficulty.EASY):
            drop_dist = tw.TreasureDist(
                (2, (tw.mid_lvl_items + tw.good_lvl_items +
                     tw.high_lvl_items)),
                (8, (tw.mid_lvl_consumables + tw.good_lvl_consumables +
                     tw.high_lvl_consumables))
            )
            charm_dist = None
            drop_rate = 0.4
        elif difficulty == rset.Difficulty.HARD:
            drop_dist = tw.TreasureDist(
                (1, (tw.passable_lvl_consumables + tw.mid_lvl_consumables +
                     tw.good_lvl_consumables))
            )
            charm_dist = tw.TreasureDist(
                (1, tw.mid_lvl_items + tw.good_lvl_items)
            )
            drop_rate = 1.0
        else:
            exit()
    elif enemy_group == RewardGroup.RAREST_ENEMY:
        if difficulty in (rset.Difficulty.NORMAL, rset.Difficulty.EASY):
            drop_dist = tw.TreasureDist(
                (1, tw.high_lvl_items + tw.awesome_lvl_items),
                (9, tw.high_lvl_consumables + tw.awesome_lvl_consumables)
            )
            charm_dist = None
            drop_rate = 0.3
        elif difficulty == rset.Difficulty.HARD:
            drop_dist = tw.TreasureDist(
                (2, (tw.mid_lvl_items + tw.good_lvl_items +
                     tw.high_lvl_items + tw.awesome_lvl_items)),
                (8, (tw.mid_lvl_consumables + tw.good_lvl_consumables +
                     tw.high_lvl_consumables + tw.awesome_lvl_consumables))
            )
        else:
            exit()
    elif enemy_group == RewardGroup.EARLY_BOSS:
        if difficulty in (rset.Difficulty.NORMAL, rset.Difficulty.EASY):
            drop_dist = tw.TreasureDist(
                (15, tw.awesome_lvl_items),
                (60, tw.good_lvl_items + tw.high_lvl_items),
                (225, tw.mid_lvl_items),
                (100, (tw.mid_lvl_consumables + tw.high_lvl_consumables +
                       tw.good_lvl_consumables + tw.awesome_lvl_consumables))
            )
            charm_dist = tw.TreasureDist(
                (5, tw.awesome_lvl_items),
                (20, tw.good_lvl_items + tw.high_lvl_items),
                (75, tw.mid_lvl_items)
            )
            drop_rate = 1.0
        elif difficulty == rset.Difficulty.HARD:
            drop_dist = tw.TreasureDist(
                (5, tw.awesome_lvl_items),
                (20, tw.good_lvl_items + tw.high_lvl_items),
                (75, tw.mid_lvl_items),
                (100, (tw.mid_lvl_consumables + tw.high_lvl_consumables +
                       tw.good_lvl_consumables + tw.awesome_lvl_consumables))
            )
            charm_dist = tw.TreasureDist(
                (5, tw.awesome_lvl_items),
                (20, tw.good_lvl_items + tw.high_lvl_items),
                (75, tw.mid_lvl_items)
            )
            drop_rate = 0.5
        else:
            exit()
    elif enemy_group == RewardGroup.MIDGAME_BOSS:
        if difficulty in (rset.Difficulty.NORMAL, rset.Difficulty.EASY):
            drop_dist = tw.TreasureDist(
                (15, tw.awesome_lvl_items),
                (60, tw.good_lvl_items + tw.high_lvl_items),
                (225, tw.good_lvl_items),
                (100, (tw.mid_lvl_consumables + tw.high_lvl_consumables +
                       tw.good_lvl_consumables + tw.awesome_lvl_consumables))
            )
            charm_dist = tw.TreasureDist(
                (5, tw.awesome_lvl_items),
                (20, tw.good_lvl_items + tw.high_lvl_items),
                (75, tw.good_lvl_items)
            )
            drop_rate = 1.0
        elif difficulty == rset.Difficulty.HARD:
            drop_dist = tw.TreasureDist(
                (5, tw.awesome_lvl_items),
                (20, tw.good_lvl_items + tw.high_lvl_items),
                (75, tw.good_lvl_items),
                (100, (tw.mid_lvl_consumables + tw.high_lvl_consumables +
                       tw.good_lvl_consumables + tw.awesome_lvl_consumables))
            )
            charm_dist = tw.TreasureDist(
                (5, tw.awesome_lvl_items),
                (20, tw.good_lvl_items + tw.high_lvl_items),
                (75, tw.good_lvl_items)
            )
            drop_rate = 1.0
        else:
            exit()
    elif enemy_group == RewardGroup.LATE_BOSS:
        if difficulty in (rset.Difficulty.NORMAL, rset.Difficulty.EASY):
            drop_dist = tw.TreasureDist(
                (15, tw.awesome_lvl_items),
                (285, tw.good_lvl_items + tw.high_lvl_items),
                (100, (tw.mid_lvl_consumables + tw.good_lvl_consumables +
                       tw.high_lvl_consumables + tw.awesome_lvl_consumables))
            )
            charm_dist = tw.TreasureDist(
                (5, tw.awesome_lvl_items),
                (95, tw.good_lvl_items, tw.high_lvl_items)
            )
            drop_rate = 1.0
        elif difficulty == rset.Difficulty.HARD:
            drop_dist = tw.TreasureDist(
                (10, tw.awesome_lvl_items),
                (190, tw.good_lvl_items + tw.high_lvl_items),
                (100, (tw.mid_lvl_consumables + tw.good_lvl_consumables +
                       tw.high_lvl_consumables + tw.awesome_lvl_consumables))
            )
            charm_dist = tw.TreasureDist(
                (5, tw.awesome_lvl_items),
                (95, tw.good_lvl_items, tw.high_lvl_items)
            )
            drop_rate = 1.0
        else:
            exit()

    return drop_dist, charm_dist, drop_rate


common_enemies = [
    EnemyID.BELLBIRD, EnemyID.BLUE_IMP, EnemyID.GREEN_IMP, EnemyID.ROLY,
    EnemyID.POLY, EnemyID.ROLYPOLY, EnemyID.ROLY_RIDER, EnemyID.BLUE_EAGLET,
    EnemyID.AVIAN_CHAOS, EnemyID.IMP_ACE, EnemyID.GNASHER, EnemyID.NAGA_ETTE,
    EnemyID.OCTOBLUSH, EnemyID.FREE_LANCER, EnemyID.JINN_BOTTLE,
    EnemyID.TEMPURITE, EnemyID.DIABLOS, EnemyID.HENCH_BLUE, EnemyID.MAD_BAT,
    EnemyID.CRATER, EnemyID.HETAKE, EnemyID.SHADOW, EnemyID.GOBLIN,
    EnemyID.CAVE_BAT, EnemyID.OGAN, EnemyID.BEETLE, EnemyID.GATO,
]

uncommon_enemies = [
    EnemyID.REPTITE_GREEN, EnemyID.KILWALA, EnemyID.KRAWLIE,
    EnemyID.HENCH_PURPLE, EnemyID.GOLD_EAGLET, EnemyID.RED_EAGLET,
    EnemyID.GNAWER, EnemyID.OCTOPOD, EnemyID.FLY_TRAP, EnemyID.MEAT_EATER,
    EnemyID.KRAKKER, EnemyID.EGDER, EnemyID.DECEDENT, EnemyID.MACABRE,
    EnemyID.GUARD, EnemyID.SENTRY, EnemyID.OUTLAW, EnemyID.REPTITE_PURPLE,
    EnemyID.BLUE_SHIELD, EnemyID.YODU_DE, EnemyID.EVILWEEVIL,
    EnemyID.GRIMALKIN, EnemyID.T_POLE, EnemyID.AMPHIBITE, EnemyID.VAMP,
    EnemyID.BUGGER, EnemyID.DEBUGGER, EnemyID.SORCERER, EnemyID.CRATER,
    EnemyID.VOLCANO, EnemyID.SHITAKE, EnemyID.SHIST, EnemyID.NEREID,
    EnemyID.MOHAVOR, EnemyID.ACID, EnemyID.ALKALINE, EnemyID.ION,
    EnemyID.ANION, EnemyID.WINGED_APE, EnemyID.MEGASAUR, EnemyID.OMNICRONE,
    EnemyID.BEAST, EnemyID.AVIAN_REX, EnemyID.RAT, EnemyID.GREMLIN,
    EnemyID.RUNNER, EnemyID.PROTO_2, EnemyID.PROTO_3, EnemyID.BUG,
    EnemyID.MASA, EnemyID.MUNE, EnemyID.MUTANT, EnemyID.DECEDENT_II,
    EnemyID.SPEKKIO_FROG, EnemyID.SPEKKIO_KILWALA, EnemyID.HEXAPOD,
    EnemyID.ROLY_BOMBER,
]

rare_enemies = [
    EnemyID.TERRASAUR, EnemyID.MARTELLO, EnemyID.PANEL, EnemyID.STONE_IMP,
    EnemyID.BANTAM_IMP, EnemyID.RUMINATOR, EnemyID.MAN_EATER, EnemyID.DEFUNCT,
    EnemyID.DECEASED, EnemyID.REAPER, EnemyID.JUGGLER, EnemyID.RETINITE_EYE,
    EnemyID.MAGE, EnemyID.INCOGNITO, EnemyID.PEEPINGDOOM, EnemyID.BOSS_ORB,
    EnemyID.GARGOYLE, EnemyID.SCOUTER, EnemyID.FLYCLOPS, EnemyID.DEBUGGEST,
    EnemyID.JINN, EnemyID.BARGHEST, EnemyID.PAHOEHOE, EnemyID.ALKALINE,
    EnemyID.THRASHER, EnemyID.LASHER, EnemyID.FLUNKY, EnemyID.GROUPIE,
    EnemyID.CAVE_APE, EnemyID.LIZARDACTYL, EnemyID.BLOB, EnemyID.ALIEN,
    EnemyID.PROTO_4, EnemyID.GOON, EnemyID.SYNCHRITE, EnemyID.METAL_MUTE,
    EnemyID.GIGASAUR, EnemyID.FOSSIL_APE, EnemyID.CYBOT, EnemyID.TUBSTER,
    EnemyID.RED_SCOUT, EnemyID.BLUE_SCOUT, EnemyID.LASER_GUARD,
    EnemyID.SPEKKIO_OGRE, EnemyID.SPEKKIO_OMNICRONE, EnemyID.SPEKKIO_MASA_MUNE,
    EnemyID.SPEKKIO_NU, EnemyID.OZZIE_MAGUS_CHAINS,
]

rarest_enemies = [
    EnemyID.NU, EnemyID.DEPARTED, EnemyID.SIDE_KICK, EnemyID.RUBBLE,
    EnemyID.NU_2,
]

early_bosses = [
    EnemyID.YAKRA, EnemyID.MASA, EnemyID.MUNE, EnemyID.MASA_MUNE,
    EnemyID.OZZIE_ZENAN, EnemyID.OZZIE_FORT, EnemyID.HECKRAN,
    EnemyID.ZOMBOR_BOTTOM, EnemyID.ZOMBOR_TOP, EnemyID.SUPER_SLASH_TRIO,
    EnemyID.FLEA_PLUS, EnemyID.ATROPOS_XR, EnemyID.GOLEM_BOSS,
]

midgame_bosses = [
    EnemyID.RETINITE_EYE, EnemyID.DRAGON_TANK, EnemyID.GRINDER, EnemyID.NIZBEL,
    EnemyID.NIZBEL_II, EnemyID.SLASH_SWORD, EnemyID.FLEA, EnemyID.TANK_HEAD,
    EnemyID.RETINITE_BOTTOM, EnemyID.RETINITE_TOP, EnemyID.DISPLAY,
    EnemyID.RUST_TYRANO, EnemyID.MOTHERBRAIN, EnemyID.YAKRA_XIII,
    EnemyID.LAVOS_2_HEAD, EnemyID.LAVOS_2_LEFT, EnemyID.LAVOS_2_RIGHT,
    EnemyID.LAVOS_3_CORE, EnemyID.GUARDIAN_BIT, EnemyID.GUARDIAN,
    EnemyID.LAVOS_SPAWN_SHELL, EnemyID.LAVOS_SPAWN_HEAD,
    EnemyID.LAVOS_OCEAN_PALACE, EnemyID.LAVOS_3_LEFT, EnemyID.LAVOS_3_RIGHT,
    EnemyID.SON_OF_SUN_EYE, EnemyID.SON_OF_SUN_FLAME, EnemyID.R_SERIES,
]

late_bosses = [
    EnemyID.MAMMON_M, EnemyID.ZEAL, EnemyID.TWIN_GOLEM, EnemyID.GOLEM,
    EnemyID.AZALA, EnemyID.ELDER_SPAWN_HEAD, EnemyID.ELDER_SPAWN_SHELL,
    EnemyID.ZEAL_2_CENTER, EnemyID.ZEAL_2_LEFT, EnemyID.ZEAL_2_RIGHT,
    EnemyID.GIGA_MUTANT_HEAD, EnemyID.GIGA_MUTANT_BOTTOM,
    EnemyID.TERRA_MUTANT_HEAD, EnemyID.TERRA_MUTANT_BOTTOM,
    EnemyID.FLEA_PLUS_TRIO, EnemyID.SUPER_SLASH, EnemyID.GREAT_OZZIE,
    EnemyID.BLACKTYRANO, EnemyID.GIGA_GAIA_HEAD, EnemyID.GIGA_GAIA_LEFT,
    EnemyID.GIGA_GAIA_RIGHT, EnemyID.MAGUS, EnemyID.DALTON_PLUS,
]


# This method just alters the cfg.RandoConfig object.
def process_ctrom(ctrom: CTRom, settings: rset.Settings,
                  config: cfg.RandoConfig):

    # Maybe this dict can be set up globally with the enemy lists
    enemy_group_dict = dict()
    enemy_group_dict[RewardGroup.COMMON_ENEMY] = common_enemies
    enemy_group_dict[RewardGroup.UNCOMMON_ENEMY] = uncommon_enemies
    enemy_group_dict[RewardGroup.RARE_ENEMY] = rare_enemies
    enemy_group_dict[RewardGroup.RAREST_ENEMY] = rarest_enemies
    enemy_group_dict[RewardGroup.EARLY_BOSS] = early_bosses
    enemy_group_dict[RewardGroup.MIDGAME_BOSS] = midgame_bosses
    enemy_group_dict[RewardGroup.LATE_BOSS] = late_bosses

    for group in list(RewardGroup):
        enemies = enemy_group_dict[group]
        drop_dist, charm_dist, drop_rate = \
            get_distributions(group, settings.item_difficulty)

        for enemy in enemies:
            drop = drop_dist.get_random_item()
            if charm_dist is None:
                charm = drop
            else:
                charm = charm_dist.get_random_item()

            if random.random() > drop_rate:
                drop = ItemID.NONE

            config.enemy_dict[enemy].drop_item = drop
            config.enemy_dict[enemy].charm_item = charm

            # print(f"Enemy: {enemy} assigned drop={drop}, charm={charm}")


def main():

    '''
    en_list = ew.late_boss_ids

    for x in en_list:
        enemy_id = repr(EnemyID(x))[1:].split(':')[0]
        print(f"{enemy_id}, ")

    quit()
    '''

    # Test randomizer configuration
    ctrom = CTRom.from_file('./roms/jets_test.sfc', True)
    settings = rset.Settings.get_race_presets()
    config = cfg.RandoConfig(ctrom.rom_data.getbuffer())

    process_ctrom(ctrom, settings, config)

    exit()

    # Test for overlaps
    enemy_classes = [common_enemies, uncommon_enemies, rare_enemies,
                     rarest_enemies, early_bosses, midgame_bosses,
                     late_bosses]

    for ind, group in enumerate(enemy_classes):
        complement = []
        other_groups = [x for x in enemy_classes if x is not group]
        for x in other_groups:
            complement += x

        overlap = [x for x in group if x in complement]
        print(f"Group {ind} overlaps:")
        print(overlap)
        print()

    total_assigned = []
    for x in enemy_classes:
        total_assigned += x

    for x in list(EnemyID):
        if x not in total_assigned:
            print(f"{x} [0x{int(x):02X}] not assigned")

    exit()

    # Checking to make sure the definitions are common across the files
    tw_items = tw.alvlconsumables
    ew_items = ew.alvlconsumables

    tw_minus_ew = [x for x in tw_items if x not in ew_items]
    ew_minus_tw = [x for x in ew_items if x not in tw_items]

    print("Treasure but not enemy drop/charm:")
    for x in tw_minus_ew:
        print(f"    {ItemID(x)}")

    print("Enemy drop/charm but not item:")
    for x in ew_minus_tw:
        print(f"    {ItemID(x)}")


if __name__ == '__main__':
    main()
