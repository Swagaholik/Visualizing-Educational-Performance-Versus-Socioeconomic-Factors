"""
Anthony Chung, Anson Huang, Sonia Fereidooni
CSE 163 Final Project
6/11/2021

The purpose of this file is to test the data cleaning methods
implemented in cse163final.py. This is to ensure that our methods
properly cleaned and filtered the information that we expect.
"""
import cse163final
import pandas as pd
from sodapy import Socrata

from cse163_utils import assert_equals


def test_clean_grad_data(df_graduation, subset_size=3):
    """
    Tests to make sure that the clean_grad_data works
    correctly (i.e. has the correct expected columns, returns
    the correct samples, etc.).
    """
    expected_columns = [
        'studentgrouptype', 'studentgroup', 'cohort',
        'year1dropout', 'year2dropout', 'year3dropout',
        'year4dropout', 'year5dropout', 'year6dropout',
        'transferout', 'finalcohort', 'graduate',
        'continuing', 'dropout', 'graduationrate',
        'year7dropout'
    ]

    first_n_subset = df_graduation.head(subset_size).copy()
    first_n_subset = cse163final.clean_grad_data(first_n_subset)

    random_subset_grad = df_graduation.sample(n=subset_size)
    random_subset_grad = cse163final.clean_grad_data(random_subset_grad)

    cleaned_grad = cse163final.clean_grad_data(df_graduation)

    # Verify columns were filtered out correctly
    assert_equals(expected_columns, list(first_n_subset.columns))
    assert_equals(expected_columns, list(random_subset_grad.columns))
    assert_equals(expected_columns, list(cleaned_grad.columns))

    # Verify that the first_n_subset is equal to the first subset_size rows
    # in cleaned_grad. This is meant to be a sanity check
    assert_equals(True, cleaned_grad.head(subset_size).equals(first_n_subset))

    # Verify cohort column was modified correctly
    cohort_column = list(cleaned_grad['cohort'])
    assert_equals(True, '4 Year Graduation' in cohort_column)
    assert_equals(True, '5 Year Graduation' in cohort_column)
    assert_equals(True, '6 Year Graduation' in cohort_column)
    assert_equals(True, '7 Year Graduation' in cohort_column)


def test_clean_growth_data(df_growth, subset_size=3):
    """
    Tests to make sure that the clean_growth_data works
    correctly (i.e. has the correct expected columns, returns
    the correct samples, etc.).
    """
    expected_columns = [
        'studentgroup', 'subject',
        'percentlowgrowth', 'percenttypicalgrowth', 'percenthighgrowth'
    ]

    first_n_subset = df_growth.head(subset_size).copy()
    first_n_subset = cse163final.clean_growth_data(first_n_subset)

    random_subset_growth = df_growth.sample(n=subset_size)
    random_subset_growth = cse163final.clean_growth_data(random_subset_growth)

    cleaned_growth = cse163final.clean_growth_data(df_growth)
    assert_equals(expected_columns, list(first_n_subset.columns))
    assert_equals(expected_columns, list(random_subset_growth.columns))
    assert_equals(expected_columns, list(cleaned_growth.columns))
    demographics = list(cleaned_growth['studentgroup'])
    assert_equals(True, 'Homeless' in demographics)
    assert_equals(True, 'Low-Income' in demographics)
    assert_equals(True, 'Non-Low Income' in demographics)
    assert_equals(True, 'All Students' in demographics)


def main():
    pd.options.display.max_columns = None
    pd.options.display.max_rows = None
    client = Socrata("data.wa.gov",
                     "EogizcHnQhkBqvQkL9trDzsWW",
                     username="ansonh@cs.washington.edu",
                     password="CSE163Project")
    # Graduation_data
    results_grad = client.get("gges-4vcv", limit=1000)
    df_graduation = pd.DataFrame.from_records(results_grad)
    # Growth_data
    results_growth = client.get("uj4q-wr8d", limit=1000)
    df_growth = pd.DataFrame.from_records(results_growth)

    test_clean_grad_data(df_graduation, subset_size=5)
    test_clean_growth_data(df_growth, subset_size=2)


if __name__ == '__main__':
    main()
