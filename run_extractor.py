#!/home/metctm1/array/soft/anaconda3/bin/python
'''
Date: June 14, 2021
WRF extractor for subset nc and csv files


Revision:
June 14, 2021 --- MVP
Zhenning LI
'''

import numpy as np
import pandas as pd
import os, logging.config

import lib 
import lib.utils as utils

def main_run():
    
    print('*************************WRFOUT EXTRACTOR START*************************')
       
    # wall-clock ticks
    time_mgr=lib.time_manager.time_manager()
    
    # logging manager
    logging.config.fileConfig('./conf/logging_config.ini')
    
    utils.write_log('Read Config...')
    cfg_hdl=lib.cfgparser.read_cfg('./conf/config.ini')
   
    wrf_extractor=lib.wrf_extractor.WRFMesh(cfg_hdl)
    wrf_extractor.extract()

    print('*********************WRFOUT EXTRACTOR ACCOMPLISHED*********************')

if __name__=='__main__':
    main_run()
