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

logpath= os.path.join(path,'Botlogs/strategy1.logs')
logpath= os.path.normpath(logpath)
logger=env.setup_logger(logpath)


class strategy:
    def __init__(self):
        self.utilityobj= utility.misc()
        self.settings= self.utilityobj.loadsettings()
   

    def wilder_rma(self,series, length):
     return series.ewm(alpha=1/length, adjust=False).mean()

    
    def rsi_sma_source_sma(self, data, source_sma=14, rsi_period=14, rsi_sma=7):

        # 1️⃣ Smooth the price first (RSI Source = SMA)
        # data['price_sma'] = data['close'].rolling(source_sma).mean()

        # 2️⃣ RSI on the SMA price

        delta = data['close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = self.wilder_rma(gain, rsi_period)
        avg_loss = self.wilder_rma(loss, rsi_period)

        rs = avg_gain / avg_loss
        data['rsi'] = 100 - (100 / (1 + rs))

        data['rsi'] = 100 - (100 / (1 + rs))

        # 3️⃣ RSI smoothing (SMA)
        data['rsi_sma'] = data['rsi'].rolling(rsi_period).mean()

        return data


        
    # def crossover(self,data):
    #     try:
        
    #         for i in range(len(data)):
    #             if data['rsi'].iloc[i]>data['rsi_sma'].iloc[i]:
    #                 data.loc[i,'buyconditions']=True

    #             elif data['rsi'].iloc[i]<data['rsi_sma'].iloc[i]:
    #                 data.loc[i,'sellconditions']=True


    #         return data
    #     except Exception as e:
    #         logger.error(e,exc_info=True)
            
    def crossover(self, data):
        try:
            data['buyconditions'] = False
            data['sellconditions'] = False

            data['prev_rsi'] = data['rsi'].shift(1)
            data['prev_rsi_sma'] = data['rsi_sma'].shift(1)

            # BUY crossover
            data.loc[
                (data['prev_rsi'] <= data['prev_rsi_sma']) &
                (data['rsi'] > data['rsi_sma']),
                'buyconditions'
            ] = True
            # data prevsignal false if buycondtions is false 



            

            # SELL crossover
            data.loc[
                (data['prev_rsi'] >= data['prev_rsi_sma']) &
                (data['rsi'] < data['rsi_sma']),
                'sellconditions'
            ] = True

            return data

        except Exception as e:
            logger.error(e, exc_info=True)
            return data


    

    def trend(self,data,period):
        data= self.ema(data,period)

        data['buyconditonTrend']= data['close']>data['ema']
        data['sellconditonTrend']= data['close']<data['ema']
        return data



    def sma(self,data,period):
        data['sma']=pd.Series(data['close']).rolling(period).mean()
        return data
    


    

    def conditons(self,data):
        try:
            ema_len=self.settings['ema_len']
            rsi_len= self.settings['rsi_len']
            data = self.rsi_sma_source_sma(data,ema_len,rsi_len,ema_len)
            data= self.crossover(data)
            return data
        except Exception as e :
            logger.error(e,exc_info=True)


    
    def finalconditons(self,data):
        data = self.conditons(data)
        data['buy_final'] = data['buyconditions']
        data['sell_final'] = data['sellconditions']
        

        
        # for i in range(len(data)):
        #     if data['buyconditions'].iloc[i] :
        #         data.loc[i,'buy_final']= True 
        #     elif  data['sellconditions'].iloc[i] :
        #         data.loc[i,'sell_final']= True
        return data

    

    def ordersing(self,price,sl,target,qty,side,amount,symbol,symboltoken):
        orderparam=dict()
        orderparam['symboltoken']=symboltoken
        orderparam['exchange']="NFO"
        orderparam['transactiontype']=side
        orderparam['product_type']='CARRYFORWARD'
        orderparam['order_type']='MARKET'
        orderparam['price']= price
        orderparam['sl']=sl
        orderparam['target']=target
        orderparam['Amount']=amount
        orderparam['quantity']=qty
        orderparam['ltp']=price
        orderparam['tradingsymbol']=symbol
        orderparam['Side']=side
        orderparam['Slhit']=False
        orderparam['Slhit1']=False
        orderparam['Slhit2']=False

        orderparam['TargetHit']=False
        orderparam['TargetHit1']=False
        orderparam['TargetHit2']=False
        orderparam['TargetHit3']=False
        orderparam['TargetHit4']=False
        orderparam['TargetHit5']=False
        orderparam['Tslhit']=False
        orderparam['exitedqty']=0
        orderparam['exitqty']=0

        

        return orderparam
    
    def exitbackest(self):
        pass


    
    def main(self,data,backtest,lotsize,prevsignal,ANGEL=None):

        try:
            prevsignal= prevsignal
            print('strategy started............................................................')
            logger.info("loop is running for the strategy")

            data= self.finalconditons(data)
            sl=self.settings['sl_pct']
            target=self.settings['tp_pct']

            price=data['close'].iloc[-1] 
            lot= int(self.settings['amount']/price/lotsize)*lotsize
            qty= max(lotsize,lot)
            logger.info(f"prevsignal: {prevsignal}")
            
            if ( data['buy_final'].iloc[-1]) and  (not prevsignal ): 
                logger.info(f"prevsignal in main statement: {prevsignal}")
            

                
                orderparam=self.ordersing(price,sl,target,qty,'BUY',0,data['symbol'].iloc[-1],data['token'].iloc[-1])
                data['updated_at']= pd.to_datetime(data['updated_at'],unit='ms')
                orderparam['updated_atdiff']=data['updated_at'].iloc[-1].minute-data['updated_at'].iloc[-2].minute
                print('buy order placed reason' , orderparam['updated_atdiff'])
                self.utilityobj.processorder(orderparam,backtest=backtest,ANGEL=ANGEL)

                logger.info('buy order placed reason' + str(data[['updated_at','buy_final','buyconditions']].iloc[-2:]))
                prevsignal= True
                data['prevsignal']= True

            elif ( not data['buy_final'].iloc[-1]):
                logger.info(f"prevsignal in else statement : {prevsignal}")

                prevsignal= False
                data['prevsignal']= False

            # elif data['sell_final'].iloc[-1] and (not data['sell_final'].iloc[-2]):
            #     logger.info('sell order placed reason' + str(data[['updated_at','sell_final','sellconditions']].iloc[-2:]))
            #     orderparam=self.ordersing(price,sl,target,qty,'SELL',0,data['symbol'].iloc[-1],data['token'].iloc[-1])
            #     orderparam['updated_atdiff']=data['updated_at'].iloc[-1].minute-data['updated_at'].iloc[-2].minute
            #     self.utilityobj.closeorder(forceclose=True,ANGEL=ANGEL)

            data.to_csv(f'data/{data["symbol"].iloc[-1]}.csv')
            
            return prevsignal
        except Exception as e :
            logger.error(e,exc_info=True)
    
            return prevsignal

