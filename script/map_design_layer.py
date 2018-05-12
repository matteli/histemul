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
import shlex, subprocess
#from PIL import Image, ImageFilter

'''img = Image.open('worldid.png')

img = img.filter(ImageFilter.CONTOUR)
img.save('color.png')
img = img.convert('L')
mask = img.point(lambda i: 0 if (i == 0) else 255)
img.save('dd.png')
mask.save('worldedge.png')'''

print("1/5")
#p = subprocess.Popen(shlex.split("convert worldid.png -morphology Convolve Laplacian:0 -threshold 0.1 -morphology Edge Octagon:1 -negate worldedge.png"))
p = subprocess.Popen(shlex.split("convert worldid.png  -morphology Edge Disk:1.0 -threshold 0.1 -negate worldedge.png"))
p.wait()
print("2/5")
p = subprocess.Popen(shlex.split("convert worldedge.png -blur 0x2 -shade 115x30 worldtemp1.png"))
p.wait()
print("3/5")

p = subprocess.Popen(shlex.split("convert worldedge.png -blur 0x20 -level 65%,100% worldtemp2.png"))
p.wait()
print("4/5")
p = subprocess.Popen(shlex.split("composite -compose multiply worldtemp1.png worldtemp2.png worldshading.png"))
p.wait()

print("5/5")
p = subprocess.Popen(shlex.split("convert worldid.png  -morphology Edge Disk:3.0 -threshold 0.1 worldborder.png"))
p.wait()
print("Finish")


