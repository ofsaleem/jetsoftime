from __future__ import annotations

import copy

from byteops import to_little_endian
from collections.abc import Callable
from dataclasses import dataclass, replace
from freespace import FSWriteType
import random

# from ctdecompress import compress, decompress, get_compressed_length
from bossdata import Boss, BossScheme, LinearScaleBoss, LinearNoHPScaleBoss, \
    get_default_boss_assignment
from ctenums import LocID, BossID, EnemyID
from enemystats import EnemyStats
from ctevent import Event, free_event, get_loc_event_ptr
from ctrom import CTRom
from eventcommand import EventCommand as EC, get_command, FuncSync
from eventfunction import EventFunction as EF
# from eventscript import get_location_script, get_loc_event_ptr
from freespace import FreeSpace as FS
from mapmangler import LocExits, duplicate_heckran_map, duplicate_location_data

import randosettings as rset
import randoconfig as cfg


def no_scale(stat: int, from_power: int, to_power: int):
    return stat


def linear_scale(stat: int, from_power: int, to_power: int):
    return stat*to_power//from_power


# Original exponential scaling
def orig_exp_scale(stat: int, from_power, int, to_power: int):
    tier_diff = to_power - from_power

    exp_dict = {
        -3: 0.7,
        -2: 0.85,
        -1: 0.95,
        0: 1,
        1: 1.15,
        2: 1.25
    }

    if tier_diff < -3:
        exp = exp_dict[-3]
    elif tier_diff > 2:
        exp = exp_dict[2]

    return int(pow(stat, exp))


def no_scale_fn(stats: EnemyStats, from_power: int,
                to_power: int) -> EnemyStats:
    return stats


def linear_scale_fn(stats: EnemyStats, from_power: int,
                    to_power: int) -> EnemyStats:
    print(stats)
    base_stats = [stats.hp, stats.level, stats.magic, stats.offense,
                  stats.xp, stats.gp, stats.tp]
    max_stats = [0xFFFF, 0xFF, 0xFF, 0xF, 0xFFFF, 0xFFFF, 0xFF]
    [hp, level, magic, offense, xp, gp, tp] \
        = [min(base_stats[i]*(to_power/from_power), max_stats[i])
           for i in range(len(base_stats))]
    ret = EnemyStats(hp, level, stats.speed, magic, stats.mdef, offense,
                     stats.defense, xp, gp, tp)
    print(ret)
    return ret


def set_manoria_boss(ctrom: CTRom, boss: BossScheme):
    # 0xC6 is Yakra's map - Manoria Command
    loc_id = 0xC6

    boss_obj = 0xA
    first_x, first_y = 0x80, 0xA0

    set_generic_one_spot_boss(ctrom, boss, loc_id, boss_obj,
                              lambda s: s.get_function_end(0xA, 3) - 1,
                              first_x, first_y)


def set_denadoro_boss(ctrom: CTRom, boss: BossScheme):
    # 0x97 is M&M's map - Cave of the Masamune
    loc_id = 0x97
    boss_obj = 0x14

    first_x, first_y = 0x80, 0xE0

    set_generic_one_spot_boss(ctrom, boss, loc_id, boss_obj,
                              lambda s: s.get_function_end(0x14, 4) - 1,
                              first_x, first_y)


def set_reptite_lair_boss(ctrom: CTRom, boss: BossScheme):
    # 0x121 is Nizbel's map - Reptite Lair Azala's Room
    loc_id = 0x121
    boss_obj = 0x9

    first_x, first_y = 0x370, 0xC0

    set_generic_one_spot_boss(ctrom, boss, loc_id, boss_obj,
                              lambda s: s.get_function_end(0x9, 4) - 1,
                              first_x, first_y)


def set_magus_castle_flea_spot_boss(ctrom: CTRom, boss: BossScheme):
    # 0xAD is Flea's map - Castle Magus Throne of Magic
    loc_id = 0xAD

    boss_obj = 0xC

    first_x, first_y = 0x70, 0x150

    def show_pos_fn(script: Event) -> int:
        # The location to insert is a bit before the second battle in this
        # function.  The easiest marker is a 'Mem.7F020C = 01' command.
        # In bytes it is '7506'
        pos = script.find_exact_command(EC.generic_one_arg(0x75, 0x06),
                                        script.get_function_start(0xC, 0))

        if pos is None:
            print("Error finding show pos (flea spot)")
            exit()

        return pos
    # end show_pos_fn

    set_generic_one_spot_boss(ctrom, boss, loc_id, boss_obj, show_pos_fn,
                              first_x, first_y)
# End set_magus_castle_flea_spot_boss


def set_magus_castle_slash_spot_boss(ctrom: CTRom, boss: BossScheme):
    # 0xA9 is Slash's map - Castle Magus Throne of Strength
    loc_id = 0xA9
    script = ctrom.script_manager.get_script(loc_id)

    if boss.ids[0] in [EnemyID.ELDER_SPAWN_SHELL, EnemyID.LAVOS_SPAWN_SHELL]:
        # Some sprite issue with overlapping slots?
        # If the shell is the static part, it will be invisible until it is
        # interacted with.
        boss.ids[0], boss.ids[1] = boss.ids[1], boss.ids[0]
        boss.slots[0], boss.slots[1] = boss.slots[1], boss.slots[0]
        boss.disps[0] = (-boss.disps[0][0], -boss.disps[0][1])
        boss.disps[1] = (-boss.disps[1][0], -boss.disps[1][1])

    # Slash's spot is ugly because there's a second Slash object that's used
    # for one of the endings (I think?).  You really have to set both of them
    # to the boss you want, otherwise you're highly likely to hit graphics
    # limits.
    set_object_boss(script, 0xC, boss.ids[0], boss.slots[0])

    # The real, used Slash is in object 0xB.
    boss_obj = 0xB

    first_x, first_y = 0x80, 0x240

    def show_pos_fn(script: Event) -> int:
        pos = script.find_exact_command(EC.generic_one_arg(0xE8, 0x8D),
                                        script.get_function_start(0xB, 1))

        if pos is None:
            print("Failed to find show pos (slash spot)")
            exit()

        return pos

    set_generic_one_spot_boss_script(script, boss, boss_obj,
                                     show_pos_fn, first_x, first_y)
