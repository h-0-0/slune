import unittest
import os
import pandas as pd
from slune.savers import SaverCsv
from slune.loggers import LoggerDefault

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
        saver = SaverCsv(LoggerDefault(), ["--folder3=0.3", "--folder2=0.2", "--folder1=0.1"], root_dir=self.test_dir)

        # Test if get_match finds correct match and builds correct directory path using the parameters
        matching_dir = saver.get_match(["--folder3=0.3", "--folder2=0.2", "--folder1=0.1"])
        self.assertEqual(matching_dir, os.path.join(self.test_dir, "--folder1=0.1/--folder2=0.2/--folder3=0.3"))

    def test_get_match_partial_match(self):
        # Create a SaverCsv instance
        saver = SaverCsv(LoggerDefault(), ["--folder2=0.2", "--folder1=0.1"], root_dir=self.test_dir)

        # Test if get_match finds correct match and builds correct directory path using the parameters
        matching_dir = saver.get_match(["--folder2=0.2", "--folder1=0.1"])
        self.assertEqual(matching_dir, os.path.join(self.test_dir, "--folder1=0.1/--folder2=0.2"))

    def test_get_match_different_values(self):
        # Create a SaverCsv instance
        saver = SaverCsv(LoggerDefault(), ["--folder2=2.2", "--folder1=1.1"], root_dir=self.test_dir)

        # Test if get_match finds correct match and builds correct directory path using the parameters
        matching_dir = saver.get_match(["--folder2=2.2", "--folder1=1.1"])
        self.assertEqual(matching_dir, os.path.join(self.test_dir, "--folder1=1.1/--folder2=2.2"))

    def test_get_match_too_deep(self):
        # Create a SaverCsv instance
        saver = SaverCsv(LoggerDefault(), ["--folder2=0.2", "--folder3=0.3"], root_dir=self.test_dir)

        # Test if get_match finds correct match and builds correct directory path using the parameters
        matching_dir = saver.get_match(["--folder2=0.2", "--folder3=0.3"])
        self.assertEqual(matching_dir, os.path.join(self.test_dir, '--folder2=0.2', '--folder3=0.3'))

    def test_get_match_no_match(self):
        # Create a SaverCsv instance
        saver = SaverCsv(LoggerDefault(), ["--folder_not_there=0", "--folder_also_not_there=0.1"], root_dir=self.test_dir)

        # Test if get_match finds correct match and builds correct directory path using the parameters
        matching_dir = saver.get_match(["--folder_not_there=0", "--folder_also_not_there=0.1"])
        self.assertEqual(matching_dir, os.path.join(self.test_dir, "--folder_not_there=0/--folder_also_not_there=0.1"))

    def test_get_path_no_results(self):
        # Create a SaverCsv instance
        saver = SaverCsv(LoggerDefault(), ["--folder5=0.5","--folder1=0.1", "--folder6=0.6"], root_dir=self.test_dir)

        # Test if get_path gets the correct path
        path = saver.current_path
        self.assertEqual(path, os.path.join(self.test_dir, "--folder1=0.1/--folder5=0.5/--folder6=0.6/results_0.csv"))

    def test_get_path_already_results(self):
        # Create a SaverCsv instance
        saver = SaverCsv(LoggerDefault(), ["--folder3=0.3", "--folder2=0.2", "--folder1=0.1"], root_dir=self.test_dir)

        # Test if get_path gets the correct path
        path = saver.current_path
        self.assertEqual(path, os.path.join(self.test_dir, "--folder1=0.1/--folder2=0.2/--folder3=0.3/results_1.csv"))

    def test_save_collated(self):
        # Create a SaverCsv instance
        saver = SaverCsv(LoggerDefault(), ["--folder3=0.3", "--folder2=0.2", "--folder1=0.1"], root_dir=self.test_dir)
        # Create a data frame with some results
        results = pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]})
        # Save the results
        saver.save_collated_from_results(results)
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
        saver.save_collated_from_results(results)
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
    
    def test_creates_path_if_no_full_match(self):
        # Create a SaverCsv instance
        saver = SaverCsv(LoggerDefault(), ["--folder3=0.03", "--folder2=0.02", "--folder1=0.01"], root_dir=self.test_dir)
        # Create a data frame with some results
        results = pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]})
        # Save the results
        saver.save_collated_from_results(results)
        # Check if the results were saved correctly
        read_results = pd.read_csv(os.path.join(self.test_dir, "--folder1=0.01/--folder2=0.02/--folder3=0.03/results_0.csv"))
        self.assertEqual(read_results.shape, (3,2))
        self.assertEqual(results.columns.tolist(), read_results.columns.tolist())
        read_values = [x for x in read_results.values.tolist() if str(x) != 'nan']
        values = [x for x in results.values.tolist() if str(x) != 'nan']
        self.assertEqual(values, read_values)
        # Remove the results file
        os.remove(os.path.join(self.test_dir, '--folder1=0.01', '--folder2=0.02', '--folder3=0.03', 'results_0.csv'))
        os.rmdir(os.path.join(self.test_dir, '--folder1=0.01', '--folder2=0.02', '--folder3=0.03'))
        os.rmdir(os.path.join(self.test_dir, '--folder1=0.01', '--folder2=0.02'))
        os.rmdir(os.path.join(self.test_dir, '--folder1=0.01'))
        
