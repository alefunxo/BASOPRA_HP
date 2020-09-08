#!/usr/bin/python3
# -*- coding: utf-8 -*-
## @namespace Core_LP
# Created on Tue Oct 31 11:11:33 2017
# Author
# Alejandro Pena-Bello
# alejandro.penabello@unige.ch
# Description
# -----------
# INPUTS
# ------
# OUTPUTS
# -------
# TODO
# ----
# Generalize for the different configurations including HP
# Requirements
# ------------
# Pandas, numpy, itertools, os

import os
import pandas as pd
import numpy as np
import itertools
def back_to_dict(dict_filename,df_filename):
    '''
    allows to get back a dictionary from the two csv produced by the optimization (the df and the metadata-dict). Needed only if it is not possible to use the pickle and the whole data is needed. Pay attention to the way in which the data is stored in the csv. Here indexes are:
    0                     Tech
    1                 App_comb
    2                 Capacity
    3                     conf
    4                  Cap_arr
    5                      SOH
    6                      DoD
    7     Cycle1_aging0_factor
    8                    P_max
    9                     name
    10                 results
    11           cycle_cal_arr
    12                  PV_nom
    13                   cases
    14                  status

        '''
    df=pd.read_csv(df_filename,index_col=[0],sep=';|,',engine='python',parse_dates=[0],infer_datetime_format=True)
    df.index=df.index.tz_localize('UTC').tz_convert('Europe/Brussels')
    df_dict=pd.read_csv(dict_filename,header=None)
    new_dict={'df':df}
    for i in df_dict.index:
        if i not in [4,5,6,8,10,11]:
            try:
                new_dict.update({str(df_dict.iloc[i,0]):float(df_dict.iloc[i,1])})
            except:
                new_dict.update({str(df_dict.iloc[i,0]):(df_dict.iloc[i,1])})
        else:
            try:
                a=np.array([float(i) for i in df_dict.iloc[i,1].replace('[','').replace(']','').split()])
            except:
                a=np.array([float(i) for i in df_dict.iloc[10,1].replace('[','').replace(']','').split(',')])
            finally:
                new_dict.update({str(df_dict.iloc[i,0]):a})
    return new_dict



def get_table_inputs():
    clusters=pd.read_csv('../Input/clusters.csv',index_col=[0])
    aux=pd.DataFrame()

    for i in range(9):
            aux=aux.append(clusters.loc[(clusters.country=='CH')&(clusters.cluster==i)][:(min(30,clusters.loc[(clusters.country=='CH')&(clusters.cluster==i),'name'].size))])


    PV=[{'PV':3.2,'quartile':25,'country':'US'},
        {'PV':5,'quartile':50,'country':'US'},
        {'PV':6.4,'quartile':75,'country':'US'},
        {'PV':3.2,'quartile':25,'country':'CH'},
        {'PV':4.8,'quartile':50,'country':'CH'},
        {'PV':6.9,'quartile':75,'country':'CH'}]
    PV=pd.DataFrame(PV)


    App_comb_scenarios=np.array([i for i in itertools.product([False, True],repeat=3)])
    App_comb_scenarios=np.insert(App_comb_scenarios,slice(1,2),True,axis=1)
    App_comb=pd.DataFrame(App_comb_scenarios)
    App_comb=App_comb[0].map(str)+' '+App_comb[1].map(str)+' '+App_comb[2].map(
                    str)+' '+App_comb[3].map(str)
    App_comb=App_comb.reset_index()
    App_comb=App_comb.rename(columns={'index':'App_index',0:'App_comb'})
    conf_scenarios=np.array([i for i in itertools.product([False, True],repeat=3)])
    conf_scenarios=np.insert(conf_scenarios,slice(1,2),True,axis=1)
    conf=pd.DataFrame(conf_scenarios)
    conf=conf[0].map(str)+' '+conf[1].map(str)+' '+conf[2].map(
                    str)+' '+conf[3].map(str)
    conf=conf.reset_index()
    conf=conf.rename(columns={'index':'conf_index',0:'conf'})

    house_types=pd.DataFrame(np.array(['SFH100','SFH45','SFH15']),columns=['House_type'])
    hp_types=pd.DataFrame(np.array(['GSHP','ASHP']),columns=['HP_type'])
    rad_types=pd.DataFrame(np.array(['under','rad']),columns=['Rad_type'])
    aux=aux.rename(columns={'name':'hh'}).reset_index()
    return[aux,PV,App_comb,conf,house_types,hp_types,rad_types]

