from ase.io import read, write
from JDFTx_BT import JDFTx #Modified JDFTx-ASE interface
from ase.vibrations import Vibrations

#Read structure
atoms=read('Pt111_HCO3.poscar') #Read structure that was optimized in JDFTx, saved as poscar
vibatoms=[atom.index for atom in atoms if atom.symbol not in ['Pt']] #only vibrate adsorbate atoms

#Set-up JDFTx calculator
atoms.calc = JDFTx(ntask=8,
                    ncpu=8,
                commands={'initial-state' : '$VAR',
                          'coulomb-interaction' : 'Periodic',
                          'core-overlap-check' : 'none',
                          'elec-cutoff' : '20 100',
                          'spintype' : 'no-spin',
                          'symmetries' : 'automatic',
                          'elec-ex-corr' : 'gga-x-pbe gga-c-pbe',
                          'van-der-waals' : 'D3',
                          'kpoint' : '0.5 0.5 0.5 1',
                          'kpoint-folding' : '4 4 1',
                          'elec-smearing' : 'Fermi 0.00734',
                          'electronic-minimize' : 'nIterations 100 energyDiffThreshold 1E-7',
                          'fluid' : 'LinearPCM',
                          'pcm-variant' : 'CANDLE',
                          'fluid-solvent' : 'H2O',
                          'fluid-cation' : 'Na+ 1.',
                          'fluid-anion' : 'F- 1.',
                          'dump-name' : '$VAR',
                          'dump' : 'End Ecomponents Forces State'
                          })
#Set-up vibration run
vib = Vibrations(atoms,indices=vibatoms,delta=0.03)
vib.run()
#Write output and modes
vib.summary(method='standard')
vib.write_mode()

