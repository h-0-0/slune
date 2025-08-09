import unittest
from slune.utils import dict_to_strings, strings_to_dict


class TestDictToStringsEdgeCases(unittest.TestCase):
    def test_empty_dict(self):
        self.assertEqual(dict_to_strings({}), [])

    def test_ready_for_cl_true(self):
        d = {"alpha": 0.1, "beta": True, "gamma": 3}
        out = dict_to_strings(d, ready_for_cl=True)
        self.assertEqual(sorted(out), sorted(["--alpha=0.1", "--beta=True", "--gamma=3"]))


class TestStringsToDictEdgeCases(unittest.TestCase):
    def test_empty_list(self):
        self.assertEqual(strings_to_dict([]), {})

    def test_scientific_and_negative_numbers(self):
        s = ["lr=1e-3", "momentum=-0.9", "epochs=10"]
        out = strings_to_dict(s)
        self.assertEqual(out["lr"], 1e-3)
        self.assertEqual(out["momentum"], -0.9)
        self.assertEqual(out["epochs"], 10)

    def test_value_with_trailing_dot(self):
        s = ["x=3."]
        out = strings_to_dict(s)
        self.assertEqual(out["x"], 3.0)

    def test_no_equals_raises(self):
        with self.assertRaises(ValueError):
            strings_to_dict(["arg1-1"])  # missing '='


if __name__ == "__main__":
    unittest.main()