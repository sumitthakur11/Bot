from Bot import env
from utility import misc
import os
import sys

path = env.currenenv
logpath= os.path.join(path,'botlogs/utility.logs')
logpath= os.path.normpath(logpath)
# logpath= os.path.join(logpath,'Angelbroker.logs')
print(logpath,'logpath')



logger=env.setup_logger(logpath)
retryno=0

def startsocket(self):
    try :

        misc.startwebsocket()
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

        startsocket()



if __name__ == '__main__':
    try:
        startsocket()
    except Exception as e:
        print(e)