# End set_magus_castle_slash_spot_boss


def set_giants_claw_boss(ctrom: CTRom, boss: BossScheme):
    # 0xC5 is the Rust Tyrano's map - Giant's Claw Last Tyrano
    loc_id = 0xC5

    # First part is in object 0x9, function 0 (init)
    boss_obj = 0x9

    first_x, first_y = 0x80, 0x27F

    # Objects can start out shown, no real need for show_pos_fn
    set_generic_one_spot_boss(ctrom, boss, loc_id, boss_obj,
                              lambda s: s.get_function_start(0, 0) + 1,
                              first_x, first_y, True)
# end set giant's claw boss


def set_tyrano_lair_midboss(ctrom: CTRom, boss: BossScheme):
    # 0x130 is the Nizbel II's map - Tyrano Lair Nizbel's Room
    loc_id = 0x130
    boss_obj = 0x8
    first_x = 0x70
    first_y = 0xD0

    set_generic_one_spot_boss(ctrom, boss, loc_id, boss_obj,
                              lambda s: s.get_function_end(8, 3) - 1,
                              first_x, first_y)
# end set_tyrano_lair_midboss


def set_zeal_palace_boss(ctrom: CTRom, boss: BossScheme):
    # 0x14E is the Golem's map - Zeal Palace's Throneroom (Night)
    # Note this is different from vanilla, where it's 0x14C
    loc_id = 0x14E
    script = ctrom.script_manager.get_script(loc_id)

    # So much easier to just manually set the coordinates than parse
    # the script for them.  This is after the golem comes down.
    first_x = 0x170
    first_y = 0x90

    # First, let's delete some objects to avoid sprite limits.
    #   - Object F: Schala
    #   - Object E: Queen Zeal
    #   - Object 10: Magus Prophet

    # reverse order to not screw things up
    # removing seems to mess up the color of the beam above the portal.
    # I think it's the colormath commands needing palettes loaded?
    # For now, see if just leaving the junk in is ok.
    # del_objs = [0x10, 0xF, 0xE]

    # for obj in del_objs:
    #     script.remove_object(obj)

    # After deletion, the boss object is 0xA (unmoved)
    boss_obj = 0xA

    def show_pos_fn(script: Event) -> int:
        # Right after the golem comes down to its final position.  The marker
        # is a play anim 5 command 'AA 05'
        pos = script.find_exact_command(EC.generic_one_arg(0xAA, 0x5),
                                        script.get_function_start(0xA, 3))

        if pos is None:
            print('Error finding show pos (zeal palace)')
            exit()

        return pos

    set_generic_one_spot_boss_script(script, boss, boss_obj,
                                     show_pos_fn,
                                     first_x, first_y)


# Two spot locations follow the same general procedure:
#   - For a 1-spot boss, overwrite the legs object (0xB3 for Zombor) with the
#     new boss id.  Then delete the head object and all references to it.
#   - For a 2-spot boss, overwrite the legs and head object with the new
#     boss ids.  Add in coordinate shifts (will vary with location).
#     Possibly it's easier to delete all but one object and then
#   - For a 3+ spot boss, do the 2-spot procedure and then add new objects
#     that pop into existence right
def set_zenan_bridge_boss(ctrom: CTRom, boss: BossScheme):
    # 0x87 is Zombor's map - Zenan Bridge (Middle Ages)
    loc_id = 0x87
    script = ctrom.script_manager.get_script(loc_id)

    num_parts = len(boss.ids)

    if num_parts == 1:
        # Use object 0xB (Zombor's Head, 0xB4) for the boss because it has
        # sound effects in it.  But we'll change the coordinates so that the
        # boss will be on the ground

        # Zombor has an attract battle scene.  So we skip over the conditionals
        pos = script.get_function_start(0xB, 0)
        found_boss = False
        found_coord = False

        first_x, first_y = 0xE0, 0x80
        first_id, first_slot = boss.ids[0], boss.slots[0]

        while pos < script.get_function_end(0xB, 0):
            cmd = get_command(script.data, pos)

            print(cmd)
            if cmd.command in EC.fwd_jump_commands:
                pos += (cmd.args[-1] - 1)
            elif cmd.command == 0x83:
                found_boss = True
                cmd.args[0] = first_id
                cmd.args[1] = first_slot
                script.data[pos:pos+len(cmd)] = cmd.to_bytearray()
            elif cmd.command == 0x8B:
                found_coord = True
                # This is only safe because we know it will give the tile
                # based command to perfectly overwrite the existing tile based
                # command.
                cmd = EC.set_object_coordinates(first_x, first_y)
                script.data[pos:pos+len(cmd)] = cmd.to_bytearray()

            pos += len(cmd)

        if not found_boss or not found_coord:
            print(f"Error: found boss({found_boss}), " +
                  f"found coord({found_coord})")
            exit()

        # Delete the other Zombor object (0xC) to save memory.  It might be
        # OK to leave it in, set it to the one-spot boss, and delete all
        # references as we do below.
        script.remove_object(0xC)

    # end 1 part

    if num_parts > 1:
        first_x, first_y = 0xE0, 0x60

        # object to overwrite with new boss ids and coords
        reused_objs = [0xB, 0xC]

        for i in [0, 1]:
            new_x = first_x + boss.disps[i][0]
            new_y = first_y + boss.disps[i][1]

            # print(f"({new_x:04X}, {new_y:04X})")
            # input()
            new_id = boss.ids[i]
            new_slot = boss.slots[i]

            set_object_boss(script, reused_objs[i], new_id, new_slot)
            set_object_coordinates(script, reused_objs[i], new_x, new_y)

        show_cmds = bytearray()
        for i in range(2, len(boss.ids)):
            new_obj = append_boss_object(script, boss, i,
                                         first_x, first_y, False)
            show = EC.set_object_drawing_status(new_obj, True)
            show_cmds.extend(show.to_bytearray())

        # Suitable time for them to appear is right after the first two parts'
        # entrance.  The very end of obj C, activate (1), before the return
        ins_pos = script.get_function_end(0xC, 1) - 1
        script.insert_commands(show_cmds, ins_pos)
    # end multi-part


