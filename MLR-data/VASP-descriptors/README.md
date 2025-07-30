# VASP DFT for molecular dipole descriptor of anions

- Each anion was geometrically optimized on Pt(111) at pzc in JDFTx.

- After converted to VASP structure file (POSCAR), the Pt atoms are stripped, leaving just the adsorb anion in the same unit cell.

- Single-point DFT was performed with dipolar correction in the z-direction, which also gives the final z-dipole moment as descriptors.
