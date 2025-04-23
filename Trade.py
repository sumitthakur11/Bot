import subprocess
from pathlib import Path
import os
import stat
import pandas as pd
currenenv= Path(__file__).resolve().parent.parent

try:
    from Bot import env
except ImportError as e:
    command= f"{str(currenenv)}/Bot/env.py"
    command= os.path.join(currenenv,"Bot/env.py")
    command= os.path.normpath(command)
    subprocess.run(["python3",command])


from  Bot.utility import utility
from Bot.Strategy import bb
from concurrent.futures import ThreadPoolExecutor
import threading 
import pytz
path = env.currenenv
logerpath=os.path.join(path,'Botlogs/Trade.logs') 
loggerpath= os.path.normpath(logerpath)
misc=utility.misc()
logger= env.setup_logger(loggerpath)       



def mainfunc(symbol):
    while True:
        try :

            settings= misc.loadsettings()
            tmf= settings['tmf']
            data =misc.getmergedata(symbol)
            print(len(data))


            start_time = pd.Timestamp('09:15').time()
            end_time = pd.Timestamp('15:25').time()
            timezon= pytz.timezone('Asia/Kolkata')
            data['updated_at'] = data['updated_at'].dt.tz_localize('UTC')
            data['updated_at']= data['updated_at'].dt.tz_convert('Asia/Kolkata') 
            data = data[(data['updated_at'].dt.time >= start_time) & (data['updated_at'].dt.time <= end_time)]
            data= data.dropna() 
            data= data.reset_index()
            print(data.iloc[0])
            print(data.iloc[-1])

            data= misc.buildcandels(data,tmf,False)
            stat=bb.strategy()
            stat.main(data,False)
        except Exception as e :
            logger.error(e,exc_info=True)
            






if __name__=='__main__':
    threadlsit= {}
    symbols = misc.getsymbols()

    for symbol in   symbols['tradingsymbol'] :

        threadlsit[symbol]= threading.Thread(target=mainfunc,args=(symbol,))
        threadlsit[symbol].start()
        threadlsit[symbol].join()
        


