# RHadronProduction

### The purpose of this repository is to generate di-Rhadron events with the "v3" bug fix. The first CMSSW release where this is available is  CMSSW_10_6_46. This repo uses CMSSW_10_6_47 (newest at time of writing). You will be able to generate, simulate, and reconstruct the simulated data with both a custom event display.

---

## Local Running and initial setup

To begin, navigate to your preferred directory inside of lxplus or cmslpc and run the following commands:

```
cmssw-el7
cmsrel CMSSW_10_6_47
cd CMSSW_10_6_47/src
```

Now clone the repository using your SSH key. Refer to [connecting-to-github-with-ssh-key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) if you have trouble.

```
git clone git@github.com:gracecummings/RHadronProduction.git --recursive
```

Now compile the code and navigate into the repository:

```
scram b -j 8
cd RHadronProduction
```

The file `gensimToNTuple.sh` conveniently does as suggested. It will generate and simulate however many di-gluino R-Hadron events that you would like and at whatever mass point. It can also continue through the reconstruction chain. It can also create a CSV designed for making event displays, more on that at the end. It previously was able to ntuplize, but this has been moved to a different repo.

The bash executable take the following arguments:

```
./gensimToNtuple.sh MASS NEVENTS JOBNUMB GENSEED G4SEED VTXSMEAR SEED
```

This was done to make the condor job submission easier. There are more parameters to edit, if you open the file.

- The CM energy of the beam
- And whether or not you would like your sample to be seeded
- Whether or not you would like a csv for eventdisplay purposes
- Whether or not you would like to pass the RECO file through the framework to make an NTuple

The seeding is turned on, because not setting the seed seemed to not randomize, but this worked. 

If run locally, all generated files will be saved under `SpikedRHadronAnalyzer/data`

---

## Condor submission

To submit jobs the cmslpc cluster via condor, DO NOT enter the sl7 containter. Stay on the el9 login node, and enter the `condor_batch` directory

```
cd CMSSW_10_6_47/src/RHadronProduction/condor_batch
```

The submission script takes the following arguments

- `-f` a .csv file with masses and desired number of events (example configs included in repo)
-  `-n` the max number events to process in a given job
- `-k` a boolean that kills the job submission, and instead prints the arguments to pass to the executable.

the `submitColbyProdToCondor.py` does the job chunking, makes the eos output directories, and generates the random-ish seeds used for thi quick and dirty generation. 


