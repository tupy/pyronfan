# -*- coding: utf-8 -*-
"""
  pyronfan.fabric
  ~~~~~~~~~~~~~~~

  Configuration variables.

  @copyright: (c) 2012 by Osvaldo Matos-Junior <tupy@jusbrasil.com.br>
  :license: BSD, see LICENSE for more details.
"""

from __future__ import absolute_import

import os

from chef import *
from chef.fabric import chef_environment, chef_roledefs

from fabric.api import env, task, roles, hosts, local, sudo

from pyronfan.cluster import Cluster
from pyronfan.loader import YAMLLoader
from pyronfan.utils import create_nodes, search_node


env.cluster_name = None


@task
def cluster(cluster_name):
  """Load and configure the cluster on the Fabric environment."""

  # moved to the first line to auto configure the chef api
  env.roledefs = chef_roledefs(hostname_attr=['ipaddress'])

  cluster = Cluster.TYPES.get(cluster_name)
  if cluster is None:

    loader = YAMLLoader(cluster_name)
    cluster = loader.load()

    for facet in cluster.facets:
      create_nodes(cluster, facet)
      # update list of hosts
      hosts = facet.nodes.keys()
      #env.hosts.extend(hosts)

  # update env
  env.cluster = cluster
  env.cluster_name = cluster.name
  env.user = env.cluster.cloud.user

  # update the roledefs and set the cluster role
  env.roledefs[env.cluster_name] = env.cluster.hosts
  env.roles.append(env.cluster_name)
  # get chef_environment from the cluster when not specified
  if not getattr(env, 'chef_environment', None):
    env.chef_environment = env.cluster.environment


@task
def bootstrap(pattern=None):
  """Execute knife bootstrap to start a new node."""

  node = env.cluster.get(env.host)
  if pattern and not node.name.startswith(pattern):
    return
  # if node is None:
  #   node = search_node(env.host)
  ctx = {
    'user': env.user,
    'host': env.host,
    'nodename': node.name,
    'environment': env.chef_environment,
    'run_list': ','.join(node.run_list)
  }

  local('knife bootstrap %(host)s -x %(user)s -r "%(run_list)s" --sudo -N %(nodename)s -E %(environment)s' % ctx)

@task
def kick(pattern=None):
  """Execute chef-client in the host."""

  node = env.cluster.get(env.host)
  if pattern and not node.name.startswith(pattern):
    return
  sudo('chef-client')

@task
@hosts('localhost')
def kill():
  """Remove the cluster nodes from Chef server."""

  for facet in env.cluster.facets:
    for node in facet.nodes.values():
      if node.chef_environment == env.chef_environment:
        node.delete()
        print("%s deleted" % node.name)


@task
@hosts('localhost')
def sync():
  """Syncronize cluster nodes with Chef server."""

  # create cluster roles
  cluster_role = "%s_cluster" % env.cluster.name
  cluster_role = Role(cluster_role)
  cluster_role.save()
  print('role[%s] saved' % cluster_role)
  for facet in env.cluster.facets:
    facet_role = '%s_%s' % (env.cluster.name, facet.name)
    facet_role = Role(facet_role)
    facet_role.save()
    print('role[%s] saved\n' % facet_role)
    for node in facet.nodes.values():
      print('Node Name: %s' % node.name)
      print('IP:        %s' % node['ipaddress'])
      print('Run List:  %s' % ', '.join(node.run_list))
      print('')
      node.save()


@task
@hosts('localhost')
def test():

  print('Cluster Name: %s' % env.cluster.name)
  print('Cloud Name: %s' % env.cluster.cloud.name)
  print('Environment: %s' % env.cluster.environment)

  for facet in env.cluster.facets:
    print('---------------------------------------------')
    print('Facet Name: %s\n' % facet.name)
    for node in facet.nodes.values():
      print('Node Name: %s' % node.name)
      print('IP:        %s' % node['ipaddress'])
      print('Run List:  %s' % ', '.join(node.run_list))
      print('')
