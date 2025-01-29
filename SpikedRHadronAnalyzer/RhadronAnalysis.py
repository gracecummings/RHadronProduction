from matplotlib import pyplot as plt
from matplotlib import colors
import matplotlib.gridspec as gridspec
import math
import pandas as pd
import seaborn as sns
import numpy as np
from collections import Counter
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay


def xyEventDisplay(df, x_scalefactor, y_scalefactor, g_mass, events=None, savefig=False):
    #Plots the xy locations of the CaloHits for each event, with arrows representing the Rhadron momenta. Calohit energies are scaled
    #by their size and color.
    if events is None:
        maxrange = range(max(df['Event']))
    else:
        maxrange = events

    for i in maxrange:
        if events is None:
            j = i+1
        else:
            j = i
        event = df[df['Event'] == j]
        Rhad1_px = x_scalefactor * event['Rhad1_px [GeV]'].iloc[0]
        Rhad1_py = y_scalefactor * event['Rhad1_py [GeV]'].iloc[0]
        Rhad1_ET = (g_mass**2 + (Rhad1_px/x_scalefactor)**2 + (Rhad1_py/y_scalefactor)**2)**0.5
        Rhad2_px = x_scalefactor * event['Rhad2_px [GeV]'].iloc[0]
        Rhad2_py = y_scalefactor * event['Rhad2_py [GeV]'].iloc[0]
        Rhad2_ET = (g_mass**2 + (Rhad2_px/x_scalefactor)**2 + (Rhad2_py/y_scalefactor)**2)**0.5


        plt.clf()
        plt.scatter(event['Calohit X [cm]'], event['Calohit Y [cm]'], s=event['Calohit Energy [GeV]'], 
                    c=event['Calohit Energy [GeV]'], alpha=0.5, cmap='viridis', norm=colors.LogNorm(vmin=0.1, vmax=10000))
        plt.arrow(0,0,Rhad1_px,Rhad1_py, width=1, label=r'Rhadron 1; $E_T={} GeV$'.format(round(Rhad1_ET)), color='orange')
        plt.arrow(0,0,Rhad2_px,Rhad2_py, width=1, label=r'Rhadron 2; $E_T={} GeV$'.format(round(Rhad2_ET)), color='deepskyblue')
        plt.xlabel('X [cm]')
        plt.ylabel('Y [cm]')
        plt.suptitle('Event ' + str(j) + ': CaloHit Locations & Energies for g=1800GeV')
        plt.legend(loc='upper left')
        cbar = plt.colorbar()
        cbar.set_label('Energy [GeV]')
        if savefig:
            plt.savefig('xyEvent' + str(j) + '.png')
        else:
            plt.show()


def rzEventDisplay(df, g_mass, energyCut=0, savefig=False):
    #Plots the rz locations of the CaloHits in the entire dataset
    #reduced_df = df[(df['Calohit Energy [GeV]'] > energyCut) & (df['ECal Type'] == 'EB')]
    plt.clf()
    plt.scatter(df['Calohit Z [cm]'], df['Calohit R [cm]'], alpha=0.5)
    plt.xlabel('Z [cm]')
    plt.ylabel('R [cm]')
    if energyCut == 0:
        plt.suptitle('RZ CaloHit Locations for g=1800GeV')
    else:
        plt.suptitle('RZ CaloHit Locations with Energy > ' + str(energyCut) + ' GeV for g=1800GeV')

    if savefig:
        plt.savefig('rzEventDisplay.png')
    else:
        plt.show()


def hitLocations(df, energyCut=0):
    #Returns the number of hits in the EB, EE, and ES regions for hits with energy > energyCut.
    reduced_df = df[df['Calohit Energy [GeV]'] > energyCut]

    return len(reduced_df[reduced_df['ECal Type']=='EB']), len(reduced_df[reduced_df['ECal Type']=='EE']), len(reduced_df[reduced_df['ECal Type']=='ES'])


