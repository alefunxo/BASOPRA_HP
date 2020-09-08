# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 10:12:39 2018

@author: alejandro
"""
import os
os.chdir('C:/Users/alejandro/Dropbox/0. PhD/Python/Paper1_v5')
import paper_classes_2 as pc

Technologies=['LFP']#,'NMC','NCA','LTO','ALA']
for tech in Technologies:
    filename='C:/Users/alejandro/Documents/Data/Output/df_CHtwo_'+tech+'_1111_2.pickle'
    if tech=='LFP':
        out_LFP=pd.read_pickle(filename)
        df_LFP=out_LFP['df']
    elif tech=='NMC':
        out_NMC=pd.read_pickle(filename)
        df_NMC=out_NMC['df']
    elif tech=='LTO':
        out_LTO=pd.read_pickle(filename)
        df_LTO=out_LTO['df']
    elif tech=='NCA':
        out_NCA=pd.read_pickle(filename)
        df_NCA=out_NCA['df']
    elif tech=='ALA':
        out_ALA=pd.read_pickle(filename)
        df_ALA=out_ALA['df']
out_tech=[out_LFP]#,out_NMC,out_LTO,out_NCA,out_ALA]    
for tech in out_tech:
    print(sum(tech['results']))
    print(sum(tech['cycle_cal_arr']))
    print(mean(tech['DoD']))
    print(str(tech['Tech']))
    print('###################')
font = {'family':'monospace',
        'weight' : 'normal',
        'size'   : 22}
matplotlib.rc('font', **font)
df_LFP=df_LFP.set_index(df_LFP.index.time)

fig = plt.figure()


ax = fig.add_axes([0.1, 0.4, 0.8, 0.5],
                   xticklabels=[])
ax2 = fig.add_axes([0.1, 0.1, 0.8, 0.3])
#ax.set_title('Single off-peak timeslot')
ax.set_title('Sinus wave test')
ax.plot((df_LFP.E_char-df_LFP.E_dis)*4,label='Charge/discharge kW')
ax.set_ylabel('Power kW')
ax.set_xlabel('Hour')
ax2.set_xticklabels([0,0,5,11,17,22])



ax2.plot(df_LFP.price,color='r',label='Price USD/kWh')
ax2.set_ylabel('Price USD/kWh')

#ax.plot(df_LFP.E_Demand)
ax.legend(loc=(0.8,1.01),fontsize=15)
ax2.legend(loc=(0.8,2.82),fontsize=15)
ax.grid()
ax2.grid()


fig,ax=plt.subplots()
#ax.plot(df_LFP.SOC[:35040])
#ax.plot(df_LFP.E_Demand)
#ax.plot(df_LFP.E_cons)





ax.plot(df_LFP.E_char-df_LFP.E_dis,label='Charge/discharge kW')
ax.set_ylabel('Power kW')
ax.set_xlabel('Hour')
ax.set_xticklabels([0,0,5,11,17,22])

ax2 = ax.twinx()

ax2.plot(df_LFP.price,color='r',label='Price USD/kWh')
ax2.set_ylabel('Price USD/kWh')

#ax.plot(df_LFP.E_Demand)
ax.legend(loc=(0.8,1.01),fontsize=15)
plt.title('Sinus wave test')
ax2.legend(loc=(0.8,1.07),fontsize=15)
#ax2.set_yticks(np.linspace(ax2.get_yticks()[0], ax2.get_yticks()[-1], len(ax.get_yticks())))

ax.grid()
#After getting the results 

    data_input=d
    name=str(data_input['name'])
    PV_nominal_power=data_input['nominal_power']
    data_input=data_input['df']
    data_input.columns=['E_demand','E_PV','Price_flat','Price_DT']
    if 'CH' in name:
        Capacity_tariff=9.39*12/365
    elif 'US' in name:
        Capacity_tariff=10.14*12/365
    Export_price=0.0559
    Inverter_power=(PV_nominal_power/1.3).round(1)
    Curtailment=0.5
    Inverter_Efficiency=0.95
    #dt is 1/4 hours i.e. 15 min
    #P=E/dt
    dt=0.25
    nyears=20
    ndays=365*nyears
Capacity_tariff=0.33
Export_price=0.0559
Inverter_power=(PV_nominal_power/1.3).round(1)
Curtailment=0.5
Inverter_Efficiency=0.95
#dt is 1/4 hours i.e. 15 min
#P=E/dt
dt=0.25
nyears=20
ndays=365*nyears
#total yearly bill:

sum(df_out['results'][:365])
df22.E_char.groupby([(df1.index.year),(df1.index.month),(df1.index.day)]).sum()/2

(df_out['P_max'][:365]*Capacity_tariff).sum()

def Base_prices(df,DPS_day_month):
    df=df2
    delta_t=0.25
    curt=0.5
    if 'CH'in df['name']:
        Export_price=0.0559
        Flat_tariff=0.22
        Capacity_tariff=9.39
    else:
        Export_price=0.0559
        Flat_tariff=0.05
        Capacity_tariff=10
    App_comb=df['App_comb']
    Batt_eff=pc.Battery(df['Capacity'],df['Tech']).Efficiency
    PV_nominal_power=df['PV_nom']
    df_=df['df']
    E_sp=df_.E_PV-df_.E_Demand
    E_sp[E_sp<0]=0
    E_sp_Power=E_sp/delta_t
    E_load=df_.E_Demand-df_.E_PV
    E_load[E_load<0]=0
    DPS_base=0
    PVAC_base=0
    if DPS_day_month=='day':
        aux=df_.E_Demand.groupby([df_.index.year,df_.index.month,df_.index.day]).max()
        aux_cons=df_.E_cons.groupby([df_.index.year,df_.index.month,df_.index.day]).max()
        Capacity_tariff=Capacity_tariff*12/365
    else:
        aux=df_.E_Demand.groupby([df_.index.year,df_.index.month]).max()
        aux_cons=df_.E_cons.groupby([df_.index.year,df_.index.month]).max()
    if App_comb[-1]==1:
        DPS_base=aux.sum()*Capacity_tariff/delta_t
        DPS_new=aux_cons.sum()*Capacity_tariff/delta_t
        DPS_diff=DPS_base-DPS_new
        print('the difference in DPS is:',DPS_base-DPS_new)
    if App_comb[0]==1:
        PVAC_base=((E_sp_Power[E_sp_Power>PV_nominal_power*curt]
                    -PV_nominal_power*curt)*delta_t).sum()*df_.price.max()*Batt_eff
        E_sp[E_sp/delta_t>PV_nominal_power*curt]=PV_nominal_power*curt*delta_t
        PVAC_new=df_.E_PV_curt.sum()*df_.price.max()*Batt_eff
        print('the difference in PVAC is:',PVAC_base-PVAC_new)
        PVSC_base=(E_load*df_.price).sum()-(E_sp.sum()*Export_price)
        PVSC_new=(df_.E_cons*df_.price).sum()-(df_.E_PV_grid.sum()*Export_price)
        print('the difference in PVSC is:',PVSC_base-PVSC_new)
        PVAC_diff=PVAC_base-PVAC_new
        PVSC_diff=PVSC_base-PVSC_new
    else:
        PVSC_base=(E_load*df_.price).sum()-(E_sp.sum()*Export_price)
        PVSC_new=(df_.E_cons*df_.price).sum()-(df_.E_PV_grid.sum()*Export_price)
        PVSC_diff=PVSC_base-PVSC_new
    print('%%%%%%%%% cost without battery and same retail tariff is:%%%%%%%%%%%%%%%%')
    print((df_.E_Demand*df_.price).sum()-PVSC_base+DPS_base*App_comb[-1]+PVAC_base*App_comb[0])
    
    print('%%%%%%%%% cost with PV %%%%%%%%%%%%%%%%')
    print(PVSC_new+PVAC_new+DPS_new)
    print(PVSC_base+PVAC_base+DPS_base)
    
    print('%%%%%%%%% cost with PV & no Batt nor restictions is:%%%%%%%%%%%%%%%%')
    print((E_load*Flat_tariff).sum()-(E_sp.sum()*Export_price))
    return [PVSC_base,PVAC_base,DPS_base]