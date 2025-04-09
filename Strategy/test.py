import time 
import os 
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from BotKapil.utility import utility
from BotKapil.Strategy import bb
from BotKapil.Broker import Angelsdk as angel
from BotKapil import env

path = env.currenenv
path= os.path.join(path,'BotKapil')
print(path)

logpath= os.path.join(path,'botlogs/test.logs')
logpath= os.path.normpath(logpath)
print(logpath,'logpath')
logger=env.setup_logger(logpath)

utilis= utility.misc()
# raw= utilis.gettestdata('nifty')

# print(raw.head())
# data= utilis.buildcandels(raw,'5min')
# print(data.head())
# logger.info('test starts')

# obj = angel.HTTP(1)
# candel= obj.candels('NSE','26000','FIVE_MINUTE')



def test():
    try:

        logger.info("Test start for the all the symbols")
        misc=utility.misc()
        symbol = misc.getsymbols()
        for i in symbol:
            testdata = misc.gettestdata(i)
            data= obj.buildcandels(testdata,'5min')
            for j in data.items():
                Strategy.bb.main(j)
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


    order= obj.processorder(orderparam)
    time.wait(0.5)
    
def testmerge():
    data=utilis.mergebacktest()
    return data

def testclosorder():
    data = utilis.closeorder()
    print(data)

def testpnl():
    utilis.checkpnlbox()

times= time.time()

from concurrent.futures import ThreadPoolExecutor
times= time.time()

threadobj=ThreadPoolExecutor(max_workers=5)

# for _ in range(5):
threadobj.submit(testclosorder)

print('threading',time.time()-times)


# testclosorder()