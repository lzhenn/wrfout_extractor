#/usr/bin/env python
"""Time manager obj to record execution time."""

import time

class time_manager:
    '''
    Time manager object to record execution time
    
    Attributes
    -----------
    tic0, float, absolute start time of the program
    tic, float, absolute start time before each module in runtime
    record, list[i]=(evt_str, dt), runtime duration of each individual event 

    Methods
    -----------
    toc(evt_str), press toc after each event (evt_str)
    dump(), dump time manager object in output stream

    '''

    def __init__(self):
        """construct time manager object"""
        self.tic0=time.time()
        self.tic=self.tic0
        self.record={}

    def toc(self, evt_str):
        """press toc after each event (evt_str)"""
        if evt_str in self.record:
            self.record[evt_str]['ntimes']=self.record[evt_str]['ntimes']+1
            self.record[evt_str]['elapsed']=self.record[evt_str]['elapsed']+time.time()-self.tic
        else:
            self.record[evt_str]={}
            self.record[evt_str]['ntimes']=1
            self.record[evt_str]['elapsed']=time.time()-self.tic
        
        self.tic=time.time()


    def dump(self):
        """Dump time manager object in output stream"""
        fmt='%20s:%10.4fs%6dx%6.1f%%'
        print('\n----------------TIME MANAGER PROFILE----------------\n\n')
        total_t=time.time()-self.tic0
        for key,value in self.record.items():
            print(fmt % (key,value['elapsed']/value['ntimes'],value['ntimes'],100.0*value['elapsed']/total_t))
        print(fmt % ('TOTAL ELAPSED TIME', total_t, 1, 100.0))
        print('\n----------------TIME MANAGER PROFILE----------------\n\n')
