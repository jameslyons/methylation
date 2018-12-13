from readRunFile import loadRex
from sklearn.svm import SVR
import re
import numpy as np
from scipy.optimize import minimize
import os


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
        fun = lambda x: np.sum((singleExp - ((1 - x) * meanZpc) - x * meanHpc) ** 2)
        # res = minimize(fun, 0.5, bounds=bnds)
        res = minimize(fun, 0.5)

        listFeat.append(res.x[0])

    return listFeat


def label(controlLabel):
    listLabel = []
    for lab in controlLabel:
        listLabel.append(float(lab.split("%")[0]))
    return listLabel


#fileName = '/home/rhys/work/forElgit/RexFiles/HOXD12_Sample_Group_4b_61oC_140617.rex'

FNameREXList = 'RexList.txt'
with open(FNameREXList) as fp:
    listREXNames = fp.read().splitlines()

for REXName in listREXNames:
    #fileName='/home/rhys/work/forElgit/RexFiles/DPYS_PLATE_8_60oC_120517.rex'

    FNameREX = '/home/rhys/work/forElgit/RexFiles/'+REXName
    print(FNameREX)

    FNameOutput = os.path.splitext(os.path.basename(FNameREX))[0]+".svm"


    # read the rex file to get the data.
    try:
        control, controlQpcr, exp, expQpcr, controlLabel, expLabel, numControl, numExp, temperature = loadRex(FNameREX)
    except:
        print("error reading", FNameREX)
        raise

    featControl=feat(control, controlLabel, control[2:])
    featExp    =feat(control, controlLabel, exp)

    labelControl = label(controlLabel[2:])

    '''
    for C in [0.001,0.01,0.1,0.2,0.5,0.8,1,2,5]:
        for ESPILON in [0.001,0.01,0.1,0.2,0.5,0.8,1,2,5]:

            mod = SVR(kernel='rbf', C=C, epsilon=ESPILON)
            mod.fit(np.matrix(featControl).T, np.array(labelControl))
            pred = mod.predict(np.matrix(featExp).T)
            #print(C, ESPILON, pred)
    '''


    gridERR =[]
    gridC = []
    gridEPSILON = []

    #listC = list(np.linspace(0.001, 50, 50))
    listC = list(np.logspace(-3, 5))
    listEPSILON = list(np.linspace(0, 15, 50))

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

            gridERR.append(np.sum(accCV))

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
    mod.fit(np.matrix(featControl).T, np.array(labelControl)/100)
    predExp = mod.predict(np.matrix(featExp).T)*100

    #print(predExp)

    strTemp = "\n".join([str(a) for a in predExp])
    #print(strTemp)

    with open('./results/'+FNameOutput, 'w') as fpPred:
        fpPred.write(strTemp)

