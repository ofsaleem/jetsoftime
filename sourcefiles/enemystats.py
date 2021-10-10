from __future__ import annotations
from dataclasses import dataclass
from io import BufferedWriter

from byteops import get_value_from_bytes, to_little_endian
import ctstrings
import ctenums


@dataclass
class EnemyStats:
    hp: int = 0
    level: int = 0
    speed: int = 0
    magic: int = 0
    mdef: int = 0
    offense: int = 0
    defense: int = 0
    # rewards
    xp: int = 0
    gp: int = 0
    drop_item: ctenums.ItemID = ctenums.ItemID.MOP
    charm_item: ctenums.ItemID = ctenums.ItemID.MOP
    tp: int = 0

    # There are more special flags, but I'm ignoring them for now
    can_sightscope: bool = False

    name: ctstrings.CTString = ctstrings.CTString.from_ascii('Nu')

    def from_rom(rom: bytearray, enemy_id: int):
        # enemy stat data is a 23 byte structure beginning at 0x0C4700
        stat_addr = 0x0C4700 + 23*enemy_id

        hp = get_value_from_bytes(rom[stat_addr:stat_addr+2])
        level = rom[stat_addr+2]
        speed = rom[stat_addr+9]
        magic = rom[stat_addr+0xA]
        mdef = rom[stat_addr+0xD]
        offense = rom[stat_addr+0xE]
        defense = rom[stat_addr+0xF]

        can_sightscope = bool(rom[stat_addr+0x15] & 0x2)

        # enemy rewards data is a 7 byte structure beginning at 0x0C5E00
        reward_addr = 0x0C5E00 + 7*enemy_id

        xp = get_value_from_bytes(rom[reward_addr:reward_addr+2])
        gp = get_value_from_bytes(rom[reward_addr+2:reward_addr+4])
        drop_item = rom[reward_addr+4]
        charm_item = rom[reward_addr+5]
        tp = rom[reward_addr+6]

        # enemy name starts at 0x0C6500
        # TODO: read pointer from rom
        name_start = 0x0C6500
        name_b = rom[name_start+enemy_id*11:name_start+(enemy_id+1)*11]
        name = ctstrings.CTString.ct_bytes_to_ascii(name_b)

        return EnemyStats(hp, level, speed, magic, mdef, offense, defense,
                          xp, gp, drop_item, charm_item, tp, can_sightscope,
                          name)

    def write_to_stream(self, stream: BufferedWriter, enemy_id: int):
        # enemy stat data is a 23 byte structure beginning at 0x0C4700
        stat_addr = 0x0C4700 + 23*enemy_id

        stream.seek(stat_addr)
        stream.write(to_little_endian(self.hp, 2))

        stream.write(to_little_endian(self.level, 1))

        stream.seek(stat_addr+9)
        stream.write(to_little_endian(self.speed, 1))
        stream.write(to_little_endian(self.magic, 1))

        stream.seek(stat_addr+0xD)
        stream.write(to_little_endian(self.mdef, 1))
        stream.write(to_little_endian(self.offense, 1))
        stream.write(to_little_endian(self.defense, 1))

        stream.seek(stat_addr + 0x15)
        flags = stream.read()[0]
        if self.can_sightscope:
            flags |= 0x2

            # The name doesn't show up unless this is set to 0.  It controls
            # whether the enemy's name appears when targeted.
            stream.seek(0x21DE80+enemy_id)
            stream.write(bytes([0]))
        else:
            flags &= 0xFD

        stream.seek(-1, 1)
        stream.write(bytes([flags]))

        # enemy rewards data is a 7 byte structure beginning at 0x0C5E00
        reward_addr = 0x0C5E00 + 7*enemy_id

        stream.seek(reward_addr)
        stream.write(to_little_endian(self.xp, 2))
        stream.write(to_little_endian(self.xp, 2))
        stream.write(to_little_endian(self.drop_item, 1))
        stream.write(to_little_endian(self.charm_item, 1))
        stream.write(to_little_endian(self.tp, 1))

        # I'm going to skip writing the name out for now.
        # We shouldn't be changing those, right?


def get_stat_dict(rom: bytearray) -> dict[ctenums.EnemyID,
                                          ctenums.EnemyID:EnemyStats]:

    EnemyID = ctenums.EnemyID
    stat_dict = dict()
    for enemy_id in list(EnemyID):
        # print(f"{int(enemy_id):02X}: {enemy_id}")
        stat_dict[enemy_id] = EnemyStats.from_rom(rom, enemy_id)

    return stat_dict


def main():

    EnemyID = ctenums.EnemyID

    # Get enemy names
    with open('./roms/ct.sfc', 'rb') as infile1:
        rom1 = infile1.read()

    with open('./roms/jets_test.sfc', 'rb') as infile2:
        rom2 = infile2.read()

    enemy_name_st = 0x0C6500
    enemy_name_end = 0x0C6FC9

    name_size = 0x11
    enemy_names1 = rom1[enemy_name_st:enemy_name_end]
    enemy_names2 = rom2[enemy_name_st:enemy_name_end]

    for ind in range(0xFB):
        st = ind*11
        end = (ind+1)*11
        
        name1 = enemy_names1[st:end]
        name2 = enemy_names2[st:end]

        if name1 != name2:
            str1 = ctstrings.CTString.ct_bytes_to_ascii(name1)
            str2 = ctstrings.CTString.ct_bytes_to_ascii(name2)

            print(f"{ind:02X}: {str1} != {str2}")

        # x = ctstrings.CTString.ct_bytes_to_ascii(name).upper()
        # x = x.replace(' ', '_')
        # print(f"    {x} = 0x{ind:02X}")

    exit()

    # Read all enemy stats
    with open('./roms/jets_test.sfc', 'rb') as infile:
        rom = bytearray(infile.read())

    stat_dict = dict()
    for enemy_id in list(EnemyID):
        print(f"{int(enemy_id):02X}: {enemy_id}")
        stat_dict[enemy_id] = EnemyStats.from_rom(rom, enemy_id)

    print(stat_dict[EnemyID.MAGUS])
    exit()
    


if __name__ == '__main__':
    main()
