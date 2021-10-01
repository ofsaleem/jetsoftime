# This module makes classes for storing a configuration of the randomizer.
# Each module of the randomizer will get passed the GameConfig object and the
# flags and update the GameConfig.  Then, the randomizer will write the
# GameConfig out to the rom.

from enum import auto
import hashlib
from io import BytesIO

from byteops import to_little_endian, get_value_from_bytes_be
from ctenums import ItemID, LocID, TreasureID as TID, CharID
# from ctevent import ScriptManager as SM, Event
from ctrom import CTRom
from freespace import FSWriteType  # Only for the test main() code


# All CharRecruits are script-based
class CharRecruit:

    # Indexed by CharID, so load_cmds[CharID.Crono] is Crono's load cmd
    load_cmds = [0x57, 0x5C, 0x62, 0x6A, 0x68, 0x6C, 0x6D]

    def __init__(self, held_char: CharID,
                 loc_id: LocID,
                 load_obj_id: int,
                 recruit_obj_id: int):
        self.held_char = held_char
        self.loc_id = loc_id
        self.load_obj_id = load_obj_id
        self.recruit_obj_id = recruit_obj_id

    # This might be poor naming, but the writing goes to the script manager
    # of the ctrom.  A separate call has to commit those changes to the rom.
    def write_to_ctrom(self, ctrom: CTRom):
        script_manager = ctrom.script_manager
        script = script_manager.get_script(self.loc_id)

        start = script.get_object_start(self.load_obj_id)
        end = script.get_object_end(self.load_obj_id)

        # First find the load command that's already in the script
        # There should be a LoadPC (not in party) command before any other
        # pc-related commands.  This has command id = 0x81.

        pos, cmd = script.find_command([0x81], start, end)

        if pos is None:
            print('Error finding initial load')
            print(self.loc_id, self.object_id)
            exit()

        script.data[pos+1] = int(self.held_char)

        orig_char = CharID(cmd.args[0])
        orig_load_cmd = CharRecruit.load_cmds[orig_char]
        target_load_cmd = CharRecruit.load_cmds[self.held_char]

        # Now handle the recruitment
        pos = script.get_object_start(self.recruit_obj_id)
        end = script.get_object_end(self.recruit_obj_id)

        while pos < end:
            # character manip commands:
            # 0x81 - Load out of party charater: 1st arg pc_id
            # 0xD2 - If PC is active: 1st arg pc_id
            # 0xCF - If PC is recruited: 1st arg pc_id
            # 0xC8 - Special Dialog (name): 1st arg pc_id | 0xC0
            # 0xD0 - Add PC to Reserve: 1st arg pc_id
            # the load command is pc-specific, 0 arg

            (pos, cmd) = \
                script.find_command(
                    [0x81, 0xD2, 0xCF, 0xC8, 0xD0, 0xD3] + [orig_load_cmd],
                    pos, end
                )

            if pos is None:
                break

            # cmds that just need the pc id written
            if cmd.command in [0x81, 0xD2, 0xCF, 0xD0, 0xD3]:
                script.data[pos+1] = int(self.held_char)
            elif cmd.command == 0xC8:
                script.data[pos+1] = int(self.held_char | 0xC0)
            elif cmd.command == orig_load_cmd:
                script.data[pos] == target_load_cmd
            else:
                print(f"Error, uncaught command ({cmd.command:02X})")
                exit()

            pos += len(cmd)


class Treasure:

    def __init__(self, held_item: ItemID = ItemID.MOP):
        self.held_item = held_item

    def write_to_ctrom(self, ctrom: CTRom):
        raise NotImplementedError