def nHitsInEvent(df, energyCut=0):
    #Returns the number of hits in each event with energy > energyCut.
    nHits = []
    for i in range(max(df['Event'])):
        event = df[df['Event'] == i+1]
        nHits.append(len(event[event['Calohit Energy [GeV]'] > energyCut]))
        if len(event[event['Calohit Energy [GeV]'] > energyCut]) == 4:
            print(i+1)
    return nHits


def nHitsAssociatedWithRHadron(df):
    #Returns the number of hits associated with the Rhadrons in the dataset.
    nHits = 0
    nHitsFromRHadron = 0
    for i in range(max(df['Event'])):
        event = df[df['Event'] == i+1]
        Rhad1_px = event['Rhad1_px [GeV]'].iloc[0]
        Rhad1_py = event['Rhad1_py [GeV]'].iloc[0]
        Rhad1_theta = math.atan2(Rhad1_py, Rhad1_px)
        Rhad2_px = event['Rhad2_px [GeV]'].iloc[0]
        Rhad2_py = event['Rhad2_py [GeV]'].iloc[0]
        Rhad2_theta = math.atan2(Rhad2_py, Rhad2_px)
       
        hits = event[(event['Calohit Energy [GeV]'] > 1000)]
        for index, row in hits.iterrows():
            hit_theta = math.atan2(row['Calohit Y [cm]'], row['Calohit X [cm]'])
            if abs(hit_theta - Rhad1_theta) < 0.1 or abs(hit_theta - Rhad2_theta) < 0.1:
                nHitsFromRHadron += 1
            nHits += 1
        
    return nHits, nHitsFromRHadron


def removeMuonHits(df):
    #Removes hits from the muon chamber in the dataset.
    return df[~df['Detector Type'].isin(['MuonRPC', 'MuonDT', 'MuonCSC'])]


def removeECALHits(df):
    #Removes hits from the ECAL in the dataset.
    return df[~df['Detector Type'].isin(['EB', 'EE', 'ES'])]


def analyzeVertices(df, energy=(1800.97,1800.99)):
    # Prepare data for plotting
    df = df[(df['Calo Hit Energy [GeV]'] >= energy[0]) & (df['Calo Hit Energy [GeV]'] <= energy[1])]
    interactionCounts = df.groupby(df['Parent'].abs())['Daughters'].value_counts()
    parents = []
    daughters = []
    for i, v in interactionCounts.items():
        parents.append(i[0])
        daughters.append(i[1])
    uniqueParents = Counter(parents).keys()
    uniqueDaughters = Counter(daughters).keys()

    confusion = [[] for _ in range(len(uniqueDaughters))]
    counter = 0
    for daughter in uniqueDaughters:
        for parent in uniqueParents:
            for i, v in interactionCounts.items():
                if i[0] == parent and i[1] == daughter:
                    confusion[counter].append(v)
        counter += 1
    confusion = np.array(confusion)
    print(confusion)

    # Plot the data
    fig, ax = plt.subplots(figsize=(10,10))
    sns.set(font_scale=1.4)  # for label size
    sns.heatmap(confusion, annot=True, annot_kws={"size": 8}, xticklabels=uniqueParents, yticklabels=uniqueDaughters, cmap='crest', linewidths=0.5, linecolor='black')
    ax.set_xlabel('Parent PDGID', fontsize=12)
    ax.set_ylabel('Daughter PDGIDs', fontsize=12)
    plt.suptitle("Frequency of Interactions for Calo Hit Energies in Range {}-{} GeV".format(energy[0], energy[1]))
    plt.xticks(rotation=45)
    plt.yticks(size=10)
    plt.show()


