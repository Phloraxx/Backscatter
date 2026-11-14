"""Offline tests for Backscatter's fixed, label-free HH signal filters.

No Earthdata credentials or source GeoTIFFs are needed.
Run: python -m unittest discover -s tests -v
"""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from evaluate_signal_coherence import confusion, local_median, methods, neighbor_count


class RadarSignalTests(unittest.TestCase):
    def setUp(self):
        self.base = np.full((12, 12), -12.0, dtype=np.float32)

    def test_unmodified_scene_has_no_signal_candidates(self):
        masks, _ = methods(self.base, self.base.copy())
        for decrease, increase in masks.values():
            self.assertFalse(np.any(decrease | increase))

    def test_single_pixel_speckle_is_suppressed(self):
        after = self.base.copy()
        after[5, 5] = -3.0
        masks, _ = methods(self.base, after)
        self.assertEqual(int(masks["raw"][1].sum()), 1)
        self.assertEqual(int(masks["median3"][1].sum()), 0)
        self.assertEqual(int(masks["coherent"][1].sum()), 0)

    def test_large_coherent_signal_is_retained(self):
        after = self.base.copy()
        after[3:10, 3:10] = -5.0
        masks, _ = methods(self.base, after)
        self.assertTrue(masks["coherent"][1][6, 6])
        self.assertFalse(np.any(masks["coherent"][0]))

    def test_change_direction_not_assumed_to_be_water(self):
        after = self.base.copy()
        after[3:10, 3:10] = -20.0
        masks, _ = methods(self.base, after)
        self.assertTrue(masks["coherent"][0][6, 6])
        self.assertFalse(np.any(masks["coherent"][1]))

    def test_missing_second_scene_does_not_create_detection(self):
        after = np.full_like(self.base, np.nan)
        masks, data = methods(self.base, after)
        self.assertEqual(int(data["common"].sum()), 0)
        for decrease, increase in masks.values():
            self.assertFalse(np.any(decrease | increase))

    def test_nan_median_requires_at_least_five_valid_neighbours(self):
        values = np.full((6, 6), np.nan, dtype=np.float32)
        values[1, 1] = values[1, 2] = values[2, 1] = values[2, 2] = -11.0
        result = local_median(values)
        self.assertTrue(np.isnan(result[2, 2]))
        values[3, 3] = -11.0
        result = local_median(values)
        self.assertAlmostEqual(float(result[2, 2]), -11.0)

    def test_neighbor_count_includes_center(self):
        values = np.zeros((5, 5), dtype=bool)
        values[2, 2] = True
        values[1, 2] = True
        self.assertEqual(int(neighbor_count(values)[2, 2]), 2)
        self.assertEqual(int(neighbor_count(values)[0, 0]), 0)

    def test_confusion_excludes_masked_reference_cells(self):
        pred = np.array([[True, False, True], [False, False, True]])
        true = np.array([[True, True, False], [False, False, False]])
        valid = np.array([[True, True, False], [True, False, True]])
        m = confusion(pred, true, valid)
        self.assertEqual((m["tp"], m["fp"], m["fn"], m["tn"]), (1, 1, 1, 1))
        self.assertAlmostEqual(m["f1"], 0.5)

    def test_no_reference_positives_does_not_claim_f1(self):
        false = np.zeros((2, 3), dtype=bool)
        outcome = confusion(false, false, np.ones_like(false))
        self.assertIsNone(outcome["f1"])


if __name__ == "__main__":
    unittest.main()
