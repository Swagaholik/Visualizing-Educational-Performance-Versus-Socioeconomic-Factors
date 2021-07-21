"""
Anthony Chung, Anson Huang, Sonia Fereidooni
CSE 163 Final Project
6/11/2021

The purpose of this file is to implement methods that will
visualize graduation rate, dropout rate, and student growth rate
across demographics using data from Washington's 2019 - 2020
Report Card Graduation and Report Card Growth
"""
import pandas as pd
import altair as alt
from sodapy import Socrata


def clean_grad_data(graduation_data):
    """
    Clean the graduation_data and return a new DataFrame with
    relevant information. More specifically:
    - Updates "cohort" column by replacing values
      with corresponding graduation track
    - Filters data to only include data relating to state totals
    - Drop irrelevant columns

    param graduation_data: a pandas DataFrame containing data on
                           graduation rate
    return: a new pandas DataFrame with the relevant information.
    """
    # X year graduation means it took X years for
    # them to graduate where we start counting
    # from 9th grade
    graduation_data['cohort'] = \
        graduation_data['cohort'].replace(['Four Year'], '4 Year Graduation')
    graduation_data['cohort'] = \
        graduation_data['cohort'].replace(['Five Year'], '5 Year Graduation')
    graduation_data['cohort'] = \
        graduation_data['cohort'].replace(['Six Year'], '6 Year Graduation')
    graduation_data['cohort'] = \
        graduation_data['cohort'].replace(['Seven Year'], '7 Year Graduation')

    is_state_total = graduation_data['schoolname'] == 'State Total'
    graduation_data = graduation_data[is_state_total].copy()

    # We determined what were irrelevant columns by looking at the columns
    # in the dataset:
    # https://data.wa.gov/Education/Report-Card-Graduation-2019-20/gges-4vcv
    irrelevant_columns = [
        'schoolyear', 'organizationlevel', 'county',
        'esdname', 'esdorganizationid', 'districtcode',
        'districtname', 'districtorganizationid',
        'schoolcode', 'schoolname', 'schoolorganizationid',
        'suppression', 'beggininggrade9', 'transferin',
        'dataasof'
    ]

    graduation_data.drop(irrelevant_columns, axis=1, inplace=True)

    return graduation_data


def clean_growth_data(growth_data):
    """
    Clean the growth_data and return a new DataFrame with
    relevant information. More specifically:
    - Filters data to only include state total and growth data
      of all grades.
    - Keeps the relevant columns

    param growth_data: a pandas DataFrame containing data on
                           graduation rate
    return: a new pandas DataFrame with the relevant information.
    """
    is_state_total = growth_data['schoolname'] == 'State Total'
    is_all_grades = growth_data['gradelevel'] == 'All Grades'

    growth_data = growth_data[is_state_total & is_all_grades].copy()

    relevant_columns = [
        'studentgroup', 'subject',
        'percentlowgrowth', 'percenttypicalgrowth', 'percenthighgrowth'
    ]

    growth_data = growth_data[relevant_columns]

    return growth_data


