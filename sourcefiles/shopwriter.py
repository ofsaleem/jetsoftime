from __future__ import annotations
from io import BytesIO
import math
import struct as st
import random as rand

from byteops import get_value_from_bytes, to_little_endian, to_file_ptr
from ctenums import ItemID, ShopID
from ctrom import CTRom
import treasurewriter as tw

import randoconfig as cfg
import randosettings as rset

# There are minor changes do the item distributions for shops.
# low_lvl_consumables: tw has powermeal but not shopwriter
# good_lvl_items: tw has greendream but not shopwriter
# hlvlconsumables: tw has tabs but not shopwriter

# There's no reason for these to be in treasurewriter.  Maybe a method
# in the enum?
low_lvl_items = tw.low_lvl_items
low_lvl_consumables = tw.low_lvl_consumables[:]
low_lvl_consumables.remove(ItemID.POWER_MEAL)

passable_lvl_items = tw.passable_lvl_items
passable_lvl_consumables = tw.passable_lvl_consumables
mid_lvl_items = tw.mid_lvl_items
mid_lvl_consumables = tw.mid_lvl_consumables
good_lvl_items = tw.good_lvl_items[:]
good_lvl_items.remove(ItemID.GREENDREAM)

good_lvl_consumables = tw.good_lvl_consumables
high_lvl_items = tw.high_lvl_items
high_lvl_consumables = tw.high_lvl_consumables[:]

for x in [ItemID.POWER_TAB, ItemID.MAGIC_TAB, ItemID.SPEED_TAB]:
    high_lvl_consumables.remove(x)

awesome_lvl_items = tw.awesome_lvl_items
awesome_lvl_consumables = tw.awesome_lvl_consumables

regular_shop_ids = [
    ShopID.TRUCE_MARKET_600,
    ShopID.ARRIS_DOME,
    ShopID.DORINO,
    ShopID.PORRE_600,
    ShopID.PORRE_1000,
    ShopID.CHORAS_INN_1000,
    ShopID.CHORAS_MARKET_600,
    ShopID.MILENNIAL_FAIR_ARMOR,
    ShopID.MILLENIAL_FAIR_ITEMS,
]

good_shop_ids = [
    ShopID.MELCHIORS_HUT,
    ShopID.IOKA_VILLAGE,
    ShopID.NU_NORMAL_KAJAR,
    ShopID.ENHASA,
    ShopID.EARTHBOUND_VILLAGE,
    ShopID.TRANN_DOME,
    ShopID.MEDINA_MARKET,
]

good_lapis_shop_ids = [
    ShopID.FIONAS_SHRINE,
    ShopID.TRUCE_MARKET_1000,
]

best_shop_ids = [
    ShopID.NU_SPECIAL_KAJAR,
    # ShopID.LAST_VILLAGE_UPDATED,  # This shop is actually unused
    ShopID.NU_BLACK_OMEN,
]

unused_shop_ids = [
    ShopID.LAST_VILLAGE_UPDATED,
    ShopID.EMPTY_12,
    ShopID.EMPTY_14,
]