def get_power(df):
    #print('Getting power')
    Power_out=pd.DataFrame()
    El_out=pd.DataFrame()
    aux2=pd.DataFrame()

    df1=df.reindex(columns=['E_PV_grid','E_cons','E_demand','E_PV','E_demand_hp_pv','E_demand_hp_pv_dhw','E_demand_pv'])
    spring = range(80, 172)#march 20
    summer = range(172, 264)#june 21
    fall = range(264, 355)#september 22
    # winter = everything else#december 21
    df1['season']='winter'
    df1.loc[(df1.index.dayofyear>80) &(df1.index.dayofyear < 172),'season']='spring'
    df1.loc[(df1.index.dayofyear>=172) &(df1.index.dayofyear < 264),'season']='summer'
    df1.loc[(df1.index.dayofyear>=264) &(df1.index.dayofyear < 355),'season']='fall'

    groupby_month_electricity=df1.groupby([df1.index.month],as_index=False).sum()
    groupby_month_power=df1.groupby([df1.index.month],as_index=False).max()*4
    aux=groupby_month_power.drop('season',axis=1).unstack().reset_index()
    Power_out['name']='power_'+aux["level_0"].map(str) +'_'+ aux["level_1"].map(str)
    Power_out['value']=aux.iloc[:,2]

    aux=groupby_month_electricity.unstack().reset_index()

    El_out['name']='electricity_'+aux["level_0"].map(str) +'_'+ aux["level_1"].map(str)
    El_out['value']=aux.iloc[:,2]

    groupby_season_electricity=df1.groupby(df1.season).sum()
    groupby_season_power=df1.groupby(df1.season).max()*4
    aux=groupby_season_power.unstack().reset_index()

    aux2['value']=aux.loc[:,0]
    aux2['name']=aux.loc[:,['level_0','season']].apply(lambda x:  'power_'+'_'.join(x), axis=1)
    Power_out=Power_out.append(aux2,ignore_index=True,sort=False)

    aux=groupby_season_electricity.unstack().reset_index()

    aux2['value']=aux.loc[:,0]
    aux2['name']=aux.loc[:,['level_0','season']].apply(lambda x:  'electricity_'+'_'.join(x), axis=1)
    El_out=El_out.append(aux2,ignore_index=True,sort=False)

    total_electricity=df1.sum()

    max_power=df1.max()*4

    El_out=El_out.append(total_electricity.drop('season').reset_index().rename(columns={'index':'name',0:'value'}),ignore_index=True,sort=True)
    Power_out=Power_out.append(max_power.drop('season').reset_index().rename(columns={'index':'name',0:'value'}),ignore_index=True,sort=True)
    Power_out.iloc[-7:,0]=Power_out.iloc[-7:,0].apply(lambda x:  'power_'+(x)+'_year')
    El_out.iloc[-7:,0]=El_out.iloc[-7:,0].apply(lambda x:  'electricity_'+(x)+'_year')
    El_out=El_out.set_index('name')
    El_out=El_out.squeeze()
    Power_out=Power_out.set_index('name')
    Power_out=Power_out.squeeze()
    return[Power_out,El_out]

