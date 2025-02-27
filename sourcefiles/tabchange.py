import random as rand

from byteops import to_little_endian, to_rom_ptr
from ctrom import CTRom
from freespace import FSWriteType
import randoconfig as cfg
import randosettings as rset


def choose_binom(min_val: int, max_val: int, p_succ: float):

    num_flips = max_val - min_val + 1
    add = 0
    for i in range(num_flips):
        add += int(rand.random() < p_succ)

    return min_val+add


def process_ctrom(ctrom: CTRom,
                  settings: rset.Settings,
                  config: cfg.RandoConfig):

    tab_settings = settings.tab_settings

    if tab_settings.scheme == rset.TabRandoScheme.BINOMIAL:
        p_succ = tab_settings.binom_success

        def rand_func(x: int, y: int):
            return choose_binom(x, y, p_succ)
    elif tab_settings.scheme == rset.TabRandoScheme.UNIFORM:

        def rand_func(x: int, y: int):
            return rand.randrange(x, y+1)

    power_amt = rand_func(tab_settings.power_min, tab_settings.power_max)
    magic_amt = rand_func(tab_settings.magic_min, tab_settings.magic_max)
    speed_amt = rand_func(tab_settings.speed_min, tab_settings.speed_max)

    rewrite_tabs_fs(ctrom, power_amt, magic_amt, speed_amt)


# New version that uses the freespace manager to write wherever is free
# if no argument is given.
def rewrite_tabs_fs(ctrom: CTRom, power_amt, magic_amt, speed_amt,
                    rt_start=None):

    power_hex = bytearray([power_amt]).hex()
    magic_hex = bytearray([magic_amt]).hex()
    speed_hex = bytearray([speed_amt]).hex()

    spaceman = ctrom.rom_data.space_manager

    # Change the effect of the tabs
    # put the new routine at rt_start
    rt = bytearray.fromhex('18 65 6F AA E2 20 AD BD 0D C9 01 D0 0A' +
                           'A9' + power_hex +
                           '85 10 A9 63 85 12 80 16 C9 06 D0 0A' +
                           'A9' + magic_hex +
                           '85 10 A9 63 85 12 80 08' +
                           'A9' + speed_hex +
                           '85 10 A9 10 85 12' +
                           'BD 0B 00 18 65 10 C5 12 90 02 A5 12 9D 0B 00' +
                           'A6 00 BD 2F 00 18 65 10 C5 12 90 02	A5 12' +
                           '9D 2F 00 5C 0E B3 C2')

    if rt_start is None:
        rt_start = spaceman.get_free_addr(len(rt))

    rt_start_b = to_little_endian(to_rom_ptr(rt_start), 3)

    #  Turn CLC, ADC, TAX into JMP at $C2B2F8
    jmp = bytearray([0x5C]) + rt_start_b

    # old_rom[0x02B2F8:0x02B2F8+len(jmp)] = jmp[:]
    ctrom.rom_data.seek(0x02B2F8)
    ctrom.rom_data.write(jmp)

    # old_rom[rt_start:rt_start+len(rt)] = rt[:]
    ctrom.rom_data.seek(rt_start)
    ctrom.rom_data.write(rt)

    # Change the number that is displayed when a tab is used
    rt = bytearray.fromhex('AD BD 0D 29 FF 00 C9 01 00 D0 05' +
                           'A9' + power_hex + '00' +
                           '80 0D C9 06 00 D0 05' +
                           'A9' + magic_hex + '00' +
                           '80 03' +
                           'A9' + speed_hex + '00' +
                           '9D 63 0F 5C D6 B2 C2')

    if rt_start is None:
        disp_start = spaceman.get_free_addr(len(rt))
    else:
        # put the display routine a little bit later on
        disp_start = rt_start + 0x100

    disp_start_b = to_little_endian(to_rom_ptr(disp_start), 3)
    jmp = bytearray([0x5C]) + disp_start_b

    # old_rom[0x02B2D0:0x02B2D0+len(jmp)] = jmp[:]
    ctrom.rom_data.seek(0x02B2D0)
    ctrom.rom_data.write(jmp)

    # old_rom[disp_start:disp_start+len(rt)] = rt[:]
    ctrom.rom_data.seek(disp_start)
    ctrom.rom_data.write(rt)

    # Overwrite numbers in item descriptions
    # old_rom[0x375DC4] = pow_add[0] + 0xD4
    # old_rom[0x375DCF] = mag_add[0] + 0xD4
    # old_rom[0x375DD9] = spd_add[0] + 0xD4
    ctrom.rom_data.seek(0x375DC4)
    ctrom.rom_data.write(bytes([power_amt+0xD4]))

    ctrom.rom_data.seek(0x375DCF)
    ctrom.rom_data.write(bytes([magic_amt+0xD4]))

    ctrom.rom_data.seek(0x375DD9)
    ctrom.rom_data.write(bytes([magic_amt+0xD4]))



