---
title: Splitting String in Ansible - Get Last Element
tags: ['ansible', 'jinja2']
---

Working on a simple template that prints out a bind9 reverse lookup file.
Wanted to take an IP address and print out the last octet of it in the bind9
reverse lookup file.

### vars/main.yml

```yaml
demomgmt_hosts:
  demo1:
    mac: '11:22:33:44:55:66'
    ip: '192.168.0.3'
```

### templates/db.0.168.192.in-addr.arpa

```jinja
;
; BIND data file for 0.168.192.in-addr.arpa zone.
;
;
$ORIGIN 0.168.192.in-addr.arpa.
$TTL  604800
@ IN  SOA localhost. root.localhost. (
    1427819976    ; Serial
    604800    ; Refresh
    86400   ; Retry
    2419200   ; Expire
    604800  ) ; Negative Cache TTL
;
@   IN  NS  .
;
1   IN  PTR demomgmtvm.lab.local.
{% raw %}
{% for hostname, dnsattr in demomgmt_hosts.iteritems() %}
{{ dnsattr.ip.split('.')[-1] }} IN  PTR {{hostname}}.lab.local.
{% endfor %}
{% endraw %}

```
