---
title: Parse Sensu Client Logs Using Logstash
tags: ['logstash', 'json']
---

I had a need to analyze Sensu client log files in
``/var/log/sensu`` for historial CPU, disk and network data.

Web search revealed I should give [Logstash]('https://www.elastic.co/products/logstash') a try.

I decided I would try and also install ElastichSearch and Kibana. My distro
of choice is of cause Ubuntu, in this case Ubuntu 14.04

## Install Logstash

[Download Logstash deb]('https://www.elastic.co/downloads/logstash')
and install it using ``dpkg``

```
# sudo dpkg -i logstash_1.5.0-1_all.deb
```

Logstash service did not work me. So for the rest of this post, I just manually
called logstash from a terminal

## Install ElasticSearch

[Download ElasticSearch deb]('https://www.elastic.co/downloads/elasticsearch')
and install it using ``dpkg``

```
sudo dpkg -i elasticsearch-1.5.2.deb
```

Elasticsearch did start as a service ``sudo service elasticsearch start``
and I went to [http://localhost:9200]('http://localhost:9200') to confirm
it worked.

## Install Kibana

[Download Kibana Linux tar archive]('https://www.elastic.co/downloads/kibana')
and install it using ``tar``

```
tar xvfz kibana-4.0.2-linux-x64.tar.gz $HOME/apps
```

Kibana is by default, in ``config/kibana.yml`` configured to find a
elasticsearch server running at localhost:9200. so just start kibana using
``./bin/kibana`` in the expanded tar archive.

## Delete any ``sincedb`` files

Remove any ``$HOME/.sincedb*`` files. This keeps track of the current position
of monitored log files. When I first started experimenting with Logstash, it
created the ``sincedb`` files which prevented the sensu files from being
reparsed after I fixed the logstash config. After deleting these files, Logstash
correctly reparsed the Sensu log files and I was happy.

## Create Logstash Config file

### $HOME/tmp/logstash.config
```

# delete $HOME/.since_db files to reparse files
input {
  file {
     type => "sensu_logs"
     path => "/home/stanley/tmp/sensu/sensu-client*"
     start_position => "beginning"
  }
}

filter {
  json {
     source => "message"
  }
}
output {
  elasticsearch {
    host => '127.0.0.1'
  }
}

```

## Run Logstash

```
# /opt/logstash/bin/logstash agent -f logstash_config
```

This is a breakdown of what Logstash is doing:

Parse any file, **from the beginning**,  in ``/home/stanley/tmp/sensu`` that
starts with ``sensu-client``. The ``file`` input plugin splits up the file at
the delimiter, by default a ``\n``(carriage return), and then returns a
structure for each entry that looks like this:


```
{
       "message" =>
"{\"timestamp\":\"2015-05-15T02:17:20.561814-0700\",\"level\":\"info\",\"message\":\"publishing
check
result\",\"payload\":{\"client\":\"my-server\",\"check\":{\"handlers\":[\"graphite\"],\"type\":\"metric\",\"command\":\"/opt/sensu/embedded/bin/ruby
/etc/sensu/plugins/cpu-metrics.rb -s
os.inf.net.sw.my-server.cpu\",\"standalone\":true,\"interval\":60,\"name\":\"cpu-metrics\",\"issued\":1431681438,\"executed\":1431681438,\"duration\":2.0319999999999996,\"output\":\"os.inf.net.sw.my-server.cpu.total.user
844451226 1431681440\\n\",\"status\":0}}}",
      "@version" => "1",
    "@timestamp" => "2015-05-17T12:08:57.237Z",
          "type" => "browsers",
          "host" => "stanleyk-pc",
          "path" => "/home/stanleyk/tmp/sensu/sensu-client.log"
}

```

Logstash then takes the value of the ``message`` hash key and applies the
``json`` filter to it. The filter is smart in that it recursively goes down the
json output and outputs each json field and its value. So the output then
becomes like this

```
{
       "message" => "publishing check result",
      "@version" => "1",
    "@timestamp" => "2015-05-17T12:13:13.167Z",
          "type" => "browsers",
          "host" => "stanleyk-pc",
          "path" => "/home/stanleyk/tmp/sensu/sensu-client.log",
     "timestamp" => "2015-05-15T02:17:20.561814-0700",
         "level" => "info",
       "payload" => {
        "client" => "my-server",
         "check" => {
              "handlers" => [
                [0] "graphite"
            ],
                  "type" => "metric",
               "command" => "/opt/sensu/embedded/bin/ruby
/etc/sensu/plugins/cpu-metrics.rb -s os.inf.net.sw.my-server.cpu",
            "standalone" => true,
              "interval" => 60,
                  "name" => "cpu-metrics",
                "issued" => 1431681438,
              "executed" => 1431681438,
              "duration" => 2.0319999999999996,
                "output" => "os.inf.net.sw.my-server.cpu.total.user 844451226
1431681440\n",
                "status" => 0
        }
    }
}

```

What I don't know yet, and I will update the post, is how to take the
``payload.check.output`` value and extract the value so that I can have a field
called ``payload.check.output.cpu.total.user`` with a value of 844451226. Not
sure yet why ``cpu-metrics.rb`` prints 2 values for the total user cpu entry.

These entries are feed into the output elasticsearch plugin that adds the
entries into the elasticsearch datastore.


## Viewing Data in Kibana

I will update the post shortly with this info
