import ROOT
from ROOT import TMVA, TFile, TString, TH1F, TH2F, TF1
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
reader.BookMVA('Fisher', TString('dataset/weights/TMVAClassification_Fisher.weights.xml'))

#FILE CREATION
output = TFile.Open('applicationfileFischer.root', 'RECREATE')

#HISTOGRAMS CREATION
histFisher = TH1F('histFisher', 'histFisher', 1000, -1.0, 1.0)
histVsInvMassFisher = TH2F( 'MVA_vs_InvMassFisher', 'MVA_vs_InvMassFisher; Fisher; m_{inv}(pK^{0}_{S})[GeV/#it{c}^{2}]', 1000, -1.0, 1.0, 1000, 2.05, 2.55)
histInvariantMass = TH1F('histInvariantMass', 'Invariant Mass; m_{inv}(pK^{0}_{S})[GeV/#it{c}^{2}]; Entries', 55, 2.05, 2.55)

#FIT CREATION
backgroundFit = TF1("gausFit", "gaus")
#TF1 *gausFit = new TF1("gausFit", "gaus");

#LOOP FOR FILLING HISTOGRAMS
print('Processing tree:')
nevents = signal.GetEntries()
print('Number of events: ', nevents)
#for i in range(nevents): #RIMETTERE nevents PER OTTIMIZZARE, LASCIARE 10000 PER VELOCIZZARE
for i in range(100000):
    if i%10000 == 0:
        print('--- ... Processing event: ', i)
    signal.GetEntry(i)
    LcPt = spectators['LcPt'][0]
    massLc2K0Sp = spectators['massLc2K0Sp'][0]
    if LcPt < 1.0 and LcPt > 0.0:
     histFisher.Fill(reader.EvaluateMVA('Fisher'))
     histVsInvMassFisher.Fill(reader.EvaluateMVA('Fisher'), massLc2K0Sp) 
     if reader.EvaluateMVA('Fisher') >= -0.045: #OTTIMALE A -0.0449
        histInvariantMass.Fill(massLc2K0Sp)

print('Finished loop')

#gaustFit()

histFisher.Write()
histVsInvMassFisher.Write()
histInvariantMass.Write()

output.Close()

print('Finished scripting Fisher')

