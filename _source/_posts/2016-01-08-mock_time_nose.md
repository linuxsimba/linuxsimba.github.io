---
title: Mocking Time Using Nose and Mock
tags: ['nose', 'mock']
---

This is an example of how I mock `time.time()` using Nose and Mock

<pre><code>
import mock
from nose.tools import assert_equals
from simple_network_rates import base

class TestSimpleNetworkRates(object)

  def setup(self):
    self.instance = base.Base('eth1', 'sysfs', 'tx_bytes')

  @mock.patch('simple_network_rates.base.Base.create_wsp_file')
  @mock.patch('simple_network_rates.base.whisper.update')
  def test_write_wsp_file(self, mock_wsp_update,
                          mock_create_wsp_file):
      <strong>with mock.patch('simple_network_rates.base.time.time') as mock_time:</strong>
          <strong>mock_time.return_value = 1111</strong>
          self.instance.write_to_wsp_file(1234)
          assert_equals(mock_create_wsp_file.call_count, 1)
          mock_wsp_update.assert_called_with('')
</code></pre>

When I run `nosetests` I get the following result:

<pre><code>
=====================================================================
FAIL: test_base.TestSimpleNetworkRates.test_write_wsp_file
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/stanleyk/py2/local/lib/python2.7/site-packages/nose/case.py", line 197, in runTest
    self.test(*self.arg)
  File "/home/stanleyk/py2/local/lib/python2.7/site-packages/mock/mock.py", line 1305, in patched
    return func(*args, **keywargs)
  File "/home/stanleyk/git/simple-network-rates/tests/test_base.py", line 42, in test_write_wsp_file
    mock_wsp_update.assert_called_with('')
  File "/home/stanleyk/py2/local/lib/python2.7/site-packages/mock/mock.py", line 937, in assert_called_with
    six.raise_from(AssertionError(_error_message(cause)), cause)
  File "/home/stanleyk/py2/local/lib/python2.7/site-packages/six.py", line 718, in raise_from
    raise value
AssertionError: Expected call: update('')
<strong>Actual call: update('/var/run/eth1_sysfs_tx_bytes.wsp', 1234, 1111)</strong>
</code></pre>
