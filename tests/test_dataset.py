import json
import tempfile
import shutil
import warnings

import pandas as pd
import numpy as np
import great_expectations as ge

import unittest


class TestDataset(unittest.TestCase):

    def test_dataset(self):

        D = ge.dataset.PandasDataSet({
            'x' : [1,2,4],
            'y' : [1,2,5],
            'z' : ['hello', 'jello', 'mello'],
        })

        # print D._expectations_config.keys()
        # print json.dumps(D._expectations_config, indent=2)

        self.assertEqual(
            D._expectations_config,
            {
                "dataset_name" : None,
                "meta": {
                    "great_expectations.__version__": ge.__version__
                },
                "expectations" : [{
                    "expectation_type" : "expect_column_to_exist",
                    "kwargs" : { "column" : "x" }
                },{
                    "expectation_type" : "expect_column_to_exist",
                    "kwargs" : { "column" : "y" }
                },{
                    "expectation_type" : "expect_column_to_exist",
                    "kwargs" : { "column" : "z" }
                }]
            }
        )

        self.maxDiff = None
        self.assertEqual(
            D.get_expectations_config(),
            {
                "dataset_name" : None,
                "meta": {
                    "great_expectations.__version__": ge.__version__
                },
                "expectations" : [{
                    "expectation_type" : "expect_column_to_exist",
                    "kwargs" : { "column" : "x" }
                },{
                    "expectation_type" : "expect_column_to_exist",
                    "kwargs" : { "column" : "y" }
                },{
                    "expectation_type" : "expect_column_to_exist",
                    "kwargs" : { "column" : "z" }
                }]
            }
        )

    def test_expectation_meta(self):
        df = ge.dataset.PandasDataSet({
            'x' : [1,2,4],
            'y' : [1,2,5],
            'z' : ['hello', 'jello', 'mello'],
        })

        result = df.expect_column_median_to_be_between('x', 2, 2, meta={"notes": "This expectation is for lolz."})
        k = 0
        self.assertEqual(result['success'], True)
        config = df.get_expectations_config()
        for expectation_config in config['expectations']:
            if expectation_config['expectation_type'] == 'expect_column_median_to_be_between':
                k += 1
                self.assertEqual(
                    expectation_config['meta'],
                    {"notes": "This expectation is for lolz."}
                )

        self.assertEqual(k,1)

        #This should raise an error because meta isn't serializable.
        with self.assertRaises(Exception) as context:
            df.expect_column_values_to_be_increasing("x", meta={"unserializable_array":np.array(range(10))})



    #TODO: !!! Add tests for expectation and column_expectation
    #TODO: !!! Add tests for save_expectation

    def test_set_default_expectation_argument(self):
        df = ge.dataset.PandasDataSet({
            'x' : [1,2,4],
            'y' : [1,2,5],
            'z' : ['hello', 'jello', 'mello'],
        })

        self.assertEqual(
            df.get_default_expectation_arguments(),
            {
                "include_config" : False,
                "catch_exceptions" : False,
                "result_format" : 'BASIC',
            }
        )

        df.set_default_expectation_argument("result_format", "SUMMARY")

        self.assertEqual(
            df.get_default_expectation_arguments(),
            {
                "include_config" : False,
                "catch_exceptions" : False,
                "result_format" : 'SUMMARY',
            }
        )

    def test_get_and_save_expectation_config(self):
        directory_name = tempfile.mkdtemp()

        df = ge.dataset.PandasDataSet({
            'x' : [1,2,4],
            'y' : [1,2,5],
            'z' : ['hello', 'jello', 'mello'],
        })
        df.expect_column_values_to_be_in_set('x', [1,2,4])
        df.expect_column_values_to_be_in_set('y', [1,2,4], catch_exceptions=True, include_config=True)
        df.expect_column_values_to_match_regex('z', 'ello')

        ### First test set ###

        output_config = {
          "expectations": [
            {
              "expectation_type": "expect_column_to_exist",
              "kwargs": {
                "column": "x"
              }
            },
            {
              "expectation_type": "expect_column_to_exist",
              "kwargs": {
                "column": "y"
              }
            },
            {
              "expectation_type": "expect_column_to_exist",
              "kwargs": {
                "column": "z"
              }
            },
            {
              "expectation_type": "expect_column_values_to_be_in_set",
              "kwargs": {
                "column": "x",
                "values_set": [
                  1,
                  2,
                  4
                ]
              }
            },
            {
              "expectation_type": "expect_column_values_to_match_regex",
              "kwargs": {
                "column": "z",
                "regex": "ello"
              }
            }
          ],
          "dataset_name": None,
          "meta": {
            "great_expectations.__version__": ge.__version__
          }
        }

        self.assertEqual(
            df.get_expectations_config(),
            output_config,
        )

        df.save_expectations_config(directory_name+'/temp1.json')
        temp_file = open(directory_name+'/temp1.json')
        self.assertEqual(
            json.load(temp_file),
            output_config,
        )
        temp_file.close()

        ### Second test set ###

        output_config = {
          "expectations": [
            {
              "expectation_type": "expect_column_to_exist",
              "kwargs": {
                "column": "x"
              }
            },
            {
              "expectation_type": "expect_column_to_exist",
              "kwargs": {
                "column": "y"
              }
            },
            {
              "expectation_type": "expect_column_to_exist",
              "kwargs": {
                "column": "z"
              }
            },
            {
              "expectation_type": "expect_column_values_to_be_in_set",
              "kwargs": {
                "column": "x",
                "values_set": [
                  1,
                  2,
                  4
                ]
              }
            },
            {
              "expectation_type": "expect_column_values_to_be_in_set",
              "kwargs": {
                "column": "y",
                "values_set": [
                  1,
                  2,
                  4
                ]
              }
            },
            {
              "expectation_type": "expect_column_values_to_match_regex",
              "kwargs": {
                "column": "z",
                "regex": "ello"
              }
            }
          ],
          "dataset_name": None,
          "meta": {
            "great_expectations.__version__": ge.__version__
          }
        }

        self.assertEqual(
            df.get_expectations_config(
                discard_failed_expectations=False
            ),
            output_config
        )

        df.save_expectations_config(
          directory_name+'/temp2.json',
          discard_failed_expectations=False
        )
        temp_file = open(directory_name+'/temp2.json')
        self.assertEqual(
            json.load(temp_file),
            output_config,
        )
        temp_file.close()

        ### Third test set ###

        output_config = {
          "expectations": [
            {
              "expectation_type": "expect_column_to_exist",
              "kwargs": {
                "column": "x"
              }
            },
            {
              "expectation_type": "expect_column_to_exist",
              "kwargs": {
                "column": "y"
              }
            },
            {
              "expectation_type": "expect_column_to_exist",
              "kwargs": {
                "column": "z"
              }
            },
            {
              "expectation_type": "expect_column_values_to_be_in_set",
              "kwargs": {
                "column": "x",
                "values_set": [
                  1,
                  2,
                  4
                ],
                "result_format": "BASIC"
              }
            },
            {
              "expectation_type": "expect_column_values_to_match_regex",
              "kwargs": {
                "column": "z",
                "regex": "ello",
                "result_format": "BASIC"
              }
            }
          ],
          "dataset_name": None,
          "meta": {
            "great_expectations.__version__": ge.__version__
          }
        }

        self.assertEqual(
            df.get_expectations_config(
                discard_result_format_kwargs=False,
                discard_include_configs_kwargs=False,
                discard_catch_exceptions_kwargs=False,
            ),
            output_config
        )

        df.save_expectations_config(
          directory_name+'/temp3.json',
          discard_result_format_kwargs=False,
          discard_include_configs_kwargs=False,
          discard_catch_exceptions_kwargs=False,
        )
        temp_file = open(directory_name+'/temp3.json')
        self.assertEqual(
            json.load(temp_file),
            output_config,
        )
        temp_file.close()

        # Clean up the output directory
        shutil.rmtree(directory_name)

    def test_format_column_map_output(self):
        df = ge.dataset.PandasDataSet({
            "x" : list("abcdefghijklmnopqrstuvwxyz"),
        })
        self.maxDiff = None

        ### Normal Test ###

        success = True
        element_count = 20
        nonnull_values = pd.Series(range(15))
        nonnull_count = 15
        boolean_mapped_success_values = pd.Series([True for i in range(15)])
        success_count = 15
        unexpected_list = []
        unexpected_index_list = []

        self.assertEqual(
            df._format_column_map_output(
                "BOOLEAN_ONLY",
                success,
                element_count, nonnull_count,
                unexpected_list, unexpected_index_list
            ),
            {'success': True}
        )

        self.assertEqual(
            df._format_column_map_output(
                "BASIC",
                success,
                element_count, nonnull_count,
                unexpected_list, unexpected_index_list
            ),
            {
                'success': True,
                'result_obj': {
                    'element_count': 20,
                    'missing_count': 5,
                    'missing_percent': 0.25,
                    'partial_unexpected_list': [],
                    'unexpected_count': 0,
                    'unexpected_percent': 0.0,
                    'unexpected_percent_nonmissing': 0.0
                }
            }
        )

        self.assertEqual(
            df._format_column_map_output(
                "SUMMARY",
                success,
                element_count,
                nonnull_count,
                unexpected_list, unexpected_index_list
            ),
            {
                'success': True,
                'result_obj': {
                    'element_count': 20,
                    'missing_count': 5,
                    'missing_percent': 0.25,
                    'partial_unexpected_list': [],
                    'unexpected_count': 0,
                    'unexpected_percent': 0.0,
                    'unexpected_percent_nonmissing': 0.0,
                    'partial_unexpected_index_list': [],
                    'partial_unexpected_counts': []
                }
            }
        )

        self.assertEqual(
            df._format_column_map_output(
                "COMPLETE",
                success,
                element_count,
                nonnull_count,
                unexpected_list, unexpected_index_list
            ),
            {
                'success': True,
                'result_obj':
                    {
                        'element_count': 20,
                        'missing_count': 5,
                        'missing_percent': 0.25,
                        'partial_unexpected_list': [],
                        'unexpected_count': 0,
                        'unexpected_percent': 0.0,
                        'unexpected_percent_nonmissing': 0.0,
                        'partial_unexpected_index_list': [],
                        'partial_unexpected_counts': [],
                        'unexpected_list': [],
                        'unexpected_index_list': []
                    }
            }
        )

        ### Test the case where all elements are null ###

        success = True
        element_count = 20
        nonnull_values = pd.Series([])
        nonnull_count = 0
        boolean_mapped_success_values = pd.Series([])
        success_count = 0
        unexpected_list = []
        unexpected_index_list = []

        self.assertEqual(
            df._format_column_map_output(
                "BOOLEAN_ONLY",
                success,
                element_count,
                nonnull_count,
                unexpected_list, unexpected_index_list
            ),
            {'success': True}
        )

        self.assertEqual(
            df._format_column_map_output(
                "BASIC",
                success,
                element_count,
                nonnull_count,
                unexpected_list, unexpected_index_list
            ),
            {
                'success': True,
                'result_obj': {
                    'element_count': 20,
                    'missing_count': 20,
                    'missing_percent': 1,
                    'partial_unexpected_list': [],
                    'unexpected_count': 0,
                    'unexpected_percent': 0.0,
                    'unexpected_percent_nonmissing': None
                }
            }
        )

        self.assertEqual(
            df._format_column_map_output(
                "SUMMARY",
                success,
                element_count,
                nonnull_count,
                unexpected_list, unexpected_index_list
            ),
            {
                'success': True,
                'result_obj': {
                    'element_count': 20,
                    'missing_count': 20,
                    'missing_percent': 1,
                    'partial_unexpected_list': [],
                    'unexpected_count': 0,
                    'unexpected_percent': 0.0,
                    'unexpected_percent_nonmissing': None,
                    'partial_unexpected_index_list': [],
                    'partial_unexpected_counts': []
                }
            }
        )

        self.assertEqual(
            df._format_column_map_output(
                "COMPLETE",
                success,
                element_count,
                nonnull_count,
                unexpected_list, unexpected_index_list
            ),
            {
                'success': True,
                'result_obj': {
                    'element_count': 20,
                    'missing_count': 20,
                    'missing_percent': 1,
                    'partial_unexpected_list': [],
                    'unexpected_count': 0,
                    'unexpected_percent': 0.0,
                    'unexpected_percent_nonmissing': None,
                    'partial_unexpected_index_list': [],
                    'partial_unexpected_counts': [],
                    'unexpected_list': [],
                    'unexpected_index_list': []
                }
            }
        )

        ### Test the degenerate case where there are no elements ###

        success = False
        element_count = 0
        nonnull_values = pd.Series([])
        nonnull_count = 0
        boolean_mapped_success_values = pd.Series([])
        success_count = 0
        unexpected_list = []
        unexpected_index_list = []

        self.assertEqual(
            df._format_column_map_output(
                "BOOLEAN_ONLY",
                success,
                element_count,
                nonnull_count,
                unexpected_list, unexpected_index_list
            ),
            {'success': False}
        )

        self.assertEqual(
            df._format_column_map_output(
                "BASIC",
                success,
                element_count,
                nonnull_count,
                unexpected_list, unexpected_index_list
            ),
            {
                'success': False,
                'result_obj': {
                    'element_count': 0,
                    'missing_count': 0,
                    'missing_percent': None,
                    'partial_unexpected_list': [],
                    'unexpected_count': 0,
                    'unexpected_percent': None,
                    'unexpected_percent_nonmissing': None
                }
            }
        )

        self.assertEqual(
            df._format_column_map_output(
                "SUMMARY",
                success,
                element_count,
                nonnull_count,
                unexpected_list, unexpected_index_list
            ),
            {
                'success': False,
                'result_obj': {
                    'element_count': 0,
                    'missing_count': 0,
                    'missing_percent': None,
                    'partial_unexpected_list': [],
                    'unexpected_count': 0,
                    'unexpected_percent': None,
                    'unexpected_percent_nonmissing': None,
                    'partial_unexpected_counts': [],
                    'partial_unexpected_index_list': []
                }
            }
        )

        self.assertEqual(
            df._format_column_map_output(
                "COMPLETE",
                success,
                element_count,
                nonnull_count,
                unexpected_list, unexpected_index_list
            ),
            {
                'success': False,
                'result_obj': {
                    'element_count': 0,
                    'missing_count': 0,
                    'missing_percent': None,
                    'partial_unexpected_list': [],
                    'unexpected_count': 0,
                    'unexpected_percent': None,
                    'unexpected_percent_nonmissing': None,
                    'partial_unexpected_counts': [],
                    'partial_unexpected_index_list': [],
                    'unexpected_list': [],
                    'unexpected_index_list': []
                }
            }
        )

    def test_calc_map_expectation_success(self):
        df = ge.dataset.PandasDataSet({
            "x" : list("abcdefghijklmnopqrstuvwxyz")
        })
        self.assertEqual(
            df._calc_map_expectation_success(
                success_count=10,
                nonnull_count=10,
                mostly=None
            ),
            (True, 1.0)
        )

        self.assertEqual(
            df._calc_map_expectation_success(
                success_count=90,
                nonnull_count=100,
                mostly=.9
            ),
            (True, .9)
        )

        self.assertEqual(
            df._calc_map_expectation_success(
                success_count=90,
                nonnull_count=100,
                mostly=.8
            ),
            (True, .9)
        )

        self.assertEqual(
            df._calc_map_expectation_success(
                success_count=80,
                nonnull_count=100,
                mostly=.9
            ),
            (False, .8)
        )

        self.assertEqual(
            df._calc_map_expectation_success(
                success_count=0,
                nonnull_count=0,
                mostly=None
            ),
            (True, None)
        )

        self.assertEqual(
            df._calc_map_expectation_success(
                success_count=0,
                nonnull_count=100,
                mostly=None
            ),
            (False, 0.0)
        )

    def test_find_expectations(self):
        my_df = ge.dataset.PandasDataSet({
            'x' : [1,2,3,4,5,6,7,8,9,10],
            'y' : [1,2,None,4,None,6,7,8,9,None],
            'z' : ['cello', 'hello', 'jello', 'bellow', 'fellow', 'mellow', 'wellow', 'xello', 'yellow', 'zello'],
        })
        my_df.expect_column_values_to_be_of_type('x', 'int', 'python')
        my_df.expect_column_values_to_be_of_type('y', 'int', 'python')
        my_df.expect_column_values_to_be_of_type('z', 'int', 'python')
        my_df.expect_column_values_to_be_increasing('x')
        my_df.expect_column_values_to_match_regex('z', 'ello')

        self.assertEqual(
            my_df.find_expectations("expect_column_to_exist", "w"),
            []
        )

        self.assertEqual(
            my_df.find_expectations("expect_column_to_exist", "x", expectation_kwargs={}),
            [{
              "expectation_type": "expect_column_to_exist",
              "kwargs": {
                "column": "x"
              }
            }]
        )

        self.assertEqual(
            my_df.find_expectations("expect_column_to_exist", expectation_kwargs={"column": "y"}),
            [{
              "expectation_type": "expect_column_to_exist",
              "kwargs": {
                "column": "y"
              }
            }]
        )

        self.assertEqual(
            my_df.find_expectations("expect_column_to_exist"),
            [{
              "expectation_type": "expect_column_to_exist",
              "kwargs": {
                "column": "x"
              }
            },{
              "expectation_type": "expect_column_to_exist",
              "kwargs": {
                "column": "y"
              }
            },{
              "expectation_type": "expect_column_to_exist",
              "kwargs": {
                "column": "z"
              }
            }]
        )

        with self.assertRaises(Exception) as context:
            my_df.find_expectations("expect_column_to_exist", "x", {"column": "y"})

        #FIXME: I don't understand why this test fails.
        # print context.exception
        # print 'Conflicting column names in remove_expectation' in context.exception
        # self.assertTrue('Conflicting column names in remove_expectation:' in context.exception)

        self.assertEqual(
            my_df.find_expectations(column="x"),
            [{
              "expectation_type": "expect_column_to_exist",
              "kwargs": {
                "column": "x"
              }
            },{
              "expectation_type": "expect_column_values_to_be_of_type",
              "kwargs": {
                "column": "x",
                "type_": "int",
                "target_datasource": "python",
              }
            },{
              "expectation_type": "expect_column_values_to_be_increasing",
              "kwargs": {
                "column": "x"
              }
            }]
        )


    def test_remove_expectation(self):
        my_df = ge.dataset.PandasDataSet({
            'x' : [1,2,3,4,5,6,7,8,9,10],
            'y' : [1,2,None,4,None,6,7,8,9,None],
            'z' : ['cello', 'hello', 'jello', 'bellow', 'fellow', 'mellow', 'wellow', 'xello', 'yellow', 'zello'],
        })
        my_df.expect_column_values_to_be_of_type('x', 'int', 'python')
        my_df.expect_column_values_to_be_of_type('y', 'int', 'python')
        my_df.expect_column_values_to_be_of_type('z', 'int', 'python', include_config=True, catch_exceptions=True)
        my_df.expect_column_values_to_be_increasing('x')
        my_df.expect_column_values_to_match_regex('z', 'ello')

        with self.assertRaises(Exception) as context:
            my_df.remove_expectation("expect_column_to_exist", "w", dry_run=True),

        #FIXME: Python 3 doesn't like this. It would be nice to use assertRaisesRegex, but that's not available in python 2.7
        # self.assertTrue('No matching expectation found.' in context.exception)

        self.assertEqual(
            my_df.remove_expectation("expect_column_to_exist", "x", expectation_kwargs={}, dry_run=True),
            {
              "expectation_type": "expect_column_to_exist",
              "kwargs": {
                "column": "x"
              }
            }
        )

        self.assertEqual(
            my_df.remove_expectation("expect_column_to_exist", expectation_kwargs={"column": "y"}, dry_run=True),
            {
              "expectation_type": "expect_column_to_exist",
              "kwargs": {
                "column": "y"
              }
            }
        )

        self.assertEqual(
            my_df.remove_expectation("expect_column_to_exist", expectation_kwargs={"column": "y"}, remove_multiple_matches=True, dry_run=True),
            [{
              "expectation_type": "expect_column_to_exist",
              "kwargs": {
                "column": "y"
              }
            }]
        )

        with self.assertRaises(ValueError) as context:
            my_df.remove_expectation("expect_column_to_exist", dry_run=True)

        #FIXME: Python 3 doesn't like this. It would be nice to use assertRaisesRegex, but that's not available in python 2.7
        # self.assertTrue('Multiple expectations matched arguments. No expectations removed.' in context.exception)

        self.assertEqual(
            my_df.remove_expectation("expect_column_to_exist", remove_multiple_matches=True, dry_run=True),
            [{
              "expectation_type": "expect_column_to_exist",
              "kwargs": {
                "column": "x"
              }
            },{
              "expectation_type": "expect_column_to_exist",
              "kwargs": {
                "column": "y"
              }
            },{
              "expectation_type": "expect_column_to_exist",
              "kwargs": {
                "column": "z"
              }
            }]
        )

        with self.assertRaises(Exception) as context:
            my_df.remove_expectation("expect_column_to_exist", "x", {"column": "y"}, dry_run=True)

        #FIXME: I don't understand why this test fails.
        # print context.exception
        # print 'Conflicting column names in remove_expectation' in context.exception
        # self.assertTrue('Conflicting column names in remove_expectation:' in context.exception)

        self.assertEqual(
            my_df.remove_expectation(column="x", remove_multiple_matches=True, dry_run=True),
            [{
              "expectation_type": "expect_column_to_exist",
              "kwargs": {
                "column": "x"
              }
            },{
              "expectation_type": "expect_column_values_to_be_of_type",
              "kwargs": {
                "column": "x",
                "type_": "int",
                "target_datasource": "python",
              }
            },{
              "expectation_type": "expect_column_values_to_be_increasing",
              "kwargs": {
                "column": "x"
              }
            }]
        )

        self.assertEqual(
            len(my_df._expectations_config.expectations),
            8
        )

        self.assertEqual(
            my_df.remove_expectation("expect_column_to_exist", "x"),
            None
        )
        self.assertEqual(
            len(my_df._expectations_config.expectations),
            7
        )

        self.assertEqual(
            my_df.remove_expectation(column="x", remove_multiple_matches=True),
            None
        )
        self.assertEqual(
            len(my_df._expectations_config.expectations),
            5
        )

        my_df.remove_expectation(column="z", remove_multiple_matches=True),
        self.assertEqual(
            len(my_df._expectations_config.expectations),
            2
        )

        self.assertEqual(
            my_df.get_expectations_config(discard_failed_expectations=False),
            {
                'expectations': [
                    {
                        'expectation_type': 'expect_column_to_exist',
                        'kwargs': {'column': 'y'}
                    },
                    {
                        'expectation_type': 'expect_column_values_to_be_of_type',
                        'kwargs': {'column': 'y', 'type_': 'int', 'target_datasource': 'python'}
                    }
                ],
                'dataset_name': None,
                "meta": {
                    "great_expectations.__version__": ge.__version__
                }
            }
        )

    def test_test_expectation_function(self):
        D = ge.dataset.PandasDataSet({
            'x' : [1,3,5,7,9],
            'y' : [1,2,None,7,9],
        })
        D2 = ge.dataset.PandasDataSet({
            'x' : [1,3,5,6,9],
            'y' : [1,2,None,6,9],
        })
        def expect_dataframe_to_contain_7(self):
            return {
                "success": bool((self==7).sum().sum() > 0)
            }

        self.assertEqual(
            D.test_expectation_function(expect_dataframe_to_contain_7),
            {'success': True}
        )
        self.assertEqual(
            D2.test_expectation_function(expect_dataframe_to_contain_7),
            {'success': False}
        )


    def test_test_column_map_expectation_function(self):

        D = ge.dataset.PandasDataSet({
            'x' : [1,3,5,7,9],
            'y' : [1,2,None,7,9],
        })
        def is_odd(self, column, mostly=None, result_format=None, include_config=False, catch_exceptions=None, meta=None):
            return column % 2 == 1

        self.assertEqual(
            D.test_column_map_expectation_function(is_odd, column='x'),
            {'result_obj': {'element_count': 5, 'missing_count': 0, 'missing_percent': 0, 'unexpected_percent': 0.0, 'partial_unexpected_list': [], 'unexpected_percent_nonmissing': 0.0, 'unexpected_count': 0}, 'success': True}
        )
        self.assertEqual(
            D.test_column_map_expectation_function(is_odd, 'x', result_format="BOOLEAN_ONLY"),
            {'success': True}
        )
        self.assertEqual(
            D.test_column_map_expectation_function(is_odd, column='y', result_format="BOOLEAN_ONLY"),
            {'success': False}
        )
        self.assertEqual(
            D.test_column_map_expectation_function(is_odd, column='y', result_format="BOOLEAN_ONLY", mostly=.7),
            {'success': True}
        )

    def test_test_column_aggregate_expectation_function(self):
        D = ge.dataset.PandasDataSet({
            'x' : [1,3,5,7,9],
            'y' : [1,2,None,7,9],
        })
        def expect_second_value_to_be(self, column, value, result_format=None, include_config=False, catch_exceptions=None, meta=None):
            return {
                "success": column.ix[1] == value,
                "result_obj": {
                    "observed_value": column.ix[1],
                }
            }

        self.assertEqual(
            D.test_column_aggregate_expectation_function(expect_second_value_to_be, 'x', 2),
            {'result_obj': {'observed_value': 3.0, 'element_count': 5, 'missing_count': 0, 'missing_percent': 0.0}, 'success': False}
        )
        self.assertEqual(
            D.test_column_aggregate_expectation_function(expect_second_value_to_be, column='x', value=3),
            {'result_obj': {'observed_value': 3.0, 'element_count': 5, 'missing_count': 0, 'missing_percent': 0.0}, 'success': True}
        )
        self.assertEqual(
            D.test_column_aggregate_expectation_function(expect_second_value_to_be, 'y', value=3, result_format="BOOLEAN_ONLY"),
            {'success': False}
        )
        self.assertEqual(
            D.test_column_aggregate_expectation_function(expect_second_value_to_be, 'y', 2, result_format="BOOLEAN_ONLY"),
            {'success': True}
        )

    def test_meta_version_warning(self):
        D = ge.dataset.DataSet();

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            out = D.validate(expectations_config={"expectations": []})
            self.assertEqual(str(w[0].message),
                             "WARNING: No great_expectations version found in configuration object.")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            out = D.validate(expectations_config={"meta": {"great_expectations.__version__": "0.0.0"}, "expectations": []})
            self.assertEqual(str(w[0].message),
                             "WARNING: This configuration object was built using a different version of great_expectations than is currently validating it.")

    def test_catch_exceptions_with_bad_expectation_type(self):
        my_df = ge.dataset.PandasDataSet({"x":range(10)})
        my_df.append_expectation({'expectation_type':'foobar', 'kwargs':{}})
        result = my_df.validate(catch_exceptions=True)

        self.assertEqual(result["results"][1]["success"], False)
        self.assertEqual(result["results"][1]["expectation_config"]["expectation_type"], "foobar")
        self.assertEqual(result["results"][1]["expectation_config"]["kwargs"], {})
        self.assertEqual(result["results"][1]["exception_info"]["raised_exception"], True)
        assert "AttributeError: \'PandasDataSet\' object has no attribute \'foobar\'" in result["results"][1]["exception_info"]["exception_traceback"]

        with self.assertRaises(AttributeError) as context:
            result = my_df.validate(catch_exceptions=False)


if __name__ == "__main__":
    unittest.main()
