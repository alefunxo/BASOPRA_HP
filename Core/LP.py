#Series

 # -*- coding: utf-8 -*-
## @namespace LP
# Created on Wed Nov  1 15:44:25 2017
# Author
# Alejandro Pena-Bello
# alejandro.penabello@unige.ch
# In this script the optimization is set up.
# This LP algorithm allows the user to optimize the daily electricity bill
# The system here presented is a DC-coupled system with a charge controller and
# a bi-directional inverter as presented in [1]
# It includes efficiency losses.
# It includes 4 applications and their combination with PVSC as base app.
# avoidance of PV curtailment, Demand peak shaving and demand load shifting.
# Demand peak shaving is done in the same basis than the optimization, i.e.
# if it is a daily optimization, the peak shaving is done every day, if it is
# yearly, then the peak of the year is shaved and so on.
# According to the Data it can be expanded to one month or n years optimization
# An Integrated Inverter is used, in this script the Converter and inverter
# efficiency are the same and are an input from the user.
# The delta_t allows the user to set the time step delta_t=fraction of hour, e.g.
# delta_t=0.25 is a 15 min time step
#<img src='C:/Users/alejandro/Documents/GitHub/Paper1_last/HP_PV_Batt_system_oct.jpg'>

# [1] Installed Cost Benchmarks and Deployment Barriers for Residential Solar+
# Photovoltaics with Energy Storage: Q1 2016
# Kristen Ardani,Eric O'Shaughnessy,Ran Fu,Chris McClurg,Joshua Huneycutt,
# and Robert Margolis


import pyomo.environ as en