def set_death_peak_boss(ctrom: CTRom, boss: BossScheme):
    # 0x1EF is the Lavos Spawn's map - Death Peak Guardian Spawn
    loc_id = 0x1EF
    script = ctrom.script_manager.get_script(loc_id)

    # The shell is important since it needs to stick around after battle.
    # It is in object 9, and the head is in object 0xA
    boss_objs = [0x9, 0xA]

    num_used = min(len(boss.ids), 2)

    first_x, first_y = 0x70, 0xC0

    for i in range(num_used):
        boss_id = boss.ids[i]
        boss_slot = boss.slots[i]

        new_x = first_x + boss.disps[i][0]
        new_y = first_y + boss.disps[i][1]
        set_object_boss(script, boss_objs[i], boss_id, boss_slot)
        set_object_coordinates(script, boss_objs[i], new_x, new_y)

    # Remove unused boss objects from the original script.
    # Will do nothing unless there are fewer boss ids provided than there
    # are original boss objects
    for i in range(len(boss.ids), len(boss_objs)):
        script.remove_object(boss_objs[i])

    # For every object exceeding the count in this map, make a new object.
    # For this particular map, we're going to copy the object except for
    # the enemy load/coords
    calls = bytearray()

    for i in range(len(boss_objs), len(boss.ids)):
        obj_id = script.append_copy_object(0xA)

        new_x = first_x + boss.disps[i][0]
        new_y = first_y + boss.disps[i][1]

        set_object_boss(script, obj_id, boss.ids[i], boss.slots[i])
        set_object_coordinates(script, obj_id, new_x, new_y)

        call = EC.call_obj_function(obj_id, 3, 3, FuncSync.CONT)
        calls.extend(call.to_bytearray())

    # Insertion point is right before the first Move Party command (0xD9)
    pos, cmd = script.find_command([0xD9],
                                   script.get_function_start(8, 1),
                                   script.get_function_end(8, 1))

    if pos is None:
        print('Error finding insertion point.')
        exit()

    script.insert_commands(calls, pos)


def set_giga_mutant_spot_boss(ctrom: CTRom, boss: BossScheme):
    # 0x143 is the Giga Mutant's map - Black Omen 63F Divine Guardian
    loc_id = 0x143
    script = ctrom.script_manager.get_script(loc_id)

    boss_objs = [0xE, 0xF]

    num_used = min(len(boss.ids), 2)
    first_x, first_y = 0x278, 0x1A0

    # mutant coords are weird.  The coordinates are the bottom of the mutant's
    # bottom part.  We need to shift up so non-mutants aren't on the party.
    if boss.ids[0] not in [EnemyID.GIGA_MUTANT_HEAD,
                           EnemyID.GIGA_MUTANT_BOTTOM,
                           EnemyID.TERRA_MUTANT_HEAD,
                           EnemyID.TERRA_MUTANT_BOTTOM,
                           EnemyID.MEGA_MUTANT_HEAD,
                           EnemyID.MEGA_MUTANT_BOTTOM]:
        first_y -= 0x20

    # overwrite as many boss objects as possible
    for i in range(num_used):
        boss_id = boss.ids[i]
        boss_slot = boss.slots[i]

        new_x = first_x + boss.disps[i][0]
        new_y = first_y + boss.disps[i][1]

        set_object_boss(script, boss_objs[i], boss_id, boss_slot)
        set_object_coordinates(script, boss_objs[i], new_x, new_y)

    # Remove unused boss objects.
    for i in range(len(boss.ids), len(boss_objs)):
        script.remove_object(boss_objs[i])

    # Add more boss objects if needed
    calls = bytearray()
    for i in range(len(boss_objs), len(boss.ids)):
        obj_id = script.append_copy_object(boss_objs[1])

        new_x = first_x + boss.disps[i][0]
        new_y = first_y + boss.disps[i][1]

        set_object_boss(script, obj_id, boss.ids[i], boss.slots[i])
        set_object_coordinates(script, obj_id, new_x, new_y)

        # mimic call of other objects
        call = EC.call_obj_function(obj_id, 3, 3, FuncSync.CONT)
        calls.extend(call.to_bytearray())

    # Insertion point is right after call_obj_function(0xE, touch, 3, cont)
    ins_cmd = EC.call_obj_function(0xE, 2, 3, FuncSync.CONT)
    # print(f"{ins_cmd.command:02X}" + str(ins_cmd))

    pos = script.find_exact_command(ins_cmd,
                                    script.get_function_start(0xA, 1),
                                    script.get_function_end(0xA, 1))
    if pos is None:
        print("Error finding insertion position (giga mutant)")
        exit()
    else:
        # shift to after the found command
        pos += len(ins_cmd)

    script.insert_commands(calls, pos)

    # This script is organized as a bunch of call(...., cont) with a terminal
    # call(...., halt).  We may have deleted the halting one, so just make sure
    # the last call is a halt
    script.data[pos + len(calls) - len(ins_cmd)] = 0x4  # Call w/ halt


