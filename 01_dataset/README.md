# Training Data and Configuration

This directory contains the labeled atomic configurations and training
configuration used to develop the Fe-Cr-C-Mn-Si-W deep potential model.

## Dataset

The `data_npy` directory contains the datasets in the standard DeepMD
NumPy format. The atomic configurations are divided into training and
validation datasets:

- `npt`: Configurations generated from NPT molecular dynamics.
- `nvt`: Configurations generated from NVT molecular dynamics.
- `defect`: Defective and distorted atomic configurations.

The dataset contains atomic coordinates, simulation cells, atomic types,
energies, atomic forces, and virials obtained from first-principles
calculations.

The element order used throughout the dataset is:

```text
Fe Cr C Mn Si W
