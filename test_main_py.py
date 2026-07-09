import unittest

from main_py import build_plan_from_inputs


class InteractiveEntryPointTests(unittest.TestCase):
    def test_build_plan_from_inputs_returns_a_complete_mix(self):
        mix = build_plan_from_inputs(["PEDV", "PDCoV"], [30.0, 30.5], final_volume_ul=3000.0)

        self.assertEqual(len(mix["components"]), 2)
        self.assertAlmostEqual(mix["shared_diluent_volume_ul"], 1388.89, places=2)
        self.assertEqual(mix["components"][0]["virus"], "PEDV")
        self.assertEqual(mix["components"][1]["virus"], "PDCoV")


if __name__ == "__main__":
    unittest.main()
