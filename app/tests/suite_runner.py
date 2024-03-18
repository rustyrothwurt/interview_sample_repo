import unittest
from . import test_benfords_law
from . import test_models
from . import test_pandas_ingestion


def get_test_suite():
    suite = unittest.TestSuite()
    for mod in [test_benfords_law, test_pandas_ingestion, test_models]:
        suite.addTest(unittest.TestLoader().loadTestsFromModule(mod))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(get_test_suite())
