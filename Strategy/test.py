from Bot import env
import time 
import os 
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from Bot.utility import utility
from Bot.Strategy import bb
from Bot.Broker import Angelsdk as angel

path = env.currenenv

logpath= os.path.join(path,'Botlogs/test.logs')
logpath= os.path.normpath(logpath)
print(logpath,'logpath')
logger=env.setup_logger(logpath)

utilis= utility.misc()


def test():
    try:

        logger.info("Test start for the all the symbols")
        misc=utility.misc()
        symbol = misc.getsymbols()
        for i in symbol:
            testdata = misc.gettestdata(i)
            data= misc.buildcandels(testdata,'5min',True)
            obj=bb.strategy()
            obj.main(data,True)
            logger.info(f"Test Completed for {i}")

    except Exception as e:
        logger.error(f"Error in test: {e}")
    
def tesbb(data):
    try:

        obj=bb.strategy()
        datar= obj.main(data)
        
        logger.info('test end')
    except Exception as e:
        logger.error(e,exc_info=True)
def testorder():
    obj= utility.misc()
    orderparam= dict()

    orderparam['symboltoken']=26000
    orderparam['exchange']='NSE'
    orderparam['transactiontype']='BUY'
    orderparam['product_type']='MIS'
    orderparam['quantity']=1
    orderparam['order_type']='MKT'
    orderparam['price']=22000   
    orderparam['sl']=10
    orderparam['target']=10
    orderparam['trail']=10
    orderparam['Amount']=0
    orderparam['quantity']=75
    orderparam['ltp']=22900
    orderparam['tradingsymbol']='NIFTY50'
    orderparam['Side']='Long'
    orderparam['updated_atdiff']=1
    orderparam['TargetHit']=False
    orderparam['Tslhit']=False
    orderparam['Slhit']=False





    order= obj.processorder(orderparam)
    
def testmerge():
    data=utilis.mergebacktest()
    return data
def testbuildcandle():
    data= utilis.getdata('NIFTY50',True)
    print(data.head())
    candle= utilis.buildcandels(data,'5min')
    print(candle.head())
    return candle
def testclosorder():
    data = utilis.closeorder()
    print(data)

def testpnl():
    utilis.checkpnlbox()

def websockettest():
    utilis.startwebsocket()
times= time.time()
# data =utilis.getmergedata('nifty')
websockettest()
from concurrent.futures import ThreadPoolExecutor
times= time.time()


import datetime
date= datetime.datetime.today()
print(f"{date.year}-{date.month}")