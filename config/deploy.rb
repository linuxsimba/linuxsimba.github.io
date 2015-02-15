# config valid only for current version of Capistrano
lock '3.3.5'

require 'capistrano/rvm'

set :rvm_ruby_string, 'ruby-2.2.0'
set :application, 'linuxsimba'
set :repo_url, 'http://github.com/skamithi/linuxsimba.git'
set :domain, "csf"
set :user,
set :deploy_to, "/home/#{user}/blog"
set :scm, "git"
set :deploy_via, :remote_cache
set :use_sudo, false
ssh_options[:format_agent], { :forward_agent => true, kesy: ['~/.vagrant.d/insecure_private_key']}

role :app, domain

