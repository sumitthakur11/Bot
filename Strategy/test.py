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
def testorder(backtest):
    obj= utility.misc()
    orderparam= dict()

    orderparam['symboltoken']='57133'
    orderparam['exchange']='NFO'
    orderparam['transactiontype']='BUY'
    orderparam['product_type']='INTRADAY'
    orderparam['order_type']='MARKET'
    orderparam['price']=0
    orderparam['sl']=10
    orderparam['target']=10
    orderparam['trail']=10
    orderparam['Amount']=0
    orderparam['quantity']=75
    orderparam['ltp']=24200
    orderparam['tradingsymbol']='NIFTY29MAY25FUT'
    orderparam['Side']='Long'
    orderparam['updated_atdiff']=1
    orderparam['TargetHit']=False
    orderparam['Tslhit']=False
    orderparam['Slhit']=False





    order= obj.processorder(orderparam,backtest=backtest)
    



def testclosorder():
    data = utilis.closeorder()
    print(data)

def testpnl():
    utilis.checkpnlbox()

def websockettest():
    utilis.startwebsocket()

def testgettoken():
    utilis.gettoken('NIFTY')

testgettoken()