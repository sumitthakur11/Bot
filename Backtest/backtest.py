
from Bot import env
from Bot.Strategy import bb as strategy
from Bot.utility import utility
from Bot.Broker import Angelsdk

import logging
import os 
import sys
import pandas as pd 
path= env.currenenv
logpath= os.path.join(path,'botlogs/backtest.logs')
logpath= os.path.normpath(logpath)
# logpath= os.path.join(logpath,'Angelbroker.logs')
print(logpath,'logpath')
logger=env.setup_logger(logpath)

retryno= 0

def scheduelbacktest(): 
    try:
        misc= utility.misc()
        symbollist=misc.getsymbols()
        print(symbollist)
        datalist= []
        stat=strategy.strategy()
        login= Angelsdk.SMARTAPI(1)
        login.smartAPI_Login()
        for i in symbollist['symbol']:
            logger.info(f"backtest starts for symbol:{i}")
            data = misc.getdata(i,test=True)
            for j in range(len(data)):
                datadict={}
                datadict['updated_at']= data['updated_at'].iloc[j]
                datadict['Close']= data['Close'].iloc[j]
                datadict['OI']= data['OI'].iloc[j]
                datadict['Volume']= data['Volume'].iloc[j]
                datalist.append(datadict)
                datafin= pd.DataFrame(datalist)
                datafin= misc.buildcandels(datafin,'5min',True)
                print(datafin.iloc[-1])
                print(float(data['Close'].iloc[j]))
                flag=stat.main(datafin,True)
                misc.checkpnlbox(float(data['Close'].iloc[j]))
                misc.closeorder()
                passed= "strategy runnning well" if {flag} else "something went wrong.check detail in strategy executions logs"
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
        global retryno
        retryno+=1
        print(retryno)
        logger.error(f"Got an exception {e}",exc_info=True)
        logger.info(f"restart function again retry:{retryno}")
        if retryno>3:
        
            logger.info(f"retry exceeded max retry allowed ")
            sys.exit(1)

            retryno= 0

        scheduelbacktest()

        



scheduelbacktest()

if __name__ =="__main":
    scheduelbacktest()

    
