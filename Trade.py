import subprocess
from pathlib import Path
import os
import stat
import traceback
import pandas as pd
from scipy import signal
currenenv= Path(__file__).resolve().parent.parent
from Bot import env
from  Bot.utility import utility,checkopenorder,startsocket
from Bot.Strategy import bb
from Bot.Broker import Angelsdk as angel
from concurrent.futures import ThreadPoolExecutor
import threading 
import pytz
import sys
import time
import signal
import logging
from pathlib import Path

path = env.currenenv
logerpath=os.path.join(path,'Botlogs/Trade.logs') 
loggerpath= os.path.normpath(logerpath)
# Clear log files larger than 10 MB
def clearlogs():
    for i in Path(f'{path}/Botlogs').glob('*.logs'):
        if i.stat().st_size > 10 * 1024 * 1024:  # 10 MB
            with open(i, 'w'):
                pass  # Clear the file contents
        
misc=utility.misc()
# misc.restartdata()

logger= env.setup_logger(loggerpath)       

threadlist = {}
stop_event = threading.Event()
executor = ThreadPoolExecutor(max_workers=2)

def shutdown_handler(sig, frame):
    print("\nCTRL+C pressed. Stopping all threads...")
    stop_event.set()

    for t in threadlist.values():
        t.join()
    executor.shutdown(wait=False)
    

    print("All threads stopped.")
    sys.exit(0)

import pandas as pd
import random
from datetime import datetime, timedelta
res= misc.angellogin()
if not res:
    logger.error('Please add valid angel credentials in config  file')
    time.sleep(10)
    sys.exit(1)

ANGEL= angel.HTTP(1)
def startprice():
    while not stop_event.is_set():
        try:
                tokenparam= {'NSE':['26000']}

                print("Fetching NIFTY LTP..........................................................................")
                checkltp= ANGEL.get_quotes(tokenparam)
                if checkltp is None:
                    logger.info("LTP fetch failed, retrying... syestem on hold for 30 sec")
                    time.sleep(30)
                    continue
                data= pd.DataFrame([checkltp['data']['fetched'][0]])
                paths= os.path.join(path,'data/feeddata')
                data.to_json(os.path.join(paths,'NIFTY_LTP.json'),orient='records',lines=True,mode='a')

                
                time.sleep(2)
        except KeyboardInterrupt as key:
            logger.info("keyboard intrupted stopping the trade bot ")
            stop_event.set()
            sys.exit(1)
            
        except Exception as e :
            logger.error(e,exc_info=True)
            continue
        time.sleep(300)  # Wait for 5 minutes before fetching again

def generate_random_candles(
        start_price=100,
        count=50,
        start_time=None
    ):
    """
    Generates random 5-minute OHLC candles

    Columns: updated_at, open, high, low, close
    """

    if start_time is None:
        start_time = datetime.now(tz=pytz.timezone('Asia/Kolkata'))

    candles = []
    price = start_price

    for i in range(count):
        open_price = price

        # random % move
        move = random.uniform(-1.5, 1.5)
        close_price = open_price * (1 + move / 100)

        high = max(open_price, close_price) * (1 + random.uniform(0.0, 0.5) / 100)
        low  = min(open_price, close_price) * (1 - random.uniform(0.0, 0.5) / 100)

        candle_time = start_time + timedelta(minutes=5 * i)

        candles.append({
            "updated_at": candle_time,
            "open": round(open_price, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "close": round(close_price, 2)
        })

        price = close_price   # next candle opens at previous close

    return pd.DataFrame(candles)



def mainfunc_safe(token):
    try:
        mainfunc(token)
    except Exception as e:
        print(f"\n❌ THREAD CRASHED for {token}")
        logger.error(f"Thread crashed for token {token}: {e}")
        traceback.print_exc()
    
def mainfunc(TOKEN):
    prevsignal=False

    while not stop_event.is_set():
        try :
            clearlogs()
            print(f"start trade for token {TOKEN}")
        
            settings= misc.loadsettings()
            tokenlist= misc.loadtokenlist()
            tokenlist['token'] = tokenlist['token'].astype(str).str.strip()
            TOKEN = str(TOKEN).strip()

            tokenfilter= tokenlist[tokenlist['token']==TOKEN]
            
            tmf= settings['tmf']

            if tmf:
                
                # tokenparam= {'NSE':['26000']}

                # checkltp= ANGEL.get_quotes(tokenparam)
                checkltp= pd.read_json(os.path.join(path,'data/feeddata/NIFTY_LTP.json'),lines=True).iloc[-1]
                if checkltp.empty:
                    logger.info("LTP fetch failed, retrying... syestem on hold for 30 sec")
                    time.sleep(30)
                    continue
                
                ltp = checkltp['ltp']
                time.sleep(3)
                
                if (not tokenfilter.empty ) and (ltp>tokenfilter['strike'].iloc[0]) and (ltp<tokenfilter['strike'].iloc[0]+99):
                   
                    logger.info(f"start trade for token {TOKEN}")

                    # data= generate_random_candles()
                    data = angel.HTTP(1).candels('NFO',TOKEN,settings['tmf'])
                    
                    start_time = pd.Timestamp('09:15').time()
                    end_time = pd.Timestamp('15:25').time()
                    timezon= pytz.timezone('Asia/Kolkata')
                    data['updated_at'] = pd.to_datetime(data['updated_at'])
                    
                    data['buy_final']=False
                    data['sell_final']=False
                    data['buyconditions']=False
                    data['sellconditions']=False
                    data['symbol']= tokenfilter['symbol'].iloc[0]
                    data['token']= TOKEN
                    stat=bb.strategy()
                    res=stat.main(data,settings['paper'],tokenfilter['lotsize'].iloc[0],prevsignal,ANGEL)
                    prevsignal=res
            if datetime.now(tz=pytz.timezone('Asia/Kolkata')).time() > pd.Timestamp('15:30').time():
                command= 'sudo systemctl stop tradingbot.service'
                os.system(command)
                logger.info('Market closed stopping the trade bot service')
                
                # logger.info(f"start trade for token {TOKEN}")
                # print(f"start trade for token {TOKEN}")
                
               # else:
                #     logger.info(f"LTP {ltp} not in range for trading for token {TOKEN}")
                #     print(f"LTP {ltp} not in range for trading for token {TOKEN}")
        except KeyboardInterrupt as key:
            logger.info("keyboard intrupted stopping the trade bot ")
            stop_event.set()
            sys.exit(1)
            
        except Exception as e :
            logger.error(e,exc_info=True)
            continue








if __name__=='__main__':
        

                threadlsit= {}
                
                print("""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""")
                signal.signal(signal.SIGINT, shutdown_handler)
                sys.stdout.write("Angel Login Initiated \n")
                tokenlist,totalstrike= misc.gettoken('NIFTY',ANGEL)
                if not  totalstrike:
                     logger.error('the angel broker is not responding please try later after 10 min')
                     time.sleep(10)
                     sys.exit(1)

                print("Starting Trade Bot....Press Ctrl+C to stop")
                
                for TOKEN in totalstrike:

                    
                    
                    threadlsit[TOKEN]= threading.Thread(target=mainfunc_safe,args=(TOKEN,))
                    threadlsit[TOKEN].start()
                    time.sleep(2)
                
                
                executor.submit(
                    checkopenorder.checkopenorder,ANGEL)
                
                executor.submit(startprice)

              
                
                while True:
                    time.sleep(1)
      
                




        



