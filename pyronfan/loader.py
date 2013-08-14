# -*- coding: utf-8 -*-
"""
  pyronfan.loader
  ~~~~~~~~~~~~~~~

  Configuration variables.

  @copyright: (c) 2012 by Osvaldo Matos-Junior <tupy@jusbrasil.com.br>
  :license: BSD, see LICENSE for more details.
"""
import os
import yaml

from pyronfan.cluster import Cluster, Cloud, Facet


class ClusterLoader:

  def __init__(self, cluster_name):
    self.cluster_name = cluster_name

  def load():
    """
    Load the cluster configuration.

    return: a `Cluster` instance
    """
    raise NotImplemented


class YAMLLoader(ClusterLoader):
  """Load cluster configuration from a YAML file."""

  def load(self):

    filename = '%s.yml' % self.cluster_name
    if not os.path.exists(filename):
      raise IOError('Could not load the File not found')

    f = open(filename)
    data = yaml.load(f)
    f.close()

    assert 'name' in data
    cluster = Cluster(data['name'], environment=data.get('environment'))

    assert 'cloud' in data
    cluster.cloud = self.__cloud(data['cloud'])

    if 'roles' in data:
      cluster.run_list.extend(self.__roles(data['roles']))

    if 'recipes' in data:
      cluster.run_list.extend(self.__recipes(data['recipes']))

    if 'facets' in data:
      cluster.facets = self.__facets(data['facets'])

    return cluster

  def __cloud(self, cloud):

    return Cloud(cloud['name'], user=cloud.get('user'))

  def __facets(self, facets_data):
    facets = []
    for f in facets_data:
      facet = Facet(f['name'])
      facet.instances = f['instances']
      if 'roles' in f:
        facet.roles(*f['roles'])
      if 'recipes' in f:
        facet.recipes(*f['recipes'])
      facets.append(facet)
    return facets

  def __roles(self, roles):
    return [u'role[%s]' % r for r in roles]

  def __recipes(self, recipes):
    return [u'recipe[%s]' % r for r in recipes]
