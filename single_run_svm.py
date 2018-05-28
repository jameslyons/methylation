from readRunFile import loadRex
from sklearn.svm import SVR
import matplotlib.pyplot as plt
import re
import numpy as np
from scipy.optimize import minimize

#fileName = '/home/rhys/work/forElgit/RexFiles/HOXD12_Sample_Group_4b_61oC_140617.rex'
fileName='/home/rhys/work/forElgit/RexFiles/DPYS_PLATE_8_60oC_120517.rex'

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

featControl=feat(control, controlLabel, control[2:])
featExp    =feat(control, controlLabel, exp)

labelControl = label(controlLabel[2:])

for C in [0.001,0.01,0.1,0.2,0.5,0.8,1,2,5]:
    for ESPILON in [0.001,0.01,0.1,0.2,0.5,0.8,1,2,5]:

        mod = SVR(kernel='rbf', C=C, epsilon=ESPILON)
        mod.fit(np.matrix(featControl).T, np.array(labelControl))
        pred = mod.predict(np.matrix(featExp).T)
        #print(C, ESPILON, pred)



gridERR =[]
gridC = []
gridEPSILON = []

listC = list(np.linspace(0.1, 15, 20))
listEPSILON = list(np.linspace(0, 15,20))

for C in listC:
    for EPSILON in listEPSILON:
        #print(C,EPSILON)
        gridC.append(C)
        gridEPSILON.append(EPSILON)

        accCV = []
        # leave one out CV
        for i in range(len(featControl)):
            labelTrain = [a for j,a in enumerate(labelControl) if j!=i]
            labelTest = labelControl[i]/100
            featTrain = [a for j,a in enumerate(featControl) if j!=i]
            featTest = featControl[i]/100

            modCV = SVR(kernel='rbf', C=C, epsilon=EPSILON)
            #print(featTrain, labelTrain)
            modCV.fit(np.matrix(featTrain).T,np.array(labelTrain))
            #print(featTest)
            predCV = modCV.predict(np.matrix(featTest).T)

            accCV.append((labelTest-predCV)**2)

        gridERR.append(np.mean(accCV))

'''
plt.figure()
plt.scatter(gridC, gridEPSILON, c=gridERR)
plt.xlabel('C')
plt.ylabel('Epsilon')
plt.colorbar()
plt.show()
'''

minERRIdx = np.argmin(gridERR)
minC = gridC[minERRIdx]
minEPSILON = gridEPSILON[minERRIdx]

mod = SVR(kernel='rbf', C=minC, epsilon=minEPSILON)
mod.fit(np.matrix(featControl).T, np.array(labelControl))
predExp = mod.predict(np.matrix(featExp).T)

print(predExp)

