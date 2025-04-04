import pandas as pd 
import time 
from datetime import datetime,timedelta
import os
import logging

path = os.getcwd()
path= os.path.join(path,'Botkapil')
path= str(path)
logpath= os.path.join(path,'botlogs/strategy1.logs')
logpath= os.path.normpath(logpath)
print(logpath,'logpath')
logging.basicConfig(level=logging.DEBUG,filename=str(logpath),format="%(asctime)s - %(levelname)s - %(message)s",datefmt="%d-%m-%y %H:%M:%S")
logger= logging.getLogger("Strategy1 Bollingerband")


class strategy:
    def __init__(self):
        self.settings= self.loadsettings()
        
    def  loadsettings(self):
        try:

            logpath= os.path.join(path,'congif/config.logs')
            logpath= os.path.normpath(logpath)

            filepath=str(path)
            with open() as file:
                settings= file['settings']

            return settings
        except Exception as e:
            logger.error(e)
    def bollingerband(self):
        pass
    def crossover(self):
        pass

    def ema(self):
        pass

    def stdeviation(self,data,period):


        pass

    def trend(self,data,period):
        ema= self.ema(data,period)
        buyconditons= ema.loc[ema['close']>ema['ema']]
        sellcondtions= ema[ema['close']<ema['ema']]
        

        return buyconditons,sellcondtions

    def sma(self,data,period):
        pass

    def volumeconditon(self,data,period,stdperiod):
        vol_std= self.stdeviation(data,stdperiod)
        sma= self.sma(vol_std,period)
        buy_sell_condition_vol= sma.loc[sma['vol_std']>sma['volumesma']]


        return buy_sell_condition_vol
    

    def conditons(self):
        upper,lower= self.bollingerband()
        buyconditonbb= self.crossover(close,upper)
        sellcondtionsbb= self.crossover(close,lower)
        buy_condition_trend,sell_contition_trend=  self.trend(data,trendperiod)
        volumeconditon= self.volumeconditon(data,volumeperiod,stdperiod)
        pass

        
    