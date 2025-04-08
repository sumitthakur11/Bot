from BotKapil.Broker import upstoxsdk as upstox
from BotKapil.Broker import Angelsdk as Angel

import os
import logging
import json
import pandas as pd 
import time as ts 
import pytz
from BotKapil import env
import datetime


# path= os.getcwd()
path = env.currenenv
path= env.currenenv
path= os.path.join(path,'BotKapil')
path= str(path)
logpath= os.path.join(path,'botlogs/utility.logs')
logpath= os.path.normpath(logpath)
# logpath= os.path.join(logpath,'Angelbroker.logs')
print(logpath,'logpath')



logger=env.setup_logger(logpath)
class misc:
    def __init__(self):

        self.orderdata = pd.DataFrame(columns=['AccountNo','Entrytime','Broker','Side','Buyorderid','Symbol','Token','Status','Ltp','Qty','AveragePrice','Sellorderid','Sellprice','TargetHit','Slhit','Tslhit','Exittime','Target','Trail','Sl','Backtest','Transactiontype','Order_type'],dtype='object')
        self.account = pd.DataFrame(columns=['AccountNo','Apikey','Secret','Password','Token'],dtype='object')
        
        self.orderobject()
        self.fetchaccounts()

        
        

    
    def getsymbols(self):
        
        try:
            with open(path+f"config/symbols.json", 'rb') as f:
                loaded_dict = json.load(f)
            return loaded_dict
        except Exception as e :
                        logger.error(e,exc_info=True)

    
    def  loadsettings(self):
        try:

            filepath= os.path.join(path,'config/config.json')
            filepath= os.path.normpath(filepath)

            with open(filepath,'rb') as file:

                settings= json.load(file)
            logger.info('Sucessfully loaded settings')
            return settings['strategy']
            
        except Exception as e:
            logger.error(e,exc_info=True)

    
    def getdata(self,symbol):
        try:

            df= pd.read_json(path+f"data/feeddata/{symbol}.json")
            df= df[-2000:]
            
            return df 
        except Exception as e :
            logger.error(e,exc_info=True)


    def orderobject(self,accountno='',newdata:pd.DataFrame=pd.DataFrame()):
        try:
            file=None
            orderpath= "data/liveorderdata/orderdata.csv"
            orderpath= os.path.join(path,orderpath)
            if not os.path.exists(orderpath):
                self.orderdata.to_csv(orderpath)
            if not newdata.empty:
                 
                 newdata.to_csv(orderpath)
                
                 print('HERE')
            else:
                file = pd.read_csv(orderpath)

            return file
            
        except Exception as e:
            logger.error(f"check the orderobject function {e}")
    def uniqueno(self):
        import uuid
        return uuid.uuid1()

    def closeorder(self):
        try :

             
            orderobj=self.orderobject()
            orderobj=pd.DataFrame(orderobj,dtype='object')
            orderobj= orderobj[orderobj['Status']==True]
            for i in range(len(orderobj)):
                    print(orderobj.iloc[i])
                    
                    if (orderobj['Slhit'].iloc[i] or     orderobj['TargetHit'].iloc[i] or orderobj['Tslhit'].iloc[i]) and not orderobj['Backtest'].iloc[i]  :
                        accountdetail = self.fetchaccounts(key=orderobj['AccountNo'])

                        if not accountdetail.empty:
                            apikey= accountdetail['Apikey'].iloc[-1]
                            username= accountdetail['AccountNo'].iloc[-1]
                            pws= accountdetail['Password'].iloc[-1]
                            token= accountdetail['Token'].iloc[-1]
                            brokeri = Angel.HTTP(1,apikey,username,pws,token) 
                            orderparam= dict()
                            
                            orderparam['Token']=26009
                            orderparam['exchange']='NSE'
                            orderparam['Transactiontype']='BUY'
                            orderparam['product_type']='MIS'
                            orderparam['ordertype']='MIS'
                            orderparam['price']=orderobj['Ltp'].iloc[i]
                            orderparam['quantity']=orderobj['Qty'].iloc[i]
                            orderparam['Symbol']=orderobj['Symbol'].iloc[i]

                            orderid=brokeri.closetrade(orderparam,orderobj['Backtest'].iloc[i])
                            if orderid:
                                orderobj.loc[i,'Status']=False
                                orderobj.loc[i,'Exittime']=datetime.datetime.now()
                                orderobj.loc[i,'Sellorderid']=orderid
                    
                    elif (orderobj['Slhit'].iloc[i] or orderobj['TargetHit'].iloc[i] or orderobj['Tslhit'].iloc[i]) and  orderobj['Backtest'].iloc[i]  :
                            logger.info('Check order close')
                            orderobj.loc[i,'Status']=False
                            orderobj.loc[i,'Exittime']=datetime.datetime.now()
                            orderobj.loc[i,'Sellorderid']=self.uniqueno()


                            
                                
            self.orderobject(newdata=orderobj)
        except Exception as e:
             logger.error(e,exc_info=True)
                     
    
    
    def processorder (self,orderparams,atmcal=60,subclients=0,STOPLOSS=False,PAPER=True,makesymbol=True,advicecheck='',backtest=True):
        try:

            orderid=  []
            placeorders=False
            if backtest :
                broker= Angel.HTTP(1)
                print('yes')
                order_ids=broker.placeorder(orderparams,self.orderobject,True)
                
                

                
            else :
                brokerlist= self.fetchaccounts()
                for i in range(len(brokerlist)):
                    apikey= brokerlist['apikey'].iloc[i]
                    username= brokerlist['apikey'].iloc[i]
                    pws= brokerlist['apikey'].iloc[i]
                    token= brokerlist['apikey'].iloc[i]

                    broker= Angel.HTTP(1,apikey,username,pws,token)
                    placeorders= True # left to  add more conditons 
                    if placeorders:
                        order_ids=broker.placeorder(orderparams,self.orderobject,False)
                        
                        orderid.append(order_ids)
                        placeorders=False

                return orderid
        except Exception as e:
            logger.error(e,exc_info=True)
            return str(e)

        

    def fetchaccounts(self,key=''):
        try:
            logpath= f"config/account.csv"
            logpath= os.path.join(path,logpath)

            if not os.path.exists(logpath):
                 self.account.to_csv(logpath)


            df= pd.read_csv(logpath)
            if key:
                 df=df[df['AccountNo']==key]
            return df 
        except Exception as e :
            logger.error(e,exc_info=True)



    def fetchorders(self):
        try:
            logpath= path+"data/liveorderdata/orderdata.csv"
            if not os.path.exists(logpath):
                os.makedirs(logpath)


            df= pd.read_csv(path+f"config/account.csv")
            return df 
        except Exception as e :
            logger.error(e,exc_info=True)
            
    def mergebacktest(self):
        datapath= "data/ZohoWorkDrive/10-2024/10-2024/NIFTY_I.csv"
        datapath= os.path.join(path,datapath)
        df1= pd.read_csv(datapath)
        datapath= "data/ZohoWorkDrive/11-2024/11-2024/NIFTY_I.csv"
        datapath= os.path.join(path,datapath)
        df2= pd.read_csv(datapath)

        datapath= "data/ZohoWorkDrive/01-2025/01-2025/NIFTY_I.csv"
        datapath= os.path.join(path,datapath)
        df3= pd.read_csv(datapath)
        
        dffinal = pd.concat([df1, df2, df3], ignore_index=True)
        dffinal['updated_at']= pd.to_datetime(dffinal['Date'],format='%Y%m%d')
        dffinal['updated_at']=dffinal['updated_at']+pd.to_timedelta(dffinal['Time'])
        dffinal['updated_at'] = dffinal['updated_at'].dt.tz_localize('Asia/Kolkata')
            
        return dffinal
    def checkpnlbox(self,account):
        settings= self.loadsettings()
        orderobj=self.orderobject()
        orderobj= orderobj[orderobj['Status']==True]


        if not orderobj.empty:
            for i in range(len(orderobj)):
                ltp= self.checkltp(orderobj['Exchange'].iloc[i],
                                   orderobj['Token'].iloc[i])
                orderobj['Exchange'].iloc[i]= ltp


                if orderobj['AccountNo'].iloc[i]==account:
                    if (ltp<orderobj['AveragePrice'].iloc[i]*(1-settings['sl_pct'])) and (orderobj['Side'].iloc[i]=='LONG'):
                         orderobj.loc[i,'Slhit']=True


                    
                    elif (ltp>orderobj['AveragePrice'].iloc[i]*(1+settings['sl_pct'])) and (orderobj['Side'].iloc[i]=='SHORT'):
                         orderobj.loc[i,'Slhit']=True
                    
                    if (ltp>orderobj['AveragePrice'].iloc[i]*(1+settings['tp_pct'])) and (orderobj['Side'].iloc[i]=='LONG'):
                         orderobj.loc[i,'TargetHit']=True
                    
                    elif (ltp<orderobj['AveragePrice'].iloc[i]*(1-settings['tp_pct'])) and (orderobj['Side'].iloc[i]=='SHORT'):
                         orderobj.loc[i,'TargetHit']=True

                    
                    if (ltp<orderobj['AveragePrice'].iloc[i]*(1-settings['trail_stop_pct'])) and (orderobj['Side'].iloc[i]=='LONG'):
                         orderobj.loc[i,'Slhit']=True

                    
                    elif (ltp>orderobj['AveragePrice'].iloc[i]*(1+settings['trail_stop_pct'])) and (orderobj['Side'].iloc[i]=='SHORT'):
                         orderobj.loc[i,'Slhit']=True

                
                    if (ltp<orderobj['AveragePrice'].iloc[i]*(1+settings['trail_offset_pct'])) and (orderobj['Side'].iloc[i]=='LONG'):
                         orderobj.loc[i,'Tslhit']=True

                    
                    elif (ltp>orderobj['AveragePrice'].iloc[i]*(1-settings['trail_offset_pct'])) and (orderobj['Side'].iloc[i]=='SHORT'):
                         orderobj.loc[i,'Tslhit']=True
                         

        self.orderobject(newdata=orderobj)



    
    
                             
                   
              



    def exitconditon(self):
        while True:
            self.checkpnlbox()
    

         
         
         
    
    def checkltp(self,exh,token):
         

        broker = Angel.HTTP(1)
        tokenparam= {exh:[]}
        tokenparam[exh].append(token)

        ltp= broker.get_quotes(tokenparam)
        ltp= float(ltp['data']['fetched'][0]['ltp'])
        print(ltp,'ltpange;')
            

       
        return ltp

         



         
         

    def gettestdata(self,symbol):
        try:
            datapath= "data/ZohoWorkDrive/01-2025/01-2025/NIFTY_I.csv"
            datapath= os.path.join(path,datapath)

            # if not os.path.exists(datapath):
            #     os.makedirs(datapath)
            

            df= pd.read_csv(datapath)
            df['updated_at']= pd.to_datetime(df['Date'],format='%Y%m%d')
            df['updated_at']=df['updated_at']+pd.to_timedelta(df['Time'])
            df['updated_at'] = df['updated_at'].dt.tz_localize('Asia/Kolkata')
            


            # df=df[df["instrumentname"]==symbol.upper()]
            return df 
        except Exception as e :
            logger.error(e,exc_info=True)

        

    def buildcandels(self,data,timeframe_seconds=None):
        try:    
                
                
                # data['updated_at'] = pd.to_datetime(str(data['Date'])+str(data['Time']))
                # data['updated_at'] = data['updated_at'].dt.tz_localize('Asia/Kolkata')
                df = data.set_index('updated_at')
                open_price = df['Close'].resample(timeframe_seconds).first()
                high_price = df['Close'].resample(timeframe_seconds).max()
                low_price = df['Close'].resample(timeframe_seconds).min()
                close_price = df['Close'].resample(timeframe_seconds).last()
                volume= df['Close'].resample(timeframe_seconds).last()
                OI= df['OI'].resample(timeframe_seconds).last()

                self.ohlc = pd.DataFrame({
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'close': close_price,
                    'volume':volume,
                    'OI':OI
                    
                })
                self.ohlc=self.ohlc.dropna()
                self.ohlc = self.ohlc.reset_index()
                return self.ohlc
        except Exception as e:
                            logger.error(e,exc_info=True)

    
