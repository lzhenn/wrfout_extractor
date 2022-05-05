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

class WRFMesh:

    '''
    Construct grid info and UVW mesh template
    
    Attributes
    -----------
    Methods
    '''
    
    def __init__(self, cfg):
        """ construct input wrf file names """
        
        utils.write_log(print_prefix+'Read input files...')
        
        self.mean_flag=cfg['EXTRACTOR'].getboolean('area_mean_flag') 
        if (self.mean_flag):
        
            self.lat_bottom_str=cfg['SLICER']['lat_bottom']
            self.lat_top_str=cfg['SLICER']['lat_top']
            self.lon_left_str=cfg['SLICER']['lon_left']
            self.lon_right_str=cfg['SLICER']['lon_right']
            
            self.lat_bottom=float(cfg['SLICER']['lat_bottom'])
            self.lat_top=float(cfg['SLICER']['lat_top'])
            self.lon_left=float(cfg['SLICER']['lon_left'])
            self.lon_right=float(cfg['SLICER']['lon_right'])

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
            self.nc_fnlist.append(input_dir+'wrfout_d04_'+datestamp.strftime('%Y-%m-%d_%H:%M:%S'))
            #self.nc_fnlist.append(input_dir+'wrfout_d04_'+datestamp.strftime('%Y-%m-%d_%H:%M:%S')+'_sub')

        if (self.mean_flag):
            self.get_vertex()
        else:
            self.get_xy()
    
    def extract(self):
        """ extract variable from wrf or subset wrf """
        utils.write_log(print_prefix+'extract variables from wrfout...')
       
        # init var2d np array and var3d dict
        var2d_val=np.zeros((self.ntimes,self.nvar2d))
       
        var3d_vdic={'time':[], 'lev':[]}
        for varname in self.var3d_list:
            var3d_vdic[varname]=[]

        # read meta data
        if not(self.mean_flag):
            ncfile=nc4.Dataset(self.nc_fnlist[0])
            lsmask=wrf.getvar(ncfile, 'LANDMASK')
            self.lsmask=lsmask.sel(south_north=self.isn, west_east=self.iwe).values
            luid=wrf.getvar(ncfile, 'LU_INDEX')
            self.luid=luid.sel(south_north=self.isn, west_east=self.iwe).values
            ncfile.close()
            
        for idx, nc_fn in enumerate(self.nc_fnlist):
            utils.write_log(print_prefix+'Read '+nc_fn)
            
            ncfile=nc4.Dataset(nc_fn)
             
            for iv, varname in enumerate(self.var2d_list):
                var=wrf.getvar(ncfile, varname)
                if self.mean_flag:
                    var2d_val[idx,iv]=var.sel(south_north=slice(self.xy_strt[1],self.xy_end[1]), 
                    west_east=slice(self.xy_strt[0],self.xy_end[0])).mean(('south_north', 'west_east')).values

                else:
                    var2d_val[idx, iv]=var.sel(south_north=self.isn, west_east=self.iwe).values
            
            # get idz_max 
            z1d=wrf.getvar(ncfile, 'z')
            if self.mean_flag:
                z1d=z1d.sel(south_north=slice(self.xy_strt[1],self.xy_end[1]), 
                    west_east=slice(self.xy_strt[0],self.xy_end[0])).mean(('south_north', 'west_east')).values
            else:
                z1d=z1d.sel(south_north=self.isn, west_east=self.iwe).values
            
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
                if self.mean_flag:
                    var3d_vdic[varname]+=var.sel(south_north=slice(self.xy_strt[1],self.xy_end[1]), 
                    west_east=slice(self.xy_strt[0],self.xy_end[0]),
                    bottom_top=slice(0,iz)).mean(('south_north', 'west_east')).values.tolist()
                else:
                    var3d_vdic[varname]+=var.sel(south_north=self.isn, west_east=self.iwe, bottom_top=slice(0,iz)).values.tolist()
                
            ncfile.close()
        df_2d=pd.DataFrame(var2d_val, index=self.dateseries, columns=self.var2d_list)
        df_3d=pd.DataFrame(var3d_vdic, columns=['time', 'lev']+self.var3d_list)
        
        utils.write_log(print_prefix+'Output dataframe...')
        if self.mean_flag:
            df_2d.to_csv(self.outpath+'/var2d_S'+self.strt_timestr+'E'+self.end_timestr+'_lat'+self.lat_bottom_str+'-'+self.lat_top_str+'_lon'+self.lon_left_str+'-'+self.lon_right_str+'.csv')
            df_3d.to_csv(self.outpath+'/var3d_S'+self.strt_timestr+'E'+self.end_timestr+'_lat'+self.lat_bottom_str+'-'+self.lat_top_str+'_lon'+self.lon_left_str+'-'+self.lon_right_str+'.csv')
        
        else:
            df_2d.to_csv(self.outpath+'/var2d_S'+self.strt_timestr+'E'+self.end_timestr+'_lat'+self.latstr+'_lon'+self.lonstr+'.csv')
            df_3d.to_csv(self.outpath+'/var3d_S'+self.strt_timestr+'E'+self.end_timestr+'_lat'+self.latstr+'_lon'+self.lonstr+'.csv')
        
            with open(self.outpath+'/ReadMe_S'+self.strt_timestr+'E'+self.end_timestr+'_lat'+self.latstr+'_lon'+self.lonstr+'.csv', 'w') as f:
                f.write('Extractor for lat: '+self.latstr+', lon: '+self.lonstr+',\n')
                f.write('found nearest grid lat:'+str(self.ilat.values)+', lon: '+str(self.ilon.values)+',\n')
                f.write('grid landsea mask (1-land 0 water):'+str(self.lsmask)+', and land use code: '+str(self.luid)+',\n')
                f.write('with grid irow:'+str(self.isn.values)+', icol: '+str(self.iwe.values)+' in WRF mesh.\n')


    def get_xy(self):
        '''get the aimed xy'''
        temp_fn=self.nc_fnlist[0]
        ncfile = nc4.Dataset(temp_fn)
        xy = wrf.ll_to_xy(ncfile, self.lat, self.lon)
        self.isn=xy[1]
        self.iwe=xy[0]
        ll = wrf.xy_to_ll(ncfile, self.iwe, self.isn)
        self.ilat=ll[0]
        self.ilon=ll[1]

    def get_vertex(self):
        ''' get the vertex xyz '''
        temp_fn=self.nc_fnlist[0]
        ncfile = nc4.Dataset(temp_fn)
        xy = wrf.ll_to_xy(ncfile, self.lat_bottom, self.lon_left)
        xy2 = wrf.ll_to_xy(ncfile, self.lat_top, self.lon_right)
        self.xy_strt=xy.values
        self.xy_end=xy2.values
     
        ncfile.close()


def get_varlist(cfg, dim='2d'):
    varlist=cfg['EXTRACTOR']['var'+dim].split(',')
    varlist=[ele.strip() for ele in varlist]
    return varlist


if __name__ == "__main__":
    pass
