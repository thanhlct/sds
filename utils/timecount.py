'''
Time Couting
'''
import resource

class TimeStats(object):
    def __init__(self):
        self.init_update()
    
    def init_update(self):
        self.clocks = {}
        self.clocks_temp = {}
    
    def start_clock(self,name):
        self.clocks_temp[name] = self._CPU()

    def end_clock(self,name):
        if (name in self.clocks):
            self.clocks[name] += self._CPU() - self.clocks_temp[name]
        else:
            self.clocks[name] = self._CPU() - self.clocks_temp[name]
    def _CPU(self):
        return (resource.getrusage(resource.RUSAGE_SELF).ru_utime+
                resource.getrusage(resource.RUSAGE_SELF).ru_stime)

