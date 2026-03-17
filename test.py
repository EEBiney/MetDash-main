import unittest
import pandas as pd
from Python_script_test import load_data, process_heights, subtract_blank, normalize_ribitol

class TestPipeline(unittest.TestCase):
    def setUp(self):
        # Create dummy dataframes for testing
        self.temp = pd.DataFrame({
            "ID":[1,2,3],
            "C2":["a","b","c"],
            "C3":["x","y","z"],
            "Rawname":["S1.D","S2.D","BLK1.D"],
            "dummy1":[0,0,0],
            "dummy2":[0,0,0],
            "dummy3":[0,0,0],
            "Met1":[10,15,5],
            "ribitol":[5,10,2]
        })
        self.samp = pd.DataFrame({
            "Sample":["S1","S2","BLK1"],
            "Rawname":["S1","S2","BLK1"]
        })

    def test_process_heights(self):
        heights = process_heights(self.temp, self.samp)
        self.assertIn("Met1", heights.columns)

    def test_subtract_blank(self):
        heights = process_heights(self.temp, self.samp)
        heights, BK = subtract_blank(heights, self.samp)
        self.assertTrue((BK >= 0).all())

    def test_normalize_ribitol(self):
        heights = process_heights(self.temp, self.samp)
        heights, BK = subtract_blank(heights, self.samp)
        heights = normalize_ribitol(heights)
        self.assertFalse(heights.isnull().values.any())

if __name__ == "__main__":
    unittest.main()
