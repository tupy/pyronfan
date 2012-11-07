# -*- coding: utf-8 -*-
"""
  pyronfan
  ~~~~~~~~

  Configuration variables.

  @copyright: (c) 2012 by Osvaldo Matos-Junior <tupy@jusbrasil.com.br>
  :license: BSD, see LICENSE for more details.
"""

class Cluster:
  """
  The cluster definition, such as cloud, environment, server schemas (facets).
  """

  TYPES = {}

  def __init__(self, name, environment='_default'):
    self.name = name
    self.cloud = None
    self.environment = environment
    self.facets = []
    self.run_list = []

    # register the cluster
    Cluster.TYPES[name] = self

  def get(self, key):

    for facet in self.facets:
      node = facet.nodes.get(key)
      if node: return node

  @property
  def hosts(self):
    hosts = []
    for facet in self.facets:
      hosts.extend(facet.hosts)
    return hosts

class Cloud:
  """The cloud provider, such as Amazon EC2, Liquidweb, etc."""

  def __init__(self, name=None, user='ubuntu'):
    self.name = name
    self.user = user

class Facet:

  def __init__(self, name):
    self.name = name
    self.instances = []
    self.run_list = []
    self.nodes = {}

  def roles(self, *names):
    for name in names:
      self.run_list.append(u'role[%s]' % name)

  def recipes(self, names):
    for name in names:
      self.run_list.append(u'recipe[%s]' % name)

  @property
  def hosts(self):
    return self.nodes.keys()

