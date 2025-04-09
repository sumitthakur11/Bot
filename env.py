import os 
import sys
try :

    abspaths=os.environ['VIRTUAL_ENV']
    currenenv= os.path.abspath(abspaths)


except Exception as e:
    print('>>>>>>>>>>>Looks like virtual enviroment is not activated/created.')
    print('- Kindly create New Virtual enviroment and install  all packages mentioned in  requirements.text <<<<<<<< ')
    print('- Kindly activate Virtual enviroment <<<<<<<< ')
    print("- Ensure You Have pip Installed- Make sure you have pip installed in your environment (it comes with Python by default). You can check by running:pip --version")
    print("- Activate Your Virtual Environment (if needed)- If you're using a virtual environment, activate it first. For example:- On Windows:./venv/Scripts/activate")
    print("- On macOS/Linux:source venv/bin/activate")
    print("- Install Dependencies")
    print("Use pip to install all the packages listed in requirements.txt:pip install -r requirements.txt")
    print('- Verify Installation')
    print('Once the installation is complete, ensure the packages are installed by running: pip list')
    sys.exit(1)






import pandas as pd
import json

def defaultset():
    try:
        retryno= 0


    
        configpath= os.path.join(currenenv,'config/config.json')
        configpath= os.path.normpath(configpath)

        if not os.path.exists(configpath):
            print('creating credentials default settings')

            defaultsettings= dict()
            defaultsettings['strategy']={"BBLEN":14,
                                        "BBSTDEVE":2.1 ,
                                        "trend_period":365,
                                        "vol_filter_length":15,
                                        "vol_ma_length":10,
                                        "trail_stop_pct":0.002,
                                        "trail_offset_pct":0.002,
                                        "sl_pct":0.001,
                                        "tp_pct":0.001
                                        }
            defaultsettings['Angelcred']={
                "api_key":"",
                "username":"",
                "pwd":"",
                "token":""

            }
            obj= open(configpath,'w')
            obj= json.dump(defaultsettings,obj,indent=6)
            print(f"- Path to change default settings and add Broker configuration to get Ltp feeds  {configpath}")

        print(f"- Path to change default settings and add Broker configuration to get Ltp feeds  {configpath}")
    except Exception as e:
        retryno+=1 
        print(e)
        defaultset()
        if retryno>3:
            sys.exit(1)
        



def defaultcsv():
    print("- creating required files")
    orderpath= "data/liveorderdata/orderdata.csv"
    orderpath= os.path.join(currenenv,orderpath)
    orderpath= os.path.normpath(orderpath)

    if not os.path.exists(orderpath):
        orderdata = pd.DataFrame(columns=['AccountNo','Entrytime','Broker','Side','Buyorderid','Symbol','Token','Status','Ltp','Qty','AveragePrice','Sellorderid','Sellprice','TargetHit','Slhit','Tslhit','Exittime','Target','Trail','Sl','Backtest','Transactiontype','Order_type','Exchange','Pnl'],dtype='object')
        orderdata.to_csv(orderpath)
    accountpath= f"config/account.csv"
    accountpath= os.path.join(currenenv,accountpath)
    accountpath= os.path.normpath(accountpath)
    
    if not os.path.exists(accountpath):
        account = pd.DataFrame(columns=['AccountNo','Apikey','Secret','Password','Token'],dtype='object')
        account.to_csv(accountpath)
        print("- creating account csv. Please add your upstox account in requied format")
        print("- Kindly Do Not Change The foramts of any files")
    print("- path of files are as follows: ")
    print(f"- Path for check orderbook  {orderpath}")
    print(f"- Path for update all upstox account details  {accountpath}")


          
          
    

    

    

listpath= ['data/backtestdata','data/db','data/feeddata',
           'data/liveorderdata','data/testdata','config','Broker','Botlogs','Backtestresult']
            
for i in listpath:
    dirpath=os.path.join(currenenv,i)
    dirpath= os.path.normpath(dirpath)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
        print(f'creating  dir {i}')
    else:
        pass
    
defaultset()
defaultcsv()

import logging

def setup_logger(logpath):
    logger = logging.getLogger(logpath)  
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(logpath)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%d-%m-%y %H:%M:%S")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