shop_starts = list(range(0xC2C6F,0xC2C9D,2))
regular_shops = [0xC2C6F,0xC2C73,0xC2C77,0xC2C79,0xC2C85] + list(range(0xC2C89,0xC2C91,2))
good_shops = [0xC2C71,0xC2C75,0xC2C7D,0xC2C81,0xC2C83,0xC2C87,0xC2C93,0xC2C97,0xC2C99]
best_shops = [0xC2C7B,0xC2C7F,0xC2C9B]
forbid_shops = [0xC2C91,0xC2C95]
llvlitems = [0x95,0x98,0x99,0x97,0x96,0xA4,0x02,0x03,0x12,0x13,0x20,0x21,0x2F,0x30,0x3C,0x7E,0x7F,0x80,0x5C,0x5D,0x5E,
0x5F,0x60,0x61]
llvlconsumables = [0xBD,0xBE,0xC6,0xC7,0xC8]
plvlitems = [0xAB,0xA6,0x9C,0xB4,0xAC,0x04,0x05,0x0F,0xB9,0x14,0x22,0x23,0x31,0x81,0x82,0x62,0x63,0x64,0x65]
plvlconsumables = [0xBE,0xC0]
mlvlitems = [0xA8,0xA9,0xA0,0xA7,0x9D,0x9E,0x9F,0x06,0x07,0x08,0x15,0x16,0x24,0x25,0x32,0x33,0x34,0x3E,0x3F,0x4C,0x83,
0x84,0x8B,0x66,0x67,0x75,0x76,0x77,0x78,0x79]
mlvlconsumables =[0xBF,0xC1,0xCA,0xCB,0xCC]
glvlitems = [0xAD,0xB5,0xB6,0xB7,0xA1,0xA2,0x09,0x0A,0x10,0x17,0x18,0x26,0x29,0x35,0x36,0x40,0x43,0x4D,0x85,
0x88,0x92,0x93,0x68,0x69,0x71,0x72,0x73,0x74]
glvlconsumables = [0xBF,0xC2,0xC4]
hlvlitems = [0x9A,0x9B,0xA3,0xBA,0x0B,0x0C,0x0D,0x19,0x1A,0x27,0x37,0x38,0x41,0x4E,0x89,0x8A,0x8C,0x8D,0x8E,0x6A,0x6E,0x70]
hlvlconsumables = [0xC3,0xC4]
alvlitems = [0xBB,0x0E,0x53,0x54,0x55,0x28,0x39,0x91,0x86,0x8F,0x6C,0x7A,0x6D,0x6B]
alvlconsumables = [0xC3,0xC5]


def write_shops_to_config(settings: rset.Settings,
                          config: cfg.RandoConfig):
    regular_dist = tw.TreasureDist(
        (6, low_lvl_consumables + passable_lvl_consumables),
        (4, passable_lvl_items + mid_lvl_items)
    )
    regular_guaranteed = []

    good_dist = tw.TreasureDist(
        (5, passable_lvl_consumables + mid_lvl_consumables),
        (5, mid_lvl_items + good_lvl_items)
    )
    good_guaranteed = []
    good_lapis_guaranteed = [ItemID.LAPIS]

    best_dist = tw.TreasureDist(
        (5, (good_lvl_consumables + high_lvl_consumables +
             awesome_lvl_consumables)),
        (5, good_lvl_items + high_lvl_items + awesome_lvl_items)
    )
    best_guaranteed = [ItemID.AMULET]

    shop_manager = config.shop_manager
    shop_manager.set_shop_items(ShopID.MELCHIOR_FAIR,
                                get_melchior_shop_items())

    shop_types = [regular_shop_ids, good_shop_ids,
                  good_lapis_shop_ids, best_shop_ids]
    shop_dists = [regular_dist, good_dist, good_dist, best_dist]
    shop_guaranteed = [regular_guaranteed, good_guaranteed,
                       good_lapis_guaranteed, best_guaranteed]

    for i in range(len(shop_types)):
        for shop in shop_types[i]:
            guaranteed = shop_guaranteed[i]
            dist = shop_dists[i]
            items = get_shop_items(guaranteed, dist)

            shop_manager.set_shop_items(shop, items)

    for shop in unused_shop_ids:
        shop_manager.set_shop_items(shop, [ItemID.MOP])

    # With the whole shop list in hand, you can do some global guarantees
    # here if desired.  For example, guarantee ethers/midtonics in LW.


def write_item_prices_to_config(settings: rset.Settings,
                                config: cfg.RandoConfig):
    items_to_modify = list(ItemID)

    # Set up the list of items to randomize
    if settings.shopprices == rset.ShopPrices.MOSTLY_RANDOM:
        excluded_items = [ItemID.MID_TONIC, ItemID.ETHER, ItemID.HEAL,
                          ItemID.REVIVE, ItemID.SHELTER]
        items_to_modify = [item for item in items_to_modify
                           if item not in excluded_items]
    elif settings.shopprices == rset.ShopPrices.NORMAL:
        items_to_modify = []

    # Actually modify the prices
    for item in items_to_modify:
        if settings.shopprices in (rset.ShopPrices.FULLY_RANDOM,
                                   rset.ShopPrices.MOSTLY_RANDOM):
            price = getRandomPrice()
        elif settings.shopprices == rset.ShopPrices.FREE:
            price = 0

        config.price_manager.set_price(item, price)