def plotRHadronEnergies(df):
    eb_df = df[df['Detector Type'] == 'EB']
    eb_rhad_df = eb_df[(eb_df['Particle Type'].abs() > 999999) & (eb_df['Particle Type'].abs() < 10000000)]
    energy_value_counts = eb_rhad_df['Calohit Energy [GeV]'].value_counts()
    fig = plt.figure(figsize=(12, 8))
    gs = gridspec.GridSpec(2, 3, height_ratios=[2, 1])

    ax1 = fig.add_subplot(gs[0, :])
    ax1.scatter(energy_value_counts.index, energy_value_counts.values, alpha=0.5, color='mediumseagreen', edgecolors='black')
    ax1.set_xticklabels([10e-5,10e-3,10e-1,10,180,10e3,1800])
    ax1.set_xscale('log')
    
    ax2, ax3, ax4 = fig.add_subplot(gs[1, 0], sharey=ax1), fig.add_subplot(gs[1, 1], sharey=ax1), fig.add_subplot(gs[1, 2], sharey=ax1)
    axes = [ax2, ax3, ax4]
    ranges = [(0,1),(175,185),(1795,1805)]
    i = 0
    for ax in axes:
        ax.scatter(energy_value_counts.index, energy_value_counts.values, alpha=0.5, color='mediumseagreen', edgecolors='black')
        if i < 1:
            ax.set_xscale('log')
        if i == 0:
            ax.annotate(0.00170333, (0.000140333, 56))
            ax.annotate(0.000510999, (0.0000410999, 12))
            ax.annotate(0.00510999, (0.00510999, 10))
        #if i == 1:
        #    ax.annotate(180.126, (180.126, 7))
        #if i == 2:
        #    ax.annotate(1800.98, (1800.98, 78))
        ax.set_xlim(ranges[i])
        i+=1
    plt.suptitle("R-Hadron Hits in the EB")
    fig.text(0.5, 0.04, 'Energy [GeV]', ha='center')
    fig.text(0.04, 0.5, 'Frequency', va='center', rotation='vertical')
    plt.show()


def plotNonRHadronEnergies(df):
    eb_df = df[df['Detector Type'] == 'EB']
    eb_df = eb_df[(eb_df['Particle Type'].abs() < 999999) | (eb_df['Particle Type'].abs() > 10000000)]
    energy_value_counts = eb_df['Calohit Energy [GeV]'].value_counts()
    print(energy_value_counts)
    plt.scatter(energy_value_counts.index, energy_value_counts.values, alpha=0.5, color='skyblue', edgecolors='black')
    plt.xscale('log')
    plt.xlim(0.0001, 10000)
    plt.xlabel('Energy [GeV]')
    plt.ylabel('Frequency')
    plt.suptitle("SM Particle Hits in the EB")
    plt.annotate(0.000510999, (0.000250999, 121300))
    plt.annotate(0.00170333, (0.000570333, 40000))
    plt.annotate(0.001022, (0.0005022, 4500))
    plt.annotate(0.00510999, (0.00210999, 3200))
    j = 0
    for i, v in energy_value_counts.items():
        print(i, v)
        j+=1
        if j == 10:
            break
    plt.show()


def particleCountsByEnergy(df, energy):
    eb_df = df[df['Detector Type'] == 'EB']
    eb_df = eb_df[(eb_df['Particle Type'].abs() > 999999) & (eb_df['Particle Type'].abs() < 10000000)]
    eb_energy_df = eb_df[eb_df['Calohit Energy [GeV]'] == energy]
    print(eb_energy_df['Particle Type'].abs().value_counts())


