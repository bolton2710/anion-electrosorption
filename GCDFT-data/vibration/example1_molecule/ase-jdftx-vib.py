from ase.io import read, write
from JDFTx_BT import JDFTx #Modifed ASE-JDFTx interface (see JDFTx_BT.py)
from ase.vibrations import Vibrations

#Read structure
atoms=read('PH3.poscar') #read structure previously optimized in JDFTx, saved as POSCAR
vibatoms=[atom.index for atom in atoms] #vibrate all atoms

#Set-up JDFTx calculator
atoms.calc = JDFTx(ntask=1,
                    ncpu=16,
                commands={'initial-state' : '$VAR',
                          'coulomb-interaction' : 'Periodic',
                          'core-overlap-check' : 'none',
                          'elec-cutoff' : '20 100',
                          'spintype' : 'no-spin',
                          'symmetries' : 'automatic',
                          'elec-ex-corr' : 'gga-x-pbe gga-c-pbe',
                          'van-der-waals' : 'D3',
                          'kpoint' : '0. 0. 0. 1',
                          'kpoint-folding' : '1 1 1',
                          'elec-smearing' : 'Fermi 0.00734',
                          'electronic-minimize' : 'nIterations 100 energyDiffThreshold 1E-7',
                          'dump-name' : '$VAR',
                          'dump' : 'End Ecomponents Forces State'
                          })
#Set-up vibration run
vib = Vibrations(atoms,indices=vibatoms,delta=0.03)
vib.run()
#Write output and modes
vib.summary(method='standard')
vib.write_mode()

