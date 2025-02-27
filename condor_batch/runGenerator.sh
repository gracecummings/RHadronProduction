#!/bin/bash

export X509_CERT_DIR=/cvmfs/grid.cern.ch/etc/grid-security/certificates/

#Print stuff about the job
echo "Starting job on " `date` #Date/time of start of job
#echo "Running on: `uname -a`" #Condor job is running on this node
echo "System software: `cat /etc/redhat-release`" #Operating System on that node

#untar your crap
source /cvmfs/cms.cern.ch/cmsset_default.sh
echo "Untaring  directory with analyzer code"
tar -xf cmsswTar.tar.gz
cd CMSSW_10_6_30/src/RHadronProduction
scram b ProjectRename
cmsenv

#Arguments taken
#1 - R-hadron mass
#2 - number of events for this specific production
#3 - eos directory
#4job number

#Running the selection maker
echo "Beginning the production"
echo "Generating R-hadron mass:"
echo $1
echo "Generating this many events:"
echo $2
echo "(Desired) output directory:"
echo $3
echo "Job number:"
echo $4

./gensimToNTuple.sh $1 $2 $4

for FILE in SpikedRHadronAnalyzer/data/M*reco*.root
do
    echo "Full path: ${FILE}"
    echo "copying ${FILE##*\/} to eos $3"
    xrdcp ${FILE} $3/${FILE##*\/}
    #XRDEXIT=$?
    #if [[ $XRDEXIT -ne 0 ]]; then
	#rm ${FILE}
	#echo "failure in xrdcp, exit code $XRDEXIT"
	#exit $XRDEXIT
    #fi
    #rm ${FILE}
done


