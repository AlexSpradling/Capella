from utilities.tooltips import TextExtractor 
import unittest

class TestSightReduction(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.test_cases = TextExtractor('text_files/capella_tests.md')

    def get_test_cases(self):
        # iterate through test cases, and extract the test cases
        test_cases = {}
        for key in self.test_cases.text_blocks:
            if key.startswith('test_case_'):
                test_cases[key] = self.test_cases.text_blocks[key]

        return test_cases

# test 
if __name__ == '__main__':
    unittest.main()   