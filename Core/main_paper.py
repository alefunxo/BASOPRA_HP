# -*- coding: utf-8 -*-
## @namespace main_paper
# Created on Wed Feb 28 09:47:22 2018
# Author
# Alejandro Pena-Bello
# alejandro.penabello@unige.ch
# Modification of main script used for the paper Optimized PV-coupled battery systems for combining applications: Impact of battery technology and geography (Pena-Bello et al 2019).
# This enhancement includes the use of HP and thermal storage together with the previously assessed PV and battery system. We study the different applications which residential batteries can perform from a consumer perspective. Applications such as avoidance of PV curtailment, demand load-shifting and demand peak shaving are considered along  with the base application, PV self-consumption. It can be used with six different battery technologies currently available in the market are considered as well as three sizes (3 kWh, 7 kWh and 14 kWh). We analyze the impact of the type of demand profile and type of tariff structure by comparing results across dwellings in Switzerland.
# The HP, battery and TS schedule is optimized for every day (i.e. 24 h optimization framework), we assume perfect day-ahead forecast of the electricity and heat demand load and solar PV generation in order to determine the maximum economic potential regardless of the forecast strategy used. Battery aging was treated as an exogenous parameter, calculated on daily basis and was not subject of optimization. Data with 15-minute temporal resolution were used for simulations. The model objective function have two components, the energy-based and the power-based component, as the tariff structure depends on the applications considered, a boolean parameter activate the power-based factor of the bill when is necessary.

# The script works in Linux and Windows
# This script works was tested with pyomo version 5.4.3
# INPUTS
# ------
# OUTPUTS
# -------
# TODO
# ----
# User Interface, including path to save the results and choose countries, load curves, etc.
# Simplify by merging select_data and load_data and probably load_param.
# Requirements
# ------------
#  Pandas, numpy, sys, glob, os, csv, pickle, functools, argparse, itertools, time, math, pyomo and multiprocessing



import os
import pandas as pd
import argparse
import numpy as np
import itertools
import sys
import glob
import multiprocessing as mp
import time
import paper_classes as pc
from functools import wraps
from pathlib import Path
import traceback
import pickle
import csv
from Core_LP import single_opt2
import post_proc as pp

def fn_timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print ("Total time running %s: %s seconds" %
               (function.__name__, str(t1-t0))
               )
        return result
    return function_timer

def expand_grid(dct):
    rows = itertools.product(*dct.values())
    return pd.DataFrame.from_records(rows, columns=dct.keys())

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")

def load_obj(name ):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)

def load_param(combinations):
    '''
    Description
    -----------
    Load all parameters into a dictionary, if aging is present (True) or not
    (False), percentage of curtailment, Inverter and Converter efficiency, time
    resolution (0.25), number of years or days if only some days want to be
    optimized, applications, capacities and technologies to optimize.

    Applications are defined as a Boolean vector, where a True activates the
    corresponding application. PVSC is assumed to be always used. The order
    is as follows: [PVCT, PVSC, DLS, DPS]
	i.e PV avoidance of curtailment, PV self-consumption,
	Demand load shifting and demand peak shaving.
    [0,1,0,0]-0
    [0,1,0,1]-1
    [0,1,1,0]-2
    [0,1,1,1]-3
    [1,1,0,0]-4
    [1,1,0,1]-5
    [1,1,1,0]-6
    [1,1,1,1]-7


    Parameters
    ----------
    PV_nominal_power : int

    Returns
    ------
    param: dict
    Comments
    -----
    week 18 day 120 is transtion from cooling to heating
    week 40 day 274 is transtion from cooling to heating
    '''
    print('##############')
    print('load data')
    id_dwell=str(int(combinations['hh']))
    print(id_dwell)
    [clusters,PV,App_comb_df,conf,house_types,hp_types,rad_types]=pp.get_table_inputs()

    PV_nom=PV[PV.PV==combinations['PV_nom']].PV.values[0]
    quartile=PV[(PV.PV==combinations['PV_nom'])&(PV.country==combinations['country'])].quartile.values[0]
    App_comb=[str2bool(i) for i in App_comb_df[App_comb_df.index==int(combinations['App_comb'])].App_comb.values[0].split(' ')]
