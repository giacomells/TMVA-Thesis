import ROOT
from ROOT import TMVA, TFile, TString, TH1F, TH2F
from array import array
from subprocess import call
from os.path import isfile
import math



# Setup TMVA
TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()
reader = TMVA.Reader("Color:!Silent")

#LOAD DATA
data = TFile.Open('dataNew.root')
signal = data.Get('treeList_0_24_0_24_Sgn')

#VARIABLES ASSOCIATION
variables = {}
variableNames = ['massK0S', 'tImpParBach', 'tImpParV0', 'CtK0S', 'cosPAK0S', 'nSigmapr', 'dcaV0', 'asymmPt']
for i in range(8):
    print(i, variableNames[i])
    varName = variableNames[i];
    variables[varName] = array('f', [-999])
    reader.AddVariable(varName, variables[varName])
    signal.SetBranchAddress(varName, variables[varName])   
    
#SPECATATORS ASSOCIATION
spectators = {}
spectatorNames =  ['LcPt', 'massLc2K0Sp']
for i in range(2):
    specName = spectatorNames[i]
    spectators[specName] = array('f', [-999])
    signal.SetBranchAddress(specName, spectators[specName])
    
#BOOK METHODS
reader.BookMVA('PyKeras', TString('dataset/weights/TMVAClassification_PyKeras.weights.xml'))

#FILE CREATION
output = TFile.Open('applicationfileKeras.root', 'RECREATE')

#HISTOGRAMS CREATION
histKeras = TH1F('histKeras', 'histKeras', 1000, 0, 1.0)
histVsInvMassKeras = TH2F( 'MVA_vs_InvMassKeras', 'MVA_vs_InvMassKeras; Keras m_{inv}(pK^{0}_{S})[GeV/#it{c}^{2}]', 1000, 0, 1.0, 1000, 2.05, 2.55)
histInvariantMass = TH1F('histInvariantMass', 'Invariant Mass; m_{inv}(pK^{0}_{S})[GeV/#it{c}^{2}]; Entries', 1000, 2.05, 2.55)

#LOOP FOR FILLING HISTOGRAMS
print('Processing tree:')
nevents = signal.GetEntries()
print('Number of events: ', nevents)
#for i in range(100000): #RIMETTERE nevents PER OTTIMIZZARE, LASCIARE 10000 PER VELOCIZZARE
for i in range(nevents):
    if i%10000 == 0:
        print('--- ... Processing event: ', i)
    signal.GetEntry(i)
    LcPt = spectators['LcPt'][0]
    massLc2K0Sp = spectators['massLc2K0Sp'][0]
    if LcPt < 1.0 and LcPt > 0.0:
     histKeras.Fill(reader.EvaluateMVA('PyKeras'))
     histVsInvMassKeras.Fill(reader.EvaluateMVA('PyKeras'), massLc2K0Sp) 
     if reader.EvaluateMVA('PyKeras') > 0.08:  #OTTIMALE A 0.0881---->FATTO A 0.08
        histInvariantMass.Fill(massLc2K0Sp)

print('Finished loop')

histKeras.Write()
histVsInvMassKeras.Write()
histInvariantMass.Write()

output.Close()

print('Finished scripting Keras')

