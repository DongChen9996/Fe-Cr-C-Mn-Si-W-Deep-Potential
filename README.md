# Fe–Cr–C–Mn–Si–W Deep Potential for SIMP Steel Weld Metals

This repository provides the datasets, training configuration, trained deep
potential, validation results, molecular dynamics input files, analysis
scripts, and source data associated with the manuscript:

> **Development of a Fe–Cr–C–Mn–Si–W Deep Potential and Application for
> Thermal Cycling and Composition-Dependent Tensile Response of SIMP Steel
> Weld Metals**

**Manuscript number:** COMMAT-D-26-03547  
**Journal:** Computational Materials Science

## Authors

- Yinglong Zhang
- Chen Dong
- Hongpeng Zhang
- Xuan Fang
- Bo Wu
- Shichen Yan
- Cunfeng Yao
- Jiankang Huang

## 1. Repository overview

The Fe–Cr–C–Mn–Si–W deep potential was developed for atomistic simulations of
SIMP steel weld-metal compositions. The repository includes the labeled
training and validation datasets, final potential models, model-validation
outputs, an NPT thermal cycling simulation, and 300 K tensile simulations for
three weld-metal compositions.

The repository is organized as follows:

```text
Fe-Cr-C-Mn-Si-W-Deep-Potential/
├── 01_training_data/
├── 02_trained_potential/
├── 03_model_validation/
├── 04_thermal_cycling/
├── 05_tensile_300K/
├── LICENSE
└── README.md
```

| Directory | Description |
|---|---|
| `01_training_data` | DeepMD-format datasets and training configuration |
| `02_trained_potential` | Frozen and compressed deep-potential models |
| `03_model_validation` | Training convergence and energy, force, and virial validation results |
| `04_thermal_cycling` | NPT thermal-cycle inputs, structures, scripts, and processed data |
| `05_tensile_300K` | 300 K tensile inputs, trajectories, stress–strain data, and processing scripts |

Each directory contains a separate `README.md` with detailed file descriptions
and reproduction instructions.

## 2. Dataset

The labeled dataset contains 840 atomic configurations covering thermal,
structural, compositional, and defect-related local environments:

| Dataset category | Number of configurations |
|---|---:|
| NVT molecular dynamics | 421 |
| NPT molecular dynamics | 400 |
| Defective and distorted structures | 19 |
| **Total** | **840** |

The configurations include body-centered cubic, body-centered tetragonal, and
face-centered cubic structural environments. The compositional space covers:

| Element | Range (wt.%) |
|---|---:|
| Cr | 8.5–12.5 |
| C | 0–0.30 |
| Mn | 0–1.50 |
| Si | 0–2.50 |
| W | 0–2.50 |
| Fe | Balance |

The atomic type order used throughout the dataset and simulations is:

```text
Fe Cr C Mn Si W
```

The DeepMD-format datasets contain atomic coordinates, simulation cells,
atomic types, energies, atomic forces, and virials obtained from
first-principles calculations.

## 3. Deep-potential training

The main training settings are:

| Parameter | Value |
|---|---|
| Descriptor | `se_e2_a` |
| Cutoff radius | 6.0 Å |
| Smooth cutoff radius | 5.8 Å |
| Embedding network | 25–50–100 |
| Fitting network | 240–240–240 |
| Axis neurons | 16 |
| Initial learning rate | 1.0 × 10⁻³ |
| Final learning rate | 1.0 × 10⁻⁸ |
| Learning-rate decay steps | 5000 |
| Total training steps | 200,000 |

The primary training files are located in `01_training_data`:

- `input_v2_compat.json`: DeepMD-kit v2-compatible training input.
- `out.json`: Expanded training configuration with resolved default values.
- `data_npy/`: Training and validation datasets in DeepMD NumPy format.

Train the model from the dataset directory using:

```bash
cd 01_training_data
dp train input_v2_compat.json
```

## 4. Trained potential

The trained potential models are provided in `02_trained_potential`:

- `graph_200000.pb`: Frozen model after 200,000 training steps.
- `graph-compress.pb`: Compressed model used in LAMMPS simulations.

The compressed model is recommended for the thermal cycling and tensile
simulations.

## 5. Model validation

The model-validation files are provided in `03_model_validation`. The reported
validation errors are:

