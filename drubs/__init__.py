import sys
import argparse
import textwrap
import drubs
from fabric.colors import red, yellow, green, cyan

def main():
  """Entry point for the command line tool."""

  # Exit if python version is not correct.
  if sys.version_info[0] != 2 or sys.version_info[1] < 7:
    print(red("Drubs requires Python 2, version 2.7 or greater."))
    sys.exit(1)

  parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''\

      Drubs 0.2.0

        A command-line tool tool for building, deploying, and managing Drupal
        sites across multiple servers and environments.

      Available actions:

        init     Create a new project with the specified nodes
        status   Return some status information about the specified nodes
        install  Install the project on the specified nodes (destroys any
                   existing site)
        update   Update the project on the specified nodes (data safe*)
        disable  Put specified nodes into Drupal's 'maintenance mode'
        enable   Turns off Drupal's maintenance mode (if on)
        destroy  Completely deletes the project from the specified nodes

      Example commands:

        drubs install myserver1
          - perform the install action on myserver1

        drubs install myserver1 myserver2
          - perform the install action on myserver1 AND myserver2

        drubs install all
          - perform the install action on all nodes found in project.yml

        drubs -f /home/me/new_project/foo.yml install myserver1
          - perform the install action on myserver1, without pwd currently
            being /home/me/new_project, and use a project config file named
            'foo.yml' instead of the default 'project.yml'

        '''),
    epilog='http://drubs.org'
  )
  parser.add_argument('action', choices=['init', 'install', 'update', 'destroy', 'enable', 'disable', 'var_dump', 'status'], help='The action to perform on the specified nodes. (see descriptions above)', metavar='action')
  parser.add_argument('nodes', nargs='+', help='one or more nodes, or "all" which will perform the specified action on all valid nodes found in project.yml')
  parser.add_argument('-f', '--file', default='project.yml', help='path to project.yml file (not necessary if pwd contains the project.yml file)')
  parser.add_argument('-v', '--verbose', action='store_const', const=True, default=False, help='print verbose output from drush commands, if available')
  parser.add_argument('-d', '--debug', action='store_const', const=True, default=False, help='print debug output from drush commands, if available')
  parser.add_argument('-c', '--cache', action='store_const', const=True, default=False, help='use drush cache of projects when building sites, where available')
  parser.add_argument('-D', '--fab_debug', action='store_const', const=True, default=False, help='print fabric debug messages')
  parser.add_argument('--version', action='version', version='%(prog)s 0.2.0')

  # Print help if no arguments are supplied.
  if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)

  args = parser.parse_args()
  drubs.drubs(args)
