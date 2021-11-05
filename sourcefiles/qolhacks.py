# File for quality of life hacks
from ctrom import CTRom
import randosettings as rset

# Trick the game into thinking P1 has the SightScope equipped, for enemy health
# to always be visible.
def force_sightscope_on(ctrom: CTRom, settings: rset.Settings):
    if rset.GameFlags.VISIBLE_HEALTH in settings.gameflags:
        # Seek to the location in the ROM after the game checks if P1's
        # accessory is a SightScope
        ctrom.rom_data.seek(0x0CF039)
        # Ignore the result of that comparison and evaluate to always true, by
        # overwriting the BEQ (branch-if-equal) to BRA (branch-always)
        ctrom.rom_data.write(0x80)

# Testing
if __name__ == "__main__":
    ctrom = CTRom.from_file("test1.sfc")
    settings = rset.Settings.get_new_player_presets()
    force_sightscope_on(ctrom, settings)


