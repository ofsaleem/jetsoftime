from ctrom import CTRom
import randosettings as rset

def process_ctrom(ctrom: CTRom, settings: rset.Settings):
    if rset.GameFlags.VISIBLE_HEALTH in settings.gameflags:
        ctrom.rom_data.seek(0x0CF039)
        ctrom.rom_data.write(0x80)

