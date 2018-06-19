import random

def merge_qsets(*args):
    qset = []
    for arg in args:
        if arg:
            try:
                qset += arg
            except:
                qset = arg
    return qset

def bool_random(true, on=1):
    return random.choices([True, False], cum_weights=[true, on])[0]