def massEnergyFrequencyChart(df, energy_range=(1800,1802)):
    pdgToMassConversion = { 
                            1000021 : 1800.0,     # ~g
                            1000993 : 1800.700,   # ~g_glueball
                            1009213 : 1800.650,   # ~g_rho+
                            1009313 : 1800.825,   # ~g_K*0
                            1009323 : 1800.825,   # ~g_K*+
                            1009113 : 1800.650,   # ~g_rho0
                            1009223 : 1800.650,   # ~g_omega
                            1009333 : 1801.800,   # ~g_phi
                            1091114 : 1800.975,   # ~g_Delta-
                            1092114 : 1800.975,   # ~g_Delta0
                            1092214 : 1800.975,   # ~g_Delta+
                            1092224 : 1800.975,   # ~g_Delta++
                            1093114 : 1801.150,   # ~g_Sigma*-
                            1093214 : 1801.150,   # ~g_Sigma*0
                            1093224 : 1801.150,   # ~g_Sigma*+
                            1093314 : 1801.300,   # ~g_Xi*-
                            1093324 : 1801.300,   # ~g_Xi*0
                            1093334 : 1801.600    # ~g_Omega-
                        }
    correlation = {
                1800.0 : [],
                1800.700 : [],
                1800.825 : [],
                1800.650 : [],
                1801.800 : [],
                1800.975 : [],
                1801.150 : [],
                1801.300 : [],
                1801.600 : []
            }
    
    eb_df = df[df['Detector Type'] == 'EB']
    eb_df = eb_df[(eb_df['Calohit Energy [GeV]'] >= energy_range[0]) & (eb_df['Calohit Energy [GeV]'] <= energy_range[1])]
    uniqueParticleEnergyDeposits = eb_df.groupby(eb_df['Particle Type'].abs())['Calohit Energy [GeV]'].value_counts()
    for i, v in uniqueParticleEnergyDeposits.items():
        for j in range(v):
            correlation[pdgToMassConversion[i[0]]].append(i[1])

    # Prepare the data for plotting
    masses = []
    energies = []
    for key, value in correlation.items():
        masses.append(key)
        for i in value:
            energies.append(i)
    masses = sorted(masses)
    energies = sorted(Counter(energies).keys(), reverse=True)
    confusion = [[] for _ in range(len(energies))]
    for i in range(len(energies)):
        for mass in masses:
            confusion[i].append(correlation[mass].count(energies[i]))
    confusion = np.array(confusion)

    # Plot the data
    fig, ax = plt.subplots(figsize=(12,12))
    sns.set(font_scale=1.4)  # for label size
    sns.heatmap(confusion, annot=True, annot_kws={"size": 8}, xticklabels=masses, yticklabels=energies,
                 cmap='crest', linewidths=0.5, linecolor='black', mask=(confusion==0))
    ax.set_xlabel('Particle Mass [GeV]', fontsize=14)
    ax.set_ylabel('EB Energy Deposit [GeV]', fontsize=14)
    plt.title("Frequency of Energy Deposits in the EB by Particle Mass (1800-1802 GeV)", size=16)
    plt.xticks(rotation=45)
    plt.yticks(size=8)
    yticks = ax.get_yticks()
    print(yticks)
    yticks[0].set_color('blue')
    yticks[5].set_color('blue')
    yticks[14].set_color('blue')
    yticks[19].set_color('blue')
    yticks[38].set_color('blue')
    yticks[49].set_color('blue')
    plt.savefig('massEnergyFrequencyChart.png')
    plt.show()


def lowEnergyRHadHistogram(df):
    df = df[df['Calohit Energy [GeV]'] <= 1]
    df = df[df['Particle Type'].abs() > 999999]
    df = df[(df['Particle Type'].abs() > 999999) & (df['Particle Type'].abs() < 10000000)]
    plt.hist(df['Calohit Energy [GeV]'], bins=200, color='mediumseagreen', edgecolor='black')
    plt.xlabel('Energy [GeV]')
    plt.ylabel('Frequency')
    plt.title('R-Hadron Hits with Energy <= 1 GeV in EB')
    plt.yscale('log')
    plt.show()



file = 'Gluino1800GeV_Hits.csv'
df = pd.read_csv(file)
#x_scalefactor, y_scalefactor = 125 / max(max(df['Rhad1_px [GeV]']), max(df['Rhad2_px [GeV]'])), 125 / max(max(df['Rhad1_py [GeV]']), max(df['Rhad2_py [GeV]']))
#g_mass = 1800

#df = removeMuonHits(df)
#df = removeECALHits(df)
#nHits, nHitsFromRHadron = nHitsAssociatedWithRHadron(df)
#print(nHits, nHitsFromRHadron)
#analyzeVertices(df, energy=(1800.97,1800.99))
#plotRHadronEnergies(df)
#plotNonRHadronEnergies(df)
#particleCountsByEnergy(df, 0.00510999)
#massEnergyFrequencyChart(df, energy_range=(1800,1802))
lowEnergyRHadHistogram(df)

#xyEventDisplay(muonless_df, x_scalefactor, y_scalefactor, g_mass, events=None, savefig=False)
#rzEventDisplay(removeMuonHits(df), g_mass, energyCut=0, savefig=False)