#Model
def Concrete_model(Data):
    
    m = en.ConcreteModel()
    #Sets
    m.Time=en.Set(initialize=Data['Set_declare'][1:],ordered=True)
    m.Time_1=en.Set(initialize=Data['Set_declare'][1:9],ordered=True)
    m.Time_2=en.Set(initialize=Data['Set_declare'][9:17],ordered=True)
    m.Time_3=en.Set(initialize=Data['Set_declare'][17:25],ordered=True)
    m.Time_4=en.Set(initialize=Data['Set_declare'][25:33],ordered=True)
    m.Time_5=en.Set(initialize=Data['Set_declare'][33:41],ordered=True)
    m.Time_6=en.Set(initialize=Data['Set_declare'][41:49],ordered=True)
    m.Time_7=en.Set(initialize=Data['Set_declare'][49:57],ordered=True)
    m.Time_8=en.Set(initialize=Data['Set_declare'][57:65],ordered=True)
    m.Time_9=en.Set(initialize=Data['Set_declare'][65:73],ordered=True)
    m.Time_10=en.Set(initialize=Data['Set_declare'][73:81],ordered=True)
    m.Time_11=en.Set(initialize=Data['Set_declare'][81:89],ordered=True)
    m.Time_12=en.Set(initialize=Data['Set_declare'][89:],ordered=True)

    
    m.tm=en.Set(initialize=Data['Set_declare'],ordered=True)
    #Electric Parameters
    m.dt=en.Param(initialize=Data['delta_t'])
    m.doy=en.Param(initialize=Data['dayofyear'])
    m.toy=en.Param(initialize=Data['toy'])
    m.E_storage=en.Param(initialize=Data['conf'][0])
    m.heating=en.Param(initialize=Data['conf'][1])
    m.T_storage=en.Param(initialize=Data['conf'][2])
    m.DHW=en.Param(initialize=Data['conf'][3])
    #m.Cooling=en.Param(initialize=Data['Cooling'])
    m.subset_tank_day=en.Param(initialize=Data['subset_tank_day'])
    
    m.PVAC=en.Param(initialize=Data['App_comb_mod'][0])
    m.PVSC=en.Param(initialize=Data['App_comb_mod'][1])
    m.DLS=en.Param(initialize=Data['App_comb_mod'][2])
    m.DPS=en.Param(initialize=Data['App_comb_mod'][3])

    m.retail_price=en.Param(m.Time,initialize=Data['retail_price'])
    m.E_PV=en.Param(m.Time,initialize=Data['E_PV'])
    m.E_demand_el=en.Param(m.Time,initialize=Data['E_demand'])

    m.export_price=en.Param(m.Time,initialize=Data['Export_price'])
    m.capacity_tariff=en.Param(default=Data['Capacity_tariff'])
    m.Inverter_power=en.Param(initialize=Data['Inv_power'])
    m.Inverter_eff=en.Param(initialize=Data['Inverter_eff'])
    m.Converter_eff=en.Param(initialize=Data['Converter_Efficiency_Batt'])

    m.Max_injection=en.Param(initialize=Data['Max_inj'])
    m.SOC_min=en.Param(initialize=Data['Batt'].SOC_min)
    m.SOC_max=en.Param(initialize=Data['SOC_max'])
    m.Efficiency=en.Param(initialize=Data['Batt'].Efficiency)
    m.Batt_dis_max=en.Param(initialize=-Data['Batt'].P_max_dis)
    m.Batt_char_max=en.Param(initialize=Data['Batt'].P_max_char)
    #Heating parameters
    m.HP_power_SH=en.Param(m.Time,initialize=Data['hp_sh_cons'])#kWh/h=kW
    m.HP_power_tank=en.Param(m.Time,initialize=Data['hp_tank_cons'])#kWh/h=kW
    m.HP_dhw_power=en.Param(m.Time,initialize=Data['hp_dhw_cons'])#kWh/h=kW
    #m.Backup_heater=en.Param(initialize=Data['Backup_heater'])
    #m.Temp=en.Param(m.Time,initialize=Data['Temp'])
    m.T_supply=en.Param(m.Time,initialize=Data['Temp_supply'])
    #m.T_supply_min=en.Param(initialize=Data['T_supply'])
    m.Set_T=en.Param(m.Time,initialize=Data['Set_T'])
    m.COP_SH=en.Param(m.Time,initialize=Data['COP_SH'])
    m.COP_DHW=en.Param(m.Time,initialize=Data['COP_DHW'])
    m.COP_tank=en.Param(m.Time,initialize=Data['COP_tank'])
    m.Req_kWh=en.Param(m.Time,initialize=Data['Req_kWh'])# In kWh!
    m.Req_kWh_DHW=en.Param(m.Time,initialize=Data['Req_kWh_DHW'])# In kWh!
    m.T_max=en.Param(m.Time,initialize=Data['T_aux_supply'])# In K

    m.T_min=en.Param(m.Time,initialize=Data['Temp_supply'])# In K
    m.T_max_dhw=en.Param(initialize=Data['tank_dhw'].t_max)# In K
    m.T_min_dhw=en.Param(initialize=Data['tank_dhw'].t_min)# In K

    m.T_init=en.Param(initialize=Data['T_init'])# In K

    m.A=en.Param(initialize=Data['tank_sh'].surface)#m2
    m.U=en.Param(initialize=Data['tank_sh'].U_value)#kW/(m2*K)!!!
    m.c_p=en.Param(initialize=Data['tank_sh'].specific_heat)#kWh/(K*l)
    m.m=en.Param(initialize=Data['tank_sh'].mass)#liters

    m.A_dhw=en.Param(initialize=Data['tank_dhw'].surface)#m2
    m.U_dhw=en.Param(initialize=Data['tank_dhw'].U_value)#kW/(m2*K)!!!
    m.c_p_dhw=en.Param(initialize=Data['tank_dhw'].specific_heat)#kWh/(K*l)
    m.m_dhw=en.Param(initialize=Data['tank_dhw'].mass)#liters
    m.Backup_heater=en.Param(initialize=Data['Backup_heater'])

    #m.T_min_cooling=en.Param(initialize=Data['T_min_cooling'])# In K
    #m.toy=en.Param(initialize=Data['toy'])
    #Variables
    m.E_cons=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.E_PV_grid=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.E_PV_load=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.E_PV_batt=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.E_PV_curt=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.E_grid_load=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.E_grid_batt=en.Var(m.Time,bounds=(0,m.Batt_char_max*m.dt),
                       initialize=0)#because the power is in C terms thus, per hour

    m.E_char=en.Var(m.Time,bounds=(0,m.dt*m.Batt_char_max))#because the power is in C terms thus, per hour
    m.E_dis=en.Var(m.Time,bounds=(0,m.dt*m.Batt_dis_max))#because the power is in C terms thus, per hour
    m.P_max_day=en.Var(initialize=0)
    m.P_max_day_export=en.Var(initialize=0)
    m.Bool_dis=en.Var(m.Time,within=en.Boolean,initialize=1)
    m.Bool_char=en.Var(m.Time,within=en.Boolean,initialize=0)
    m.Bool_inj=en.Var(m.Time,within=en.Boolean,initialize=1)
    m.Bool_cons=en.Var(m.Time,within=en.Boolean,initialize=0)
    m.SOC=en.Var(m.tm,bounds=(m.SOC_min,m.SOC_max),initialize=m.SOC_min)

    m.E_loss_Batt=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.E_loss_conv=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.E_loss_inv=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.E_loss_inv_PV=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.E_loss_inv_batt=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.E_loss_inv_grid=en.Var(m.Time,bounds=(0,None),initialize=0)

    m.E_batt_load=en.Var(m.Time,bounds=(0,None))#new due to HP

    #HP variables
    m.E_PV_hp=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.E_batt_hp=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.E_grid_hp=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.E_hp=en.Var(m.Time,bounds=(0,None),initialize=0)
    #m.E_hp_cooling=en.Var(m.Time,bounds=(0,m.dt*m.HP_power),initialize=0)
    #m.COP=en.Var(m.Time,bounds=(0.01,None),initialize=1)
    #TS
    m.Q_ts_sh=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.Q_hp_sh=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.Q_hp_ts=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.T_ts=en.Var(m.tm,bounds=(0,None),initialize=m.T_init)#Temperature storage
    m.Q_ts=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.Q_ts_delta=en.Var(m.Time,bounds=(None,None),initialize=0)
    m.Q_loss_ts=en.Var(m.Time,bounds=(None,None),initialize=0)
    #hpdhwvariables
    m.E_PV_hpdhw=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.E_batt_hpdhw=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.E_grid_hpdhw=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.E_hpdhw=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.Bool_hp=en.Var(m.Time,within=en.Boolean,initialize=1)

    m.Bool_hpdhw=en.Var(m.Time,within=en.Boolean,initialize=0)

    #DHW
    m.Q_dhwst_hd=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.T_dhwst=en.Var(m.tm,bounds=(m.T_min_dhw,m.T_max_dhw),initialize=40+273.15)#Temperature storage
    m.Q_loss_dhwst=en.Var(m.Time,bounds=(0,None),initialize=0)

    #Backup_heater
    m.E_PV_bu=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.E_batt_bu=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.E_grid_bu=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.E_bu=en.Var(m.Time,bounds=(0,m.Backup_heater*m.dt),initialize=0)
    m.E_PV_budhw=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.E_batt_budhw=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.E_grid_budhw=en.Var(m.Time,bounds=(0,None),initialize=0)
    m.E_budhw=en.Var(m.Time,bounds=(0,m.Backup_heater*m.dt),initialize=0)

    #TS
    #m.Bool_bu=en.Var(m.Time,within=en.Boolean,initialize=1)
    #m.Bool_budhw=en.Var(m.Time,within=en.Boolean,initialize=0)
    #Objective Function

    m.total_cost = en.Objective(rule=Obj_fcn,sense=en.minimize)

    #Constraints

    #HP Constraints
    m.Balance_bu_demand_r=en.Constraint(m.Time,rule=Balance_bu_demand_rule)
    m.Balance_budhw_demand_r=en.Constraint(m.Time,rule=Balance_budhw_demand_rule)
    #m.bu_ch1=en.Constraint(m.Time,rule=Bool_bu_rule_1)
    #m.bu_ch2=en.Constraint(m.Time,rule=Bool_bu_rule_2)
    #m.bu_cd3=en.Constraint(m.Time,rule=Bool_bu_rule_3)
    #m.bu_cd4=en.Constraint(m.Time,rule=Bool_bu_rule_4)
    #m.Bu_1_2_r=en.Constraint(m.Time,rule=Bu_1_2)

    m.Balance_space_heat_demand_r_1=en.Constraint(m.Time_1,rule=Balance_space_heat_demand_1)
    m.Balance_space_heat_demand_r_2=en.Constraint(m.Time_2,rule=Balance_space_heat_demand_2)
    m.Balance_space_heat_demand_r_3=en.Constraint(m.Time_3,rule=Balance_space_heat_demand_3)
    m.Balance_space_heat_demand_r_4=en.Constraint(m.Time_4,rule=Balance_space_heat_demand_4)
    m.Balance_space_heat_demand_r_5=en.Constraint(m.Time_5,rule=Balance_space_heat_demand_5)
    m.Balance_space_heat_demand_r_6=en.Constraint(m.Time_6,rule=Balance_space_heat_demand_6)
    m.Balance_space_heat_demand_r_7=en.Constraint(m.Time_7,rule=Balance_space_heat_demand_7)
    m.Balance_space_heat_demand_r_8=en.Constraint(m.Time_8,rule=Balance_space_heat_demand_8)
    m.Balance_space_heat_demand_r_9=en.Constraint(m.Time_9,rule=Balance_space_heat_demand_9)
    m.Balance_space_heat_demand_r_10=en.Constraint(m.Time_10,rule=Balance_space_heat_demand_10)
    m.Balance_space_heat_demand_r_11=en.Constraint(m.Time_11,rule=Balance_space_heat_demand_11)
    m.Balance_space_heat_demand_r_12=en.Constraint(m.Time_12,rule=Balance_space_heat_demand_12)
    
    m.Balance_hp_demand_r=en.Constraint(m.Time,rule=Balance_hp_demand_rule)
    #m.Balance_space_heat_demand_r=en.Constraint(m.Time,
     #                               rule=Balance_space_heat_demand)
    m.Change_tank_thermal_energy_rule_r=en.Constraint(m.Time,rule=Change_tank_thermal_energy_rule)
    m.Available_tank_thermal_energy_rule_r=en.Constraint(m.Time,rule=Available_tank_thermal_energy_rule)
    m.Balance_hp_supply_r=en.Constraint(m.Time,rule=Balance_hp_supply_rule)#*
    m.Balance_hp_power_r=en.Constraint(m.Time,rule=Balance_hp_power)
    m.Balance_hp_dhw_power_r=en.Constraint(m.Time,rule=Balance_hp_dhw_power)
    m.Ts_losses_r=en.Constraint(m.Time,rule=Ts_losses)
    m.Balance_ts_r=en.Constraint(m.Time,rule=Balance_ts)#Verify if is necessary
    m.def_ts_state_r=en.Constraint(m.tm,rule=def_ts_state_rule)
    m.def_ts_state2_r=en.Constraint(m.Time,rule=def_ts_state2_rule)
    #hpdhw Constraints
    m.Balance_hp_DHW_r=en.Constraint(m.Time,rule=Balance_hp_DHW_rule)
    m.Balance_DHW_demand_r=en.Constraint(m.Time,rule=Balance_DHW_demand)
    m.Balance_hp_supply_r2=en.Constraint(m.Time,rule=Balance_hp_supply_rule2)#
    m.DHWST_losses_r=en.Constraint(m.Time,rule=DHWST_losses)
    m.Balance_dhwst_r=en.Constraint(m.tm,rule=Balance_dhwst)#Verify if is necessary
    m.def_dhwst_state_r=en.Constraint(m.tm,rule=def_dhwst_state_rule)

    m.hp_ch1=en.Constraint(m.Time,rule=Bool_hp_rule_1)
    m.hp_ch2=en.Constraint(m.Time,rule=Bool_hp_rule_2)
    m.hp_cd3=en.Constraint(m.Time,rule=Bool_hp_rule_3)
    m.hp_cd4=en.Constraint(m.Time,rule=Bool_hp_rule_4)
    m.HP_1_2_r=en.Constraint(m.Time,rule=HP_1_2)

    m.Bool_char_rule_1_r=en.Constraint(m.Time,rule=Bool_char_rule_1)
    m.Bool_char_rule_2_r=en.Constraint(m.Time,rule=Bool_char_rule_2)
    m.Bool_char_rule_3_r=en.Constraint(m.Time,rule=Bool_char_rule_3)
    m.Bool_char_rule_4_r=en.Constraint(m.Time,rule=Bool_char_rule_4)
    m.Batt_char_dis_r=en.Constraint(m.Time,rule=Batt_char_dis)

    m.E_dis_hp_r=en.Constraint(m.Time,rule=E_dis_hp_rule)

    #Battery
    m.Balance_batt=en.Constraint(m.Time,rule=Balance_Batt_rule)
    m.E_char_r=en.Constraint(m.Time,rule=E_char_rule)
    m.E_dis_r=en.Constraint(m.Time,rule=E_dis_rule)

    m.Bool_cons_rule_1_r=en.Constraint(m.Time,rule=Bool_cons_rule_1)
    m.Bool_cons_rule_2_r=en.Constraint(m.Time,rule=Bool_cons_rule_2)
    m.Bool_cons_rule_3_r=en.Constraint(m.Time,rule=Bool_cons_rule_3)
    m.Bool_cons_rule_4_r=en.Constraint(m.Time,rule=Bool_cons_rule_4)
    m.Cons_rule_r=en.Constraint(m.Time,rule=Cons_rule)

    m.E_storage_r=en.Constraint(m.tm,rule=E_storage_rule)

    #Balance
    m.Grid_cons=en.Constraint(m.Time,rule=Grid_cons_rule)
    m.Balance_PV=en.Constraint(m.Time,rule=Balance_PV_rule)
    m.Sold=en.Constraint(m.Time,rule=Sold_rule)
    m.Balance_load=en.Constraint(m.Time,rule=Balance_load_rule)
    m.Batt_SOC=en.Constraint(m.tm,rule=def_storage_state_rule)

    #Losses
    m.Conv_losses=en.Constraint(m.Time,rule=Conv_losses_rule)
    m.Inv_losses_PV=en.Constraint(m.Time,rule=Inv_losses_PV_rule)
    m.Inv_losses_batt=en.Constraint(m.Time,rule=Inv_losses_Batt_rule)
    m.Inv_losses_grid=en.Constraint(m.Time,rule=Inv_losses_Grid_rule)
    m.Inv_losses=en.Constraint(m.Time,rule=Inv_losses_rule)
    m.Batt_losses=en.Constraint(m.Time,rule=Batt_losses_rule)

    #Power
    m.Inverter=en.Constraint(m.Time,rule=Inverter_rule)
    m.Converter=en.Constraint(m.Time,rule=Converter_rule)
    m.Inverter_grid=en.Constraint(m.Time,rule=Inverter_grid_rule)
    m.P_max=en.Constraint(m.Time,rule=P_max_rule)
    #m.P_max_exp=en.Constraint(m.Time,rule=P_max_rule_grid)
    #Apps
    m.Curtailment_r=en.Constraint(m.Time,rule=Curtailment_rule)
    m.DLS_const=en.Constraint(m.Time,rule=DLS_rule)


    #m.transitions_rule=en.Constraint(m.Time,rule=transitions)
    #m.transitions_rule2=en.Constraint(m.Time,rule=transitions2)

    #m.COP_r=en.Constraint(m.Time,rule=COP_rule)
    #m.double_bu_r=en.Constraint(m.Time,rule=double_bu)
    #m.Q_ts_sh_r=en.Constraint(m.Time,rule=Q_ts_sh_rule)#Verify if is necessary
    #m.P_max_grid=en.Constraint(m.Time,rule=P_max_rule_grid)

    return m


