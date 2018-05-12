#!/usr/bin/python3
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

import random
import sys
from PIL import Image, ImageDraw
import csv
import math
from math import sin, cos, pi, sqrt
import shlex, subprocess
import yaml

#import pdb; pdb.set_trace()
def id2HexColor(id):
    a = (id & 0x200) >> 1 | (id & 0x40) << 3 | (id & 0x8) << 7 | \
    (id & 0x1) << 11 | (id & 0x400) >> 6 | (id & 0x80) >> 2 | \
    (id & 0x10) << 2 | (id & 0x2) << 6 | (id & 0x800) >> 11 | \
    (id & 0x100) >> 7 | (id & 0x20) >> 3 | (id & 0x4) << 1 | \
    (id & 0xF000)
    
    b = (a & 0xF00) << 12 | (a & 0xF0) << 8 | (a & 0xF) << 4 | \
    (a & 0xF000) >> 4
    
    
    return("#%06x" % b)

def id2Color(id):
    a = (id & 0x200) >> 1 | (id & 0x40) << 3 | (id & 0x8) << 7 | \
    (id & 0x1) << 11 | (id & 0x400) >> 6 | (id & 0x80) >> 2 | \
    (id & 0x10) << 2 | (id & 0x2) << 6 | (id & 0x800) >> 11 | \
    (id & 0x100) >> 7 | (id & 0x20) >> 3 | (id & 0x4) << 1 | \
    (id & 0xF000)
    
    b = (a & 0xF00) << 12 | (a & 0xF0) << 8 | (a & 0xF) << 4 | \
    (a & 0xF000) >> 4
    
    return(b+0xff000000)
    
#height = 2000
provinceArea = 15000
seaArea = 60000
continent_color = {(255,0,0): "france", (0,0,255): "italia", (0,255,0):"deutschland", (255,255,0):"england"}

space = (provinceArea**0.5)/1.1
armySpaceFromCapital = int((provinceArea**0.5)/3)

maskImage = Image.open("land.png")
#image = image.crop((0, int(image.size[1]*0.02), image.size[0], int(image.size[1]*0.98)))
width = maskImage.size[0]
height = maskImage.size[1]

with open("culture.yaml") as cultureFile:
    culture = yaml.load(cultureFile)



print ('Load background')
pix = maskImage.load()

print ('Numerate white pixel :')
maskImageColors = maskImage.getcolors()
whiteP = 0
for t in maskImageColors:
    if t[1] != (0,0,0): #white
        whiteP += t[0]

print (str(whiteP) + " whites pixels")
blackP = width*height - whiteP

landImage = Image.new("RGB", (width,height), (0,0,0))
land = ImageDraw.Draw(landImage)


print ('Place capitals :')
sys.stdout.write("...")
sys.stdout.flush()

nbProvinces = int(whiteP/provinceArea)
mxy = []
continent = []


mxy.append((-width,height/2))
mxy.append((2*width,height/2))
mxy.append((width/2,2*height))
mxy.append((width/2,-height))
continent.append("")
continent.append("")
continent.append("")
continent.append("")

i = 0
while i < nbProvinces:
    a = random.randint(0, width - 1)
    b = random.randint(0, height - 1)

    if pix[a,b] != (0,0,0): #black
        avalaible = True
        for k in mxy:
            if (abs(a-k[0]) < space) and (abs(b-k[1]) < space):
                avalaible = False
                break
        if avalaible :
            i += 1
            mxy.append((a,b))
            continent.append(continent_color[pix[a,b]])
            pc = int(i*100/nbProvinces)
            sys.stdout.write("\r" + str(pc) + "%" + " "*4)
            sys.stdout.flush()
sys.stdout.write("\n")
print (str(nbProvinces) + ' provinces')

print ('Make provinces :')
sys.stdout.write("...")
sys.stdout.flush()

from scipy.spatial import Voronoi
import numpy as np
mpxy = np.array(mxy)

vor = Voronoi(mpxy)

csvfile = open('province.csv', 'w')
#with open('province.csv', 'w') as csvfile:
csvwriter = csv.writer(csvfile)

csvwriter.writerow(["name", "_id", "culture", "city_x", "city_y", "army_x", "army_y"])#,"nameXPos","nameYPos","nameAngle","nameLength"])

for k, idVRegion in enumerate(vor.point_region):
    if k > 3:
        idProvince = k-3
        nb = random.randint(0, 2)
        name = random.choice(culture[continent[k]]["province"]["first"])
        for i in range(nb):
            name += random.choice(culture[continent[k]]["province"]["middle"])
        name += random.choice(culture[continent[k]]["province"]["end"])
        armyXPos = mxy[k][0] + armySpaceFromCapital
        armyYPos = mxy[k][1] + armySpaceFromCapital
        csvwriter.writerow([name] + [idProvince] + [continent[k]] + list(mxy[k]) + [armyXPos] + [armyYPos])# + list(p1) + [alpha] + [length])
        
        vertices = []
        for idVertice in vor.regions[idVRegion]:
            if idVertice >= 0:
                vertices.append(tuple(vor.vertices[idVertice]))
                
        land.polygon(vertices, fill=id2HexColor(idProvince))
        pc = int(idProvince*100/nbProvinces)
        sys.stdout.write("\r" + str(pc) + "%" + " "*4)
        sys.stdout.flush()

