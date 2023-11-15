#include "TH1F.h"
#include "TF1.h"
#include "TCanvas.h"

#include "TMVA/Tools.h"
#include "TMVA/Reader.h"
#include "TMVA/PyMethodBase.h"
#include "TTree.h"
#include "TH1F.h"
#include "TF1.h"

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
    reader.BookMVA("Keras", "dataset/weights/TMVAClassification_PyKeras.weights.xml");

    // FILE CREATION
    // TFile output("AnalysisBDT.root", "RECREATE");  // Utilizzo diretto dell'oggetto output invece di un puntatore
    // TFile *file = new TFile("mySimulation.root");
    TFile *output = new TFile("AnalysisKeras.root", "RECREATE");

    // HISTOGRAMS CREATION
    // TH1F *histInvariantMassBDT = (TH1F*)output->Get("histInvariantMass");//, "Invariant Mass; m_{inv}(pK^{0}_{S})[GeV/#it{c}^{2}]; Entries", 60, 2.1, 2.43);
    // TH1F *hist_type = (TH1F *)file->Get("hist_type");
    TH1F *histInvariantMassKeras = new TH1F("histInvariantMass", "Invariant Mass; m_{inv}(pK^{0}_{S})[GeV/#it{c}^{2}]; Entries", 60, 2.1, 2.43);

    // FIT CREATION
    // TF1 *backgroundFit = new TF1("backgroundFit", "pol3", 2.1, 2.43);  // Utilizzo diretto dell'oggetto backgroundFit invece di un puntatore
    // TF1 *gausFit = new TF1("gausFit", "gaus", 2.1, 2.43);

    // backgroundFit->SetLineColor(kYellow);
    // backgroundFit->SetLineWidth(5);
    // gausFit->SetLineColor(kRed);
    // gausFit->SetLineWidth(4);

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
            if (reader.EvaluateMVA("Keras") >= 0.08)
            {
                histInvariantMassKeras->Fill(massLc2K0Sp);
            }
        }
    }

    std::cout << "Finished loop" << std::endl;

    // Effettuare il fit dell'istogramma con la funzione definita
    // histInvariantMassBDT->Fit("backgroundFit", "R", "", 2.1, 2.45);  // Utilizzo diretto dell'oggetto backgroundFit

    // CREAZIONE DELLA CANVAS
    // TCanvas canvas("canvas", "Fit Example", 800, 600);  // Utilizzo diretto dell'oggetto canvas invece di un puntatore

    // histInvariantMassBDT->Draw();
    // backgroundFit->Draw("same");

    // canvas.Write();
    output->Write();
    output->Close();
}

//////////////////////////////////////////////////////////////
void gausFit(){

}

void totalFit(){
    
}

void smartAnalysis()
{
    // FILE CREATION
    TFile *output = new TFile("AnalysisKeras.root");
    // HISTOGRAM CREATION
    TH1F *histInvariantMassKeras = (TH1F *)output->Get("histInvariantMass");
    TH1F *histDifference = (TH1F *)histInvariantMassKeras->Clone("histDifference");
    histDifference->SetTitle("Segnale massa invariante;Massa Invariante;Conteggio");

    // FITTING CREATION
    TF1 *backgroundFit = new TF1("backgroundFit", "pol3", 2.1, 2.43);
    backgroundFit->SetLineColor(kYellow);
    backgroundFit->SetLineWidth(5);
    TF1 *gausFit = new TF1("gausFit", "gaus");
    gausFit->SetLineColor(kRed);
    gausFit->SetLineWidth(5);
    TF1 *totalFit = new TF1("totalFit", "totalFit");
    ;

    // SAVING IN A ROOT FILE-----> NON SALVA L'ISTOGRAMMA FITTATO, PERCHÈ????
    TFile *finalHisto = new TFile("finalHisto.root", "RECREATE");
    // 1ST CANVAS
    TCanvas *canvas1 = new TCanvas("canvas1", "Results", 200, 10, 1400, 900);
    canvas1->SetGrid();

    // BACKGROUND FITTING
    histInvariantMassKeras->Fit("backgroundFit", "Q", "", 2.1, 2.43);
    histInvariantMassKeras->DrawCopy();

    // LOOP FOR CREATION OF HISTDIFFERENCE
    for (int i = 1; i <= histInvariantMassKeras->GetNbinsX(); ++i)
    {
        // Troviamo il centro del bin
        double binCenter = histInvariantMassKeras->GetBinCenter(i);
        // Valutiamo il fit in questo punto
        double fitValue = backgroundFit->Eval(binCenter);
        // Otteniamo il contenuto del bin originale
        double binContent = histInvariantMassKeras->GetBinContent(i);
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
    gausFit->SetParLimits(1, 2.26, 2.288);
    histDifference->Fit("gausFit", "Q", "", 2.1, 2.45);

    histDifference->GetXaxis()->SetTitle("m_{inv}(pK^{0}_{S})[GeV/#it{c}^{2}]");
    histDifference->GetXaxis()->SetTitleOffset(1.1);
    histDifference->GetYaxis()->SetTitleOffset(1.3);
    histDifference->DrawCopy("E1"); // Disegna l'istogramma con gli errori
    histDifference->Write();

    // Aggiornare la canvas per mostrare l'istogramma
    canvas2->Modified();                                     // Assicurati che la canvas sia aggiornata
    canvas2->Update();                                       // Forza l'aggiornamento della visualizzazione
    canvas2->SaveAs("histDifferenceKeras.root", "RECREATE"); // Salva come immagine PNG

    TF1 *fitResult = histDifference->GetFunction("gausFit");

    //CALCOLO DELLO YIELD
    // integrale della funzione di fit nell'intervallo di interesse
    double BinWidth = histDifference->GetBinWidth(1);
    double integral = fitResult->Integral(2.15, 2.4);

    // Stampi l'integrale a terminale
    std::cout << "Integrale del fit gaussiano nel range [2.1, 2.45]: " << integral/BinWidth << std::endl;

    finalHisto->cd(); // Cambia la directory corrente al nuovo file ROOT
    // histDifference->Write(); // Scrive l'istogramma nel file ROOT
    finalHisto->Close(); // Chiudi il file ROOT
    output->Close();     // Chiudi il file di input ROOT

    output->Close();
}



//TROVARE UN TAGLIO PER OTTENERE LA STESSA EFFICIENZA CON E ESENZA VARIABILE ASYMPT