def set_terra_mutant_spot_boss(ctrom: CTRom, boss: BossScheme):
    # 0x145 is the Terra Mutant's map - Black Omen 98F Astral Guardian
    loc_id = 0x145
    script = ctrom.script_manager.get_script(loc_id)

    boss_objs = [0xF, 0x10]

    num_used = min(len(boss.ids), 2)
    first_x, first_y = 0x70, 0x80

    # mutant coords are weird.  The coordinates are the bottom of the mutant's
    # bottom part.  We need to shift up so non-mutants aren't on the party.
    if boss.ids[0] not in [EnemyID.GIGA_MUTANT_HEAD,
                           EnemyID.GIGA_MUTANT_BOTTOM,
                           EnemyID.TERRA_MUTANT_HEAD,
                           EnemyID.TERRA_MUTANT_BOTTOM,
                           EnemyID.MEGA_MUTANT_HEAD,
                           EnemyID.MEGA_MUTANT_BOTTOM]:
        first_y -= 0x20

    for i in range(num_used):
        boss_id = boss.ids[i]
        boss_slot = boss.slots[i]

        new_x = first_x + boss.disps[i][0]
        new_y = first_y + boss.disps[i][1]

        set_object_boss(script, boss_objs[i], boss_id, boss_slot)
        set_object_coordinates(script, boss_objs[i], new_x, new_y)

    # Remove unused boss objects.
    for i in range(len(boss.ids), len(boss_objs)):
        script.remove_object(boss_objs[i])

    # Add more boss objects if needed
    calls = bytearray()
    for i in range(len(boss_objs), len(boss.ids)):
        obj_id = script.append_copy_object(boss_objs[1])

        new_x = first_x + boss.disps[i][0]
        new_y = first_y + boss.disps[i][1]

        set_object_boss(script, obj_id, boss.ids[i], boss.slots[i])
        set_object_coordinates(script, obj_id, new_x, new_y)

        # mimic call of other objects
        call = EC.call_obj_function(obj_id, 3, 1, FuncSync.SYNC)
        calls.extend(call.to_bytearray())

    # Insertion point is right after call_obj_function(0xF, arb0, 1, sync)
    ins_cmd = EC.call_obj_function(0xF, 3, 1, FuncSync.SYNC)

    pos = script.find_exact_command(ins_cmd,
                                    script.get_function_start(8, 1))
    if pos is None:
        print("Error finding insertion position (terra mutant)")
        exit()
    else:
        pos += len(ins_cmd)

    script.insert_commands(calls, pos)


def set_elder_spawn_spot_boss(ctrom: CTRom, boss: BossScheme):
    # 0x60 is the Elder Spawn's map - Black Omen 98F Astral Progeny
    loc_id = 0x60
    script = ctrom.script_manager.get_script(loc_id)

    boss_objs = [0x8, 0x9]

    num_used = min(len(boss.ids), 2)
    first_x, first_y = 0x170, 0xB2

    # overwrite as many boss objects as possible
    for i in range(num_used):
        boss_id = boss.ids[i]
        boss_slot = boss.slots[i]

        new_x = first_x + boss.disps[i][0]
        new_y = first_y + boss.disps[i][1]

        set_object_boss(script, boss_objs[i], boss_id, boss_slot)
        # The coordinate setting is in activate for whatever reason.
        set_object_coordinates(script, boss_objs[i], new_x, new_y, True, 1)

    # Remove unused boss objects.
    for i in range(len(boss.ids), len(boss_objs)):
        script.remove_object(boss_objs[i])

    # Add more boss objects if needed
    calls = bytearray()
    for i in range(len(boss_objs), len(boss.ids)):
        obj_id = script.append_copy_object(boss_objs[1])

        new_x = first_x + boss.disps[i][0]
        new_y = first_y + boss.disps[i][1]

        set_object_boss(script, obj_id, boss.ids[i], boss.slots[i])
        # The coordinate setting is in activate for whatever reason.
        set_object_coordinates(script, obj_id, new_x, new_y, True,
                               fn_id=1)

        # mimic call of other objects
        call = EC.call_obj_function(obj_id, 2, 6, FuncSync.CONT)
        calls.extend(call.to_bytearray())

    # Insertion point is right before call_obj_function(0x8, touch, 6, cont)
    ins_cmd = EC.call_obj_function(0x8, 2, 6, FuncSync.CONT)

    pos = script.find_exact_command(ins_cmd,
                                    script.get_function_start(0, 0))

    if pos is None:
        print("Error finding insertion point (elder spawn)")
        exit()
    else:
        pos += len(ins_cmd)

    script.insert_commands(calls, pos)


def set_heckrans_cave_boss(ctrom: CTRom, boss: BossScheme):

    # Heckran is in 0xC0 now.
    loc_id = 0xC0

    boss_obj = 0xA
    first_x, first_y = 0x340, 0x190

    set_generic_one_spot_boss(ctrom, boss, loc_id, boss_obj,
                              lambda scr: scr.get_function_end(0xA, 1)-1,
                              first_x, first_y)


def set_kings_trial_boss(ctrom: CTRom, boss: BossScheme):
    # Yakra XIII is in 0xC1 now.
    loc_id = 0xC1
    boss_obj = 0xB
    first_x, first_y = 0x40, 0x100

    # show spot is right at the end of obj 0xB, arb 0
    set_generic_one_spot_boss(ctrom, boss, loc_id, boss_obj,
                              lambda scr: scr.get_function_end(0xB, 3)-1,
                              first_x, first_y)


def set_ozzies_fort_flea_plus_spot_boss(ctrom: CTRom, boss: BossScheme):
    loc_id = 0xB7
    boss_obj = 0x9
    first_x, first_y = 0x270, 0x250

    # show spot is right at the end of obj 0xB, arb 0
    # This one is different since we're adding at the start of a function.
    # Need to double check that the routines are setting start/end correctly
    set_generic_one_spot_boss(ctrom, boss, loc_id, boss_obj,
                              lambda scr: scr.get_function_start(0x9, 1),
                              False, first_x, first_y)


def set_ozzies_fort_super_slash_spot_boss(ctrom: CTRom, boss: BossScheme):
    loc_id = 0xB8
    script = ctrom.script_manager.get_script(loc_id)

    boss_obj = 0x9
    first_x, first_y = 0x270, 0x250

    # show spot is right at the end of obj 0xB, arb 0
    # This one is different since we're adding at the start of a function.
    # Need to double check that the routines are setting start/end correctly
    set_generic_one_spot_boss(ctrom, boss, loc_id, boss_obj,
                              lambda scr: scr.get_function_start(0x9, 1),
                              False, first_x, first_y)


