import sys
from fabric.state import env
from fabric.operations import local
from fabric.api import lcd, cd, run
from fabric.context_managers import settings
from fabric.colors import red, yellow, green, cyan
from drubs.node import Node

instance = Node(env)
drush = instance.drush
drush_sql = instance.drush_sql
drubs_run = instance.drubs_run

def pre(*args, **kwargs):
  with env.cd(env.node['site_root']):
    print(cyan("Beginning pre-install configuration tasks for project..."))
    '''
    Enter any pre-install configuration tasks below.
    Typically you will not need to execute tasks prior to installing.

    Any tasks specified here will only be executed prior to installing, and will
    not be executed at any time during update.
    '''
    print(cyan("End of pre-install configuration tasks..."))



def post(*args, **kwargs):
  with env.cd(env.node['site_root']):
    print(cyan("Beginning post-install configuration tasks for project..."))
    '''
    Enter any post-install configuration tasks below (examples provided).

    Typically this is where you will enable and disable modules/themes/etc.
    Generally you will be using drubs_run(), drush(), and drush_sql() functions.

    Some examples:

    drush('vset [variable_name] [variable_value]')
    drubs_run('cp somefile someplace')
    drush('en [module_name]')
    drush('en [module1_name,module2_name,module3_name]')
    drush('dis [module]')
    drush_sql(<triple single quotes here>UPDATE some_table...<triple single quotes here>)

    See http://drush.ws/ for more examples of drush commands you may wish to
    use.

    Almost always, you will want to execute these postinstall tasks after
    installing AND after updating a project.  In rare circumstances, you may
    need a task to ONLY be executed during install, or only during update.
    The appropriate sections for each of these types of tasks are below.
    '''
    # Regular tasks to be executed during install AND update below this line.

    drush('en module_filter,admin_menu,admin_menu_toolbar,ctools,views,wysiwyg,libraries')
    drush('dis toolbar,overlay')

    # Set error reporting in Drupal.  Drupal 7 overrides whatever
    # error_reporting that is set in php.ini with E_ALL, then handles reporting
    # levels inside Drupal with this setting.  Values:
    # 0 = none, 1 = errors and warnings, 2 = all messages.  Production
    # environments should use 0.
    drush('vset error_level 2')

    # Revert all features.  Remember that "features revert" is code -> database,
    # and "features update" is database -> code.  You may wish to uncomment this
    # line if the features module is enabled in this project.
    # drush('features-revert-all')

    if env.command in ('install_project', 'install'):
      # Tasks to be executed only on install below this line.
      pass # Replace/remove this line if adding other code.

    elif env.command in ('update_project', 'update'):
      # Tasks to be executed only on update below this line.
      pass # Replace/remove this line if adding other code.

    print(cyan("End of post-install configuration tasks..."))

