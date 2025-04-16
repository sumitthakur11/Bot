from Bot import env
from .SmartApi import smartConnect
from .SmartApi import smartWebSocketV2
import pyotp
import asyncio
import base64
import hashlib
import hmac
import json
import logging
from random import random
import time
import uuid
import requests
import threading
import pandas as pd 
import datetime
import math
import pytz
import os 
import pathlib as p
from stat import *


path= env.currenenv
logpath= os.path.join(path,'botlogs/Angelbroker.logs')
logpath= os.path.normpath(logpath)
# logpath= os.path.join(logpath,'Angelbroker.logs')
print(logpath,'logpath')
logger=env.setup_logger(logpath)


def searchscrip (Symbol='',exchange='NFO',instrument=''):
        try:

            data = requests.get('https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json')
            if data.status_code == 200:
                db = pd.DataFrame(data.json())
            else:
                print(f"Failed to download the file. Status code: {data.status_code}")
            logpath= os.path.join(path,'data/NFO.csv')
            logpath= os.path.normpath(logpath)

            db.to_csv(logpath)
            if instrument =='TOKEN':

                db =db[db['token']==Symbol] 

            if instrument=='FUTIDXS':
                db =db[db['instrumenttype']=='FUTIDX'] 


            elif instrument !='EQ':
                db =db[db['instrumenttype']==instrument] 
                db = db[db['name'] ==  Symbol ]   


            else:
                db = db[db['exch_seg'] == exchange]
                db = db[db['symbol'] ==  Symbol ] 
            
            logger.info("function called searchscrip")
            return db
        except Exception as err:
            logger.error(err)
            raise err

# RES= searchscrip('NIFTY',instrument='FUTIDX') 

symboldata=searchscrip(instrument='FUTIDXS')

def preparetoken():
    dkeys= {}
    with open(path+f"/config/symbol.json", 'rb') as f:
        loaded_dict = json.load(f)
    tokens= []
    symbol = loaded_dict['symbol']
    for i in symbol:
       data= searchscrip(i,instrument='FUTIDX')
       data= data.sort_values(by='expiry')
       
       tk= data['token'].iloc[0]
       print(tk)
       tokens.append(tk)
       dkeys[i]=[]


    return tokens,dkeys

tokens1,finaldata= preparetoken()
class Ltp:
    def __init__(self,data) :
        try:
            self.data= {}
            self.data['LTP'] =int(data['last_traded_price'])/100 
            self.data['updated_at']= time.time()
            self.data['exchange_timestamp']= data['exchange_timestamp']
            self.data['exchange']= 'NFO'
            if data['exchange_type']==1:
                self.data['exchange']= 'NSE'
            elif data['exchange_type']==2:
                self.data['exchange']= 'NFO'
            elif data['exchange_type']==3:
                self.data['exchange']= 'BSE'
            elif data['exchange_type']==4:
                self.data['exchange']= 'BFO'
            self.data['token']= data['token']
            self.data['volume']= data['volume_trade_for_the_day']  if 'volume_trade_for_the_day' in data.keys() else 0
            sym=data['token']
            
            symbold=symboldata[symboldata['token']==sym]
            sym = symbold['name'].iloc[-1]
            date= datetime.datetime.today().date()
            rawpath= os.path.join(path,f'data/feeddata/{date}/{sym}')

            
            if  not os.path.exists(rawpath):
                os.makedirs(rawpath)
            rawpath= os.path.join(rawpath,f'{sym}.json')
            rawpath= os.path.normpath(rawpath)
            self.save_depth_data(sym,self.data,rawpath)

            #     time.sleep(1)
            #     rawpath= os.path.join(rawpath,f'{sym}.json')
            #     rawpath= os.path.normpath(rawpath)
            #     file= open(rawpath,'a')
            #     json.dump([],file,indent=4)
            # else:
            #     rawpath= os.path.join(rawpath,f'{sym}.json')
            #     rawpath= os.path.normpath(rawpath)
            #     file= open(rawpath,'a')
            #     json.dump(self.data,file,indent=4)
                



        except Exception as e:
            print(e)


        
    def save_depth_data(self, symbol, depth_data,rawpath):
        """Save depth data to file"""
        try:
            file_exists = os.path.exists(rawpath)
            
            with open(rawpath, 'r+') as f:
                if not file_exists:
                    f.write('[')
                else:
                    f.seek(0, os.SEEK_END)
                    f.seek(f.tell() - 1, os.SEEK_SET)
                    print(rawpath)
                    if f.read(1) == ']':
                        f.seek(f.tell() - 1, os.SEEK_SET)
                        f.truncate()
                        f.write(',')
                    else:
                        f.write('[')
                
                json_data = depth_data.copy()
                
                f.write(json.dumps(json_data))
                f.write(']')
            
            logger.info(f"Saved depth data for {symbol} to {rawpath}")
            return True
        except Exception as e:
            logger.error(f"Error saving depth data for {symbol}: {str(e)}",exc_info=True)
            return False

        