#Instance
#Energy

def Balance_bu_demand_rule(m,i):
    '''
    Description
    -------
    Balance demand backup heater (HP1) in electricity terms (BU consumption = Electricity from PV, battery and grid). If HP is used for cooling, or if there is no heating constraint is desactivated.
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        return (m.E_bu[i],m.E_PV_bu[i]+m.E_batt_bu[i]+m.E_grid_bu[i])

def Balance_budhw_demand_rule(m,i):
    '''
    Description
    -------
    Balance demand backup heater (hpdhw) in electricity terms (budhw consumption = Electricity from PV, battery and grid). If HP is used for cooling, or if there is no heating constraint is desactivated.
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.DHW:
            return (m.E_budhw[i],m.E_PV_budhw[i]+m.E_batt_budhw[i]+m.E_grid_budhw[i])
        else:
            return en.Constraint.Skip
def Balance_hp_demand_rule(m,i):
    '''
    Description
    -------
    Balance demand HP1 in electricity terms (HP consumption = Electricity from PV, battery and grid). Constraint for E_hp if heating and for E_hp_cooling if cooling. Constraint is desactivated if no heating.
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        return (m.E_hp[i],m.E_PV_hp[i]+m.E_batt_hp[i]+m.E_grid_hp[i])

def Balance_space_heat_demand_1(m,i):
    '''
    Description
    -------
    Balance demand in heating terms (heat production [kWh] = heat demand). Constraint changes on production side, if there is thermal storage, cooling or heating. In the demand side is always the required energy in thermal terms.
    TODO
    -------
    Verify without storage with cooling. I think we need return(-m.Q_ts_sh[i],m.Req_kWh[i])
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.T_storage==False:
            if m.DHW:
                #return (m.Q_ts_sh[i]+m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time)==0)#Balance
                #return(m.Q_ts_sh[i]+m.Q_hp_sh[i],m.Req_kWh[i])#
                return (sum(m.Q_ts_sh[i]+m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time_1)==0)#Balance
                #return ((sum(sum(m.Q_ts_sh[i-3:i])+sum(m.Q_hp_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

            else:
                #return(m.Q_hp_sh[i],m.Req_kWh[i])
                return (sum(m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time_1)==0)#Balance
                #return ((sum(sum(m.Q_hp_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

            #with cooling is the same thing
        else:
            #return(m.Q_ts_sh[i],m.Req_kWh[i])#+m.Q_hp_sh[i]
            return (sum(m.Q_ts_sh[i]-m.Req_kWh[i] for i in m.Time_1)==0)#Balance
            #return ((sum(sum(m.Q_ts_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

def Balance_space_heat_demand_2(m,i):
    '''
    Description
    -------
    Balance demand in heating terms (heat production [kWh] = heat demand). Constraint changes on production side, if there is thermal storage, cooling or heating. In the demand side is always the required energy in thermal terms.
    TODO
    -------
    Verify without storage with cooling. I think we need return(-m.Q_ts_sh[i],m.Req_kWh[i])
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.T_storage==False:
            if m.DHW:
                #return (m.Q_ts_sh[i]+m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time)==0)#Balance
                #return(m.Q_ts_sh[i]+m.Q_hp_sh[i],m.Req_kWh[i])#
                return (sum(m.Q_ts_sh[i]+m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time_2)==0)#Balance
                #return ((sum(sum(m.Q_ts_sh[i-3:i])+sum(m.Q_hp_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

            else:
                #return(m.Q_hp_sh[i],m.Req_kWh[i])
                return (sum(m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time_2)==0)#Balance
                #return ((sum(sum(m.Q_hp_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

            #with cooling is the same thing
        else:
            #return(m.Q_ts_sh[i],m.Req_kWh[i])#+m.Q_hp_sh[i]
            return (sum(m.Q_ts_sh[i]-m.Req_kWh[i] for i in m.Time_2)==0)#Balance
            #return ((sum(sum(m.Q_ts_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

def Balance_space_heat_demand_3(m,i):
    '''
    Description
    -------
    Balance demand in heating terms (heat production [kWh] = heat demand). Constraint changes on production side, if there is thermal storage, cooling or heating. In the demand side is always the required energy in thermal terms.
    TODO
    -------
    Verify without storage with cooling. I think we need return(-m.Q_ts_sh[i],m.Req_kWh[i])
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.T_storage==False:
            if m.DHW:
                #return (m.Q_ts_sh[i]+m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time)==0)#Balance
                #return(m.Q_ts_sh[i]+m.Q_hp_sh[i],m.Req_kWh[i])#
                return (sum(m.Q_ts_sh[i]+m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time_3)==0)#Balance
                #return ((sum(sum(m.Q_ts_sh[i-3:i])+sum(m.Q_hp_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

            else:
                #return(m.Q_hp_sh[i],m.Req_kWh[i])
                return (sum(m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time_3)==0)#Balance
                #return ((sum(sum(m.Q_hp_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

            #with cooling is the same thing
        else:
            #return(m.Q_ts_sh[i],m.Req_kWh[i])#+m.Q_hp_sh[i]
            return (sum(m.Q_ts_sh[i]-m.Req_kWh[i] for i in m.Time_3)==0)#Balance
            #return ((sum(sum(m.Q_ts_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

