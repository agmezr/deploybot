import config
from controller import timestamp, set_log, levensthein
from controller import change_service, execute
from controller import url_get, notify_slack

if __name__ == '__main__':
    ''' Deployment logic '''

    log = set_log(config)
    log.info('Starting execution')

    # setting variables
    home = config.home
    environment = config.environment.lower()
    service = config.service
    notify = config.slack['notify']
    slack_url = config.slack['url']
    deploy_path = config.deploy_path
    can_deploy = False
    last_hash = None
    options = None

    # git pull
    command = 'cd {}; git pull origin master'.format(deploy_path)
    execute(command, log)

    command = 'cd {}; git log --format="%H|%s" | head -1'.format(deploy_path)
    git_log = execute(command, log, True)[1][0]

    if git_log:
        git_hash = git_log.split('|')[0]
        git_comment = git_log.split('|')[1]
        log.debug('Last commit: {}'.format(git_log))
        match = False
        typo = (False, None)
        for keyword in config.deploy_commands:
            if keyword in git_comment:
                options = config.deploy_commands[keyword]
                match = True
                break
            else:
                word = '<{}>'.format(git_comment.split('<')[-1].split('>')[0])
                if 0 < levensthein(keyword, word) <= 3:
                    typo = (True, keyword)
        if match:
            try:
                with open('.indeploy', 'r') as f:
                    last_hash = f.read().replace('\n', '')
                if not last_hash or (git_hash not in last_hash):
                    can_deploy = True
                    with open( '.indeploy', 'w') as f:
                        f.write(git_hash)
            except (IOError, Exception) as error_:
                log.error('Failed to open lock file')
        elif (typo[0] and (git_hash not in last_hash)):
            notify_slack(
                url,
                (
                    'A typo was identified for {} command. If this is truth,'
                    ' please fix your commit message and push the change again'
                ).format(typo[1]),
                notify,
                log
            )

    log.debug('Can deploy: {}'.format(can_deploy))

    # If deploy is feasible, execute the playbook
    if can_deploy:
        stop = change_service(service, 'stop', 0, log)
        if stop:
            notify_slack(
                url,
                '{} service stopped'.format(environment.upper()),
                notify,
                log
            )
            command = ' '.join([
                config['deploy_script'],
                options
            ])
            log.debug('Executing: {}'.format(command))

            execution, result, returncode = execute(command, log)
            if execution and returncode == 0:
                start = change_service(service, 'start', 1, log)
                notify_slack(
                    url,
                    'Deploy terminated at {}'.format(timestamp()),
                    notify,
                    log
                )
                if start:
                    notify_slack(
                        url,
                        'Deploy {} succeeded, service is up'.format(git_hash),
                        notify,
                        log
                    )
                    url_status = url_get(config.check_url, 200, log)
                    if url_status == True:
                        notify_slack(
                            url,
                            'Service validated successfully',
                            notify,
                            log
                        )
                    else:
                        notify_slack(
                            url,
                            'Service validation failed, please check for exceptions',
                            notify,
                            log
                        )

            else:
                notify_slack(
                    url,
                    'Deploy terminated with errors at {}'.format(timestamp()),
                    notify,
                    log
                )
    log.info('Terminating execution')