# token=preparetoken()
# print(token)
class order:
    def __init__(self,data) :
        self.data= {}
        self.finaldata= []
        for i in range(len(data)):
                self.data['qty']=i['qty']
                self.data['prc']= i['prc']
                self.data['trgprc']= i['trgprc']
                self.data['rpt']= i['rpt']
                self.finaldata.append(self.data)
        print(self.finaldata)


class SMARTAPI(object) :
    
    def __init__(self, user,api_key ='', username = '',pwd = '',token=""):
        creddata= self.cred()
        creddata=creddata['Angelcred']
        self.api= creddata['api_key'] 
        self.username=creddata['username']
        self.pwd = creddata['pwd']
        self.orderid = None
        self.authToken= None
        self.refreshToken= None
        self.feedToken = None
        self.smartApi = smartConnect.SmartConnect(self.api)
        self.userid= user
        self.token = creddata['token']   
        self.decimals = 10**6
        self.occurred= 0
        
    def cred(self):
        try:
            with open(path+f"/config/config.json", 'rb') as f:
                loaded_dict = json.load(f)
                print(loaded_dict,'loadeddict')
            return loaded_dict
        except Exception as e :
            print(e)
    
        
    def smartAPI_Login(self):
        res= None
        self.occurred+=self.occurred
        try:
            totp = pyotp.TOTP(self.token).now()
        except Exception as e:
            logger.error(f"Invalid Token: The provided token is not valid or {e}") 
            raise e


        data = self.smartApi.generateSession(self.username, self.pwd, totp)
    

        if not data['status']:
            logger.error(data)
        else:
            tokendict={}
            tokendict['authToken'] = data['data']['jwtToken']
            tokendict['refreshToken'] = data['data']['refreshToken']
            print(tokendict['refreshToken'],'===================================================')
            tokendict['feedToken'] = self.smartApi.getfeedToken()
            self.smartApi.generateToken(tokendict['refreshToken'])
            res = self.smartApi.getProfile(tokendict['refreshToken'])
            res = res['data']['exchanges']
            filepath= os.path.join(path,f'Broker/{self.username}.json')
            filepath= os.path.normpath(filepath)

            print(filepath)
            
            out=open(filepath, 'w')
            json.dump(tokendict,out,indent=6)
            # out.close()

            
        return self.smartApi
    def get_angel_client(self):
        try:
            filepath= os.path.join(path,f'Broker/{self.username}.json')
            filepath= os.path.normpath(filepath)

            with open(filepath, 'rb') as f:
                loaded_dict = json.load(f)
                print(loaded_dict,'loadeddict')
            return loaded_dict
        except Exception as e :
            print(e)
    
        
    
    

