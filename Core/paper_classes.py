import pandas as pd
import numpy as np
class Hardware_Prices:
    '''
    Prices in Pena-Bello et al. 2017 maybe more (inverter) because is one for PV and Batt
    '''
    def __init__(self,Inverter_power):
        #Prices are in USD/kW
        self.Price_PV=1500
        self.Price_inverter=880+304*Inverter_power
        self.PV_cal_life=25
        self.Inverter_cal_life=25
        self.Interest_rate=0.04

class Battery(object):
    '''
    Battery object with a selected capacity.
    Change rate from EUR to USD 1.18 as of August 2017
    '''

    def __init__(self,Capacity,  **kwargs):
        super().__init__(**kwargs)
        self.Capacity = Capacity
        self.EUR_USD=1.18
class Battery_tech(Battery):
    '''
    Battery object with default values for different battery technologies.
    NMC (Tesla), NCA (Trina BESS), LFP (Fortelion), LTO (Leclanche),
    ALA (Fukurawa) and VRLA (Sonnenschein).
    Based on Parra & Patel, 2016 and Datasheets
    Price in USD/kWh in Pena-Bello et al. 2017 it changes according to the techno.
    TODO
    ------
    Years of usage as a variable to modify efficiency may be included as well as ageing
    '''
    def __init__(self, Technology,**kwargs):
        super().__init__(**kwargs)
        self.Technology = Technology
        if self.Technology=='NMC':#Tesla
                defaults = {'Efficiency': 0.918,
                'P_max_dis': -0.4*self.Capacity,
                'P_max_char': 0.4*self.Capacity,
                'SOC_max': 1*self.Capacity,
                'SOC_min': 0*self.Capacity,
                'Price_battery': 410*self.Capacity,
                'Battery_cal_life': 15,
                'Battery_cycle_life': 5000,
                'PCS_costs': 441*self.EUR_USD,
                'BOS_costs':2187*self.EUR_USD,
                'OandM_costs': 0,
                'Fix_costs': 0,
                'EoL': 0.7,
                'IRENA_future_Price':167*self.Capacity}

                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)
###############################################################################
        elif self.Technology=='NCA': #TRINA BESS
                defaults = {'Efficiency': 0.925,
                'P_max_dis': -1*self.Capacity,
                'P_max_char': 1*self.Capacity,
                'SOC_max': 1*self.Capacity,
                'SOC_min': 0*self.Capacity,
                'Price_battery': 650*self.Capacity,
                'Battery_cal_life': 20,
                'Battery_cycle_life': 8000,
                'PCS_costs': 286.65*self.EUR_USD,
                'BOS_costs':2241*self.EUR_USD,
                'OandM_costs': 0,
                'Fix_costs': 0,
                'EoL': 0.7,
                'IRENA_future_Price':145*self.Capacity}
                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)

###############################################################################
        elif self.Technology=='LFP':#Sony Fortelion
                defaults = {'Efficiency': 0.94,
                'P_max_dis': -2*self.Capacity,
                'P_max_char': 2*self.Capacity,
                'SOC_max': 1*self.Capacity,
                'SOC_min': 0*self.Capacity,
                'Price_battery': 980*self.Capacity,#USD,
                'Battery_cal_life': 20,
                'Battery_cycle_life': 6000, #Battery_cycle_life @ 80%DOD
                'PCS_costs': 607*self.EUR_USD,
                'BOS_costs':2061*self.EUR_USD,
                'OandM_costs': 0,
                'Fix_costs': 0,
                'EoL': 0.7,
                'IRENA_future_Price':224*self.Capacity}

                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)


###############################################################################
        elif self.Technology=='LTO':
                defaults = {'Efficiency': 0.967,
                'P_max_dis': -4*self.Capacity,
                'P_max_char': 4*self.Capacity,
                'SOC_max': 1*self.Capacity,
                'SOC_min': 0*self.Capacity,
                'Price_battery': 1630*self.Capacity,
                'Battery_cal_life': 25,
                'Battery_cycle_life': 15000,
                'PCS_costs': 287*self.EUR_USD,
                'BOS_costs':1622*self.EUR_USD,
                'OandM_costs': 0,
                'Fix_costs': 0,
                'EoL': 0.7,
                'IRENA_future_Price':480*self.Capacity}
                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)