def get_melchior_shop_items():

    swords = [ItemID.FLASHBLADE, ItemID.PEARL_EDGE,
              ItemID.RUNE_BLADE, ItemID.DEMON_HIT]
    robo_arms = [ItemID.STONE_ARM, ItemID.DOOMFINGER, ItemID.MAGMA_HAND]
    guns = [ItemID.RUBY_GUN, ItemID.DREAM_GUN, ItemID.MEGABLAST]
    bows = [ItemID.SAGE_BOW, ItemID.DREAM_BOW, ItemID.COMETARROW]
    katanas = [ItemID.FLINT_EDGE, ItemID.DARK_SABER, ItemID.AEON_BLADE]

    item_list = [
        rand.choice(swords),
        rand.choice(robo_arms),
        rand.choice(guns),
        rand.choice(bows),
        rand.choice(katanas),
        ItemID.REVIVE,
        ItemID.SHELTER
    ]

    return item_list


def get_shop_items(guaranteed_items: list[ItemID], item_dist):
    shop_items = guaranteed_items[:]

    # potentially shop size should be passed in.  Keep the random isolated.
    item_count = rand.randrange(3, 9) - len(shop_items)

    for item_index in range(item_count):
        item = item_dist.get_random_item()

        # Avoid duplicate items.
        while item in shop_items:
            item = item_dist.get_random_item()

        shop_items.append(item)

    # Typically better items have a higher index.  The big exception is
    # that consumables are at the very top.  That's ok though.
    return sorted(shop_items, reverse=True)


def pick_items(shop,rand_num):
    if shop in regular_shops:
        if rand_num > 4:
            item = rand.choice(llvlconsumables+plvlconsumables)
        else: 
            item = rand.choice(plvlitems+mlvlitems)
    elif shop in good_shops:
        if rand_num < 5:
            item = rand.choice(plvlconsumables + mlvlconsumables)
        else:
            item = rand.choice(mlvlitems+glvlitems)
    elif shop in best_shops:
        if rand_num < 5:
            item = rand.choice(glvlconsumables + hlvlconsumables + alvlconsumables)
        else:
            item = rand.choice(glvlitems + hlvlitems + alvlitems)
    return item
def write_slots(file_pointer,shop_start,items,shop_address):
    buffer = []
    item_count = items
    while items > 0:
       if items == 1:
            item = 0x00
       else:
            rand_num = rand.randrange(0,10,1)	
            item = pick_items(shop_start,rand_num)
       #Guarantee for Lapises from Fritz's and Fiona's shop
       if shop_start == 0xC2C71 or shop_start == 0xC2C99:
          if items == item_count:
             item = 0xCA
       #Guarantee for Amulets from shops in Kajar and the Black Omen
       if shop_start == 0xC2C7B or shop_start == 0xC2C9B:
          if items == item_count:
             item = 0x9A
       if item in buffer:
            continue
       buffer.append(item)
       file_pointer.seek(shop_address)
       file_pointer.write(st.pack("B",item))
       shop_address += 1
       items -= 1
    return shop_address
def warranty_shop(file_pointer):
    shop_address = 0x1AFC29
    guaranteed_items = [0x0,0xC8,0xC7,rand.choice([0x6,0x7,0x8]),rand.choice([0x15,0x16,0x17]),rand.choice([0x24,0x25,
    0x26]),rand.choice([0x31,0x32,0x33]),rand.choice([0x3E,0x3F,0x40,0x43])]
    shop_size = len(guaranteed_items) - 1
    while shop_size > -1:
            shop_address = write_guarantee(file_pointer,shop_address,guaranteed_items[shop_size])
            shop_size -= 1
def write_guarantee(file_pointer,shop_address,item):
    file_pointer.seek(shop_address)
    file_pointer.write(st.pack("B",item))
    shop_address += 1
    return shop_address
def randomize_shops(outfile):
   shop_pointer = 0xFC31
   shop_address = 0x1AFC31
   f = open(outfile,"r+b")
   warranty_shop(f)
   for start in shop_starts:
     if start in forbid_shops:
        f.seek(start)
        f.write(st.pack("H",shop_pointer + 1))
        continue
     shop_items = rand.randrange(4,10)
     f.seek(start)
     f.write(st.pack("H",shop_pointer))
     shop_pointer += shop_items
     shop_address = write_slots(f,start,shop_items,shop_address)
   f.close()