# TODO: add tests for root_dir that has '/'s in it

class TestSaverCsvReadMethod(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory with some CSV files for testing
        self.test_dir = 'test_directory'
        os.makedirs(self.test_dir, exist_ok=True)

        # Creating some CSV files with specific subdirectory paths
        self.csv_files = [
            'dir1/file1.csv',
            'dir2/file2.csv',
            'dir1/subdir1/file3.csv',
            'dir2/subdir2/file4.csv',
            'dir2/subdir2/subdir3/file5.csv'
        ]

        for i, file in enumerate(self.csv_files):
            file_path = os.path.join(self.test_dir, file)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            # Create a data frame with different values for each CSV file
            if file_path == 'dir2/subdir2/subdir3/file5.csv':
                results = pd.DataFrame({'a': [i+1,i+2,i+3], 'b': [i+4,i+5,i+6], 'c': [i+7,i+8,i+9]})
            else:
                results = pd.DataFrame({'a': [i+1,i+2,i+3], 'b': [i+4,i+5,i+6]})
            # Save the results
            results.to_csv(file_path, mode='w', index=False)
        # The data frames we created should look like this: 
        # file1.csv: a b    
        #            1 4
        #            2 5
        #            3 6
        # file2.csv: a b
        #            2 5
        #            3 6
        #            4 7
        # file3.csv: a b
        #            3 6
        #            4 7
        #            5 8
        # file4.csv: a b
        #            4 7
        #            5 8
        #            6 9
        # file5.csv: a b
        #            5 8
        #            6 9
        #            7 10

    def tearDown(self):
        # Clean up the temporary directory and files after testing
        for root, dirs, files in os.walk(self.test_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.test_dir)

    def test_read_max_metric(self):
        # Create some params to use for testing
        params = ['dir1', 'subdir1']
        # Create an instance of SaverCsv
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

        # Call the read method to get min and max values
        max_param_a, max_value_a = saver.read(params, 'a')
        max_param_b, max_value_b = saver.read(params, 'b')

        # Perform assertions based on your expectations
        self.assertEqual(max_param_a, ['dir1','subdir1','file3.csv'])
        self.assertEqual(max_param_b, ['dir1','subdir1','file3.csv'])
        self.assertEqual(max_value_a, 5)
        self.assertEqual(max_value_b, 8)
    
    def test_read_min_metric(self):
        # Create some params to use for testing
        params = ['dir1', 'subdir1']
        # Create an instance of SaverCsv
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

        # Call the read method to get min and max values
        max_param_a, min_value_a = saver.read(params, 'a', min_max='min')
        max_param_b, min_value_b = saver.read(params, 'b', min_max='min')

        # Perform assertions based on your expectations
        self.assertEqual(max_param_a, ['dir1','subdir1','file3.csv'])
        self.assertEqual(max_param_b, ['dir1','subdir1','file3.csv'])
        self.assertEqual(min_value_a, 3)
        self.assertEqual(min_value_b, 6)

    def test_read_nonexistent_metric(self):
        # Create some params to use for testing
        params = ['dir1', 'subdir1']
        # Create an instance of SaverCsv
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

        # Call the read method to get min and max values
        with self.assertRaises(KeyError):
            saver.read(params, 'c')
        
    def test_multiple_matching_paths(self):
        # Create some params to use for testing
        params = ['dir2']
        # Create an instance of SaverCsv
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

        # Call the read method to get max value and params
        param, value = saver.read(params, 'a')

        # Check results are as expected
        self.assertEqual(param, ['dir2','subdir2','subdir3','file5.csv'])
        self.assertEqual(value, 7)
    
    def test_no_matching_paths(self):
        # Create some params to use for testing
        params = ['dir3']
        # Create an instance of SaverCsv
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

        # Call the read method to get max value and params
        with self.assertRaises(ValueError):
            saver.read(params, 'a')
    
    def test_multiple_matching_paths_missing_metrics(self):
        # Create some params to use for testing
        params = ['dir2']
        # Create an instance of SaverCsv
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

        # Call the read method to get max value and params
        with self.assertRaises(KeyError):
            saver.read(params, 'c')


if __name__ == "__main__":
    unittest.main()
