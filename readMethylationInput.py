import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import ntpath

def getFeaturesFromRex(fname):
    # this function will take a filename and get the input features for each of the samples in the file    
   
    from readRunFile import loadRex
    
    # get the gene and run names from fname.
    geneName = ntpath.basename(fname).split('_')[0]
    
    if re.search("cell_lines", ntpath.basename(fname), re.IGNORECASE):
        sampleGroup = "CL"
    elif re.search("plate", ntpath.basename(fname), re.IGNORECASE):
        sampleGroup = ntpath.basename(fname).split('_')[2]
    elif re.search("sample_group", ntpath.basename(fname), re.IGNORECASE):
        sampleGroup = ntpath.basename(fname).split('_')[3] 
    else:
        print("CAN'T FIND SAMPLE GROUP FOR", fname)
        
    
    # read the rex file to get the data.
    try:
        control, controlQpcr, exp, expQpcr, controlLabel, expLabel, numControl, numExp, temperature = loadRex(fileName)
    except:
        print("error reading", fileName)
        
        raise
    
        
    listFeatures = []
    
    
    for i, tempExp in enumerate(exp):
        tempFeat = geneName,sampleGroup,i, np.vstack([control[2:],tempExp])
                #"Features": np.vstack([control[2:],tempExp])})
        
        listFeatures.append(tempFeat)
        
    dfFeatures = pd.DataFrame(listFeatures, columns=['geneName', 'sampleGroup', 'sampleNumber', 'Features'])    
    return(dfFeatures)   
    
    #control, controlQpcr, exp, expQpcr, controlLabel, expLabel, numControl, numExp, temperature = loadRex(fileName)
    
if __name__=="__main__":inputListFileName = './inputlist.txt'


with open(inputListFileName) as fp:
    fileList = fp.readlines()
        
    fileList = [f.strip() for f in fileList]

    for fileName in fileList[0:1]:
    #for fileName in fileList:
        
        print("getting features for", fileName)
        try:
            listFeatures = getFeaturesFromRex(fileName)
        except :
            raise
        
        
        print(listFeatures)
#        for Features in listFeatures:
#            print(Features['geneName'], Features['sampleGroup'], Features['sampleNumber'])
        
        
        
            