# Treasures that are obtained through a regular chest
class ChestTreasure(Treasure):

    # pointer to the start of the treasure data
    # Treasure Data (from db)
    #   bytes 0,1: x and y coords (if blank does something weird)
    #   bytes 2,3: 0x80 = Gold Flag, 0x40 = Empty Flag 0x3FFF = contents
    #              If gold flag is set, 0x7FFF = gold amount / 2
    # Since it's little endian the bits are flag bits are the leading bits
    # of byte 3.

    treasure_ptr = 0x35F402

    def __init__(self, chest_index, held_item=ItemID.MOP):
        super().__init__(held_item)
        self.chest_index = chest_index

    # Unlike script-based treasures, the ChestTreasure actually writes the
    # changes directly to the rom.
    def write_to_ctrom(self, ctrom: CTRom):
        fsrom = ctrom.rom_data
        fsrom.seek(ChestTreasure.treasure_ptr+4*self.chest_index + 2)

        # write two bytes to clear the gold/empty flags
        ctrom.write(to_little_endian(self.held_item, 2))


# Treasures that are obtained by the script adding it to your inventory
class ScriptTreasure(Treasure):

    def __init__(self, location: LocID, object_id: int, function_id: int,
                 held_item: ItemID = ItemID.MOP, item_num=0):
        super().__init__(held_item)
        self.location = location
        self.object_id = object_id
        self.function_id = function_id
        self.item_num = item_num

    def __repr__(self):
        x = (
            f"{type(self).__name__}(location={self.location}, " +
            f"object_id={self.object_id}, function_id={self.function_id},  " +
            f"held_item={self.held_item})"
        )
        return x

    def write_to_ctrom(self, ctrom: CTRom):

        script_manager = ctrom.script_manager
        script = script_manager.get_script(self.location)

        pos = script.get_function_start(self.object_id,
                                        self.function_id)
        end = script.get_function_end(self.object_id,
                                      self.function_id)

        num_add_item = 0
        num_set_item_mem = 0

        # 0x4F is setting memory, 0xCA is adding item
        cmd_ids = [0x4F, 0xCA]

        # Loop until we find exactly the right number of item display and
        # item add commands
        while (num_add_item != self.item_num and
               num_set_item_mem != self.item_num):

            pos, cmd = script.find_command(cmd_ids, pos, end)

            if pos is None:
                print('Error setting item:\n\t', end='')
                print(self)
                exit()

            if cmd.command == 0x4F:
                # Item text location is 0x7F0200.  In the command, this is
                # the last argument.
                if cmd.args[-1] != 0x00:
                    continue
                else:
                    num_set_item_mem += 1
                    set_item_mem_addr = pos + 2  # cmd, val, mem
            elif cmd.command == 0xCA:
                num_add_item += 1
                add_item_addr = pos + 1  # cmd, item

        script.data[set_item_mem_addr] = int(self.held_item)
        script.data[add_item_addr] = int(self.held_item)


