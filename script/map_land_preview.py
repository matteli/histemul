import os

for i in range(10000):
    os.popen("./gengif "+ str(i) + " 2000 300 75")
