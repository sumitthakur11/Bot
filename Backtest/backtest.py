
from Bot import env
from Strategy import bb as strategy
from utility import utility
import logging
import os 
import sys

path= env.currenenv
logpath= os.path.join(path,'botlogs/Angelbroker.logs')
logpath= os.path.normpath(logpath)
# logpath= os.path.join(logpath,'Angelbroker.logs')
print(logpath,'logpath')
logger=env.setup_logger(logpath)


def scheduelbacktest():
    try:
        retryno= 0
        misc= utility.misc()
        symbollist=misc.getsymbols()
        
        for i in symbollist:
            logger.info(f"backtest starts for symbol:{i}")
            data = misc.getdata(i)
            for j in data.items():
                flag=strategy.strategy.finalprocess(j,True)
                logger.info(f"current running ticks are as follows:{j}")
                passed= "strategy runnning well" if flag else "something went wrong.check detail in strategy executions logs"
                logger.debug(passed)
        logger.info(f"backtest completed for symbol:{i}")
        
    except KeyboardInterrupt as kr:
        logger.info(f"Backetest stopped forcefully")
        print(kr)
        sys.exit(1)
        
        

    except SystemExit as ss:
        logger.debug(f"System intrupted by system exit check all the logs for more information {ss}")
        sys.exit(1)


    except Exception as e :
        retryno+=1
        logger.error(f"Got an exception {e}")
        logger.info(f"restart function again retry:{retryno}")
        scheduelbacktest()
        if retryno>3:
            logger.info(f"retry exceeded max retry allowed ")
            sys.exit(1)

        




if __name__ =="__main":
    scheduelbacktest()

    
