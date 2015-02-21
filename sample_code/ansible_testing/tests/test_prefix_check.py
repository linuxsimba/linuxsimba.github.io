import mock
import library.prefix_check as prefix_check
from nose.tools import assert_equals, set_trace

@mock.patch('library.prefix_check.check_if_route_exists')
@mock.patch('library.prefix_check.AnsibleModule')
def test_module_args(mock_module,
                     mock_route_check):
    """
    prefix_check - test module arguments
    """
    prefix_check.main()
    mock_module.assert_called_with(
        argument_spec={
          'prefix': {'required': True, 'type': 'str'},
          'timeout': {'type': 'int', 'default': 5},
        })

@mock.patch('library.prefix_check.check_if_route_exists')
@mock.patch('library.prefix_check.AnsibleModule')
def test_main_exit_functionality_success(mock_module,
                     mock_route_check):
    """
    prefix_check - test_main_exit_functionality - success
    """

    # This creates a instance of the AnsibleModule mock.
    instance = mock_module.return_value

    # What happens the route is found. Check that correct
    # exit function is called
    mock_route_check.return_value = True

    prefix_check.main()

    # AnsibleModule.exit_json should be called
    # "changed" var should be false
    instance.exit_json.assert_called_with(
            msg='Route Found', changed=False)

    # AnsibleModule.fail_json should not be called
    assert_equals(instance.fail_json.call_count, 0)

@mock.patch('library.prefix_check.check_if_route_exists')
@mock.patch('library.prefix_check.AnsibleModule')
def test_main_exit_functionality_failure(mock_module,
                     mock_loop_route_check):
    """
    prefix_check - test_main_exit_functionality - failure
    """
    instance = mock_module.return_value

    # What happens when the check_if_route_exists returns False
    # that is route is not found
    mock_loop_route_check.return_value = False

    prefix_check.main()

    # AnsibleModule.exit_json should be activated
    assert_equals(instance.exit_json.call_count, 0)

    # AnsibleModule.fail_json should be called
    instance.fail_json.assert_called_with(
        msg='Route not Found. Check Routing Configuration')


@mock.patch('library.prefix_check.single_route_check_run')
@mock.patch('library.prefix_check.AnsibleModule')
def test_route_check_route_found(mock_module, mock_single_run):
    """
    prefix_check - test action when prefix is found
    """

    # on success, single_route_check_run() will return true
    mock_single_run.return_value = True
    result = prefix_check.check_if_route_exists(mock_module)
    assert_equals(result, True)


@mock.patch('library.prefix_check.single_route_check_run')
@mock.patch('library.prefix_check.AnsibleModule')
def test_route_check_route_found(mock_module, mock_single_run):
    """
    prefix_check - test action when prefix is found
    """

    # on success, single_route_check_run() will return true
    mock_single_run.return_value = True
    result = prefix_check.check_if_route_exists(mock_module)
    assert_equals(result, True)


@mock.patch('library.prefix_check.time.sleep')
@mock.patch('library.prefix_check.single_route_check_run')
@mock.patch('library.prefix_check.AnsibleModule')
def test_route_check_route_timeout_occurs(mock_module,
        mock_single_run, mock_sleep):
    """
    prefix_check - test action when prefix not found. timeout occurs
    """
    # define some important variables for the test.
    mock_module.timeout = 5
    poll_interval = 5

    # on failure, single_route_check_run() will return false
    mock_single_run.return_value = False

    # Run the function under test
    result = prefix_check.check_if_route_exists(mock_module)

    # Confirm that function failed
    assert_equals(result, False)

    # Also check that the poll interval works correctly.
    # Mock time.sleep and check that it was executed
    # (poll_interface/timeout) times. In this case 5 times.
    assert_equals(mock_sleep.call_count, poll_interval)


@mock.patch('library.prefix_check.AnsibleModule')
def test_ip_route_show_execution(mock_module):
    """
    prefix_check - test ip route show execution
    """

    # define necessary variables. Prefix was initial
    # set in the main() function. Needs to be hardcoded in this test.
    mock_module.prefix = '10.1.1.0/24'

    # AnsibleModule.run_command outputs list of output. Make
    # sure to mimic this for the test.
    mock_module.run_command.return_value = (1,'ip route stuff', None)

    # Run the function under test
    prefix_check.single_route_check_run(mock_module)

    #Confirm command outputs used to get prefix info
    mock_module.run_command.assert_called_with('/sbin/ip route show 10.1.1.0/24')
