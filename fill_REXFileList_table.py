import sqlite3

from utils.meth_utils import full_2_short

FNamesqlite = "ES_meth_calls.sqlite"
tableName = "REXFileList"
conn = sqlite3.connect(FNamesqlite)
cur = conn.cursor()

CLEARTABLE=True

if CLEARTABLE:
    cur.execute("DELETE FROM {}".format(tableName))

RexFileList = 'RexFileList.txt'

with open(RexFileList, 'r') as fp:
    listFiles = fp.readlines()


for FName in listFiles:
    FName = FName[:-1]

    print("ADDINGS", FName)
    geneName = FName.split('_')[0].upper()
    if "cell_lines_b" in FName.lower():
        sampleGroup="CLB"
    elif "cell_lines_c" in FName.lower():
        sampleGroup="CLC"
    elif "cell_lines" in FName.lower():
        sampleGroup="CL"
    elif "plate" in FName.lower():
        sampleGroup="PLATE"+FName.split('_')[2]
    elif "sample_group" in FName.lower():
        sampleGroup=FName.split('_')[3].upper()
    else:
        sampleGroup = ""
        #print("NO SAMPLE GROUP FOUND")

    print(geneName, full_2_short(geneName), sampleGroup)
    strSQL = """INSERT INTO {}(FileName, GeneName, GeneNameShort, SampleGroup)
                VALUES(?,?,?,?);
                """.format(tableName)
    #print(strSQL)
    cur.execute(strSQL, [FName, geneName, full_2_short(geneName), sampleGroup])

conn.commit()