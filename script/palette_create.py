#!/usr/bin/env python

def id2Color(id):
    a = (id & 0x200) >> 1 | (id & 0x40) << 3 | (id & 0x8) << 7 | \
    (id & 0x1) << 11 | (id & 0x400) >> 6 | (id & 0x80) >> 2 | \
    (id & 0x10) << 2 | (id & 0x2) << 6 | (id & 0x800) >> 11 | \
    (id & 0x100) >> 7 | (id & 0x20) >> 3 | (id & 0x4) << 1 | \
    (id & 0xF000)
    
    b = (a & 0xF00) << 12 | (a & 0xF0) << 8 | (a & 0xF) << 4 | \
    (a & 0xF000) >> 4
    
    return(str((b & 0xFF0000) >> 16), ' ' , str((b & 0xFF00) >> 8), ' ' , str(b & 0xFF), ' ', str(id), '\n')


if __name__ == "__main__":
    #for i in range(64):
    #    f = open('./histemul' + str(i*1024) + 'to' + str((i+1)*1024-1) + '.gpl','w')
    #    f.write("GIMP Palette\nName: HistEmul" + str(i*1024) + 'to' + str((i+1)*1024-1) + "\n#\n")
    #    for j in range(1024):
    #        f.write(''.join(id2Color(i*1024+j)))
    #while true:
	idd = input("quel id ?")
        #if (idd == 0): break
	print id2Color(idd)
