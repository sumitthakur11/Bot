import os 
print(os.environ)
try :

    abspaths=os.environ['VIRTUAL_ENV']
    currenenv= os.path.abspath(abspaths)


except Exception as e:
    print('Looks virtual enviroment is not activated. Kindly Activate Python Virtual environment or  Add enviroment path manually in config file under the field of env')
    currenenv= os.path.abspath("C:/Users/sumit/Bot")

print(currenenv)




import logging

def setup_logger(logpath):
    # Create a custom logger
    logger = logging.getLogger(logpath)  # Use the file path as the logger name
    logger.setLevel(logging.DEBUG)

    # Create a file handler
    file_handler = logging.FileHandler(logpath)
    file_handler.setLevel(logging.DEBUG)

    # Define the formatter
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%d-%m-%y %H:%M:%S")
    file_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(file_handler)

    return logger

# Example usage in different files
# logpath = "logfile1.log"
# logger1 = setup_logger(logpath)
# logger1.debug("This is a debug message from file 1.")

# logpath = "logfile2.log"
# logger2 = setup_logger(logpath)
# logger2.info("This is an info message from file 2.")