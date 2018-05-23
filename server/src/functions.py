def merge_qsets(*args):
    qset = []
    for a in args:
        if a:
            try:
                qset += a
            except:
                qset = a
    return qset
