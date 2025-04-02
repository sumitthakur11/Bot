from utility import utility
from Strategy import bb as startegy
import os 
import logging
import threading
from concurrent.futures import ThreadPoolExecutor


path= os.getcwd()
path= str(path)
logpath= os.path.join(path,'botlogs')
logging.basicConfig(level=logging.DEBUG,filename=logpath,datefmt="%d-%m-%y %H:%M:%S")
logger= logging.getLogger("test")

def test():
    try:

        logger.info("Test start for the all the symbols")
        misc=utility.misc()
        symbol = misc.getsymbols()
        for i in symbol:
            testdata = misc.gettestdata(i)
            for j in testdata.items():
                startegy.strategy.finalprocess(j)
        logger.info(f"Test Completed for {i}")

    except Exception as e:
        logger.error(f"Error in test: {e}")
    