#####################################################
    design_param=load_obj('Input/dict_design')
    aging=True
    Inverter_power=round(PV_nom/1.2,1)
    Curtailment=0.5
    Inverter_Efficiency=0.95
    Converter_Efficiency_HP=0.98
    dt=0.25
    Capacity_tariff=9.39*12/365*2
    nyears=1
    days=365
    testing=False
    cooling=False
    week=47
######################################################

    filename_el=Path('Input/Electricity_demand_supply_2017.csv')
    filename_heat=Path('Input/preprocessed_heat_demand_2017.csv')
    filename_prices=Path('Input/Prices_2017.csv')

    fields_el=['index',id_dwell,'E_PV']
    new_cols=['E_demand', 'E_PV']

    df_el = pd.read_csv(filename_el,engine='python',sep=',|;',index_col=0,
                        parse_dates=[0],infer_datetime_format=True, usecols=fields_el)

    if np.issubdtype(df_el.index.dtype, np.datetime64):
        df_el.index=df_el.index.tz_localize('UTC').tz_convert('Europe/Brussels')
    else:
        df_el.index=pd.to_datetime(df_el.index,utc=True)
        df_el.index=df_el.index.tz_convert('Europe/Brussels')

    df_el.columns=new_cols

    if (combinations['house_type']=='SFH15')| (combinations['house_type']=='SFH45'):
        aux_name='SFH15_45'
    else:
        aux_name='SFH100'

    fields_heat=['index','Set_T','Temp', combinations['house_type']+'_kWh','DHW_kWh', 'Temp_supply_'+aux_name,'Temp_supply_'+aux_name+'_tank',
                'COP_'+combinations['house_type'],'hp_'+combinations['house_type']+'_el_cons','COP_'+combinations['house_type']+'_DHW',
                 'hp_'+combinations['house_type']+'_el_cons_DHW','COP_'+combinations['house_type']+'_tank',
                 'hp_'+combinations['house_type']+'_tank_el_cons']
    new_cols=['Set_T','Temp', 'Req_kWh','Req_kWh_DHW','Temp_supply','Temp_supply_tank','COP_SH','COP_tank','COP_DHW',
              'hp_sh_cons','hp_tank_cons','hp_dhw_cons']
    df_heat=pd.read_csv(filename_heat,engine='python',sep=';',index_col=[0],
                        parse_dates=[0],infer_datetime_format=True, usecols=fields_heat)
    df_heat.columns=new_cols


    if np.issubdtype(df_heat.index.dtype, np.datetime64):
        df_heat.index=df_heat.index.tz_localize('UTC').tz_convert('Europe/Brussels')
    else:
        df_heat.index=pd.to_datetime(df_heat.index,utc=True)
        df_heat.index=df_heat.index.tz_convert('Europe/Brussels')

    fields_prices=['index', 'Price_flat', 'Price_DT', 'Export_price', 'Price_flat_mod',
   'Price_DT_mod']
    df_prices=pd.read_csv(filename_prices,engine='python',sep=',|;',index_col=[0],
                        parse_dates=[0],infer_datetime_format=True ,usecols=fields_prices)

    if np.issubdtype(df_prices.index.dtype, np.datetime64):
        df_prices.index=df_prices.index.tz_localize('UTC').tz_convert('Europe/Brussels')
    else:
        df_prices.index=pd.to_datetime(df_prices.index,utc=True)
        df_prices.index=df_prices.index.tz_convert('Europe/Brussels')

    data_input=pd.concat([df_el,df_heat,df_prices],axis=1,copy=True,sort=False)
    #skip the first DHW data since cannot be produced simultaneously with SH
    data_input.loc[(data_input.index.hour<2),'Req_kWh_DHW']=0
    T_var=data_input.Temp.resample('1d').mean()
    data_input.loc[:,'E_PV']=data_input.loc[:,'E_PV']*PV_nom
    data_input['T_var']=T_var
    data_input.T_var=data_input.T_var.fillna(method='ffill')
    data_input['Cooling']=0
    data_input.loc[((data_input.index.month<=4)|(data_input.index.month>=10))&(data_input.Req_kWh<0),'Req_kWh']=0
    if cooling:
        data_input.loc[(data_input.index.month>4)&(data_input.index.month<10)&(data_input.T_var>20),'Cooling']=1#is T_var>20 then we need to cool only
        data_input.loc[(data_input.Cooling==1)&(data_input.Req_kWh>0),'Req_kWh']=0#if we should cool then ignore the heating requirements
        data_input.loc[(data_input.Cooling==1),'Req_kWh']=abs(data_input.loc[(data_input.Cooling==1),'Req_kWh'])

    data_input.loc[(data_input.index.month>4)&(data_input.index.month<10)&(data_input.Cooling==0),'Req_kWh']=0#if we should heat then ignore the cooling requirements
    data_input['Temp']=data_input['Temp']+273.15
    data_input['Set_T']=data_input['Set_T']+273.15
    data_input['Temp_supply']=data_input['Temp_supply']+273.15
    data_input['Temp_supply_tank']=data_input['Temp_supply_tank']+273.15
    data_input.loc[data_input.index.dayofyear==120,'Req_kWh']=0
    data_input.loc[data_input.index.dayofyear==274,'Req_kWh']=0
    data_input.loc[(data_input.index.dayofyear<120)|(data_input.index.dayofyear>274),'season']=0#'heating'
    data_input.loc[data_input.index.dayofyear==120,'season']=1#'transition_heating_cooling'
    data_input.loc[(data_input.index.dayofyear>120)&(data_input.index.dayofyear<274),'season']=2#'cooling'
    data_input.loc[data_input.index.dayofyear==274,'season']=3#'transition_cooling_heating'
    if data_input[((data_input.index.dayofyear<120)|(data_input.index.dayofyear>274))&(data_input.Temp_supply==data_input.Temp_supply_tank)].empty==False:
        data_input.loc[((data_input.index.dayofyear<120)|(data_input.index.dayofyear>274))&(data_input.Temp_supply==data_input.Temp_supply_tank),'Temp_supply_tank']+=1.5

    if testing:
        data_input=data_input[data_input.index.week==week]
        nyears=1
        days=7
        ndays=7

    print('##############')
    print('load parameters')
    conf=combinations['conf']
    print('conf')
    print(conf)

    #configuration=[Batt,HP,TS,DHW]
    #if all false, only PV
    conf_aux=[False,True,False,False]#[Batt,HP,TS,DHW]

    if conf<4:#No battery
        #print('inside batt')
        Converter_Efficiency_Batt=1
    else:
        conf_aux[0]=True
        Converter_Efficiency_Batt=0.98

    if (conf!=0)&(conf!=1)&(conf!=4)&(conf!=5):#TS present
        #print('inside TS')
        conf_aux[2]=True

        tank_sh=pc.heat_storage_tank(mass=1500,surface=5.6) # For a 1500 liter tank with 1.426 m height and 1.25 diameter
        T_min_cooling=285.15#12°C
    else:#No TS
        tank_sh=pc.heat_storage_tank(mass=0, surface=0.41)# For a 50 liter tank with .26 m height and .25 diameter
        T_min_cooling=0

    if (conf==1)|(conf==3)|(conf==5)|(conf==7):#DHW present
        #print('inside DHW')
        conf_aux[3]=True
        tank_dhw=pc.heat_storage_tank(mass=200, t_max=60+273.15, t_min=40+273.15,surface=1.6564) # For a 200 liter tank with 0.95 m height and .555 diameter
        if (conf==1)|(conf==5):
            if combinations['house_type']=='SFH15':
                tank_sh=pc.heat_storage_tank(mass=100, surface=1.209)# For a 100 liter tank with  .52m height and .25 diameter
            elif combinations['house_type']=='SFH45':
                tank_sh=pc.heat_storage_tank(mass=200, surface=1.913)# For a 200 liter tank with .52 m height and .35 diameter
            elif combinations['house_type']=='SFH100':
                tank_sh=pc.heat_storage_tank(mass=400, surface=3.2)# For a 50 liter tank with .52 m height and .5 diameter
    else:#No DHW
        tank_dhw=pc.heat_storage_tank(mass=1, t_max=0, t_min=0,specific_heat_dhw=0,U_value_dhw=0,surface_dhw=0)#null

    ndays=days*nyears
    print(data_input.head())
    if combinations['HP']=='AS':
        if combinations['house_type']=='SFH15':
            Backup_heater=design_param['bu_15']+6
            hp=pc.HP_tech(technology='ASHP',power=design_param['hp_15'])
        elif combinations['house_type']=='SFH45':
            Backup_heater=design_param['bu_45']+5
            hp=pc.HP_tech(technology='ASHP',power=design_param['hp_45'])
        else:
            Backup_heater=design_param['bu_100']
            hp=pc.HP_tech(technology='ASHP',power=design_param['hp_100'])
    elif combinations['HP']=='GSHP':
        #TODO
        pass
    param={'conf':conf_aux,
    'aging':aging,'Inv_power':Inverter_power,
    'Curtailment':Curtailment,'Inverter_eff':Inverter_Efficiency,
    'Converter_Efficiency_HP':Converter_Efficiency_HP,
    'Converter_Efficiency_Batt':Converter_Efficiency_Batt,
    'delta_t':dt,'nyears':nyears,'T_min_cooling':T_min_cooling,
    'days':days,'ndays':ndays,'hp':hp,'tank_dhw':tank_dhw,'tank_sh':tank_sh,
    'Backup_heater':Backup_heater,'Capacity':combinations['Capacity'],'Tech':combinations['Tech'],
    'App_comb':App_comb,'cases':combinations['cases'],'ht':combinations['house_type'],
    'HP_type':combinations['HP'],'testing':testing, 'Cooling_ind':cooling,'name':str(id_dwell)+'_'+combinations['country']+'_PV'+str(quartile),
    'PV_nom':PV_nom,'Capacity_tariff':Capacity_tariff}
    return param,data_input

