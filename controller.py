from requests import post, get
from requests.exceptions import RequestException
from subprocess import Popen, PIPE
from re import sub
from logging.handlers import RotatingFileHandler
from logging import getLogger, Formatter
from datetime import datetime
from time import sleep

def timestamp():
   ''' Return a timestamp using ISO Format '''

   return datetime.now().isoformat()

def url_get(url, code, log):
    ''' HTTP GET over url and validate return code is the expected '''
    try:
        request = get(url)
        status_code = request.status_code
        if status_code == code:
            log.info('The return code is the expected value')
            return True
        log.info('The return code {} is not the expected value: {}'.format(status_code, code))
        return False
    except (RequestException, Exception) as error:
        log.error('Failed to validate the URL')
        return False 

def notify_slack(url, message, notify, log):
    ''' Notify a message to a URL (using slack webhooks) '''

    if not notify:
        log.warning('Notifications are off')
        return True
    try:
        headers = {'Content-type': 'application/json'}
        notification = post(url, json={'text': message}, headers=headers)
        status_code = notification.status_code
        log.info('Notification completed with code {}'.format(status_code))
    except (RequestException, Exception) as error_:
        log.error('Notification failed; error: {}'.format(error_))
        return False
    else:
        if status_code != 200:
            return False
        return True

def execute(command, log, return_output=None):
    ''' Execute a command in the console '''

    returncode = -1
    try:
        results = {
            'output': None,
            'error': None
        }
        process = Popen(
            command,
            shell=True,
            stdout=PIPE,
            stderr=PIPE
        )
        stdout = sub('\n$', '', process.stdout.read().decode('utf-8'))
        stdout = stdout.split('\\n')
        for item in stdout:
            log.debug(item)
        results['output'], results['error'] = process.communicate()
        returncode = process.returncode
        if results.get('error', None):
            log.error('Execution failed: {}'.format(results['error']))
        log.info('Command: "{}" terminated with status {}'.format(
            command,
            returncode
        ))
    except (OSError, Exception) as error_:
        log.error('Command could not execute; error: {}'.format(error_))
        return False, None, returncode
    else:
        if results['error']:
            return False, None, returncode
        if return_output:
            return True, stdout, returncode
        return True, None, returncode

def set_log(config):
    ''' Set a log using a configuration '''

    handler = RotatingFileHandler(
        config.log['file'],
        maxBytes= config.log['limit'],
        backupCount=config.log['keep']
    )
    handler.setFormatter(Formatter(config.log['format']))

    log = getLogger('deploybot-log')
    log.setLevel(config.log['level'].upper())
    log.addHandler(handler)
    return log

def change_service(service, action, count, log):
    ''' Change a service status using the execute function '''

    command = 'sudo service {} {}'.format(service, action)
    check = 'ps -fea | grep {} | grep -v grep'.format(service)
    execution = None
    log.info('Changing service {} to {}'.format(service, action))
    for commands in (command, check):
        execution = execute(commands, log, True)
        sleep(3)
    if len(execution[1][0]) >= count:
        log.info('Service {} status is: {}'.format(service, action))
        return True
    else:
        log.info('Failed to change status from service: {}'.format(service))
        return False

def levensthein(word_a, word_b):
    ''' Levensthein distance '''

    if word_a == word_b: 
        return 0
    elif len(word_a) == 0: 
        return len(word_b)
    elif len(word_b) == 0: 
        return len(word_a)
    else:
        v0 = [None for i in range(len(word_b) + 1)]
        v1 = [None for i in range(len(word_b) + 1)]
        for i in range(len(v0)):
            v0[i] = i
        for i in range(len(word_a)):
            v1[0] = i + 1
            for j in range(len(word_b)):
                cost = 0 if word_a[i] == word_b[j] else 1
                v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
            for j in range(len(v0)):
                v0[j] = v1[j]
                
        return v1[len(word_b)]