###############################################################################
        elif self.Technology=='ALA':
                defaults = {'Efficiency': 0.91,
                'P_max_dis': -1*self.Capacity,
                'P_max_char': 1*self.Capacity,
                'SOC_max': 0.9*self.Capacity,
                'SOC_min': 0.2*self.Capacity,
                'Price_battery': 750*self.Capacity,
                'Battery_cal_life': 15,
                'Battery_cycle_life': 4500,
                'PCS_costs': 766,
                'BOS_costs':2030*self.EUR_USD,
                'OandM_costs': 22*self.EUR_USD,
                'Fix_costs': 0,
                'EoL': 0.7,
                'IRENA_future_Price':330*self.Capacity}
                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)
###############################################################################
        elif self.Technology=='VRLA':
                defaults = {'Efficiency': 0.85,
                'P_max_dis': -0.1*self.Capacity,
                'P_max_char': 0.1*self.Capacity,
                'SOC_max': 1*self.Capacity,
                'SOC_min': 0.5*self.Capacity,
                'Price_battery': 330*self.Capacity,
                'Battery_cal_life': 10,
                'Battery_cycle_life': 1500,
                'PCS_costs': 466*self.EUR_USD,
                'BOS_costs':1143*self.EUR_USD,
                'OandM_costs': 0,
                'Fix_costs': 0,
                'EoL': 0.7,
                'IRENA_future_Price':150*self.Capacity}
                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)

###############################################################################
        elif self.Technology=='test':
                defaults = {'Efficiency': 0.95,
                'P_max_dis': -1*self.Capacity,
                'P_max_char': 1*self.Capacity,
                'SOC_max': 1*self.Capacity,
                'SOC_min': 0*self.Capacity,
                'Price_battery': 450*self.Capacity,
                'Battery_cal_life': 15,
                'Battery_cycle_life': 5000,
                'PCS_costs': 466*self.EUR_USD,
                'BOP_costs': 0,
                'OandM_costs': 0,
                'Fix_costs': 0,
                'EoL': 0.7}
                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)

###############################################################################
        else:
                raise ValueError