class HTTP(SMARTAPI):
    def __init__(self,user,api_key ='', username = '',pwd = '',token=""):
        super().__init__(self,api_key , username ,pwd,token)
        self.user=user
        self.smartApi=self.client_()
        print(api_key , username ,pwd)
    
    

    def client_(self):
        self.client= self.get_angel_client()
        token=self.client['authToken'].split(' ')[1]
        self.smartApi = smartConnect.SmartConnect(self.api,access_token=token)

        return self.smartApi
    
    


    def wallet(self):
    
    
        data= self.smartApi.rmsLimit()
        return data['data']
    
    def optionchain(self,orderparam):
        print(orderparam['symbol'],''.join(orderparam['expiry']))
        expiry=(''.join(orderparam['expiry'])).upper().strip()
        payload =  {
        "name":orderparam['symbol'],    
        "expirydate":expiry
        }   

        data= self.smartApi.optionGreek(payload)
        data= pd.DataFrame(data['data'])
        data =data.sort_values(by=['tradeVolume','impliedVolatility'],key=lambda col: col.astype(float),ascending=False)
        
        print(data)

        return data

        
        
    #   

    
    def candels(self,exchange,symboltoken,interval):
        print(exchange,symboltoken,interval)
        todate= datetime.datetime.today().astimezone(pytz.timezone('Asia/Kolkata'))
        fromdate=todate- datetime.timedelta(days=100)
        todate= todate.strftime("%Y-%m-%d %H:%M")
        fromdate= fromdate.strftime("%Y-%m-%d %H:%M")

        candleParams={  
        "exchange": exchange,
        "symboltoken": symboltoken,
        "interval": interval,
        "fromdate":fromdate ,
        "todate": todate
        }
        candledetails= self.smartApi.getCandleData(candleParams)
        columns= ['updated_at', 'open', 'high', 'low', 'Close', 'Volume']
        candledetails= pd.DataFrame(candledetails['data'],columns=columns)
        candledetails['OI']=0

        return candledetails
                
    
    def get_quotes(self,exchangeTokens):
        mode= 'FULL'    
        # tokens= {
        # segment: [str(exchangeTokens)]
        # }
        print(exchangeTokens)
        
        # client= self.client_()
        data =self.smartApi.getMarketData(mode,exchangeTokens)
        
        return data
                

   
    
    
    
    def cancel_order(self, orderid):
        data = self.smartApi.cancelOrder(orderid, "NORMAL")
        return data
    
    

    
    def uniqueno(self):
        # import uuid
        return int(time.time()*1000)
    def closetrade(self, orderparam,PAPER):
        
        if not PAPER:

                orderparams1 = {
                        "variety": "NORMAL",
                        "tradingsymbol": orderparam['Symbol'],
                        "symboltoken":str(orderparam['Token']),
                        "transactiontype": orderparam['Transactiontype'],
                        "exchange": orderparam['exchange'],
                        "ordertype": orderparam['ordertype'],
                        "producttype": orderparam['product_type'],
                        "duration": "DAY",
                        "price": orderparam['price'],
                        'triggerprice':orderparam['price'],
                        "squareoff": "0",
                        "stoploss": "0",
                        "quantity": orderparam['quantity']}

                orderid = self.smartApi.placeOrder(orderparams1) 
        else:
                orderid  =self.uniqueno()
        

        return   orderid
    
    
    def placeorder(self, orderparam,orderobject,PAPER):
        try:

            
            print(PAPER,'paper')
            print(orderparam)
            quantity=orderparam['quantity']

            orderid= None
            orderupdate= orderobject() 
              
            orderupdate['Backtest']= orderupdate['Backtest'].astype('object')      
            orderupdate['Order_type']= orderupdate['Order_type'].astype('object')      
            orderupdate['Side']= orderupdate['Side'].astype('object')   
            orderupdate['Entrytime']= orderupdate['Entrytime'].astype('object') 
            orderupdate['Exittime']= orderupdate['Exittime'].astype('object')   
            orderupdate['Status']= orderupdate['Status'].astype('object')      






            

            minqty= None
            if int(orderparam['Amount'])!=0 and not  PAPER:
                wallet = self.wallet()
                minvalue= min(float(wallet['net']),orderparam['Amount'])
                if orderparam['instrument']=='EQ':
                    minqty=int(math.floor(minvalue/float(orderparam['ltp'])))
                else:
                    
                    
                    minqty=int((minvalue/int(orderparam['ltp']))/int(orderparam['lotsize']))*int(orderparam['lotsize'])
                    print(minqty)
                    minqty=int(min(minqty,int(orderparam['lotsize'])))
            maxvalue=float(orderparam['Amount']) 
            maxqty=int(math.floor(maxvalue/float(orderparam['ltp'])))

            quantity=orderparam['quantity'] if minqty is None else minqty
            quantity=orderparam['quantity']  if quantity== 0  else quantity
            maxfinal= None
            lastindex= len(orderupdate)
            print(lastindex) 
            lastindex=lastindex+1
            if PAPER:
                maxfinal= max(int(quantity),int(maxqty))
                orderupdate.loc[lastindex,'Qty']=maxfinal         


            orderparams = {
            "variety": "NORMAL",
            "tradingsymbol": orderparam['tradingsymbol'],
            "symboltoken":str(orderparam['symboltoken']),
            "transactiontype": orderparam['transactiontype'],
            "exchange": orderparam['exchange'],
            "ordertype": orderparam['order_type'],
            "producttype": orderparam['product_type'],
            "duration": "DAY",
            "price": orderparam['price'],
            "squareoff": "0",
            "stoploss": "0",
            "quantity": quantity}
            if not PAPER:
                orderid = self.smartApi.placeOrder(orderparams)
                orderupdate.loc[lastindex,'Buyorderid']=orderid
                orderupdate.loc[lastindex,'Backtest']=False

                
            else:

                orderupdate.loc[lastindex,'Buyorderid']=self.uniqueno()
                orderupdate.loc[lastindex,'Backtest']=True

                
            # orderparam['user']=1
            orderupdate.loc[lastindex,'Status']=True
            orderupdate.loc[lastindex,'AveragePrice']=orderparam['ltp']
            orderupdate.loc[lastindex,'Broker']='ANGEL'
            orderupdate.loc[lastindex,'Tradingsymbol']=orderparam['tradingsymbol']
            orderupdate.loc[lastindex,'Token']=orderparam['symboltoken']
            orderupdate.loc[lastindex,'Order_type']=orderparam['order_type']
            orderupdate.loc[lastindex,'Transactiontype']=orderparam['transactiontype']
            orderupdate.loc[lastindex,'Product_type']=orderparam['product_type']
            orderupdate.loc[lastindex,'Sl']=orderparam['sl']
            orderupdate.loc[lastindex,'Target']=orderparam['target']
            orderupdate.loc[lastindex,'Trail']=orderparam['trail']
            orderupdate.loc[lastindex,'Entrytime']=datetime.datetime.now()
            orderupdate.loc[lastindex,'Exchange']=orderparam['exchange']
            orderupdate.loc[lastindex,'Side']='LONG' if orderparam['transactiontype']=='BUY' else 'SHORT'
            orderupdate.loc[lastindex,'TargetHit']=orderparam['TargetHit']
            orderupdate.loc[lastindex,'Slhit']=orderparam['Slhit']     
            orderupdate.loc[lastindex,'Tslhit']=orderparam['Tslhit']     

            


        




            
            orderobject(newdata=orderupdate,newdataflag=True)
            
            
            return   orderid
        except Exception as e:
            logger.error(e,exc_info=True)
    
    
    
    def gainersLosers(self,typedata):
        params= {
            "datatype":typedata, # Type of Data you want(PercOILosers/PercOIGainers/PercPriceGainers/PercPriceLosers)
            "expirytype":"NEAR" #Expiry Type (NEAR/NEXT/FAR)
            }
        data = self.smartApi.gainersLosers(params)
        logger.info(f"Order Book: {data}")
        return data

    def order_history(self):

        data = self.smartApi.orderBook()
        logger.info(f"Order Book: {data}")
        return data
    def modifyorder(self,exchange,tradingsymbol, orderno, newprice,PAPER,orderobject):
        print('here',PAPER)
        
        orderparams = {
        "variety": "NORMAL",
        "orderid": orderno,
        "price":newprice,
        }
        orderid = None
        if not PAPER:
            orderid = self.smartApi.modifyOrder(orderparams)

        orderobject.sellorderstatus= 'MODIFIED'
        orderobject.sellprice= float(newprice)

        if PAPER:
            # orderobject.status=False
            pass


        orderobject.save()
        return orderid