class RandoConfig:

    def __init__(self):

        self.treasure_assign_dict = {
            TID.MT_WOE_1ST_SCREEN: ChestTreasure(0xD8),
            TID.MT_WOE_2ND_SCREEN_1: ChestTreasure(0xD1),
            TID.MT_WOE_2ND_SCREEN_2: ChestTreasure(0xD2),
            TID.MT_WOE_2ND_SCREEN_3: ChestTreasure(0xD3),
            TID.MT_WOE_2ND_SCREEN_4: ChestTreasure(0xD4),
            TID.MT_WOE_2ND_SCREEN_5: ChestTreasure(0xD5),
            TID.MT_WOE_3RD_SCREEN_1: ChestTreasure(0xD6),
            TID.MT_WOE_3RD_SCREEN_2: ChestTreasure(0xD7),
            TID.MT_WOE_3RD_SCREEN_3: ChestTreasure(0xD8),
            TID.MT_WOE_3RD_SCREEN_4: ChestTreasure(0xD9),
            TID.MT_WOE_3RD_SCREEN_5: ChestTreasure(0xDA),
            TID.MT_WOE_FINAL_1: ChestTreasure(0xDC),
            TID.MT_WOE_FINAL_2: ChestTreasure(0xDD),
            TID.MT_WOE_KEY: ScriptTreasure(location=LocID.MT_WOE_SUMMIT,
                                           object_id=0x08,
                                           function_id=0x01),
            TID.FIONA_KEY: ScriptTreasure(location=LocID.FIONAS_SHRINE,
                                          object_id=0x08,
                                          function_id=0x03),
            TID.ARRIS_DOME_RATS: ChestTreasure(0x71),
            TID.ARRIS_DOME_FOOD_STORE: ChestTreasure(0xD0),
            TID.ARRIS_DOME_KEY: ScriptTreasure(location=LocID.ARRIS_DOME,
                                               object_id=0x0F,
                                               function_id=0x2),
            TID.SUN_PALACE_KEY: ScriptTreasure(location=LocID.SUN_PALACE,
                                               object_id=0x11,
                                               function_id=0x01),
            TID.SEWERS_1: ChestTreasure(0x84),
            TID.SEWERS_2: ChestTreasure(0x85),
            TID.SEWERS_3: ChestTreasure(0x86),
            TID.LAB_16_1: ChestTreasure(0x6D),
            TID.LAB_16_2: ChestTreasure(0x6E),
            TID.LAB_16_3: ChestTreasure(0x6F),
            TID.LAB_16_4: ChestTreasure(0x70),
            TID.LAB_32_1: ChestTreasure(0x71),
            TID.PRISON_TOWER_1000: ChestTreasure(0xF6),
            TID.GENO_DOME_1F_1: ChestTreasure(0x8B),
            TID.GENO_DOME_1F_2: ChestTreasure(0x8C),
            TID.GENO_DOME_1F_3: ChestTreasure(0x8D),
            TID.GENO_DOME_1F_4: ChestTreasure(0x8E),
            TID.GENO_DOME_ROOM_1: ChestTreasure(0x8F),
            TID.GENO_DOME_ROOM_2: ChestTreasure(0x90),
            TID.GENO_DOME_PROTO4_1: ChestTreasure(0x91),
            TID.GENO_DOME_PROTO4_2: ChestTreasure(0x92),
            TID.GENO_DOME_2F_1: ChestTreasure(0x99),
            TID.GENO_DOME_2F_2: ChestTreasure(0x9A),
            TID.GENO_DOME_2F_3: ChestTreasure(0x9B),
            TID.GENO_DOME_2F_4: ChestTreasure(0x9C),
            TID.GENO_DOME_KEY: ScriptTreasure(
                location=LocID.GENO_DOME_MAINFRAME,
                object_id=0x01,
                function_id=0x04
            ),
            TID.FACTORY_LEFT_AUX_CONSOLE: ChestTreasure(0x79),
            TID.FACTORY_LEFT_SECURITY_RIGHT: ChestTreasure(0x7A),
            TID.FACTORY_LEFT_SECURITY_LEFT: ChestTreasure(0x7B),
            TID.FACTORY_RIGHT_DATA_CORE_1: ChestTreasure(0x93),
            TID.FACTORY_RIGHT_DATA_CORE_2: ChestTreasure(0x94),
            TID.FACTORY_RIGHT_FLOOR_TOP: ChestTreasure(0x7C),
            TID.FACTORY_RIGHT_FLOOR_LEFT: ChestTreasure(0x7D),
            TID.FACTORY_RIGHT_FLOOR_BOTTOM: ChestTreasure(0x7E),
            TID.FACTORY_RIGHT_FLOOR_SECRET: ChestTreasure(0x7F),
            TID.FACTORY_RIGHT_CRANE_LOWER: ChestTreasure(0x80),
            TID.FACTORY_RIGHT_CRANE_UPPER: ChestTreasure(0x81),
            TID.FACTORY_RIGHT_INFO_ARCHIVE: ChestTreasure(0x82),
            # Inaccessible Robot storage chest omitted -- would be 0xE7
            TID.GIANTS_CLAW_KINO_CELL: ChestTreasure(0x19),
            TID.GIANTS_CLAW_TRAPS: ChestTreasure(0x1A),
            TID.GIANTS_CLAW_CAVES_1: ChestTreasure(0x5A),
            TID.GIANTS_CLAW_CAVES_2: ChestTreasure(0x5B),
            TID.GIANTS_CLAW_CAVES_3: ChestTreasure(0x5C),
            TID.GIANTS_CLAW_CAVES_4: ChestTreasure(0x5D),
            TID.GIANTS_CLAW_CAVES_5: ChestTreasure(0x5F),
            TID.GIANTS_CLAW_ROCK: ChestTreasure(0x5E),
            TID.GIANTS_CLAW_KEY: ScriptTreasure(
                location=LocID.GIANTS_CLAW_TYRANO,
                object_id=0x0A,
                function_id=0x01
            ),
            # Weirdness with Northern Ruins.
            # There's a variable set, only for these
            # locations indicating whether you're in the
            #   0x7F10A3 & 0x10 ->  600
            #   0x7F10A3 & 0x20 -> 1000
            TID.NORTHERN_RUINS_BASEMENT_600: ScriptTreasure(
                location=LocID.NORTHERN_RUINS_BASEMENT,
                object_id=0x08,
                function_id=0x01,
                item_num=1
            ),
            TID.NORTHERN_RUINS_UPSTAIRS_600: auto(),
            TID.NORTHERN_RUINS_UPSTAIRS_1000: auto(),
            TID.HEROS_GRAVE_1_600: auto(),
            TID.HEROS_GRAVE_2_600: auto(),
            TID.HEROS_GRAVE_3_600: auto(),
            TID.HEROS_GRAVE_1_1000: auto(),
            TID.HEROS_GRAVE_2_1000: auto(),
            TID.HEROS_GRAVE_3_1000: auto(),
            # Frog locked one
            TID.NORTHERN_RUINS_BASEMENT_1000: ScriptTreasure(
                location=LocID.NORTHERN_RUINS_BASEMENT,
                object_id=0x08,
                function_id=0x01,
                item_num=0
            ),
            TID.GUARDIA_BASEMENT_1: ChestTreasure(0x06),
            TID.GUARDIA_BASEMENT_2: ChestTreasure(0x07),
            TID.GUARDIA_BASEMENT_3: ChestTreasure(0x08),
            TID.GUARDIA_TREASURY_1: ChestTreasure(0xE8),
            TID.GUARDIA_TREASURY_2: ChestTreasure(0xE9),
            TID.GUARDIA_TREASURY_3: ChestTreasure(0xEA),
            TID.KINGS_TRIAL_KEY: ScriptTreasure(
                location=LocID.GUARDIA_REAR_STORAGE,
                object_id=0x02,
                function_id=0x03
            ),
            TID.OZZIES_FORT_GUILLOTINES_1: ChestTreasure(0x54),
            TID.OZZIES_FORT_GUILLOTINES_2: ChestTreasure(0x55),
            TID.OZZIES_FORT_GUILLOTINES_3: ChestTreasure(0x56),
            TID.OZZIES_FORT_GUILLOTINES_4: ChestTreasure(0x57),
            TID.OZZIES_FORT_FINAL_1: ChestTreasure(0x58),
            TID.OZZIES_FORT_FINAL_2: ChestTreasure(0x59),
            TID.TRUCE_MAYOR_1F: ChestTreasure(0x02),
            TID.TRUCE_MAYOR_2F: ChestTreasure(0x03),
            TID.FOREST_RUINS: ChestTreasure(0x0A),
            TID.PORRE_MAYOR_2F: ChestTreasure(0x0F),
            TID.TRUCE_CANYON_1: ChestTreasure(0x1B),
            TID.TRUCE_CANYON_2: ChestTreasure(0x1C),
            TID.FIONAS_HOUSE_1: ChestTreasure(0x3E),
            TID.FIONAS_HOUSE_2: ChestTreasure(0x3F),
            TID.CURSED_WOODS_1: ChestTreasure(0x28),
            TID.CURSED_WOODS_2: ChestTreasure(0x29),
            TID.FROGS_BURROW_RIGHT: ChestTreasure(0x2A),
            TID.ZENAN_BRIDGE_KEY: ScriptTreasure(LocID.GUARDIA_THRONEROOM_600,
                                                 object_id=0x0F,
                                                 function_id=0x00),
            TID.SNAIL_STOP_KEY: ScriptTreasure(LocID.SNAIL_STOP,
                                               object_id=0x09,
                                               function_id=0x01),
            TID.LAZY_CARPENTER: ScriptTreasure(LocID.CHORAS_CARPENTER_1000,
                                               object_id=0x08,
                                               function_id=0x01),
            TID.HECKRAN_CAVE_SIDETRACK: ChestTreasure(0x0B),
            TID.HECKRAN_CAVE_ENTRANCE: ChestTreasure(0x0C),
            TID.HECKRAN_CAVE_1: ChestTreasure(0x0D),
            TID.HECKRAN_CAVE_2: ChestTreasure(0x0E),
            TID.TABAN_KEY: ScriptTreasure(LocID.LUCCAS_WORKSHOP,
                                          object_id=0x08,
                                          function_id=0x01,
                                          item_num=0),
            TID.KINGS_ROOM_1000: ChestTreasure(0x04),
            TID.QUEENS_ROOM_1000: ChestTreasure(0x05),
            TID.KINGS_ROOM_600: ChestTreasure(0x1D),
            TID.QUEENS_ROOM_600: ChestTreasure(0x1E),
            TID.ROYAL_KITCHEN: ChestTreasure(0x1F),
            TID.QUEENS_TOWER_600: ChestTreasure(0xEB),
            TID.KINGS_TOWER_600: ChestTreasure(0xF2),
            TID.KINGS_TOWER_1000: ChestTreasure(0xF3),
            TID.QUEENS_TOWER_1000: ChestTreasure(0xF4),
            TID.GUARDIA_COURT_TOWER: ChestTreasure(0xF5),
            TID.MANORIA_CATHEDRAL_1: ChestTreasure(0x21),
            TID.MANORIA_CATHEDRAL_2: ChestTreasure(0x22),
            TID.MANORIA_CATHEDRAL_3: ChestTreasure(0x23),
            TID.MANORIA_INTERIOR_1: ChestTreasure(0x24),
            TID.MANORIA_INTERIOR_2: ChestTreasure(0x25),
            TID.MANORIA_INTERIOR_3: ChestTreasure(0x26),
            TID.MANORIA_INTERIOR_4: ChestTreasure(0x27),
            TID.MANORIA_SHRINE_SIDEROOM_1: ChestTreasure(0x61),
            TID.MANORIA_SHRINE_SIDEROOM_2: ChestTreasure(0x62),
            TID.MANORIA_BROMIDE_1: ChestTreasure(0x63),
            TID.MANORIA_BROMIDE_2: ChestTreasure(0x64),
            TID.MANORIA_BROMIDE_3: ChestTreasure(0x65),
            TID.MANORIA_SHRINE_MAGUS_1: ChestTreasure(0x66),
            TID.MANORIA_SHRINE_MAGUS_2: ChestTreasure(0x67),
            TID.YAKRAS_ROOM: ChestTreasure(0x60),
            TID.DENADORO_MTS_SCREEN2_1: ChestTreasure(0x2B),
            TID.DENADORO_MTS_SCREEN2_2: ChestTreasure(0x2C),
            TID.DENADORO_MTS_SCREEN2_3: ChestTreasure(0x2D),
            TID.DENADORO_MTS_FINAL_1: ChestTreasure(0x2E),
            TID.DENADORO_MTS_FINAL_2: ChestTreasure(0x2F),
            TID.DENADORO_MTS_FINAL_3: ChestTreasure(0x30),
            TID.DENADORO_MTS_WATERFALL_TOP_1: ChestTreasure(0x31),
            TID.DENADORO_MTS_WATERFALL_TOP_2: ChestTreasure(0x32),
            TID.DENADORO_MTS_WATERFALL_TOP_3: ChestTreasure(0x33),
            TID.DENADORO_MTS_WATERFALL_TOP_4: ChestTreasure(0x34),
            TID.DENADORO_MTS_WATERFALL_TOP_5: ChestTreasure(0x35),
            TID.DENADORO_MTS_ENTRANCE_1: ChestTreasure(0x36),
            TID.DENADORO_MTS_ENTRANCE_2: ChestTreasure(0x37),
            TID.DENADORO_MTS_SCREEN3_1: ChestTreasure(0x38),
            TID.DENADORO_MTS_SCREEN3_2: ChestTreasure(0x39),
            TID.DENADORO_MTS_SCREEN3_3: ChestTreasure(0x3A),
            TID.DENADORO_MTS_SCREEN3_4: ChestTreasure(0x3B),
            TID.DENADORO_MTS_AMBUSH: ChestTreasure(0x3C),
            TID.DENADORO_MTS_SAVE_PT: ChestTreasure(0x3D),
            TID.DENADORO_MTS_KEY: ScriptTreasure(
                location=LocID.CAVE_OF_MASAMUNE,
                object_id=0x0A,
                function_id=0x2
            ),
            TID.BANGOR_DOME_SEAL_1: ChestTreasure(0x68),
            TID.BANGOR_DOME_SEAL_2: ChestTreasure(0x69),
            TID.BANGOR_DOME_SEAL_3: ChestTreasure(0x6A),
            TID.TRANN_DOME_SEAL_1: ChestTreasure(0x6B),
            TID.TRANN_DOME_SEAL_2: ChestTreasure(0x6C),
            TID.ARRIS_DOME_SEAL_1: ChestTreasure(0x72),
            TID.ARRIS_DOME_SEAL_2: ChestTreasure(0x73),
            TID.ARRIS_DOME_SEAL_3: ChestTreasure(0x74),
            TID.ARRIS_DOME_SEAL_4: ChestTreasure(0x75),
            TID.TRUCE_INN_SEALED_600: auto(),
            TID.PORRE_ELDER_SEALED_1: auto(),
            TID.PORRE_ELDER_SEALED_2: auto(),
            TID.GUARDIA_CASTLE_SEALED_600: auto(),
            TID.GUARDIA_FOREST_SEALED_600: auto(),
            TID.TRUCE_INN_SEALED_1000: auto(),
            TID.PORRE_MAYOR_SEALED_1: auto(),
            TID.PORRE_MAYOR_SEALED_2: auto(),
            TID.GUARDIA_FOREST_SEALED_1000: auto(),
            TID.GUARDIA_CASTLE_SEALED_1000: auto(),
            TID.HECKRAN_SEALED_1: auto(),
            TID.HECKRAN_SEALED_2: auto(),
            TID.PYRAMID_LEFT: auto(),
            TID.PYRAMID_RIGHT: auto(),
            TID.MAGIC_CAVE_SEALED: auto(),
            TID.MYSTIC_MT_STREAM: ChestTreasure(0x9D),
            TID.FOREST_MAZE_1: ChestTreasure(0x9E),
            TID.FOREST_MAZE_2: ChestTreasure(0x9F),
            TID.FOREST_MAZE_3: ChestTreasure(0xA0),
            TID.FOREST_MAZE_4: ChestTreasure(0xA1),
            TID.FOREST_MAZE_5: ChestTreasure(0xA2),
            TID.FOREST_MAZE_6: ChestTreasure(0xA3),
            TID.FOREST_MAZE_7: ChestTreasure(0xA4),
            TID.FOREST_MAZE_8: ChestTreasure(0xA5),
            TID.FOREST_MAZE_9: ChestTreasure(0xA6),
            TID.REPTITE_LAIR_REPTITES_1: ChestTreasure(0xAD),
            TID.REPTITE_LAIR_REPTITES_2: ChestTreasure(0xAE),
            TID.REPTITE_LAIR_KEY: ScriptTreasure(
                LocID.REPTITE_LAIR_AZALA_ROOM,
                object_id=0x00,
                function_id=0x00
            ),
            TID.DACTYL_NEST_1: ChestTreasure(0xAF),
            TID.DACTYL_NEST_2: ChestTreasure(0xB0),
            TID.DACTYL_NEST_3: ChestTreasure(0xB1),
            TID.MELCHIOR_KEY: ScriptTreasure(
                location=LocID.GUARDIA_REAR_STORAGE,
                object_id=0x17,
                function_id=0x1
            ),
            TID.FROGS_BURROW_LEFT: ScriptTreasure(location=LocID.FROGS_BURROW,
                                                  object_id=0x0A,
                                                  function_id=0x01)
            # Tabs later if they're going to be randomized
            # GUARDIA_FOREST_POWER_TAB_600: auto()
            # GUARDIA_FOREST_POWER_TAB_1000: auto()
            # SUN_KEEP_POWER_TAB_600: auto()
            # MEDINA_ELDER_SPEED_TAB: auto()
            # MEDINA_ELDER_MAGIC_TAB: auto()
        }

        # char assignments are completely arbitrary here
        # the keys can be different since there's some redundancy in the
        # key and the arg to CharRecruit
        self.char_assign_dict = {
            LocID.MANORIA_SANCTUARY: CharRecruit(
                held_char=CharID.LUCCA,
                loc_id=LocID.MANORIA_SANCTUARY,
                load_obj_id=0x19,
                recruit_obj_id=0x19
            ),
            LocID.GUARDIA_QUEENS_CHAMBER_600: CharRecruit(
                held_char=CharID.MARLE,
                loc_id=LocID.GUARDIA_QUEENS_CHAMBER_600,
                load_obj_id=0x17,
                recruit_obj_id=0x18
            ),
            LocID.FROGS_BURROW: CharRecruit(
                held_char=CharID.FROG,
                loc_id=LocID.FROGS_BURROW,
                load_obj_id=0x0F,
                recruit_obj_id=0x0F
            ),
            LocID.DACTYL_NEST_SUMMIT: CharRecruit(
                held_char=CharID.AYLA,
                loc_id=LocID.DACTYL_NEST_SUMMIT,
                load_obj_id=0x0D,
                recruit_obj_id=0x0D
            ),
            LocID.PROTO_DOME: CharRecruit(
                held_char=CharID.ROBO,
                loc_id=LocID.PROTO_DOME,
                load_obj_id=0x18,
                recruit_obj_id=0x18
            )
        }


def main():
    with open('./roms/jets_test.sfc', 'rb') as infile:
        rom = bytearray(infile.read())

    ctrom = CTRom(rom, ignore_checksum=True)
    space_manager = ctrom.rom_data.space_manager

    # Set up some safe free blocks.
    space_manager.mark_block((0, 0x40FFFF),
                             FSWriteType.MARK_USED)
    space_manager.mark_block((0x411007, 0x5B8000),
                             FSWriteType.MARK_FREE)

    
    config = RandoConfig()

    cath = config.char_assign_dict[LocID.MANORIA_SANCTUARY]
    cath.held_char = CharID.LUCCA
    cath.write_to_ctrom(ctrom)

    ctrom.write_all_scripts_to_rom()

    with open('./roms/jets_test_out.sfc', 'wb') as outfile:
        ctrom.rom_data.seek(0)
        outfile.write(ctrom.rom_data.read())


if __name__ == '__main__':
    main()
