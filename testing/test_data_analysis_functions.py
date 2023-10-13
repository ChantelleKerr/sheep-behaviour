import unittest
import pandas as pd
from pandas.testing import assert_frame_equal
from data_analysis.plot import AnalyseSheep

sampleDataFile = "testing/test_data.csv"
expectedData = pd.DataFrame({'ACCEL_X': [236, 223, 262], 'ACCEL_Y': [28, 56, 12], 'ACCEL_Z': [471, 503, 497], 'DATE': [pd.to_datetime("2023-02-15 08:03:12"), pd.NaT, pd.to_datetime("2023-03-02 10:09:12")]})
sampleStartDate = "2023-02-15 08:03:12"
sampleEndDate   = "2023-03-02 10:09:12"

class TestDataAnalysis(unittest.TestCase):
    
    def setUp(self):
        analyseSheep = AnalyseSheep()
        self.date = analyseSheep.find_start_and_end_data(sampleDataFile, sampleStartDate, sampleEndDate)
    
    def test_start_and_end_data(self):
        assert_frame_equal(self.date, expectedData, "Start and end data location error")

if __name__ == "__main__":
    unittest.main()