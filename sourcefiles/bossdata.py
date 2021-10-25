from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Tuple, Type, TypeVar

from enemystats import EnemyStats

from ctenums import EnemyID, BossID, LocID


# Silly thing for typing classmethod return type from stackexchange
# https://stackoverflow.com/questions/44640479
T = TypeVar('T', bound='Boss')


@dataclass
class Boss:

    ids: list[int] = field(default_factory=list)
    stats: list[EnemyStats] = field(default_factory=list)
    disps: list[Tuple(int, int)] = field(default_factory=list)
    power: int = 0
    slots: list[int] = field(default_factory=list)

    def __str__(self):
        ret = f"Boss Power Level: {self.power}\n"
        for ind, partid in enumerate(self.ids):
            stats = self.stats[ind]
            ret += (f"Part {ind+1}\n"
                    f"\tEnemyID: {partid}\n"
                    f"\tName: {stats.name}\n"
                    f"\tLvl = {stats.level}\n"
                    f"\tHP = {stats.hp}\tSpd = {stats.speed}\n"
                    f"\tOff = {stats.offense}\tDef = {stats.defense}\n"
                    f"\tMag = {stats.magic}\tMdf = {stats.mdef}\n"
                    f"\tXP = {stats.xp}\tTP = {stats.tp}\tGP={stats.gp}\n"
                    f"\tDrop = {stats.drop_item}\n"
                    f"\tCharm = {stats.charm_item}\n")

        return ret

    # Make a subclass to implement scaling styles
    def scale_relative_to(self, other: Boss):
        raise NotImplementedError

    @classmethod
    def generic_one_spot(cls: Type[T], rom, boss_id, slot, power) -> T:
        ret = cls()
        ret.ids = [boss_id]
        ret.stats = [EnemyStats.from_rom(rom, boss_id)]
        ret.disps = [(0, 0)]
        ret.power = power
        ret.slots = [slot]

        return ret

    @classmethod
    def generic_multi_spot(cls: Type[T], rom, boss_ids, disps,
                           slots, power) -> T:
        ret = cls()
        ret.ids = boss_ids[:]
        ret.stats = [EnemyStats.from_rom(rom, x) for x in ret.ids]
        ret.slots = slots[:]
        ret.disps = disps[:]
        ret.power = power

        return ret

    @classmethod
    def ATROPOS_XR(cls: Type[T], rom: bytearray) -> T:
        return cls.generic_one_spot(rom, EnemyID.ATROPOS_XR, 3, 20)

    @classmethod
    def DALTON_PLUS(cls: Type[T], rom: bytearray) -> T:
        return cls.generic_one_spot(rom, EnemyID.DALTON_PLUS, 3, 30)

    # Note to self: Extra grinder objects at end of script?
    @classmethod
    def DRAGON_TANK(cls: Type[T], rom: bytearray) -> T:
        ids = [EnemyID.DRAGON_TANK, EnemyID.TANK_HEAD, EnemyID.GRINDER]
        slots = [3, 9, 0xA]
        disps = [(0, 0), (0, 0), (0, 0)]
        power = 15

        return cls.generic_multi_spot(rom, ids, disps, slots, power)

    # Shell goes first for pushing on death's peak.  The first object will
    # be the static, pushable one.
    @classmethod
    def ELDER_SPAWN(cls: Type[T], rom: bytearray) -> T:
        ids = [EnemyID.ELDER_SPAWN_SHELL,
               EnemyID.ELDER_SPAWN_HEAD]
        slots = [3, 9]
        disps = [(0, 0), (-8, 1)]
        power = 30

        return cls.generic_multi_spot(rom, ids, disps, slots, power)

    @classmethod
    def FLEA(cls: Type[T], rom: bytearray) -> T:
        return cls.generic_one_spot(rom, EnemyID.FLEA, 7, 15)

    @classmethod
    def FLEA_PLUS(cls: Type[T], rom: bytearray) -> T:
        return cls.generic_one_spot(rom, EnemyID.FLEA_PLUS, 7, 20)

    # This does virtually nothing since guardian sprite is built into the
    # background.  Eventually replace with lavos versions?
    @classmethod
    def GUARDIAN(cls: Type[T], rom: bytearray) -> T:
        ids = [EnemyID.GUARDIAN, EnemyID.GUARDIAN_BIT,
               EnemyID.GUARDIAN_BIT]
        slots = [3, 7, 8]
        disps = [(0, 0), (-0x50, -0x98), (0x40, -0x98)]
        power = 15

        return cls.generic_multi_spot(rom, ids, disps, slots, power)

    @classmethod
    def GIGA_GAIA(cls: Type[T], rom: bytearray) -> T:
        ids = [EnemyID.GIGA_GAIA_HEAD, EnemyID.GIGA_GAIA_LEFT,
               EnemyID.GIGA_GAIA_RIGHT]
        slots = [6, 7, 9]
        disps = [(0, 0), (0x40, 0x30), (-0x40, 0x30)]
        power = 25

        return cls.generic_multi_spot(rom, ids, disps, slots, power)

    @classmethod
    def GIGA_MUTANT(cls: Type[T], rom: bytearray) -> T:
        ids = [EnemyID.GIGA_MUTANT_HEAD, EnemyID.GIGA_MUTANT_BOTTOM]
        slots = [3, 9]
        disps = [(0, 0), (0, 0)]
        power = 35

        return cls.generic_multi_spot(rom, ids, disps, slots, power)

    @classmethod
    def GOLEM(cls: Type[T], rom: bytearray) -> T:
        return cls.generic_one_spot(rom, EnemyID.GOLEM, 3, 20)

    @classmethod
    def GOLEM_BOSS(cls: Type[T], rom: bytearray) -> T:
        return cls.generic_one_spot(rom, EnemyID.GOLEM_BOSS, 3, 20)

    @classmethod
    def HECKRAN(cls: Type[T], rom: bytearray) -> T:
        return cls.generic_one_spot(rom, EnemyID.HECKRAN, 3, 12)

    # TODO: Check on this.  It should be the displacement is -8 but that
    #       doesn't work...sometimes?  It's weird.
    @classmethod
    def LAVOS_SPAWN(cls: Type[T], rom: bytearray) -> T:
        ids = [EnemyID.LAVOS_SPAWN_SHELL,
               EnemyID.LAVOS_SPAWN_HEAD]
        slots = [3, 9]
        disps = [(0, 0), (-0x7, 0)]
        power = 18
        return cls.generic_multi_spot(rom, ids, disps, slots, power)

    @classmethod
    def MASA_MUNE(cls: Type[T], rom: bytearray) -> T:
        return cls.generic_one_spot(rom, EnemyID.MASA_MUNE, 6, 15)

    @classmethod
    def MEGA_MUTANT(cls: Type[T], rom: bytearray) -> T:
        ids = [EnemyID.MEGA_MUTANT_HEAD,
               EnemyID.MEGA_MUTANT_BOTTOM]
        slots = [3, 7]
        disps = [(0, 0), (0, 0)]
        power = 30

        return cls.generic_multi_spot(rom, ids, disps, slots, power)

    # For own notes:  real screens are 0x20, 0x21, 0x22.  0x23 never shows
    @classmethod
    def MOTHER_BRAIN(cls: Type[T], rom: bytearray) -> T:
        ids = [EnemyID.MOTHERBRAIN,
               EnemyID.DISPLAY, EnemyID.DISPLAY, EnemyID.DISPLAY]
        slots = [3, 6, 7, 8]
        disps = [(0, 0), (-0x50, -0x1F), (-0x10, -0x2F), (0x40, -0x1F)]
        power = 25

        return cls.generic_multi_spot(rom, ids, disps, slots, power)

    @classmethod
    def NIZBEL(cls: Type[T], rom: bytearray) -> T:
        return cls.generic_one_spot(rom, EnemyID.NIZBEL, 3, 15)

    @classmethod
    def NIZBEL_II(cls: Type[T], rom: bytearray) -> T:
        return cls.generic_one_spot(rom, EnemyID.NIZBEL_II, 3, 18)

    @classmethod
    def RETINITE(cls: Type[T], rom: bytearray) -> T:
        ids = [EnemyID.RETINITE_EYE, EnemyID.RETINITE_TOP,
               EnemyID.RETINITE_BOTTOM]
        slots = [3, 9, 6]
        disps = [(0, 0), (0, -0x8), (0, 0x28)]
        power = 15

        return cls.generic_multi_spot(rom, ids, disps, slots, power)

    @classmethod
    def R_SERIES(cls: Type[T], rom: bytearray) -> T:
        ids = [EnemyID.R_SERIES, EnemyID.R_SERIES, EnemyID.R_SERIES,
               EnemyID.R_SERIES]
        slots = [3, 4, 7, 8]
        disps = [(0, 0), (0, 0x20), (0x20, 0), (0x20, 0x20)]  # maybe wrong
        power = 15

        return cls.generic_multi_spot(rom, ids, disps, slots, power)

    @classmethod
    def RUST_TYRANO(cls: Type[T], rom: bytearray) -> T:
        return cls.generic_one_spot(rom, EnemyID.RUST_TYRANO, 3, 15)

    @classmethod
    def SLASH_SWORD(cls: Type[T], rom: bytearray) -> T:
        return cls.generic_one_spot(rom, EnemyID.SLASH_SWORD, 3, 15)

    @classmethod
    def SUPER_SLASH(cls: Type[T], rom: bytearray) -> T:
        return cls.generic_one_spot(rom, EnemyID.SUPER_SLASH, 7, 20)

    @classmethod
    def SON_OF_SUN(cls: Type[T], rom: bytearray) -> T:
        ids = [EnemyID.SON_OF_SUN_EYE,
               EnemyID.SON_OF_SUN_FLAME,
               EnemyID.SON_OF_SUN_FLAME,
               EnemyID.SON_OF_SUN_FLAME,
               EnemyID.SON_OF_SUN_FLAME]
        slots = [3, 4, 5, 6, 7]
        disps = [(0, 0), (-0x20, 0), (0x20, 0), (-0x10, 0x10), (0x10, 0x10)]
        power = 18
        return cls.generic_multi_spot(rom, ids, disps, slots, power)

    @classmethod
    def TERRA_MUTANT(cls: Type[T], rom: bytearray) -> T:
        ids = [EnemyID.TERRA_MUTANT_HEAD, EnemyID.TERRA_MUTANT_BOTTOM]
        slots = [3, 9]
        disps = [(0, 0), (0, 0)]
        power = 35

        return cls.generic_multi_spot(rom, ids, disps, slots, power)

    @classmethod
    def TWIN_GOLEM(cls: Type[T], rom: bytearray) -> T:
        ids = [EnemyID.TWIN_GOLEM, EnemyID.TWIN_GOLEM]
        slots = [3, 6]
        disps = [(-20, 0), (20, 0)]
        power = 30
        return cls.generic_multi_spot(rom, ids, disps, slots, power)

    @classmethod
    def YAKRA(cls: Type[T], rom: bytearray) -> T:
        return cls.generic_one_spot(rom, EnemyID.YAKRA, 3, 5)

    @classmethod
    def YAKRA_XIII(cls: Type[T], rom: bytearray) -> T:
        return cls.generic_one_spot(rom, EnemyID.YAKRA_XIII, 3, 15)

    @classmethod
    def ZOMBOR(cls: Type[T], rom: bytearray) -> T:
        return cls.generic_multi_spot(rom,
                                      [EnemyID.ZOMBOR_TOP,
                                       EnemyID.ZOMBOR_BOTTOM],
                                      [(0, 0), (0, 0x20)],
                                      [9, 3],
                                      10)
