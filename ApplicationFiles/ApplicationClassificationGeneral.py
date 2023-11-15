#!/usr/bin/env python
## \file
## \ingroup tutorial_tmva_keras
## \notebook -nodraw
## This tutorial shows how to apply a trained model to new data.
##
## \macro_code
##
## \date 2017
## \author TMVA Team

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


###################################
#data = TFile.Open('signalNew.root')
#signal = data.Get('treeList_0_24_0_24_Sgn')

######################################

data = TFile.Open('dataNew.root')
signal = data.Get('treeList_0_24_0_24_Sgn')

#dataBack = TFile.Open('dataNew.root')
#background = dataBack.Get('treeList_0_24_0_24_Sgn')


#branches = {}
#for branch in signal.GetListOfBranches():
#    branchName = branch.GetName()
#    branches[branchName] = array('f', [-999])
#    reader.AddVariable(branchName, branches[branchName])
#    signal.SetBranchAddress(branchName, branches[branchName])
#    background.SetBranchAddress(branchName, branches[branchName])

variables = {}
variableNames = ['massK0S', 'tImpParBach', 'tImpParV0', 'CtK0S', 'cosPAK0S', 'nSigmapr', 'dcaV0', 'asymmPt']
#variableNames = ['massK0S', 'tImpParBach', 'tImpParV0', 'CtK0S', 'cosPAK0S', 'nSigmapr', 'dcaV0']
for i in range(8):
    print(i, variableNames[i])
    varName = variableNames[i];
    variables[varName] = array('f', [-999])
    reader.AddVariable(varName, variables[varName])
    signal.SetBranchAddress(varName, variables[varName])
    #background.SetBranchAddress(varName, variables[varName])

spectators = {}
spectatorNames =  ['LcPt', 'massLc2K0Sp']
for i in range(2):
    specName = spectatorNames[i]
    spectators[specName] = array('f', [-999])
    signal.SetBranchAddress(specName, spectators[specName])


# Book methods
reader.BookMVA('PyKeras', TString('dataset/weights/TMVAClassification_PyKeras.weights.xml'))
reader.BookMVA('BDT', TString('dataset/weights/TMVAClassification_BDT.weights.xml'))
reader.BookMVA('Fischer', TString('dataset/weights/TMVAClassification_Fisher.weights.xml'))
reader.BookMVA('MLP', TString('dataset/weights/TMVAClassification_MLP.weights.xml'))
#reader.BookMVA('DNN', TString('dataset/weights/TMVAClassification_DNN.weights.xml'))
reader.BookMVA('DL', TString('dataset/weights/TMVAClassification_DL.weights.xml'))

# Print some example classifications

output = TFile.Open('applicationfileProva.root', 'RECREATE')

histKeras = TH1F('histKeras', 'histKeras', 1000, -1.0, 1.0 )
histBDT = TH1F('histBDT', 'histBDT', 1000, -1.0, 1.0)
histFischer = TH1F('histFischer', 'histFischer', 1000, -1.0, 1.0)
histMLP = TH1F('MLP', 'MLP', 1000, -1.0, 1.0)
#histDNN = TH1F('DNN', 'DNN', 1000, -1.0, 2.0)
histDL = TH1F('DL', 'DL', 1000, -1.0, 1.0)


