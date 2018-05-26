import sqlite3
import pandas as pd
import numpy as np

# Create your connection.
cnx = sqlite3.connect('ES_meth_calls.sqlite')
new = pd.read_sql_query("SELECT * FROM ES_new_calls", cnx)
old = pd.read_sql_query("SELECT * FROM ES_old_calls", cnx)
cnx.close()

new2old = {'AD': 'ADCY8', 'DP': 'DPYS', 'GA': 'GARL1',
           'GR': 'GRM6', 'H12': 'HOXD12', 'HD9': 'None', 'PR': 'PRAC',
           'PT': 'PTGDR', 'SA': 'SALL3', 'SI': 'SIX6', 'SL': 'SLC6A2',
           'TL': 'TLX3', 'TR': 'TRIM58', 'ZF': 'ZFP41'}
old2new = {new2old[i]: i for i in new2old.keys() if new2old[i] is not None}

# list labels that are trustworthy for each of three things
# --> is methylated
# --> homogeneous/heterogeneous
# --> level of methylation

########## labels in new
# Homogeneous_or_Heterogeneous_or_Unclear?_(O/E/?) O means homo, E means hetero, ?, Null means never asked
# Control_'a'_Assessment, Control_'b'_Assessment  and Sample_'a'_Quality,Sample_'a'_Quality are the same things for control/not control
# Methylated_(Y/N) , if not methylated, won't have homo/hetero or methylation level
# Level of Methylation 0-100

# percentage = Level_of_methylation
# yes/no = Methylated_(Y/N)
# same/diff = Homogeneous_or_Heterogeneous_or_Unclear?_(O/E/?)
# gene = Gene_Name

old['Gene_Name'] = [old2new[i] for i in old.gene]
old.index = [a.Gene_Name + '_' + a._9 for a in old.itertuples()]
new.index = [a.Gene_Name + '_' + a.ID_info for a in new.itertuples()]

shared = old.join(new, lsuffix='_old', how='inner')
shared.rename(columns={'yes/no': 'yesno', 'Methylated_(Y/N)': 'Methylated_YN', 'same/diff': 'samediff',
                       '_Methylation_Homogeneous_or_Heterogeneous_or_Unclear?_(O/E/?)': 'homo_or_hetero'}, inplace=True)


################## get a list of samples where methylation agrees between old and new
# convert any characters to uppercase, ignore errors due to None
def toupper(x):
    try:
        return x.upper()
    except:
        return x


shared['Methylated_YN'] = shared['Methylated_YN'].apply(toupper)
shared['yesno'] = shared['yesno'].apply(toupper)

methylated = shared[shared['yesno'] == shared['Methylated_YN']]


################## get a list of samples where homo/hetero agrees between old and new
def convert_hh(x):
    try:
        if x.upper() == 'O' or x.upper() == 'S':
            return 'O'
        elif x.upper() == 'E' or x.upper() == 'D':
            return 'E'
    except:
        return x


shared['homo_or_hetero'] = shared['homo_or_hetero'].apply(convert_hh)
shared['samediff'] = shared['samediff'].apply(convert_hh)

print(shared['samediff'])
homohetero = shared[shared['homo_or_hetero'] == shared['samediff']]
print(homohetero['homo_or_hetero'])
print(np.shape(homohetero))

'''

##### convert all the calls to uppercase
#print(shared['yes/no'])
yesno,meth = [],[]
for row in shared.itertuples():
    if row.yesno == 'Y': yesno.append('Y')
    if row.yesno == 'N': yesno.append('N')
    

shared['Methylated_YN'] = meth
shared[shared['Methylated_(Y/N)']=='m']['Methylated_(Y/N)'] = 'N'
shared['yes/no'] = [str(i).upper() for i in shared['yes/no'] if len(str(i)) > 0]
shared['Methylated_(Y/N)'] = [str(i).upper() for i in shared['Methylated_(Y/N)'] if len(str(i)) > 0]




print(np.unique(shared['yes/no']))
print(np.unique(shared['Methylated_(Y/N)']))
'''
