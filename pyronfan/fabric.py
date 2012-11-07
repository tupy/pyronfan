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
from fabric.api import *
from chef import *
from chef.fabric import chef_environment, chef_roledefs

from pyronfan import Cluster
from pyronfan.utils import load_cluster, create_nodes, search_node

env.cluster_name = None

def configure(cluster_name):
  """Load and configure the cluster on the Fabric environment."""

  cluster = Cluster.TYPES.get(cluster_name)
  if cluster:
    return cluster

  filename = '%s.yml' % cluster_name
  print('Loading %s' % filename)
  if not os.path.exists(filename):
    raise IOError('Could not load the File not found')
  cluster = load_cluster(filename)

  for facet in cluster.facets:
    create_nodes(cluster, facet)
    # update list of hosts
    hosts = facet.nodes.keys()
    #env.hosts.extend(hosts)

  env.cluster = cluster
  env.cluster_name = cluster.name
  env.user = env.cluster.cloud.user

@task
def cluster(cluster_name):
  """Load and configure the cluster on the Fabric environment."""

  env.roledefs = chef_roledefs(hostname_attr = ['ipaddress'])
  configure(cluster_name)

  # update the roledefs and set the cluster role
  env.roledefs[env.cluster_name] = env.cluster.hosts
  env.roles.append(env.cluster_name)
  # get chef_environment from the cluster when not specified
  if not getattr(env, 'chef_environment', None):
    env.chef_environment = env.cluster.environment

@task
def kick():
  """Execute chef-client in the host."""

  sudo('chef-client')

@task
@hosts('localhost')
def kill(cluster_name=None):
  """Remove the cluster nodes from Chef server."""

  cluster_name = cluster_name or env.cluster_name
  if not cluster_name:
    raise IOError('cluster_name not defined')

  configure(cluster_name)

  for facet in env.cluster.facets:
    for node in facet.nodes.values():
      if node.chef_environment == env.chef_environment:
        node.delete()
        print("%s deleted" % node.name)

@task
@hosts('localhost')
def sync(cluster_name=None):
  """Syncronize cluster nodes with Chef server."""

  cluster_name = cluster_name or env.cluster_name
  if not cluster_name:
    raise IOError('cluster_name not defined')

  configure(cluster_name)

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
    # save nodes
    for node in facet.nodes.values():
      print('Node Name: %s' % node.name)
      print('IP:        %s' % node['ipaddress'])
      print('Run List:  %s' % ', '.join(node.run_list))
      print('')
      node.save()

@task
def bootstrap():
  """Execute knife bootstrap to start a new node."""

  print("Running bootstrap on %s" % env.host)
  node = env.cluster.get(env.host)
  if node is None:
    node = search_node(env.host)
  ctx = {
    'user': env.user,
    'host': env.host,
    'nodename': node.name,
    'environment': env.chef_environment,
    'run_list': ','.join(node.run_list)
  }

  local('knife bootstrap %(host)s -x %(user)s -r "%(run_list)s" --sudo -N %(nodename)s -E %(environment)s' % ctx)
