import yaml
import tasks
from os.path import isfile, dirname, abspath
from fabric.state import env, output
from fabric.tasks import execute
from fabric.colors import red, yellow, green, cyan


def load_config_file(config_file):
  '''
  Returns yaml file contents as an object.

  Also sets the following fabric/global env vars:

  env.config_file - the supplied path to the project config file.  Under typical
    usage without the -f parameter, this will be 'project.yml'
  env.config_dir - the absolute path to the project config directory
  env.config - the actual contents of the config file

  Accepts one parameter 'config_file': the relative or absolute path to a drubs
  project config file.
  '''
  if isfile(config_file):
    env.config_file = config_file
    env.config_dir = dirname(abspath(config_file))
    with open(config_file, 'r') as stream:
      env.config = yaml.load(stream)

    # If env.config evaluates to false, nothing parseable existed in the file.
    if not env.config:
      print(red("The project config file '%s' does not contain anything or is not valid. Exiting..." % (config_file)))
      exit(1)
    if 'nodes' not in env.config:
      print(red("The project config file '%s' does not contain a 'nodes' section. Exiting..." % (config_file)))
      exit(1)
    return env.config
  else:
    if config_file == 'project.yml':
      print(red("No project config file found in current working directory.  Either run drubs from a directory containing a valid project config file (named 'project.yml'), or use '-f'."))
      exit(1)
    else:
      print(red("The project config file '%s' does not exist or could not be read." % (config_file)))
      exit(1)


def check_config_requirements_per_node(nodes):
  '''
  Checks for required values per nodes supplied.
  '''
  for node in nodes:
    if node not in env.config['nodes']:
      print(red("No node named '%s' found in drubs project config file '%s'.  Exiting..." % (node, env.config_file)))
      exit(1)

    required_node_keys = [
      'account_mail',
      'account_name',
      'account_pass',
      'db_host',
      'db_name',
      'db_pass',
      'db_user',
      'make_file',
      'py_file',
      'server_host',
      'server_port',
      'server_user',
      'site_mail',
      'site_name',
      'site_root',
    ]
    for key in required_node_keys:
      if key not in env.config['nodes'][node]:
        print(red("No key named '%s' for node '%s' found.  Exiting..." % (key, node)))
        exit(1)
      elif env.config['nodes'][node][key].strip() == '':
        print(red("No value for '%s' for node '%s' found.  Exiting..." % (key, node)))
        exit(1)


def get_fabric_hosts(nodes):
  '''
  Gets fabric hosts from associated node names.

  Returns a list of fabric host strings (user@host:port) for the supplied nodes.
  Passing 'all' for nodes, returns a list of fabric host strings for all nodes
  found in the project's config file.
  '''
  hosts = []
  for node in nodes:
    user = env.config['nodes'][node]['server_user'].strip()
    host = env.config['nodes'][node]['server_host'].strip()
    port = env.config['nodes'][node]['server_port'].strip()
    host_string = '%s@%s:%s' % (user, host, port)
    hosts.append(host_string)
  return hosts


def set_flags(args):
  env.verbose = args.verbose
  env.debug   = args.debug
  env.cache   = args.cache
  if args.fab_debug:
    output.debug = True


def drubs(args):

  set_flags(args)
  load_config_file(args.file)

  # If 'all' has been supplied as the only item for the 'nodes' parameter, set
  # 'nodes' to a list of all nodes found in the project config file.
  if len(args.nodes) == 1 and args.nodes[0] == 'all':
    args.nodes = env.config['nodes']

  check_config_requirements_per_node(args.nodes)

  # Build/set fabric host strings.
  hosts = get_fabric_hosts(args.nodes)

  # Execute the requested task on the specified hosts.  For passing variable
  # task/action names to execute(), getattr() is used to load the tasks from
  # tasks.py.  See: http://stackoverflow.com/questions/23605418/in-fabric-
  # how-%20can-i-execute-tasks-from-another-python-file
  execute(getattr(tasks, args.action), hosts=hosts)
