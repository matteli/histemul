#!/usr/bin/env python
from gimpfu import *
from gimpenums import *
import sys
import os

def color2id(color):
    a = (color[0]<<16) | (color[1]<<8) | color[2]
    b = (a & 0xF00000) >> 12 | (a & 0xF000) >> 8 | (a & 0xF00) << 4 | \
    (a & 0xF0) >> 4
    c = (b & 0xF000) | (b & 0x800) >> 11 | (b & 0x400) >> 7 | \
    (b & 0x200) >> 3 | (b & 0x100) << 1 | (b & 0x80) >> 6 | \
    (b & 0x40) >> 2 | (b & 0x20) << 2 | (b & 0x10) << 6 | \
    (b & 0x8) >> 1 | (b & 0x4) << 3 | (b & 0x2) << 7 | (b & 0x1) << 11
    return (c)
    
def gimp_histemul(img, layer):
    idd = color2id(gimp.get_foreground())
    gimp.pdb.gimp_message_set_handler (MESSAGE_BOX)
    gimp.pdb.gimp_message (idd)


register(
        "python_fu_histemul_id",
        "",
        "",
        "matteli",
        "matteli",
        "",
        "<Image>/Filters/Histemul/_id",
        "RGB*",
        [],
        [],
        gimp_histemul)

main()
