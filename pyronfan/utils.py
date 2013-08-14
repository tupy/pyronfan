# -*- coding: utf-8 -*-
"""
  pyronfan.utils
  ~~~~~~~~~~~~~~

  Configuration variables.

  @copyright: (c) 2012 by Osvaldo Matos-Junior <tupy@jusbrasil.com.br>
  :license: BSD, see LICENSE for more details.
"""

from chef import Node, Search


def create_instances(cluster, facet):
  """Extract the different facet instances"""

  instances = []
  prefix = "%s-%s" % (cluster.name, facet.name)
  if isinstance(facet.instances, list):
    # create a sequence: webcluster-webnode-0, webcluster-webnode-1 ...
    for index, ipaddress in enumerate(facet.instances):
      nodename = "%s-%d" % (prefix, index)
      node = (nodename, ipaddress)
      instances.append(node)
  elif isinstance(facet.instances, dict):
    for nodename, ipaddress in facet.instances.iteritems():
      # webcluster-webnode-2
      if isinstance(nodename, int):
        nodename = "%s-%d" % (prefix, nodename)
      node = (nodename, ipaddress)
      instances.append(node)
  return instances


def create_nodes(cluster, facet):
  """Initialize Chef nodes"""

  instances = create_instances(cluster, facet)

  for nodename, ipaddress in instances:
    node = Node(nodename)
    if node.exists:
      node_ipaddress = node.get('ipaddress')
      if ipaddress is None and node_ipaddress:
        ipaddress = node_ipaddress
      elif node_ipaddress and node_ipaddress != ipaddress:
        raise Exception('The remote IP address is different: %s' % node_ipaddress)

    if ipaddress is None:
      raise Exception('Can not determine the IP address for %s' % nodename)

    node['ipaddress'] = ipaddress

    # update environment and run_list
    node.chef_environment = cluster.environment

    run_list = list(cluster.run_list)
    run_list.extend(facet.run_list)

    # tagging the cluster
    run_list.append(u'role[%s_cluster]' % cluster.name)
    run_list.append(u'role[%s_%s]'% (cluster.name, facet.name))

    for role in run_list:
      if role not in node.run_list:
        node.run_list.append(role)

    facet.nodes[ipaddress] = node



def search_node(host):
  """ Search for node with the ipaddress"""

  print('Searching for host %s' % host)

  search_node = Search('node', q='ipaddress:%s or ec2_public_hostname:%s' % (host, host), rows=1, start=0, api=None)[0]
  return Node(search_node['name'])


import sys

if __name__ == '__main__':

   if len(sys.argv) < 2:
     sys.exit('Usage: %s <cluster_name>' % sys.argv[0])
