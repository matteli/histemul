#!/usr/bin/env python3

def id2HexColor(id):
    a = (id & 0x200) >> 1 | (id & 0x40) << 3 | (id & 0x8) << 7 | \
    (id & 0x1) << 11 | (id & 0x400) >> 6 | (id & 0x80) >> 2 | \
    (id & 0x10) << 2 | (id & 0x2) << 6 | (id & 0x800) >> 11 | \
    (id & 0x100) >> 7 | (id & 0x20) >> 3 | (id & 0x4) << 1 | \
    (id & 0xF000)
    
    b = (a & 0xF00) << 12 | (a & 0xF0) << 8 | (a & 0xF) << 4 | \
    (a & 0xF000) >> 4
    
    
    return("#%06x" % b)


if __name__ == "__main__":
    while (True):
        idd = input("quelle id ? : ")
        if (idd == 0): break
        print (id2HexColor(int(idd)))
