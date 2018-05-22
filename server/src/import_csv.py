from mongoengine import *
import importlib
import ast

def import_csv(file):
    #import pdb;pdb.set_trace()
    cl = file.split('.')[0]
    mod = importlib.import_module(cl)

    with open(file, 'r') as f:
        header = f.readline().strip().split(";")
        for li in f.readlines():
            li = li.strip()
            tab_li = li.split(";")
            d = {}
            for i in range(len(tab_li)):
                if tab_li[i][0] == "[":
                    a = tab_li[i][1:-1]
                    if a:
                        t = a.split(",")
                        d[header[i]] = t
                elif tab_li[i][0] == "{":
                    t = ast.literal_eval(tab_li[i])
                    d[header[i]] = t
                else:
                    if tab_li[i] != 'null':
                        d[header[i]] = tab_li[i]
            obj = getattr(mod, cl.title())(**d)
            obj.save()
            print("saved")


db = connect ('histemul')
db.drop_database('histemul')
connect ('histemul')
import_csv('province.csv')
import_csv('culture.csv')
import_csv('title.csv')
import_csv('land.csv')
import_csv('player.csv')
import_csv('person.csv')




