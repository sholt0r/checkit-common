import logging

class ColourFormatter(logging.Formatter):

    # ANSI codes are a bit weird to decipher if you're unfamiliar with them, so here's a refresher
    # It starts off with a format like \x1b[XXXm where XXX is a semicolon separated list of commands
    # The important ones here relate to colour.
    # 30-37 are black, red, green, yellow, blue, magenta, cyan and white in that order
    # 40-47 are the same except for the background
    # 90-97 are the same but "bright" foreground
    # 100-107 are the same as the bright ones but for the background.
    # 1 means bold, 2 means dim, 0 means reset, and 4 means underline.

    LEVEL_COLOURS = [
        (logging.DEBUG, '\x1b[40;1m'),
        (logging.INFO, '\x1b[34;1m'),
        (logging.WARNING, '\x1b[33;1m'),
        (logging.ERROR, '\x1b[31m'),
        (logging.CRITICAL, '\x1b[41m'),
    ]

    FORMATS = {
        level: logging.Formatter(
            f'\x1b[30;1m%(asctime)s\x1b[0m {colour}%(levelname)-8s\x1b[0m \x1b[38;2;250;149;73m%(name)s\x1b[0m %(message)s',
            '%Y-%m-%d %H:%M:%S',
        )
        for level, colour in LEVEL_COLOURS
    }

    def format(self, record):
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[logging.DEBUG]

        # Override the traceback to always print in red
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f'\x1b[31m{text}\x1b[0m'

        output = formatter.format(record)

        # Remove the cache layer
        record.exc_text = None
        return output

def setup_logger(logger_name=__name__, log_level=logging.DEBUG):
    """
    Sets up and returns a logger with the given name and log level.
    The logger will have console output with colorized messages.
    
    Parameters:
    -----------
    logger_name : str, optional
        The name of the logger. If None, it defaults to the module's __name__.
    
    log_level : int, optional
        The logging level for the logger and the handler. 
        Default is logging.DEBUG, but can be set to any valid logging level.
    
    Returns:
    --------
    logging.Logger
        A logger instance configured with the specified log level and colorized output.
    """

    if logger_name is None:
        logger_name = __name__

    logger = logging.getLogger(logger_name)
    
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        handler.setLevel(log_level)

        formatter = ColourFormatter()
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.setLevel(log_level)

    return logger