'''c = 0
for i in vor.regions:
    #avalaible = True
    if i:
        p = []
        for j in i:
            if j >= 0:
                p.append(tuple(vor.vertices[j]))
                #l += list(tuple(vor.vertices[j]))
        s = []
        for j in i:
            if j >= 0:
                t = (int(vor.vertices[j][0]), int(vor.vertices[j][1]))
                if (t[0] >= 0 and t[0] < width and t[1] >=0 and t[1] < height):
                    if pix[t[0],t[1]] != (0,0,0):
                        s.append(t)
        
        c += 1
        #import pdb; pdb.set_trace()
        for k, v in enumerate(vor.point_region):
            if (v == c) and (continent[k]):
                #import pdb; pdb.set_trace()
                nb = random.randint(0, 2)
                name = random.choice(culture[continent[k]]["province"]["first"])
                for i in range(nb):
                    name += random.choice(culture[continent[k]]["province"]["middle"])
                name += random.choice(culture[continent[k]]["province"]["end"])
                maxDis = 0
                for l in s:
                    for n in s:
                        dis = (l[0]-n[0])**2 + (l[1]-n[1])**2
                        if dis > maxDis:
                            maxDis = dis
                            if min(l[0], n[0])==l[0]:
                                p1 = l
                                p2 = n
                            else:
                                p1 = n
                                p2 = l
                
                alpha = int(math.degrees(math.atan2(p1[1]-p2[1],p2[0]-p1[0])))
                length = int(((p2[1]-p1[1])**2 + (p2[0]-p1[0])**2)**0.5)
                random.shuffle(s)
                pos = []
                if s:
                    pos.append(int((2*s[0][0] + mxy[k][0])/3))
                    pos.append(int((2*s[0][1] + mxy[k][1])/3))
                else:
                    pos.append(mxy[k][0])
                    pos.append(mxy[k][1])
                csvwriter.writerow([name] + [c] + [continent[k]] + list(mxy[k]))# + pos + list(p1) + [alpha] + [length])
                
                break
        land.polygon(p, fill=id2HexColor(c))
        pc = int(c*100/m)
        sys.stdout.write("\r" + str(pc) + "%" + " "*4)
        sys.stdout.flush()'''

#for k in mxy:
#    land.point(k,"#%06x" % 255)
sys.stdout.write("\n")

landImage.save("landtemp.png", "PNG")
p = subprocess.Popen(shlex.split("convert landtemp.png -interpolate integer -background Black -wave " + str(int(space/4)) + "x" + str(int(space*3)) + " -rotate -90 -wave " + str(int(space/4)) + "x" + str(int(space*3)) + " -rotate +90 landtemp.png"))
p.wait()
del (landImage)
landImage = Image.open("landtemp.png")
landImage = landImage.crop((int((landImage.size[0]-width)/2), int((landImage.size[1]-height)/2), int((landImage.size[0]+width)/2), int((landImage.size[1]+height)/2)))



seaImage = Image.new("RGB", (width,height), (0,0,0))
sea = ImageDraw.Draw(seaImage)

nbSeaProvince = int(blackP/seaArea)
mxy = []
space = (seaArea**0.5)/1.2

print ('Place seas :')
sys.stdout.write("...")
sys.stdout.flush()

mxy.append((-width,height/2))
mxy.append((2*width,height/2))
mxy.append((width/2,2*height))
mxy.append((width/2,-height))

i = 0
while i < nbSeaProvince:
    a = random.randint(0, width - 1)
    b = random.randint(0, height - 1)

    if pix[a,b] == (0,0,0): #black
        avalaible = True
        for k in mxy:
            if (abs(a-k[0]) < space) and (abs(b-k[1]) < space):
                avalaible = False
                break
        if avalaible :
            i += 1
            mxy.append((a,b))
            pc = int(i*100/nbSeaProvince)
            sys.stdout.write("\r" + str(pc) + "%" + " "*4)
            sys.stdout.flush()
sys.stdout.write("\n")
print (str(nbSeaProvince) + ' seas')

print ('Make sea provinces :')
sys.stdout.write("...")
sys.stdout.flush()

mpxy = np.array(mxy)

vor = Voronoi(mpxy)


for k, idVRegion in enumerate(vor.point_region):
    if k > 3:
        idProvince += 1
        '''nb = random.randint(0, 2)
        name = random.choice(culture[continent[k]]["province"]["first"])
        for i in range(nb):
            name += random.choice(culture[continent[k]]["province"]["middle"])
        name += random.choice(culture[continent[k]]["province"]["end"])'''
        csvwriter.writerow(["ocean" + str(idProvince)] + [idProvince] + [""] + [-1] + [-1] + list(mxy[k]))# + pos + list(p1) + [alpha] + [length])
        
        vertices = []
        for idVertice in vor.regions[idVRegion]:
            if idVertice >= 0:
                vertices.append(tuple(vor.vertices[idVertice]))
                
        sea.polygon(vertices, fill=id2HexColor(idProvince))
        pc = int(idProvince*100/(nbProvinces+nbSeaProvince))
        sys.stdout.write("\r" + str(pc) + "%" + " "*4)
        sys.stdout.flush()

maskImage = Image.open("mask.png")
result = Image.composite(landImage, seaImage, maskImage)
        
sys.stdout.write("\n")



print ('Save file')
result.save("worldid.png", "PNG")
csvfile.close()
#seaImage.save("sea307.png", "PNG")
print ('Job done')
