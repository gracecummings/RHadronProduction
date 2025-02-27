import sys
import os
import argparse
import subprocess
from datetime import date

parser = argparse.ArgumentParser()

if __name__=='__main__':
    parser.add_argument("-f","--samplecsv",type=str,help=".csv with hscp mass point and number of events")
    parser.add_argument("-k","--killsubmission",type=bool,default=False,help="removes jdl creation and job submission, meant for printing a command to pass for interactive running")
    args = parser.parse_args()

    #Check there is a text file to run over
    if (args.samplecsv is None):
        print("No list provided, please provide appropriate list")
        fsjson = {}
    else:
        if (not os.path.exists(args.sampleTextFile)):
            print("Invalid text")

    #Make log directories
    if not os.path.exists("condorMonitoringOutput/"+str(date.today())+"/"):
        os.makedirs("condorMonitoringOutput/"+str(date.today())+"/")

    #Tar the working area
    print("Creating tarball of working area")
    tarballName = "cmsswTar.tar.gz"
    if not os.path.exists(tarballName):
        os.system("tar -hcf "+tarballName+" ../../../../CMSSW_10_6_30")
    else:
        print('FOUND A TARBALL -- USING, BE CAREFULL!!!!!')

    #Where do you want to save it
    eosForOutput = "root://cmseos.fnal.gov//store/user/lpchscp/signalv3_prod_"+str(date.today())
    eosOnlypath  = eosForOutput.split("root://cmseos.fnal.gov/")[-1]
    eosFinalDir  = eosOnlypath.split("/")[-1]

    #check eos for premade directories
    if os.system("eos root://cmseos.fnal.gov/ ls /store/user/lpchscp/ | grep signalv3_prod_") == 0:#if there are eos directories
        eos_conflict_dirs = subprocess.check_output("eos root://cmseos.fnal.gov/ ls /store/user/lpchscp/ | grep signalv3_prod_",shell=True).decode(sys.stdout.encoding).split()
        if not any(eosFinalDir in path for path in eos_conflict_dirs): 
            print("Desired EOS output directory does not exist - creating it!")
            os.system("eos root://cmseos.fnal.gov mkdir {}".format(eosOnlypath))
        else:
            print("Desired EOS directory already exits.")
    else:
        print("Desired EOS output directory does not exist - creating it!")
        os.system("eos root://cmseos.fnal.gov mkdir {}".format(eosOnlypath))

    
    #Submit the jobs
    #Get list grouped by sample
    jobcnt = 0
    print("Root files are written to {0}".format(eosOnlypath))

    ##I would make args.sampleTextFile actually a textfile that is a list of the text files you want to make
    ##then, you read in the list, and make the .jdls in a for loop (everything below in the that loop)
    ###remember to replace then everywhere w/ args.sampleTextFile with the read in paht
    
    #get a name
    protoName = args.sampleTextFile.split("_13TeV")[0]
    sampleName = protoName.split("/")[-1]
    outFileName = sampleName+"_llpanalyzer.root"
    

            
    #Args to pass
    argu = "Arguments = {0} {1} {2}\n".format(eosForOutput,args.sampleTextFile,outFileName)
            
    if not args.killsubmission:
        #Make the jdl for each sample
        jdlName = "llpanalyzer_"+sampleName+"_"+str(date.today())+".jdl"
        jdl = open(jdlName,"w")
        jdl.write("universe = vanilla\n")
        jdl.write("Should_Transfer_Files = YES\n")
        jdl.write("WhenToTransferOutput = ON_EXIT\n")
        jdl.write("Transfer_Input_Files = "+tarballName+"\n")
        jdl.write("Output = condorMonitoringOutput/{0}/{1}_out.stdout\n".format(str(date.today()),sampleName))
        jdl.write("Error = condorMonitoringOutput/{0}/{1}_err.stder\n".format(str(date.today()),sampleName))
        jdl.write("Log = condorMonitoringOutput/{0}/{1}_log.log\n".format(str(date.today()),sampleName))
        jdl.write("Executable = gensimToNTuple.sh\n")
        jdl.write(argu)
        jdl.write('+DESIRED_Sites="T3_US_Baylor,T2_US_Caltech,T3_US_Colorado,T3_US_Cornell,T3_US_FIT,T3_US_FNALLPC,T3_US_Omaha,T3_US_JHU,T3_US_Kansas,T2_US_MIT,T3_US_NotreDame,T2_US_Nebraska,T3_US_NU,T3_US_OSU,T3_US_Princeton_ICSE,T2_US_Purdue,T3_US_Rice,T3_US_Rutgers,T3_US_MIT,T3_US_NERSC,T3_US_SDSC,T3_US_FIU,T3_US_FSU,T3_US_OSG,T3_US_TAMU,T3_US_TTU,T3_US_UCD,T3_US_UCSB,T2_US_UCSD,T3_US_UMD,T3_US_UMiss,T2_US_Vanderbilt,T2_US_Wisconsin"')
        jdl.write("\n")
        jdl.write('+ApptainerImage = "/cvmfs/singularity.opensciencegrid.org/cmssw/cms:rhel7"')
        jdl.write("\n")
        jdl.write("Queue 1\n")#Not sure about this one
        jdl.close()
        
        #submit the jobs
        os.system("condor_submit {0}".format(jdlName))
        
        jobcnt += 1

    else:
        print("Not submitting jobs, printing passed arguments")
        print(argu)
    print("Submitted {} jobs".format(jobcnt))