def get_technical_indicators(App,agg_results,country,df,conf):
    '''
    Uses the inputs to calculate technical indicators such as



    DSC
    ISC
    EFC
    Curtailment
    BS
    Load shifted*
    Peak shaved*
    *these indicators are calculated for different configurations, i.e. when there is
    only electricity demand without PV and then a PV system is added. When the system
    with PV includes now a HP. When from the PV+HP system a storage system is included (e.g. Batt)
    And finally compares as well the initial system (w/o PV) with the final system (PV+HP+storage and DHW if included)
    The results are added to agg_results
    TODO
    -----
    Do we need to include the Apps here for PS?
    '''
    #print('Getting techno indicators')

    #TSC
    agg_results['TSC']=(agg_results.E_PV_load+agg_results.E_PV_batt+agg_results.E_PV_bu+agg_results.E_PV_budhw+agg_results.E_PV_hp+agg_results.E_PV_hpdhw)/agg_results.E_PV*100#[%]
    #print('TSC ok')
    agg_results['DSC']=(agg_results.E_PV_load+agg_results.E_PV_bu+agg_results.E_PV_budhw+agg_results.E_PV_hp+agg_results.E_PV_hpdhw)/agg_results.E_PV*100#[%]
    #print('DSC ok')
    agg_results['ISC']=(agg_results.E_PV_batt)/agg_results.E_PV*100#[%]
    #print('ISC ok')

    agg_results['CU']=(agg_results.E_PV_curt)/agg_results.E_PV*100#[%]
    #print('General techno ok')
    if conf>3:
        agg_results['EFC_nolifetime']=(agg_results.E_dis)/param['Capacity']
        #print('EFC_nolifetime ok')

    else:
        agg_results['EFC_nolifetime']=0
        #print('EFC_nolifetime ok')

    if (conf==3)|(conf==4):
        #print('conf==3 or 4')
        agg_results['BS']=(agg_results.E_dis)/(agg_results.E_demand_hp_pv)*100#[%]
    elif conf==5:
        #print('conf==5')
        agg_results['BS']=(agg_results.E_dis)/(agg_results.E_demand_hp_pv_dhw)*100#[%]

    if (conf!=2)&(conf!=5):
        #print('conf!=2 and 5')
        if (App==2) or (App==3) or (App==6) or (App==7):
            #print('conf==2,3,6 or 7')
            if country=='US':
                #print('in US')
                cons=df.E_cons[df.price==df.price.max()].groupby(
                        df.E_cons[df.price==df.price.max()].index.month).sum()
                cons.index=cons.index-1
                rem=df.E_demand_hp_pv[df.price==df.price.max()].groupby(
                        df.E_demand_hp_pv[df.price==df.price.max()].index.month).sum()
                rem.index=rem.index-1

                cons1=df.E_demand_pv[df.price==df.price.max()].groupby(
                        df.E_demand_pv[df.price==df.price.max()].index.month).sum()
                cons1.index=cons1.index-1
                rem1=df.E_demand[df.price==df.price.max()].groupby(
                        df.E_demand[df.price==df.price.max()].index.month).sum()
                rem1.index=rem1.index-1

                cons2=df.E_demand_hp_pv[df.price==df.price.max()].groupby(
                        df.E_demand_hp_pv[df.price==df.price.max()].index.month).sum()
                cons2.index=cons2.index-1
                rem2=df.E_demand_pv[df.price==df.price.max()].groupby(
                        df.E_demand_pv[df.price==df.price.max()].index.month).sum()
                rem2.index=rem2.index-1

                cons4=df.E_cons[df.price==df.price.max()].groupby(
                        df.E_cons[df.price==df.price.max()].index.month).sum()
                cons4.index=cons4.index-1
                rem4=df.E_demand[df.price==df.price.max()].groupby(
                        df.E_demand[df.price==df.price.max()].index.month).sum()
                rem4.index=rem4.index-1

                cons5=df.E_cons[df.price==df.price.max()].groupby(
                        df.E_cons[df.price==df.price.max()].index.month).sum()
                cons5.index=cons5.index-1
                rem5=df.E_demand_pv[df.price==df.price.max()].groupby(
                        df.E_demand_pv[df.price==df.price.max()].index.month).sum()
                rem5.index=rem5.index-1

            else:
                #print('in CH')
                cons=df.E_cons[df.price==df.price.max()].groupby(
                        df.E_cons[df.price==df.price.max()].index.month).sum().reset_index(drop=True)
                rem=df.E_demand_hp_pv[df.price==df.price.max()].groupby(
                        df.E_demand_hp_pv[df.price==df.price.max()].index.month).sum().reset_index(drop=True)

                cons1=df.E_demand_pv[df.price==df.price.max()].groupby(
                        df.E_demand_pv[df.price==df.price.max()].index.month).sum().reset_index(drop=True)
                rem1=df.E_demand[df.price==df.price.max()].groupby(
                        df.E_demand[df.price==df.price.max()].index.month).sum().reset_index(drop=True)

                cons2=df.E_demand_hp_pv[df.price==df.price.max()].groupby(
                        df.E_demand_hp_pv[df.price==df.price.max()].index.month).sum().reset_index(drop=True)
                rem2=df.E_demand_pv[df.price==df.price.max()].groupby(
                        df.E_demand_pv[df.price==df.price.max()].index.month).sum().reset_index(drop=True)

                cons4=df.E_cons[df.price==df.price.max()].groupby(
                        df.E_cons[df.price==df.price.max()].index.month).sum().reset_index(drop=True)
                rem4=df.E_demand[df.price==df.price.max()].groupby(
                        df.E_demand[df.price==df.price.max()].index.month).sum().reset_index(drop=True)
                cons5=df.E_cons[df.price==df.price.max()].groupby(
                        df.E_cons[df.price==df.price.max()].index.month).sum().reset_index(drop=True)
                rem5=df.E_demand_pv[df.price==df.price.max()].groupby(
                        df.E_demand_pv[df.price==df.price.max()].index.month).sum().reset_index(drop=True)
            #print('get LS')
            agg_results['LS1']=(1-cons1.sum()/rem1.sum())*100#El->El+PV
            agg_results['LS2']=(1-cons2.sum()/rem2.sum())*100#El+PV->El+PV+HP
            agg_results['LS3']=(1-cons.sum()/rem.sum())*100#El+PV+HP->new_conf***
            agg_results['LS4']=(1-cons4.sum()/rem4.sum())*100#El->new_conf
            agg_results['LS5']=(1-cons5.sum()/rem5.sum())*100#El+PV->new_conf
            #print('LS are ok')
        else:
            #print('conf diff from 2,3,6 or 7')
            if country=='US':
                #print('in US')
                cons=df.E_cons[df.price==df.price.max()].groupby(
                        df.E_cons[df.price==df.price.max()].index.month).sum()
                cons.index=cons.index-1
                rem=df.E_demand_hp_pv[df.price==df.price.max()].groupby(
                        df.E_demand_hp_pv[df.price==df.price.max()].index.month).sum()
                rem.index=rem.index-1

                cons1=df.E_demand_pv[df.price==df.price.max()].groupby(
                        df.E_demand_pv[df.price==df.price.max()].index.month).sum()
                cons1.index=cons1.index-1
                rem1=df.E_demand[df.price==df.price.max()].groupby(
                        df.E_demand[df.price==df.price.max()].index.month).sum()
                rem1.index=rem1.index-1

                cons2=df.E_demand_hp_pv[df.price==df.price.max()].groupby(
                        df.E_demand_hp_pv[df.price==df.price.max()].index.month).sum()
                cons2.index=cons2.index-1
                rem2=df.E_demand_pv[df.price==df.price.max()].groupby(
                        df.E_demand_pv[df.price==df.price.max()].index.month).sum()
                rem2.index=rem2.index-1

                cons4=df.E_cons[df.price==df.price.max()].groupby(
                        df.E_cons[df.price==df.price.max()].index.month).sum()
                cons4.index=cons2.index-1
                rem4=df.E_demand[df.price==df.price.max()].groupby(
                        df.E_demand[df.price==df.price.max()].index.month).sum()
                rem4.index=rem4.index-1

                cons5=df.E_cons[df.price==df.price.max()].groupby(
                        df.E_cons[df.price==df.price.max()].index.month).sum()
                cons5.index=cons5.index-1
                rem5=df.E_demand_pv[df.price==df.price.max()].groupby(
                        df.E_demand_pv[df.price==df.price.max()].index.month).sum()
                rem5.index=rem5.index-1


            else:
                #print('in CH')
                cons=df.E_cons[df.price==df.price.max()].groupby(
                        df.E_cons[df.price==df.price.max()].index.month).sum().reset_index(drop=True)
                rem=df.E_demand_hp_pv_dhw[df.price==df.price.max()].groupby(
                        df.E_demand_hp_pv_dhw[df.price==df.price.max()].index.month).sum().reset_index(drop=True)

                cons1=df.E_demand_pv[df.price==df.price.max()].groupby(
                        df.E_demand_pv[df.price==df.price.max()].index.month).sum().reset_index(drop=True)
                rem1=df.E_demand[df.price==df.price.max()].groupby(
                        df.E_demand[df.price==df.price.max()].index.month).sum().reset_index(drop=True)

                cons2=df.E_demand_hp_pv_dhw[df.price==df.price.max()].groupby(
                        df.E_demand_hp_pv_dhw[df.price==df.price.max()].index.month).sum().reset_index(drop=True)
                rem2=df.E_demand_pv[df.price==df.price.max()].groupby(
                        df.E_demand_pv[df.price==df.price.max()].index.month).sum().reset_index(drop=True)

                cons4=df.E_cons[df.price==df.price.max()].groupby(
                        df.E_cons[df.price==df.price.max()].index.month).sum().reset_index(drop=True)
                rem4=df.E_demand[df.price==df.price.max()].groupby(
                        df.E_demand[df.price==df.price.max()].index.month).sum().reset_index(drop=True)
                cons5=df.E_cons[df.price==df.price.max()].groupby(
                        df.E_cons[df.price==df.price.max()].index.month).sum().reset_index(drop=True)
                rem5=df.E_demand_pv[df.price==df.price.max()].groupby(
                        df.E_demand_pv[df.price==df.price.max()].index.month).sum().reset_index(drop=True)

            #print('get the LS')
            agg_results['LS1']=(1-cons1.sum()/rem1.sum())*100#El->El+PV
            agg_results['LS2']=(1-cons2.sum()/rem2.sum())*100#El+PV->El+PV+HP+DHW
            agg_results['LS3']=(1-cons.sum()/rem.sum())*100#El+PV+HP+DHW->new_conf***
            agg_results['LS4']=(1-cons4.sum()/rem4.sum())*100#El->new_conf
            agg_results['LS5']=(1-cons5.sum()/rem5.sum())*100#El+PV->new_conf
            #print('LS ok')
    #Do we need to include the Apps here?
    #print('get PS')
    agg_results['PS1']=(df.E_demand_pv.max()*4-df.E_demand.max()*4)/(df.E_demand.max()*4)*100#El->El+PV
    #print('PS1 ok')
    #print('get PS2 and 3')
    if (conf!=2)&(conf!=5):#w/o DHW
        agg_results['PS2']=(df.E_demand_hp_pv.max()*4-df.E_demand_pv.max()*4)/(df.E_demand_pv.max()*4)*100#El+PV->El+PV+HP+DHW
        agg_results['PS3']=(df.E_cons.max()*4-df.E_demand_hp_pv.max()*4)/(df.E_demand_hp_pv.max()*4)*100#El+PV+HP+DHW->new_conf***
    else:#with DHW
        agg_results['PS2']=(df.E_demand_hp_pv_dhw.max()*4-df.E_demand_pv.max()*4)/(df.E_demand_pv.max()*4)*100#El+PV->El+PV+HP+DHW
        agg_results['PS3']=(df.E_cons.max()*4-df.E_demand_hp_pv_dhw.max()*4)/(df.E_demand_hp_pv_dhw.max()*4)*100#El+PV+HP+DHW->new_conf***
    #print('PS2 and 3 ok')
    #print('get PS4 and 5')
    agg_results['PS4']=(df.E_cons.max()*4-df.E_demand.max()*4)/(df.E_demand.max()*4)*100#El->new_conf
    agg_results['PS5']=(df.E_cons.max()*4-df.E_demand_pv.max()*4)/(df.E_demand_pv.max()*4)*100#El+PV->new_conf
    #print('PS4 and 5 are ok')
    return agg_results

