import Bot.env
from  Bot.utility import utility
from Bot.Strategy import bb
from concurrent.futures import ThreadPoolExecutor
import threading 

misc=utility.misc()

def mainfunc(symbol):
    while True:
        settings= misc.loadsettings()
        tmf= settings['tmf']
        data =misc.getmergedata(symbol)
        data= misc.buildcandels(data,tmf,False)
        stat=bb.strategy()
        stat.main(data,False)








if __name__=='__main__':
    threadlsit= {}
    symbols = misc.getsymbols()

    for symbol in   symbols['tradingsymbol'] :
        threadlsit[symbol]= threading.Thread(target=mainfunc,args=(symbol,))
        threadlsit[symbol].start()
        threadlsit[symbol].join()
        


