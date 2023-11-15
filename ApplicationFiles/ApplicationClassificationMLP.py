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
reader.BookMVA('MLP', TString('dataset/weights/TMVAClassification_MLP.weights.xml'))

#FILE CREATION
output = TFile.Open('applicationfileMLP.root', 'RECREATE')

#HISTOGRAMS CREATION
histMLP = TH1F('histMLP', 'histMLP', 1000, 0, 1.0)
histVsInvMassMLP = TH2F( 'MVA_vs_InvMassMLP', 'MVA_vs_InvMassKeras; Keras; m_{inv}(pK^{0}_{S})[GeV/#it{c}^{2}]', 1000, 0, 1.0, 1000, 2.05, 2.55)
histInvariantMass = TH1F('histInvariantMass', 'Invariant Mass; m_{inv}(pK^{0}_{S})[GeV/#it{c}^{2}]; Entries', 50, 2.05, 2.55)

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
     histMLP.Fill(reader.EvaluateMVA('MLP'))
     histVsInvMassMLP.Fill(reader.EvaluateMVA('MLP'), massLc2K0Sp) 
     if reader.EvaluateMVA('MLP') > 0.1005:  #OTTIMALE A 0.1005--->FATTO
        histInvariantMass.Fill(massLc2K0Sp)

print('Finished loop')

histMLP.Write()
histVsInvMassMLP.Write()
histInvariantMass.Write()

output.Close()

print('Finished scripting MLP')

