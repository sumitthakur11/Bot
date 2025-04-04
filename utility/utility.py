from Broker import upstoxsdk as upstox
import os
import logging
import json
import pandas as pd 
import time as ts 
import pytz


path= os.getcwd()
path= os.path.join(path,'Botkapil')
path= str(path)
logpath= os.path.join(path,'botlogs/utility.logs')
logpath= os.path.normpath(logpath)
print(logpath,'logpath')
logging.basicConfig(level=logging.DEBUG,filename=str(logpath),format="%(asctime)s - %(levelname)s - %(message)s",datefmt="%d-%m-%y %H:%M:%S")

logger= logging.getLogger("UTILITY")

class misc:
    def __init__(self):

        self.orderdata = pd.DataFrame()

        

    
    def getsymbols(self):
        
        try:
            with open(path+f"config/symbols.json", 'rb') as f:
                loaded_dict = json.load(f)
            return loaded_dict
        except Exception as e :
                        logger.error(e)

    
    
    
    def getdata(self,symbol):
        try:

            df= pd.read_json(path+f"data/feeddata/{symbol}.json")
            df= df[-2000:]
            
            return df 
        except Exception as e :
            logger.error(e)


    def orderobject(self,newdata):
        try:
            path= path+"data/liveorderdata/orderdata.csv"
            if not os.path.exists(path):
                self.orderdata.to_csv(path)
            file = pd.read_csv(path)
            return file
            
        except Exception as e:
            logger.error(f"check the orderobject function {e}")

    
    def processorder (self,orderparams,atmcal=60,subclients=0,STOPLOSS=True,PAPER=True,makesymbol=True,advicecheck='',backtest=True):
        try:
            
            orderid=  []
            placeorders=False
            if backtest :
                pass
            else :
                brokerlist= self.fetchaccounts()
                for i in brokerlist:
                    broker= upstox.HTTP()
                    if placeorders:
                        order_ids=broker.placeorder(orderparams,self.orderobject,STOPLOSS,backtest)
                        
                        orderid.append(order_ids)
                        placeorders=False

                return orderid
        except Exception as e:
            print(str(e))
            return str(e)

        

    def fetchaccounts(self):
        try:
            path= path+f"config/account.csv"
            if not os.path.exists(path):
                os.makedirs(path)


            df= pd.read_csv(path+f"config/account.csv")
            return df 
        except Exception as e :
            logger.error(e)

        pass

    def fetchorders(self):
        try:
            path= path+"data/liveorderdata/orderdata.csv"
            if not os.path.exists(path):
                os.makedirs(path)


            df= pd.read_csv(path+f"config/account.csv")
            return df 
        except Exception as e :
            logger.error(e)

    
    def gettestdata(self):
        try:
            path= path+"data/testdata/test.json"
            if not os.path.exists(path):
                os.makedirs(path)


            df= pd.read_json(path+f"config/account.csv")
            return df 
        except Exception as e :
            logger.error(e)

        

    def buildcandels(self,data,timeframe_seconds=None):
        try:
                
                data['updated_at'] = pd.to_datetime(data['updated_at'])
                data['updated_at'] = data['updated_at'].dt.tz_localize('Asia/Kolkata')
                df = data.set_index('updated_at')
                open_price = df['LTP'].resample(timeframe_seconds).first()
                high_price = df['LTP'].resample(timeframe_seconds).max()
                low_price = df['LTP'].resample(timeframe_seconds).min()
                close_price = df['LTP'].resample(timeframe_seconds).last()
                volume= df['LTP'].resample(timeframe_seconds).last()
                self.ohlc = pd.DataFrame({
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'close': close_price,
                    
                })
                self.ohlc=self.ohlc.dropna()
                self.ohlc = self.ohlc.reset_index()
                return self.ohlc
        except Exception as e:
                            logger.error(e)




    
    
    
    
