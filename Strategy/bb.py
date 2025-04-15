from Bot import env
import pandas as pd 
import time 
from datetime import datetime,timedelta
import os
import logging
import json
from Bot.utility import utility
import pytz

path= env.currenenv

logpath= os.path.join(path,'botlogs/strategy1.logs')
logpath= os.path.normpath(logpath)
print(logpath,'logpath')
logger=env.setup_logger(logpath)


class strategy:
    def __init__(self):
        self.utilityobj= utility.misc()
        self.settings= self.utilityobj.loadsettings()
    
    def bollingerband(self,data,period,stdperiod,mult):
        try:

            data['basis']= data['close'].rolling(period).mean()
            data['stddata']= data['close'].rolling(stdperiod).std()
            data['dev'] = mult*data['stddata']
            data['upper']=data['basis']+data['dev']
            data['lower']=data['basis']-data['dev']
            data['buy_final']= False
            data['sell_final']= False


            print(data,'check data ')
            return data
        
        except Exception as e:
            logger.error(e,exc_info=True)

        
    def crossover(self,data):
        try:
            data['buyconditions']=False
            data['sellconditions']=False

            for i in range(len(data)):
                if data['close'].iloc[i]>data['upper'].iloc[i]:
                    data.loc[i,'buyconditions']=True
                elif data['close'].iloc[i]<data['lower'].loc[i]:
                    data.loc[i,'sellconditions']=True


            return data
        except Exception as e:
            logger.error(e)
            

    def ema(self,data,length):
        alpha = 2 / (length + 1)
        data['ema']=pd.Series(data['close']).ewm(alpha=alpha, adjust=False).mean()

        return data

    def stdeviation(self,data,period):
        data['vol_std']=pd.Series(data['close']).rolling(period).std()
        return data


    def trend(self,data,period):
        data= self.ema(data,period)

        data['buyconditonTrend']= data['close']>data['ema']
        data['sellconditonTrend']= data['close']<data['ema']
        

        return data

    def sma(self,data,period):
        data['volumesma']=pd.Series(data['vol_std']).rolling(period).mean()
        return data
    

    def volumeconditon(self,data,period,stdperiod):
        data= self.stdeviation(data,stdperiod)
        data= self.sma(data,period)
        data['buy_sell_condition_vol']= data['vol_std']>data['volumesma']


        return data
    

    def conditons(self,data):
        try:
            bbperiod=self.settings['BBLEN']
            mult=self.settings['BBLEN']
            BBSTDEVE=int(self.settings['BBSTDEVE'])
            trendperiod=self.settings['trend_period']
            stdperiod=self.settings['vol_filter_length']
            volumeperiod=self.settings['vol_ma_length']
            data= self.bollingerband(data,bbperiod,BBSTDEVE,mult)
            data= self.crossover(data)
            data=  self.trend(data,trendperiod)
            data= self.volumeconditon(data,volumeperiod,stdperiod)

            
            return data
        except Exception as e :
            logger.error(e,exc_info=True)

    
    def finalconditons(self,data):
        data = self.conditons(data)
        for i in range(len(data)):
            if data['buyconditions'].iloc[i] and data['buyconditonTrend'].iloc[i] and data['buy_sell_condition_vol'].iloc[i]:
                data.loc[i,'buy_final']= True 
            elif  data['sellconditions'].iloc[i] and data['sellconditonTrend'].iloc[i] and data['buy_sell_condition_vol'].iloc[i]:
                data.loc[i,'sell_final']= True

        return data

         
    def ordersing(self,price,sl,target,trail,qty,side,amount):
        orderparam=dict()
        orderparam['symboltoken']=26000
        orderparam['exchange']='NSE'
        orderparam['transactiontype']='BUY'
        orderparam['product_type']='MIS'
        orderparam['quantity']=1
        orderparam['order_type']='MKT'
        orderparam['price']= price
        orderparam['sl']=sl
        orderparam['target']=target
        orderparam['trail']=trail
        orderparam['Amount']=amount
        orderparam['quantity']=qty
        orderparam['ltp']=price
        orderparam['tradingsymbol']='NIFTY50'
        orderparam['Side']=side
        orderparam['Slhit']=False
        orderparam['TargetHit']=False
        orderparam['Tslhit']=False

        return orderparam

    
    def main(self,data,backtest):
        try:

            data= self.finalconditons(data)
            sl=self.settings['sl_pct']
            trail=self.settings['trail_offset_pct']
            target=self.settings['tp_pct']
            stoptrail=self.settings['trail_stop_pct']
            price=data['close'].iloc[-1]
            qty=75
            if not backtest:

                nowtime= datetime.now(tz=pytz.timezone('Asia/Kolkata')).minute>data['updated_at'].iloc[-1].minute

            else:
                nowtime= datetime.now(tz=pytz.timezone('Asia/Kolkata')).minute>data['updated_at'].iloc[-1].minute



            
            if data['buy_final'].iloc[-1] and not data['buy_final'].iloc[-2]   :
                orderparam=self.ordersing(price,sl,target,trail,qty,'BUY',0)
                orderparam['updated_atdiff']=data['updated_at'].iloc[-1].minute-data['updated_at'].iloc[-2].minute
                self.utilityobj.processorder(orderparam,backtest=backtest)
            elif data['sell_final'].iloc[-1] and not data['buy_final'].iloc[-2]  :
                orderparam=self.ordersing(price,sl,target,trail,qty,'SELL',0)
                orderparam['updated_atdiff']=data['updated_at'].iloc[-1].minute-data['updated_at'].iloc[-2].minute

                self.utilityobj.processorder(orderparam,backtest=backtest)

            data.to_csv('Finaltestdata.csv')
            
            return True
        except Exception as e :
            logger.error(e,exc_info=True)
            print(e)
            return False




# if __name__== "__main__":
#     obj = strategy()
#     # obj.main()
#     logger.debug("%s")
