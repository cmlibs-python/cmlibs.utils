import os


_here = os.path.abspath(os.path.dirname(__file__))


def get_test_resource_name(name):
    return os.path.join(_here, 'resources', name)


def assert_almost_equal_list(testcase, actual_list, expected_list, delta):
    assert len(actual_list) == len(expected_list)
    for actual, expected in zip(actual_list, expected_list):
        testcase.assertAlmostEqual(actual, expected, delta=delta)