def Balance_space_heat_demand_4(m,i):
    '''
    Description
    -------
    Balance demand in heating terms (heat production [kWh] = heat demand). Constraint changes on production side, if there is thermal storage, cooling or heating. In the demand side is always the required energy in thermal terms.
    TODO
    -------
    Verify without storage with cooling. I think we need return(-m.Q_ts_sh[i],m.Req_kWh[i])
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.T_storage==False:
            if m.DHW:
                #return (m.Q_ts_sh[i]+m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time)==0)#Balance
                #return(m.Q_ts_sh[i]+m.Q_hp_sh[i],m.Req_kWh[i])#
                return (sum(m.Q_ts_sh[i]+m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time_4)==0)#Balance
                #return ((sum(sum(m.Q_ts_sh[i-3:i])+sum(m.Q_hp_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

            else:
                #return(m.Q_hp_sh[i],m.Req_kWh[i])
                return (sum(m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time_4)==0)#Balance
                #return ((sum(sum(m.Q_hp_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

            #with cooling is the same thing
        else:
            #return(m.Q_ts_sh[i],m.Req_kWh[i])#+m.Q_hp_sh[i]
            return (sum(m.Q_ts_sh[i]-m.Req_kWh[i] for i in m.Time_4)==0)#Balance
            #return ((sum(sum(m.Q_ts_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance


def Balance_space_heat_demand_5(m,i):
    '''
    Description
    -------
    Balance demand in heating terms (heat production [kWh] = heat demand). Constraint changes on production side, if there is thermal storage, cooling or heating. In the demand side is always the required energy in thermal terms.
    TODO
    -------
    Verify without storage with cooling. I think we need return(-m.Q_ts_sh[i],m.Req_kWh[i])
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.T_storage==False:
            if m.DHW:
                #return (m.Q_ts_sh[i]+m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time)==0)#Balance
                #return(m.Q_ts_sh[i]+m.Q_hp_sh[i],m.Req_kWh[i])#
                return (sum(m.Q_ts_sh[i]+m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time_5)==0)#Balance
                #return ((sum(sum(m.Q_ts_sh[i-3:i])+sum(m.Q_hp_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

            else:
                #return(m.Q_hp_sh[i],m.Req_kWh[i])
                return (sum(m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time_5)==0)#Balance
                #return ((sum(sum(m.Q_hp_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

            #with cooling is the same thing
        else:
            #return(m.Q_ts_sh[i],m.Req_kWh[i])#+m.Q_hp_sh[i]
            return (sum(m.Q_ts_sh[i]-m.Req_kWh[i] for i in m.Time_5)==0)#Balance
            #return ((sum(sum(m.Q_ts_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

def Balance_space_heat_demand_6(m,i):
    '''
    Description
    -------
    Balance demand in heating terms (heat production [kWh] = heat demand). Constraint changes on production side, if there is thermal storage, cooling or heating. In the demand side is always the required energy in thermal terms.
    TODO
    -------
    Verify without storage with cooling. I think we need return(-m.Q_ts_sh[i],m.Req_kWh[i])
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.T_storage==False:
            if m.DHW:
                #return (m.Q_ts_sh[i]+m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time)==0)#Balance
                #return(m.Q_ts_sh[i]+m.Q_hp_sh[i],m.Req_kWh[i])#
                return (sum(m.Q_ts_sh[i]+m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time_6)==0)#Balance
                #return ((sum(sum(m.Q_ts_sh[i-3:i])+sum(m.Q_hp_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

            else:
                #return(m.Q_hp_sh[i],m.Req_kWh[i])
                return (sum(m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time_6)==0)#Balance
                #return ((sum(sum(m.Q_hp_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

            #with cooling is the same thing
        else:
            #return(m.Q_ts_sh[i],m.Req_kWh[i])#+m.Q_hp_sh[i]
            return (sum(m.Q_ts_sh[i]-m.Req_kWh[i] for i in m.Time_6)==0)#Balance
            #return ((sum(sum(m.Q_ts_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance


def Balance_space_heat_demand_7(m,i):
    '''
    Description
    -------
    Balance demand in heating terms (heat production [kWh] = heat demand). Constraint changes on production side, if there is thermal storage, cooling or heating. In the demand side is always the required energy in thermal terms.
    TODO
    -------
    Verify without storage with cooling. I think we need return(-m.Q_ts_sh[i],m.Req_kWh[i])
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.T_storage==False:
            if m.DHW:
                #return (m.Q_ts_sh[i]+m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time)==0)#Balance
                #return(m.Q_ts_sh[i]+m.Q_hp_sh[i],m.Req_kWh[i])#
                return (sum(m.Q_ts_sh[i]+m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time_7)==0)#Balance
                #return ((sum(sum(m.Q_ts_sh[i-3:i])+sum(m.Q_hp_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

            else:
                #return(m.Q_hp_sh[i],m.Req_kWh[i])
                return (sum(m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time_7)==0)#Balance
                #return ((sum(sum(m.Q_hp_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

            #with cooling is the same thing
        else:
            #return(m.Q_ts_sh[i],m.Req_kWh[i])#+m.Q_hp_sh[i]
            return (sum(m.Q_ts_sh[i]-m.Req_kWh[i] for i in m.Time_7)==0)#Balance
            #return ((sum(sum(m.Q_ts_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

def Balance_space_heat_demand_8(m,i):
    '''
    Description
    -------
    Balance demand in heating terms (heat production [kWh] = heat demand). Constraint changes on production side, if there is thermal storage, cooling or heating. In the demand side is always the required energy in thermal terms.
    TODO
    -------
    Verify without storage with cooling. I think we need return(-m.Q_ts_sh[i],m.Req_kWh[i])
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.T_storage==False:
            if m.DHW:
                #return (m.Q_ts_sh[i]+m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time)==0)#Balance
                #return(m.Q_ts_sh[i]+m.Q_hp_sh[i],m.Req_kWh[i])#
                return (sum(m.Q_ts_sh[i]+m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time_8)==0)#Balance
                #return ((sum(sum(m.Q_ts_sh[i-3:i])+sum(m.Q_hp_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

            else:
                #return(m.Q_hp_sh[i],m.Req_kWh[i])
                return (sum(m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time_8)==0)#Balance
                #return ((sum(sum(m.Q_hp_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

            #with cooling is the same thing
        else:
            #return(m.Q_ts_sh[i],m.Req_kWh[i])#+m.Q_hp_sh[i]
            return (sum(m.Q_ts_sh[i]-m.Req_kWh[i] for i in m.Time_8)==0)#Balance
            #return ((sum(sum(m.Q_ts_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

def Balance_space_heat_demand_9(m,i):
    '''
    Description
    -------
    Balance demand in heating terms (heat production [kWh] = heat demand). Constraint changes on production side, if there is thermal storage, cooling or heating. In the demand side is always the required energy in thermal terms.
    TODO
    -------
    Verify without storage with cooling. I think we need return(-m.Q_ts_sh[i],m.Req_kWh[i])
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.T_storage==False:
            if m.DHW:
                #return (m.Q_ts_sh[i]+m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time)==0)#Balance
                #return(m.Q_ts_sh[i]+m.Q_hp_sh[i],m.Req_kWh[i])#
                return (sum(m.Q_ts_sh[i]+m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time_9)==0)#Balance
                #return ((sum(sum(m.Q_ts_sh[i-3:i])+sum(m.Q_hp_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

            else:
                #return(m.Q_hp_sh[i],m.Req_kWh[i])
                return (sum(m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time_9)==0)#Balance
                #return ((sum(sum(m.Q_hp_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

            #with cooling is the same thing
        else:
            #return(m.Q_ts_sh[i],m.Req_kWh[i])#+m.Q_hp_sh[i]
            return (sum(m.Q_ts_sh[i]-m.Req_kWh[i] for i in m.Time_9)==0)#Balance
            #return ((sum(sum(m.Q_ts_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

