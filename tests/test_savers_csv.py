import unittest
import os
import pandas as pd
from slune.savers.csv import SaverCsv
from slune.loggers.default import LoggerDefault
import numpy as np

class TestSaverCsvGetMatch(unittest.TestCase):
    def setUp(self):
        # Check if the test directory already exists, if it does remove it and all its contents
        if os.path.isdir('test_directory'):
            for root, dirs, files in os.walk('test_directory', topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir('test_directory')
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

    def test_full_match(self):
        # Create a SaverCsv instance
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

        # Test if get_match finds correct match and builds correct directory path using the parameters
        matching_dir = saver.get_match(["--folder3=0.3", "--folder2=0.2", "--folder1=0.1"])
        self.assertEqual(matching_dir, os.path.join(*[self.test_dir, '--folder1=0.1','--folder2=0.2','--folder3=0.3']))

    def test_partial_match(self):
        # Create a SaverCsv instance
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

        # Test if get_match finds correct match and builds correct directory path using the parameters
        matching_dir = saver.get_match(["--folder2=0.2", "--folder1=0.1"])
        self.assertEqual(matching_dir, os.path.join(*[self.test_dir, '--folder1=0.1','--folder2=0.2']))

    def test_partial_match_more_params(self):
        # Create a SaverCsv instance
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

        # Test if get_match finds correct match and builds correct directory path using the parameters
        matching_dir = saver.get_match(["--folder1=0.1", "--folder6=0.6", "--folder5=0.5", "--folder7=0.7"])
        self.assertEqual(matching_dir, os.path.join(*[self.test_dir, '--folder1=0.1','--folder5=0.5','--folder6=0.6','--folder7=0.7']))

    def test_different_values(self):
        # Create a SaverCsv instance
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

        # Test if get_match finds correct match and builds correct directory path using the parameters
        matching_dir = saver.get_match(["--folder2=2.2", "--folder1=1.1"])
        self.assertEqual(matching_dir, os.path.join(*[self.test_dir, '--folder1=1.1','--folder2=2.2']))

    def test_too_deep(self):
        # Create a SaverCsv instance
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

        # Test if get_match finds correct match and builds correct directory path using the parameters
        matching_dir = saver.get_match(["--folder2=0.2", "--folder3=0.3"])
        self.assertEqual(matching_dir, os.path.join(*[self.test_dir, '--folder2=0.2', '--folder3=0.3']))

    def test_no_match(self):
        # Create a SaverCsv instance
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

        # Test if get_match finds correct match and builds correct directory path using the parameters
        matching_dir = saver.get_match(["--folder_not_there=0", "--folder_also_not_there=0.1"])
        self.assertEqual(matching_dir, os.path.join(*[self.test_dir, '--folder_not_there=0','--folder_also_not_there=0.1']))

    def test_duplicate_params(self):
        # Create a SaverCsv instance
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

        # Test if get_match returns an error if there are duplicate parameters
        with self.assertRaises(ValueError):
            saver.get_match(["--folder1=0.1", "--folder1=0.2"])

    def test_existing(self):
        # Arrange
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        params = ['--folder2=0.20', '--folder1=0.1', '--folder3=0.3']
        expected_path = os.path.join(self.test_dir, '--folder1=0.1', '--folder2=0.2', '--folder3=0.3')

        # Act
        actual_path = saver.get_match(params)

        # Assert
        self.assertEqual(expected_path, actual_path)


class TestSaverCsvGetPath(unittest.TestCase):
    def setUp(self):
        # Check if the test directory already exists, if it does remove it and all its contents
        if os.path.isdir('test_directory'):
            for root, dirs, files in os.walk('test_directory', topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir('test_directory')
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

    def test_duplicate_params(self):
        # Create a SaverCsv instance
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

        # Test if get_path returns an error if there are duplicate parameters
        with self.assertRaises(ValueError):
            saver.get_path(["--folder1=0.1", "--folder1=0.2"])

    def test_no_results(self):
        # Create a SaverCsv instance
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

        # Test if get_path gets the correct path
        path = saver.get_path(["--folder5=0.5","--folder1=0.1", "--folder6=0.6"])
        self.assertEqual(path, os.path.join(*[self.test_dir, '--folder1=0.1','--folder5=0.5','--folder6=0.6','results_0.csv']))

    def test_already_results(self):
        # Create a SaverCsv instance
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

        # Test if get_path gets the correct path
        path = saver.get_path(["--folder3=0.3", "--folder2=0.2", "--folder1=0.1"]) 
        self.assertEqual(path, os.path.join(*[self.test_dir, '--folder1=0.1','--folder2=0.2','--folder3=0.3','results_1.csv']))

class TestSaverCsvSaveCollatedFromResults(unittest.TestCase):
    def setUp(self):
        # Check if the test directory already exists, if it does remove it and all its contents
        if os.path.isdir('test_directory'):
            for root, dirs, files in os.walk('test_directory', topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir('test_directory')
        # Create a temporary directory for testing
        self.test_dir = 'test_directory'
        os.makedirs(os.path.join(self.test_dir, 'folder1=0.1', 'folder2=0.2', 'folder3=0.3'))
        os.makedirs(os.path.join(self.test_dir, 'folder1=0.1', 'folder2=0.22', 'folder3=0.33', 'folder4=0.4'))
        os.makedirs(os.path.join(self.test_dir, 'folder1=0.1', 'folder2=0.2', 'another_folder'))
        os.makedirs(os.path.join(self.test_dir, 'folder1=0.1', 'folder5=0.5', 'folder6=0.6'))
        # Add a results file at folder1=0.1/folder2=0.2/folder3=0.3
        with open(os.path.join(self.test_dir, 'folder1=0.1', 'folder2=0.2', 'folder3=0.3', 'results_0.csv'), 'w') as f:
            f.write('')
        

    def tearDown(self):
        # Remove the temporary directory and its contents after testing  
        os.remove(os.path.join(self.test_dir, 'folder1=0.1', 'folder2=0.2', 'folder3=0.3', 'results_0.csv'))
        os.rmdir(os.path.join(self.test_dir, 'folder1=0.1', 'folder2=0.2', 'folder3=0.3'))
        os.rmdir(os.path.join(self.test_dir, 'folder1=0.1', 'folder2=0.22', 'folder3=0.33', 'folder4=0.4'))
        os.rmdir(os.path.join(self.test_dir, 'folder1=0.1', 'folder2=0.22', 'folder3=0.33'))
        os.rmdir(os.path.join(self.test_dir, 'folder1=0.1', 'folder2=0.2', 'another_folder'))
        os.rmdir(os.path.join(self.test_dir, 'folder1=0.1', 'folder2=0.2'))
        os.rmdir(os.path.join(self.test_dir, 'folder1=0.1', 'folder2=0.22'))
        os.rmdir(os.path.join(self.test_dir, 'folder1=0.1', 'folder5=0.5', 'folder6=0.6'))
        os.rmdir(os.path.join(self.test_dir, 'folder1=0.1', 'folder5=0.5'))
        os.rmdir(os.path.join(self.test_dir, 'folder1=0.1'))
        os.rmdir(self.test_dir)

    def test_general(self):
        # Create a SaverCsv instance
        saver = SaverCsv(LoggerDefault(), params={'folder3':0.3, 'folder2':0.2, 'folder1':0.1}, root_dir=self.test_dir)
        # Create a data frame with some results
        results = pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]})
        # Save the results
        saver.save_collated_from_results(results)
        # Check if the results were saved correctly
        read_results = pd.read_csv(os.path.join(*[self.test_dir, 'folder1=0.1','folder2=0.2','folder3=0.3','results_1.csv']))
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
        read_results = pd.read_csv(os.path.join(*[self.test_dir, 'folder1=0.1','folder2=0.2','folder3=0.3','results_1.csv']))
        results = pd.concat([pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]}), results], ignore_index=True)
        self.assertEqual(read_results.shape, (6,3))
        self.assertEqual(results.columns.tolist(), read_results.columns.tolist())
        read_values = [[j for j in i if str(j) != 'nan'] for i in read_results.values.tolist()]
        values = [[j for j in i if str(j) != 'nan'] for i in results.values.tolist()]
        self.assertEqual(read_values, values)
        # Remove the results file
        os.remove(os.path.join(self.test_dir, 'folder1=0.1', 'folder2=0.2', 'folder3=0.3', 'results_1.csv'))


    def test_creates_path_if_no_full_match(self):
        # Create a SaverCsv instance
        saver = SaverCsv(LoggerDefault(), params={'folder3':0.03, 'folder2':0.02, 'folder1':0.01}, root_dir=self.test_dir)
        # Create a data frame with some results
        results = pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]})
        # Save the results
        saver.save_collated_from_results(results)
        # Check if the results were saved correctly
        read_results = pd.read_csv(os.path.join(*[self.test_dir, 'folder1=0.01','folder2=0.02','folder3=0.03','results_0.csv']))
        self.assertEqual(read_results.shape, (3,2))
        self.assertEqual(results.columns.tolist(), read_results.columns.tolist())
        read_values = [x for x in read_results.values.tolist() if str(x) != 'nan']
        values = [x for x in results.values.tolist() if str(x) != 'nan']
        self.assertEqual(values, read_values)
        # Remove the results file
        os.remove(os.path.join(self.test_dir, 'folder1=0.01', 'folder2=0.02', 'folder3=0.03', 'results_0.csv'))
        os.rmdir(os.path.join(self.test_dir, 'folder1=0.01', 'folder2=0.02', 'folder3=0.03'))
        os.rmdir(os.path.join(self.test_dir, 'folder1=0.01', 'folder2=0.02'))
        os.rmdir(os.path.join(self.test_dir, 'folder1=0.01'))
        
    def test_root_dir_has_forwardslash(self):
        # Create a SaverCsv instance
        saver = SaverCsv(LoggerDefault(), {'folder3':0.3, 'folder2':0.2}, root_dir=os.path.join(self.test_dir,'folder1=0.1'))
        # Create a data frame with some results
        results = pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]})
        # Save the results
        saver.save_collated_from_results(results)
        # Check if the results were saved correctly
        read_results = pd.read_csv(os.path.join(*[self.test_dir, 'folder1=0.1','folder2=0.2','folder3=0.3','results_1.csv']))
        self.assertEqual(read_results.shape, (3,2))
        self.assertEqual(results.columns.tolist(), read_results.columns.tolist())
        read_values = [x for x in read_results.values.tolist() if str(x) != 'nan']
        values = [x for x in results.values.tolist() if str(x) != 'nan']
        self.assertEqual(values, read_values)
        # Remove the results file
        os.remove(os.path.join(self.test_dir, 'folder1=0.1', 'folder2=0.2', 'folder3=0.3', 'results_1.csv'))


