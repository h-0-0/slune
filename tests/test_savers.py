import unittest
import os
import pandas as pd
from slune.savers import SaverCsv

class TestSaverCsv(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = 'test_directory'
        os.makedirs(os.path.join(self.test_dir, '--folder1=0.1', '--folder2=0.2', '--folder3=0.3'))
        os.makedirs(os.path.join(self.test_dir, '--folder1=0.1', '--folder2=0.22', '--folder3=0.33', '--folder4=0.4'))
        os.makedirs(os.path.join(self.test_dir, '--folder1=0.1', '--folder2=0.2', 'another_folder'))
        os.makedirs(os.path.join(self.test_dir, '--folder1=0.1', '--folder5=0.5', '--folder6=0.6'))
        # Add a results file at --folder1=0.1/--folder2=0.2/--folder3=0.3
        with open(os.path.join(self.test_dir, '--folder1=0.1', '--folder2=0.2', '--folder3=0.3', 'results_0.csv'), 'w') as f:
            f.write('')
        

    def tearDown(self):
        # Remove the temporary directory and its contents after testing  
        os.remove(os.path.join(self.test_dir, '--folder1=0.1', '--folder2=0.2', '--folder3=0.3', 'results_0.csv'))
        os.rmdir(os.path.join(self.test_dir, '--folder1=0.1', '--folder2=0.2', '--folder3=0.3'))
        os.rmdir(os.path.join(self.test_dir, '--folder1=0.1', '--folder2=0.22', '--folder3=0.33', '--folder4=0.4'))
        os.rmdir(os.path.join(self.test_dir, '--folder1=0.1', '--folder2=0.22', '--folder3=0.33'))
        os.rmdir(os.path.join(self.test_dir, '--folder1=0.1', '--folder2=0.2', 'another_folder'))
        os.rmdir(os.path.join(self.test_dir, '--folder1=0.1', '--folder2=0.2'))
        os.rmdir(os.path.join(self.test_dir, '--folder1=0.1', '--folder2=0.22'))
        os.rmdir(os.path.join(self.test_dir, '--folder1=0.1', '--folder5=0.5', '--folder6=0.6'))
        os.rmdir(os.path.join(self.test_dir, '--folder1=0.1', '--folder5=0.5'))
        os.rmdir(os.path.join(self.test_dir, '--folder1=0.1'))
        os.rmdir(self.test_dir)

    def test_get_match_full_match(self):
        # Create a SaverCsv instance
        saver = SaverCsv(["--folder3=0.3", "--folder2=0.2", "--folder1=0.1"], root_dir=self.test_dir)

        # Test if get_match finds correct match and builds correct directory path using the parameters
        matching_dir = saver.get_match(["--folder3=0.3", "--folder2=0.2", "--folder1=0.1"])
        self.assertEqual(matching_dir, os.path.join(self.test_dir, "--folder1=0.1/--folder2=0.2/--folder3=0.3"))

    def test_get_match_partial_match(self):
        # Create a SaverCsv instance
        saver = SaverCsv(["--folder2=0.2", "--folder1=0.1"], root_dir=self.test_dir)

        # Test if get_match finds correct match and builds correct directory path using the parameters
        matching_dir = saver.get_match(["--folder2=0.2", "--folder1=0.1"])
        self.assertEqual(matching_dir, os.path.join(self.test_dir, "--folder1=0.1/--folder2=0.2"))

    def test_get_match_different_values(self):
        # Create a SaverCsv instance
        saver = SaverCsv(["--folder2=2.2", "--folder1=1.1"], root_dir=self.test_dir)

        # Test if get_match finds correct match and builds correct directory path using the parameters
        matching_dir = saver.get_match(["--folder2=2.2", "--folder1=1.1"])
        self.assertEqual(matching_dir, os.path.join(self.test_dir, "--folder1=1.1/--folder2=2.2"))

    def test_get_match_too_deep(self):
        # Create a SaverCsv instance
        saver = SaverCsv(["--folder2=0.2", "--folder3=0.3"], root_dir=self.test_dir)

        # Test if get_match finds correct match and builds correct directory path using the parameters
        matching_dir = saver.get_match(["--folder2=0.2", "--folder3=0.3"])
        self.assertEqual(matching_dir, os.path.join(self.test_dir, "--folder2=0.2/--folder3=0.3"))

    def test_get_match_no_match(self):
        # Create a SaverCsv instance
        saver = SaverCsv(["--folder_not_there=0", "--folder_also_not_there=0.1"], root_dir=self.test_dir)

        # Test if get_match finds correct match and builds correct directory path using the parameters
        matching_dir = saver.get_match(["--folder_not_there=0", "--folder_also_not_there=0.1"])
        self.assertEqual(matching_dir, os.path.join(self.test_dir, "--folder_not_there=0/--folder_also_not_there=0.1"))

    def test_get_path_no_results(self):
        # Create a SaverCsv instance
        saver = SaverCsv(["--folder5=0.5","--folder1=0.1", "--folder6=0.6"], root_dir=self.test_dir)

        # Test if get_path gets the correct path
        path = saver.current_path
        self.assertEqual(path, os.path.join(self.test_dir, "--folder1=0.1/--folder5=0.5/--folder6=0.6/results_0.csv"))

    def test_get_path_already_results(self):
        # Create a SaverCsv instance
        saver = SaverCsv(["--folder3=0.3", "--folder2=0.2", "--folder1=0.1"], root_dir=self.test_dir)

        # Test if get_path gets the correct path
        path = saver.current_path
        self.assertEqual(path, os.path.join(self.test_dir, "--folder1=0.1/--folder2=0.2/--folder3=0.3/results_1.csv"))

    def test_save_collated(self):
        # Create a SaverCsv instance
        saver = SaverCsv(["--folder3=0.3", "--folder2=0.2", "--folder1=0.1"], root_dir=self.test_dir)
        # Create a data frame with some results
        results = pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]})
        # Save the results
        saver.save_collated(results)
        # Check if the results were saved correctly
        read_results = pd.read_csv(os.path.join(self.test_dir, "--folder1=0.1/--folder2=0.2/--folder3=0.3/results_1.csv"))
        self.assertEqual(read_results.shape, (3,2))
        self.assertEqual(results.columns.tolist(), read_results.columns.tolist())
        read_values = [x for x in read_results.values.tolist() if str(x) != 'nan']
        values = [x for x in results.values.tolist() if str(x) != 'nan']
        self.assertEqual(values, read_values)
        # Create another data frame with more results
        results = pd.DataFrame({'a': [7,8,9], 'd': [10,11,12]})
        # Save the results
        saver.save_collated(results)
        # Check if the results were saved correctly
        read_results = pd.read_csv(os.path.join(self.test_dir, "--folder1=0.1/--folder2=0.2/--folder3=0.3/results_1.csv"))
        results = pd.concat([pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]}), results], ignore_index=True)
        self.assertEqual(read_results.shape, (6,3))
        self.assertEqual(results.columns.tolist(), read_results.columns.tolist())
        read_values = [[j for j in i if str(j) != 'nan'] for i in read_results.values.tolist()]
        values = [[j for j in i if str(j) != 'nan'] for i in results.values.tolist()]
        self.assertEqual(read_values, values)
        # Remove the results file
        os.remove(os.path.join(self.test_dir, '--folder1=0.1', '--folder2=0.2', '--folder3=0.3', 'results_1.csv'))
        

if __name__ == "__main__":
    unittest.main()
