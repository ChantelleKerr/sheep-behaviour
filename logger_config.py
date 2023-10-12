import logging
import sys
import os
from functools import wraps

def app_root_path():
    """Get the root path of the application (script or packaged executable)"""
    if getattr(sys, 'frozen', False):  # The application is frozen (compiled)
        return os.path.dirname(sys.executable)
    else:  # Running in a normal Python environment
        return os.path.dirname(os.path.abspath(__file__))

log_file_path = os.path.join(app_root_path(), 'app.log')

# Setup the basic logging configuration
logging.basicConfig(filename=log_file_path, level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def get_logger(name):
    """Return a logger instance for the specified name (typically the module's name)."""
    return logging.getLogger(name)

def log_func_call(level=logging.INFO):
    """Decorator to log the start and end of a function call with a specified logging level."""
    def actual_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            logger.log(level, f'{func.__name__} started')
            try:
                result = func(*args, **kwargs)
                logger.log(level, f'{func.__name__} finished')
                return result
            except Exception as e:
                logger.error(f'Error in {func.__name__}: {str(e)}', exc_info=True)
                raise  # Re-raise the exception to handle it in the main application or let it propagate
        return wrapper
    return actual_decorator