def set_sun_palace_boss(ctrom: CTRom, boss: BossScheme):
    # 0xFB is Son of Sun's map - Sun Palace
    loc_id = 0xFB
    script = ctrom.script_manager.get_script(loc_id)

    # Eyeball in 0xB and rest are flames. 0x10 is hidden in rando.
    # Really, 0x10 should just be removed from the start.
    script.remove_object(0x10)

    boss_objs = [0xB, 0xC, 0xD, 0xE, 0xF]
    num_used = min(len(boss.ids), 2)

    # After the ambush
    first_x, first_y = 0x100, 0x1B0

    # overwrite as many boss objects as possible
    for i in range(num_used):
        boss_id = boss.ids[i]
        boss_slot = boss.slots[i]

        new_x = first_x + boss.disps[i][0]
        new_y = first_y + boss.disps[i][1]

        set_object_boss(script, boss_objs[i], boss_id, boss_slot)
        set_object_coordinates(script, boss_objs[i], new_x, new_y, True)

        if i == 0:
            # SoS is weird about the first part moving before the rest are
            # visible.  So the rest will pop in relative to these coords
            first_x, first_y = 0x100, 0x200

    # Remove unused boss objects.  In reverse order of course.
    for i in range(len(boss_objs), len(boss.ids), -1):
        script.remove_object(boss_objs[i-1])

    # Add more boss objects if needed.  This will never happen for vanilla
    # Son of Sun, but maybe if scaling adds flames?

    calls = bytearray()
    for i in range(len(boss_objs), len(boss.ids)):
        obj_id = script.append_copy_object(boss_objs[1])

        new_x = first_x + boss.disps[i][0]
        new_y = first_y + boss.disps[i][1]

        set_object_boss(script, obj_id, boss.ids[i], boss.slots[i])
        # The coordinate setting is in init
        set_object_coordinates(script, obj_id, new_x, new_y, True)

        # mimic call of other objects
        call = EF()
        if i == len(boss.ids)-1:
            call.add(EC.call_obj_function(obj_id, 1, FuncSync.SYNC))
        else:
            call.add(EC.call_obj_function(obj_id, 1, FuncSync.HALT))

        call.add(EC.generic_one_arg(0xAD, 0x01))
        calls.extend(call.get_bytearray())

    # Insertion point is before the pause before Animate 0x1.
    ins_cmd = EC.generic_one_arg(0xAA, 0x01)

    # In the eyeball's (0xB) arb 1
    pos = script.find_exact_command(ins_cmd,
                                    script.get_function_start(0xB, 4))

    if pos is None:
        print("Error: Couldn't find insertion point (SoS)")
        exit()
    else:
        pos -= (len(ins_cmd) + 2)  # +2 for the pause command prior

    script.insert_commands(calls, pos)


def set_desert_boss(ctrom: CTRom, boss: BossScheme):
    # 0xA1 is Retinite's map - Sunken Desert Devourer
    loc_id = 0xA1
    script = ctrom.script_manager.get_script(loc_id)

    boss_objs = [0xE, 0xF, 0x10]

    # Extra copies of retinite bottom for the vanilla random location
    # There are some blank objects that can be removed, but will not do so.
    del_objs = [0x12, 0x11]
    for x in del_objs:
        script.remove_object(x)

    num_used = min(len(boss.ids), 2)
    first_x, first_y = 0x120, 0xC9

    # overwrite as many boss objects as possible
    for i in range(num_used):
        boss_id = boss.ids[i]
        boss_slot = boss.slots[i]

        new_x = first_x + boss.disps[i][0]
        new_y = first_y + boss.disps[i][1]

        set_object_boss(script, boss_objs[i], boss_id, boss_slot)
        # The coordinate setting is in arb0 for whatever reason.
        set_object_coordinates(script, boss_objs[i], new_x, new_y, True, 4)

    # Remove unused boss objects.  In reverse order of course.
    for i in range(len(boss_objs), len(boss.ids), -1):
        script.remove_object(boss_objs[i-1])

    # Add more boss objects if needed.
    calls = bytearray()
    for i in range(len(boss_objs), len(boss.ids)):
        obj_id = script.append_copy_object(boss_objs[1])

        new_x = first_x + boss.disps[i][0]
        new_y = first_y + boss.disps[i][1]

        set_object_boss(script, obj_id, boss.ids[i], boss.slots[i])
        # The coordinate setting is in arb0
        set_object_coordinates(script, obj_id, new_x, new_y, True,
                               fn_id=4)

        # mimic call of other objects
        call = EC.call_obj_function(obj_id, 4, 0, FuncSync.SYNC)

        calls.extend(call.to_bytearray())

    # Insertion point is before the pause before Calling obj 0xE, arb 1
    ins_cmd = EC.call_obj_function(0xE, 4, 2, FuncSync.HALT)

    # In the eyeball's (0xB) arb 1
    pos = script.find_exact_command(ins_cmd,
                                    script.get_function_start(0x2, 0))

    if pos is None:
        print("Error: Couldn't find insertion point (SoS)")
        exit()
    else:
        pos -= len(ins_cmd)

    script.insert_commands(calls, pos)


