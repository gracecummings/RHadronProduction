# RHadronProduction

### The purpose of this repository is to generate and analyze di-Rhadron events in CMSSW_10_6_30. You will be able to generate, simulate, reconstruct, and analyze the simulated data with both a custom event display and the current framework.

---

To begin, navigate to your preferred directory inside of lxplus or cmslpc and run the following commands:

```
cmssw-el7
cmsrel CMSSW_10_6_30
cd CMSSW_10_6_30/src
```

Now clone the repository using your SSH key. Refer to [connecting-to-github-with-ssh-key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) if you have trouble.

---

### _(Optional)_ 

_If you need to edit CMSSW files you can import them now. If, for example, you wanted to edit files in SimG4Core, you may run the following command:_

```
cp -r $CMSSW_RELEASE_BASE/src/SimG4Core SimG4Core/
```

### _(End of optional)_

---

Now compile the code and navigate into the repository:

```
scram b -j 8
cd RHadronProduction
```

The file `gensimToNTuple.sh` conveniently does as suggested. It will generate and simulate however many di-gluino R-Hadron events that you would like and at whatever mass point. It will also continue through the reconstruction chain and ultimately create an NTuple from the current framework. It will also create a CSV designed for making event displays, more on that at the end.

First, open `gensimToNTuple.sh` and edit the six parameters in the control center to your liking. These six parameters are:
- The mass of the gluino
- The number of events to generate
- The CM energy of the beam
- And whether or not you would like your sample to be seeded
- Whether or not you would like a csv for eventdisplay purposes
- Whether or not you would like to pass the RECO file through the framework to make an NTuple

Once finished, you may run:

```
./gensimToNTuple.sh
```

All files will be saved under `SpikedRHadronAnalyzer/data`

---

### _(Optional)_

_If you would like, you can run `RHadronAnalysis.py` over the created csv file to create 2D and 3D event displays. The parameters exist at the bottom of the python file._