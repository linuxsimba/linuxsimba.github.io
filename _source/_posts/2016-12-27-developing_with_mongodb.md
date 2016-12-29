---
title: Local MongoDB and MongoDB UI Setup on a Linux Laptop
tags: ['MongoDB','docker']
---

It is very easy using [docker-compose](https://docs.docker.com/compose/) to setup
a local MongoDB server and UI.

### Install docker-compose

Install [docker-engine](https://docs.docker.com/engine/installation/linux/ubuntulinux/), of cause, then install the docker-compose python scripts

```
# remember to install docker-engine first!
pip install docker-compose
```

### Copy the docker-compose file to an empty folder
Copy the following ``docker-compose.yml`` file into an empty folder.
{% gist linuxsimba/4b8b83fc38c5a1bdbe7f00a50e1f275b %}


### Install the MongoDB server and UI
```
mkdir mongodb-server
cd mongodb-server
wget https://goo.gl/4vTPgy -O docker-compose.yml
docker-compose up -d
```

The docker-compose file sets the following ports on the hypervisor

* 27017(TCP): MongoDB server
* 3300(TCP): MongoDB UI



At this point you can point your web browser to [http://localhost:3300](http://localhost:3300) to access
the UI. By default MongoDB does not use any authentication.

### Screenshots showing UI setup

Select the ``Connect`` Button to view the connection Screenshots

![click connect button](https://lh3.googleusercontent.com/izBz9eO4BNviVUqrq1XAmBuk9yJdEqsIXv91PZLCHE40NBoZCa4D94xedAGtc3UsSTFHTWEI=s0 "click_connect_button.png")

Enter the MongoDB connection server info. **Note**: the MongoDB hostname is ``MongoDB``. Remember the UI sits on a special network where it can reference the MongoDB server by name. So use this name, **not** ``localhost``. The database name
can be anything you want and does not need to be setup ahead of time. In this case,
``test`` is used.
![enter connection info](https://lh3.googleusercontent.com/B0fr_we_crNcwAqZN9vjVAvfrBzhTwh-SFicTMa9REy344098HK9yM-DzeXQLgVZqDdad92r=s0 "local_connection_info.png")

![connect to the database](https://lh3.googleusercontent.com/Mim6FmTRIv9jBHlRe537ScabNdMQdZy-K06uTxFyETdcUNwMxPBeo93NujIJVvHto8KWqMX8=s0 "about_to_hit_connect_now.png")

Finally the mongoclient UI should inform you that you have a successful connection
and begin to show pretty graphs and an easy way to add database entries(_documents_).


![final connection view](https://lh3.googleusercontent.com/NgPmiUPVxstBvMCG7GfTZXM_AG2onkGisKmCuHoHa7nGLlfZ8zhfRsVFmR2zzrhrFtFF2PLL=s0 "final_connection_view.png")
###  How to access the MongoDB CLI

Docker ``exec`` action allows you to access the mongo CLI

```
% docker exec -it MongoDB mongo               
MongoDB shell version v3.4.1
connecting to: MongoDB://127.0.0.1:27017
MongoDB server version: 3.4.1
Server has startup warnings:
2016-12-26T19:13:05.646+0000 I CONTROL  [initandlisten] ** WARNING: Access control is not enabled for the database.
2016-12-26T19:13:05.646+0000 I CONTROL  [initandlisten] **          Read and write access to data and configuration is unrestricted.
2016-12-26T19:13:05.646+0000 I CONTROL  [initandlisten]
> show dbs
admin  0.000GB
local  0.000GB
```