def set_twin_golem_spot(ctrom: CTRom, boss: BossScheme):
    # This one is unique because it actually depends on the size of the boss.
    # One spot bosses will be duplicated and others will just appear as-is.

    # 0x19E is the Twin Golems' map - Ocean Palace Regal Antechamber
    loc_id = 0x19E
    script = ctrom.script_manager.get_script(loc_id)

    if len(boss.ids) == 1:
        # Turn the one spot boss into a two spot copy
        # The only difficulty is that you need a new slot for the copy

        if boss.slots[0] == 3:
            new_slot = 9
        else:
            new_slot = 3

        boss.ids.append(boss.ids[0])
        boss.disps.append((40, 0))
        boss.slots.append(new_slot)

        first_x, first_y = 0x60, 0xE0
    else:
        # Somewhat center the multi_spot boss
        # 1) Change the move command to have an x-coord of 0x80 + display
        # Only twin golem has a displacement on its first part though.
        move_cmd = EC.generic_two_arg(0x96, 0x6, 0xE)
        pos = script.find_exact_command(move_cmd,
                                        script.get_function_start(0xA, 3))

        first_x = 0x80
        first_y = 0xE0

        # Move command is given in tile coords, so >> 4
        new_x = (first_x + boss.disps[0][0] >> 4)
        new_y = (first_y + boss.disps[0][1] >> 4)
        script.data[pos+1] = new_x

        # Back to pixels for set coords
        new_x = new_x << 4
        new_y = new_y << 4

        # 2) Change the following set coords command to the dest of the move
        coord_cmd = EC.set_object_coordinates(new_x, new_y)

        pos += len(move_cmd)
        script.data[pos:pos+len(coord_cmd)] = coord_cmd.to_bytearray()

    # Now proceed with a normal multi-spot assignment
    boss_objs = [0xA, 0xB]

    # overwrite the boss objs
    for i in range(0, 2):
        set_object_boss(script, boss_objs[i], boss.ids[i], boss.slots[i])

        new_x = first_x + boss.disps[i][0]
        new_y = first_y + boss.disps[i][1]

        # first object's coordinates don't matter.  Second is set in arb0
        if i != 0:
            set_object_coordinates(script, boss_objs[i], new_x, new_y,
                                   True, 3)

    # Add as many new ones as needed.  Slight modification of one spot stuff

    show = EF()
    for i in range(2, len(boss.ids)):
        new_obj = append_boss_object(script, boss, i, first_x, first_y,
                                     False)
        show.add(EC.set_object_drawing_status(new_obj, True))

    # Show after part 2 shows up.
    show_pos = script.get_function_end(0xB, 4) - 1
    script.insert_commands(show.get_bytearray(), show_pos)


# set_generic_one_spot_boss should be able to set any one spot location's boss
# with a little help
#       ctrom: has the script manager to get scripts from
#      loc_id: The id of the location to write to (not the location event id)
#    boss_obj: An object of type Boss holding the desired boss
# show_pos_fn: A function to determine how to find the insertion point after
#              the objects have been added.
#   is_static: Is the boss static?  In other words, does it stick around after
#              the battle to do something.
#     first_x: The x-coordinate of the boss when show_pos is hit.  This should
#              be after all movement is done.
#     first_y: The same as first_x but for the y_coordinate
#    is_shown: Should the boss be shown by default.  Usually this is False.
def set_generic_one_spot_boss(ctrom: CTRom,
                              boss: BossScheme,
                              loc_id: int,
                              boss_obj: int,
                              show_pos_fn: Callable[[Event], int],
                              first_x: int = None,
                              first_y: int = None,
                              is_shown: bool = False):

    script_manager = ctrom.script_manager
    script = script_manager.get_script(loc_id)

    set_generic_one_spot_boss_script(script, boss, boss_obj,
                                     show_pos_fn, first_x, first_y, is_shown)


# This is exactly like the above except that the user provides the script.
# This is needed in some cases when there is preprocessing required before
# Following the general procedure.
def set_generic_one_spot_boss_script(script: Event,
                                     boss: BossScheme,
                                     boss_obj: int,
                                     show_pos_fn: Callable[[Event], int],
                                     first_x: int = None,
                                     first_y: int = None,
                                     is_shown: bool = False):

    first_id = boss.ids[0]
    first_slot = boss.slots[0]

    set_object_boss(script, boss_obj, first_id, first_slot)

    show = EF()

    for i in range(1, len(boss.ids)):
        new_obj = append_boss_object(script, boss, i,
                                     first_x, first_y,
                                     is_shown)
        show.add(EC.set_object_drawing_status(new_obj, True))

    # If a boss starts out shown, no need to insert commands
    if not is_shown:
        # script.print_fn_starts()
        show_pos = show_pos_fn(script)
        # print(f"{show_pos:04X}")
        # input()
        script.insert_commands(show.get_bytearray(), show_pos)


def set_object_boss(script: Event, obj_id: int, boss_id: int, boss_slot: int,
                    ignore_jumps: bool = True):

    start = script.get_object_start(obj_id)
    end = script.get_function_end(obj_id, 0)

    pos = start
    while pos < end:

        cmd = get_command(script.data, pos)

        if cmd.command in EC.fwd_jump_commands and ignore_jumps:
            pos += (cmd.args[-1] - 1)
        elif cmd.command == 0x83:
            is_static = cmd.args[1] & 0x80
            cmd.args[0], cmd.args[1] = boss_id, (boss_slot | is_static)
            script.data[pos:pos+len(cmd)] = cmd.to_bytearray()
            break

        pos += len(cmd)


def set_object_coordinates(script: Event, obj_id: int, x: int, y: int,
                           ignore_jumps: bool = True, fn_id: int = 0):

    start = script.get_function_start(obj_id, fn_id)
    end = script.get_function_end(obj_id, fn_id)

    pos = start
    while pos < end:

        cmd = get_command(script.data, pos)

        if cmd.command in EC.fwd_jump_commands and ignore_jumps:
            pos += (cmd.args[-1] - 1)
        elif cmd.command in [0x8B, 0x8D]:
            new_coord_cmd = EC.set_object_coordinates(x, y)

            # The pixel-based and tile-based commands have different lengths.
            # If the new coordinates don't match the old, you have to do a
            # delete/insert.
            if new_coord_cmd.command == cmd.command:
                script.data[pos:pos+len(new_coord_cmd)] = \
                    new_coord_cmd.to_bytearray()
            else:
                script.delete_commands(pos, 1)
                script.insert_commands(new_coord_cmd.to_bytearray(), pos)

            break

        pos += len(cmd)