def Balance_space_heat_demand_10(m,i):
    '''
    Description
    -------
    Balance demand in heating terms (heat production [kWh] = heat demand). Constraint changes on production side, if there is thermal storage, cooling or heating. In the demand side is always the required energy in thermal terms.
    TODO
    -------
    Verify without storage with cooling. I think we need return(-m.Q_ts_sh[i],m.Req_kWh[i])
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.T_storage==False:
            if m.DHW:
                #return (m.Q_ts_sh[i]+m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time)==0)#Balance
                #return(m.Q_ts_sh[i]+m.Q_hp_sh[i],m.Req_kWh[i])#
                return (sum(m.Q_ts_sh[i]+m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time_10)==0)#Balance
                #return ((sum(sum(m.Q_ts_sh[i-3:i])+sum(m.Q_hp_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

            else:
                #return(m.Q_hp_sh[i],m.Req_kWh[i])
                return (sum(m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time_10)==0)#Balance
                #return ((sum(sum(m.Q_hp_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

            #with cooling is the same thing
        else:
            #return(m.Q_ts_sh[i],m.Req_kWh[i])#+m.Q_hp_sh[i]
            return (sum(m.Q_ts_sh[i]-m.Req_kWh[i] for i in m.Time_10)==0)#Balance
            #return ((sum(sum(m.Q_ts_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

def Balance_space_heat_demand_11(m,i):
    '''
    Description
    -------
    Balance demand in heating terms (heat production [kWh] = heat demand). Constraint changes on production side, if there is thermal storage, cooling or heating. In the demand side is always the required energy in thermal terms.
    TODO
    -------
    Verify without storage with cooling. I think we need return(-m.Q_ts_sh[i],m.Req_kWh[i])
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.T_storage==False:
            if m.DHW:
                #return (m.Q_ts_sh[i]+m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time)==0)#Balance
                #return(m.Q_ts_sh[i]+m.Q_hp_sh[i],m.Req_kWh[i])#
                return (sum(m.Q_ts_sh[i]+m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time_11)==0)#Balance
                #return ((sum(sum(m.Q_ts_sh[i-3:i])+sum(m.Q_hp_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

            else:
                #return(m.Q_hp_sh[i],m.Req_kWh[i])
                return (sum(m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time_11)==0)#Balance
                #return ((sum(sum(m.Q_hp_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

            #with cooling is the same thing
        else:
            #return(m.Q_ts_sh[i],m.Req_kWh[i])#+m.Q_hp_sh[i]
            return (sum(m.Q_ts_sh[i]-m.Req_kWh[i] for i in m.Time_11)==0)#Balance
            #return ((sum(sum(m.Q_ts_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

def Balance_space_heat_demand_12(m,i):
    '''
    Description
    -------
    Balance demand in heating terms (heat production [kWh] = heat demand). Constraint changes on production side, if there is thermal storage, cooling or heating. In the demand side is always the required energy in thermal terms.
    TODO
    -------
    Verify without storage with cooling. I think we need return(-m.Q_ts_sh[i],m.Req_kWh[i])
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.T_storage==False:
            if m.DHW:
                #return (m.Q_ts_sh[i]+m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time)==0)#Balance
                #return(m.Q_ts_sh[i]+m.Q_hp_sh[i],m.Req_kWh[i])#
                return (sum(m.Q_ts_sh[i]+m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time_12)==0)#Balance
                #return ((sum(sum(m.Q_ts_sh[i-3:i])+sum(m.Q_hp_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

            else:
                #return(m.Q_hp_sh[i],m.Req_kWh[i])
                return (sum(m.Q_hp_sh[i]-m.Req_kWh[i] for i in m.Time_12)==0)#Balance
                #return ((sum(sum(m.Q_hp_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance

            #with cooling is the same thing
        else:
            #return(m.Q_ts_sh[i],m.Req_kWh[i])#+m.Q_hp_sh[i]
            return (sum(m.Q_ts_sh[i]-m.Req_kWh[i] for i in m.Time_12)==0)#Balance
            #return ((sum(sum(m.Q_ts_sh[i-3:i])-sum(m.Req_kWh[i-3:i])) for i in m.subset_tank_day)==0)#Balance
            
def Change_tank_thermal_energy_rule(m,i):
    '''
    Description
    -------
    Change in tank thermal energy (Q_ts_delta [kWh]) is given by the change in tank temperature times the mass times the specific heat of water.
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.T_storage==False:
            if m.DHW:
                if m.toy==1:
                    #return en.Constraint.Skip
                    return((m.T_ts[i] ),(m.T_min[i]))
                elif m.toy==3:
                    return((m.T_ts[i] ),(m.T_min[i]))
                elif m.toy==2:
                    return((m.T_ts[i] ),(m.T_min[i]))
                else:
                    return(m.Q_ts_delta[i],((m.T_ts[i]-m.T_ts[i-1])*m.m*m.c_p))
            else:
                return en.Constraint.Skip
        else:
            if m.toy==1:
                #return en.Constraint.Skip
                return((m.T_ts[i] ),(m.T_min[i]))
            elif m.toy==3:
                return((m.T_ts[i] ),(m.T_min[i]))
            elif m.toy==2:
                return((m.T_ts[i] ),(m.T_min[i]))
            else:
                return(m.Q_ts_delta[i],((m.T_ts[i]-m.T_ts[i-1])*m.m*m.c_p))

def Available_tank_thermal_energy_rule(m,i):
    '''
    Description
    -------
    Thermal energy available in the tank (Q_ts [kWh]) is given by the temperature of the tank at time t (T_ts) and the minimum temperature accepted in the tank (T_min) times the mass times the specific heat of water. If cooling T_min is 293.15 K (20°C).
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.T_storage==False:
            if m.DHW:
                if (m.doy>=120)and(m.doy<=274):
                    return(m.Q_ts[i],(0)*m.m*m.c_p)
                else:
                    return(m.Q_ts[i],((m.T_ts[i]-m.T_supply[i])*m.m*m.c_p))
            else:
                return en.Constraint.Skip
        else:
            if (m.doy>=120)and(m.doy<=274):
                return(m.Q_ts[i],(0)*m.m*m.c_p)
            else:
                return(m.Q_ts[i],((m.T_ts[i]-m.T_supply[i])*m.m*m.c_p))

def Balance_hp_supply_rule(m,i):
    '''
    Description
    -------
    Balance of thermal energy supplied by the HP and the backup heater according to the COP. If there is no storage the electricity consumed by the HP times the COP plus the electricity consumed by the backup heater times the COP of the backup heater (i.e. 1) must be equal to the heat provided for space heating (or cooling).
    If there is storage, the electricity supplied times COP must be equal to the delta Q supplied to the tank plus the heat provided for space heating (cooling) plus the losses of the tank. It can be assimiled as Q_char. For cooling signs and COP change.
    TODO
    -------
    Change COP_SH for cooling by COP for cooling (parameter).
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.T_storage==False:
            if m.DHW:
                return ((m.E_hp[i]*m.COP_tank[i]+m.E_bu[i]),m.Q_hp_ts[i]+m.Q_hp_sh[i])
            else:
                return((m.E_hp[i]*m.COP_SH[i]+m.E_bu[i]),(m.Q_hp_sh[i]))

        else:
            return ((m.E_hp[i]*m.COP_tank[i]+m.E_bu[i]),m.Q_hp_ts[i])#+m.Q_hp_sh[i]/m.COP_SH[i])

