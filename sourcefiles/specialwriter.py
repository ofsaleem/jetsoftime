import random as rand
import struct as st

sealed_pointers = [0xC3328,0xC332C,0x1BA717,0x1BA72B,0x1BAB33,0x1BAB35,0x1BAB62,0x1BAB64,0x1BACD6,0x1BACD8,
0x1BACF7,0x1BACF9,0x393D0,0x393DE,0x393F8,0x393FF,0x1B03A4,0x1B03B1,0x1B03CD,0x1B03D0,0x1B03EF,0x1B03F2,0x1B0401,
0x1B0404,0x19FE7C,0x19FE83,0x30FBF3,0x30FBF5,0x1B90EA,0x1B90F2,0x1B9123,0x1B9126,0x1B31C7,0x1B31CA,0x3AED24,0x3AED26,
0x3AEF65,0x3AEF67,0x1BAEF4,0x1BAEF9,0x1BAF0A,0x1BAF0F,0x392FD,0x39303,0x39313,0x39319,0x24EC5C,0x24EC5E,0x24EC6E,
0x24EC70]

sealed_treasures = [0xA1,0xBF,0xC2,0xC4,0xB7,0xA8,0x9F,0xB9,0x0A,0x0B,0x10,0x17,0x26,0x35,0x3F,0x8B,0x8E,0x89,
0x79,0x75,0x76,0x77,0x78,0x6E,0x9A,0xAD,0xC3,0xC5,0x9B,0xB5,0xA2,0xBA,0x0C,0x0D,0x53,0x54,0x18,0x1A,0x27,0x36,
0x37,0x40,0x41,0x43,0x4D,0x92,0x93,0x90,0x8A,0x70,0x71,0x72,0x73,0x74,0x7A,0x6A,0xA3,0xBB,0x0E,0x55,0x19,0x28,
0x38,0x39,0x91,0x86,0x8F,0x6B,0x6D,0x6C]

taban_gift_weapon = [0x35F891,0x35F893]
taban_gift_helm = [0x35F8A4,0x35F8A6]
taban_gift_armor = [0x35F8B7,0x35F8B9]

taban_helms = [0x8B,0x8E,0x89,0x92,0x93,0x90,0x8A,0x91,0x86,0x8F]
taban_armors = [0x79,0x68,0x69,0x6E,0x70,0x7A,0x6A,0x6B,0x6D,0x6C]
taban_weapons = [0x0C,0x0D,0x53,0x54,0x18,0x1A,0x27,0x36,0x37,0x40,0x41,0x43,0x4D,0x0E,0x55,0x19,0x28,0x38,0x39,0x4E]

trade_rangeweps = [0x19,0x27,0x4E]
ranged_trades = [0x39024E,0x39026B]
trade_acces = [0xA1,0xA3,0xBB,0x9A,0x9B]
acces_trades = [0x390274,0x39027B]
trade_tabs = [0xCD,0xCE,0xCF]
tab_trades = [0x390281,0x390288]
trade_weps = [0x55,0x38,0x41]
wep_trades = [0x39028E,0x390295]
trade_armors = [0x70,0x7A,0x6A,0x6B,0x6D,0x6C]
armor_trades = [0x39029B,0x3902A4]
trade_helms = [0x8B,0x88,0x92,0x93,0x8A,0x91,0x86]
helm_trades = [0x3902AC,0x3902B9]
rocks = [0xAE,0xAF,0xB0,0xB1,0xB2]
study_rock = [0x397916,0x397919]
def randomize_hardcoded_items(outfile):
   f = open(outfile,"r+b")
   i = 0
   while i < len(sealed_pointers) - 1:
       f.seek(sealed_pointers[i])
       treasure = rand.choice(sealed_treasures)
       f.write(st.pack("B",treasure))
       f.seek(sealed_pointers[i+1])
       f.write(st.pack("B",treasure))
       i += 2
   oneoffs = [taban_gift_weapon,taban_gift_armor,taban_gift_helm,ranged_trades,acces_trades,tab_trades,wep_trades,
   armor_trades,helm_trades,study_rock]
   oneoffitems = [taban_weapons,taban_armors,taban_helms,trade_rangeweps,trade_acces,trade_tabs,trade_weps,
   trade_armors,trade_helms,rocks]
   i = 0
   while i < len(oneoffs):
       f.seek(oneoffs[i][0])
       item = rand.choice(oneoffitems[i])
       f.write(st.pack("B",item))
       f.seek(oneoffs[i][1])
       f.write(st.pack("B",item))
       i += 1
   f.close
if __name__ == "__main__":
   randomize_hardcoded_items("Projectfile.smc")