# end Boss class


def get_default_boss_assignment():
    return {
        LocID.PRISON_CATWALKS: BossID.DRAGON_TANK,
        LocID.BLACK_OMEN_ELDER_SPAWN: BossID.ELDER_SPAWN,
        LocID.MAGUS_CASTLE_FLEA: BossID.FLEA,
        LocID.OZZIES_FORT_FLEA_PLUS: BossID.FLEA_PLUS,
        LocID.MT_WOE_SUMMIT: BossID.GIGA_GAIA,
        LocID.BLACK_OMEN_GIGA_MUTANT: BossID.GIGA_MUTANT,
        LocID.ZEAL_PALACE_THRONE_NIGHT: BossID.GOLEM,
        LocID.ARRIS_DOME: BossID.GUARDIAN,
        LocID.HECKRAN_CAVE_NEW: BossID.HECKRAN,
        LocID.DEATH_PEAK_GUARDIAN_SPAWN: BossID.LAVOS_SPAWN,
        LocID.CAVE_OF_MASAMUNE: BossID.MASA_MUNE,
        LocID.GENO_DOME_MAINFRAME: BossID.MOTHER_BRAIN,
        LocID.REPTITE_LAIR_AZALA_ROOM: BossID.NIZBEL,
        LocID.TYRANO_LAIR_NIZBEL: BossID.NIZBEL_2,
        LocID.SUNKEN_DESERT_DEVOURER: BossID.RETINITE,
        LocID.GIANTS_CLAW_TYRANO: BossID.RUST_TYRANO,
        LocID.MAGUS_CASTLE_SLASH: BossID.SLASH_SWORD,
        LocID.SUN_PALACE: BossID.SON_OF_SUN,
        LocID.OZZIES_FORT_SUPER_SLASH: BossID.SUPER_SLASH,
        LocID.BLACK_OMEN_TERRA_MUTANT: BossID.TERRA_MUTANT,
        LocID.OCEAN_PALACE_TWIN_GOLEM: BossID.TWIN_GOLEM,
        LocID.MANORIA_COMMAND: BossID.YAKRA,
        LocID.KINGS_TRIAL_NEW: BossID.YAKRA_XIII,
        LocID.ZENAN_BRIDGE: BossID.ZOMBOR
    }


