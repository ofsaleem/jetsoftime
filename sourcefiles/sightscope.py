# The purpose of this file is to allow the "Sight Scope" effect to be
# permanently enabled. The game runs a check at the beginning of the battle to
# see if any characters are holding any accessories that have battle-length
# effects, and Sight Scope / Relic are among the last it checks. Here we modify
# that check to always succeed, no matter what accessories the characters are
# holding. Note that we only modify the check for the first character in the
# party, so it doesn't need to check the other two party members.

def sightscope_file(filename):
    with open(filename, 'rb') as infile:
        rom = bytearray(infile.read())

    sightscope(rom)

    with open(filename, 'wb') as outfile:
        outfile.write(rom)

def sightscope(rom):
    # The actual branch operation is at 0xCF039 in the rom file. It starts as
    # 0xF0, which is a BEQ (branch if equal) and we want it to be 0x80, a BRA
    # (branch always)
    rom[0x0CF039] = 0x80


# For testing

if __name__ == '__main__':
    with open('test1.sfc', 'rb') as infile:
        rom = bytearray(infile.read())
    rom[0x0CF039] = 0x80
    with open('test1.sfc', 'wb') as outfile:
        outfile.write(rom)

