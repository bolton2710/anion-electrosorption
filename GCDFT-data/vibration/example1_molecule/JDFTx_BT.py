#!usr/bin/env python

# Atomistic Simulation Environment (ASE) calculator interface for JDFTx
# See http://jdftx.org for JDFTx and https://wiki.fysik.dtu.dk/ase/ for ASE
# Authors: Deniz Gunceler, Ravishankar Sundararaman

#Edited by Bolton Tran, Oct 2023
#Simplified and tailored for setting-up NEB calculations with ASE with emphasis on user's control over JDFTx inputs
#i.e., less hand-holding, more customization
#Edits:
#1. Add checking and adding atom constraints
#2. Remove command checking with self.acceptableCommand, user should manually add to "commands" correctly
#3  Add init-state and dump-name manually too
#4. Remove separate self.kpoints and self.dump. User should manually add to "commands"
#5. User can specify directory to output run files (useful for NEB), default is run at current directory
#6. Remove auto coulomb-trunc option, user to add manually through "commands"
#7. Remove ignoreStress, just don't bother determining stress from ASE set-up
#8. Remove incomplete help function
#9. Allow user to specify -n and -c in srun for each NEB image

import os, scipy, subprocess
from ase.calculators.calculator import Calculator
from ase.units import Bohr, Hartree

#Run shell command and return output as a string:
def shell(cmd):
    return subprocess.check_output(cmd, shell=True)

#Return var, replacing it with environment variable varName if it is None
def replaceVariable(var, varName):
    if (var is None) and (varName in os.environ):
        return os.environ[varName]
    else:
        return var