def get_bills(country,param,df,conf,agg_results):

    #print('Getting bill')

    bill_power=0
    if param['App_comb'][3]:

        P_max_month=df.groupby([df.index.month]).E_cons.max()*4
        bill_power=P_max_month*param['Capacity_tariff']*365/12

    bill_energy_min=df.E_cons*df.price-df.E_PV_grid*df.Export_price
    bill_energy_no_exp=df.E_cons*df.price

    bill_energy_day=bill_energy_min.groupby([df.index.month, df.index.day]).sum()
    bill_energy_day_noexp=bill_energy_no_exp.groupby([df.index.month, df.index.day]).sum()

    bill=bill_energy_day#+bill_power

    bill=(bill.unstack().sum(axis=1)+bill_power).reset_index(drop=True)
    bill_noexp=(bill_energy_day_noexp.unstack().sum(axis=1)+bill_power).reset_index(drop=True)

    agg_results['bill']=bill.sum()
    agg_results['bill_noexp']=bill_noexp.sum()
    #agg_results['P_max_mean']=P_max_month.mean()
    return agg_results
def get_main_results(param,aux_dict,df):
    """

    We are interested on some results such as
    %SC
    %DSC
    %BS
    EFC

    We want to know %PS,%LS,%CU,%PVSC per year.
    """
    print('Main results')
    cols=['E_PV_batt', 'E_PV_bu', 'E_PV_budhw', 'E_PV_curt','E_PV_grid', 'E_PV_hp', 'E_PV_hpdhw', 'E_PV_load', 'E_batt_bu',
       'E_batt_budhw', 'E_batt_hp', 'E_batt_hpdhw', 'E_batt_load', 'E_bu','E_budhw', 'E_char', 'E_cons', 'E_dis', 'E_grid_batt', 'E_grid_bu',
       'E_grid_budhw', 'E_grid_hp', 'E_grid_hpdhw', 'E_grid_load', 'E_hp','E_hpdhw', 'E_loss_Batt', 'E_loss_conv', 'E_loss_inv', 'E_loss_inv_PV',
       'E_loss_inv_batt', 'E_loss_inv_grid', 'Q_dhwst_hd', 'Q_hp_sh','Q_hp_ts', 'Q_loss_dhwst', 'Q_loss_ts', 'Q_ts', 'Q_ts_delta', 'Q_ts_sh',
       'SOC', 'T_dhwst', 'T_ts', 'E_demand', 'E_PV', 'Export_price', 'price','Inv_P', 'Conv_P', 'Req_kWh', 'Req_kWh_DHW', 'Set_T', 'Temp',
       'Temp_supply', 'Temp_supply_tank', 'T_aux_supply', 'COP_tank', 'COP_SH','COP_DHW']
    df=df.loc[:,cols]
    print(df.price.head())
    [clusters,PV,App,conf2,house_types,hp_types,rad_types]=get_table_inputs()
    App=App.App_index[App.App_comb==str(param['App_comb']).replace(',','').strip(' ').replace('[','').replace(']','')].values[0]
    conf=conf2.conf_index[conf2.conf==str(param['conf']).replace(',','').strip(' ').replace('[','').replace(']','')].values[0]

    df['E_demand_hp_pv_dhw']=((df.E_demand+df.Req_kWh/df.COP_SH+df.Req_kWh_DHW/df.COP_DHW)-pd.DataFrame([df.E_demand+df.Req_kWh/df.COP_SH+df.Req_kWh_DHW/df.COP_DHW,df.E_PV]).min())
    df['E_demand_hp_pv']=((df.E_demand+df.Req_kWh/df.COP_SH)-pd.DataFrame([df.E_demand+df.Req_kWh/df.COP_SH,df.E_PV]).min())
    df['E_demand_pv']=((df.E_demand)-pd.DataFrame([df.E_demand,df.E_PV]).min())

    df=df.apply(pd.to_numeric, errors='ignore')
    agg_results=df.sum()

    #####################################################
    #Technical data
    if param['testing']:
        [Power_out,El_out]=get_power(df)
    agg_results=get_technical_indicators(App,agg_results,'CH',df,3)
    #print('out of technical')
    ####################################################
    #Metadata
    #print('Metadata')

    agg_results['App_comb']=App
    #print('conf')
    agg_results['conf']=conf
    #print('cap')
    agg_results['Capacity']=param['Capacity']
    #print('tech')
    agg_results['Tech']=param['Tech']
    #print('PV')
    agg_results['PV_nom']=param['PV_nom']
    #print('clusters')
    agg_results['cluster']=clusters[clusters.hh==int(
            param['name'].split('_')[0])].cluster.values
    #print('hh')
    agg_results['hh']=param['name'].split('_')[0]
    #print('country')
    agg_results['country']=param['name'].split('_')[1]
    #print('qt')
    agg_results['quartile']=PV[(PV.PV==param['PV_nom'])&
               (PV.country==param['name'].split('_')[1])].quartile.values[0]
    #print('case')
    agg_results['cases']=param['cases']
    #print('ht')
    agg_results['house_type']=param['ht']
    #print('hp')
    agg_results['HP']=param['HP_type']
    #print('end Metadata')
    #####################################################
    #Other data
    #print('other data')

    agg_results=agg_results.drop(['SOC','Inv_P','Conv_P','price',
                                  'Export_price'])
    agg_results['SOC_mean']=df['SOC'].mean()/param['Capacity']*100
    agg_results['P_drained_max']=df['E_cons'].max()*4
    
    agg_results['P_injected_max']=df['E_PV_grid'].max()*4
    agg_results['last_cap']=aux_dict['aux_Cap_arr'][-1]
    agg_results['cap_fading']=(1-aux_dict['aux_Cap_arr'][-1]/
               param['Capacity'])*100
    agg_results['last_SOH']=aux_dict['SOH_arr'][-1]
    agg_results['cycle_to_total']=aux_dict['cycle_cal_arr'].sum()/len(aux_dict['results_arr'])
    #print('end other data')
    #####################################################
    #Economic data
    #print('bill')
    agg_results=get_bills(param['name'].split('_')[1],param,df,conf,agg_results)
    #print('end bill')
    if param['testing']:
        return[agg_results,El_out,Power_out]
    else:
        return agg_results
