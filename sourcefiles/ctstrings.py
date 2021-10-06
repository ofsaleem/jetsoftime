

def get_token(string: str, pos: int) -> (int, int):
    symbols = ['!', '?', '/', 'unk1', 'unk2', ':', '(', ')', '\'', '.',
               ',', '=', '+', '%', 'unk3', ' ']

    char = string[pos]
    print(char, pos)
    if char.isupper():
        ct_char = (ord(char) - 0x41) + 0xA0
        length = 1
    elif char.islower():
        ct_char = (ord(char) - 0x61) + 0xBA
        length = 1
    elif char.isnumeric():
        ct_char = (ord(char) - 0x30) + 0xD4
        length = 1
    elif char in symbols:
        ct_char = symbols.index(char) + 0xDE
        length = 1
    elif char == '{':
        keyword = string[pos+1:].split('}')[0]
        length = len(keyword) + 2
        if keyword == 'null':
            ct_char = 0x00
        elif keyword == 'linebreak':
            ct_char = 0x05
        elif keyword == 'crono':
            ct_char = 0x13
        elif keyword == 'marle':
            ct_char = 0x14
        elif keyword == 'lucca':
            ct_char = 0x15
        elif keyword == 'robo':
            ct_char = 0x16
        elif keyword == 'frog':
            ct_char = 0x17
        elif keyword == 'ayla':
            ct_char = 0x18
        elif keyword == 'magus':
            ct_char = 0x19
        elif keyword == 'item':
            ct_char = 0x1F
        else:
            print(f"unknown keyword \'{keyword}\'")
            exit()
    else:
        print(f"unknown symbol \'{char}\'")
        exit()

    return (ct_char, pos+length)


def ascii_to_ct_string(ascii_string: str, start: int = None,
                       end: int = None) -> bytearray:
    if start is None:
        start = 0

    if end is None:
        end = len(ascii_string)

    outstring = bytearray()
    pos = start

    while pos < end:

        (char, pos) = get_token(ascii_string, pos)
        outstring.append(char)

    print(outstring)
    return outstring
