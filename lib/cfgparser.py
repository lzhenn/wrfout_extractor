#/usr/bin/env python3
"""configuration funcs to get parameters from user"""
import os
import configparser
import lib.utils as utils

print_prefix='lib.cfgparser>>'

def read_cfg(config_file):
    """ Simply read the config files """
    config=configparser.ConfigParser()
    config.read(config_file)
    return config

def write_cfg(cfg_hdl, config_fn):
    """ Simply write the config files """
    with open(config_fn, 'w') as configfile:
        cfg_hdl.write(configfile)

def merge_cfg(cfg_org, cfg_tgt):
    """ merge the dynamic and static cfg """
    cfg_tgt['INPUT']=cfg_org['INPUT']
    cfg_tgt['CORE']['interp_strt_t']=cfg_org['CORE']['interp_strt_t']
    cfg_tgt['CORE']['interp_t_length']=cfg_org['CORE']['interp_t_length']
    cfg_tgt['CORE']['interp_interval']=cfg_org['CORE']['interp_interval']
    
    return cfg_tgt


def cfg_valid_test(cfg):
    """ test if the cfg file is valid """

    # test input obv.csv exists
    input_file=cfg['INPUT']['input_root']+cfg['INPUT']['input_obv']
    if not(os.path.exists(input_file)):
        utils.throw_error(print_prefix, 'cannot locate:'+input_file)

    template_file='./db/'+cfg['INPUT']['input_wrf']
    
    # test wrf template exists
    if not(os.path.exists(template_file)):
        utils.throw_error(print_prefix, 'cannot locate:'+template_file)
    
    # test reasonable integration time
    t_interp=int(cfg['CORE']['interp_t_length'])
    if t_interp>120:
        utils.write_log(print_prefix+'interp_t_length='+str(t_interp)+' is larger than 120 hr',lvl=30)

    if t_interp>168 or t_interp<0:
        utils.throw_error(print_prefix,'interp_t_length='+str(t_interp)+', not allowed > 168 hr or < 0 hr')

    # test reasonable interp interval
    interp_interval=int(cfg['CORE']['interp_interval'])
    if interp_interval>180 or interp_interval<1:
        utils.throw_error(print_prefix,'interp_interval='+str(interp_interval)+', not allowed > 180 min or < 1 min')
