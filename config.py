from pathlib import Path

# service variables
home = Path.home()
environment = '[environment: dev/test/...]'
check_url = 'http://localhost/healthcheck/'
service = '[service name (init.d script)]'

# logging dictionary, using rotating handler
log = {
    'level': 'debug',
    'file': './log/deploybot.log',
    'format': '%(levelname) -10s %(asctime)s %(module)s:%(lineno)s %(funcName)s %(message)s',
    'limit':  1000000,
    'keep': 5
}

# slack url for incoming webhooks
slack = {
    'notify': True
    'url': 'https://hooks.slack.com/services/[slack url]'
}

# deploy variables
deploy_type = '[green/blue/None]'
deploy_path = '{}/[git repository name]'.format(home)

deploy_script = ' '.join([
    'cd {};',
    '/usr/local/bin/ansible-playbook',
    '-i ansible/inventories/{}'.format(deploy_path, environment.lower()),
    'ansible/[service playbook .yml]'
])

# options for your playbook
deploy_commands = {
  '<{}-deploy>'.format(deploy_type): ''
}
