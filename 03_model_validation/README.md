# Model Validation

This directory contains the training convergence and model validation
results of the Fe-Cr-C-Mn-Si-W deep potential.

## Training convergence

- `lcurve.out`: Training and validation loss as a function of training step.

## Dataset categories

The model was evaluated separately using the following configuration categories:

- `npt`: Configurations generated from NPT molecular dynamics.
- `nvt`: Configurations generated from NVT molecular dynamics.
- `defect`: Defective and distorted atomic configurations.

## Output files

- `*.e.out`: Reference and predicted total energies.
- `*.e_peratom.out`: Reference and predicted energies per atom.
- `*.f.out`: Reference and predicted atomic forces.
- `*.v.out`: Reference and predicted virials.
- `*.v_peratom.out`: Reference and predicted virials per atom.

Files containing `_test` correspond to the test datasets, whereas files
without `_test` correspond to the validation datasets.

## RMSE

The summary of the RMSE values is provided in `rmse_summary.csv`.

The datasets used for validation and testing are available in
`01_training_data/data_npy`.
