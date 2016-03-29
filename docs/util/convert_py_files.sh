#!/usr/bin/env bash

function drubs_replace () {
  sed -i "s/$1/$2/g" *.py
}

drubs_replace "from drupal3 import drupal3" "from drubs.node import Node"
drubs_replace "instance = drupal3(env)" "instance = Node(env)"
drubs_replace "drush_sql = instance.drush_sql" "drush_sql = instance.drush_sql\ndrubs_run = instance.drubs_run"
drubs_replace "env.site_root" "env.node['site_root']"
drubs_replace "env.run(" "drubs_run("


