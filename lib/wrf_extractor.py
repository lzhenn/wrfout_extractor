#/usr/bin/env python
"""Preprocessing the WRF input file"""

import datetime
import numpy as np
import xarray as xr
import pandas as pd
import netCDF4 as nc4
import wrf  
from copy import copy
import sys, os, subprocess

import lib.utils as utils

print_prefix='lib.preprocess_wrfinp>>'

class wrf_mesh:

    '''
    Construct grid info and UVW mesh template
    
    Attributes
    -----------
    Methods
    '''
    
    def __init__(self, cfg):
        """ construct input wrf file names """
        
        utils.write_log(print_prefix+'Read input files...')
        
        self.lat=float(cfg['EXTRACTOR']['lat'])
        self.lon=float(cfg['EXTRACTOR']['lon'])
        
        self.latstr=cfg['EXTRACTOR']['lat']
        self.lonstr=cfg['EXTRACTOR']['lon']
        
        self.lev_top=float(cfg['EXTRACTOR']['lev_top'])
        
        self.var2d_list=get_varlist(cfg)
        self.var3d_list=get_varlist(cfg,dim='3d')
        
        input_dir=cfg['INPUT']['extractor_input_path']
        self.strt_timestr=cfg['INPUT']['start_time']
        self.end_timestr=cfg['INPUT']['end_time']
        timestamp_start=datetime.datetime.strptime(cfg['INPUT']['start_time'],'%Y%m%d%H')
        timestamp_end=datetime.datetime.strptime(cfg['INPUT']['end_time'],'%Y%m%d%H')
        
        self.dateseries=pd.date_range(start=timestamp_start, end=timestamp_end, freq='H')
        
        self.ntimes=len(self.dateseries)
        self.nvar2d=len(self.var2d_list)
        self.nvar3d=len(self.var3d_list)
        self.outpath=cfg['OUTPUT']['extractor_output_root']

        self.nc_fnlist=[]
        
        for idx, datestamp in enumerate(self.dateseries):
            self.nc_fnlist.append(input_dir+'wrfout_d04_'+datestamp.strftime('%Y-%m-%d_%H:%M:%S')+'_sub')

        self.get_xy()
    
    def extract(self):
        """ extract variable from wrf or subset wrf """
        utils.write_log(print_prefix+'extract variables from wrfout...')
        
       
        # init var2d np array and var3d dict
        var2d_val=np.zeros((self.ntimes,self.nvar2d))
       
        var3d_vdic={'time':[], 'lev':[]}
        for varname in self.var3d_list:
            var3d_vdic[varname]=[]

        for idx, nc_fn in enumerate(self.nc_fnlist):
            utils.write_log(print_prefix+'Read '+nc_fn)
            
            ncfile=nc4.Dataset(nc_fn)
             
            for iv, varname in enumerate(self.var2d_list):
                var=wrf.getvar(ncfile, varname)
                var2d_val[idx, iv]=var.sel(south_north=self.isn, west_east=self.iwe).values
            
            # get idz_max 
            z1d=wrf.getvar(ncfile, 'z').sel(south_north=self.isn, west_east=self.iwe).values
            for iz, z in enumerate(z1d.tolist()):
                if z > self.lev_top:
                    self.idz_max=iz
                    break
            # append datetime col
            var3d_vdic['time']+=[self.dateseries[idx] for i in range(0,iz)]
            # append lev
            var3d_vdic['lev']+=z1d[0:iz].tolist()

            for iv, varname in enumerate(self.var3d_list):
                var=wrf.getvar(ncfile, varname)
                var3d_vdic[varname]+=var.sel(south_north=self.isn, west_east=self.iwe, bottom_top=slice(0,iz)).values.tolist()
                
            ncfile.close()
        df_2d=pd.DataFrame(var2d_val, index=self.dateseries, columns=self.var2d_list)
        df_3d=pd.DataFrame(var3d_vdic, columns=['time', 'lev']+self.var3d_list)
        
        utils.write_log(print_prefix+'Output dataframe...')

        df_2d.to_csv(self.outpath+'/var2d_S'+self.strt_timestr+'E'+self.end_timestr+'_lat'+self.latstr+'_lon'+self.lonstr+'.csv')
        df_3d.to_csv(self.outpath+'/var3d_S'+self.strt_timestr+'E'+self.end_timestr+'_lat'+self.latstr+'_lon'+self.lonstr+'.csv')


    def get_xy(self):
        '''get the aimed xy'''
        temp_fn=self.nc_fnlist[0]
        ncfile = nc4.Dataset(temp_fn)
        xy = wrf.ll_to_xy(ncfile, self.lat, self.lon)
        self.isn=xy[1]
        self.iwe=xy[0]


def get_varlist(cfg, dim='2d'):
    varlist=cfg['EXTRACTOR']['var'+dim].split(',')
    varlist=[ele.strip() for ele in varlist]
    return varlist


if __name__ == "__main__":
    pass
