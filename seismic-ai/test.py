import unittest
from lib import seismic_ai
from lib.seismic_ai.met import METData


class MyTestCase(unittest.TestCase):
    metData: METData

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_init()

    def test_init(self):
        self.metData = seismic_ai.met.loadData("testcase/data/met_test.json")

    def test_wswf(self):
        print(self.metData.wswf)
        print(self.metData)


if __name__ == '__main__':
    unittest.main()
