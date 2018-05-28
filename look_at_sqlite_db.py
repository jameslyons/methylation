import sqlite3
import pandas as pd
import numpy as np
from utils.meth_utils import short_2_full, full_2_short

# Create your connection.
cnx = sqlite3.connect('ES_meth_calls.sqlite')
new = pd.read_sql_query("SELECT * FROM ES_new_calls", cnx)
old = pd.read_sql_query("SELECT * FROM ES_old_calls", cnx)
cnx.close()

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

old['Gene_Name'] = [full_2_short(i) for i in old.gene]
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

# print(shared['samediff'])
homohetero = shared[shared['homo_or_hetero'] == shared['samediff']]
# print(homohetero['homo_or_hetero'])
# print(np.shape(homohetero))

from glob import glob
import os

filenames = glob('results/*.svm')
for path in filenames:
    fname = os.path.split(path)[1]
    toks = fname.split('_')

    gene_name = full_2_short(toks[0])

    if ('cell' in fname.lower()) and ('lines' in fname.lower()):
        continue
    elif 'PLATE' in fname:
        sample_group = toks[1] + toks[2]
    elif 'Sample_Group' in fname:
        sample_group = toks[3]
    else:
        sample_group = toks[3]

    f = open(path)
    for count, line in enumerate(f):
        nrow = new[(new['Gene_Name'] == gene_name) & (new['Sample_Group'] == sample_group) & (
                    new['Sample_Number'] == np.ceil((count + 1) / 2))]
        nrow = nrow[['Gene_Name', 'Sample_Group', 'Sample_Number', 'Level_of_Methylation']].values

        if len(nrow) == 0:
            continue
        elif nrow[0][3] is None:
            continue
        elif 'estimative' in nrow[0][3].lower():
            continue

        print(gene_name, sample_group, nrow[0][2],nrow[0][3], line.strip(),sep=',')

        #orow = old[(old['gene'].upper() == short_2_full(gene_name)) & (old['Cohort'].split()[-1] == sample_group) & (
        #            new['Sample_Number'] == np.ceil((count + 1) / 2))]
        #nrow = nrow[['Gene_Name', 'Sample_Group', 'Sample_Number', 'Level_of_Methylation']].values