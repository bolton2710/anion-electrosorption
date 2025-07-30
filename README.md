# Public repository for: *Predicting Competitive Anion Electrosorption on Late Transition Metals*
[![DOI](https://zenodo.org/badge/1028567744.svg)](https://doi.org/10.5281/zenodo.16619520)
[![rxiv](https://img.shields.io/badge/ChemRxiv-blue.svg)](https://doi.org/10.26434/chemrxiv-2025-pvlzg-v2)
[![MIT License](https://img.shields.io/badge/License_code-MIT-green.svg)](./LICENSE-CODE)
[![CC BY 4.0](https://img.shields.io/badge/License_data-CC_BY_4.0-blue.svg)](./LICENSE-DATA)

This repository contains input and output files for grand-canonical density function theory (**GC-DFT**)
calculations, and multiple linear regression (**MLR**) descriptors as presented in our paper: 
*Predicting Competitive Anion Electrosorption on Late Transition Metals*

Current manuscript status: *Pending peer-reviewed*

## Repository structure

The repository is organized into `GCDFT-data` and `MLR-data`.

`GCDFT-data` contains:
- `optimization`: optimized geometries and DFT calculation input for all surfaces and molecules.
- `vibration`: modified ASE-JDFTx interface for perform vibration calculations.

`MLR-data` contains:
- `NWChem-descriptors`: input and output of DFT calculations performed in NWChem for extracting anion features.
- `VASP-descriptors`: input and output of DFT calculations performed in VASP for extracting dipole feature.

## License  
- **Code/Software**: Licensed under [MIT](./LICENSE-CODE).
- **Data/Results**: Licensed under [CC BY 4.0](./LICENSE-DATA), requiring attribution to the original paper.