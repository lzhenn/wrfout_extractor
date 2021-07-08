#/usr/bin/env python
"""Preprocessing the WRF input file"""

import datetime
import numpy as np
import xarray as xr
import pandas as pd
import netCDF4 as nc4
import wrf  
import sys, os, subprocess
import lib.utils as utils
print_prefix='lib.wrf_slicer>>'

class WRFMesh:

    '''
    Construct grid info and UVW mesh template
    
    Attributes
    -----------
    Methods
    '''
    
    def __init__(self, cfg):
        """ construct input wrf file names """
        
        utils.write_log(print_prefix+'Init wrf_mesh obj...')
        
        input_dir=cfg['INPUT']['slicer_input_path']

        timestamp_start=datetime.datetime.strptime(cfg['INPUT']['start_time'],'%Y%m%d%H')
        timestamp_end=datetime.datetime.strptime(cfg['INPUT']['end_time'],'%Y%m%d%H')
        self.dateseries=pd.date_range(start=timestamp_start, end=timestamp_end, freq='H')


        self.nc_fnlist=[]

        self.lat_bottom=float(cfg['SLICER']['lat_bottom'])
        self.lat_top=float(cfg['SLICER']['lat_top'])
        self.lon_left=float(cfg['SLICER']['lon_left'])
        self.lon_right=float(cfg['SLICER']['lon_right'])

        self.out_dir=cfg['OUTPUT']['slicer_output_root']

        for idx, datestamp in enumerate(self.dateseries):
            self.nc_fnlist.append(input_dir+'wrfout_d04_'+datestamp.strftime('%Y-%m-%d_%H:%M:%S'))

        self.get_vertex()

    def pare(self):
        """ pare the subset wrfout according to configurations """
        utils.write_log(print_prefix+'pare the wrfout...')

        for idx, nc_fn in enumerate(self.nc_fnlist):
            utils.write_log(print_prefix+'Read '+nc_fn)

            ds=xr.load_dataset(nc_fn)
            
            ds=ds.sel(south_north=slice(self.xy_strt[1],self.xy_end[1]), 
                    west_east=slice(self.xy_strt[0],self.xy_end[0]),
                    south_north_stag=slice(self.xy_strt[1],self.xy_end[1]+1),
                    west_east_stag=slice(self.xy_strt[0],self.xy_end[0]+1))
            
            utils.write_log(print_prefix+'Write subset...')
            nc_fullname=nc_fn.split('/')[-1]
            ds.to_netcdf(self.out_dir+'/'+nc_fullname+'_sub')
            
            
    def get_vertex(self):
        ''' get the vertex xyz '''
        temp_fn=self.nc_fnlist[0]
        ncfile = nc4.Dataset(temp_fn)
        xy = wrf.ll_to_xy(ncfile, self.lat_bottom, self.lon_left)
        xy2 = wrf.ll_to_xy(ncfile, self.lat_top, self.lon_right)
        self.xy_strt=xy.values
        self.xy_end=xy2.values
     
        ncfile.close()
if __name__ == "__main__":
    pass