def plot_graduation_rate(graduation_data):
    """
    With the cleaned graduation_data, plot a bar chart comparing the graduation
    rate of all graduation tracks of low-income students to non-low income
    students.
    We'll define low-income as students who are labeled as low-income,
    homeless, or in foster care.
    """
    # 'studentgrouptype' just puts the appropriate tag next to the data
    # so the rows with Male or Female in 'studentgroup' would have Gender as
    # their 'studentgrouptype'
    relevant_columns = ['studentgrouptype', 'studentgroup', 'cohort',
                        'graduationrate']
    is_low_income = graduation_data['studentgroup'] == 'Low-Income'
    is_homeless = graduation_data['studentgroup'] == 'Homeless'
    is_non_low_income = graduation_data['studentgroup'] == 'Non-Low Income'
    is_foster_care = graduation_data['studentgroup'] == 'Foster Care'

    low_income_data = graduation_data.loc[is_low_income | is_homeless |
                                          is_non_low_income | is_foster_care,
                                          relevant_columns]

    low_income_data = low_income_data.astype({'graduationrate':
                                              'float64'}).copy()
    low_income_data['graduationrate'] = low_income_data['graduationrate'] * 100
    graph = alt.Chart(low_income_data).mark_bar().encode(
        x=alt.X('cohort:N', sort=['4 Year Graduation', '5 Year Graduation',
                                  '6 Year Graduation', '7 Year Graduation'],
                title=' '),
        y=alt.Y('graduationrate:Q', title='Graduation Rate (%)',
                scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('studentgroup:N', title='Student Group'),
        column=alt.Column('studentgroup:O', title=' ')
    ).properties(
        title=('The Relationship Between ' +
               'Socioeconomic Status and Graduation Rate')
    )

    graph = graph.configure_title(
        fontSize=20, anchor='middle'
    )

    graph.save('low_income_versus_graduation.png')


def plot_low_income_dropout_rate(graduation_data):
    """
    With the cleaned graduation_data, plot a bar chart comparing the dropout
    rate of all graduation tracks of low-income students to non-low income
    students.
    We'll define low-income as students who are labeled as low-income,
    homeless, or in foster care.
    """
    relevant_columns = ['studentgrouptype', 'studentgroup', 'cohort',
                        'dropout']
    is_low_income = graduation_data['studentgroup'] == 'Low-Income'
    is_homeless = graduation_data['studentgroup'] == 'Homeless'
    is_non_low_income = graduation_data['studentgroup'] == 'Non-Low Income'
    is_foster_care = graduation_data['studentgroup'] == 'Foster Care'
    low_income_data = graduation_data.loc[is_low_income | is_homeless |
                                          is_non_low_income | is_foster_care,
                                          relevant_columns]
    low_income_data = low_income_data.astype({'dropout': 'int64'}).copy()
    graph_data = alt.Chart(low_income_data).mark_bar().encode(
        x=alt.X('cohort:N', sort=['4 Year Graduation', '5 Year Graduation',
                                  '6 Year Graduation', '7 Year Graduation'],
                title=' '),
        y=alt.Y('dropout:Q', title='Number of Dropouts',
                scale=alt.Scale(domain=[0, 10000])),
        color=alt.Color('studentgroup:N', title='Student Group'),
        column=alt.Column('studentgroup:O', title=' ')
    ).properties(
        title=('The Relationship Between Socioeconomic ' +
               'Status and number of Student Dropouts')
    )

    graph_data = graph_data.configure_title(
        fontSize=20, anchor='middle'
    )

    graph_data.save('low_income_versus_dropout.png')


def plot_student_growth(growth_data, subject):
    """
    With the cleaned student growth data, plots bar charts
    that compares student income levels to the student growth
    percentiles (separated into bottom 1/3 percentile, middle
    1/3 percentile, and top 1/3 percentile) measuring which
    students had the most student growth. Student growth is
    measured by how much improvement students had in standardized
    test scores for math and english subject tests.
    """
    is_homeless = growth_data['studentgroup'] == 'Homeless'
    is_low_income = growth_data['studentgroup'] == 'Low-Income'
    is_non_low_income = growth_data['studentgroup'] == 'Non-Low Income'
    is_all = growth_data['studentgroup'] == 'All Students'

    subject_mask = growth_data['subject'] == subject

    low_income_data = growth_data.loc[((is_low_income | is_homeless
                                       | is_non_low_income | is_all)
                                       & subject_mask), :]

    # Convert decimals to percentage
    low_income_data = low_income_data.astype({'percentlowgrowth':
                                              'float64'}).copy()
    low_income_data = low_income_data.astype({'percenttypicalgrowth':
                                              'float64'}).copy()
    low_income_data = low_income_data.astype({'percenthighgrowth':
                                              'float64'}).copy()
    low_income_data['percentlowgrowth'] = \
        low_income_data['percentlowgrowth'] * 100
    low_income_data['percenttypicalgrowth'] = \
        low_income_data['percenttypicalgrowth'] * 100
    low_income_data['percenthighgrowth'] = \
        low_income_data['percenthighgrowth'] * 100

    # Create charts
    low_growth = alt.Chart(low_income_data).mark_bar().encode(
        y=alt.Y('studentgroup', sort=['Homeless', 'Low-Income',
                'Non-Low Income', 'All Students'], title=' '),
        x=alt.X('percentlowgrowth', title='Percent Low Growth (%)',
                scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('studentgroup', title='Student Group'),
    )

    typical_growth = alt.Chart(low_income_data).mark_bar().encode(
        y=alt.Y('studentgroup', sort=['Homeless', 'Low-Income',
                'Non-Low Income', 'All Students'], title=' '),
        x=alt.X('percenttypicalgrowth', title='Percent Typical Growth (%)',
                scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('studentgroup', title='Student Group'),
    )

    high_growth = alt.Chart(low_income_data).mark_bar().encode(
        y=alt.Y('studentgroup', sort=['Homeless', 'Low-Income',
                'Non-Low Income', 'All Students'], title=' '),
        x=alt.X('percenthighgrowth', title='Percent High Growth (%)',
                scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('studentgroup', title='Student Group'),
    )

    # Add labels to charts
    text_low = low_growth.mark_text(
        align='left',
        baseline='middle',
        dx=3  # Nudges text to right so it doesn't appear on top of the bar
    ).encode(
        text='percentlowgrowth'
    )

    text_typical = typical_growth.mark_text(
        align='left',
        baseline='middle',
        dx=3  # Nudges text to right so it doesn't appear on top of the bar
    ).encode(
        text='percenttypicalgrowth'
    )

    text_high = high_growth.mark_text(
        align='left',
        baseline='middle',
        dx=3  # Nudges text to right so it doesn't appear on top of the bar
    ).encode(
        text='percenthighgrowth'
    )

    all_growth = (low_growth + text_low) & (typical_growth + text_typical) & \
        (high_growth + text_high)
    all_growth = all_growth.properties(
        title='Socioeconomic Status and Student Growth (' + subject + ')'
    ).configure_title(fontSize=20, anchor='middle')
    all_growth.save('student_growth_' + subject + '.png')


def main():
    pd.options.display.max_rows = None
    pd.options.display.max_columns = None

    client = Socrata("data.wa.gov",
                     "EogizcHnQhkBqvQkL9trDzsWW",
                     username="ansonh@cs.washington.edu",
                     password="CSE163Project")

    # Graduation_data
    results_grad = client.get("gges-4vcv", limit=1000)

    # Growth_data
    results_growth = client.get("uj4q-wr8d", limit=1000)

    # Convert to pandas DataFrame (graduation)
    df_graduation = pd.DataFrame.from_records(results_grad)
    grad_data = clean_grad_data(df_graduation)

    # Convert to pandas DataFrame (growth)
    df_growth = pd.DataFrame.from_records(results_growth)
    growth_data = clean_growth_data(df_growth)

    plot_graduation_rate(grad_data)
    plot_low_income_dropout_rate(grad_data)
    plot_student_growth(growth_data, 'Math')
    plot_student_growth(growth_data, 'English Language Arts')


if __name__ == '__main__':
    main()
