# Import packages
import pandas as pd

''' Had to use Spyder and run outside VS code as pandas etc aren't available (I gave up)'''
# Reading in raw csv files from datasets_raw
df = pd.read_csv(r'C:\Users\User\Desktop\CBS\Visual Analytics\Exam\Economic sector\lfsq_epgais__custom_4004302_linear.csv')
#df = pd.read_csv('Economic_sector_gender_representation.csv')

# Melting data in the correct format (every dimension and value in a column)

# 1. Data Cleaning Step 1
# 1.1 Identify and delete columns that are not necessary for further process

print(df.info())

# DATAFLOW

# Contains the datasource, same for all
print('\n')
print(df['DATAFLOW'].unique())    
    
# LAST_UPDATE:

# When the dataset was last updated, 16/11/22
print('\n')
print(df['LAST UPDATE'].unique())

df = df.loc[:, ~df.columns.isin(['DATAFLOW', 'LAST UPDATE'])]  

# 1.2 Explore each column and there unique values, especially if categorical data AND Decide how to proceed with this data

# Frequency:

# Q: Frequency of datapoints are quarterly.
print('\n')
print(df['freq'].unique())

# Unit:
    
# THS: Data is presented as number of people employed in thousands
print('\n')
print(df['unit'].unique())

# Sex:

# F: Female
# M: Male
# T: Total
print('\n')
print(df['sex'].unique())

# Age:

# One age group, Y15-64, number of people employed between 15 and 64 years old 
print('\n')
print(df['age'].unique())

# Isco08:

# The categorisation of economic sectors employment are divided into
print('\n')
print(df['isco08'].unique())

# Worktime:

# FT: Full-time employment
print('\n')
print(df['worktime'].unique())

# Geo:

# EU countries included in the dataset, abbrivated
print('\n')
print(df['geo'].unique())

# Time_period:

# Quarterly data for the period Q1 2013 to Q2 2022
print('\n')
print(df['TIME_PERIOD'].unique())

# OBS_value:

# Number of people employed in absolute numbers, in thousands, as float
print('\n')
print(df['OBS_VALUE'].unique())

# OBS_flag:

# comments from Eurostat on the quality of the data
print('\n')
print(df['OBS_FLAG'].unique())

# Splitting TIME_PERIOD column into 'Year' and 'Quarter'
df[['Year','quarter']] = df.TIME_PERIOD.str.split("-",expand=True,)
# The other datasets are annual figures, which provide a snapshot at a certain time,
# thus any quarter will provide a comparabble snapshot 
df = df[df.quarter == 'Q2']

print(df['OBS_FLAG'].describe())
print(df['OBS_FLAG'].value_counts())

# Quarter 2 is used as it provides the most datapoints and fewer type of special values than Q1 and Q3.
# Q4 has the same categories of special values, but overall more missing values.
# Special values include: U, low reliability, C, confidential, and D, definition differs. However, since Eurostat
# still includes the data, it serves as the best estimate available and the data will be used.
# Since we're interested in the 

# Removing the following columns as they are not relevant for calculation. 
df = df.loc[:, ~df.columns.isin(['freq','unit','age','worktime', 'OBS_FLAG'])]

# Renaming columns
df.rename(columns = {'isco08':'Sector', 'geo':'Country', 'OBS_VALUE':'Value'}, inplace = True)

# 1.3 Rename country column with help of the EU27.csv in additional data
''' FIX (Ries method) '''
geo_names = {
'BE' :'Belgium',
'BG' :'Bulgaria',
'CZ' :'Czech Republic',
'DK' :'Denmark',
'DE' :'Germany',
'EE' :'Estonia',
'IE' :'Ireland',
'EL' :'Greece',
'ES' :'Spain',
'FR' :'France',
'HR' :'Croatia',
'IT' :'Italy',
'CY' :'Cyprus',
'LV' :'Latvia',
'LT' :'Lithuania',
'LU' :'Luxembourg',
'HU' :'Hungary',
'MT' :'Malta',
'NL' :'Netherlands',
'AT' :'Austria',
'PL' :'Poland',
'PT' :'Portugal',
'RO' :'Romania',
'SI' :'Slovenia',
'SK' :'Slovakia',
'FI' :'Finland',
'SE' :'Sweden'}

df['Country'] = df['Country'].map(geo_names) 

# 2. Data Cleaning Step 2 (handle null values, not valid rows etc.)

# Reshaping to calculate female percentage of employment for every sector
sector_percentage = df.pivot_table(df, index=['Year','Country','Sector'], columns=['sex'])
print(sector_percentage)
sector_percentage['percent'] = sector_percentage['Value','F']/sector_percentage['Value','T']
# selecting the percentage column
p_sector = sector_percentage.loc[:,'percent']
p_sector = p_sector.to_frame()

print(sector_percentage)
print(p_sector)

# reshaping to sector as columns to calculate average percentage over all sectors
p_country = p_sector.pivot_table(p_sector, index=['Year','Country'], columns=['Sector'])
print(p_country.describe())
# Deleting the total column (specify first levl of column index, then the actual column):
p_country = p_country.drop(('percent', 'TOTAL'), axis=1)
# Visual inspection through Excel
#p_country.to_csv('p_country.csv')
#p_country.to_excel('p_country.xlsx')

# The OC0 column has fewer datapoints, 74, while the remaining sectors have 258-269 datapoints
# However, since we're interested in the averages gender representation across a country's economy,
# missing datapoints can be accepted
#p_country = p_country.drop(('percent', 'OC0'), axis=1)

print(p_country)
p_country['sum'] = p_country.sum(axis=1)
p_country['count'] = p_country.count(axis=1)-1
# Calculate the average female representation in a country by summing the percentages and dividing by the number of available
# datapoints (the couont)
p_country['Average female percentage'] = p_country['sum']/p_country['count']
print(p_country)

# Deleting  every column except avg_percent:
p_country = p_country.drop((['percent','sum', 'count']), axis=1)
clean_df = p_country.droplevel(('Sector'), axis=1)

# Since the goal is equal gender representation, the female/male gap is calculated as the distance from 50% in either direction
# The gap is the absolute value of 50% - Female percentage:
clean_df['Gap'] = abs(0.5 - clean_df['Average female percentage'])

# Calculating index: (Actual value - worst value)/(Best value - worst value)
Best_value = 0
Worst_value = 0.5
clean_df['Index'] = (clean_df['Gap']-Worst_value)/(Best_value-Worst_value)

print(clean_df)

# Pivoting in order to fill in zeros for Nans where there is insufficent data to calculate
# the gap and thereby the index
fill_na_df = clean_df.pivot_table(clean_df, index=['Country'], columns=['Year'])
fill_na_df = fill_na_df.fillna(0)
# Reshaping to 'Country, Year, Average female percentage, gap, Index'
final_df = fill_na_df.stack()

# 2.2 Compare if each country has the same number of rows

control_df = final_df.pivot_table(final_df, index=['Country'], columns=['Year'])
print(control_df.count())
# 27 datapoints for each year


# 2.3 Compare if each year has the same number of rows
control_df = final_df.pivot_table(final_df, index=['Year'], columns=['Country'])
print(control_df)



#final_df.to_csv('Economic sector representation 2013-2022.csv')
#final_df.to_excel('Economic sector representation 2013-2022.xlsx')