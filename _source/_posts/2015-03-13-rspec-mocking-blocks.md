---
title: Testing Ruby Blocks Output with Rspec3
---

Never had the pleasure before of mocking the output of a [Ruby
Block](http://rubylearning.com/satishtalim/ruby_blocks.html).

In my puppet module test, I had to mock IO::popen which reads some interesting
output into an instance variable

## Here is the some example code

```ruby
class IfaceReader
  @attr_accessor :currentconfig :desiredconfig
  def initialize(name)
    @currentconfig = copy_to_hash
  end

  def copy_to_hash
    json = ''
    IO.popen("/sbin/ifacereader #{@resource[:name]} -t json") do |ifacereader|
      json = ifacereader.read
    end
    JSON.parse(json)[0]
  rescue Exception => ex
      Puppet.warning("ifacereader failed: #{ex}")
  end
  ...
  .....
```

## And the Rspec3 Test for it
```ruby
require 'spec_helper'
require 'pry'

provider_resource = Puppet::Type.type(:my_interface)
provider_class = provider_resource.provider(:ruby)

describe provider_class do
  context 'config changed' do
    before do
      @loc_resource = provider_resource.new(
        name: 'eth1',
        vlans: ['1-10', '20'])
    end
    context 'config has changed' do
      before do
        current_hash = "[{\"vlans\": \"1-10 20",\"name\":\"eth1\"}]"
```
```ruby
        mock_reader = double()
        allow(mock_ifquery).to receive(:read).and_return(current_hash)
        allow(IO).to receive(:popen).and_yield(mock_reader)
```
```ruby
        @loc_provider = provider_class.new(@loc_resource)
      end
      # no change from current config and desired config
      subject { @loc_provider.config_changed? }
      it { is_expected.to be false }
    end
  end
```