class TestSaverCsvExists(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory with some CSV files for testing
        self.test_dir = 'test_directory'
        os.makedirs(self.test_dir, exist_ok=True)

        # Creating some CSV files with specific subdirectory paths
        self.csv_files = [
            os.path.join('dir1=None','file1.csv'),
            os.path.join('dir2=None','file2.csv'),
            os.path.join('dir1=None','subdir1=None','file3.csv'),
            os.path.join('dir2=None','subdir2=None','file4.csv'),
            os.path.join('dir2=None','subdir2=None','subdir3=None','file5.csv')
        ]

        for i, file in enumerate(self.csv_files):
            file_path = os.path.join(self.test_dir, file)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            # Create a data frame with different values for each CSV file
            if file_path == os.path.join('dir2','subdir2','subdir3','file5.csv'):
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

    def test_one_file(self):
        # Arrange
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        params = {'dir2':None, 'subdir2':None, 'subdir3':None}

        # Act
        result = saver.exists(params)

        # Assert
        self.assertEqual(result, 1)

    def test_multi_file(self):
        # Arrange
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        params = {'dir2':None}

        # Act
        result = saver.exists(params)

        # Assert
        self.assertEqual(result, 3)
    
    def test_no_file(self):
        # Arrange
        saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
        params = {'dir3':None}

        # Act
        result = saver.exists(params)

        # Assert
        self.assertEqual(result, 0)


class TestSaverCsvRead(unittest.TestCase):
    
        def setUp(self):
            # Create a temporary directory with some CSV files for testing
            self.test_dir = 'test_directory'
            os.makedirs(self.test_dir, exist_ok=True)
    
            # Creating some CSV files with specific subdirectory paths
            self.csv_files = [
                os.path.join('param1=1','param2=True','param3=3','results_0.csv'),
                os.path.join('param1=1','param2=True','param3=3','results_1.csv'),
                os.path.join('param1=1','param2=False','param3=3','results_0.csv'),
                os.path.join('param1=string', 'param2=1', 'param3=3', 'results_0.csv'),
            ]

            for i, file in enumerate(self.csv_files):
                file_path = os.path.join(self.test_dir, file)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                # Create a data frame with different values for each CSV file
                results = pd.DataFrame({'a': [i+1,i+2,i+3], 'b': [i+4,i+5,i+6]})
                # Save the results
                results.to_csv(file_path, mode='w', index=False)
            # The data frames we created should look like this:
            # --param1=1/--param2=True/--param3=3/results_0.csv: 
            #   a b
            #   1 4
            #   2 5
            #   3 6
            # --param1=1/--param2=True/--param3=3/results_1.csv:
            #   a b
            #   2 5
            #   3 6
            #   4 7
            # --param1=1/--param2=False/--param3=3/results_0.csv:
            #   a b
            #   3 6
            #   4 7
            #   5 8
            # --param1=string/--param2=1/--param3=3/results_0.csv:
            #   a b
            #   4 7
            #   5 8
            #   6 9
                
        def tearDown(self):
            # Clean up the temporary directory and files after testing
            for root, dirs, files in os.walk(self.test_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(self.test_dir)

        def test_select_by_max(self):
            # Create some params to use for testing
            params = {'param1':1, 'param2':True, 'param3':3}
            # Create an instance of SaverCsv
            saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

            # Call the read method to get min and max values
            max_param_a, max_value_a = saver.read(params, 'a', select_by='max', collate_by='mean')
            max_param_b, max_value_b = saver.read(params, 'b', select_by='max', collate_by='mean')
            self.assertEqual(1, len(max_param_a))
            self.assertEqual(1, len(max_param_b))
            self.assertEqual(1, len(max_value_a))
            self.assertEqual(1, len(max_value_b))
            max_param_a = max_param_a[0]
            max_param_b = max_param_b[0]
            max_value_a = max_value_a[0]
            max_value_b = max_value_b[0]
            # Perform assertions based on your expectations
            self.assertEqual(max_param_a, ['param1=1', 'param2=True', 'param3=3'])
            self.assertEqual(max_param_b, ['param1=1', 'param2=True', 'param3=3'])
            self.assertEqual(max_value_a, 3.5)
            self.assertEqual(max_value_b, 6.5)

        def test_select_by_min(self):
            # Create some params to use for testing
            params = {'param1':1, 'param2':True, 'param3':3}
            # Create an instance of SaverCsv
            saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

            # Call the read method to get min and max values
            min_param_a, min_value_a = saver.read(params, 'a', select_by='min')
            min_param_b, min_value_b = saver.read(params, 'b', select_by='min')
            self.assertEqual(1, len(min_param_a))
            self.assertEqual(1, len(min_param_b))
            self.assertEqual(1, len(min_value_a))
            self.assertEqual(1, len(min_value_b))
            min_param_a = min_param_a[0]
            min_param_b = min_param_b[0]
            min_value_a = min_value_a[0]
            min_value_b = min_value_b[0]

            # Perform assertions based on your expectations
            self.assertEqual(min_param_a, ['param1=1', 'param2=True', 'param3=3'])
            self.assertEqual(min_param_b, ['param1=1', 'param2=True', 'param3=3'])
            self.assertEqual(min_value_a, 1.5)
            self.assertEqual(min_value_b, 4.5)

        def test_select_by_all(self):
            # Create some params to use for testing
            params = {'param1':1, 'param2':True, 'param3':3}
            # Create an instance of SaverCsv
            saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

            # Call the read method to get all values matching the params
            params, values = saver.read(params, 'a', select_by='all', collate_by='mean')

            # Perform assertions based on your expectations
            self.assertEqual(params, [['param1=1', 'param2=True', 'param3=3']])
            eq = np.array_equal(values, [[1.5, 2.5, 3.5]])
            self.assertEqual(True, eq)

            # Now we check that we get an error if there is a mismatch in the number of metrics returned by logger
            file_path = os.path.join(self.test_dir, 'param1=1', 'param2=True', 'param3=3', 'results_2.csv')
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            # Create a data frame with different values for each CSV file
            results = pd.DataFrame({'a': [1,2,3,4,5], 'b': [4,5,6,7,8]})
            # Save the results
            results.to_csv(file_path, mode='w', index=False)

            # Create some params to use for testing
            params = {'param1':1, 'param2':True, 'param3':3}
            with self.assertRaises(ValueError):
                saver.read(params, 'a', select_by='all', collate_by='mean')
            # Remove the results file
            os.remove(file_path)

        def test_select_by_last(self):
            # Create some params to use for testing
            params = {'param1':1, 'param2':True, 'param3':3}
            # Create an instance of SaverCsv
            saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

            # Call the read method to get last values
            param, value = saver.read(params, 'a', select_by='last', collate_by='mean')

            # Perform assertions based on your expectations
            self.assertEqual(param, [['param1=1', 'param2=True', 'param3=3']])
            self.assertEqual(value, [3.5])
        
        def test_select_by_first(self):
            # Create some params to use for testing
            params = {'param1':1, 'param2':True, 'param3':3}
            # Create an instance of SaverCsv
            saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

            # Call the read method to get first values
            param, value = saver.read(params, 'a', select_by='first', collate_by='mean')

            # Perform assertions based on your expectations
            self.assertEqual(param, [['param1=1', 'param2=True', 'param3=3']])
            self.assertEqual(value, [1.5])

        def test_select_by_mean(self):
            # Create some params to use for testing
            params = {'param1':1, 'param2':True, 'param3':3}
            # Create an instance of SaverCsv
            saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

            # Call the read method to get mean values
            param, value = saver.read(params, 'a', select_by='mean', collate_by='mean')

            # Perform assertions based on your expectations
            self.assertEqual(param, [['param1=1', 'param2=True', 'param3=3']])
            self.assertEqual(value, [2.5])

        def test_select_by_median(self):
            # Create some params to use for testing
            params = {'param1':1, 'param2':True, 'param3':3}
            # Create an instance of SaverCsv
            saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

            # Call the read method to get median values
            param, value = saver.read(params, 'a', select_by='median', collate_by='mean')

            # Perform assertions based on your expectations
            self.assertEqual(param, [['param1=1', 'param2=True', 'param3=3']])
            self.assertEqual(value, [2.5])

        def test_nonexistent_metric(self):
            # Create some params to use for testing
            params = {'param1':1, 'param2':True, 'param3':3}
            # Create an instance of SaverCsv
            saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

            # Call the read method to get min and max values
            with self.assertRaises(KeyError):
                saver.read(params, 'c')

        def test_value_exists_both_str_float(self):
            # Create some params to use for testing
            params = {'param1': 'string'}
            # Create an instance of SaverCsv
            saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

            # Call the read method to get min values
            param, value = saver.read(params, 'a', select_by='min')

            # Perform assertions based on your expectations
            self.assertEqual(param, [['param1=string', 'param2=1', 'param3=3']])
            self.assertEqual(value, [4])         

        def test_not_given_params(self):
            # Create an instance of SaverCsv
            saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

            # Call the read method to get min values, averaged over each run
            params, values = saver.read({}, 'a', select_by='min', collate_by='mean')

            # Perform assertions based on your expectations
            self.assertEqual(3, len(params))
            self.assertEqual(True, ['param1=string', 'param2=1', 'param3=3'] in params)
            self.assertEqual(True, ['param1=1', 'param2=True', 'param3=3'] in params)
            self.assertEqual(True, ['param1=1', 'param2=False', 'param3=3'] in params)
            self.assertEqual(3, len(values))
            self.assertEqual(True, 4 in values)
            self.assertEqual(True, 1.5 in values)
            self.assertEqual(True, 3 in values)

            # Now not averaging and None instead of empty list
            params, values = saver.read(None, 'a', select_by='all', collate_by='all')

            # Perform assertions based on your expectations
            self.assertEqual(4, len(params))
            self.assertEqual(True, ['param1=string', 'param2=1', 'param3=3', 'results_0'] in params)
            self.assertEqual(True, ['param1=1', 'param2=True', 'param3=3', 'results_0'] in params)
            self.assertEqual(True, ['param1=1', 'param2=True', 'param3=3', 'results_1'] in params)
            self.assertEqual(True, ['param1=1', 'param2=False', 'param3=3', 'results_0'] in params)
            # Turn values into a list of lists (from a list of numpy arrays)
            values = [list(v) for v in values]
            self.assertEqual(4, len(values))
            self.assertEqual(True, [1, 2, 3] in values)
            self.assertEqual(True, [2, 3, 4] in values)
            self.assertEqual(True, [3, 4, 5] in values)
            self.assertEqual(True, [4, 5, 6] in values)

        def test_multi_matching_paths(self):
            # Create some params to use for testing
            params = {'param1':1}
            # Create an instance of SaverCsv
            saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

            # Call the read method to get max value and params
            param, value = saver.read(params, 'a', select_by='max', collate_by='mean')

            # Check results are as expected
            self.assertEqual(2, len(param))
            self.assertEqual(True, ['param1=1', 'param2=False', 'param3=3'] in param)
            self.assertEqual(True, ['param1=1', 'param2=True', 'param3=3'] in param)
            self.assertEqual(2, len(value))
            self.assertEqual(True, 5 in value)
            self.assertEqual(True, 3.5 in value)
        
        def test_no_matching_paths(self):
            # Create some params to use for testing
            params = {'param1':2}
            # Create an instance of SaverCsv
            saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

            # Call the read method to get max value and params
            param, value = saver.read(params, 'a', select_by='max')
            self.assertEqual(param, None)
            self.assertEqual(value, None)
            
        def test_multi_matching_paths_and_missing_metrics(self):
            # Create some params to use for testing
            params = {'param1':1}
            # Create an instance of SaverCsv
            saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

            # Call the read method to get max value and params
            with self.assertRaises(KeyError):
                saver.read(params, 'c', select_by='max')

        def test_collate_by_mean_single(self):
            # Create some params to use for testing
            params = {'param1':1, 'param2':False, 'param3':3}
            # Create an instance of SaverCsv
            saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)

            # Call the read method to get max value and params
            param, value = saver.read(params, 'a', select_by='max', collate_by='mean')

            # Check results are as expected
            self.assertEqual(param,[['param1=1', 'param2=False', 'param3=3']])
            self.assertEqual(value, [5])


class TestSaverCsvGetSetCurrentPath(unittest.TestCase):
    
        def setUp(self):
            # Create a temporary directory with some CSV files for testing
            self.test_dir = 'test_directory'
            os.makedirs(self.test_dir, exist_ok=True)
    
            # Creating some CSV files with specific subdirectory paths
            self.csv_files = [
                os.path.join('--param1=1','--param2=True','--param3=3','results_0.csv'),
                os.path.join('--param1=1','--param2=True','--param3=3','results_1.csv'),
                os.path.join('--param1=1','--param2=False','--param3=3','results_0.csv'),
                os.path.join('--param1=string', '--param2=1', '--param3=3', 'results_0.csv'),
            ]

            for i, file in enumerate(self.csv_files):
                file_path = os.path.join(self.test_dir, file)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                # Create a data frame with different values for each CSV file
                results = pd.DataFrame({'a': [i+1,i+2,i+3], 'b': [i+4,i+5,i+6]})
                # Save the results
                results.to_csv(file_path, mode='w', index=False)
            # The data frames we created should look like this:
            # --param1=1/--param2=True/--param3=3/results_0.csv: 
            #   a b
            #   1 4
            #   2 5
            #   3 6
            # --param1=1/--param2=True/--param3=3/results_1.csv:
            #   a b
            #   2 5
            #   3 6
            #   4 7
            # --param1=1/--param2=False/--param3=3/results_0.csv:
            #   a b
            #   3 6
            #   4 7
            #   5 8
            # --param1=string/--param2=1/--param3=3/results_0.csv:
            #   a b
            #   4 7
            #   5 8
            #   6 9
                
        def tearDown(self):
            # Clean up the temporary directory and files after testing
            for root, dirs, files in os.walk(self.test_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(self.test_dir)

        def test_update_current_path_from_None(self):
            saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
            params = {'--param1': '1', '--param2': 'True', '--param3': '3'}
            expected_path = os.path.join(self.test_dir, '--param1=1', '--param2=True', '--param3=3', 'results_2.csv')
            actual_path = saver.getset_current_path(params)
            self.assertEqual(actual_path, expected_path)

        def test_update_current_path_from_existing(self):
            og_params = {'--param1': '1', '--param2': 'False', '--param3': '3'}
            saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir, params=og_params)
            new_params = {'--param1': '1', '--param2': 'True', '--param3': '3'}
            expected_path = os.path.join(self.test_dir, '--param1=1', '--param2=True', '--param3=3', 'results_2.csv')
            actual_path = saver.getset_current_path(new_params)
            self.assertEqual(actual_path, expected_path)

        def test_without_params(self):
            params = {'--param1': '1', '--param2': 'True', '--param3': '3'}
            saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir, params=params)
            expected_path = os.path.join(self.test_dir, '--param1=1', '--param2=True', '--param3=3', 'results_2.csv')
            actual_path = saver.getset_current_path()
            self.assertEqual(actual_path, expected_path)

        def test_no_params_no_current_params(self):
            saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
            with self.assertRaises(ValueError):
                saver.getset_current_path()

        def test_current_params_no_current_path(self):
            params = {'--param1': '1', '--param2': 'True', '--param3': '3'}
            saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
            saver.current_params = params
            with self.assertRaises(Exception):
                saver.get_current_path()

        def test_nonexistent_params(self):
            saver = SaverCsv(LoggerDefault(), root_dir=self.test_dir)
            params = {'--param1': '2', '--param2': 'False', '--param3': '4'}
            expected_path = os.path.join(self.test_dir, '--param1=2', '--param2=False', '--param3=4', 'results_0.csv')
            actual_path = saver.getset_current_path(params)
            self.assertEqual(actual_path, expected_path)

class TestSaverCsvGetCurrentParams(unittest.TestCase):
    
    def test_no_params(self):
        saver = SaverCsv(LoggerDefault())
        self.assertEqual(None, saver.get_current_params())

    def test_with_params(self):
        params = {'--param1': '1', '--param2': 'True', '--param3': '3'}
        saver = SaverCsv(LoggerDefault(), params=params)
        self.assertEqual(params, saver.get_current_params())




if __name__ == "__main__":
    unittest.main()