class Battery_case(Battery_tech): #Based on Schmidt et al. (2019)
    '''
    Include the values of Schmidt et al. (2019) for comparison using
    NMC, NCA, LFP, LTO and VRLA technologies.
    TODO
    -----
    include ALA
    '''
    def __init__(self,case, **kwargs):
        super().__init__(**kwargs)
        self.case = case
        if self.Technology=='NMC':
            if self.case=='mean':
                defaults = {
                'Efficiency': 0.89,
                'Price_battery': 335*self.Capacity,
                'Battery_cal_life': 15,
                'Battery_cycle_life': 4996,
                'SOC_max': 0.965*self.Capacity,
                'SOC_min': 0.035*self.Capacity}
                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)
            elif self.case=='min':
                defaults = {
                'Efficiency': 0.87,
                'Price_battery': 250*self.Capacity,
                'Battery_cal_life': 5,
                'Battery_cycle_life': 2555,
                'SOC_max': 0.965*self.Capacity,
                'SOC_min': 0.035*self.Capacity}
                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)
            elif self.case=='max':
                defaults = {
                'Efficiency': 0.92,
                'Price_battery': 420*self.Capacity,
                'Battery_cal_life': 20,
                'Battery_cycle_life': 8000,
                'SOC_max': 0.965*self.Capacity,
                'SOC_min': 0.035*self.Capacity}
                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)
        elif self.Technology=='NCA':
            if self.case=='mean':
                defaults = {
                'Efficiency': 0.89,
                'Price_battery': 281*self.Capacity,
                'Battery_cal_life': 12,
                'Battery_cycle_life': 2498,
                'SOC_max': 0.965*self.Capacity,
                'SOC_min': 0.035*self.Capacity}
                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)
            elif self.case=='min':
                defaults = {
                'Efficiency': 0.87,
                'Price_battery': 210*self.Capacity,
                'Battery_cal_life': 5,
                'Battery_cycle_life': 1278,
                'SOC_max': 0.965*self.Capacity,
                'SOC_min': 0.035*self.Capacity}
                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)
            elif self.case=='max':
                defaults = {
                'Efficiency': 0.92,
                'Price_battery': 352*self.Capacity,
                'Battery_cal_life': 20,
                'Battery_cycle_life': 4000,
                'SOC_max': 0.965*self.Capacity,
                'SOC_min': 0.035*self.Capacity}
                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)
        elif self.Technology=='LFP':
            if self.case=='mean':
                defaults = {
                'Efficiency': 0.87,
                'Price_battery': 461*self.Capacity,
                'Battery_cal_life': 12,
                'Battery_cycle_life': 6529,
                'SOC_max': 0.965*self.Capacity,
                'SOC_min': 0.035*self.Capacity}
                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)
            elif self.case=='min':
                defaults = {
                'Efficiency': 0.84,
                'Price_battery': 344*self.Capacity,
                'Battery_cal_life': 5,
                'Battery_cycle_life': 2000,
                'SOC_max': 0.965*self.Capacity,
                'SOC_min': 0.035*self.Capacity}
                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)
            elif self.case=='max':
                defaults = {
                'Efficiency': 0.89,
                'Price_battery': 587*self.Capacity,
                'Battery_cal_life': 20,
                'Battery_cycle_life': 10000,
                'SOC_max': 0.965*self.Capacity,
                'SOC_min': 0.035*self.Capacity}
                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)
        elif self.Technology=='LTO':
            if self.case=='mean':
                defaults = {
                'Efficiency': 0.91,
                'Price_battery': 900*self.Capacity,
                'Battery_cal_life': 23,
                'Battery_cycle_life': 15000,
                'SOC_max': 1*self.Capacity,
                'SOC_min': 0*self.Capacity}
                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)
            elif self.case=='min':
                defaults = {
                'Efficiency': 0.88,
                'Price_battery': 800*self.Capacity,
                'Battery_cal_life': 20,
                'Battery_cycle_life': 5000,
                'SOC_max': 1*self.Capacity,
                'SOC_min': 0*self.Capacity}
                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)
            elif self.case=='max':
                defaults = {
                'Efficiency': 0.95,
                'Price_battery': 1000*self.Capacity,
                'Battery_cal_life': 25,
                'Battery_cycle_life': 20000,
                'SOC_max': 1*self.Capacity,
                'SOC_min': 0*self.Capacity}
                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)

        elif self.Technology=='ALA':
            if self.case=='mean':
                defaults = {
                'Efficiency': 0.918,
                'Price_battery': 410*self.Capacity,
                'Battery_cal_life': 15,
                'Battery_cycle_life': 5000,
                'SOC_max': 0.9*self.Capacity,
                'SOC_min': 0.2*self.Capacity}
                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)
            elif self.case=='min':
                defaults = {
                'Efficiency': 0.87,
                'Price_battery': 250*self.Capacity,
                'Battery_cal_life': 5,
                'Battery_cycle_life': 2555,
                'SOC_max': 0.9*self.Capacity,
                'SOC_min': 0.2*self.Capacity}
                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)
            elif self.case=='max':
                defaults = {
                'Efficiency': 0.92,
                'Price_battery': 420*self.Capacity,
                'Battery_cal_life': 20,
                'Battery_cycle_life': 8000,
                'SOC_max': 0.9*self.Capacity,
                'SOC_min': 0.2*self.Capacity}
                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)

        elif self.Technology=='VRLA':
            if self.case=='mean':
                defaults = {
                'Efficiency': 0.75,
                'Price_battery': 263*self.Capacity,
                'Battery_cal_life': 9,
                'Battery_cycle_life': 1500,
                'SOC_max': 0.95*self.Capacity,
                'SOC_min': 0.4*self.Capacity}
                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)
            elif self.case=='min':
                defaults = {
                'Efficiency': 0.73,
                'Price_battery': 105*self.Capacity,
                'Battery_cal_life': 3,
                'Battery_cycle_life': 250,
                'SOC_max': 0.95*self.Capacity,
                'SOC_min': 0.4*self.Capacity}
                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)
            elif self.case=='max':
                defaults = {
                'Efficiency': 0.78,
                'Price_battery': 473*self.Capacity,
                'Battery_cal_life': 15,
                'Battery_cycle_life': 2500,
                'SOC_max': 0.95*self.Capacity,
                'SOC_min': 0.4*self.Capacity}
                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)

###############################################################################
        else:
                raise ValueError