def Balance_ts(m,i):
    '''
    Description
    -------
    Calcultes tank balance over the day.
    TODO
    -------
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.T_storage==False:
            if m.DHW:
                return ((m.Q_hp_ts[i]),m.Q_ts_delta[i]+m.Q_ts_sh[i]+m.Q_loss_ts[i])#Balance
            else:
                return (m.Q_hp_ts[i],0)
        else:

            return ((m.Q_hp_ts[i]),m.Q_ts_delta[i]+m.Q_ts_sh[i]+m.Q_loss_ts[i])#Balance
def Balance_hp_power(m,i):
    '''
    Description
    -------
    Balance of thermal energy supplied by the HP and the backup heater according to the COP. If there is no storage the electricity consumed by the HP times the COP plus the electricity consumed by the backup heater times the COP of the backup heater (i.e. 1) must be equal to the heat provided for space heating (or cooling).
    If there is storage, the electricity supplied times COP must be equal to the delta Q supplied to the tank plus the heat provided for space heating (cooling) plus the losses of the tank. It can be assimiled as Q_char. For cooling signs and COP change.
    TODO
    -------
    Change COP_SH for cooling by COP for cooling (parameter).
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.T_storage==False:
            if m.DHW:
                return((m.E_hp[i])<=m.HP_power_tank[i]*m.dt)
            else:
                return((m.E_hp[i])<=m.HP_power_SH[i]*m.dt)
        else:
            return((m.E_hp[i])<=m.HP_power_tank[i]*m.dt)

def Balance_hp_dhw_power(m,i):
    '''
    Description
    -------
    Balance of thermal energy supplied by the HP and the backup heater according to the COP. If there is no storage the electricity consumed by the HP times the COP plus the electricity consumed by the backup heater times the COP of the backup heater (i.e. 1) must be equal to the heat provided for space heating (or cooling).
    If there is storage, the electricity supplied times COP must be equal to the delta Q supplied to the tank plus the heat provided for space heating (cooling) plus the losses of the tank. It can be assimiled as Q_char. For cooling signs and COP change.
    TODO
    -------
    Change COP_SH for cooling by COP for cooling (parameter).
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        return((m.E_hpdhw[i])<=m.HP_dhw_power[i]*m.dt)

#TS Constraints
def Ts_losses(m,i):
    '''
    Description
    -------
    Calcultes tank losses as a function of the temperature difference between the tank and the room temperature (Set_T) times the U_value, the tank surface and delta t (since losses are per hour).
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.T_storage==False:
            return(m.Q_loss_ts[i],0)
        else:
            if i==0:
                return(m.Q_loss_ts[i],0)
            else:
                return(m.Q_loss_ts[i],m.dt*m.U*m.A*(m.T_ts[i]-(m.Set_T[i])))



def def_ts_state_rule(m, t):
    '''
    Description
    -------
    Temperature of the tank must be lower than T_min (??) when cooling
    TODO
    -------
    Verify if needed and adjust nomenclature
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.T_storage==False:
            if m.DHW:
                if t==-1:
                    return(m.T_ts[t],m.T_init)# This is what is super important
                else:
                    return en.Constraint.Skip
            else:
                return en.Constraint.Skip
        else:
            if t==-1:
                return(m.T_ts[t],m.T_init)# This is what is super important
            else:
                return en.Constraint.Skip
def def_ts_state2_rule(m, i):
    '''
    Description
    -------
    Temperature of the tank must be lower than T_min (??) when cooling
    TODO
    -------
    Verify if needed and adjust nomenclature
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.T_storage==False:
            if m.DHW:
                return (m.T_ts[i]<=m.T_max[i])
            else:
                return en.Constraint.Skip
        else:
            return (m.T_ts[i]<=m.T_max[i])



#DHW Constraints
def Balance_hp_DHW_rule(m,i):
    '''
    Description
    -------
    Balance demand hpdhw (used for DHW) in electricity terms (HP consumption = Electricity from PV, battery and grid). Skip if not DHW.
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.DHW==False:
            return en.Constraint.Skip
        else:
            return (m.E_hpdhw[i],m.E_PV_hpdhw[i]+m.E_batt_hpdhw[i]+m.E_grid_hpdhw[i])

def Balance_DHW_demand(m,i):
    '''
    Description
    -------
    Balance demand DHWST (storage tank for DHW) in thermal terms (DHWST supply = Heat demand for DHW). Skip if not DHW.
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.DHW==False:
            return en.Constraint.Skip
        else:
            return(m.Q_dhwst_hd[i],m.Req_kWh_DHW[i])#In kWh

def Balance_hp_supply_rule2(m,i):
    '''
    Description
    -------
    Balance supply DHWST (storage tank for DHW) in thermal terms (HP supply (backup heater included) = heat supplied to the DHWST). Skip if not DHW.
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.DHW==False:
            return en.Constraint.Skip
        else:
            return ((m.E_hpdhw[i])*m.COP_DHW[i]+m.E_budhw[i],((m.T_dhwst[i]-m.T_dhwst[i-1])*m.m_dhw*m.c_p_dhw)+m.Q_dhwst_hd[i]+m.Q_loss_dhwst[i])#Q_char

#DHWST Constraints
def DHWST_losses(m,i):
    '''
    Description
    -------
    Calcultes DHW storage tank losses as a function of the temperature difference between the tank and the room temperature (Set_T) times the U_value, the tank surface and delta t (since losses are per hour).
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.DHW==False:
            return en.Constraint.Skip
        else:
            if i==0:
                return(m.Q_loss_dhwst[i],0)
            else:
                return(m.Q_loss_dhwst[i],m.dt*m.U_dhw*m.A_dhw*(m.T_dhwst[i]-(m.Set_T[i])))

def Balance_dhwst(m,t):
    '''
    Description
    -------
    Calcultes DHW storage tank balance over the day.
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.DHW==False:
            return en.Constraint.Skip
        else:
            if t==-1:
                return en.Constraint.Skip
            else:
                return (sum(m.E_hpdhw[t]*m.COP_DHW[t]+m.E_budhw[t]for t in m.Time)
                -sum(((m.T_dhwst[t]-m.T_dhwst[t-1])*m.m_dhw*m.c_p_dhw)+m.Q_dhwst_hd[t]+m.Q_loss_dhwst[t] for t in m.Time)==False)#Balance


def def_dhwst_state_rule(m, t):
    '''
    Description
    -------
    Defines initial temperature of DHW storage tank.
    TODO
    -------
    Verify if useful, probably not. Maybe an easier way is possible.
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        if m.DHW==False:
            return en.Constraint.Skip
        else:
            if t==-1:
                return(m.T_dhwst[t],m.T_min_dhw)
            else:
                return en.Constraint.Skip
############################################################

def Bool_hp_rule_1(m,i):
    '''
    Description
    -------
    If DHW two HPs are used, one for heating/cooling and one for DHW. However, both cannot operate at the same time (in real world only one HP is used). BigM method to solve linear programming models using simplex algorithm. 1/4
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        bigM=500000

        return((m.E_hp[i]+m.E_bu[i])>=-bigM*(m.Bool_hp[i]))

def Bool_hp_rule_2(m,i):
    '''
    Description
    -------
    If DHW two HPs are used, one for heating/cooling and one for DHW. However, both cannot operate at the same time (in real world only one HP is used). BigM method to solve linear programming models using simplex algorithm.2/4
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        bigM=500000

        return((m.E_hp[i]+m.E_bu[i])<=bigM*(1-m.Bool_hpdhw[i]))

def Bool_hp_rule_3(m,i):
    '''
    Description
    -------
    If DHW two HPs are used, one for heating/cooling and one for DHW. However, both cannot operate at the same time (in real world only one HP is used). BigM method to solve linear programming models using simplex algorithm.3/4
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        bigM=500000
        return((m.E_hpdhw[i]+m.E_budhw[i])>=-bigM*(m.Bool_hpdhw[i]))

def Bool_hp_rule_4(m,i):
    '''
    Description
    -------
    If DHW two HPs are used, one for heating/cooling and one for DHW. However, both cannot operate at the same time (in real world only one HP is used). BigM method to solve linear programming models using simplex algorithm.4/4
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        bigM=500000
        return((m.E_hpdhw[i]+m.E_budhw[i])<=bigM*(1-m.Bool_hp[i]))

