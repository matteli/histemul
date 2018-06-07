def merge_qsets(*args):
    qset = []
    for a in args:
        if a:
            try:
                qset += a
            except:
                qset = a
    return qset

def bool_random(true, on=1):
    return random.choices([True,False],cum_weights=[true,on])[0]