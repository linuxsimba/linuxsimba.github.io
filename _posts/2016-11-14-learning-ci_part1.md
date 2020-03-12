---
title: Learning Continuous Integration - Part 1
tags: ['ci', 'gitlab']
---

 [Continuous integration](https://en.wikipedia.org/wiki/Continuous_integration) (CI) is the hot new thing in the computer infrastructure world. To learn CI I'm going to practise it using one of my favorite python projects - netshow. Hopefully in a few months I can begin to manage compute infrastructure changes using CI.

## Platform/Hypervisor
Ubuntu 16.04 Laptop with enough RAM/Disk to hold all the necessary docker components.

## Tools

* [Docker-compose](https://vexxhost.com/resources/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-14-04/)
* [GitLab](https://about.gitlab.com)
* [devpi-server](https://pypi.python.org/pypi/devpi-server)
* [python-gitlab](http://python-gitlab.readthedocs.io/en/stable/)
* [Python (2.7 and 3.4)](https://docs.python.org/3/)

### Installing GitLab

Docker-compose is used to setup the image, volume and networking of the various containers required to setup the Continuous Integration environment.
#### docker-compose.yml for setting up gitlab
{% gist linuxsimba/0be4b014b1aeedcf01f18b4a2548d8e4 %}

#### network layout of docker containers
![Docker-compose Network Topology](https://lh3.googleusercontent.com/ZWb_2X0LdQzSXyBjwLcKgyUGu9J6bhP8AGJBkLV_4TUkN0sUxs9M4AlC26xHG5Gfjdrihm0=s0 "gitlab_topology.png")

#### CLI commands on the Platform/Hypervisor

```bash
apt-get install python-setuptools
sudo easy_install pip
sudo pip install docker-compose

mkdir gitlab-docker
cd gitlab-docker
mkdir $HOME/staging_pypi
mkdir $HOME/prod_pypi

sudo chown 1000:1000 $HOME/staging_pypi
sudo chown 1000:1000 $HOME/prod_pypi
wget https://goo.gl/FHIzgO -o docker-compose.yml

docker-compose up -d
!! Wait a few minutes for Gitlab to load
```


## Initial Setup of Gitlab

> TODO: Use python-gitlab to automate the process described below

#### Add a root password

Go to [http://localhost:9080](http://localhost:9080) and create a root password. In this test case it is ``cn321cn321!``

![enter root password](https://lh3.googleusercontent.com/ylUFZeXuqNj_D50cElo9S_jFBW1GyRKjnH-SrqDcjk59zRX5eniSC72p39ZhElLUE8nRMVs=s0 "gitlab_diagram.png")


#### Create a new user
Refresh [http://localhost:9080](http://localhost:9080) and create  new user with the following parameters

* username: demo
* password: cn321cn321!
* name: demo
* email: demo@example.com

![new demo user](https://lh3.googleusercontent.com/VueiTkzUy6V_ADx1h4NnJpVBRZQths9h4b-lr4ItcPIr34DVu6LOvApxx-0MLX3ZjHzvrk8=s0 "new_demo_user.png")


#### Create a new project
Select "new project" and then import the github [netshow-core](https://github.com/linuxsimba/netshow-core)
To perform this import, one needs to create a [Github API Token](https://github.com/blog/1509-personal-api-tokens)

![import project from github](https://lh3.googleusercontent.com/TNPCgAVbJBRZJB9rL1J-GCIHEkdmT1UMEFFUAV8KeS_w2wnlOLrzLALiW7d0zz0M5TTNjbs=s0 "import_project.png")


#### Add a SSH Key to the Demo user profile
When the project is accessed for the first time, it will alert saying to add a SSH key. Take the ``$HOME/.ssh/id_rsa.pub key`` and add it to the SSH key Profile section

#### Obtain the gitlab runner token.
Gitlab uses a Go-Erlang application to manage docker containers that will run the test builds. This app is called gitlab-runner. It is stored in its own container. Each project needs to be associated with a gitlab-runner if continuous integration is to take place.

To view runners for a project, click on the top right side dropdown and select runner. Or use a link that looks like this:

* [http://localhost/9080/demo/netshow-core/runners](http://localhost/9080/demo/netshow-core/runners)

![runner_dropdown](https://lh3.googleusercontent.com/dv5qY2i6uV0uG9iwcT4P99kVY98VjKmyQ33R7BTQqoblCbXGIZya25n2uMLaDUFmJBH_q2xq=s0 "runner_dropdown.png")

One bug with the GUI is that if you have a screen that doesn't cover the whole screen, then the top right dropdown is not visible.

On the runner page, note the regsitration token. This will be used in the next step

![project registration token](https://lh3.googleusercontent.com/of9bLu412hAaXzxPtPQ_EB8TWFQzxRKW5POuCONptqoq96dI4b8g_KOHC2YimF5aa3IA7o17=s0 "get_registration_token.png")

#### Register Gitlab-runner

From the hypervisor CLI run the following commands

```
~:% docker exec -it gitlab-runner gitlab-runner register
Running in system-mode.                            

Please enter the gitlab-ci coordinator URL (e.g. https://gitlab.com/):
[http://gitlab/ci]:   [hit enter]     
Please enter the gitlab-ci token for this runner:
B4qz89Eattey2XLVx86s
Please enter the gitlab-ci description for this runner:
[python_docker]: [hit enter]
Please enter the gitlab-ci tags for this runner (comma separated):
netshow
[ wait a few seconds to get the next option ]
Registering runner... succeeded                     runner=B4qz89Ea
Please enter the executor: parallels, shell, virtualbox, docker, docker-ssh, ssh, docker+machine, docker-ssh+machine, kubernetes:
[docker]:     [hit enter]
Please enter the default Docker image (eg. ruby:2.1):
[python:2.7.12-alpine]: [hit enter]
Runner registered successfully. Feel free to start it, but if it's running already the config should be automatically reloaded!

~:% docker exec -it gitlab-runner gitlab-runner list    
Listing configured runners                          ConfigFile=/etc/gitlab-runner/config.toml
python_docker                                       Executor=docker Token=dd4b0a773e63ac56d45fde0f5fe9df URL=http://gitlab/ci

```

Gitlab is now setup to perform continuous integration on the ``netshow-core`` project.
The next article will cover how to setup the CI steps for the project and how to use CI
to validate changes to the Git repository.