def HP_1_2(m,i):
    '''
    Description
    -------
    If DHW two HPs are used, one for heating/cooling and one for DHW. However, both cannot operate at the same time (in real world only one HP is used). BigM method to solve linear programming models using simplex algorithm. Restriction to operate only one at time.
    '''
    if m.heating==False:
        return en.Constraint.Skip
    else:
        return (m.Bool_hp[i]+m.Bool_hpdhw[i],1)

###########################################################################

#Battery constraints

def Bool_char_rule_1(m,i):
    '''
    Description
    -------
    Forbids the battery to charge and discharge at the same time 1/5
    '''
    bigM=500000
    return((m.E_dis[i])>=-bigM*(m.Bool_dis[i]))

def Bool_char_rule_2(m,i):
    '''
    Description
    -------
    Forbids the battery to charge and discharge at the same time 2/5
    '''
    bigM=500000
    return((m.E_dis[i])<=0+bigM*(1-m.Bool_char[i]))

def Bool_char_rule_3(m,i):
    '''
    Description
    -------
    Forbids the battery to charge and discharge at the same time 3/5
    '''
    bigM=500000
    return((m.E_char[i])>=-bigM*(m.Bool_char[i]))

def Bool_char_rule_4(m,i):
    '''
    Description
    -------
    Forbids the battery to charge and discharge at the same time 4/5
    '''
    bigM=500000
    return((m.E_char[i])<=0+bigM*(1-m.Bool_dis[i]))

def Batt_char_dis(m,i):
    '''
    Description
    -------
    Forbids the battery to charge and discharge at the same time 5/5
    '''
    return (m.Bool_char[i]+m.Bool_dis[i],1)

def E_dis_hp_rule(m,i):
    '''
    Description
    -------
    Balance of energy discharged from the battery according to whether heating and DHW are used or not. Includes losses at the inverter.
    '''
    if m.heating==False:
        return (m.E_dis[i],m.E_batt_load[i]+m.E_loss_inv_batt[i])
    else:
        if m.DHW==False:
            return(m.E_dis[i],m.E_batt_hp[i]+m.E_batt_load[i]+m.E_batt_bu[i]+m.E_loss_inv_batt[i])
        else:
            return(m.E_dis[i],m.E_batt_hp[i]+m.E_batt_hpdhw[i]+m.E_batt_bu[i]+m.E_batt_budhw[i]+m.E_batt_load[i]+m.E_loss_inv_batt[i])
def Balance_Batt_rule(m,i):
    '''
    Description
    -------
    Balance of the battery charge, discharge and efficiency losses.
    '''
    return (sum(m.E_char[i]for i in m.Time)
            -sum(m.E_dis[i]+m.E_loss_Batt[i] for i in m.Time)==0)

def E_char_rule(m,i):
    '''
    Description
    -------
    Balance of energy charged into the battery from PV and grid.
    '''
    return(m.E_char[i],m.E_PV_batt[i]+m.E_grid_batt[i])

def E_dis_rule(m,i):
    '''
    Description
    -------
    Sets the maximum energy available to be discharged as the SOC - the minimum SOC.
    '''
    return(m.E_dis[i]<=m.SOC[i-1]-m.SOC_min)

#Energy balance constraints

def Bool_cons_rule_1(m,i):
    '''
    Description
    -------
    Forbids the system to inject and export energy at the same time 1/5
    '''
    bigM=500000
    return((m.E_cons[i])>=-bigM*(m.Bool_cons[i]))

def Bool_cons_rule_2(m,i):
    '''
    Description
    -------
    Forbids the system to inject and export energy at the same time 2/5
    '''
    bigM=500000
    return((m.E_cons[i])<=0+bigM*(1-m.Bool_inj[i]))

def Bool_cons_rule_3(m,i):
    '''
    Description
    -------
    Forbids the system to inject and export energy at the same time 3/5
    '''
    bigM=500000
    return((m.E_PV_grid[i])>=-bigM*(m.Bool_inj[i]))

def Bool_cons_rule_4(m,i):
    '''
    Description
    -------
    Forbids the system to inject and export energy at the same time 4/5
    '''
    bigM=500000
    return((m.E_PV_grid[i])<=0+bigM*(1-m.Bool_cons[i]))
def E_storage_rule(m,i):
    '''
    Description
    -------
    Sets initial E_char at 0.
    TODO
    -------
    Verify whether is needed.
    '''
    if m.E_storage==False:
        if i!=-1:
            return (m.E_char[i],0)
        else:
            return en.Constraint.Skip
    else:
        return en.Constraint.Skip
def Cons_rule(m,i):
    '''
    Description
    -------
    Forbids the system to inject and export energy at the same time 5/5
    '''
    return (m.Bool_inj[i]+m.Bool_cons[i],1)

def Grid_cons_rule(m,i):
    '''
    Description
    -------
    Balance of grid consumption, includes the electricity consumed by the battery, the loads, HP1, hpdhw, BU, budhw and losses in the inverter (when charging the battery from the grid).
    TODO
    -------
    To include if elses to reduce the variables used?
    '''
    if m.heating==False:
        return(m.E_cons[i],m.E_grid_batt[i]+m.E_grid_load[i]+m.E_loss_inv_grid[i])
    else:
        if m.DHW==False:
            return(m.E_cons[i],m.E_grid_batt[i]+m.E_grid_load[i]+m.E_grid_hp[i]+m.E_grid_bu[i]+m.E_loss_inv_grid[i])
        else:
            return(m.E_cons[i],m.E_grid_batt[i]+m.E_grid_load[i]+m.E_grid_hp[i]+m.E_grid_hpdhw[i]+m.E_grid_bu[i]+m.E_grid_budhw[i]+m.E_loss_inv_grid[i])

def Balance_PV_rule(m,i):
    '''
    Description
    -------
    Balance of PV consumption, includes the electricity provided to the battery, the loads, HP1, hpdhw, BU, budhw and losses in the inverter and the converter. Includes as well curtailed PV.
    TODO
    -------
    To include if elses to reduce the variables used?
    '''
    if m.heating==False:
        return (m.E_PV[i],m.E_PV_load[i]+m.E_PV_batt[i]+m.E_PV_grid[i]
            +m.E_loss_conv[i]+m.E_loss_inv_PV[i]+m.E_PV_curt[i])
    else:
        if m.DHW==False:
            return (m.E_PV[i],m.E_PV_load[i]+m.E_PV_batt[i]+m.E_PV_grid[i]
            +m.E_PV_hp[i]+m.E_PV_bu[i]+m.E_loss_conv[i]+m.E_loss_inv_PV[i]+m.E_PV_curt[i])
        else:
            return (m.E_PV[i],m.E_PV_load[i]+m.E_PV_batt[i]+m.E_PV_grid[i]
            +m.E_PV_hp[i]+m.E_PV_hpdhw[i]+m.E_PV_bu[i]+m.E_PV_budhw[i]+m.E_loss_conv[i]+m.E_loss_inv_PV[i]+m.E_PV_curt[i])

def Sold_rule(m,i):
    '''
    Description
    -------
    The total PV generation must be greater than the PV electricity injected into the grid and the PV curtailed.
    '''
    return m.E_PV_grid[i]+m.E_PV_curt[i]<=m.E_PV[i]

def Balance_load_rule(m,i):
    '''
    Description
    -------
    Balance of electricity demand, includes the electricity provided by the PV, the battery and the grid.
    TODO
    -------
    include the bi-directional inverter energy standby consumption as a function
    of the inverter power
    '''
    return (m.E_demand_el[i],m.E_PV_load[i]+m.E_batt_load[i]
            +m.E_grid_load[i])#-m.Inverter_power*0.5/100)

def def_storage_state_rule(m, t):
    '''
    Description
    -------
    State of charge definition as the previous SOC plus charged electricity minus losses minus discharged electricity. Stablishes as well the initial SOC at SOC_min
    '''
    if m.E_storage==False:
        return en.Constraint.Skip
    else:

        if t==-1:
            return(m.SOC[t],m.SOC_min)
        else:
            return (m.SOC[t] ==m.SOC[t-1]+m.E_char[t]-m.E_dis[t]-m.E_loss_Batt[t])

