import unittest

from cmlibs.utils.misc import sha256sum

from utilities import get_test_resource_name

class ZincUtilsTestCase(unittest.TestCase):

    def test_sha_calculation(self):
        exf_file = get_test_resource_name('two_element_cube.exf')
        sha256 = sha256sum(exf_file)
        expected_sha256 = '4ebcf6ad54c7444855becbf43390fcd3f9e469c0ac31b5442810c91f91ec5ee5'
        self.assertEqual(expected_sha256, sha256)


if __name__ == "__main__":
    unittest.main()
