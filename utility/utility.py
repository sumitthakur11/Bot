import sys

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
        orderdata= [['',datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S"),'','','','','',False,0.0,0,0.0,'',0.0,False,False,False,False,False,False,False,False,False,False,datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S"),0.0,0.0,0.0,False,'','','',0.0,0.0,0.0,0,False,0,0,False,False,False,False,False,False,False]]

        self.orderdata = pd.DataFrame(orderdata,columns=['AccountNo','Entrytime','Broker','Side','Buyorderid','Symbol','Token','Status','Ltp','Qty','AveragePrice','Sellorderid','Sellprice','TargetHit','TargetHit1','TargetHit2','TargetHit3','TargetHit4','TargetHit5','Slhit','Slhit1','Slhit2','Tslhit','Exittime','Target','Trail','Sl','Backtest','Transactiontype','Order_type','Exchange','Pnl','Netpnl','Commision','retry','forclosed','exitqty'
                                                         ,'exitedqty','sl1processed','sl2processed','target1processed','target2processed','target3processed','target4processed',"tslprocessed"],dtype='object')
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


    def repcloseorder(self,orderobj,orderobjTrue,i,settings,ANGEL):
        ind= orderobjTrue.index[i]

        orderparam= dict()
        orderparam['Token']= orderobjTrue['Token'].iloc[i]
        orderparam['exchange']=orderobjTrue['Exchange'].iloc[i]
        orderparam['Transactiontype']='SELL' if orderobjTrue['Transactiontype'].iloc[i]=='BUY' else 'BUY'
        orderparam['product_type']='CARRYFORWARD'
        orderparam['order_type']='MARKET'
        orderparam['price']=orderobjTrue['Ltp'].iloc[i]
        # qty should be multiple of lot size and should not exceed the quantity in the order
        lotsize = settings['lotsize']
        orderparam['quantity']=orderobjTrue['Qty'].iloc[i]*orderobjTrue['exitqty'].iloc[i] if orderobjTrue['exitqty'].iloc[i] else orderobjTrue['Qty'].iloc[i]
        # Ensure quantity is a multiple of lot size
        orderparam['quantity'] = min(orderparam['quantity'], orderobjTrue['Qty'].iloc[i] - orderobjTrue['exitedqty'].iloc[i]) if orderobjTrue['Slhit'].iloc[i] or orderobjTrue['TargetHit'].iloc[i] or orderobjTrue['Tslhit'].iloc[i] else orderparam['quantity']
        orderparam['quantity'] =   max(lotsize, orderparam['quantity'] // lotsize * lotsize)
        print('Original quantity:', orderparam['quantity'])
        orderparam['tradingsymbol']=orderobjTrue['Tradingsymbol'].iloc[i]
        


        orderid=ANGEL.closetrade(orderparam,orderobjTrue['Backtest'].iloc[i])
        print(f"Order close response for orderid {orderobjTrue['Buyorderid'].iloc[i]} is {orderid}")
        if orderid:

            print(f"Order {orderobjTrue['Buyorderid'].iloc[i]} closed successfully with Sell order id {orderid}")
            exitedqty= orderobjTrue['exitedqty'].iloc[i] + orderparam['quantity']
            orderobj.loc[ind,'exitedqty']= exitedqty
            orderobj.loc[ind,'Status']=False if exitedqty== orderobjTrue['Qty'].iloc[i] else True 
            orderobj.loc[ind,'Exittime']=datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")
            orderobj.loc[ind,'Sellorderid']=orderid
            orderobj.loc[ind,'Sellprice']=orderobjTrue['Ltp'].iloc[i]
            orderobj.loc[ind,'Pnl']=float(orderobjTrue['Ltp'].iloc[i]-orderobjTrue['AveragePrice'].iloc[i])*orderobjTrue['Qty'].iloc[i]
            orderobj.loc[i,'Netpnl']=float( orderobjTrue['Pnl'].iloc[i])-float( orderobjTrue['Commision'].iloc[i])
            orderobj.loc[ind,'forclosed']=True
            self.orderobjectwrite(newdata=orderobj,newdataflag=True)


    def closeorder(self,forceclose=False,ANGEL=None):
        try :

             
            orderobj=self.orderobjectread()
            orderobj=pd.DataFrame(orderobj,dtype='object')
            orderobjTrue=orderobj[orderobj['Status']==True]

            settings= self.loadsettings()

            if not orderobj.empty:
                for i in range(len(orderobjTrue)):
                        if orderobjTrue['Status'].iloc[i]: #and orderobjTrue['forclosed'].iloc[i]==False:
                            ind= orderobjTrue.index[i]

                             
                            if (orderobjTrue['Slhit'].iloc[i] or orderobjTrue['TargetHit'].iloc[i] or forceclose ) and (not orderobjTrue['Backtest'].iloc[i])  :
                                    
                                    print('Check order close for live order............................................................................')
                                    print('buffer',orderobjTrue['Slhit'].iloc[i],orderobjTrue['Slhit1'].iloc[i],orderobjTrue['Slhit2'].iloc[i],orderobjTrue['TargetHit'].iloc[i],orderobjTrue['TargetHit1'].iloc[i],orderobjTrue['TargetHit2'].iloc[i],orderobjTrue['TargetHit3'].iloc[i],orderobjTrue['TargetHit4'].iloc[i])
                                
                                    self.repcloseorder(orderobj,orderobjTrue,i,settings,ANGEL)
                            
                                    

                                    if orderobjTrue['Slhit'].iloc[i]:
                                        logger.info(f"Order {orderobjTrue['Buyorderid'].iloc[i]} closed due to MAX LOSS  HIT")
                                        sys.exit(0)
                                        
                            

                            elif (orderobjTrue['Slhit1'].iloc[i]  and orderobjTrue['sl1processed'].iloc[i]==False) or (orderobjTrue['Slhit2'].iloc[i] and orderobjTrue['sl2processed'].iloc[i]==False) and (not orderobjTrue['Backtest'].iloc[i]): 
                                logger.info(f"Order {orderobjTrue['Buyorderid'].iloc[i]} hit stoploss, processing partial close")
                                print('Check order close for stoploss partial close............................................................................')
                                print('buffer',orderobjTrue['Slhit1'].iloc[i],orderobjTrue['Slhit2'].iloc[i])
                                orderobj.loc[ind,'sl1processed']= True if orderobjTrue['Slhit1'].iloc[i] else orderobjTrue['sl1processed'].iloc[i]
                                orderobj.loc[ind,'sl2processed']= True if orderobjTrue['Slhit2'].iloc[i] else orderobjTrue['sl2processed'].iloc[i]
                                self.repcloseorder(orderobj,orderobjTrue,i,settings,ANGEL)
                            elif (orderobjTrue['TargetHit1'].iloc[i] and orderobjTrue['target1processed'].iloc[i]==False) or (orderobjTrue['TargetHit2'].iloc[i] and orderobjTrue['target2processed'].iloc[i]==False) or (orderobjTrue['TargetHit3'].iloc[i] and orderobjTrue['target3processed'].iloc[i]==False) or (orderobjTrue['TargetHit4'].iloc[i] and orderobjTrue['target4processed'].iloc[i]==False) and (not orderobjTrue['Backtest'].iloc[i]) :
                                logger.info(f"Order {orderobjTrue['Buyorderid'].iloc[i]} hit target, processing partial close")
                                print('Check order close for target partial close............................................................................')
                                print('buffer',orderobjTrue['TargetHit1'].iloc[i],orderobjTrue['TargetHit2'].iloc[i],orderobjTrue['TargetHit3'].iloc[i],orderobjTrue['TargetHit4'].iloc[i])
                                orderobj.loc[ind,'target1processed']= True if orderobjTrue['TargetHit1'].iloc[i] else orderobjTrue['target1processed'].iloc[i]
                                orderobj.loc[ind,'target2processed']= True if orderobjTrue['TargetHit2'].iloc[i] else orderobjTrue['target2processed'].iloc[i]
                                orderobj.loc[ind,'target3processed']= True if orderobjTrue['TargetHit3'].iloc[i] else orderobjTrue['target3processed'].iloc[i]
                                orderobj.loc[ind,'target4processed']= True if orderobjTrue['TargetHit4'].iloc[i] else orderobjTrue['target4processed'].iloc[i]
                                self.repcloseorder(orderobj,orderobjTrue,i,settings,ANGEL)
                            
                            elif (orderobjTrue['Tslhit'].iloc[i]  and orderobjTrue['tslprocessed'].iloc[i]==False) and (not orderobjTrue['Backtest'].iloc[i]) :
                                logger.info(f"Order {orderobjTrue['Buyorderid'].iloc[i]} hit trailing stoploss, processing partial close")
                                print('Check order close for trailing stoploss partial close............................................................................')
                                print('buffer',orderobjTrue['Tslhit'].iloc[i])
                                orderobj.loc[ind,'tslprocessed']= True if orderobjTrue['Tslhit'].iloc[i] else orderobjTrue['tslprocessed'].iloc[i]
                                self.repcloseorder(orderobj,orderobjTrue,i,settings,ANGEL)
                            
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
            orderretry=orderobj['retry'].iloc[-1]

            entry_time = pd.to_datetime(orderobj['Entrytime'].iloc[-1])
            if entry_time.tzinfo is None:
                 entry_time = entry_time.tz_localize("Asia/Kolkata")
            else:
                    entry_time = entry_time.tz_convert("Asia/Kolkata")

            
            if datetime.datetime.now(pytz.timezone("Asia/Kolkata")) > entry_time + datetime.timedelta(minutes=orderparams['updated_atdiff']):

                if backtest  and (not  orderobj['Status'].any() ):


                    # broker= Angel.HTTP(1)
                    order_ids=ANGEL.placeorder(orderparams,self.orderobjectwrite,True)
                    return order_ids




                elif (not backtest ) and (not  orderobj['Status'].any() ) and orderretry<retry:
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

   


             
            
   
    
    
    def  checkpnlbox(self,LTP='',ANGEL=None):
        try:
            logger.info("Checking SL/TP for open orders")
            settings= self.loadsettings()
            orderobj=self.orderobjectread()
            orderobjTrue=orderobj[orderobj['Status']==True]

            orderobj['Slhit']= orderobj['Slhit'].astype('object')      
            orderobj['TargetHit']= orderobj['TargetHit'].astype('object')      
            orderobj['Commision']= orderobj['Pnl'].astype('float')
            orderobj['Commision']= settings['commision']
            orderobj['Slhit1']= orderobj['Slhit1'].astype('object')   
            orderobj['Slhit2']= orderobj['Slhit2'].astype('object')   
            orderobj['Netpnl']= orderobj['Netpnl'].astype('object')   

            orderobj['TargetHit1']= orderobj['TargetHit1'].astype('object')   
            orderobj['TargetHit2']= orderobj['TargetHit2'].astype('object') 
            orderobj['TargetHit3']= orderobj['TargetHit3'].astype('object') 
            orderobj['TargetHit4']= orderobj['TargetHit4'].astype('object') 
            orderobj['Ltp']= orderobj['Ltp'].astype('object') 


              


            

            if not orderobjTrue.empty:
                for i in range(len(orderobjTrue)):

                    if orderobjTrue['Status'].iloc[i]:
                        ltp= self.checkltp(orderobjTrue['Exchange'].iloc[i],orderobjTrue['Token'].iloc[i],orderobjTrue['Backtest'].iloc[i],LTP,ANGEL)
                        time.sleep(1)
                        # generate random ltp for backtest
                        # ltp =  random.uniform(orderobjTrue['AveragePrice'].iloc[i]*0.9, orderobjTrue['AveragePrice'].iloc[i]*1.1)
                        # ltp= float(ltp)
                        ind= orderobjTrue.index[i]
                        logger.info(f"Checking SL/TP for orderid {orderobjTrue['Buyorderid'].iloc[i]} with LTP {ltp}")

                        orderobj.loc[ind,'Ltp']= ltp
                        
                        
                    # check pnl angel broker
                        if (orderobjTrue['Pnl'].sum()< -settings['maxloss']) and settings['maxloss']>0:
                            print('Max loss limit reached, closing all orders','Max loss:',orderobjTrue['Pnl'].sum(),'Max loss setting:',settings['maxloss'])
                            logger.info(f"Max loss limit reached, closing all orders")
                            orderobj.loc[:,'Slhit']=True
                            orderobj.loc[:,'exitqty']= 1
                            self.orderobjectwrite(newdata=orderobj,newdataflag=True)
                            # sys.exit(1)
                            
                        
                        
                        if (ltp<orderobjTrue['AveragePrice'].iloc[i]*(1-settings['stoploss1'])) and (orderobjTrue['Side'].iloc[i]=='LONG') and settings['stoploss1']>0:
                                orderobj.loc[ind,'Slhit1']=True
                                orderobj.loc[ind,'exitqty']= settings['stoplossqty1']
 

                        
                        # elif (ltp>orderobjTrue['AveragePrice'].iloc[i]*(1+settings['stoploss1'])) and (orderobjTrue['Side'].iloc[i]=='SHORT') and settings['stoploss1']>0:
                        #         orderobj.loc[ind,'Slhit1']=True
                        #         orderobj.loc[ind,'exitqty']= settings['stoplossqty1']

                        
                        
                        if (ltp<orderobjTrue['AveragePrice'].iloc[i]*(1-settings['stoploss2'])) and (orderobjTrue['Side'].iloc[i]=='LONG') and settings['stoploss2']>0:
                                orderobj.loc[ind,'Slhit2']=True
                                orderobj.loc[ind,'exitqty']= settings['stoplossqty2']
 
                        
                        
                        # elif (ltp>orderobjTrue['AveragePrice'].iloc[i]*(1+settings['stoploss2'])) and (orderobjTrue['Side'].iloc[i]=='SHORT') and settings['stoploss2']>0   :
                        #         orderobj.loc[ind,'Slhit2']=True
                        #         orderobj.loc[ind,'exitqty']= settings['stoplossqty2']



                        if (ltp>orderobjTrue['AveragePrice'].iloc[i]*(1+settings['target1'])) and (orderobjTrue['Side'].iloc[i]=='LONG') and settings['target1']>0:
                                orderobj.loc[ind,'TargetHit1']=True
                                orderobj.loc[ind,'exitqty']= settings['targetqty1']

                        
                        # elif (ltp<orderobjTrue['AveragePrice'].iloc[i]*(1-settings['target1'])) and (orderobjTrue['Side'].iloc[i]=='SHORT') and settings['target1']>0:
                        #         orderobj.loc[ind,'TargetHit1']=True
                        #         orderobj.loc[ind,'exitqty']= settings['targetqty1']




                        if (ltp>orderobjTrue['AveragePrice'].iloc[i]*(1+settings['target2'])) and (orderobjTrue['Side'].iloc[i]=='LONG') and settings['target2']>0:
                                orderobj.loc[ind,'TargetHit2']=True
                                orderobj.loc[ind,'exitqty']= settings['targetqty2']
                        
                        # elif (ltp<orderobjTrue['AveragePrice'].iloc[i]*(1-settings['target2'])) and (orderobjTrue['Side'].iloc[i]=='SHORT') and settings['target2']>0:
                        #         orderobj.loc[ind,'TargetHit2']=True
                        #         orderobj.loc[ind,'exitqty']= settings['targetqty2']
                        


                        if (ltp>orderobjTrue['AveragePrice'].iloc[i]*(1+settings['target3'])) and (orderobjTrue['Side'].iloc[i]=='LONG') and settings['target3']>0  :
                                orderobj.loc[ind,'TargetHit3']=True
                                orderobj.loc[ind,'exitqty']= settings['targetqty3']
                        
                        # elif (ltp<orderobjTrue['AveragePrice'].iloc[i]*(1-settings['target3'])) and (orderobjTrue['Side'].iloc[i]=='SHORT') and settings['target3']>0:
                        #         orderobj.loc[ind,'TargetHit3']=True
                        #         orderobj.loc[ind,'exitqty']= settings['targetqty3']
                        

                        if (ltp>orderobjTrue['AveragePrice'].iloc[i]*(1+settings['target4'])) and (orderobjTrue['Side'].iloc[i]=='LONG') and settings['target4']>0  :
                                orderobj.loc[ind,'TargetHit4']=True
                                orderobj.loc[ind,'exitqty']= settings['targetqty4']
                        
                        # elif (ltp<orderobjTrue['AveragePrice'].iloc[i]*(1-settings['target4'])) and (orderobjTrue['Side'].iloc[i]=='SHORT') and settings['target4']>0:
                        #         orderobj.loc[ind,'TargetHit4']=True
                        #         orderobj.loc[ind,'exitqty']= settings['targetqty4']
                        

                        if (ltp<orderobjTrue['AveragePrice'].iloc[i]*(1-settings['lockedpl'])) and (orderobjTrue['TargetHit1'].iloc[i] or orderobjTrue['TargetHit2'].iloc[i] or orderobjTrue['TargetHit3'].iloc[i] or orderobjTrue['TargetHit4'].iloc[i]) and (orderobjTrue['Side'].iloc[i]=='LONG') and settings['lockedpl']>0:
                                orderobj.loc[ind,'Tslhit']=True
                                orderobj.loc[ind,'exitqty']= 1
                        
                        # elif (ltp>orderobjTrue['AveragePrice'].iloc[i]*(1+settings['lockedpl'])) and (orderobjTrue['TargetHit1'].iloc[i] or orderobjTrue['TargetHit2'].iloc[i] or orderobjTrue['TargetHit3'].iloc[i] or orderobjTrue['TargetHit4'].iloc[i]) and (orderobjTrue['Side'].iloc[i]=='SHORT') and settings['lockedpl']>0:
                        #         orderobj.loc[ind,'Tslhit']=True
                        #         orderobj.loc[ind,'exitqty']= 1
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
                if LTP:
                     ltp= LTP
                else:
                     ltp= ANGEL.get_quotes(tokenparam)
                     ltp= float(ltp['data']['fetched'][0]['ltp'])

                
                 
                 
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

