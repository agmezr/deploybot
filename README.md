# Deploybot
---


Deploy bot is a simple script made to be run by any service or a cron so you can automate a deployment using a simple approach: **wrap your ansible playbook execution and notify the results via slack **.
This is no substitution for any specific service, it is more of a way to glue components together. You can clone this repository in a host where you need automation or like me, use it in aws by adding it's cloning and crontab insertion on your main bootstrap script.

## Dependencies:

 * Python 3.6
 * Ansible 2.4
 * A Slack incoming webhook (optional)
 * Git
 * Virtualenv (desired)
