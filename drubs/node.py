import subprocess
import time
import sys
import glob
from fabric.state import env
from fabric.operations import local, put
from fabric.api import lcd, cd, run, task, hosts, quiet, runs_once
from os.path import isfile, dirname, basename, normpath, splitext, exists as local_exists
from os import getcwd
from re import search
from contextlib import contextmanager
from datetime import datetime, timedelta
from fabric.contrib.console import confirm
from fabric.contrib.files import exists as remote_exists
from fabric.colors import red, yellow, green, cyan
from prettytable import PrettyTable
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

    # Set env.files_dir, the absolute path to the project's files dir.
    if env.host_is_local:
      env.files_dir = env.config_dir + '/files'
    else:
      env.files_dir = '/tmp/' + env.config['project_settings']['project_name'] + '/files'

    # Get node name from host.
    env.node_name = self.get_node(env.config['nodes'], env.host)

    # Set env.node, a shortcut.
    env.node = env.config['nodes'][env.node_name]

    # Start a timer, used later by print_elapsed_time().
    env.start_time = time.time()

    # Append the configs directory for the specified project to the python path.
    sys.path.append(env.config_dir)

    # Import attributes/functions from the appropriate config script.
    self.config_script = __import__(splitext(env.node['py_file'])[0])


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


  def status(self):
    self.status_per_node()
    self.print_elapsed_time()


  def install(self):
    '''
    Installs a site/project, based on .make and .py configuration files.
    '''
    self.check_destructive_action_protection()
    self.disable_apache_access()
    self.check_and_create_backup()
    with self.cleanup_on_failure():
      self.put_files()
      self.provision()
      self.make()
      self.preconfigure()
      self.site_install()
      self.postconfigure()
      self.secure()
      self.remove_files()
      # The order/flow below is important.
      self.drush('updb')
      self.drush('cc all')
    if not env.no_backup:
      self.remove_old_backups()
    self.enable_apache_access()
    self.print_elapsed_time()


  def update(self):
    '''
    Updates a site/project, based on .make and .py configuration files.
    '''
    self.disable_apache_access()
    self.check_and_create_backup()
    with self.cleanup_on_failure():
      self.put_files()
      self.make()
      self.postconfigure()
      self.secure()
      self.remove_files()
      # The order/flow below is important.
      self.drush('updb')
      self.drush('cc all')
    if not env.no_backup:
      self.remove_old_backups()
    self.enable_apache_access()
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


  def backup(self):
    '''
    Creates a drush archive dump backup of the site.
    '''
    self.create_backup()
    self.remove_old_backups()
    self.print_elapsed_time()


  def destroy(self):
    self.check_destructive_action_protection()
    self.check_and_create_backup()
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
    if not env.no_backup:
      self.remove_old_backups()
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


  def drush_sql(self, sql):
    '''
    Runs a drush-sql command with the provided sql query.

    This function was historically necessary to be able to write one query that
    could be escaped properly in order to be performed successfully on both
    local and remote nodes.  Between python, fabric, shell, and drush, escaping
    is difficult to grok.

    This function is included as-is for now to accomodate already written config
    files for existing projects, but it should be rewritten when escaping can
    be properly understood.  (Encoding queries with base64 in transit may be
    helpful.)
    '''
    if env.host_is_local:
      sql = sql.replace('"', '\\"')
    else:
      sql = sql.replace('"', '\\\\\"')
    options = str()
    if env.verbose:
      options += ' -v'
    if env.debug:
      options += ' -d'
    with env.cd(env.node['site_root']):
      self.drubs_run(r'drush sql-query "%s" %s -y' % (sql, options))


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
      with env.cd(env.node['site_root']):
        self.drubs_run('chmod u+w sites/default')
        self.drubs_run('ls -A | grep -v ".htaccess.drubs" | xargs rm -rf')
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

      cache_option = str()
      if not env.cache:
        cache_option += ' --no-cache'

      # Remove all modules/themes/libraries to ensure any deleted files are
      # removed.  See: https://github.com/komlenic/drubs/issues/30
      self.drubs_run('rm -rf sites/all/*')

      if env.host_is_local:
        self.drush('make --working-copy --no-gitinfofile %s %s' % (
          cache_option,
          make_file,
        ))
      else:
        # Copy drush make file for the node to /tmp on the node.
        put(make_file, '/tmp/' + env.config['project_settings']['project_name'])
        # Run drush make.
        self.drush('make --working-copy --no-gitinfofile %s /tmp/%s/%s' % (
          cache_option,
          env.config['project_settings']['project_name'],
          env.node['make_file'],
        ))
        # Remove drush make file from /tmp on the node.
        self.drubs_run('rm -rf /tmp/%s/%s' % (
          env.config['project_settings']['project_name'],
          env.node['make_file'],
        ))


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


  def secure(self):
    '''
    Performs some security best-practices.
    '''
    print(cyan('Performing security practices...'))
    with env.cd(env.node['site_root']):
      # Remove all txt files in site root (except robots.txt)
      self.drubs_run('ls | grep .txt | grep -v "robots.txt" | xargs rm -rf')
      # Ensure restrictive settings on settings.php
      self.drubs_run('chmod 444 sites/default/settings.php')


  def preconfigure(self):
    '''
    Runs the pre() config script from the node's specified py_file setting.
    '''
    self.config_script.pre()


  def postconfigure(self):
    '''
    Runs the post() config script from the node's specified py_file setting.
    '''
    self.config_script.post()


  def put_files(self):
    '''
    Copies the 'files' directory to /tmp location.
    '''
    print(cyan('Copying project files...'))
    self.drubs_run('mkdir -p /tmp/%s/files' % (env.config['project_settings']['project_name']))
    if env.host_is_local:
      self.drubs_run('cp -R %s/files/ /tmp/%s/' % (
        env.config_dir,
        env.config['project_settings']['project_name'],
      ))
    else:
      put(
        '%s/files/' % (env.config_dir),
        '/tmp/%s/' % (env.config['project_settings']['project_name'])
      )


  def remove_files(self):
    '''
    Removes temporarily copied files (if any).
    '''
    print(cyan('Removing project files...'))
    self.drubs_run('rm -rf /tmp/%s' % (env.config['project_settings']['project_name']))


  def disable_apache_access(self):
    '''
    Disables access to site root location.

    Used to temporarily return 503 during site install/update.
    '''
    print(cyan('Temporarily disabling access to site...'))
    self.drubs_run('mkdir -p %s' % (env.node['site_root']))
    if env.host_is_local:
      self.drubs_run('cp %s/templates/htaccess.drubs %s/.htaccess.drubs' % (
        env.drubs_data_dir,
        env.node['site_root'],
      ))
    else:
      put(
        '%s/templates/htaccess.drubs' % (env.drubs_data_dir),
        '%s/.htaccess.drubs' % (env.node['site_root'])
      )


  def enable_apache_access(self):
    '''
    Re-enables access to site root location.

    Used to remove 503 put in place during site install/upgrade.
    '''
    print(cyan('Re-enabling access to site...'))
    if env.exists(env.node['site_root'] + '/.htaccess.drubs'):
      self.drubs_run('rm %s/.htaccess.drubs' % (env.node['site_root']))


  def check_destructive_action_protection(self):
    '''
    Prevents execution if destructive action protection is 'on' for the node.
    '''
    if env.node['destructive_action_protection'] == 'on':

      if self.site_bootstrapped():
        print(red("Destructive action protection is 'on' for node '%s', and '%s' task is potentially destructive. A properly functioning site appears to already exist. Exiting..." % (
          env.node_name,
          env.command,
        )))
        exit(1)

      if self.site_files_exist() or self.site_database_exists():
        print(red("Destructive action protection is 'on' for node '%s', and '%s' task is potentially destructive. An installed site does not appear to be functioning properly, but files OR the site database seem to be present.  For more information, run 'drubs status %s' or 'drubs status all'.  Exiting..." % (
          env.node_name,
          env.command,
          env.node_name,
        )))
        exit(1)

    else:
      if env.no_backup and int(env.node['backup_minimum_count']) == 0 and int(env.node['backup_lifetime_days']) == 0:
        if not env.yes:
          if not confirm(yellow("The requested operation may cause irreversible loss of data or code on node '%s'. The command has been executed using the '--no-backup' option; and 'backup_minimum_count' as well as 'backup_lifetime_days' are set to 0 for node '%s'. Continue?" % (
            env.node_name,
            env.node_name,
          )), default=False):
            print(cyan('Exiting...'))
            exit(0)


  def site_bootstrapped(self):
    '''
    Determines if a bootstrapped drupal site exists.

    Returns 1 if the site is bootstrapped, 0 otherwise.
    '''
    if not env.exists(env.node['site_root']):
      return 0
    with env.cd(env.node['site_root']):
      result = self.drubs_run('drush status --fields=bootstrap --no-field-labels', capture=True)
      if (result.find('Successful') != -1):
        return 1
      else:
        return 0


  def site_files_exist(self):
    '''
    Determines if the site files exist.

    Returns 1 if site files exist, 0 otherwise.
    '''
    if env.exists(env.node['site_root']) and env.exists(env.node['site_root'] + '/index.php'):
      return 1
    else:
      return 0


  def site_database_exists(self):
    '''
    Determines if the database exists.

    Returns 1 if the site database exists and contains tables, 0 otherwise.
    @todo: remove replacement of mysql command line password warnings in favor
    of mysql_config_editor tools.
    '''
    status = self.drubs_run('mysql -u %s -p%s -h %s -ss -e "SHOW DATABASES LIKE \'%s\'"' % (
      env.node['db_user'],
      env.node['db_pass'],
      env.node['db_host'],
      env.node['db_name'],
    ), capture=True)
    status.replace('Warning: Using a password on the command line interface can be insecure.', '')
    if status != '':
      table_count = self.drubs_run('mysql -u %s -p%s -h %s -ss -e "SELECT COUNT(DISTINCT table_name) FROM information_schema.columns WHERE table_schema = \'%s\'"' % (
        env.node['db_user'],
        env.node['db_pass'],
        env.node['db_host'],
        env.node['db_name'],
      ), capture=True)
      table_count.replace('Warning: Using a password on the command line interface can be insecure.', '')
      if table_count > 0:
        return 1
    return 0


  def check_and_create_backup(self):
    '''
    Creates a site backup.
    '''
    if not env.no_backup:
      self.create_backup()


  def create_backup(self):
    '''
    Creates a drush archive dump backup of a site.
    '''
    if self.site_bootstrapped():
      print(cyan('Creating site backup...'))
      with env.cd(env.node['site_root']):
        if not env.exists(env.node['backup_directory']):
          self.drubs_run('mkdir -p %s' % (env.node['backup_directory']))
        self.drush('cc all')
        self.drush('archive-dump --destination="%s/%s_%s_%s.tar.gz" --preserve-symlinks' % (
          env.node['backup_directory'],
          env.config['project_settings']['project_name'],
          env.node_name,
          time.strftime("%Y-%m-%d_%H-%M-%S"),
        ))
    else:
      print(cyan('No pre-existing properly-functioning site found.  Skipping backup...'))


  def restore_latest_backup(self):
    '''
    Restores a drush archive dump backup of a site.
    '''
    print(cyan('Restoring latest site backup...'))
    with env.cd(env.node['backup_directory']):

      # Get a list of available backup files sorted with newest first.
      backup_files = glob.glob('%s/%s_%s_*.tar.gz' % (
        env.node['backup_directory'],
        env.config['project_settings']['project_name'],
        env.node_name,
      ))
      backup_files.sort(reverse=True)

      # If backup files exist, restore the latest backup file.
      if len(backup_files) > 0:
        latest_backup_file = backup_files[0]
        if env.exists(latest_backup_file):
          if not env.exists(env.node['site_root']):
            self.drubs_run('mkdir -p %s' % (env.node['site_root']))
          with env.cd(env.node['site_root']):
            self.drush('archive-restore %s --overwrite' % (
              latest_backup_file,
            ))
            self.drush('cc all')
            print(green("Latest backup '%s' restored to '%s' on node '%s'..." % (
              latest_backup_file,
              env.node['site_root'],
              env.node_name,
            )))
        else:
          print(red("Latest backup file does not exist or cannot be read in '%s' on node '%s'..." % (
            env.node['backup_directory'],
            env.node_name,
          )))
      else:
        print(red("No backup files found in '%s' on node '%s'.  Cannot restore..." % (
          env.node['backup_directory'],
          env.node_name,
        )))


  def remove_old_backups(self):
    '''
    Removes existing backup files based on the node's backup settings.
    '''
    print(cyan("Checking for site backups to be removed..."))

    # Get a list of available backup files sorted with newest first.
    backup_files = glob.glob('%s/%s_%s_*.tar.gz' % (
      env.node['backup_directory'],
      env.config['project_settings']['project_name'],
      env.node_name,
    ))
    backup_files.sort(reverse=True)

    # Exclude the first n items from the list, where n is backup_minimum_count.
    del backup_files[:int(env.node['backup_minimum_count'])]

    # Delete any remaining backup files in the list that are older than
    # backup_lifetime_days, if the list still has backups in it.
    if len(backup_files) > 0:
      for backup_filename in backup_files:
        match = search(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}', backup_filename)
        backup_time = datetime.strptime(match.group(), '%Y-%m-%d_%H-%M-%S')
        now = datetime.now()
        if backup_time < (now - timedelta(days=int(env.node['backup_lifetime_days']))):
          self.drubs_run('rm -f %s' % (backup_filename))


  def get_requirement_version(self, check_command, version_command):
    '''
    Gets the version for software if it exists.
    '''
    requirement = self.drubs_run(check_command, capture=True)
    if (requirement.return_code == 0):
      version = self.drubs_run(version_command, capture=True)
    else:
      version = red("Missing")
    return version


  def get_requirement_versions_per_node(self):
    '''
    Returns requirement versions.
    '''
    req = dict()
    req['drush']  = self.get_requirement_version("command -v drush >/dev/null 2>&1", "drush --version --pipe")
    req['git']    = self.get_requirement_version("command -v git >/dev/null 2>&1", "git --version | awk '{ print $3 }'")
    req['php']    = self.get_requirement_version("command -v php >/dev/null 2>&1", "php --version | head -n 1 | awk '{ print $2 }'")
    req['mysql']  = self.get_requirement_version("command -v php >/dev/null 2>&1", "mysql --version|awk '{ print $5 }'|awk -F\, '{ print $1 }'")
    req['python'] = self.get_requirement_version("command -v python >/dev/null 2>&1", "python -c 'import sys; print(\".\".join(map(str, sys.version_info[:3])))'")
    req['fabric'] = self.get_requirement_version("command -v fab >/dev/null 2>&1", "fab --version | head -n 1 | awk '{ print $2 }'")
    req['apache'] = self.get_requirement_version("command -v apachectl >/dev/null 2>&1", "apachectl -v | head -n 1 | awk '{ print $3 }'")
    return req


  def status_per_node(self):
    '''
    Prints status information per node.
    '''
    status_table = PrettyTable(['Property', 'Value'])
    status_table.align = "l"

    with quiet():

      status_table.add_row(['Node name', env.node_name])
      status_table.add_row(['Hostname', env.node['server_host']])

      if self.site_bootstrapped():
        bootstrap = green('yes')
      else:
        bootstrap = red('no')
      status_table.add_row(['Site bootstrap', bootstrap])

      if self.site_database_exists():
        database = green('yes')
      else:
        database = red('no')
      status_table.add_row(['Database exists', database])

      if self.site_files_exist():
        files = green('yes')
      else:
        files = red('no')
      status_table.add_row(['Site files exist', files])

      distro = self.drubs_run('lsb_release -ds 2>/dev/null || cat /etc/*release 2>/dev/null | head -n1 || uname -om', capture=True)
      status_table.add_row(['Server OS', distro])

      req = self.get_requirement_versions_per_node()
      status_table.add_row(['Apache version', req['apache']])
      status_table.add_row(['PHP version', req['php']])
      status_table.add_row(['MySQL client version', req['mysql']])
      status_table.add_row(['Drush version', req['drush']])
      status_table.add_row(['Git version', req['git']])
      status_table.add_row(['Python version', req['python']])
      status_table.add_row(['Fabric version', req['fabric']])

    print status_table


  def print_elapsed_time(self):
    '''
    Prints the elapsed time.
    '''
    seconds = time.time() - env.start_time
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print(cyan("Elapsed time: %dh:%02dm:%02ds" % (h, m, s)))


  @contextmanager
  def cleanup_on_failure(self):
    '''
    Context wrapper for operations that cleans up on/after failure.
    '''
    try:
      yield
    except SystemExit:

      # Restore site from backup if allowed by command options.
      if not env.no_restore:
        self.restore_latest_backup()
      else:
        print(yellow("Command was executed with the '--no-backup' or '--no-restore' option.  No site backup has been restored..."))

      # Remove old backups unless --no-backup option was set.
      if not env.no_backup:
        self.remove_old_backups()

      # Remove temporarily copied files if they still exist.
      self.remove_files()
