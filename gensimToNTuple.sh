#!/bin/bash

# Author: Colby Thompson
# Date: 01/02/2025
# Purpose: Executing this script will generate N di-gluino R-Hadron samples of a given mass point.
#          The script will then pass the file through the reconstruction chain, and ultimately through the current NTuplizer.
#          The script will also create CSVs of the R-Hadron energy deposits during simulation for the purpose of an event display

# CONTROL CENTER ----------------------

mass=$1 # In GeV
events=$2
jobNum=$3
cmEnergy=13000 # In GeV
seeded=False
eventdisplay=false # Set to true to create CSVs of the R-Hadron energy deposits during simulation for the purpose of an event display
ntuple=false # Set to true to run the NTuplizer over the RECO file

# -------------------------------------

# cd into correct directory
cd SpikedRHadronAnalyzer

# Create name string (called dir_name historically)
dir_name="M"$mass"_CM"$cmEnergy"_pythia8_jobNum"$jobNum
echo "All files will have the appendage $dir_name"
echo "generating $events events"

#if [ ! -d "data/$dir_name" ]; then
#    mkdir -p data/$dir_name
#    echo "creating data/${dir_name}"
#fi

if [ ! -d "data/" ]; then
    mkdir -p data/
    echo "creating directory data/"
fi

# gen-sim output files
genSimRoot=$dir_name"_gensimM"$mass"_"$events"Events.root"
genSimOut=$dir_name"_gensimM"$mass"_"$events"Events.out"

# digi-L1-digi2ray output files
digiRawRoot=$dir_name"_digirawM"$mass"_"$events"Events.root"
digiRawOut=$dir_name"_digirawM"$mass"_"$events"Events.out"

# reco output files
hltRoot=$dir_name"_hltM"$mass"_"$events"Events.root"
hltOut=$dir_name"_hltM"$mass"_"$events"Events.out"
recoRoot=$dir_name"_recoM"$mass"_"$events"Events.root"
recoOut=$dir_name"_recoM"$mass"_"$events"Events.out"

if [ ! -f data/$genSimRoot ]; then
    echo "Starting step 0: GEN-SIM"
    cmsRun EXO-RunIISummer20UL18GENSIM-00010_1_cfg_v3.py maxEvents=$events seeded=$seeded mass=$mass cmEnergy=$cmEnergy outputFile=data/$genSimRoot
    echo "Step 0 completed"
fi


if [ ! -f data/$digiRawRoot ]; then
    echo "Starting step 1: DIGI-L1-DIGI2RAW"
    cmsDriver.py --filein file:data/$genSimRoot \
        --fileout file:data/$digiRawRoot\
        --mc \
        --eventcontent RAWSIM \
        --datatier GEN-SIM-RAW \
        --conditions 106X_upgrade2018_realistic_v4 \
        --step DIGI,L1,DIGI2RAW \
        --python_filename data/step1_cfg.py \
        --geometry DB:Extended \
        --era Run2_2018 \
        -n -1 >& data/$digiRawOut
    echo "Step 1 completed"
fi

if [ ! -f data/$hltRoot ]; then
    echo "Starting step 2: RAW2DIGI-L1Reco-RECO"
    cmsDriver.py --filein file:data/$digiRawRoot \
        --fileout file:data/$hltRoot \
        --mc \
        --eventcontent RAWSIM \
        --datatier GEN-SIM-RAW \
        --conditions 106X_upgrade2018_realistic_v4 \
        --step HLT:GRun \
        --python_filename data/$stepHLT_cfg.py \
        --geometry DB:Extended \
        --era Run2_2018 \
        -n -1 >& data/$hltOut

    cmsDriver.py --filein file:data/$hltRoot \
        --fileout file:data/$recoRoot \
        --mc \
        --eventcontent FEVTDEBUGHLT \
        --datatier AODSIM \
        --conditions 106X_upgrade2018_realistic_v11_L1v1 \
        --step RAW2DIGI,L1Reco,RECO \
        --python_filename data/step2_cfg.py \
        --geometry DB:Extended \
        --era Run2_2018 \
        -n -1 >& data/$recoOut
    echo "Step 2 completed"
fi

if $eventdisplay; then

    if [ ! -f data/eventdisplay.csv ]; then
        echo "Now analyzing the data"
        echo "Creating CSV from EDMAnalyzer over GEN-SIM"
        cmsRun python/SpikedRHadronAnalyzer_cfg.py inputFiles=file:data/$genSimRoot outputFile=data/eventdisplay.csv
    fi

fi

cd ..

if $ntuple; then

    if [ ! -f Demo/SpikedRHadronAnalyzer/data/NTuple.root ]; then
    echo "Now running the NTuplizer over the RECO file"
    cmsRun HSCParticleProducerAnalyzer_2018_SignalMC_cfg.py inputFiles=file:Demo/SpikedRHadronAnalyzer/data/$recoRoot outputFile=Demo/SpikedRHadronAnalyzer/data/NTuple.root 
    fi  

fi
