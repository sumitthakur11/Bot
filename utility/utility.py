from Bot import env
from Bot.Broker import Angelsdk as Angel

import os
import logging
import json
import pandas as pd 
import time as ts 
import pytz
import datetime
import numpy as np
import time
# path= os.getcwd()
import random
from datetime import  timedelta

path = env.currenenv
logpath= os.path.join(path,'Botlogs/utility.logs')
logpath= os.path.normpath(logpath)
# logpath= os.path.join(logpath,'Angelbroker.logs')
print(logpath,'logpath')



logger=env.setup_logger(logpath)
class misc:
    def __init__(self):
        orderdata= [['',datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S"),'','','','','',False,0.0,0,0.0,'',0.0,False,False,False,datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S"),0.0,0.0,0.0,False,'','','',0.0,0.0,0.0,0,False]]

        self.orderdata = pd.DataFrame(orderdata,columns=['AccountNo','Entrytime','Broker','Side','Buyorderid','Symbol','Token','Status','Ltp','Qty','AveragePrice','Sellorderid','Sellprice','TargetHit','Slhit','Tslhit','Exittime','Target','Trail','Sl','Backtest','Transactiontype','Order_type','Exchange','Pnl','Netpnl','Commision','retry','forclosed'],dtype='object')
        self.account = pd.DataFrame(columns=['AccountNo','Apikey','Secret','Password','Token','Lot','Broker'],dtype='object')
        data=self.orderobjectread()
        self.fetchaccounts()
        print('initialised sucessfully')

    def restartdata(self):
        data=self.orderobjectread()
        data['retry']=0.0
        data['Status']= False
        data['forclosed']= False
        data=self.orderobjectwrite(newdata=data,newdataflag=True)



         
    def  loadsettings(self):
        try:
            

            filepath= os.path.join(path,'config/config.json')
            filepath= os.path.normpath(filepath)

            with open(filepath,'rb') as file:

                settings= json.load(file)
            return settings['strategy']
            
        except Exception as e:
            logger.error(e,exc_info=True)

    
    def loadtokenlist(self): 
        try:
            filepath= os.path.join(path,'config/tokenlist.json')
            filepath= os.path.normpath(filepath)
            tokenlist= pd.read_json(filepath)
            return tokenlist
        except Exception as e:
            logger.error(e,exc_info=True)

    def orderobjectwrite(self,newdata='',newdataflag=False):
        try:
            file=None
            orderpath= "data/liveorderdata/orderdatawrite.json"
            replicate= "data/liveorderdata/orderdataread.json"
            orderpath= os.path.join(path,orderpath)
            orderreplicate= os.path.join(path,replicate)
            if not os.path.exists(orderpath):

                self.orderdata.to_json(orderpath)
            if newdataflag:
                 
                 if 'level_0' in newdata.columns:
                      newdata = newdata.drop(columns=['level_0'])
                 newdata=newdata.reset_index()
                 newdata.to_json(orderpath,default_handler=str)
                 newdata.to_json(orderreplicate,default_handler=str)
                 newdata.to_csv(orderreplicate.replace('.json','.csv'),index=False)

            else:
                file = pd.read_json(orderpath)

            return file
            
        except Exception as e:
            logger.error(f"check the orderobject function {e}",exc_info=True)
             
         

    def orderobjectread(self):
        try:
            file=None
            orderpath= "data/liveorderdata/orderdataread.json"
            orderpath= os.path.join(path,orderpath)
            if not os.path.exists(orderpath):

                file=self.orderdata.to_json(orderpath)
            file = pd.read_json(orderpath)

            return file
            
        except Exception as e:
            logger.error(f"check the orderobject function {e}",exc_info=True)
    def uniqueno(self):
        return int(ts.time()*1000)

    def closeorder(self,forceclose=False,ANGEL=None):
        try :

             
            orderobj=self.orderobjectread()
            orderobj=pd.DataFrame(orderobj,dtype='object')
            orderobjTrue=orderobj[orderobj['Status']==True]

            if not orderobj.empty:
                for i in range(len(orderobjTrue)):
                        if orderobjTrue['Status'].iloc[i] and orderobjTrue['forclosed'].iloc[i]==False:
                            ind= orderobjTrue.index[i]

                             
                            if (orderobjTrue['Slhit'].iloc[i] or orderobjTrue['TargetHit'].iloc[i] or forceclose ) and (not orderobjTrue['Backtest'].iloc[i])  :
                                # accountdetail = self.fetchaccounts(key=orderobjTrue['AccountNo'].iloc[i])

                                # if not accountdetail.empty:
                                #     apikey= accountdetail['Apikey'].iloc[-1]
                                #     username= accountdetail['AccountNo'].iloc[-1]
                                #     pws= accountdetail['Password'].iloc[-1]
                                #     token= accountdetail['Token'].iloc[-1]
                                    # # loginbroker = Angel.SMARTAPI(2,apikey,username,pws,token)
                                    # # loginbroker.smartAPI_Login()

                                    # brokeri = Angel.HTTP(2,apikey,username,pws,token) 
                                    orderparam= dict()
                                    
                                    orderparam['Token']= orderobjTrue['Token'].iloc[i]
                                    orderparam['exchange']=orderobjTrue['Exchange'].iloc[i]
                                    orderparam['Transactiontype']='SELL' if orderobjTrue['Transactiontype'].iloc[i]=='BUY' else 'BUY'
                                    orderparam['product_type']='INTRADAY'
                                    orderparam['order_type']='MARKET'
                                    orderparam['price']=orderobjTrue['Ltp'].iloc[i]
                                    orderparam['quantity']=orderobjTrue['Qty'].iloc[i]
                                    orderparam['tradingsymbol']=orderobjTrue['Tradingsymbol'].iloc[i]


                                    orderid=ANGEL.closetrade(orderparam,orderobjTrue['Backtest'].iloc[i])
                                    if orderid:
                                        orderobj.loc[ind,'Status']=False
                                        orderobj.loc[ind,'Exittime']=datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")
                                        orderobj.loc[ind,'Sellorderid']=orderid
                                        orderobj.loc[ind,'Sellprice']=orderobjTrue['Ltp'].iloc[i]
                                        orderobj.loc[ind,'Pnl']=float(orderobjTrue['AveragePrice'].iloc[i]-orderobjTrue['Ltp'].iloc[i])*orderobjTrue['Qty'].iloc[i]
                                        orderobj.loc[i,'Netpnl']=float( orderobjTrue['Pnl'].iloc[i])-float( orderobjTrue['Commision'].iloc[i])
                                        orderobj.loc[ind,'forclosed']=True

                                        self.orderobjectwrite(newdata=orderobj,newdataflag=True)

                                        
                            
                            elif (orderobjTrue['Slhit'].iloc[i]  or orderobjTrue['TargetHit'].iloc[i] or forceclose ) and  (orderobjTrue['Backtest'].iloc[i] ) :
                                    logger.info('Check order close')
                                    # print('buffer',orderobjTrue['Slhit'].iloc[i],orderobjTrue['TargetHit'].iloc[i],orderobjTrue['Tslhit'].iloc[i])
                                    orderobj.loc[ind,'Status']=False
                                    orderobj.loc[ind,'Exittime']=datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")
                                    orderobj.loc[ind,'Sellorderid']=self.uniqueno()
                                    orderobj.loc[ind,'Sellprice']=orderobjTrue['Ltp'].iloc[i]
                                    orderobj.loc[ind,'Pnl']=float(orderobjTrue['Ltp'].iloc[i]-orderobjTrue['AveragePrice'].iloc[i])*orderobjTrue['Qty'].iloc[i]
                                    orderobj.loc[i,'Netpnl']=float( orderobjTrue['Pnl'].iloc[i])-float( orderobjTrue['Commision'].iloc[i])
                                    orderobj.loc[ind,'forclosed']=True

                                    self.orderobjectwrite(newdata=orderobj,newdataflag=True)




                            
                                
        except Exception as e:
             logger.error(e,exc_info=True)
                     
    
    
    def processorder (self,orderparams,atmcal=60,subclients=0,STOPLOSS=False,PAPER=True,makesymbol=True,advicecheck='',backtest=True,retry=2,ANGEL=None):
        try:

            orderid=  []
            placeorders=False
            
            orderobj=self.orderobjectread()
           
                
                
                 
            if backtest  and (not  orderobj['Status'].any() ):
                orderobj=orderobj[orderobj['Backtest']==True]


                # broker= Angel.HTTP(1)
                order_ids=ANGEL.placeorder(orderparams,self.orderobjectwrite,True)
                return order_ids




            elif (not backtest ) and (not  orderobj['Status'].any() or orderobj.empty ) and orderretry<retry:
                orderobj=orderobj[orderobj['Backtest']==False]
                orderretry=orderobj['retry'].iloc[-1]
                order_ids=ANGEL.placeorder(orderparams,self.orderobjectwrite,False)
                orderid.append(order_ids)

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



   
            
   
    
    def checkpnlbox1(self,data):
        settings= self.loadsettings()
        averageprice=0
        targetprbuy=0
        averagesellprice=0
        targetsell=0
        targetbuy=0
        tslbuyactive=0
        tslsellactive=0
        
        stoplossbuy=stoplossell=False
        data['high']= data['high'].astype('float')      
        data['exit']= data['exit'].astype('object')   
        data['entry']= data['entry'].astype('object') 
        data['side']= data['side'].astype('object')   
        data['sellprice']= data['sellprice'].astype('float')
        data['averageprice']= data['averageprice'].astype('float') 
        data['Pnl']= data['Pnl'].astype('float')
        data['Commision']= settings['commision']
        data['Commision']= data['Commision'].astype('float')
        data['drawdown']= 0
        data['drawdown']= data['drawdown'].astype('float')



        # data['Netpnl']= data['Netpnl'].astype('float')   

        
        for i in range(len(data)):

            maxhighprice = max(data['high'].iloc[i],data['high'].iloc[i-1])
            minlowprice = min(data['low'].iloc[i],data['low'].iloc[i-1])

            if  data['buy_final'].iloc[i]  and  (not averageprice) :
                averageprice=data['close'].iloc[i]
                data.loc[i,'averageprice']= float(averageprice)

                data.loc[i,'entry']=True
                data.loc[i,'side']='LONG'
                if averagesellprice:
                    data.loc[i,'exit']= True
                    data.loc[i,'sellprice']= data['low'].iloc[i]
                    data.loc[i,'Pnl']= averagesellprice-data['low'].iloc[i]
                    data.loc[i,'drawdown']= float( data['low'].iloc[i])-float(minlowprice)
                    targetsell= False
                    stoplossell= False
                    averagesellprice=0
                    tslsellactive=0


                targetsell= False
                stoplossell= False
                tslsellactive=0
                averagesellprice=0

                     

            elif  data['sell_final'].iloc[i] and (not averagesellprice ):
                averagesellprice=data['close'].iloc[i]
                data.loc[i,'averageprice']= averagesellprice
                data.loc[i,'side']='SHORT'
                data.loc[i,'entry']=True
                if averageprice:
                    data.loc[i,'exit']= True
                    data.loc[i,'sellprice']= data['high'].iloc[i]
                    data.loc[i,'Pnl']=float( data['high'].iloc[i])-averageprice
                    data.loc[i,'drawdown']= float(maxhighprice)-float( data['high'].iloc[i])
                    targetprbuy=False
                    stoplossbuy=False
                    averageprice=0
                    tslbuyactive=0
                    targetbuy=0

                     
            

            

            if averageprice:
                buyactive= data['high'].iloc[i]*(1+settings['trail_offset_pct'])
                tslbuyactive=data['high'].iloc[i]>buyactive
                prevtrailbuy = data['high'].iloc[i]*settings['trail_offset_pct']
                targetprbuy=averageprice*(1+settings['tp_pct'])
                targetbuy = data['high'].iloc[i]>targetprbuy
                stoplossbuy = data['low'].iloc[i]<averageprice*(1-settings['sl_pct'])



            if tslbuyactive:
                if (data['high'].iloc[i]<buyactive+prevtrailbuy) and tslbuyactive:
                     data.loc[i,'exit']= True
                     data.loc[i,'sellprice']= data['high'].iloc[i]

                     data.loc[i,'Pnl']=float( data['high'].iloc[i])-averageprice
                     data.loc[i,'drawdown']= float(maxhighprice)-float( data['high'].iloc[i])
                    #  data.loc[i,'Netpnl']=float( data['Pnl'].iloc[i])-float( data['Commision'].iloc[i])

                     targetprbuy=False
                     stoplossbuy=False
                     averageprice=0
                     tslbuyactive=0
                     targetbuy=0
            elif stoplossbuy:
                    data.loc[i,'exit']= True
                    data.loc[i,'sellprice']= data['low'].iloc[i]
                    data.loc[i,'Pnl']=float( data['low'].iloc[i])-averageprice
                    data.loc[i,'drawdown']= float(maxhighprice)-float( data['low'].iloc[i])

                    # data.loc[i,'Netpnl']=float( data['Pnl'].iloc[i])-float( data['Commision'].iloc[i])

                    targetprbuy=False
                    stoplossbuy=False
                    averageprice=0
                    tslbuyactive=0
                    targetbuy=0
                    
            elif targetbuy:
                    data.loc[i,'exit']= True
                    data.loc[i,'sellprice']= data['high'].iloc[i]
                    data.loc[i,'Pnl']=float( data['high'].iloc[i])-averageprice
                    data.loc[i,'drawdown']= float(maxhighprice)-float( data['high'].iloc[i])

                    # data.loc[i,'Netpnl']=float( data['Pnl'].iloc[i])-float( data['Commision'].iloc[i])

                    targetprbuy=False
                    stoplossbuy=False
                    averageprice=0
                    tslbuyactive=0
                    targetbuy=0

                 

                 


            if averagesellprice:
                sellactive= data['low'].iloc[i]*(1-settings['trail_offset_pct'])
                tslsellactive=data['low'].iloc[i]<sellactive

                 
                stoplossell = data['high'].iloc[i]>averagesellprice*(1+settings['sl_pct'])
                prevtrailsell = data['low'].iloc[i]*settings['trail_offset_pct']
                targetprsell=averagesellprice*(1-settings['tp_pct'])
                targetsell = data['low'].iloc[i]<targetprsell
            
            if tslsellactive:
                 
                if (data['low'].iloc[i]>sellactive-prevtrailsell ) and tslsellactive  :
                        data.loc[i,'exit']= True
                        data.loc[i,'sellprice']= data['low'].iloc[i]

                        data.loc[i,'Pnl']= averagesellprice-data['low'].iloc[i]
                        data.loc[i,'drawdown']= float( data['low'].iloc[i])-float(minlowprice)

                        # data.loc[i,'Netpnl']=float( data['Pnl'].iloc[i])-float( data['Commision'].iloc[i])

                        targetsell= False
                        stoplossell= False
                        averagesellprice=0
                        tslsellactive=0

            if stoplossell:
                    data.loc[i,'exit']= True
                    data.loc[i,'sellprice']= data['high'].iloc[i]

                    data.loc[i,'Pnl']= averagesellprice-data['high'].iloc[i]
                    # data.loc[i,'Netpnl']=float( data['Pnl'].iloc[i])-float( data['Commision'].iloc[i])
                    data.loc[i,'drawdown']= float( data['high'].iloc[i])-float(minlowprice)


                    targetsell= False
                    stoplossell= False
                    averagesellprice=0
                    tslsellactive=0

            if targetsell:
                data.loc[i,'exit']= True
                data.loc[i,'sellprice']= data['low'].iloc[i]
                data.loc[i,'Pnl']= averagesellprice-data['low'].iloc[i]
                # data.loc[i,'Netpnl']=float( data['Pnl'].iloc[i])-float( data['Commision'].iloc[i])
                data.loc[i,'drawdown']= float( data['low'].iloc[i])-float(minlowprice)

                

                targetsell= False
                stoplossell= False
                tslsellactive=0
                averagesellprice=0


                    
                 
                 
            
        return data
   
    def checkpnlbox(self,LTP='',ANGEL=None):
        try:
            logger.info("Checking SL/TP for open orders")
            settings= self.loadsettings()
            orderobj=self.orderobjectread()
            orderobjTrue=orderobj[orderobj['Status']==True]

            orderobj['Slhit']= orderobj['Slhit'].astype('object')      
            orderobj['TargetHit']= orderobj['TargetHit'].astype('object')      
            orderobj['Commision']= orderobj['Pnl'].astype('float')
            orderobj['Commision']= settings['commision']
            orderobj['Netpnl']= orderobj['Netpnl'].astype('float')   


            if not orderobjTrue.empty:
                for i in range(len(orderobjTrue)):

                    if orderobjTrue['Status'].iloc[i]:
                        # ltp= self.checkltp(orderobjTrue['Exchange'].iloc[i],orderobjTrue['Token'].iloc[i],orderobjTrue['Backtest'].iloc[i],LTP,ANGEL)
                        # generate random ltp for backtest
                        ltp =  random.uniform(orderobjTrue['AveragePrice'].iloc[i]*0.9, orderobjTrue['AveragePrice'].iloc[i]*1.1)
                        # ltp= float(ltp)
                        ind= orderobjTrue.index[i]
                        logger.info(f"Checking SL/TP for orderid {orderobjTrue['Buyorderid'].iloc[i]} with LTP {ltp}")

                        orderobj.loc[ind,'Ltp']= ltp
                        
                        if (ltp<orderobjTrue['AveragePrice'].iloc[i]*(1-settings['sl_pct'])) and (orderobjTrue['Side'].iloc[i]=='LONG'):
                                orderobj.loc[ind,'Slhit']=True


                        
                        elif (ltp>orderobjTrue['AveragePrice'].iloc[i]*(1+settings['sl_pct'])) and (orderobjTrue['Side'].iloc[i]=='SHORT'):
                                orderobj.loc[ind,'Slhit']=True

                
                        
                        if (ltp>orderobjTrue['AveragePrice'].iloc[i]*(1+settings['tp_pct'])) and (orderobjTrue['Side'].iloc[i]=='LONG'):
                                orderobj.loc[ind,'TargetHit']=True
                        
                        elif (ltp<orderobjTrue['AveragePrice'].iloc[i]*(1-settings['tp_pct'])) and (orderobjTrue['Side'].iloc[i]=='SHORT'):
                                orderobj.loc[ind,'TargetHit']=True
                        
                        self.orderobjectwrite(newdata=orderobj,newdataflag=True)

                        
                    else:
                         pass
        except Exception as e :
             logger.error(e,exc_info=True)


            
                     

    def exitconditon(self):
        while True:
            self.checkpnlbox()
            self.closeorder()
            time.sleep(1)
    

    def cred(self):
        try:
            credpath = os.path.join(path,"config/config.json")
            with open(credpath, 'rb') as f:
                loaded_dict = json.load(f)
            return loaded_dict
        except Exception as e :
            print(e)
    
         


    def checkltp(self,exh,token,bakctest,LTP,ANGEL=None):
        try:
             
         
            credentials = self.cred()
            creddata=credentials['Angelcred']
            api= creddata['api_key'] 
            username=creddata['username']
            pwd = str(creddata['pwd'])
            tokenangel = creddata['token']   

            # broker = Angel.HTTP(1,api,username,pwd,tokenangel)
            tokenparam= {exh:[]}
            tokenparam[exh].append((str(int(token))))
            if not bakctest:
                ltp= ANGEL.get_quotes(tokenparam)
                ltp= float(ltp['data']['fetched'][0]['ltp'])
            else:
                 ltp=LTP
                 
            return ltp

        except Exception as e:
             logger.error(e,exc_info=True)
                

       

         



         
         

    def gettestdata(self,symbol):
        try:
            datapath= "data/ZohoWorkDrive/01-2025/01-2025/NIFTY_I.csv"
            datapath= os.path.join(path,datapath)


            df= pd.read_csv(datapath)
            df['updated_at']= pd.to_datetime(df['Date'],format='%Y%m%d')
            df['updated_at']=df['updated_at']+pd.to_timedelta(df['Time'])
            df['updated_at'] = df['updated_at'].dt.tz_localize('Asia/Kolkata')
            


            # df=df[df["instrumentname"]==symbol.upper()]
            return df 
        except Exception as e :
            logger.error(e,exc_info=True)

        

    def ohlc(self,data,timeframe=None,baktest=False,count=1):
        data['updated_at']= pd.to_datetime(data['updated_at'])
        df = data.set_index('updated_at')
        if count==1:
             
            open_price = df['Close'].resample(timeframe).ohlc()
        else:
            open_price = df['close'].resample(timeframe).ohlc()
             
             

        data=open_price.dropna()
        data = data.reset_index()
        return data

    def angelcandels(self,symbol):
        credentials = self.cred()
        creddata=credentials['Angelcred']
        api= creddata['api_key'] 
        username=creddata['username']
        pwd = str(creddata['pwd'])
        tokenangel = creddata['token']   
        data= Angel.searchscrip(symbol,instrument='FUTIDX')
        if symbol in 'NIFTY,BANKNIFTY,SENSEX,FINNIFTY':
            setindex= 'FUTIDX'
        else:
            setindex= 'FUTSTK'
        
        data['expiry'] = pd.to_datetime(data['expiry'],format="%d%b%Y")
        data= data.sort_values(by='expiry')
        data= data[data['instrumenttype']==setindex] 
        symboltoken= data['token'].iloc[0]
        broker = Angel.HTTP(1,api,username,pwd,tokenangel)
        interval= interval['intervalAngel']
        data =broker.candels('NFO',symboltoken,interval)
        

        return data

        
            


    
    
    def startwebsocket(self):
        # angellogin= Angel.SMARTAPI(1)
        # angellogin.smartAPI_Login()
        a= Angel.WebSocketConnect(1)
        a.start_thread()

    def angellogin(self):
        
        angellogin= Angel.SMARTAPI(1)
        angellogin.smartAPI_Login()
        return angellogin
    
    def gettoken(self,symbol,ANGEL):
        try:
            
            tokenparam= {'NSE':['26000']}

            checkltp= ANGEL.get_quotes(tokenparam)
            # print(symbol)
        
            ltp = checkltp['data']['fetched'][0]['ltp']
            atm = round(ltp/100)*100
            totalstrike= [atm-200,atm-100,atm,atm+100,atm+200]
            tokenlist= []
            token= Angel.searchscrip(symbol,instrument='OPTIDX')
            token['expiry_dt'] = pd.to_datetime(token['expiry'], format='%d%b%Y')
            token = token.sort_values(by='expiry_dt')
            token['strike']= token['strike'].astype('float').astype('int')/100
            token= token[(token['strike'].isin(totalstrike)) & (token['instrumenttype']=='OPTIDX')]

            tokenlist= token.iloc[:10]
            # pandas to json
            tokenlist.to_json( os.path.join(path,'config/tokenlist.json'))
                

            return  tokenlist,tokenlist['token'].tolist()
        except Exception as e:
            logger.error(e,exc_info=True)
            return None ,None

