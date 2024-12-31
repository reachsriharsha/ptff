import logging

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# Create a console handler and set the formatter
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
# Get the root logger and set its level
logger = logging.getLogger()
logger.setLevel(logging.INFO) 
# Add the console handler to the logger
logger.addHandler(console_handler)

'''
# Log messages
logger.debug('This is a debug message')
logger.info('This is an info message')
logger.warning('This is a warning message')
logger.error('This is an error message')
logger.critical('This is a critical message')
'''
