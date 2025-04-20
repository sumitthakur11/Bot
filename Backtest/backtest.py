
from Bot import env
from Bot.Strategy import bb as strategy
from Bot.utility import utility
from Bot.Broker import Angelsdk

import logging
import os 
import sys
import pandas as pd 
import datetime
import time
path= env.currenenv
logpath= os.path.join(path,'Botlogs/backtest.logs')
logpath= os.path.normpath(logpath)
# logpath= os.path.join(logpath,'Angelbroker.logs')
print(logpath,'logpath')
logger=env.setup_logger(logpath)

retryno= 0
stat=strategy.strategy()
misc= utility.misc()


def scheduelbacktest(): 
    try:
        misc= utility.misc()
        symbollist=misc.getsymbols()
        print(symbollist)
        datalist= []
        login= Angelsdk.SMARTAPI(1)
        login.smartAPI_Login()
        for i in symbollist['symbol']:
            logger.info(f"backtest starts for symbol:{i}")
            data = misc.getdata(i,test=True)
            print(len(data))
            data= misc.buildcandels(data,'1min',True)
            print(len(data))
            for j in range(len(data)):
                datadict={}
                datadict['updated_at']= data['updated_at'].iloc[j]
                datadict['Close']= data['close'].iloc[j]
                datadict['OI']= data['OI'].iloc[j]
                datadict['Volume']= data['volume'].iloc[j]
                datalist.append(datadict)
                datafin= pd.DataFrame(datalist)
                datafin= misc.buildcandels(datafin,'5min',True)
                start_time = pd.Timestamp('09:15').time()
                end_time = pd.Timestamp('15:25').time()
                data = data[(data['updated_at'].dt.time >= start_time) & (data['updated_at'].dt.time <= end_time)]
                data= data.dropna()
                data= data.reset_index()


                flag=stat.main(data,True)
                misc.checkpnlbox(float(data['close'].iloc[j]))
                misc.closeorder()
                passed= "strategy runnning well" if {flag} else "something went wrong.check detail in strategy executions logs"
                logger.debug(passed)
        logger.info(f"backtest completed for symbol:{i}")
        generatereport()
    except KeyboardInterrupt as kr:
        logger.info(f"Backetest stopped forcefully")
        print(kr)
        generatereport()
        sys.exit(1)
        
        

    except SystemExit as ss:
        logger.debug(f"System intrupted by system exit check all the logs for more information {ss}")
        generatereport()
        sys.exit(1)


    except Exception as e :
        global retryno
        retryno+=1
        print(retryno)
        logger.error(f"Got an exception {e}",exc_info=True)
        logger.info(f"restart function again retry:{retryno}")
        if retryno>3:
        
            logger.info(f"retry exceeded max retry allowed ")
            generatereport()
            sys.exit(1)

            retryno= 0

        scheduelbacktest()

        
def generatereport():
    orderdata =misc.orderobject()
    date= int(time.time()*1000)
    reportpath= os.path.join(path,f'Backtestresult/{date}.csv')
    orderdata.to_csv(reportpath)
    logger.info('Backtest Report Generated Sucessfully')

    return generatereport

def exitbackest():
    symbollist=misc.getsymbols()

    for i in symbollist['symbol']:
        logger.info(f"backtest starts for symbol:{i}")
        data = misc.getdata(i,test=True)
        data= misc.buildcandels(data,'1min',True)
        print(data['updated_at'])
        print(data.head())
        print(type(data.index))
        print(data.index)
        start_time = pd.Timestamp('09:15').time()
        end_time = pd.Timestamp('15:25').time()
        data = data[(data['updated_at'].dt.time >= start_time) & (data['updated_at'].dt.time <= end_time)]
        data= data.dropna()
        data= data.reset_index()

        data=stat.finalconditons(data)
        data['averageprice']= 0
        data['entry']= False
        data['side']= ''
        data['exit']= False
        data['sellprice']= 0
        data['pnl']=0
        data =misc.checkpnlbox1(data)
        date= int(time.time()*1000)
    reportpath= os.path.join(path,f'Backtestresult/fast{date}.csv')
    data.to_csv(reportpath)

    return data










if __name__ =="__main__":
    data =exitbackest()
    scheduelbacktest()

    
