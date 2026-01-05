from Bot import env
from Bot.utility import utility
import os
import sys

path = env.currenenv
logpath= os.path.join(path,'Botlogs/utility.logs')
logpath= os.path.normpath(logpath)
print(logpath,'logpath')



logger=env.setup_logger(logpath)
retryno=0

def checkopenorder(ANGEL=None):
    while True:
        try :
            misc= utility.misc()
                
            misc.closeorder(ANGEL=ANGEL)
            misc.checkpnlbox(ANGEL=ANGEL)

        except KeyboardInterrupt as key:
            logger.info(f"keyboard intrupted stopping the quode feed ")
            sys.exit(1)
        except Exception as e:
            global retryno
            retryno+=1
            print(retryno)
            logger.error(f"Got an exception {e}",exc_info=True)
            logger.info(f"restart function again retry:{retryno}")
            if retryno>3:
            
                logger.info(f"retry exceeded max retry allowed ")
                retryno= 0
                sys.exit(1)

            checkopenorder()



if __name__ == '__main__':
    checkopenorder()
    