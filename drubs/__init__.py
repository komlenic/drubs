import sys
import argparse
from pprint import pprint
from fabric.colors import red, yellow, green, cyan

def main():
  """Entry point for the command line tool."""

  # Exit if python version is not correct.
  if sys.version_info[0] != 2 or sys.version_info[1] < 7:
    print(red("Drubs requires Python 2, version 2.7 or greater."))
    sys.exit(1)

  parser = argparse.ArgumentParser()
  parser.add_argument('action', choices=['init', 'install', 'update', 'destroy', 'enable', 'disable', 'var_dump', 'status'], help='The action to execute.')
  parser.add_argument('nodes', nargs='+', help='one or more nodes')
  parser.add_argument('-f', '--file', default='project.yml', help='path to project.yml file (not necessary if pwd contains the project.yml file)')
  parser.add_argument('-v', '--verbose', action='store_const', const='1', default='0', help='print verbose output from drush commands, if available')
  parser.add_argument('-d', '--debug', action='store_const', const='1', default='0', help='print debug output from drush commands, if available')
  parser.add_argument('-c' , '--cache', action='store_const', const='1', default='0', help='use drush cache of projects when building sites, where available')
  parser.add_argument('--version', action='version', version='%(prog)s 0.1.0')
  args = parser.parse_args()

  pprint(args)
