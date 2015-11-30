import node
from fabric.api import task
from fabric.state import env

@task
def status():
  instance = node.Node(env)
  instance.status()

@task
def install():
  instance = node.Node(env)
  instance.install()

@task
def update():
  instance = node.Node(env)
  instance.update()

@task
def disable():
  instance = node.Node(env)
  instance.disable()

@task
def enable():
  instance = node.Node(env)
  instance.enable()

@task
def destroy():
  instance = node.Node(env)
  instance.destroy()

@task
def var_dump():
  instance = node.Node(env)
  instance.var_dump()
