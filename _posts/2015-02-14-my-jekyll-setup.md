---
title: "Jekyll, Capistrano and RVM"
tags: ['rvm', 'jekyll']
---

Decided to use [Jekyll](http://jekyllrb.com/) to host my blog posts. Its really
cool! I love [Markdown](http://daringfireball.net/projects/markdown/syntax), so when I found [Jekyll](http://jekyllrb.com/), I was happy.

Here are the relevant sections of my Capistrano, Nginx and Vagrant setup that I use to test my web hosting setup on a Vagrant VM.

### nginx config: /etc/nginx/sites-available/linuxsimba
```

server {
        listen 80;

        root /home/vagrant/blog/current/_site;
        index index.html index.htm;

        server_name linuxsimba.com;

        location / {
                # First attempt to serve request as file, then
                # as directory, then fall back to displaying a 404.
                try_files $uri $uri/ =404;
                # Uncomment to enable naxsi on this location
                # include /etc/nginx/naxsi.rules
        }

        error_page 404 /404.html;
}

```

### Capistrano3 config
### Gemfile
```
....
......
gem 'capistrano', '~> 3.3.0'
gem 'capistrano-rvm'
gem 'capistrano-bundler'
```

### CapFile
```
....
......
gem 'capistrano', '~> 3.3.0'
gem 'capistrano-rvm'
gem 'capistrano-bundler'
....
........
```

### config/deploy.rb
```
lock '3.3.5'

set :rvm_type, :user
set :rvm_ruby_version, '2.2.0'
set :application, 'linuxsimba'
set :repo_url, 'http://github.com/skamithi/linuxsimba.git'
set :branch, 'master'
# executes jekyll with 'bundle exec'.
# Tried 'bundler_bins'. Didn't work.
# tried rvm_map_bins. only works in vagrant env not prod
# so disabled till I figure out why
# set :rvm_map_bins, fetch(:rvm_map_bins, []).push('jekyll')

namespace :deploy do

  task :update_jekyll do
    on roles(:app) do
      within "#{deploy_to}/current" do
        execute :bundle, "exec jekyll build"
      end
    end
  end

  after "deploy:symlink:release", "deploy:update_jekyll"
```

###config/deploy/vagrant.rb
```
....
......
role :app, %w{vagrant@192.168.33.10}
set :deploy_to, "/home/vagrant/blog"
...
.......

```

###VagrantFile
```

Vagrant.configure(2) do |config|
....
......
    # setup private network
     config.vm.network "private_network", ip: "192.168.33.10"
....
........

```

### /etc/hosts on Host PC
```
127.0.0.1 localhost
# remove linuxsimba.com when done with testing.
192.168.33.10 linuxsimba.com
```

Before executing [Capistrano](http://capistranorb.com/), I copied the public key of my host PC user to the `/home/vagrant/.ssh/authorized_keys` file on the Vagrant VM. Then, I confirmed the passwordless ssh setting by using `ssh vagrant@192.168.33.10`.

To run [Capistrano](http://capistranorb.com/), I use the command
`$ bundle exec cap vagrant deploy`



