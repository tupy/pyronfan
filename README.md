# Pyronfan

Pyronfan helps you to manage your cluster by configuring it using [Chef Server](http://docs.opscode.com/). It was inspired the [Ironfan](https://github.com/infochimps-labs/ironfan) Ruby project, and uses [Fabric](http://fabfile.org) to manage the common Chef tasks (e.g. bootstrap).

## Setup

Pyronfan requires Fabric 1.4.1 or later, PyChef 0.2.1 and PyYAML library. To install them, type:

```
pip install -r requires.txt
```

## Getting Started

First, you need to create a new cluster definition and place it in the Pyronfan root folder (the same level that `fabfile.py`).

Look the example bellow for a cluster web (YAML format): 

```yaml
name: webcluster
cloud:
  name: ec2
  user: ubuntu

environment: production

roles:
  - base

facets:
  - name: lb
    instances:
      - 10.0.0.1
    roles:
      - haproxy

  - name: webnode
    instances:
      0: 10.0.0.2
      1: 10.0.0.3
    roles:
      - nginx
```

Then, test the cluster file:

```
$ fab cluster:webcluster test
```

This will look for the `webcluster.yml` file on the current directory.

## Using Pyronfan

Here you can see the common tasks that you can run with the Pyronfan to manage your cluster.


### bootstrap

A bootstrap is a process that installs the chef-client on a target system so that it can run as a chef-client and communicate with a server.

```
$ fab cluster:webcluster bootstrap
```

This will execute the command [knife bootstrap](http://docs.opscode.com/knife_bootstrap.html) for all servers in the cluster file. Also, you can run it for a subset passing a `pattern`:

```
$ fab cluster:webcluster bootstrap:webcluster-lb-0
```
to execute bootstrap only for one server or all servers in the facet:

```
$ fab cluster:webcluster bootstrap:webcluster-webnode
```

### kick

Execute [chef-client](http://docs.opscode.com/essentials_chef_client.html) for a specific host (or more cluster instances). 

```
$ fab cluster:webcluster kick:webcluster-webnode-0
```

### kill

Destroy the cluster: removes all node and client entries on the Chef Server.

```
$ fab cluster:webcluster kill
```

This will not destroy the cloud instances.

### sync

Synchronize the local configuration with the Chef Server.

```
$ fab cluster:webcluster sync
```

Attention: turn off the `chef-client` service on the remote host before run `sync`, since `chef-client` send back your configuration to the server on the end of the cycle.

