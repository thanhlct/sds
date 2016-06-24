RUSAGE_SELF = None

def getrusage(a):
    return thanhResource()

import time
class thanhResource:
    def __init__(self):
        self.ru_utime = time.time()
        self.ru_stime = 0