class JDFTx(Calculator):

    def __init__(self, executable=None, pseudoDir=None, pseudoSet='GBRV', commands=None, runDir=None, ntask=None, ncpu=None):
        #Valid pseudopotential sets (mapping to path and suffix):
        pseudoSetMap = {
            'SG15' : 'SG15/$ID_ONCV_PBE.upf',
            'GBRV' : 'GBRV/$ID_pbe.uspp',
            'GBRV-pbe' : 'GBRV/$ID_pbe.uspp',
            'GBRV-lda' : 'GBRV/$ID_lda.uspp',
            'GBRV-pbesol' : 'GBRV/$ID_pbesol.uspp'
        }
        if pseudoSet in pseudoSetMap:
            self.pseudoSetCmd = 'ion-species ' + pseudoSetMap[pseudoSet]
        else:
            self.pseudoSetCmd = ''
            
        #Get default values from environment:
        self.executable = replaceVariable(executable, 'JDFTx')      #Path to the jdftx executable (cpu or gpu)
        self.pseudoDir = replaceVariable(pseudoDir, 'JDFTx_pseudo') #Path to the pseudopotentials folder
        if (self.executable is None):
            raise Exception('Specify path to jdftx in argument \'executable\' or in environment variable \'JDFTx\'.')
        if (self.pseudoDir is None) and (not (pseudoSet in pseudoSetMap)):
            raise Exception('Specify pseudopotential path in argument \'pseudoDir\' or in environment variable \'JDFTx_pseudo\', or specify a valid \'pseudoSet\'.')
		
        #Initialize input
        self.input = []
        
        # Parse commands, which can be a dict or a list of 2-tuples.
        if isinstance(commands, dict):
            commands = commands.items()
        elif commands is None:
            commands = []
        for cmd, v in commands:
            self.addCommand(cmd, v)

        # Accepted pseudopotential formats
        self.pseudopotentials = ['fhi', 'uspp', 'upf']

        # Current results
        self.E = None
        self.Forces = None

        # History
        self.lastAtoms = None
        self.lastInput = None

        #BT--if not specified, run right here; used in runDFTx function
        if runDir is None:
            self.runDir = '.'
        else:
            self.runDir = runDir
            if not os.path.isdir(self.runDir): #if folder not already exists
                shell('mkdir %s'% self.runDir) #if specified, mkdir

        #BT--Need -n and -c for srun execution
        if ntask is None or ncpu is None:
            raise Exception('Specify ntask and ncpu for executing jdftx')
        else:
            self.ntask=ntask
            self.ncpu=ncpu
            
    ########### Interface Functions ###########
    
    def addCommand(self, cmd, v):
        self.input.append((cmd, v))
        
    def calculation_required(self, atoms, quantities):
        if((self.E is None) or (self.Forces is None)):
            return True
        if((self.lastAtoms != atoms) or (self.input != self.lastInput)):
            return True
        return False
    
    def get_forces(self, atoms):
        if(self.calculation_required(atoms, None)):
            self.update(atoms)
        return self.Forces

    def get_potential_energy(self, atoms, force_consistent=False):
        if(self.calculation_required(atoms, None)):
            self.update(atoms)
        return self.E

    ################### I/O ###################

    #BT--This is reading off of "Ecomponents" output
    def __readEnergy(self, filename):
        Efinal = None
        for line in open(filename):
            tokens = line.split()
            if len(tokens)==3:
                Efinal = float(tokens[2])
        if Efinal is None:
            raise IOError('Error: Energy not found.')
        return Efinal * Hartree #Return energy from final line (Etot, F or G)
    
    #BT--This is reading off of "force" output
    def __readForces(self, filename):
        idxMap = {}
        symbolList = self.lastAtoms.get_chemical_symbols()
        for i, symbol in enumerate(symbolList):
            if symbol not in idxMap:
                idxMap[symbol] = []
            idxMap[symbol].append(i)
        forces = [0]*len(symbolList)
        for line in open(filename):
            if line.startswith('force '):
                tokens = line.split()
                idx = idxMap[tokens[1]].pop(0) # tokens[1] is chemical symbol
                forces[idx] = [float(word) for word in tokens[2:5]] # tokens[2:5]: force components

        if(len(forces) == 0):
            raise IOError('Error: Forces not found.')
        return (Hartree / Bohr) * scipy.array(forces)

    ############## Running JDFTx ##############

    def update(self, atoms):
        self.runJDFTx(self.constructInput(atoms))

    def runJDFTx(self, inputfile):
        """ Runs a JDFTx calculation """
        #Write input file:
        fp = open(self.runDir+'/in', 'w')
        fp.write(inputfile)
        fp.close()
        #Run jdftx:::
        shell('cd %s && mpirun -n %s %s -c %s -i in -o out' % (self.runDir, self.ntask, self.executable, self.ncpu))
        self.E = self.__readEnergy('%s/Ecomponents' % (self.runDir))
        self.Forces = self.__readForces('%s/force' % (self.runDir))

    def constructInput(self, atoms):
        """ Constructs a JDFTx input string using the input atoms and the input file arguments (kwargs) in self.input """
        inputfile = ''

        # Add lattice info
        R = atoms.get_cell() / Bohr
        inputfile += 'lattice \\\n'
        for i in range(3):
            for j in range(3):
                inputfile += '%f  ' % (R[j, i])
            if(i != 2):
                inputfile += '\\'
            inputfile += '\n'

        # Add ion info
        atomPos = [x / Bohr for x in list(atoms.get_positions())]  # Also convert to bohr
        atomNames = atoms.get_chemical_symbols()   # Get element names in a list
        inputfile += '\ncoords-type cartesian\n'
        #BT--check for constraints
        if atoms.constraints!=[] :cons=atoms.constraints[0].get_indices()
        else : cons=[]
        
        for i in range(len(atomPos)):
            if i in cons: atomFix=0
            else: atomFix=1
            inputfile += 'ion %s %f %f %f %i \n' % (atomNames[i], atomPos[i][0], atomPos[i][1], atomPos[i][2], atomFix)
        del i

        #Add pseudopotentials
        inputfile += '\n'
        if not (self.pseudoDir is None):
            added = []  # List of pseudopotential that have already been added
            for atom in atomNames:
                if(sum([x == atom for x in added]) == 0.):  # Add ion-species command if not already added
                    for filetype in self.pseudopotentials:
                        try:
                            shell('ls %s | grep %s.%s' % (self.pseudoDir, atom, filetype))
                            inputfile += 'ion-species %s/%s.%s\n' % (self.pseudoDir, atom, filetype)
                            added.append(atom)
                            break
                        except:
                            pass
        inputfile += self.pseudoSetCmd + '\n' #Pseudopotential sets
        
        # Construct most of the input file
        inputfile += '\n'
        for cmd, v in self.input:
            inputfile += '%s %s\n' % (cmd, str(v))

        # Cache this calculation to history
        self.lastAtoms = atoms.copy()
        self.lastInput = list(self.input)
        return inputfile