# Make a barebones object to make a boss part and hide it.
def append_boss_object(script: Event, boss: BossScheme, part_index: int,
                       first_x: int, first_y: int,
                       is_shown: bool = False) -> int:

    new_id = boss.ids[part_index]
    new_slot = boss.slots[part_index]

    # Pray these don't come up negative.  They shouldn't?
    new_x = first_x + boss.disps[part_index][0]
    new_y = first_y + boss.disps[part_index][1]

    # print(f"({first_x:04X}, {first_y:04X})")
    # print(f"({new_x:04X}, {new_y:04X})")
    # input()

    print(EC.set_object_coordinates(new_x, new_y))
    # print(' '.join(f"{x:02X}"
    #                for x in
    #                EC.set_object_coordinates(new_x, new_y).to_bytearray()))
    # input()

    # Make the new object
    init = EF()
    init.add(EC.load_enemy(new_id, new_slot)) \
        .add(EC.set_object_coordinates(new_x, new_y)) \
        .add(EC.set_own_drawing_status(is_shown)) \
        .add(EC.return_cmd()) \
        .add(EC.end_cmd())

    act = EF()
    act.add(EC.return_cmd())

    obj_id = script.append_empty_object()
    script.set_function(obj_id, 0, init)
    script.set_function(obj_id, 1, act)

    return obj_id


# Duplicate maps which run into sprite limits for boss rando
def duplicate_maps(fsrom: FS):

    exits = LocExits.from_rom(fsrom)
    duplicate_heckran_map(fsrom, exits, 0xC0)
    exits.write_to_fsrom(fsrom)

    # While we're here let's clean up the script.  Separate that from the
    # boss randomization part.

    # Notes for Hecrkan editing:
    #   - Remove 1, 2, 0xC, 0xE, 0xF, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16,
    #         0x17, 0x18
    #   - Heckran's object was 0xD, now 0xA (3 removed prior)
    #   - Can clean up object 0 because it controls multiple encounters, but
    #     There's no real value to doing so.

    loc_id = 0x2F  # Orig Heckran location id
    loc_ptr = get_loc_event_ptr(fsrom.getbuffer(), loc_id)
    script = Event.from_rom(fsrom.getbuffer(), loc_ptr)

    del_objs = [0x18, 0x17, 0x16, 0x15, 0x14, 0x13, 0x12, 0x11, 0x10, 0xF,
                0xE, 0xC, 2, 1]
    for x in del_objs:
        script.remove_object(x)

    free_event(fsrom, 0xC0)  # New Heckran location id
    Event.write_to_rom_fs(fsrom, 0xC0, script)

    # Now do King's Trial
    #   - In location 0x1B9 (Courtroom Lobby) change the ChangeLocation
    #     command of Obj8, Activate.  It's after a 'If Marle in party' command.

    loc_id = 0x1B9
    loc_ptr = get_loc_event_ptr(fsrom.getbuffer(), loc_id)
    script = Event.from_rom(fsrom.getbuffer(), loc_ptr)

    # Find the if Marle is in party command
    (pos, cmd) = script.find_command([0xD2],
                                     script.get_function_start(8, 1),
                                     script.get_function_end(8, 1))
    if pos is None or cmd.args[0] != 1:
        print("Error finding command (kings trial 1)")
        print(pos)
        print(cmd.args[1])
        exit()

    # Find the changelocation in this conditional block
    jump_target = pos + cmd.args[-1] - 1
    (pos, cmd) = script.find_command([0xDC, 0xDD, 0xDE,
                                      0xDF, 0xE0, 0xE1],
                                     pos, jump_target)

    if pos is None:
        print("Error finding command (kings trial 2)")
    else:
        loc = cmd.args[0]
        # print(f"{loc:04X}")
        loc = (loc & 0xFE00) + 0xC1
        # print(f"{loc:04X}")
        script.data[pos+1:pos+3] = to_little_endian(loc, 2)
        # input()

    free_event(fsrom, 0x1B9)
    Event.write_to_rom_fs(fsrom, 0x1B9, script)

    # duplicate the King's Trial, 0x1B6, to 0xC1 (unused)
    duplicate_location_data(fsrom, 0x1B6, 0xC1)

    loc_ptr = get_loc_event_ptr(fsrom.getbuffer(), 0x1B6)
    script = Event.from_rom(fsrom.getbuffer(), loc_ptr)

    # Can delete:
    #   - Object 0xB: The false witness against the king
    #   - Object 0xC: The paper the chancellor holds up in trial (small)
    #   - Object 0xD: The blue sparkle left by the Yakra key
    # This might not be enough.  Maybe the soldiers can go too?  The scene will
    # be changed, but it's worth it?

    del_objs = [0x19, 0x0C, 0x0B]
    for x in del_objs:
        script.remove_object(x)

    # New Yakra XII object is 0xB

    free_event(fsrom, 0xC1)
    Event.write_to_rom_fs(fsrom, 0xC1, script)