# Associate BossID with the Boss data structure.
def get_boss_data_dict(rom: bytearray):
    return {
        BossID.ATROPOS_XR: LinearScaleBoss.ATROPOS_XR(rom),
        BossID.DALTON_PLUS: LinearScaleBoss.DALTON_PLUS(rom),
        BossID.DRAGON_TANK: LinearScaleBoss.DRAGON_TANK(rom),
        BossID.ELDER_SPAWN: LinearScaleBoss.ELDER_SPAWN(rom),
        BossID.FLEA: LinearScaleBoss.FLEA(rom),
        BossID.FLEA_PLUS: LinearScaleBoss.FLEA_PLUS(rom),
        BossID.GIGA_GAIA: LinearScaleBoss.GIGA_GAIA(rom),
        BossID.GIGA_MUTANT: LinearScaleBoss.GIGA_MUTANT(rom),
        BossID.GOLEM: LinearScaleBoss.GOLEM(rom),
        BossID.GOLEM_BOSS: LinearScaleBoss.GOLEM_BOSS(rom),
        BossID.GUARDIAN: LinearScaleBoss.GUARDIAN(rom),
        BossID.HECKRAN: LinearScaleBoss.HECKRAN(rom),
        BossID.LAVOS_SPAWN: LinearScaleBoss.LAVOS_SPAWN(rom),
        BossID.MASA_MUNE: LinearScaleBoss.MASA_MUNE(rom),
        BossID.MEGA_MUTANT: LinearScaleBoss.MEGA_MUTANT(rom),
        BossID.MOTHER_BRAIN: LinearScaleBoss.MOTHER_BRAIN(rom),
        BossID.NIZBEL: LinearScaleBoss.NIZBEL(rom),
        BossID.NIZBEL_2: LinearScaleBoss.NIZBEL_II(rom),
        BossID.RETINITE: LinearScaleBoss.RETINITE(rom),
        BossID.R_SERIES: LinearScaleBoss.R_SERIES(rom),
        BossID.RUST_TYRANO: LinearScaleBoss.RUST_TYRANO(rom),
        BossID.SLASH_SWORD: LinearScaleBoss.SLASH_SWORD(rom),
        BossID.SON_OF_SUN: LinearNoHPScaleBoss.SON_OF_SUN(rom),
        BossID.SUPER_SLASH: LinearScaleBoss.SUPER_SLASH(rom),
        BossID.TERRA_MUTANT: LinearScaleBoss.TERRA_MUTANT(rom),
        BossID.TWIN_GOLEM: LinearScaleBoss.TWIN_GOLEM(rom),
        BossID.YAKRA: LinearScaleBoss.YAKRA(rom),
        BossID.YAKRA_XIII: LinearScaleBoss.YAKRA_XIII(rom),
        BossID.ZOMBOR: LinearScaleBoss.ZOMBOR(rom)
    }