| Quantity | RMSE |
|---|---:|
| Energy | 2.86 × 10⁻³ eV/atom |
| Atomic force | 6.17 × 10⁻² eV/Å |
| Virial | 1.13 × 10⁻² eV/atom |

The validation directory contains the training-loss history and the reference
and predicted energy, force, and virial data for the NPT, NVT, and defective
configuration subsets.

## 6. NPT thermal cycling

The files in `04_thermal_cycling` reproduce the NPT thermal cycling simulation
of a 16,148-atom model. The thermal history consists of:

1. Equilibration at 300 K for 20 ps.
2. Heating from 300 K to 1850 K over 100 ps.
3. Holding at 1850 K for 50 ps.
4. Cooling from 1850 K to 300 K over 100 ps.
5. Final equilibration at 300 K for 20 ps.

The directory contains the LAMMPS input, representative structures, the
thermodynamic log, processed temperature/energy/pressure/volume data, radial
distribution functions, mean-square displacement data, and analysis scripts.

Run the simulation using:

```bash
cd 04_thermal_cycling
lmp -in in.simp_npt_cycle
```

The complete raw LAMMPS trajectory is archived separately in Zenodo:

[https://doi.org/10.5281/zenodo.22089925](https://doi.org/10.5281/zenodo.22089925)

## 7. Tensile simulations at 300 K

The files in `05_tensile_300K` contain the 300 K tensile simulations for the
W1, W2, and W3 weld-metal compositions.

The main loading parameters are:

| Parameter | Value |
|---|---:|
| Temperature | 300 K |
| Timestep | 0.001 ps |
| NVT equilibration | 15 ps |
| Tensile direction | z direction |
| Engineering strain rate | 0.0015 ps⁻¹ |
| Tensile loading time | 200 ps |
| Maximum engineering strain | Approximately 0.30 |

The simulations use periodic boundary conditions and homogeneous deformation
of the simulation cell through the LAMMPS `fix deform` command. The directory
contains the three LAMMPS input files, direct stress–strain outputs, compressed
trajectories, processed CSV files, and the `extract_stress_strain.py` analysis
script.

Run the three simulations using:

```bash
cd 05_tensile_300K
lmp -in in.tensile_W1_joint_300K
lmp -in in.tensile_W2_joint_300K
lmp -in in.tensile_W3_joint_300K
```

Process the stress–strain data using:

```bash
python extract_stress_strain.py
```

The present repository directory contains the 300 K tensile files. Source
files for tensile results at any other temperature must be archived separately
if those results are reported in the associated manuscript.

## 8. Software requirements

The simulations and analysis use:

- DeePMD-kit
- LAMMPS with DeePMD-kit support
- Python 3
- pandas
- NumPy
- Matplotlib
- OVITO with its Python interface for structural analysis
- Origin, optionally, for plotting the prepared CSV data

The calculations were performed on a workstation equipped with two NVIDIA RTX
4090D GPUs. The production calculations used two MPI ranks and two OpenMP
threads per task.

Exact software, compiler, CUDA, and library version numbers should be recorded
in a separate environment file when available.

## 9. Data and code availability

The training datasets, trained potential, validation outputs, simulation input
files, analysis scripts, and processed numerical data are available in this
public GitHub repository:

[https://github.com/DongChen9996/Fe-Cr-C-Mn-Si-W-Deep-Potential](https://github.com/DongChen9996/Fe-Cr-C-Mn-Si-W-Deep-Potential)

The complete raw trajectory for the NPT thermal cycling simulation is archived
at Zenodo:

[https://doi.org/10.5281/zenodo.22089925](https://doi.org/10.5281/zenodo.22089925)

## 10. Citation

If you use the datasets, potential model, input files, or scripts in this
repository, please cite the associated manuscript and the Zenodo dataset.

The journal citation will be added after publication.

## 11. License

The source code and scripts in this repository are distributed under the MIT
License provided in `LICENSE`. The raw thermal-cycling trajectory is distributed
under the license specified in the corresponding Zenodo record.

## 12. Contact

For questions about the potential model, datasets, or simulations, please
contact the corresponding author of the associated manuscript:

**Jiankang Huang**  
School of Materials Science and Engineering  
Lanzhou University of Technology
