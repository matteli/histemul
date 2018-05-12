#!/usr/bin/env python3
'''
Copyright (c) 2012-2015, Matthieu Nué
All rights reserved.

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, 
  this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice, 
  this list of conditions and the following disclaimer in the documentation 
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT 
OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF 
THE POSSIBILITY OF SUCH DAMAGE.
'''

import sys
import math
import itertools
import struct
#import progressbar
#import numpypy
import numpy as np
from PIL import Image
import csv
from collections import OrderedDict

class Map(object):
    def __init__(self):
        self.sizeBlock = 32
        self.circum = 0
        self.river = 65535
        self.sizeRiver = 20
        self.levelMax = int(math.log(self.sizeBlock) / math.log(2))
        self.width = 0
        self.height = 0
        self.nb_square = 0
    
    def color2id(self, color):
        a = (color[0]<<16) | (color[1]<<8) | color[2]
        b = (a & 0xF00000) >> 12 | (a & 0xF000) >> 8 | (a & 0xF00) << 4 | \
        (a & 0xF0) >> 4
        c = (b & 0xF000) | (b & 0x800) >> 11 | (b & 0x400) >> 7 | \
        (b & 0x200) >> 3 | (b & 0x100) << 1 | (b & 0x80) >> 6 | \
        (b & 0x40) >> 2 | (b & 0x20) << 2 | (b & 0x10) << 6 | \
        (b & 0x8) >> 1 | (b & 0x4) << 3 | (b & 0x2) << 7 | (b & 0x1) << 11
        return (c)
        
    def pic2tab(self, ffile, typeTab):
        sys.stdout.write("...")
        sys.stdout.flush()
        
        im = Image.open(ffile)
        w = im.size[0]
        h = im.size[1]
        if (w % self.sizeBlock != 0) | (h % self.sizeBlock != 0):
            print ("Width or height are not divided by " + str(self.sizeBlock))
            return (0,0,0,-1)
            
        pix = im.load()
        if typeTab == "id":
            mmap = np.zeros((w,h),np.uint16)
        elif typeTab == "indexGray":
            mmap = np.zeros((w,h),np.uint8)
        elif typeTab == "border":
            mmap = np.zeros((w,h),np.uint8)
            
        pc = 0  
        for i in range(w):
            if int(100 * i / (w - 1)) != pc :
                pc = int(100 * i / (w - 1))
                sys.stdout.write("\r" + str(pc) + "%" + " "*4)
                sys.stdout.flush()
            for j in range(h):
                if typeTab == "id":
                    a = self.color2id(pix[i,j])
                    if (a >= 0) & (a < 65536) :
                        mmap[i][j] = a
                    else :
                        print ("Id out of range at x=" + str(i) + " and y=" + str(j))
                        return (0,0,0,-1)
                elif typeTab == "indexGray":
                    a = int(pix[i,j][0] / 4)
                    if (a >= 0) & (a < 64):
                        mmap[i][j] = a
                    else:
                        print ("Shading out of range at x=" + str(i) + " and y=" + str(j))
                        return (0,0,0,-1)
                elif typeTab == "border":
                    a = int(pix[i,j][0])
                    if (a > 0) :
                        mmap[i][j] = 1
                    else :
                        mmap[i][j] = 0
        sys.stdout.write("\n")
        return (mmap, w, h, 0)
        
    def inspectBlock(self, level, xo, yo, tree, leafGray, leafBorder, block):
        block0 = block[xo][yo]
        for j,i in itertools.product(range(yo, yo + int(self.sizeBlock / math.pow(2,level-1))), \
        range(xo, xo + int(self.sizeBlock / math.pow(2,level-1)))):
            if (block[i][j] != block0): # Divide the quad in 4 quads
                tree.append(1)
                if level < self.levelMax + 1:
                    for p in ((0,0),(1,0),(1,1),(0,1)):
                        self.inspectBlock(level+1, xo + p[0] * int(self.sizeBlock / math.pow(2,level)) \
                        , yo + p[1] * int(self.sizeBlock / math.pow(2,level)), tree, leafGray, leafBorder, block)
                    return
                self.nb_square += 1
                break
        if level < self.levelMax + 1: 
            tree.append(0) #Quad (min size 2)
            self.nb_square += 1
        
        if block0[0] == 1 : 
            tree.append(1) #id mapped
            if block0[1] == 1 : #river
                block0[3]+=64
            if block0[2] > 0 : #border
                block0[3]+=128
                leafBorder.append(block0[2])
            leafGray.append(block0[3])
        else:
            tree.append(0) #not id
        return

    def writeInFile(self, ffile, data):
        f = open(ffile, 'wb')
        f.write(data)
        f.close()
        return
    
    def findClosedId(self, x, y):
        if self.idMap[x][y] <  self.river:
            return (self.idMap[x][y])
        
        k = 0
        while(True):
            k+=1
            for i in (x - k, x,  x + k):
                if (i > 0) & (i < self.width):
                    if (y + k < self.height):
                        if (self.idMap[i][y + k] < self.river) & (self.idMap[i][y + k] > 0):
                            return(self.idMap[i][y + k])
                    if (y - k >= 0):
                        if (self.idMap[i][y - k] < self.river) & (self.idMap[i][y - k] > 0):
                            return(self.idMap[i][y - k])
                            
            for j in (y,):
                if (j > 0) & (j < self.height):
                    if (x + k < self.width):
                        if (self.idMap[x + k][j] < self.river) & (self.idMap[x + k][j] > 0):
                            return(self.idMap[x + k][j])
                    if (x - k >= 0):
                        if (self.idMap[x - k][j] < self.river) & (self.idMap[x - k][j] > 0):
                            return(self.idMap[x - k][j])
        return

    
    def find2ClosedId(self, x, y):
        returnId = []
        if self.idMap[x][y] <  self.river:
            returnId.append(self.idMap[x][y])
        
        k = 0
        while(len(returnId)<2):
            k+=1
            for i in (x - k, x,  x + k):
                if (i > 0) & (i < self.width):
                    if (y + k < self.height):
                        if (self.idMap[i][y + k] < self.river) & (self.idMap[i][y + k] > 0):
                            if (len(returnId) == 0):
                                returnId.append (self.idMap[i][y + k])
                            elif (self.idMap[i][y + k] != returnId[0]):
                                returnId.append (self.idMap[i][y + k])
                    if (y - k >= 0):
                        if (self.idMap[i][y - k] < self.river) & (self.idMap[i][y - k] > 0):
                            if (len(returnId) == 0):
                                returnId.append (self.idMap[i][y - k])
                            elif (self.idMap[i][y - k] != returnId[0]):
                                returnId.append (self.idMap[i][y - k])
                            
            for j in (y,):
                if (j > 0) & (j < self.height):
                    if (x + k < self.width):
                        if (self.idMap[x + k][j] < self.river) & (self.idMap[x + k][j] > 0):
                            if (len(returnId) == 0):
                                returnId.append (self.idMap[x + k][j])
                            elif (self.idMap[x + k][j] != returnId[0]):
                                returnId.append (self.idMap[x + k][j])
                    if (x - k >= 0):
                        if (self.idMap[x - k][j] < self.river) & (self.idMap[x - k][j] > 0):
                            if (len(returnId) == 0):
                                returnId.append (self.idMap[x - k][j])
                            elif (self.idMap[x - k][j] != returnId[0]):
                                returnId.append (self.idMap[x - k][j])
        return returnId
        
    def initBlock(self, i, j, idUsed):
        block = []
        for k in range(self.sizeBlock):
            lineBlock = []
            for l in range(self.sizeBlock):
                pointBlock = []
                closedId = self.findClosedId(i+k, j+l)
                if (closedId != idUsed) :
                    pointBlock.append(0) #0
                    pointBlock.append(0) #1
                    pointBlock.append(0) #2
                    pointBlock.append(0) #3
                else :
                    pointBlock.append(1) #0
                    if closedId != self.idMap[i+k][j+l] :
                        pointBlock.append(1) #1 - River
                    else :
                        pointBlock.append(0) #1 - Land
                    if self.borMap[i+k][j+l] == 1:
                        closedIds = self.find2ClosedId(i+k, j+l)
                        if closedIds[0] == idUsed:
                            pointBlock.append(closedIds[1]) #2 - Border
                        elif closedIds[1] == idUsed:
                            pointBlock.append(closedIds[0]) #2 - Border
                        else :
                            pointBlock.append(0) #2 - No Border for Idused
                    else :
                        pointBlock.append(0) #2 - No Border
                    pointBlock.append(self.shaMap[i+k][j+l]) #3 - Gray
                lineBlock.append(pointBlock)
            block.append(lineBlock)
        return block
    
    def create_lightmap(self):
        #Writing of the ligthmap.bin
        print("Create the lightmap")
        sys.stdout.write("...")
        sys.stdout.flush()
        #pbar = progressbar.ProgressBar().start()
        #Head of the file
        nbBlock = int(self.width / self.sizeBlock) * int(self.height / self.sizeBlock)
        numBlock = 0
        dataBlock = {}
        for j,i in itertools.product(range(0, self.height, self.sizeBlock), range(0, self.width, self.sizeBlock)):
            idDoneInBlock = []
            #Loop for a block
            while True:
                idUsed = 0
                #Detected a new id in a block
                for l,k in itertools.product(range(self.sizeBlock), range(self.sizeBlock)):
                    #id is valid if not PTI and not already done
                    if (self.idMap[i+k][j+l] != 0) :
                        closedId = self.findClosedId(i+k, j+l)
                        if idDoneInBlock.count(closedId) == 0 :
                            idUsed = closedId
                            idDoneInBlock.append(idUsed)
                            break
                # Create data for an id in a block
                if idUsed != 0:
                    tree = []
                    leafGray = []
                    leafBorder = []
                    block = self.initBlock(i, j, idUsed)
                    #Create quad node tree and leaf gray
                    self.inspectBlock(1, 0, 0, tree, leafGray, leafBorder, block)
                    #pack tree in a string
                    charTree = []
                    char = 0
                    for index, item in enumerate(tree):
                        if index % 8 == 0:
                            if index > 0 : 
                                charTree.append(char)
                            char = 0
                        char = char | (item << (7 - (index % 8)))
                    charTree.append(char)
                    
                    dataPack = [charTree, leafGray, leafBorder]
                    
                    # Header of the idBlock
                    typePack = "=IIII" +  str(len(charTree)) + "B" + str(len(leafGray)) + "B" + str(len(leafBorder)) + "H"
                    #idBlock
                    if idUsed in dataBlock :
                        dataBlock[idUsed] += struct.pack(typePack, numBlock, len(charTree), len(leafGray), len(leafBorder) , *(m for n in dataPack for m in n))
                    else :
                        dataBlock[idUsed] = struct.pack(typePack, numBlock, len(charTree), len(leafGray), len(leafBorder) , *(m for n in dataPack for m in n))
                else:
                    break
                
            numBlock += 1
            #pbar.update(int ((100 * numBlock)  / nbBlock))
            sys.stdout.write("\r" + str(int ((100 * numBlock)  / nbBlock)) + "%" + " "*3)
            sys.stdout.flush()

        for i in dataBlock:
            self.writeInFile("./map/light" + str(i) + ".bin", dataBlock[i])
        #pbar.finish()
        #print (maxdataId)
        sys.stdout.write("\n")
        return 0
        
    def create_hitmap(self):
        #Writing hitmap
        print("Create the hitmap")
        sys.stdout.write("...")
        sys.stdout.flush()
        #pbar = progressbar.ProgressBar().start()
        hitMap = {}
        
        for i in range(self.width):
            #pbar.update(int(100*i / self.width))
            sys.stdout.write("\r" + str(int(100*i / (self.width-1))) + "%" + " "*3)
            sys.stdout.flush()
            idOld = -1
            for j in range (self.height):
                idNew = self.idMap[i][j]
                if (idNew != idOld) :
                    if idNew not in hitMap :
                        hitMap[idNew] = []
                    hitMap[idNew].append(i)
                    hitMap[idNew].append(j)
                    if (idOld != -1):
                        hitMap[idOld].append(j-1)
                    idOld = idNew
            hitMap[idOld].append(self.height-1)    
        
        for i in hitMap :
            if (i < self.river) & (i > 0):
                #data = struct.pack("=I"+ str(len(hitMap[i])) + "H", len(hitMap[i]), *(p for p in hitMap[i]))
                #self.writeInFile("./map/hit" + str(i) + ".bin", data)
                data = struct.pack("="+ str(len(hitMap[i])) + "H", *(p for p in hitMap[i]))
                self.writeInFile("./map/hit" + str(i) + ".bin", data)
        sys.stdout.write("\n")
        #pbar.finish()
        return (0)
        
    def create_boundmap(self):
        print("Create the boundmap")
        #pbar = progressbar.ProgressBar().start()
        boundMap = {}
        for i in range(self.width):
            #pbar.update(int(100*i / self.width))
            sys.stdout.write("\r" + str(int(100*i / (self.width-1))) + "%" + " "*3)
            sys.stdout.flush()
            for j in range (self.height):
                idd = self.idMap[i][j]
                if (idd < self.river) & (idd > 0) :
                    if idd not in boundMap :
                        boundMap[idd] = [int (self.width / self.sizeBlock), 0, int (self.height / self.sizeBlock), 0]
                    if int(i / self.sizeBlock) < boundMap[idd][0] :
                         boundMap[idd][0] = int(i / self.sizeBlock)
                    if int(i / self.sizeBlock) > boundMap[idd][1] :
                         boundMap[idd][1] = int(i / self.sizeBlock)
                    if int(j / self.sizeBlock) < boundMap[idd][2] :
                         boundMap[idd][2] = int(j / self.sizeBlock)
                    if int(j / self.sizeBlock) > boundMap[idd][3] :
                         boundMap[idd][3] = int(j / self.sizeBlock)
        for i in boundMap :
            data = struct.pack("=4H", *(m for m in boundMap[i]))
            self.writeInFile("./map/bound" + str(i) + ".bin", data)
        sys.stdout.write("\n")
        #pbar.finish()
        return 0
    
        
    def create_adjamap(self):
        print("Create the province.csv")
        #pbar = progressbar.ProgressBar().start()
        sys.stdout.write("...")
        sys.stdout.flush()
        adja = {}
        for i in range(self.width):
            #pbar.update(int(100*i / self.width))
            sys.stdout.write("\r" + str(int(100*i / (self.width-1))) + "%" + " " * 4)
            sys.stdout.flush()
            for j in range (self.height):
                idMap = self.idMap[i][j]
                if idMap < self.river and idMap > 0:
                    if idMap not in adja:
                        adja[idMap] = {}
                        adja[idMap][0] = []
                        adja[idMap][1] = []
                    for k in ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)):
                        if (i+k[0] < self.width) & (i+k[0] >= 0) & (j+k[1] < self.height) & (j+k[1] >= 0) :
                            if idMap != self.idMap[i+k[0]][j+k[1]]:
                                if self.idMap[i+k[0]][j+k[1]] < self.river and self.idMap[i+k[0]][j+k[1]] > 0:
                                    if (self.idMap[i+k[0]][j+k[1]] not in adja[idMap][0]):
                                        adja[idMap][0].append(self.idMap[i+k[0]][j+k[1]])
                                        adja[idMap][1].append(0)
                                    else:
                                        adja[idMap][1][adja[idMap][0].index(self.idMap[i+k[0]][j+k[1]])] = 0
                                else:
                                    for l in range(1, self.sizeRiver + 1, 1):
                                        if (i+k[0]*l < self.width) & (i+k[0]*l >= 0) & (j+k[1]*l < self.height) & (j+k[1]*l >= 0) :
                                            if self.idMap[i+k[0]*l][j+k[1]*l] < self.river and self.idMap[i+k[0]*l][j+k[1]*l] > 0:
                                                if idMap != self.idMap[i+k[0]*l][j+k[1]*l]:
                                                    if (self.idMap[i+k[0]*l][j+k[1]*l] not in adja[idMap][0]):
                                                        adja[idMap][0].append(self.idMap[i+k[0]*l][j+k[1]*l])
                                                        adja[idMap][1].append(1)
        

        csvtab = 65536 * [None]

        with open('province.csv') as csvfile:
            for row in csvfile:
                a = row.split(';')
                if a[1] == "_id":
                    header = a[:-1]
                else:
                    a[-1] = a[-1][:-1]
                    csvtab[int(a[1])] = a

        for row in csvtab:
            if row and int(row[1])!=0:
                row.append(set())
                for i in adja[int(row[1])][0]:
                    row[7].add(i)
                row.append(adja[int(row[1])][1])

        with open('province2.csv', 'wt') as csvfile:
            line = ''
            for i in header:
                line += str(i) + ';'
            line += 'adjacency;sea_adjacency\n'
            csvfile.write(line)
            for row in csvtab:
                if row:
                    line=''
                    for i in row:
                        if type(i) == type(set()):
                            line += '['
                            for j in i:
                                line += str(j) + ','
                            line = line[:-1]
                            line += '];'
                        else:
                            line += str(i) + ';'
                    csvfile.write(line[:-1] + '\n')
        
        
        sys.stdout.write("\n")
        #pbar.finish()
        return 0
    
    def create_configmap(self):
        print("Create the config.bin")
        data = struct.pack("=4H", self.sizeBlock, int(self.width/self.sizeBlock), int(self.height/self.sizeBlock), self.circum)
        self.writeInFile("./map/config.bin", data)
        return 0
        
    def start(self):
        #Reading of the idmap.png
        print("Reading of the picture idmap")
        res = self.pic2tab("worldid.png", "id")
        if  res[3] == -1:
            return (-1)
        self.idMap = res[0]
        self.width = res[1]
        self.height = res[2]
        
        #Reading of the lightmap.png
        print("Reading of the picture lightmap")
        res = self.pic2tab("worldshading.png", "indexGray")
        if  res[3] == -1:
            return (-1)
        self.shaMap = res[0]
        if (self.width != res[1]) | (self.height != res[2]):
            print ("Width or height are different betwenn worldid and worldshading")
            return (-1)
            
        #Reading of the bordermap.png
        print("Reading of the picture bordermap")
        res = self.pic2tab("worldborder.png", "border")
        if  res[3] == -1:
            return (-1)
        self.borMap = res[0]
        if (self.width != res[1]) | (self.height != res[2]):
            print ("Width or height are different betwenn IDmap and BorderMap")
            return (-1)
        
        #self.create_lightmap()
        #self.create_boundmap()
        self.create_adjamap()
        #self.create_hitmap()
        #self.create_configmap()
        print (self.nb_square)
        print ("Job finished !")
        
        return 0

if __name__ == "__main__":
    dmap = Map()
    dmap.start()
