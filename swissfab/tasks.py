from fabric.api import local, run, task, env
from swissfab.tools import *

import os


@task
def vagrant():
    """
    configures host and user to connect to you local vagrant instance
    requires to be run from vagrant directory / vagrant command to work
    """
    env.user = 'vagrant'
    env.hosts = ['127.0.0.1:2222']

    key_filename = local('vagrant ssh-config | grep IdentityFile', capture=True).strip().split()[1]
    print "Vagrant ssh key: {0}".format(key_filename)
    env.key_filename = key_filename


@memoized
def remote_home():
    """
    :returns: remote home directory
    """
    return run("echo $HOME")


@task
def remote_pubkey():
    """
    Returns remote pubkey
    """
    run("cat ~/.ssh/id_dsa.pub")


@task
def ssh_keygen():
    """
    SSH key generation - remote
    """
    dsa_filename = os.path.join(remote_home(), '.ssh', 'id_dsa')
    run("ssh-keygen -t dsa -P '' -f %s" % dsa_filename)
    remote_pubkey()


@task
def ipython():
    """
    starts ipython within fabric context
    """
    import IPython
    IPython.embed()


@task
def shell(hostname=None, user=None):
    """
    a shell that opens separate console (on open_shell replacement)
    open_shell does not pass through ctrl+C
    additionally we allow user to use as many as possible keys
    """
    if hostname:
        env.host = hostname
    if user:
        env.user = user

    key_files = get_keyfiles(include_other_pems=True)
    key_args = map(lambda x: "-i {key}".format(key=x), key_files)
    local('ssh -o "ServerAliveInterval 30" {keys} -p {port} {user}@{host}'.format(keys=" ".join(key_args), user=env.user, host=env.host, port=env.port))
