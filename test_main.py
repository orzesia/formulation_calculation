import unittest

from main import calculate_component, calculate_mix


class DilutionCalculatorTests(unittest.TestCase):
    def test_calculates_practical_dilution_and_volumes(self):
        result = calculate_component(
            stock_ct=23.3,
            target_ct=26.0,
            final_volume_ul=3000.0,
            component_count=1,
        )

        self.assertEqual(result["total_dilution_factor"], 8)
        self.assertEqual(result["additional_dilution_factor"], 2)
        self.assertEqual(result["shared_vial_dilution_factor"], 1)
        self.assertAlmostEqual(result["achieved_ct"], 26.28, places=2)
        self.assertAlmostEqual(result["rna_volume_ul"], 1500.0, places=2)

    def test_mix_includes_shared_vial_dilution_and_shared_diluent(self):
        mix = calculate_mix(
            [
                {"virus": "PEDV", "target_ct": 27.0},
                {"virus": "PDCoV", "target_ct": 27.0},
            ],
            final_volume_ul=3000.0,
        )

        self.assertEqual(len(mix["components"]), 2)
        self.assertEqual(mix["components"][0]["shared_vial_dilution_factor"], 2)
        self.assertEqual(mix["components"][0]["additional_dilution_factor"], 8)
        self.assertAlmostEqual(mix["shared_diluent_volume_ul"], 2676.14, places=2)

    def test_rejects_too_high_target(self):
        with self.assertRaises(ValueError):
            calculate_component(
                stock_ct=23.3,
                target_ct=32.5,
                final_volume_ul=3000.0,
                component_count=1,
            )


if __name__ == "__main__":
    unittest.main()
