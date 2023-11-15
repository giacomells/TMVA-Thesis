import ROOT
import os

from ROOT import TMVA, TFile, TTree, TCut

from subprocess import call
from os.path import isfile


from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation
from tensorflow.keras.optimizers import SGD
 
# Setup TMVA
TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()
 
output = TFile.Open('TMVA_Classification_BDT.root', 'RECREATE')
factory = TMVA.Factory('TMVAClassification', output,
                       '!V:!Silent:Color:DrawProgressBar:Transformations=D,G:AnalysisType=Classification')
 

dataS = TFile.Open('signalNew.root')
dataB = TFile.Open('dataNew.root')
signal = dataS.Get('treeList_0_24_0_24_Sgn')
background = dataB.Get('treeList_0_24_0_24_Sgn')

dataloader = TMVA.DataLoader('dataset')
#for branch in signal.GetListOfBranches():
#    dataloader.AddVariable(branch.GetName())

dataloader.AddVariable('massK0S')
dataloader.AddVariable('tImpParBach')
dataloader.AddVariable('tImpParV0')
#dataloader.AddVariable('CtK0S := DecayLengthK0S*0.497/v0P')
dataloader.AddVariable('CtK0S')
dataloader.AddVariable('cosPAK0S')
#dataloader.AddVariable('CosThetaStar')
#dataloader.AddVariable('nSigmapr := nSigmaTOFpr > -900 ? sqrt(nSigmaTOFpr*nSigmaTOFpr + nSigmaTPCpr*nSigmaTPCpr) : nSigmaTPCpr')
dataloader.AddVariable('nSigmapr')
dataloader.AddVariable('dcaV0')
#dataloader.AddVariable('bachelorPt')   #QUESTE VARIABILI SEMBRANO NON FARE
#dataloader.AddVariable('v0Pt')         #FUNZIONARE IL MODELLO
#dataloader.AddVariable('massLc2K0Sp')  #COME FACCIO ALLORA AD UTILIZZARE ASYMMPT?????
#dataloader.AddVariable('LcPt')         #MANNAGGIAAAAA
#dataloader.AddVariable('asymmPt := (bachelorPt-v0Pt)/(bachelorPt+v0Pt)')
dataloader.AddVariable('asymmPt')

#dataloader.AddSpectator('LcPt')
#dataloader.AddSpectator('origin')

dataloader.AddSignalTree(signal, 1.0)
dataloader.AddBackgroundTree(background, 1.0)
#dataloader.PrepareTrainingAndTestTree(TCut(''),
#                                      'nTrain_Signal=4000:nTrain_Background=4000:SplitMode=Random:NormMode=NumEvents:!V')
mycuts = TCut('LcPt < 1.0 && LcPt > 0.0 && origin == 4');
mycutb = TCut('LcPt < 1.0 && LcPt > 0.0 && abs(massLc2K0Sp - 2.286) > 3*0.0076');
dataloader.PrepareTrainingAndTestTree(mycuts, mycutb, 'nTrain_Signal=10000:nTrain_Background=100000:nTest_Signal=10000:nTest_Background=100000:SplitMode=Random:NormMode=NumEvents:!V')


# Generate model
 
# Define model
model = Sequential()
model.add(Dense(64, activation='relu', input_dim=8))
model.add(Dense(2, activation='softmax'))
 
# Set loss and optimizer
model.compile(loss='categorical_crossentropy',
              optimizer=SGD(learning_rate=0.01), weighted_metrics=['accuracy', ])
 
# Store model to file
model.save('modelClassification.h5')
model.summary()
 
# Book methods
#factory.BookMethod(dataloader, TMVA.Types.kFisher, 'Fisher',
#                   '!H:!V:Fisher:VarTransform=D,G')
factory.BookMethod(dataloader, TMVA.Types.kBDT, 'BDT',
		           '!H:!V:NTrees=850:MinNodeSize=2.5%:MaxDepth=3:BoostType=AdaBoost:AdaBoostBeta=0.5:UseBaggedBoost:BaggedSampleFraction=0.5:SeparationType=GiniIndex:nCuts=20');
#factory.BookMethod(dataloader, TMVA.Types.kPyKeras, 'PyKeras',
#                   'H:!V:VarTransform=D,G:FilenameModel=modelClassification.h5:FilenameTrainedModel=trainedModelClassification.h5:NumEpochs=20:BatchSize=32')
#factory.BookMethod(dataloader, ROOT.TMVA.Types.kMLP, "MLP",
#                   "H:!V:NeuronType=tanh:VarTransform=N:NCycles=500:HiddenLayers=N+5:TestRate=5:!UseRegulator")
#factory.BookMethod(dataloader, ROOT.TMVA.Types.kDNN, "DNN",
#                   "H:!V:VarTransform=N:Layout=TANH|128,TANH|128,TANH|128,LINEAR")
#factory.BookMethod(dataloader, TMVA.Types.kDL, "DL",
#                   "H:!V:VarTransform=N:Architecture=CPU:Layout=TANH|128,TANH|128,TANH|128,LINEAR:!UseRegolator")


# Run training, test and evaluation
factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()
