# VASP DFT for molecular dipole descriptor of anions

1) Each anion was geometrically optimized on Pt(111) at pzc in JDFTx.

2) After converted to VASP structure file (POSCAR), the Pt atoms are stripped, leaving just the adsorb anion in the same unit cell.

3) Single-point DFT was performed with dipolar correction in the z-direction, which also gives the final z-dipole moment as descriptors.
