from Bot import env
from Bot.Broker import upstoxsdk as upstox
from Bot.Broker import Angelsdk as Angel

import os
import logging
import json
import pandas as pd 
import time as ts 
import pytz
import datetime
import numpy as np

# path= os.getcwd()
path = env.currenenv
logpath= os.path.join(path,'botlogs/utility.logs')
logpath= os.path.normpath(logpath)
# logpath= os.path.join(logpath,'Angelbroker.logs')
print(logpath,'logpath')



logger=env.setup_logger(logpath)
class misc:
    def __init__(self):
        orderdata= [['',datetime.datetime.now(),'','','','','',False,0.0,0,0.0,'',0.0,False,False,False,datetime.datetime.now(),0.0,0.0,0.0,False,'','','',0.0]]

        self.orderdata = pd.DataFrame(orderdata,columns=['AccountNo','Entrytime','Broker','Side','Buyorderid','Symbol','Token','Status','Ltp','Qty','AveragePrice','Sellorderid','Sellprice','TargetHit','Slhit','Tslhit','Exittime','Target','Trail','Sl','Backtest','Transactiontype','Order_type','Exchange','Pnl'],dtype='object')
        self.account = pd.DataFrame(columns=['AccountNo','Apikey','Secret','Password','Token'],dtype='object')
       
        


        data=self.orderobject()
        self.fetchaccounts()

        
        

    
    def getsymbols(self):
        
        try:
            symbolpath= os.path.join(path,"config/symbol.json")
            symbolpath= os.path.normpath(symbolpath)

            with open(symbolpath) as f:
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

    
    def getdata(self,symbol,test):
        try:
            if not test:
                 filepath= os.path.join(path,f"data/feeddata/{symbol}.csv")
            else:
                 filepath= os.path.join(path,f"data/testdata/{symbol}.csv")
                 
                 

            filepath= os.path.normpath(filepath)


            df= pd.read_csv(filepath)
            df.reset_index(drop=True,inplace=True)

            
            
            return df 
        except Exception as e :
            logger.error(e,exc_info=True)


    def orderobject(self,newdata='',newdataflag=False):
        try:
            file=None
            print(newdata,newdataflag,'new data')

            orderpath= "data/liveorderdata/orderdata.json"
            orderpath= os.path.join(path,orderpath)
            if not os.path.exists(orderpath):

                self.orderdata.to_json(orderpath)
                'here'
            if newdataflag:
                 
                 if 'level_0' in newdata.columns:
                      newdata = newdata.drop(columns=['level_0'])
                 newdata=newdata.reset_index()
                 print('HERE')
                 print(newdata,'??????????????????????????????')
                 newdata.to_json(orderpath,default_handler=str)
                
            else:
                file = pd.read_json(orderpath)

            return file
            
        except Exception as e:
            logger.error(f"check the orderobject function {e}",exc_info=True)
    def uniqueno(self):
        return int(ts.time()*1000)

    def closeorder(self):
        try :

             
            orderobj=self.orderobject()
            orderobj=pd.DataFrame(orderobj,dtype='object')
            orderobjTrue=orderobj[orderobj['Status']==True]

            # orderobj= orderobj[orderobj['Status']==True]
            if not orderobj.empty:
                for i in range(len(orderobjTrue)):
                        print(orderobjTrue.iloc[i])
                        if orderobjTrue['Status'].iloc[i]:
                            ind= orderobjTrue.index[i]

                             
                            if (orderobjTrue['Slhit'].iloc[i] or orderobjTrue['TargetHit'].iloc[i] or orderobjTrue['Tslhit'].iloc[i]) and not orderobjTrue['Backtest'].iloc[i]  :
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
                                        orderobj.loc[ind,'Status']=False
                                        orderobj.loc[ind,'Exittime']=datetime.datetime.now()
                                        orderobj.loc[ind,'Sellorderid']=orderid
                                        orderobj.loc[ind,'Sellprice']=orderobjTrue['Ltp'].iloc[i]
                                        orderobj.loc[ind,'Pnl']=float(orderobjTrue['AveragePrice'].iloc[i]-orderobjTrue['Ltp'].iloc[i])*orderobjTrue['Qty'].iloc[i]
                                        self.orderobject(newdata=orderobj,newdataflag=True)

                                        
                            
                            elif (orderobjTrue['Slhit'].iloc[i] or orderobjTrue['TargetHit'].iloc[i] or orderobjTrue['Tslhit'].iloc[i]) and  orderobjTrue['Backtest'].iloc[i]  :
                                    logger.info('Check order close')
                                    print('buffer',orderobjTrue['Slhit'].iloc[i],orderobjTrue['TargetHit'].iloc[i],orderobjTrue['Tslhit'].iloc[i])
                                    orderobj.loc[ind,'Status']=False
                                    orderobj.loc[ind,'Exittime']=datetime.datetime.now()
                                    orderobj.loc[ind,'Sellorderid']=self.uniqueno()
                                    orderobj.loc[ind,'Sellprice']=orderobjTrue['Ltp'].iloc[i]
                                    orderobj.loc[ind,'Pnl']=float(orderobjTrue['Ltp'].iloc[i]-orderobjTrue['AveragePrice'].iloc[i])*orderobjTrue['Qty'].iloc[i]
                                    self.orderobject(newdata=orderobj,newdataflag=True)




                            
                                
        except Exception as e:
             logger.error(e,exc_info=True)
                     
    
    
    def processorder (self,orderparams,atmcal=60,subclients=0,STOPLOSS=False,PAPER=True,makesymbol=True,advicecheck='',backtest=True):
        try:

            orderid=  []
            placeorders=False
            
            orderobj=self.orderobject()
            print(datetime.timedelta(minutes=orderparams['updated_atdiff']))
            print(orderobj['Entrytime'].iloc[-1]/1000)
            print(datetime.datetime.fromtimestamp(orderobj['Entrytime'].iloc[-1]/1000))
            
            print(datetime.datetime.fromtimestamp(orderobj['Entrytime'].iloc[-1]/1000)+ datetime.timedelta(minutes=orderparams['updated_atdiff']))
            if datetime.datetime.now()> datetime.datetime.fromtimestamp(orderobj['Entrytime'].iloc[-1]/1000)+datetime.timedelta(minutes=orderparams['updated_atdiff']):
                
                
                orderobj=orderobj[orderobj['Backtest']==True]
                 
                if backtest  and not  orderobj['Status'].any() :

                    broker= Angel.HTTP(1)
                    print('yes')
                    order_ids=broker.placeorder(orderparams,self.orderobject,True)


                
                else :
                    brokerlist= self.fetchaccounts()


                    for i in range(len(brokerlist)):
                        orderobj=orderobj[orderobj['Accountno']==brokerlist['AccountNo'].iloc[i]]
                        if not orderobj['Status'].any():
                            apikey= brokerlist['Apikey'].iloc[i]
                            username= brokerlist['AccountNo'].iloc[i]
                            pws= brokerlist['Password'].iloc[i]
                            token= brokerlist['Token'].iloc[i]

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
        datapath= "Bot/data/ZohoWorkDrive/10-2024/10-2024/NIFTY_I.csv"
        datapath= os.path.join(path,datapath)
        datapath= os.path.normpath(datapath)

        df1= pd.read_csv(datapath)
        datapath= "Bot/data/ZohoWorkDrive/11-2024/11-2024/NIFTY_I.csv"
        datapath= os.path.join(path,datapath)
        datapath= os.path.normpath(datapath)

        df2= pd.read_csv(datapath)

        datapath= "Bot/data/ZohoWorkDrive/01-2025/01-2025/NIFTY_I.csv"
        datapath= os.path.join(path,datapath)
        datapath= os.path.normpath(datapath)

        df3= pd.read_csv(datapath)
        
        dffinal = pd.concat([df1, df2, df3], ignore_index=True)
        dffinal['updated_at']= pd.to_datetime(dffinal['Date'],format='%Y%m%d')
        dffinal['updated_at']=dffinal['updated_at']+pd.to_timedelta(dffinal['Time'])
        dffinal['updated_at'] = dffinal['updated_at'].dt.tz_localize('Asia/Kolkata')
        csvpath = os.path.join(path,'data/testdata/NIFTY50.csv')
        csvpath=os.path.normpath(csvpath)
        dffinal.to_csv(csvpath)

        return dffinal 
    def checkpnlbox(self,LTP):
        try:
             
            settings= self.loadsettings()
            orderobj=self.orderobject()
            orderobjTrue=orderobj[orderobj['Status']==True]

            orderobj['Slhit']= orderobj['Slhit'].astype('object')      
            orderobj['TargetHit']= orderobj['TargetHit'].astype('object')      
            orderobj['Tslhit']= orderobj['Tslhit'].astype('object')      
            if not orderobj.empty:
                for i in range(len(orderobjTrue)):

                    if orderobjTrue['Status'].iloc[i]:
                        ltp= self.checkltp(orderobjTrue['Exchange'].iloc[i],
                                        orderobjTrue['Token'].iloc[i],orderobjTrue['Backtest'].iloc[i],LTP)
                        ltp= float(ltp)
                        ind= orderobjTrue.index[i]
                        print(ind)

                        orderobj.loc[ind,'Ltp']= ltp
                        print(i,orderobj.loc[i,'Ltp'])
                        print('check pnl$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$',ltp)
                        
                        if (ltp<orderobjTrue['AveragePrice'].iloc[i]*(1-settings['sl_pct'])) and (orderobjTrue['Side'].iloc[i]=='LONG'):
                                orderobj.loc[ind,'Slhit']=True


                        
                        elif (ltp>orderobjTrue['AveragePrice'].iloc[i]*(1+settings['sl_pct'])) and (orderobjTrue['Side'].iloc[i]=='SHORT'):
                                orderobj.loc[ind,'Slhit']=True

                
                        
                        if (ltp>orderobjTrue['AveragePrice'].iloc[i]*(1+settings['tp_pct'])) and (orderobjTrue['Side'].iloc[i]=='LONG'):
                                orderobj.loc[ind,'TargetHit']=True
                        
                        elif (ltp<orderobjTrue['AveragePrice'].iloc[i]*(1-settings['tp_pct'])) and (orderobjTrue['Side'].iloc[i]=='SHORT'):
                                orderobj.loc[ind,'TargetHit']=True

                        
                        if (ltp<orderobjTrue['AveragePrice'].iloc[i]*(1-settings['trail_stop_pct'])) and (orderobjTrue['Side'].iloc[i]=='LONG'):
                                orderobj.loc[ind,'Slhit']=True

                        
                        elif (ltp>orderobjTrue['AveragePrice'].iloc[i]*(1+settings['trail_stop_pct'])) and (orderobjTrue['Side'].iloc[i]=='SHORT'):
                                orderobj.loc[ind,'Slhit']=True

                    
                        if (ltp<orderobjTrue['AveragePrice'].iloc[i]*(1+settings['trail_offset_pct'])) and (orderobjTrue['Side'].iloc[i]=='LONG'):
                                orderobj.loc[ind,'Tslhit']=True
                                print(orderobj,'$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                                print(orderobj['AveragePrice'].iloc[i]*(1+settings['trail_offset_pct']))
                        elif (ltp>orderobjTrue['AveragePrice'].iloc[i]*(1-settings['trail_offset_pct'])) and (orderobjTrue['Side'].iloc[i]=='SHORT'):
                                orderobj.loc[ind,'Tslhit']=True
                        self.orderobject(newdata=orderobj,newdataflag=True)
                    else:
                         pass
        except Exception as e :
             logger.error(e,exc_info=True)



    
    
                             
                   
              



    def exitconditon(self):
        while True:
            self.checkpnlbox()
    

         
         
         
    
    def checkltp(self,exh,token,bakctest,LTP):
        try:
             
         

            broker = Angel.HTTP(1)
            tokenparam= {exh:[]}
            tokenparam[exh].append((str(token)))
            if not bakctest:
                ltp= broker.get_quotes(tokenparam)
                ltp= float(ltp['data']['fetched'][0]['ltp'])
            else:
                 ltp=LTP
                 
            print(ltp,'ltpange;')
            return ltp

        except Exception as e:
             logger.error(e,exc_info=True)
                

       

         



         
         

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

        

    def buildcandels(self,data,timeframe_seconds=None,backtest=False):
        try:    
                
                data['updated_at']= pd.to_datetime(data['updated_at'])

                if not backtest:
                     
                    df = data.set_index('updated_at')
                else :
                    pass
                df = data.set_index('updated_at')
                     
                # print(df)
                # df.groupby('date')['Close'].resample(timeframe_seconds).first()
                open_price = df['Close'].resample(timeframe_seconds).first()
                high_price = df['Close'].resample(timeframe_seconds).max()
                low_price = df['Close'].resample(timeframe_seconds).min()
                close_price = df['Close'].resample(timeframe_seconds).last()
                volume= df['Volume'].resample(timeframe_seconds).last()
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

    