#
# Get a random price from 1-65000.  This function tends to 
# bias lower numbers to avoid everything being prohibitively expensive.
#
def getRandomPrice():
  r1 = rand.uniform(0, 1)
  r2 = rand.uniform(0, 1)
  return math.floor(abs(r1 - r2) * 65000 + 1)
   
#
# Modify shop prices based on the selected flags.
#
def modify_shop_prices(outfile, flag):
  if flag == "Normal":
    return
    
  f = open(outfile, "r+b")

  # Items
  # The first 147 (0x93) items are 6 bytes each.
  # Item price is 16 bits in bytes 2 and 3.
  # The price bytes are the same for all types of items.
  item_base_address = 0x0C06A4
  for index in range(0, 0x94):
    f.seek(item_base_address + (index * 6) + 1)
    price = 0
    if flag != "Free":
      price = getRandomPrice()
    f.write(st.pack("H", price))
    
  # Accessories
  # The next 39 (0x27) items are 4 bytes each.
  accessory_base_address = 0x0C0A1C
  for index in range(0, 0x28):
    f.seek(accessory_base_address + (index * 4) + 1)
    price = 0
    if flag != "Free":
      price = getRandomPrice()
    f.write(st.pack("H", price))
    
  # Key Items and Consumables
  # The final 53 (0x35) item definitions are 3 bytes each.
  consumables_base_address = 0x0C0ABC
  # In "Mostly Random" mode, exlclude midtonics, ethers, heals, 
  # revives, and shelters.
  exclusion_list = [2, 4, 10, 11, 12]
  for index in range(0, 0x36):
    f.seek(consumables_base_address + (index * 3) + 1)
    price = 0
    if flag == "Mostly Random":
      if not index in exclusion_list:
        f.write(st.pack("H", getRandomPrice()))
    elif flag == "Fully Random":
      f.write(st.pack("H", getRandomPrice()))
    else:
      # Free shops
      f.write(st.pack("H", 0))
  
  f.close()


def main():

    with open('./roms/jets_test.sfc', 'rb') as infile:
        rom = bytearray(infile.read())

    # Do a test shop writing.
    ctrom = CTRom(rom, ignore_checksum=True)
    # space_manager = ctrom.rom_data.space_manager

    # Set up some safe free blocks.
    # space_manager.mark_block((0, 0x40FFFF),
    #                          FSWriteType.MARK_USED)
    # space_manager.mark_block((0x411007, 0x5B8000),
    #                          FSWriteType.MARK_FREE)
    config = cfg.RandoConfig(rom)

    settings = rset.Settings.get_race_presets()
    settings.shopprices = rset.ShopPrices.MOSTLY_RANDOM

    process_rom(ctrom, settings, config)

    config.shop_manager.print_with_prices(config.price_manager)
    quit()

    # Turn shop pointers into ShopIDs

    print('best shops:')
    for x in best_shops:
        shop_id = (x - 0xC2C6D)//2
        name = repr(ShopID(shop_id))[1:].split(':')[0]
        print(f"    {name}")

    print('unused shops:')
    for x in shop_starts:
        shop_id = (x - 0xC2C6D)//2
        if shop_id not in (regular_shop_ids+good_shop_ids+best_shop_ids):
            name = repr(ShopID(shop_id))[1:].split(':')[0]
            print(f"    {name}")
    quit()

    # Checking to make sure the definitions are common across the files
    tw_items = tw.plvlitems
    sw_items = plvlitems

    tw_minus_sw = [x for x in tw_items if x not in sw_items]
    sw_minus_tw = [x for x in sw_items if x not in tw_items]

    print("Treasure but not enemy drop/charm:")
    for x in tw_minus_sw:
        print(f"    {ItemID(x)}")

    print("Enemy drop/charm but not item:")
    for x in sw_minus_tw:
        print(f"    {ItemID(x)}")

    # Results:
    # low_lvl_consumables: tw has powermeal but not sw
    # good_lvl_items: tw has greendream but not sw
    # hlvlconsumables: tw has tabs but not sw


if __name__ == "__main__":
    main()
    # randomize_shops("Project.sfc")
