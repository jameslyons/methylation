from readRunFile import loadRex
from sklearn.svm import SVR
import matplotlib.pyplot as plt
import re
import numpy as np
from scipy.optimize import minimize

fileName = '/home/rhys/work/ForEl/RUN_FILES_V5_Combined/ADCY8_Sample_Group_4b_58oC_150617.rex'

def feat(control, controlLabel, exp):
    listzpc = []
    listhpc = []
    for i, cntrLabel in enumerate(controlLabel):
        if re.match("^0", cntrLabel):
            listzpc.append(control[i, :])
        elif "100" in cntrLabel:
            listhpc.append(control[i, :])

    meanZpc = np.mean(np.array(listzpc), axis=0)
    meanHpc = np.mean(np.array(listhpc), axis=0)

    bnds = ((0, 1))

    listFeat = []
    for singleExp in exp:
        fun = lambda x: np.sum((singleExp - ((1-x)*meanZpc) - x*meanHpc)**2)
        #res = minimize(fun, 0.5, bounds=bnds)
        res = minimize(fun, 0.5)

        listFeat.append(res.x[0])

    return listFeat

def label(controlLabel):
    listLabel = []
    for lab in controlLabel:
        listLabel.append(float(lab.split("%")[0]))
    return listLabel


# read the rex file to get the data.
try:
    control, controlQpcr, exp, expQpcr, controlLabel, expLabel, numControl, numExp, temperature = loadRex(fileName)
except:
    print("error reading", fileName)
    raise

print(controlLabel)

controlFeat=feat(control, controlLabel, control[2:])
expFeat    =feat(control, controlLabel, exp)

controlLabel = label(controlLabel[2:])
print(controlLabel)

mod = SVR()
mod.fit(np.matrix(controlFeat).T,np.array(controlLabel))
pred = mod.predict(np.matrix(expFeat).T)
print(pred)