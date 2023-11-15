#include <iostream>
#include <cmath>
#include <cstdlib>
#include "TFile.h"
#include "TMath.h"

#include "TROOT.h"
#include "TStyle.h"
#include "TH1F.h"
#include "TF1.h"
#include "TCanvas.h"

#include "TMVA/Tools.h"
#include "TMVA/Reader.h"
#include "TMVA/PyMethodBase.h"
#include "TTree.h"
#include "TH1F.h"
#include "TF1.h"
#include "TGraphErrors.h"

#include <iostream>

void histCreation()
{
    // Setup TMVA
    TMVA::Tools::Instance();
    TMVA::PyMethodBase::PyInitialize();
    TMVA::Reader reader("Color:!Silent"); // Utilizzo diretto dell'oggetto reader invece di un puntatore

    // LOAD DATA
    TFile data("dataNew.root");                                                // Utilizzo diretto dell'oggetto data invece di un puntatore
    TTree *signal = dynamic_cast<TTree *>(data.Get("treeList_0_24_0_24_Sgn")); // Utilizzo dynamic_cast per gestire eventuali errori

    // VARIABLES ASSOCIATION
    std::vector<Float_t> varValues(8, -999); // Creazione di un vettore per i valori delle variabili
    std::vector<std::string> variableNames = {"massK0S", "tImpParBach", "tImpParV0", "CtK0S", "cosPAK0S", "nSigmapr", "dcaV0", "asymmPt"};
    for (int i = 0; i < 8; i++)
    {
        reader.AddVariable(variableNames[i], &varValues[i]); // Utilizzo diretto dell'oggetto reader
        signal->SetBranchAddress(variableNames[i].c_str(), &varValues[i]);
    }

    // SPECTATORS ASSOCIATION
    std::map<std::string, Float_t> spectators; // Rimozione di una variabile non utilizzata
    std::vector<std::string> spectatorNames = {"LcPt", "massLc2K0Sp"};
    for (const auto &specName : spectatorNames)
    {
        Float_t specValue = -999;
        spectators[specName] = specValue; // Inizializzazione diretta della mappa
        signal->SetBranchAddress(specName.c_str(), &spectators[specName]);
    }

    // BOOK METHODS
    reader.BookMVA("Fisher", "dataset/weights/TMVAClassification_Fisher.weights.xml");

    // FILE CREATION
    TFile *output = new TFile("AnalysisFisher.root", "RECREATE");

    // HISTOGRAMS CREATION
    TH1F *histInvariantMassFisher = new TH1F("histInvariantMass", "Invariant Mass; m_{inv}(pK^{0}_{S})[GeV/#it{c}^{2}]; Entries", 60, 2.1, 2.43);

    // LOOP FOR FILLING HISTOGRAMS
    std::cout << "Processing tree:" << std::endl;
    Int_t nevents = signal->GetEntries();
    std::cout << "Number of events: " << nevents << std::endl;
    for (Int_t i = 0; i < nevents; i++)
    {
        if (i % 10000 == 0)
        {
            std::cout << "--- ... Processing event: " << i << std::endl;
        }
        signal->GetEntry(i);
        Float_t LcPt = spectators["LcPt"];
        Float_t massLc2K0Sp = spectators["massLc2K0Sp"];
        if (LcPt < 1.0 && LcPt > 0.0)
        {
            if (reader.EvaluateMVA("Fisher") >= -0.045)
            {
                histInvariantMassFisher->Fill(massLc2K0Sp);
            }
        }
    }

    std::cout << "Finished loop" << std::endl;

    // canvas.Write();
    output->Write();
    output->Close();
}

//////////////////////////////////////////////////////////////

void smartAnalysis()
{
    // FILE CREATION
    TFile *output = new TFile("AnalysisFisher.root");
    // HISTOGRAM CREATION
    TH1F *histInvariantMassFisher = (TH1F *)output->Get("histInvariantMass");
    TH1F *histDifference = (TH1F *)histInvariantMassFisher->Clone("histDifference");
    histDifference->SetTitle("Segnale massa invariante;Massa Invariante;Conteggio");

    // FITTING CREATION
    TF1 *backgroundFit = new TF1("backgroundFit", "pol3", 2.1, 2.43);
    backgroundFit->SetLineColor(kYellow);
    backgroundFit->SetLineWidth(5);
    TF1 *gausFit = new TF1("gausFit", "gaus");
    gausFit->SetLineColor(kRed);
    gausFit->SetLineWidth(5);

    // SAVING IN A ROOT FILE-----> NON SALVA L'ISTOGRAMMA FITTATO, PERCHÈ????
    TFile *finalHisto = new TFile("finalHisto.root", "RECREATE");
    // 1ST CANVAS
    TCanvas *canvas1 = new TCanvas("canvas1", "Results", 200, 10, 1400, 900);
    canvas1->SetGrid();

    // BACKGROUND FITTING
    histInvariantMassFisher->Fit("backgroundFit", "Q", "", 2.1, 2.43);
    histInvariantMassFisher->DrawCopy();

    // LOOP FOR CREATION OF HISTDIFFERENCE
    for (int i = 1; i <= histInvariantMassFisher->GetNbinsX(); ++i)
    {
        // Troviamo il centro del bin
        double binCenter = histInvariantMassFisher->GetBinCenter(i);
        // Valutiamo il fit in questo punto
        double fitValue = backgroundFit->Eval(binCenter);
        // Otteniamo il contenuto del bin originale
        double binContent = histInvariantMassFisher->GetBinContent(i);
        // Calcoliamo la differenza e impostiamo il nuovo contenuto per il bin
        histDifference->SetBinContent(i, binContent - fitValue);
    }
    // AUMENTO L'ERRORE
    for (int i = 1; i <= histDifference->GetNbinsX(); ++i)
    {
        double currentError = histDifference->GetBinError(i);
        double newError = currentError * 13;
        histDifference->SetBinError(i, newError);
    }

    // 2ND CANVAS
    TCanvas *canvas2 = new TCanvas("canvas2", "Results", 200, 10, 1400, 900);
    canvas2->cd();
    canvas2->SetGrid();

    histDifference->SetMarkerStyle(20);  // Imposta lo stile del marcatore per una migliore visualizzazione
    histDifference->SetLineColor(kBlue); // Imposta il colore della linea dell'istogramma

    gausFit->SetParameter(1, 2.28);
    // gausFit->SetParLimits(1, 2.26, 2.288);
    histDifference->Fit("gausFit", "Q", "", 2.1, 2.45);

    histDifference->GetXaxis()->SetTitle("m_{inv}(pK^{0}_{S})[GeV/#it{c}^{2}]");
    histDifference->GetXaxis()->SetTitleOffset(1.1);
    histDifference->GetYaxis()->SetTitleOffset(1.3);
    histDifference->DrawCopy("E1"); // Disegna l'istogramma con gli errori
    histDifference->Write();

    // Aggiornare la canvas per mostrare l'istogramma
    canvas2->Modified();                                      // Assicurati che la canvas sia aggiornata
    canvas2->Update();                                        // Forza l'aggiornamento della visualizzazione
    canvas2->SaveAs("histDifferenceFisher.root", "RECREATE"); // Salva come immagine PNG


    finalHisto->cd(); // Cambia la directory corrente al nuovo file ROOT
    // histDifference->Write(); // Scrive l'istogramma nel file ROOT
    finalHisto->Close(); // Chiudi il file ROOT
    output->Close();     // Chiudi il file di input ROOT

    output->Close();
}