def pooling2(combinations):
    '''
    Description
    -----------
    Calls other functions, load the data and Core_LP.
    This function includes the variables for the tests (testing and data_input.index.week)
    Parameters
    ----------
    selected_dwellings : dict

    Returns
    ------
    bool
        True if successful, False otherwise.


    '''

    print('##########################################')
    print('pooling')
    print(combinations)
    print('##########################################')
    param,data_input=load_param(combinations)
    try:
        if param['nyears']>1:
            data_input=pd.DataFrame(pd.np.tile(pd.np.array(data_input).T,
                                   param['nyears']).T,columns=data_input.columns)
        print('#############pool################')
        print(param['tank_dhw'].mass)
        print(param['tank_sh'].mass)
        [df,aux_dict]=single_opt2(param,data_input)
        print('out of optimization')
    except IOError as e:
        print ("I/O error({0}): {1}".format(e.errno, e.strerror))
        raise

    except :
        print ("Back to main.")
        raise
    return


@fn_timer
def main():
    '''
    Main function of the main script. Allows the user to select the country
	(CH or US). For the moment is done automatically if working in windows
	the country is US. It opens a pool of 4 processes to process in parallel, if several dwellings are assessed.
    '''
    print(os.getcwd())
    print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
    print('Welcome to basopra')
    print('Here you will able to optimize the schedule of PV-coupled HP systems with electric and/or thermal storage for a given electricity demand')

    try:
        filename=Path('Output/aggregated_results.csv')
        df_done=pd.read_csv(filename,sep=';|,',engine='python',index_col=False).drop_duplicates()
        #df_done.drop(df_done.tail(2).index,inplace=True)
        aux=df_done.groupby([df_done.Capacity,df_done.App_comb,df_done.Tech,df_done.PV_nom,df_done.cluster,df_done.hh,df_done.country,df_done.cases,df_done.conf,df_done.HP,df_done.house_type]).size().reset_index()
    except IOError:
        #There is not such a file, then create it
        cols=['E_PV_batt','E_PV_bu','E_PV_budhw','E_PV_curt','E_PV_grid','E_PV_hp','E_PV_hpdhw','E_PV_load','E_batt_bu','E_batt_budhw','E_batt_hp','E_batt_hpdhw','E_batt_load','E_bu','E_budhw','E_char','E_cons','E_dis','E_grid_batt','E_grid_bu','E_grid_budhw','E_grid_hp','E_grid_hpdhw','E_grid_load','E_hp','E_hpdhw','E_loss_Batt','E_loss_conv','E_loss_inv','E_loss_inv_PV','E_loss_inv_batt','E_loss_inv_grid','Q_dhwst_hd','Q_hp_sh','Q_hp_ts','Q_loss_dhwst','Q_loss_ts','Q_ts','Q_ts_delta','Q_ts_sh','T_dhwst','T_ts','E_demand','E_PV','Req_kWh','Req_kWh_DHW','Set_T','Temp','Temp_supply','Temp_supply_tank','T_aux_supply','COP_tank','COP_SH','COP_DHW','E_demand_hp_pv_dhw','E_demand_hp_pv','E_demand_pv','TSC','DSC','ISC','CU','EFC_nolifetime','BS','LS1','LS2','LS3','LS4','LS5','PS1','PS2','PS3','PS4','PS5','App_comb','conf','Capacity','Tech','PV_nom','cluster','hh','country','quartile','cases','house_type','HP','SOC_mean','P_drained_max','P_injected_max','last_cap','cap_fading','last_SOH','cycle_to_total','Bill']
        with open(filename, "w+") as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(cols)

        aux=pd.DataFrame()
    finally:
        #Define the different combinations of inputs to be run
        #dct={'Capacity':[7.],'App_comb':[3],'Tech':['NMC',],'PV_nom':[4.8],'cluster':['[11]'],'country':['CH'],'cases':[False],'conf':[5.],'house_type':['SFH15'],'HP':['AS']}
        dct={'Capacity':[7.],'App_comb':[3],'Tech':['NMC',],'PV_nom':[4.8],'country':['CH'],'cases':['mean'],'conf':[2,4,6,7],'house_type':['SFH100','SFH45','SFH15'],'HP':['AS'],'hh':[110143956137, 110696729111, 110699430256, 110696128856, 110146056594, 110697329480, 1127345129698, 110698629959, 110699130150, 110699130179, 110145156465, 110697129372, 110699430252, 110141955895, 110698830059, 110696729126, 1127343129680, 110698329854, 110698129793, 110696929241, 1127342129671, 1127351129756, 1127344129690, 110696328886, 110145456531, 110696428972, 110696529000, 110697529546, 110698830056, 110696529033, 110697029326, 110696929265, 110145156468, 110143956140, 110697129369, 110142556018, 110698129799, 110697729654, 110145456526, 110698429912, 110696629081, 110144356264, 110144556322, 110698329858, 110142956058, 110143956143, 110699430243, 110144856407, 110697029318, 110697129350, 1127348129729, 1127345129705, 1127343129678, 110697329441, 110698830063, 110142956059, 110696328882, 110696529027, 110141755842, 110145356503, 110698629962, 110143556102, 110142355939, 110697529550, 110697129375, 110144356267, 110696128849, 110144756372, 1127346129712, 110698429916, 110697929733, 110696328876, 110699330240, 110699130169, 110696428960, 1127350129746, 1127345129700, 110141955897, 1127353129781, 110697629607, 110698830065, 110696529007, 110696829161, 110142355940, 110143556103, 110142756041, 1127342129672, 110698129801, 110698329861, 1127342129669, 1127341129655, 110144856411, 110696929206, 1127343129676, 1127347129716, 110698629965, 110696729145, 110696929283, 110697929737, 110145556546, 110696528993, 110697329444, 110698830067, 110696929232, 110696929258, 110697329486, 110144356269, 1127345129695, 110696829200, 110697529557, 110696729103, 110144756374, 110142956061, 1127341129660, 110141755854, 110698529920, 110141755863, 110696529022, 110698830069, 110145256477, 110141955898, 110696629073, 110143956145, 110142355941, 1127345129703, 110143556104, 110145456522, 1127348129725, 110696629051, 110698329867, 110699230205, 110698129805, 1127355129784, 110142756042, 110697029312, 110696629067, 110145656576, 110697629613, 110145056430, 110697129381, 110697329488, 110698830071, 110697329446, 110145256480, 110696128842, 110141955877, 110144756376, 110697829674, 110696829194, 110699130162, 110699330238, 110696128864, 110696128835, 1127343129683, 110697129344, 110144356270, 110142756043, 110697929745, 110696529044, 110142956062, 110141755847, 110698529926, 1127344129688, 110696428966, 110698830073, 110142355942, 110698629973, 110696428987, 110697329450, 110697129383, 110143556105, 1127346129709, 110698329871, 1127342129667, 110698129812, 1127347129714, 1127351129753, 110696729137, 110696929276, 110697529561, 110699430248, 110143956148, 110697129353, 110697729616, 1127347129720, 110145056432, 1127351129760, 110145256495, 110698830079, 110145256483, 110697429491, 110145356516, 110144356271, 110141955878, 110697829679, 110699430262, 110144756379, 1127344129693, 1127349129736, 1127341129658, 110696729096, 110141755852, 110696428981, 110142756044, 110698029749, 110696529016, 110696428963, 110142956063, 110699330235, 110698529930, 110696729154, 110697329454, 110698629977, 110698930092, 110142355943, 110696829183, 110697229396, 110698229816, 110699130193, 110697029304, 110145356511, 110699230221, 110697129336, 110696629062, 110145656567, 110696729150, 1127341129663, 110697529565, 110143956150, 110696929216, 110142956064, 110698930096, 110142355944, 110145056435, 1127344129686, 110144356272, 110698629981, 110143556107, 110144756381, 110698029755, 110141755835, 110146056597, 1127343129681, 110696829176, 110696128859, 110699430245, 110696729128, 110141955902, 1127348129730, 1127344129691, 110141755855, 110697229401, 110698529934, 110141755845, 110697429498, 110697729619, 110698930100, 1127351129757, 1127346129707, 110698229819, 110698329880, 110145256489, 110697829690, 110143956153, 110697529569, 110696929268, 110141755833, 110141755840, 110696629086, 110145056438, 1127345129701, 110697329456, 110142355945, 110696529037, 110145656579, 110699430258, 110141955880, 1127347129717, 110699430254, 110142956065, 110143556108, 110141755850, 110696529011, 110698229823, 110696729124, 110698629985, 1127341129656, 110142756046, 110698029760, 110696428975, 1127346127589, 110697029296, 110696529047, 110697229406, 110698529936, 110696729115, 110696328884, 110696929245, 110698930108, 110145556534, 110144356274, 110142355946, 110142956066, 110143756116, 110145556555, 110145356505, 1127354129797, 110145256492, 110696529004, 1127342129673, 110697529571, 110697329461, 110696128853, 110697429509, 110696929256, 110141955882, 1127343129679, 110697029321, 110698429896, 110699330241, 110698930113, 110696929209, 110696529030, 110698229825, 1127343129677, 110697729630, 110145456529, 1127349129734, 110142756047, 110696829164, 110698629989, 110145556549, 110697829698, 110144156209, 110698529939, 110141955906, 110141755838, 110142355947, 110697129356, 110697229408, 1127350129747, 1127341129661, 110144756389, 1127342129670, 110698930117, 110141755843, 110696929236, 110144556313, 1127350127593, 110143156073, 1127344127587, 110145856588, 110141755831, 110696529024, 110698629992, 110143756118, 110696629055, 110145056447, 110696328879, 110697429513, 110696528996, 110141755856, 110144156211, 110696128845, 110697329465, 1127345129697, 110698429899, 110697229411, 1127348129726, 110144556314, 110697729634, 110696629071, 1127351129754, 110697029314, 110142956052, 1127345129704, 110698730003, 110696929228, 110143756120, 110696929262, 110698529942, 110699230230, 110145456524, 110142556012, 110699030128, 110698029768, 110696929286, 110141955907, 1127355129786, 110144856395, 110697129359, 110141955885, 110144556315, 110699330239, 110143156074, 110696929280, 110696929203, 110696428969, 110142956053, 110699130166, 110698730006, 110141755848, 110697929712, 110144156214, 110145056453, 1127344129689, 110696829197, 110697429516, 110699030131, 110697229419, 110696528990, 110697329468, 110697129348, 110698429902, 110141755857, 1127347129715, 1127342129668, 110698229830, 110697729637, 110696128837, 110696729099, 110698029770, 110697629584, 1127352129767, 110698730009, 1127348127591, 110143756122, 110141955887, 110698529945, 110144556316, 1127346129710, 110142556013, 110699030135, 110696729157, 1127349129739, 110145456520, 110143156075, 110144856397, 110697029308, 1127341129659, 1127345127588, 110145556543, 110143156076, 110696428984, 110697929717, 110144156217, 110142956055, 110697329472, 110698730016, 110699330237, 110699030138, 110141755829, 110698229835, 110145156456, 110697529529, 110699130197, 110697129362, 110699230224, 110696829190, 110696629065, 110141755853, 110144856399, 110696128862, 110698029774, 1127355129783, 110696929220, 110697729644, 110145356514, 110699030142, 1127345129702, 110697629587, 110144556317, 1127343129682, 1127341129664, 110141755841, 110141755846, 110698529950, 110142556015, 110143156077, 110697929723, 110697229425, 110697329474, 110141755836, 110698429906, 110698730039, 110699030146, 110699430246, 110698229838, 110697129340, 110696829179, 1127351129752, 110697129366, 110698029777, 110696929272, 110142956056, 1127344129692, 110697729648, 1127341129657, 1127351129758, 1127347129719, 110145156459, 110697529533, 110143756126, 110141955890, 110141955910, 1127346129708, 110144856401, 110696729091, 110141755860, 110696529013, 110696428978, 110696729133, 1127354129799, 110696529040, 110699230217, 110141955891, 1127341129662, 110697629595, 110142556016, 110698830051, 110697929727, 1127349129735, 110697329477, 110698529953, 110698429909, 110143156078, 1127344129685, 110698129789, 110698329851, 1127346129706, 110697029301, 110145556537, 110145356508, 110696328892, 110697129333, 110699430242, 110697229429, 110699230232, 110142956057, 110142556017, 110698830053, 110696629058, 110141955911, 110145156462, 110144856404, 110143356092, 110144156229, 110696729119, 110699130188]}
        Total_combs=expand_grid(dct)
        print(Total_combs.dtypes)
        print(aux)
        if aux.empty:
            Combs_todo=Total_combs.copy()
        else:

            Combs_todo=aux.merge(Total_combs,how='outer',indicator=True)#Warning

            Combs_todo=Combs_todo[Combs_todo['_merge']=='right_only']
            Combs_todo=Combs_todo.loc[:,Combs_todo.columns[:-1]]

        print(Combs_todo.head())
        Combs_todo=[dict(Combs_todo.loc[i,:]) for i in Combs_todo.index]
        print(len(Combs_todo))
        mp.freeze_support()
        print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
        pool=mp.Pool(processes=8)
        #selected_dwellings=select_data(Combs_todo)
        #print(selected_dwellings)
        #print(Combs_todo)
        pool.map(pooling2,Combs_todo)
        pool.close()
        pool.join()
        print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')


if __name__== '__main__':
    main()
