import os 

currenenv= os.path.abspath("C:/Users/sumit/BotKapil")


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