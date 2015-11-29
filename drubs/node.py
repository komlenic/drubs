import subprocess
import time
from fabric.state import env
from fabric.operations import local, put
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

    # Start a timer, used later by print_elapsed_time().
    env.start_time = time.time()


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
    self.print_elapsed_time()


  def status(self):
    self.drubs_run('uname')
    self.print_elapsed_time()


  def install(self):
    '''
    Installs a site/project, based on .make and .py configuration files.
    '''
    self.provision()
    self.make()
    self.site_install()
    self.print_elapsed_time()


  def update(self):
    '''
    Updataes a site/project, based on .make and .py configuration files.
    '''
    self.print_elapsed_time()


  def disable(self):
    '''
    Disables a site using Drupal's maintenance mode.
    '''
    print(cyan('Disabling site...'))
    with env.cd(env.node['site_root']):
      self.drush('vset maintenance_mode 1')
      self.drush('cc all')
    self.print_elapsed_time()


  def enable(self):
    '''
    Enables a site by disabling Drupal's maintenance mode.
    '''
    print(cyan('Enabling site...'))
    with env.cd(env.node['site_root']):
      self.drush('vset maintenance_mode 0')
      self.drush('cc all')
    self.print_elapsed_time()


  def destroy(self):
    print(cyan('Removing database...'))
    self.drubs_run('mysql -h%s -u%s -p%s -e "DROP DATABASE IF EXISTS %s";' % (
      env.node['db_host'],
      env.node['db_user'],
      env.node['db_pass'],
      env.node['db_name'],
    ))
    print(cyan('Removing files...'))
    if env.exists(env.node['site_root']):
      self.drubs_run('chmod -R u+w %s' % (env.node['site_root']))
      self.drubs_run('rm -rf %s' % (env.node['site_root']))
    else:
      print(yellow('Site root %s does not exist.  Nothing to remove.' % (
        env.node['site_root'],
      )))
    self.print_elapsed_time()


  def var_dump(self):
    '''
    Prints the global fabric env dictionary.
    '''
    pprint(env)
    self.print_elapsed_time()


  def drush(self, cmd):
    '''
    Runs the specified drush command.
    '''
    if env.verbose:
      cmd += ' -v'
    if env.debug:
      cmd += ' -d'
    with env.cd(env.node['site_root']):
      self.drubs_run('drush %s -y' % (cmd))


  def provision(self):
    '''
    Creates database and site root.
    '''
    print(cyan('Creating database...'))
    self.drubs_run('mysql -h%s -u%s -p%s -e "DROP DATABASE IF EXISTS %s;CREATE DATABASE %s;"' % (
      env.node['db_host'],
      env.node['db_user'],
      env.node['db_pass'],
      env.node['db_name'],
      env.node['db_name'],
    ))
    print(cyan('Creating site root location...'))
    if env.exists(env.node['site_root'] + '/sites/default'):
      self.drubs_run('chmod -R u+w %s/sites/default' % (env.node['site_root']))
      self.drubs_run('rm -rf %s' % (env.node['site_root']))
    self.drubs_run('mkdir -p %s' % (env.node['site_root']))


  def make(self):
    '''
    Runs drush make using the make file specified in project configs.
    '''
    print(cyan('Beginning drush make...'))
    with env.cd(env.node['site_root']):
      if env.exists(env.node['site_root'] + '/sites/default'):
        self.drubs_run('chmod 775 sites/default')
      make_file = env.config_dir + '/' + env.node['make_file']

      if env.host_is_local:
        make_file = env.config_dir + '/' + env.node['make_file']
        self.drush('make --working-copy --no-gitinfofile --no-cache %s' % (
          make_file,
        ))
      else:
        # Copy drush make file for the node to /tmp on the node.
        put(make_file, '/tmp')
        # Run drush make.
        self.drush('make --working-copy --no-gitinfofile --no-cache /tmp/%s' % (
          env.node['make_file'],
        ))
        # Remove drush make file from /tmp on the node.
        self.drubs_run('rm -rf /tmp/%s' % (env.node['make_file']))


  def site_install(self):
    '''
    Runs drush site install.
    '''
    db_url = 'mysql://%s:%s@%s/%s' % (
      env.node['db_user'],
      env.node['db_pass'],
      env.node['db_host'],
      env.node['db_name'],
    )
    with env.cd(env.node['site_root']):
      print(cyan('Beginning drush site-install...'))
      self.drush('si --account-name="%s" --account-pass="%s" --account-mail="%s" --site-mail="%s" --db-url="%s" --site-name="%s"' % (
        env.node['account_name'],
        env.node['account_pass'],
        env.node['account_mail'],
        env.node['site_mail'],
        db_url,
        env.node['site_name'],
      ))
      self.drubs_run('chmod 775 sites/default/files')


  def print_elapsed_time(self):
    '''
    Prints the elapsed time.
    '''
    seconds = time.time() - env.start_time
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print(cyan("Elapsed time: %dh:%02dm:%02ds" % (h, m, s)))
