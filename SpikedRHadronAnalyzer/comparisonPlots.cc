#include <TFile.h>
#include <TH1.h>
#include <TCanvas.h>
#include <TLegend.h>

// Run via: root -l -b -q 'comparisonPlots.cc'

void comparisonPlots() {
    // Open the ROOT files
    TFile *file1 = TFile::Open("data/Evap_NoMassChange_Gluino_M1800_13TeV_pythia8/Evap_NoMassChange_NTuple_1000Events.root");
    TFile *file2 = TFile::Open("data/v3_M1800_13TeV_pythia8/v3_NTuple_1000Events.root");

    if (!file1 || !file2) {
        std::cerr << "Error opening files!" << std::endl;
        return;
    }
    /////////////////////
    // First histogram //
    /////////////////////
    // Retrieve the histograms
    TH1F *hist1 = (TH1F*)file1->Get("HSCParticleAnalyzer/BaseName/CutFlow");
    TH1F *hist2 = (TH1F*)file2->Get("HSCParticleAnalyzer/BaseName/CutFlow");

    if (!hist1 || !hist2) {
        std::cerr << "Error retrieving histograms!" << std::endl;
        return;
    }

    // Create a canvas
    TCanvas *canvas = new TCanvas("canvas", "CutFlow", 800, 600);

    canvas->SetLogy();

    // Draw the histograms
    hist1->SetTitle("CutFlow");
    hist1->SetStats(0);
    hist2->SetStats(0);
    hist1->SetLineColor(TColor::GetColor("#00A88F"));
    hist1->Draw("HIST SAME");
    hist2->SetLineColor(TColor::GetColor("#BF2229"));
    hist2->Draw("HIST SAME");

    // Add a legend
    TLegend *legend = new TLegend(0.2, 0.73, 0.6, 0.88);
    legend->AddEntry(hist1, "v5-Evap", "l");
    legend->AddEntry(hist2, "v3", "l");
    legend->SetNColumns(2); // Set number of columns
    legend->SetTextSize(0.03); // Adjust text size
    legend->SetBorderSize(0); // Remove border
    legend->Draw();

    // Save the canvas as a PDF
    canvas->SetTitle("CutFlow");
    canvas->Print("comparison.pdf(");

    //////////////////////
    // Second histogram //
    //////////////////////

    TCanvas *canvas2 = new TCanvas("canvas2", "AnotherHistogram", 800, 600);

    TH1F *hist3 = (TH1F*)file1->Get("HSCParticleAnalyzer/BaseName/PostPreS_Mass");
    TH1F *hist4 = (TH1F*)file2->Get("HSCParticleAnalyzer/BaseName/PostPreS_Mass");

    // Draw the second set of histograms
    hist3->SetStats(0);
    hist4->SetStats(0);
    hist3->SetLineColor(TColor::GetColor("#00A88F"));
    hist3->GetYaxis()->SetRangeUser(0, 50);
    hist3->Draw("HIST SAME");
    hist4->SetLineColor(TColor::GetColor("#BF2229"));
    hist4->GetYaxis()->SetRangeUser(0, 50);
    hist4->Draw("HIST SAME");

    // Add a legend for the second comparison
    TLegend *legend2 = new TLegend(0.2, 0.73, 0.6, 0.88);
    legend2->AddEntry(hist3, Form("v5-Evap (Integral: %.0f)", hist3->Integral()), "l");
    legend2->AddEntry(hist4, Form("v3 (Integral: %.0f)", hist4->Integral()), "l");
    legend2->SetTextSize(0.03); // Adjust text size
    legend2->SetBorderSize(0); // Remove border
    legend2->Draw();

    // Save the second canvas to the PDF
    canvas2->Print("comparison.pdf)");

    //////////////
    // Clean up //
    //////////////
    delete canvas;
    file1->Close();
    file2->Close();
    delete file1;
    delete file2;
}