#Efficiency losses constraints

def Conv_losses_rule(m,i):
    '''
    Description
    -------
    Converter losses definition. 1-Converter_efficiency times the electricity that pass through the converter. Since E_PV_load, E_PV_batt and E_PV_grid are the energy flows after the inverter, they need to be divided by the inverter efficiency to get the real converter losses
    '''
    if m.heating==False:
        return(m.E_loss_conv[i],((m.E_PV_load[i]+m.E_PV_grid[i])/(m.Inverter_eff)+m.E_PV_batt[i])*(1-m.Converter_eff))
    else:
        if m.DHW==False:
            return(m.E_loss_conv[i],((m.E_PV_load[i]+m.E_PV_grid[i]+m.E_PV_hp[i]+m.E_PV_bu[i])/(m.Inverter_eff)+m.E_PV_batt[i])*(1-m.Converter_eff))
        else:
            return(m.E_loss_conv[i],((m.E_PV_load[i]+m.E_PV_grid[i]+m.E_PV_hp[i]+m.E_PV_hpdhw[i]+m.E_PV_bu[i]+m.E_PV_budhw[i])/(m.Inverter_eff)+m.E_PV_batt[i])*(1-m.Converter_eff))

def Inv_losses_PV_rule(m,i):
    '''
    Description
    -------
    PV inverter losses definition. 1-Inverter_efficiency times the electricity that pass through the Inverter (takes into account only PV related electricity). Since E_PV_load and E_PV_grid are the energy flows after the inverter, they need to be divided by the inverter efficiency to get the real inverter losses.
    '''
    if m.heating==False:
        return(m.E_loss_inv_PV[i],(m.E_PV_grid[i]
           +m.E_PV_load[i])*(1-m.Inverter_eff)/(m.Inverter_eff))
    else:
        if m.DHW==False:
            return(m.E_loss_inv_PV[i],(m.E_PV_grid[i]
           +m.E_PV_load[i]+m.E_PV_hp[i]+m.E_PV_bu[i])*(1-m.Inverter_eff)/(m.Inverter_eff))
        else:
            return(m.E_loss_inv_PV[i],(m.E_PV_grid[i]
           +m.E_PV_load[i]+m.E_PV_hp[i]+m.E_PV_hpdhw[i]+m.E_PV_bu[i]+m.E_PV_budhw[i])*(1-m.Inverter_eff)/(m.Inverter_eff))

def Inv_losses_Batt_rule(m,i):
    '''
    Description
    -------
    Battery inverter losses definition. 1-Inverter_efficiency times the electricity that pass through the Inverter (takes into account only battery related electricity). E_dis is the energy discharged from the battery, thus no need to divide by the inverter efficiency.
    '''
    return(m.E_loss_inv_batt[i],(m.E_dis[i])*(1-m.Inverter_eff))

def Inv_losses_Grid_rule(m,i):
    '''
    Description
    -------
    PV inverter losses definition. 1-Inverter_efficiency times the electricity that pass through the Inverter (takes into account only grid related electricity, i.e. for charging the battery). E_grid_batt does not need to be divided by the inverter efficiency since it is at the consumption side of the system.
    '''
    return(m.E_loss_inv_grid[i],(m.E_grid_batt[i])*(1-m.Inverter_eff))

def Inv_losses_rule(m,i):
    '''
    Description
    -------
    Inverter losses definition. Summation of the PV, battery and grid related losses.
    '''
    return(m.E_loss_inv[i],m.E_loss_inv_grid[i]
           +m.E_loss_inv_batt[i]+m.E_loss_inv_PV[i])

def Batt_losses_rule(m,i):
    '''
    Description
    -------
    Battery losses definition. 1-Battery_efficiency times the electricity that pass through the battery (roundtrip efficiency).
    '''
    return(m.E_loss_Batt[i],(m.E_grid_batt[i]+m.E_PV_batt[i])*(1-m.Efficiency))

#Power

def Inverter_rule(m,i):
    '''
    Description
    -------
    Inverter power definition. All electricity flows through the inverter must be lower than the inverter nominal power (including losses).
    '''
    if m.heating==False:
        return(m.E_PV_grid[i]+m.E_dis[i]+m.E_PV_load[i]+m.E_loss_inv[i]<=m.Inverter_power*m.dt)
    else:
        if m.DHW==False:
            return(m.E_PV_grid[i]+m.E_dis[i]+m.E_PV_load[i]+m.E_PV_hp[i]+m.E_PV_bu[i]+m.E_loss_inv[i]<=m.Inverter_power*m.dt)
        else:
            return(m.E_PV_grid[i]+m.E_dis[i]+m.E_PV_load[i]+m.E_PV_hp[i]+m.E_PV_hpdhw[i]+m.E_PV_bu[i]+m.E_PV_budhw[i]+m.E_loss_inv[i]<=m.Inverter_power*m.dt)

def Converter_rule(m,i):
    '''
    Description
    -------
    Converter power definition. All electricity flows through the Converter must be lower than the inverter nominal power (including losses).
    '''
    if m.heating==False:
        return(m.E_PV_grid[i]+m.E_PV_batt[i]+m.E_PV_load[i]+m.E_loss_conv[i]<=m.Inverter_power*m.dt)
    else:
        if m.DHW==False:
            return(m.E_PV_grid[i]+m.E_PV_batt[i]+m.E_PV_load[i]+m.E_PV_hp[i]+m.E_PV_bu[i]+m.E_loss_conv[i]<=m.Inverter_power*m.dt)
        else:
            return(m.E_PV_grid[i]+m.E_PV_batt[i]+m.E_PV_load[i]+m.E_PV_hp[i]+m.E_PV_hpdhw[i]+m.E_PV_bu[i]+m.E_PV_budhw[i]+m.E_loss_conv[i]<=m.Inverter_power*m.dt)

def Inverter_grid_rule(m,i):
    '''
    Description
    -------
    Inverter power definition. All electricity flows through the inverter must be lower than the inverter nominal power (including losses). This rule is used for grid charging only.
    '''
    return(m.E_grid_batt[i]+m.E_loss_inv_grid[i]<=m.Inverter_power*m.dt)

def P_max_rule(m,i):
    '''
    Description
    -------
    Calculates the maximum power drained from the grid each day.
    TODO
    -------
    include the same rule for PV injection as well
    #def P_max_rule_grid(m,i):
    return (m.E_PV_grid[i]<=m.P_max_day*m.dt)
    '''
    return(m.E_cons[i]<=m.P_max_day*m.dt)
def P_max_rule_grid(m,i):
    return (m.E_PV_grid[i]<=m.P_max_day*m.dt)
#App

def Curtailment_rule(m,i):
    '''
    Description
    -------
    Restrains the maximum PV injection into the grid (in kW) if avoidance of PV curtailment is activated. In the other case it skips the rule since PV curtailed is not necessarily zero, it depends as well on the inverter size.
    '''
    if m.PVAC==False:
        return en.Constraint.Skip
    else:
        return m.E_PV_grid[i]<=m.Max_injection*m.dt

def DLS_rule(m,i):
    '''
    Description
    -------
    Sets the flows from grid to the battery to zero if demand load shifting is not activated. In the other case it skips the rule.
    '''
    if m.DLS==True:
        return en.Constraint.Skip
    else:
        return(m.E_grid_batt[i]==False)

#Objective

def Obj_fcn(m):
    '''
    Description
    -------
    The bill is calculated in two parts, the energy related part is the retail price times the energy consumed from the grid minus the export price times the PV injection. If there is demand peak shaving (a capacity tariff is applied) the maximum power taken from the grid (in kW) is multiplied by the DAILY capacity tariff ($/kW per day).
    '''
    return(sum((m.retail_price[i]*m.E_cons[i])
    -(m.export_price[i]*m.E_PV_grid[i]) for i in m.Time))*m.PVSC+(m.P_max_day*m.capacity_tariff)*m.DPS