# This function needs to write the boss assignment to the config respecting
# the provided settings.
def write_assignment_to_config(settings: rset.Settings,
                               config: cfg.RandoConfig):

    boss_settings = settings.ro_settings

    if boss_settings.preserve_parts:
        # Do some checks to make sure that the lists are ok.
        # TODO:  Make these sets to avoid repeat element errors.

        for boss in [BossID.SON_OF_SUN, BossID.RETINITE]:
            if boss in boss_settings.boss_list:
                print(f"Legacy Boss Randomization: Removing {boss} from the "
                      'boss pool')
                boss_settings.boss_list.remove(boss)

        for loc in [LocID.SUNKEN_DESERT_DEVOURER, LocID.SUN_PALACE]:
            if loc in boss_settings.loc_list:
                print(f"Legacy Boss Randomization: Removing {loc} from the "
                      'location pool')
                boss_settings.loc_list.remove(loc)

        # Make sure that there are enough one/two partbosses to distribute to
        # the one/two part locations
        one_part_bosses = [boss for boss in boss_settings.boss_list
                           if boss in BossID.get_one_part_bosses()]

        one_part_locations = [loc for loc in boss_settings.loc_list
                              if loc in LocID.get_one_spot_boss_locations()]

        if len(one_part_bosses) < len(one_part_locations):
            print("Legacy Boss Randomization Error: "
                  f"{len(one_part_locations)} "
                  "one part locations provided but "
                  f"only {len(one_part_bosses)} one part bosses provided.")
            exit()

        two_part_bosses = [boss for boss in boss_settings.boss_list
                           if boss in BossID.get_two_part_bosses()]

        two_part_locations = [loc for loc in boss_settings.loc_list
                              if loc in LocID.get_two_spot_boss_locations()]

        if len(two_part_bosses) < len(two_part_locations):
            print("Legacy Boss Randomization Error: "
                  f"{len(two_part_locations)} "
                  "two part locations provided but "
                  f"only {len(two_part_locations)} two part bosses provided.")
            exit()

        # Now do the assignment
        random.shuffle(one_part_bosses)
        print(one_part_bosses)

        for i in range(len(one_part_locations)):
            boss = one_part_bosses[i]
            location = one_part_locations[i]
            config.boss_assign_dict[location] = boss

        random.shuffle(two_part_bosses)
        print(two_part_bosses)
        input()

        for i in range(len(two_part_locations)):
            boss = two_part_bosses[i]
            location = two_part_locations[i]
            config.boss_assign_dict[location] = boss
    else:  # Ignore part count, just randomize!
        locations = boss_settings.loc_list
        bosses = boss_settings.boss_list

        random.shuffle(bosses)

        if len(bosses) < len(locations):
            print('RO Error: Fewer bosses than locations given.')
            exit()

        for i in range(len(locations)):
            config.boss_assign_dict[locations[i]] = bosses[i]


# Scale the bosses given (the game settings) and the current assignment of
# the bosses.  This is to be differentiated from the boss scaling flag which
# scales based on the key item assignment.
def scale_bosses_given_assignment(settings: rset.Settings,
                                  config: cfg.RandoConfig):

    # dictionaries: location --> BossID
    default_assignment = get_default_boss_assignment()
    current_assignment = config.boss_assign_dict

    # dictionaries: BossID --> Boss data
    orig_data = config.boss_data_dict

    # We want to avoid a potential chain of assignments such as:
    #    A is scaled relative to B
    #    C is scaled relative to A
    # In the second scaling we want to scale relative to A's original stats,
    # not the stats that arose from the first scaling.

    # So here's a dict to store the scaled stats before writing them back
    # to the config at the very end.
    scaled_dict = dict()

    for location in settings.ro_settings.loc_list:
        orig_boss = orig_data[default_assignment[location]]
        new_boss = orig_data[current_assignment[location]]

        scaled_stats = new_boss.scale_relative_to(orig_boss,
                                                  config.enemy_dict)
        # Put the stats in scaled_dict
        for ind, part_id in enumerate(new_boss.scheme.ids):
            scaled_dict[part_id] = scaled_stats[ind]

    # Write all of the scaled stats back to config's dict
    for enemy_id in scaled_dict.keys():
        config.enemy_dict[enemy_id] = scaled_dict[enemy_id]


def write_bosses_to_ctrom(ctrom: CTRom, settings: rset.Settings,
                          config: cfg.RandoConfig):

    # Config should have a list of what bosses are to be placed where, so
    # now it's just a matter of writing them to the ctrom.

    # Associate each boss location with the function which sets that
    # location's boss.
    assign_fn_dict = {
        LocID.MANORIA_COMMAND: set_manoria_boss,
        LocID.CAVE_OF_MASAMUNE: set_denadoro_boss,
        LocID.REPTITE_LAIR_AZALA_ROOM: set_reptite_lair_boss,
        LocID.MAGUS_CASTLE_FLEA: set_magus_castle_flea_spot_boss,
        LocID.MAGUS_CASTLE_SLASH: set_magus_castle_slash_spot_boss,
        LocID.GIANTS_CLAW_TYRANO: set_giants_claw_boss,
        LocID.TYRANO_LAIR_NIZBEL: set_tyrano_lair_midboss,
        LocID.ZEAL_PALACE_THRONE_NIGHT: set_zeal_palace_boss,
        LocID.ZENAN_BRIDGE: set_zenan_bridge_boss,
        LocID.DEATH_PEAK_GUARDIAN_SPAWN: set_death_peak_boss,
        LocID.BLACK_OMEN_GIGA_MUTANT: set_giga_mutant_spot_boss,
        LocID.BLACK_OMEN_TERRA_MUTANT: set_terra_mutant_spot_boss,
        LocID.BLACK_OMEN_ELDER_SPAWN: set_elder_spawn_spot_boss,
        LocID.HECKRAN_CAVE_NEW: set_heckrans_cave_boss,
        LocID.KINGS_TRIAL_NEW: set_kings_trial_boss,
        LocID.OZZIES_FORT_FLEA_PLUS: set_ozzies_fort_flea_plus_spot_boss,
        LocID.OZZIES_FORT_SUPER_SLASH: set_ozzies_fort_super_slash_spot_boss,
        LocID.SUN_PALACE: set_sun_palace_boss,
        LocID.SUNKEN_DESERT_DEVOURER: set_desert_boss,
        LocID.OCEAN_PALACE_TWIN_GOLEM: set_twin_golem_spot
    }

    # Now do the writing. Only to locations in the above dict.  Only if the
    # assignment differs from default.

    default_assignment = get_default_boss_assignment()
    current_assignment = config.boss_assign_dict

    for loc in current_assignment.keys():
        if current_assignment[loc] == default_assignment[loc]:
            print(f"Not assigning to {loc}.  No change from default.")
        else:
            if loc not in assign_fn_dict.keys():
                print(f"Error: Tried assigning to {loc}.  Location not "
                      "supported for boss randomization.")
                exit()
            else:
                assign_fn = assign_fn_dict[loc]
                boss_id = current_assignment[loc]
                boss_scheme = config.boss_data_dict[boss_id].scheme
                print(f"Writing {boss_id} to {loc}")
                print(f"{boss_scheme}")
                assign_fn(ctrom, boss_scheme)


def main():
    pass


if __name__ == '__main__':
    main()
