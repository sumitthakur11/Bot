import os 
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from BotKapil.utility import utility
from BotKapil.Strategy import bb

from BotKapil import env

path = env.currenenv
path= os.path.join(path,'BotKapil')
print(path)

logpath= os.path.join(path,'botlogs/test.logs')
logpath= os.path.normpath(logpath)
print(logpath,'logpath')
logger=env.setup_logger(logpath)

obj= utility.misc()
raw= obj.gettestdata('nifty')
print(raw.head())
data= obj.buildcandels(raw,'5min')
print(data.head())
logger.info('test starts')

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
    
def tesbb():
    try:

        obj=bb.strategy()
        datar= obj.main(data)
        
        logger.info('test end')
    except Exception as e:
        logger.error(e,exc_info=True)


    

tesbb()
