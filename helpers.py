import pprint
from time import mktime
from datetime import datetime
from termcolor import cprint

def logit(name, kind, message):
    """
    :param name: str: <method>.__name__
    :param kind: str: error, warning, info
    :param message: str: will pprint(message)
    :return:
    """
    msg = '\n' + '-' * 80 + '\n' + '{}: {}: {}: {}'.format(datetime.now(), name, kind, pprint.pformat(message))
    cprint(msg, 'green', attrs=['bold'])
