# this version works in windows/python3, but needed mods to work in linux/python2
# presumably need to run dos2unix on the files before opening them in linux

from __future__ import print_function
import numpy as np
import re

def readRunFile(fname):
    try:
        f = open(fname,'r')
    except IOError:
        raise IOError
    else:
        data = []
        header = f.readline().rstrip()
        header = re.split(r'[\t,]',header)
        # check the header to see which of the two formats we are working with.
        # one will have every second (1,3,5,etc) field == 'X'
        # The second will have every third (1,4,7, etc) field == 'X' and (2,5,8, etc) == 'Y'
        if header[1] == 'X' and header[4] == 'X' and header[7] == 'X':
            
            for i, line in enumerate(f):
                line = line.split(',')
                if i == 0:
                    heading = [line[i] for i in range(len(line)) if i % 3 == 0]                    
                line = [line[i] for i in range(len(line)) if i % 3 != 0]
                line = [float(i) for i in line]
                if len(line) <1: continue
                data.append(line)
        elif header[1] == 'X' and header[3] == 'X' and header[5] == 'X':
            heading = [header[i] for i in range(2,len(header),2)]
            
            for line in f:
                line = re.split(r'[\t,]',line)[1:]
                line = [float(i) for i in line]
                if len(line) <1: continue
                data.append(line)
        else:
            print('Invalid file type. Can\'t read {}'.format(fname))
            raise Exception('Invalid file type {}'.format(fname))
        f.close()
        return heading, np.vstack(data)
        

def loadRun(fname, returnTemp=None):

    heading, data = readRunFile(fname)

    # parse the headings to find the length of the controls, the control labels, and the length of the exp
    controlLabel = []
    sampleLabel = []
    for h in heading:
        sampleID, name = h.split(': ')
        name = name.upper().rstrip()

        # if it's the NTC, add it to the control labels
        if 'NTC' in name:
            controlLabel.append(name)
        # if the name ends in a % sign, we assume it's control
        elif '%' in name:
            controlLabel.append(name)
        # if the name starts with the work 'Sample' we assume it is one of the samples.
        else:
            sampleLabel.append(name)
#            else:
#                print('Unknown signal label - {}'.format(name))


    controlLen = len(controlLabel)
    expLen = len(sampleLabel)
    N,D = np.shape(data)
    control = np.zeros((controlLen,N))
    exp = np.zeros((expLen,N))

    if returnTemp == True:
        temperature = data[:,0]


    for i in range(controlLen):
        control[i,:] = data[:,i*2+1]
    for i in range(expLen):
        exp[i,:] = data[:,(i+controlLen)*2+1]
    if returnTemp == True:
        return control,exp, controlLabel, sampleLabel, controlLen, expLen, temperature
    else:
        return control,exp, controlLabel, sampleLabel, controlLen, expLen



def readRexFile(fname):
  import xml.etree.ElementTree as et
  #import matplotlib.pyplot as plt
  import numpy as np

  try:
    root = et.parse(fname).getroot()
  except IOError:
    raise IOError
  else:
  
    callerId = root.find('Operator').text
    startTime = root.find('StartTime').text
    
    meltStartTemp = float(root.find('Profile').find('MeltCycle').find('StartTemp').text)
    meltEndTemp = float(root.find('Profile').find('MeltCycle').find('EndTemp').text)
    meltStep = float(root.find('Profile').find('MeltCycle').find('TempStep').text)
    meltNumSteps = (meltEndTemp - meltStartTemp) / meltStep 
    meltAxis = np.linspace(meltStartTemp, meltEndTemp, meltNumSteps)
    
    #print(meltStartTemp, meltEndTemp, meltStep, meltNumSteps, meltAxis)
    
    allSample = []
    for rawSample in root.find('Samples').find('Page').findall('Sample'):
      sample = dict()
      sample['name'] = rawSample.find('Name').text
      sample['ID'] = rawSample.find('ID').text
      sample['tubePos'] = rawSample.find('TubePosition').text
      
      allSample.append(sample)
      
    for rawData in root.find('RawChannels').findall('RawChannel'):
    
      #print(rawData)
      
      # if this is the amp data
      #if rawData.find('Name').text == root.find('Analyses').find('Quantitate').find('RawChannelRef').text:
      if rawData.find('Name').text == "Cycling A.Green":
        print('found amp')
        # findall returns in the order that they are read in. I assume that the
        # data is saved in the same order here as it was in the sample section
        # above.
        for id, rawAmp in enumerate(rawData.findall('Reading')):
          allSample[id]['amp'] = np.array(rawAmp.text.split(' '),dtype=float)     
          allSample[id]['normAmp'] = np.log10(allSample[id]['amp'])
        
      # if this is the melt data
      #elif rawData.find('Name').text == root.find('Analyses').find('Melt').find('RawChannelRef').text:
      elif rawData.find('Name').text == "HRM A.HRM":
        print('found melt')
        # findall returns in the order that they are read in. I assume that the
        # data is saved in the same order here as it was in the sample section
        # above.
        for id, rawMelt in enumerate(rawData.findall('Reading')):
          allSample[id]['melt'] = np.array(rawMelt.text.split(' '),dtype=float)
          allSample[id]['dfdt'] = np.diff(allSample[id]['melt'])

      else:
        print(rawData.find('Name').text, 'wasn\'t amp ', root.find('Analyses').find('Quantitate').find('RawChannelRef').text, 'nor melt',root.find('Analyses').find('Melt').find('RawChannelRef').text )
        
         
    return allSample, meltAxis
  

def loadRex(fname):

    allSample, temperature = readRexFile(fname)
    controlLabel = []
    controlMelt = []
    controlDfdt = []
    controlNormAmp = []
    controlAmp = []
    sampleLabel = []
    sampleMelt = []
    sampleDfdt = []
    sampleNormAmp = []
    sampleAmp = []


    for ind, sample in enumerate(allSample):
        
        #print(ind, sample['name'])
            
        sampleID = sample['ID']
        name = sample['name'].upper()
    #    print(sample_id, name)    

        # if it's the NTC, add it to the control labels
        if 'NTC' in name: 
            controlLabel.append(name)
            controlMelt.append(sample['melt'])
            controlDfdt.append(sample['dfdt'])
            controlNormAmp.append(sample['normAmp'])
            controlAmp.append(sample['amp'])
            
        # if the name ends in a % sign, we assume it's control
        elif '%' in name: 
            controlLabel.append(name)
            controlMelt.append(sample['melt'])
            controlDfdt.append(sample['dfdt'])
            controlNormAmp.append(sample['normAmp'])
            controlAmp.append(sample['amp'])
            
        # if the name starts with the work 'Sample' we assume it is one of the samples.
        else: 
            sampleLabel.append(name)
            sampleMelt.append(sample['melt'])
            sampleDfdt.append(sample['dfdt'])
            sampleNormAmp.append(sample['normAmp'])
            sampleAmp.append(sample['amp'])
            
    #    else:
    #        print('Unknown signal label - {}'.format(name))
           
    controlLen = len(controlLabel)         
    expLen = len(sampleLabel)           
            
    controlMelt = np.array(controlMelt)   
    controlDfdt = np.array(controlDfdt)  
    controlAmp = np.array(controlAmp)  
    expMelt = np.array(sampleMelt)   
    expDfdt = np.array(sampleDfdt)
    expAmp = np.array(sampleAmp)       

    #print(control_melt, control_amp, exp_melt, exp_amp, control_label, sample_label, controlLen, expLen, temperature)
    return -controlDfdt, controlAmp, -expDfdt, expAmp, controlLabel, sampleLabel, controlLen, expLen, temperature
  