class WebSocketConnect(SMARTAPI):
    def __init__(self, user,api_key ='',  username = '',pwd = '',token="",update_depth=''):
        super().__init__(user,api_key , username ,pwd)
        self.update_depth= update_depth
        
        NIFTY= '26000'
        BANKNIFTY= 26009
        FINNIFTY = ''
        MIDCAP= 26014

        
    def start_thread(self):


        token = self.get_angel_client()
        authToken= token['authToken'].split(' ')[1]
        feedToken=token['feedToken']
        



        

        self.sws = smartWebSocketV2.SmartWebSocketV2(authToken, self.api, self.username, feedToken,
                                    max_retry_attempt=2, retry_strategy=0, retry_delay=10, retry_duration=30)



        self.correlation_id = "abcde"   
        self.mode =2

        tokenlist,dkyes= preparetoken()
        print(tokenlist)
        self.token_list = [
        {
            "exchangeType": 2,
            "tokens": tokenlist
        }]   
    

        # Callback for tick reception.
        def close_connection(self):
            self.sws.close_connection()

        def on_data(wsapp, message):
            logger.info("Ticks: {}".format(message))
            Ltp(message)
            print(message)
            # close_connection()


        def on_open(wsapp):
            logger.info("on open")
            print('open...')
            some_error_condition = False
            if some_error_condition:
                error_message = "Simulated error"
                if hasattr(wsapp, 'on_error'):
                    wsapp.on_error("Custom Error Type", error_message)
            else:
                self.sws.subscribe(self.correlation_id, self.mode, self.token_list)
        # Callback when current connection is closed.
        def on_close(wsapp):
           logger.info("Close")


        # Callback when connection closed with error.
        def on_error(wsapp, error):
            logger.error(error)
        # Callback when all reconnect failed (exhausted max retries)
        def on_control_message(wsapp, message):
            logger.info(f"Control Message: {message}")
        # Assign the callbacks.
        self.sws.on_data = on_data
        self.sws.on_open = on_open
        self.sws.on_close = on_close
        self.sws.on_error = on_error
        self.sws.on_control_message = on_control_message

        self.sws.connect()


