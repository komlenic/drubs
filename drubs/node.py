import subprocess
from fabric.state import env
from fabric.operations import local
from fabric.api import lcd, cd, run, task, hosts, quiet, runs_once
from os.path import isfile, dirname, basename, normpath, exists as local_exists
from os import getcwd
from fabric.contrib.files import exists as remote_exists
from fabric.colors import red, yellow, green, cyan
from pprint import pprint


class Node(object):

  def __init__(self, env):
    self.env = env

    # Get server_hostname from server on which command is being run.
    # This is done outside of fabric's usual "run" or "local" commands (because
    # it isn't known yet at this point whether the command is being run locally
    # or remotely).
    output = subprocess.Popen(["hostname", "-f"], stdout=subprocess.PIPE)
    hostname = output.stdout.read().strip()

    # If the 'server_hostname' for this node, from the project.yml file
    # is equal to the hostname from 'hostname -f' (obtained above), then set/use
    # local commands.
    if env.host == hostname:
      env.host_is_local = True
      env.cd = lcd
      env.exists = local_exists
    else:
      env.host_is_local = False
      env.cd = cd
      env.exists = remote_exists
      env.forward_agent = True

    # Get node name from host.
    env.node_name = self.get_node(env.config['nodes'], env.host)

    # Set env.node, a shortcut.
    env.node = env.config['nodes'][env.node_name]


  def drubs_run(self, cmd, *args, **kwargs):
    '''
    Effectively wraps fabric's run() and local() into a single function.

    This eliminates the need for tedious if/else logic when a run/local function
    call is needed: drubs_run calls the appropriate fabric function, run() or
    local(), based on whether the host being executed on is local or remote.

    Note that all args and kwargs available to run() and local() are passed
    through this function to their respective function, however, any invalid
    kwargs are stripped.

    The primary example of this is the 'capture' kwarg, only accepted by the
    local() function.  In order to capture output from local and remote commands
    branching logic based on local/remote host would have to be used.  With
    drubs_run(), a single command can be written, using 'capture=True', which
    will apply to any local() calls, but be stripped from any run() calls.
    '''
    if env.host_is_local:
      return local(cmd, *args, **kwargs)
    else:
      kwargs.pop('capture', None)
      return run(cmd, *args, **kwargs)


  def get_node(self, d, host):
    '''
    Recursive function to determine node name from hostname.
    '''
    for k,v in d.items():
      if isinstance(v,dict):
        p = self.get_node(v,host)
        if p:
          return k
      elif v == host:
        return k


  def init(self):
    '''
    Creates stubbed-out versions of project configuration files.
    '''
    pass


  def status(self):
    self.drubs_run('uname')


  def install(self):
    '''
    Installs a site/project, based on .make and .py configuration files.
    '''
    pass


  def update(self):
    '''
    Updataes a site/project, based on .make and .py configuration files.
    '''
    pass


  def disable(self):
    '''
    Disables a site using Drupal's maintenance mode.
    '''
    pass


  def enable(self):
    '''
    Enables a site by disabling Drupal's maintenance mode.
    '''
    pass


  def destroy(self):
    print(cyan('Removing database...'))
    self.drubs_run('mysql -h' + env.node['db_host'] + ' -u' + env.node['db_user'] + ' -p' + env.node['db_pass'] + ' -e "DROP DATABASE IF EXISTS ' + env.node['db_name'] + ';"')
    print(cyan('Removing files...'))
    if env.exists(env.node['site_root']):
      self.drubs_run('chmod -R u+w ' + env.node['site_root'])
      self.drubs_run('rm -rf ' + env.node['site_root'])
    else:
      print(yellow('Site root %s does not exist.  Nothing to remove.' % env.node['site_root']))


  def var_dump(self):
    '''
    Prints the global fabric env dictionary.
    '''
    pprint(env)
