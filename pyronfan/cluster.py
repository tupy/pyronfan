# -*- coding: utf-8 -*-
"""
  pyronfan.cluster
  ~~~~~~~~~~~~~~~~

  Cluster schemas.

  @copyright: (c) 2012 by Osvaldo Matos-Junior <tupy@jusbrasil.com.br>
  :license: BSD, see LICENSE for more details.
"""

DEFAULT_ENVIRONMENT = '_default'
DEFAULT_USERNAME = 'ubuntu'


class Cluster:
  """
  The entire cluster definition: cloud, environment, server schemas (facets).
  """

  TYPES = {}

  def __init__(self, name, environment=None):
    self.name = name
    self.cloud = None
    self.environment = environment or DEFAULT_ENVIRONMENT
    self.facets = []
    self.run_list = []

    # register the cluster
    Cluster.TYPES[name] = self

  def get(self, key):

    for facet in self.facets:
      node = facet.nodes.get(key)
      if node:
        return node

  @property
  def hosts(self):
    hosts = []
    for facet in self.facets:
      hosts.extend(facet.hosts)
    return hosts


class Cloud:
  """Cloud provider used: amazon, rackspace, liquidweb, etc."""

  def __init__(self, name=None, user=None):
    self.name = name
    self.user = user or DEFAULT_USERNAME


class Facet:
  """The server group definition. Used to create server schemas,"""

  def __init__(self, name):
    self.name = name
    self.instances = []
    self.run_list = []
    self.nodes = {}

  def roles(self, *names):
    for name in names:
      self.run_list.append(u'role[%s]' % name)

  def recipes(self, *names):
    for name in names:
      self.run_list.append(u'recipe[%s]' % name)

  @property
  def hosts(self):
    return self.nodes.keys()
