

from Bot import env

# from .SmartApi.smartConnect import SmartConnect
# from .SmartApi.smartWebSocketV2 import SmartWebSocketV2
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
import websocket
import threading
import pandas as pd 
import datetime
import math
import pytz
import os 
import pathlib

path= env.currenenv
logpath= os.path.join(path,'botlogs/upstox.logs')
logpath= os.path.normpath(logpath)
# logpath= os.path.join(logpath,'Angelbroker.logs')
print(logpath,'logpath')
logger=env.setup_logger(logpath)


class balance:
     def __init__(self, Balance):
        self.Account= dict()
        self.totalaccount= []
        # print(Balance.keys())
        self.Account['account'] = Balance['account']
        self.Account['username'] = Balance['username']
        self.Account['account_type'] = Balance['account_type']
        self.Account['available_balance'] = Balance['available_balance']
        self.Account['signing_keys'] = Balance['signing_keys'][-1]
        self.totalaccount.append(self.Account)
    
        
class Ltp:
    def __init__(self,data) :
        self.data= {}
        self.finaldata= []
        self.data['LTP'] =int(data['last_traded_price'])/100 
        self.data['updated_at']= time.time()
        self.data['exchange']= data['exchange_type']
        self.data['token']= data['token']
        self.data['volume']= 0
        self.data['instrumentname']= ''
        self.data['spikemark']=0
        self.data['isexpiryday']= 0


        finaldata.append(data)
        db.storedb(self.data)
        

def searchscrip (Symbol,exchange='NFO',instrument=''):
        try:

            data = requests.get('https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json')
            if data.status_code == 200:
                db = pd.DataFrame(data.json())
            else:
                print(f"Failed to download the file. Status code: {data.status_code}")
            if instrument !='EQ':
                db =db[db['instrumenttype']==instrument] 
                db = db[db['symbol'] ==  Symbol ]   

            db = db[db['exch_seg'] == exchange]
            db = db[db['symbol'] ==  Symbol ] 
            logger.info("function called searchscrip")
            return db
        except Exception as err:
            logger.error(err)
            raise err

# searchscrip('NIFTY',instrument='OPTIDX')     
        

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


class upstoxclient(object) :
    
    def __init__(self, user,api_key ='', username = '',pwd = '',token=''):
        self.api= api_key 
        self.username=username
        self.pwd = pwd
        self.orderid = None
        self.authToken= None
        self.refreshToken= None
        self.feedToken = None
        # self.smartApi = SmartConnect(api_key)
        self.userid= user
        self.token = token   #"46PG2HG3ST4NDTRD4FUUNVDC6Q"
        self.decimals = 10**6
        self.occurred= 0
        self.headers= {'Content-Type':'application/json','Accept':'application/json'}
        

        # self.upstoxAPI_Login()
    def upstoxAPI_Login(self,clientid,secret):
        payload= {'client_id':clientid}
        data= {'client_secret':secret}

        url = "https://api.upstox.com/v3/login/auth/token/request/:client_id"

        response = requests.request("POST", url, headers=self.headers,payload=payload, data=data)
        return response.json()

            
        
    def get_angel_client(self):
        try:
            with open(path+f"/Broker/{self.username}.json", 'rb') as f:
                loaded_dict = json.load(f)
                print(loaded_dict,'loadeddict')
            return loaded_dict
        except Exception as e :
            print(e)
    
        
    
    

class HTTP(upstoxclient):
    def __init__(self,user,api_key ='', username = '',pwd = '',token=''):
        super().__init__(self,api_key , username ,pwd,token)
        self.user=user
        self.smartApi=self.client_()
        print(api_key , username ,pwd)
    
    

        
    
    
    def client_(self):
        self.client= self.get_angel_client()
        token=self.client['authToken'].split(' ')[1]
        # self.smartApi = SmartConnect(self.api,access_token=token)
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
        fromdate=todate- datetime.timedelta(days=20)
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
        columns= ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        candledetails= pd.DataFrame(candledetails['data'],columns=columns)

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
                

   
    def get_coin_balance(self): 
        # print(self.key,self.secret,self.passphrase)
        
        try :
            return self.submit_request(
                method = "GET",
                path = "/account"
            )
        except Exception as e :
            return e
    
    
    
    
    def cancel_order(self, orderid):
        data = self.smartApi.cancelOrder(orderid, "NORMAL")
        return data
    
    

    
    
    
    
    def placeorder(self, orderparam,orderobject,PAPER):
        try:
            url= 'https://api-hft.upstox.com/v3'
            access_token= None
            self.headers['Authorization']= f'Bearer {access_token}'

            quantity=orderparam['quantity']

            orderid= None
            orderupdate= orderobject() 
              
            orderupdate['Backtest']= orderupdate['Backtest'].astype('object')      
            orderupdate['Order_type']= orderupdate['Order_type'].astype('object')      
            orderupdate['Side']= orderupdate['Side'].astype('object')   
            orderupdate['Entrytime']= orderupdate['Entrytime'].astype('object') 
            orderupdate['Exittime']= orderupdate['Exittime'].astype('object')      





            

            minqty= None
            if int(orderparam['Amount'])!=0 and  PAPER==False:
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
            if PAPER:
                maxfinal= max(int(quantity),int(maxqty))
                orderupdate.loc[lastindex,'Qty']=maxfinal         


           
            if not PAPER:
                payload = json.dumps({
                                "quantity": quantity,
                                "product": "D",
                                "validity": "DAY",
                                "price": orderparam['price'],
                                "tag": "string",
                                "instrument_token": f"{orderparam['exchange']}|{orderparam['symboltoken']}",
                                "order_type": orderparam['order_type'],
                                "transaction_type": orderparam['transactiontype'],
                                "disclosed_quantity": quantity,
                                "trigger_price": orderparam['price'],
                                "is_amo": False,
                                "slice": False
                                })
                orderid = requests.request("POST", url, headers=self.headers, data=payload)
                orderid= orderid.json()
                orderid= orderid['data']['order_ids']
                orderupdate.loc[lastindex,'Buyorderid']=orderid[0]
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

            


        




            
            orderobject(newdata=orderupdate)
            
            
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
class WebSocketConnect(upstoxclient):
   def __init__(self, user,api_key ='', username = '',pwd = '',update_depth=''):
        super().__init__(user,api_key , username ,pwd)
        self.update_depth= update_depth
        
        NIFTY= '26000'
        BANKNIFTY= 26009
        FINNIFTY = ''
        MIDCAP= 26014

        
        

        token = self.get_angel_client()
        authToken= token['authToken'].split(' ')[1]
        feedToken=token['feedToken']



        

        self.sws = SmartWebSocketV2(authToken, self.api, self.username, feedToken,
                                    max_retry_attempt=2, retry_strategy=0, retry_delay=10, retry_duration=30)

        self.correlation_id = "abcde"   
        self.mode =1
        self.token_list = [
        {
            "exchangeType": 1,
            "tokens": ["26009"]
        }]   
    

        # Callback for tick reception.
        def close_connection(self):
            self.sws.close_connection()

        def on_data(wsapp, message):
            logger.info("Ticks: {}".format(message))
            # self.update_depth(message)
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

        # Infinite loop on the main thread.
        # You have to use the pre-defined callbacks to manage subscriptions.
        self.sws.connect()



    