histVsInvMassKeras = TH2F( 'MVA_vs_InvMassKeras', 'MVA_vs_InvMassKeras; m_{inv}(pK^{0}_{S})[GeV/#it{c}^{2}]; pyKeras', 1000, 2.05, 2.55, 1000, -1.0, 1)
histVsInvMassBDT = TH2F( 'MVA_vs_InvMassBDT', 'MVA_vs_InvMassBDT; m_{inv}(pK^{0}_{S})[GeV/#it{c}^{2}]; BDT', 1000, 2.05, 2.55, 1000, -1.0, 1)
histVsInvMassFischer = TH2F( 'MVA_vs_InvMassFischer', 'MVA_vs_InvMassFischer; m_{inv}(pK^{0}_{S})[GeV/#it{c}^{2}]; Fischer', 1000, 2.05, 2.55, 1000, -1.0, 1)
histVsInvMassMLP = TH2F( 'MVA_vs_InvMassMLP', 'MVA_vs_InvMassMLP; m_{inv}(pK^{0}_{S})[GeV/#it{c}^{2}]; MLP', 1000, 2.05, 2.55, 1000, -1.0, 1)
histVsInvMassDNN = TH2F( 'MVA_vs_InvMassDNN', 'MVA_vs_InvMassDNN; m_{inv}(pK^{0}_{S})[GeV/#it{c}^{2}]; DNN', 1000, 2.05, 2.55, 1000, -1.0, 2)
histVsInvMassDL = TH2F( 'MVA_vs_InvMassDL', 'MVA_vs_InvMassDL; m_{inv}(pK^{0}_{S})[GeV/#it{c}^{2}]; DL', 1000, 2.05, 2.55, 1000, -1.0, 1)



histInvariantMass = TH1F('histInvariantMass', 'Invariant Mass; m_{inv}(pK^{0}_{S})[GeV/#it{c}^{2}]; Entries', 1000, 2.05, 2.55)
histInvariantMass2D = TH2F('histInvariantMass2D', 'Invariant Mass 2D; m_{inv}(pK^{0}_{S})[GeV/#it{c}^{2}]; Entries',1000, 2.05, 2.55, 1000, -1.0, 1)
    
print('Processing tree:')
nevents = signal.GetEntries()
print('Number of events: ', nevents)
for i in range(50000): #RIMETTERE nevents PER OTTIMIZZARE, LASCIARE 10000 PER VELOCIZZARE
#for i in range(nevents):
    if i%10000 == 0:
        print('--- ... Processing event: ', i)
    signal.GetEntry(i)
    LcPt = spectators['LcPt'][0]
    massLc2K0Sp = spectators['massLc2K0Sp'][0]
    if LcPt < 1.0 and LcPt > 0.0:
     histKeras.Fill(reader.EvaluateMVA('PyKeras'))
     histBDT.Fill(reader.EvaluateMVA('BDT'))
     histFischer.Fill(reader.EvaluateMVA('Fischer'))
     histMLP.Fill(reader.EvaluateMVA('MLP'))
     #histDNN.Fill(reader.EvaluateMVA('DNN'))
     histDL.Fill(reader.EvaluateMVA('DL'))
     
     
     histVsInvMassKeras.Fill(massLc2K0Sp, reader.EvaluateMVA('PyKeras'))
     histVsInvMassBDT.Fill(massLc2K0Sp, reader.EvaluateMVA('BDT'))
     histVsInvMassFischer.Fill(massLc2K0Sp, reader.EvaluateMVA('Fischer'))
     histVsInvMassMLP.Fill(massLc2K0Sp, reader.EvaluateMVA('MLP'))
     #histVsInvMassDNN.Fill(massLc2K0Sp, reader.EvaluateMVA('DNN'))
     histVsInvMassDL.Fill(massLc2K0Sp, reader.EvaluateMVA('DL'))
     
     invariantMass = massLc2K0Sp
     
     histInvariantMass.Fill(invariantMass)
     #histInvariantMass2D.Fill()
print('Finished')

#canvas = ROOT.TCanvas("canvas", "Visualizzazione Istogramma", 800, 600)

histKeras.Write()
histBDT.Write()
histFischer.Write()
histMLP.Write()
#histDNN.Write()
histDL.Write()


histVsInvMassKeras.Write()
histVsInvMassBDT.Write()
histVsInvMassFischer.Write()
histVsInvMassMLP.Write()
#histVsInvMassDNN.Write()
histVsInvMassDL.Write()


histInvariantMass.Write()
#hist.Draw()
#histVsInvMass.Draw()

#ROOT.gApplication.Run()

output.Close()

#ROOT.gApplication.Terminate()

