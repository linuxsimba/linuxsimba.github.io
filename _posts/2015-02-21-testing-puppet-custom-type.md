---
title: Testing Puppet Custom Type and Provider
tags: ['puppet']
---

Recently tasked with building puppet modules using a custom type and provider.

Watched some videos on how to do this on YouTube but then realized the best
training ground was the puppet source code. It also had some interesting spec
tests to learn from.

Here are some of the common rspec tests I gravitated towards.

1. Testing a`confine` call in a provider

_lib/puppet/provider/mycustomtype/ruby.rb_

```ruby
Puppet::Type.type(mycustomtype).provide :ruby do
  confine operatingsystem: [:debian]
end
```
----------

<i>spec/unit/provider/mycustomtype/ruby_spec.rb</i>

```ruby
require 'spec_helper'
provider_resource = Puppet::Type.type(:mycustomtype)
provider_class = provider_resource.provider(:ruby)

describe provider_class do
  context 'operating system confine' do
    subject do
       provider_class.confine_collection.summary[:variable][:operatingsystem]
    end
    it { is_expected.to eq ['debian'] }
  end
end
```

2. Testing a custom type property

_lib/puppet/type/mycustomtype.rb_

```ruby

Puppet::Type.newtype(:mycustomtype) do

  newproperty(:config_state) do
    desc "Reflect config state"

    defaultto :insync

    def retrieve
      prov = @resource.provider
      if prov && prov.respond_to?(:config_changed?)
        result = @resource.provider.config_changed?
      else
        errormsg = "Can't find func"
        fail Puppet::DevError, errormsg

      result? :outofsync : :insync
    end

    newvalue: outofsync
    newvalue: insync do
      prov = @resource.provider
      if prov && prov.respond_to?(:update_config)
        prov.update_config
      else
        errormsg = "Can't find func"
        fail Puppet::DevError, errormsg
      end
      nil
    end
  end
end

```
----------

<i>spec/unit/type/mycustomtype_spec.rb</i>

```ruby
require 'spec_helper'

mycustomtype = Puppet::Type.type(:mycustomtype)

describe mycustomtype do
 context 'config_state property' do
    before do
      @provider = double 'provider'
      allow(@provider).to receive(:name).and_return(:ruby)
      mycustomtype.stubs(:defaultprovider).returns @provider
      @customtype = mycustomtype.new(name: 'customtype')
    end

    subject { allow(@customtype.provider).to receive(:config_changed?) }
    let(:config_state_result) { @customtype.property(:ensure).retrieve }
    context 'when provider config_changed? is false' do
      before do
          subject.and_return(false)
      end
      it { expect(config_state_result).to eq(:insync) }
    end

    context 'when provider config_changed? is true' do
      before do
        subject.and_return(true)
      end
      it { expect(config_state_result).to eq(:outofsync) }
    end

    context 'insync provider call' do
      let(:provider) { @customtype.provider }
      let(:config_state_insync_exec) { @customtype.property(:config_state).set_insync }
      subject { config_state_insync_exec }
      it do
        expect(provider).to receive(:update_config).once
        subject
      end
    end
  end
end

```


3. [I do not take credit for this one](https://github.com/garethr/garethr-digitalocean/blob/master/spec/unit/type/droplet_spec.rb). Testing presence of custom properties and
parameters

_lib/puppet/type/mycustomtype.rb_

```ruby
Puppet::Type.newtype(:mycustomtype) do
  newparam(:foo) do
  end
  newparam(:bar) do
  end
end

```
-----------

<i>spec/unit/type/mycustomtype_spec.rb</i>

```ruby
require 'spec_helper'

mycustomtype = Puppet::Type.type(:mycustomtype)

describe mycustomtype do
  let :params do
    [ :foo, :bar ]
  end

  let :properties do
    [:config_state]
  end

  it 'should have expected properties' do
    properties.each do |property|
      expect(cl_ports.properties.map(&:name)).to be_include(property)
    end
  end

  it 'should have expected parameters' do
    params.each do |param|
      expect(cl_ports.parameters).to be_include(param)
    end
  end
end
```