#-------------------------------------------------------------------------------
class hp(object):
    '''
    hp object with a selected thermal power.
    Change rate from EUR to USD 1.18 as of August 2017
    Parameters
    ----------
    Power: float; Thermal power [lookup table only available for 4,6,8,11,14,16] otherwise use COP_static @ 2.5
    Returns
    ------
    hp object with power and COP_static
    '''

    def __init__(self,power,  **kwargs):
        #super().__init__(**kwargs)
        self.power = power#Power refers to thermal power
        self.COP_static=2.5
        self.EUR_USD=1.18

class HP_tech(hp):
    '''
    Air to water HP object with default values for investment_cost, installation_costs, operation_costs and calendar_life
    Based on Swisstore project data
    Parameters
    ----------
    hp: hp class
    Returns
    ------
    hp class with investment_onsts, calendar_life, operation and intallation costs
    Comments
    ------
    Contains a method to use a lookup table only available for ratings in [4,6,8,11,14,16]
    TODO
    ------
    Prices are for air-water HP
    For Air source HP outside temperature is used
    For Ground source HP the ground temperature should be used, but the same methodology should apply
    '''
        
    def find_interval_hp_method(self, x, partition):
        '''
        Description
        -----------
        find_interval at which x belongs inside partition. Returns the index i.
        Parameters
        ------
        x: float; numerical value
        partition: array; sequence of numerical values
        Returns
        ------
        i: index; index for which applies
        partition[i] < x < partition[i+1], if such an index exists.
        -1 otherwise
        TODO
        ------
        '''

        for i in range(0, len(partition)):
            if x <= partition[i]:
                return i
        if x >partition[i]:
            return i

    def include_COP_from_lookup_table_method(self,dist_temperature,df):
        '''
        Description
        -----------
        Includes COP_SH and COP_DHW in the given df for the given hp power rating.
        Parameters
        ------
        df: dataframe including outdoor temperature (df.Temp) in Celcius
        hp: hp class
        dist_temperature: int; Temperature of distribution in celcius or kelvin
        Returns
        ------
        df: dataframe; including the columns COP_SH and COP_DHW for the given Temperature
        TODO
        ------
        '''
        try:
            
            if dist_temperature>200:
                lookup_table=self.COP_lookup_method(dist_temperature).reset_index()
                
                df.loc[:,'COP_SH']=df.apply(lambda x:  lookup_table.loc[self.find_interval_hp_method(x.Temp+273.15,lookup_table.T_outside),['COP']].values[0],axis=1)
                lookup_table=self.COP_lookup_method(dist_temperature=55+273.15).reset_index()#DHW @ 55
                df.loc[:,'COP_DHW']=df.apply(lambda x:  lookup_table.loc[self.find_interval_hp_method(x.Temp+273.15,lookup_table.T_outside),['COP']].values[0],axis=1)
            
                return df
            else:
                lookup_table=self.COP_lookup_method(dist_temperature+273.15).reset_index()
                df.loc[:,'COP_SH']=df.apply(lambda x:  lookup_table.loc[self.find_interval_hp_method(x.Temp+273.15,lookup_table.T_outside),['COP']].values[0],axis=1)
                lookup_table=self.COP_lookup_method(dist_temperature=55+273.15).reset_index()#DHW @ 55
                df.loc[:,'COP_DHW']=df.apply(lambda x:  lookup_table.loc[self.find_interval_hp_method(x.Temp+273.15,lookup_table.T_outside),['COP']].values[0],axis=1)
            
                return df
        except:
            print('An exception occurred.')
            print('%%%% Warning %%%%\nNone was returned')
            return None
    def COP_lookup_method(self,dist_temperature):
        '''
        Loads the HP data from Hoval Belaria (provided by Philip Schutz from HSLU)
        Parameters
        ----------
        dist_temperature: float; Temperature of distribution in kelvin or celsius
        Returns
        ------
        df_out: dataframe; lookup table for the given power and temperature of distribution temperatures in kelvin
        Comments
        ------
        Temperature in HP_data is in Celcius, it is converted in K for the output
        TODO
        ------
        Include other power rating
        '''
        try:
            if dist_temperature>200:
                print('Distribution temperature in Kelvin')
                df_hp=pd.read_csv('Input/HP_data.csv',sep=';')# Temperature in celcius
                df_hp.loc[:,'T_dist']+=273.15
                df_hp.loc[:,'T_outside']+=273.15
                df_hp.loc[:,'P_el']=df_hp.loc[:,'P_el'].str.replace(',','.').astype(float)
                df_hp.loc[:,'COP']=df_hp.loc[:,'COP'].str.replace(',','.').astype(float)

                df_out=df_hp.loc[(df_hp.HP_rating==self.power) & (df_hp.T_dist==dist_temperature),:].copy()
                if df_out.empty:
                    print('The distribution temperature selected is not supported.')
                    print('%%%% Warning %%%%\nNone was returned')
                    return None
                else:
                    print('Output temperatures in Kelvin')
                    return df_out    
            else:
                print('Distribution temperature in Celsius')
                df_hp=pd.read_csv('Input/HP_data.csv',sep=';')# Temperature in celcius
                df_hp.loc[:,'T_dist']+=273.15
                df_hp.loc[:,'T_outside']+=273.15
                df_hp.loc[:,'P_el']=df_hp.loc[:,'P_el'].str.replace(',','.').astype(float)
                df_hp.loc[:,'COP']=df_hp.loc[:,'COP'].str.replace(',','.').astype(float)

                df_out=df_hp.loc[(df_hp.HP_rating==self.power) & (df_hp.T_dist==dist_temperature+273.15),:].copy()
                if df_out.empty:
                    print('The distribution temperature selected is not supported.')
                    print('%%%% Warning %%%%\nNone was returned')
                    return None
                else:
                    print('Output temperatures in Kelvin')
                    return df_out    
        except:
            print('An exception occurred.')
            print('%%%% Warning %%%%\nNone was returned')
            return None

    def __init__(self, technology,**kwargs):
        '''
        Init method for hp_tech subclass
        Parameters
        ----------
        hp: hp class
        technology: string; should be air-water (ASHP), water-water or brine-water (GSHP)
        Returns
        ------
        hp class with investment_onsts, calendar_life, operation and intallation costs
        Comments
        ------
        Contains a method to use a lookup table only available for ratings in [4,6,8,11,14,16]
        TODO
        ------
        Prices are for air-water HP
        For Air source HP outside temperature is used
        For Ground source HP the ground temperature should be used, but the same methodology should apply?
        GSHP are brine-water?
        actualize the GSHP data
        '''
        super().__init__(**kwargs)
        self.technology = technology
        #self.dist_temperature = dist_temperature
        if self.technology=='ASHP':
                defaults = {
                'investment_cost': 1608*self.power,#Swisstore project data; cost per kW_th
                'calendar_life': 20,
                'operation_costs': 190,#cost per year
                'installation_costs':158*self.power,#cost per kW_th
                'power_el':self.power/1.5
                }

                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)
        elif self.technology=='GSHP':
                print('warning: data must be actualized')
                defaults = {
                'investment_cost': 1*self.power,#Swisstore project data; cost per kW_th
                'calendar_life': 1,
                'operation_costs': 1,#cost per year
                'installation_costs':1*self.power,#cost per kW_th
                'power_el':self.power/1.5
                }

                for key, val in defaults.items():
                    setattr(self, key, val)
                self.__dict__.update(kwargs)
        else:
                raise ValueError
#-------------------------------------------------------------------------------

class heat_storage_tank(object):
    '''
    Heat storage tank object definition
    
    Parameters
    ----------
    Power: float; Thermal power [lookup table only available for 4,6,8,11,14,16] otherwise use COP_static @ 2.5
    TODO
    ------
    Actualize the default values
    
    Returns
    ------
    hp object with power and COP_static
    '''

    def __init__(self,mass,  **kwargs):
        #super().__init__(**kwargs)
        self.mass = mass#in kg of water
        
        defaults = {
        'investment_cost': 1608*self.mass,#Swisstore project data; cost per kW_th
        'calendar_life': 20,
        'operation_costs': 190,#cost per year
        'installation_costs':158*self.mass,#cost per kW_th
        'specific_heat':0.00116, #kWh/(l*K)
        #'mass':200, #l for a 200 liter tank
        'U_value':0.36/1000, #kW/(m2*K)
        'surface':2.39, # For a 200 liter tank with 0.26 height and .5 radius (m2)
        't_max':333.15, #60°C
        't_min':323.15 #50°C
        }

        for key, val in defaults.items():
            setattr(self, key, val)
        self.__dict__.update(kwargs)