# Deprecated.  Keeping around for now to hold the rom documentation.
def rewrite_tabs(filename, rt_start=0x5F7450):
    with open(filename, 'rb') as file:
        old_rom = bytearray(file.read())
    #new_rom = old_rom[:]

    # Four major components
    # 1) Prevent activation of a tab when the stat is at max.
    # 2) Add the appropriate stats
    # 3) Change the number that pops up when you use the tab
    # 4) Change the descriptions to have the right magnitudes

    # 1) Prevent activation of a tab when the stat is at max. 

    """
    Tab index comes in through X
    $C2/B293 BF 2B CF FF LDA $FFCF2B,x[$FF:CF2C] 
    $C2/B297 A8          TAY                     
    $C2/B298 B9 9B 9A    LDA $9A9B,y[$7E:9A9B]   
    $C2/B29B DF 32 CF FF CMP $FFCF32,x[$FF:CF33] <--- holds stat maximums
    $C2/B29F B0 05       BCS $05    [$B2A6]      
    $C2/B2A1 A9 02       LDA #$02                
    $C2/B2A3 8D BC 0D    STA $0DBC  [$7E:0DBC]   
    $C2/B2A6 60          RTS                     
    """

    # I think this part needs no change.  But we'll keep the comment here just
    # in case it becomes relevant at some point.

    # 2) Add the appropriate stats
    """
    $C2/B2E3 7B          TDC                     
    $C2/B2E4 AE BD 0D    LDX $0DBD  [$7E:0DBD]   
    1 = power, 6 = magic, 2 = speed
    This is set somewhere earlier when the tab is first used.
    TODO: Look trace how this is set.
    $C2/B2E7 BF 15 B3 C2 LDA $C2B315,x[$C2:B316] 
    Range of values turning the above numbers into stat offsets
    Values: 60 00 02 01 03 04 05 ...
    $C2/B2EB C2 31       REP #$31  
    Set A,X,Y to 16-bit
    $C2/B2ED 65 6F       ADC $6F    [$00:006F]
    $6F holds (16 bit) start of a PC's stats in bank 7E
    $C2/B2EF 85 00       STA $00    [$00:0000]   
    $C2/B2F1 BF 2B CF FF LDA $FFCF2B,x[$FF:CF2C] 
    Another way to turn the values into stat offsets.
    Values: 04 00 02 01 04 05 03 ...
    The stats are stored in different orders in different places.
    The current stats use one order and the base stats use another.
    C2B315,x is the base stat order.
    FFCF2B,x is the current stat order.
    $C2/B2F5 29 FF 00    AND #$00FF              
    $C2/B2F8 18          CLC                     
    $C2/B2F9 65 6F       ADC $6F    [$00:006F]   
    $C2/B2FB AA          TAX                     
    $C2/B2FC FE 0B 00    INC $000B,x[$7E:27EB]
    Increment the current stat
    $C2/B2FF E2 20       SEP #$20                
    $C2/B301 A6 00       LDX $00    [$00:0000]   
    $C2/B303 BD 2F 00    LDA $002F,x[$7E:2721]   
    Load the base stat.
    $C2/B306 C9 63       CMP #$63
    $63 = 99d.  I'm not sure why there's a check here.  The current stat was
    checked for max already, and the base stat is always lower...
    $C2/B308 B0 04       BCS $04    [$B30E]      
    $C2/B30A 1A          INC A                   
    $C2/B30B 9D 2F 00    STA $002F,x[$7E:2721]   
    """

    rt_start_addr = to_little_endian(rt_start,3)

    # Change these, make them function parameters, etc to alter the magnitudes
    random_num = rand.randrange(0,100,1)
    if random_num < 33:
        pow_add = bytearray([2])
    elif random_num > 32 and random_num < 66:
        pow_add = bytearray([3])
    else:
        pow_add = bytearray([4])
    random_num = rand.randrange(0,101,1)
    if random_num < 33:
        mag_add = bytearray([2])
    elif random_num > 32 and random_num < 66:
        mag_add = bytearray([3])
    else:
        mag_add = bytearray([1])
    spd_add = bytearray([1])
    
    #  Turn CLC, ADC, TAX into JMP at $C2B2F8
    jmp = bytearray.fromhex('5C'+rt_start_addr.hex())
    old_rom[0x02B2F8:0x02B2F8+len(jmp)] = jmp[:]

    # put the new routine at rt_start
    rt = bytearray.fromhex('18 65 6F AA E2 20 AD BD 0D C9 01 D0 0A' +
                           'A9' + pow_add.hex() +
                           '85 10 A9 63 85 12 80 16 C9 06 D0 0A' +
                           'A9' + mag_add.hex() +
                           '85 10 A9 63 85 12 80 08' +
                           'A9' + spd_add.hex() +
                           '85 10 A9 10 85 12' +
                           'BD 0B 00 18 65 10 C5 12 90 02 A5 12 9D 0B 00' +
                           'A6 00 BD 2F 00 18 65 10 C5 12 90 02	A5 12' +
                           '9D 2F 00 5C 0E B3 C2')

    old_rom[rt_start:rt_start+len(rt)] = rt[:]

    #print("%2.2X" % len(rt))

    # 3) Change the number that pops up
    # $C2/B2D0 A9 01 00    LDA #$0001
    # $C2/B2D3 9D 63 0F    STA $0F63,x[$7E:0F63]
    # Need to include the STA command in after the branch.

    disp_start = rt_start + 0x100
    disp_start_addr = to_little_endian(disp_start, 3)

    jmp = bytearray.fromhex('5C' + disp_start_addr.hex())

    old_rom[0x02B2D0:0x02B2D0+len(jmp)] = jmp[:]

    rt = bytearray.fromhex('AD BD 0D 29 FF 00 C9 01 00 D0 05' +
	                   'A9' + pow_add.hex() +'00' +
                           '80 0D C9 06 00 D0 05' +
                           'A9' + mag_add.hex() +'00' +
                           '80 03' +
                           'A9' +spd_add.hex() + '00' +
                           '9D 63 0F 5C D6 B2 C2')

    old_rom[disp_start:disp_start+len(rt)] = rt[:]

    # 4) Change the descriptions to have the right magnitudes
    # For now, don't allow for magnitudes > 9.  We just have to overwrite
    # The right byte in the description.

    # In jets, descs are in a different place
    # Power: 0x375DBD --> 'E1 AF 62 26 E2 EF EC D5 00'
    #    The 'D5' is '1' (0x375DC4)
    # Magic: 0x375DC6 --> 'E1 AC BA C0 C2 BC E2 EF EC D5 00'
    #    The 'D5' is '1' (0x375DCF)
    # Speed: 0x375DD1 --> 'E1 B2 C9 6D BD E2 EF EC D5 00'
    #    Again, the 'D5' is '1 (0x375DD9)

    old_rom[0x375DC4] = pow_add[0] + 0xD4
    old_rom[0x375DCF] = mag_add[0] + 0xD4
    old_rom[0x375DD9] = spd_add[0] + 0xD4

    # If magnitudes over 9 are desired, then there's some surgery that needs
    # to be done to the description pointer table.

    with open(filename, 'wb') as outfile:
        outfile.write(old_rom)


def main():

    # Set up a ctrom environment
    filename = './roms/jets_test.sfc'

    ctrom = CTRom.from_file(filename, True)
    space_manager = ctrom.rom_data.space_manager

    # Set up some safe free blocks.
    space_manager.mark_block((0, 0x40FFFF),
                             FSWriteType.MARK_USED)
    space_manager.mark_block((0x411007, 0x5B8000),
                             FSWriteType.MARK_FREE)

    # Make some tabs settings changes
    settings = rset.Settings.get_race_presets()

    settings.tab_settings.scheme = rset.TabRandoScheme.BINOMIAL
    
    settings.tab_settings.power_min = 1
    settings.tab_settings.power_max = 5

    settings.tab_settings.magic_min = 3
    settings.tab_settings.magic_max = 6

    settings.tab_settings.speed_min = 2
    settings.tab_settings.speed_max = 3

    config = cfg.RandoConfig()

    process_ctrom(ctrom, settings, config)

    with open('./roms/jets_test.sfc', 'wb') as outfile:
        outfile.write(ctrom.rom_data.read())


if __name__ == '__main__':
    main()
