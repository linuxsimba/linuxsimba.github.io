---
title: Sensu Triggered Alerting of Quagga Routing Crashes
tags: ['monitoring', 'sensu']
---

I have been testing various monitoring systems lately. This month I am looking
at [Sensu](https://sensuapp.org).
When I deployed Quagga, it comes with a little [monit](https://mmonit.com/monit)
type application called
[watchquagga](http://manpages.ubuntu.com/manpages/trusty/man8/watchquagga.8.html).
This application, within a few seconds, restarts a failed routing
protocol, like ospf6d or bgpd. Watching the routing protocol processes using
[check-proc.rb](https://github.com/sensu/sensu-community-plugins/blob/master/plugins/processes/check-procs.rb) does not help.

So I needed to write a triggered Sensu alert within the BASH script that
restarts the routing protocol. Because watchquagga does not currently support
issuing a script when it reloads a routing protocol, I had to hack the
`/etc/init.d/quagga` startup script. Not sure how this hack would work on a
systemd system.

Here is a snippet of the appropriate section, that was modified.

<pre><code>
# Starts the server if it's not alrady running according to the pid file.
# The Quagga daemons creates the pidfile when starting.
start()
{
  if [ "$1" = "watchquagga" ]; then

    # We may need to restart watchquagga if new daemons are added and/or
    # removed
    if started "$1" ; then
      stop watchquagga
    else
      # Echo only once. watchquagga is printed in the stop above
      echo -n " $1"
    fi


    start-stop-daemon \
      --start \
      --pidfile=`pidfile $1` \
      --exec "$D_PATH/$1" \
      -- \
      "${watchquagga_options[@]}"

    <strong>
    /etc/sensu/plugins/triggers/quagga-reload-event.rb --handler pagerduty,logstash "${watchquagga_options[@]}"
    </strong>
  elif [ -n "$2" ]; then
    echo -n " $1-$2"
    if ! check_daemon $1 $2

...
.......
</code></pre>

The `quagga-reload-event.rb` script takes the watchquagga options and strips
all options leaving only the routing protocols that were reloaded in the
argument string list. This is then passed as a message to the ``send_event()``
function so that the user can be told exactly which routing protocols were
restarted.

In the `quagga-reload-event.rb` file, the magic to send a Sensu event without
using a check is shown below

```
require 'socket'
require 'json'

def send_event(metric_name, options, msg, check_type='standard')
  data = {
    'name'      => metric_name,
    'type'      => check_type,
    'output'    => msg,
    # options is an OpenStruct object
    'handlers'  => options.handler,
    'status'    => 2
  }
  # Dump the data to the socket
  socket = TCPSocket.new '127.0.0.1', 3030
  socket.print data.to_json
  socket.close
end

```

Here is an image of the alert on Uchiwa
![Sensu Quagga](https://lh3.googleusercontent.com/-exBfP1FJFjI/Vnt4Acs5rMI/AAAAAAAAIPA/VTyB96Hv2vQ/s0/Screenshot+from+2015-12-23+23%253A42%253A38.png "sensu_quagga.png")