def linear_scale_stats(stats: EnemyStats,
                       from_power: int, to_power: int,
                       scale_hp: bool = True,
                       scale_level: bool = True,
                       scale_speed: bool = False,
                       scale_magic: bool = True,
                       scale_mdef: bool = False,
                       scale_offense: bool = True,
                       scale_defense: bool = False,
                       scale_xp: bool = True,
                       scale_gp: bool = True,
                       scale_tp: bool = True) -> EnemyStats:

    try:
        # rewrite x -> kx as x -> x + (k-1)x so that the second term can
        # be conditioned on the scale_stat variables
        scale_factor = to_power/from_power - 1
    except ZeroDivisionError:
        print('Warning: from_power == 0.  Not scaling')
        return stats

    base_stats = [stats.hp, stats.level, stats.speed, stats.magic,
                  stats.mdef, stats.offense, stats.defense, stats.xp,
                  stats.gp, stats.tp]
    is_scaled = [scale_hp, scale_level, scale_speed, scale_magic,
                 scale_mdef, scale_offense, scale_defense, scale_xp,
                 scale_gp, scale_tp]
    max_stats = [0xFFFF, 0xFF, 0x10, 0xFF, 0xFF, 0xFF, 0xFF, 0xFFFF,
                 0xFFFF, 0xFF]

    [hp, level, speed, magic, mdef, offense, defense, xp, gp, tp] = \
        [int(min(base_stats[i] + is_scaled[i]*base_stats[i]*scale_factor,
             max_stats[i]))
         for i in range(len(base_stats))]

    return replace(stats, hp=hp, level=level, speed=speed, magic=magic,
                   mdef=mdef, offense=offense, defense=defense, xp=xp,
                   gp=gp, tp=tp)


class LinearScaleBoss(Boss):

    def scale_relative_to(self, other: Boss):
        # All this really uses is the other boss's power
        # Arguably, the HP will be set based on the other boss_obj

        # print(f"from power = {self.power}")
        # print(f"to power = {other.power}")

        for i in range(len(self.stats)):
            print(self.power, other.power)
            self.stats[i] = linear_scale_stats(self.stats[i], self.power,
                                               other.power)

        # I don't think setting the power will do anything, but maybe if
        # boss scaling or some other boss scaling option comes in we'll want
        # to know the "real" power of the boss.
        self.power = other.power


class LinearNoHPScaleBoss(LinearScaleBoss):

    # Scale like a linear boss, but then reset the hps to default
    def scale_relative_to(self, other: Boss):
        part_hps = [x.hp for x in self.stats]
        LinearScaleBoss.scale_relative_to(self, other)

        # reset the hps
        for i in range(len(self.ids)):
            self.stats[i].hp = part_hps[i]
