# Tensile Simulations at 300 K

This directory contains the LAMMPS input files, raw trajectories,
stress–strain data, processing script, and processed source data for tensile
simulations of the W1, W2, and W3 weld-metal compositions at 300 K.

## 1. Simulation systems

Three Fe–Cr–C–Mn–Si–W weld-metal compositions were investigated:

- `W1_joint`
- `W2_joint`
- `W3_joint`

The atomic type mapping used in all LAMMPS data and trajectory files is:

```text
1 Fe
2 Cr
3 C
4 Mn
5 Si
6 W
```

Atomic interactions were described using the compressed deep potential
provided in:

```text
../02_trained_potential/graph-compress.pb
```

## 2. Simulation conditions

The simulations were performed using LAMMPS with the following settings:

- Unit system: `metal`
- Atom style: `atomic`
- Boundary conditions: periodic in the x, y, and z directions
- Timestep: 0.001 ps
- Simulation temperature: 300 K
- Thermodynamic ensemble: NVT
- Thermostat damping parameter: 0.2 ps
- Initial-velocity random seed: 12345
- Tensile direction: z direction
- Engineering strain rate: 0.0015 ps⁻¹
- Tensile loading time: 200 ps
- Maximum engineering strain: approximately 0.30

The atomic structures were first minimized using the conjugate-gradient
method. Initial velocities were subsequently assigned at 300 K, followed by
NVT equilibration for 15,000 steps (15 ps). Uniaxial tensile deformation was
then applied along the z direction for 200,000 steps using the LAMMPS
`fix deform` command.

All atoms were thermostatted at 300 K during tensile loading. The simulations
used periodic boundary conditions and homogeneous deformation of the
simulation cell; fixed end regions were not used in these input files.

## 3. Stress and strain definitions

Engineering strain was calculated as:

```text
strain = (Lz - Lz,0) / Lz,0
```

where `Lz,0` is the simulation-cell length before tensile loading and `Lz` is
the instantaneous cell length.

The tensile stress was obtained from the LAMMPS pressure tensor:

```text
stress_z_GPa = -pzz / 10000
```

Because pressure is reported in bar when LAMMPS uses `metal` units, division
by 10,000 converts the stress to GPa. The x- and y-direction stresses were
calculated in the same way.

## 4. Directory contents

### LAMMPS input files

- `in.tensile_W1_joint_300K`: Tensile input file for W1 at 300 K.
- `in.tensile_W2_joint_300K`: Tensile input file for W2 at 300 K.
- `in.tensile_W3_joint_300K`: Tensile input file for W3 at 300 K.

The corresponding initial atomic-configuration files required by the
`read_data` commands are:

- `W1_joint.data`
- `W2_joint.data`
- `W3_joint.data`

### Direct stress–strain outputs

- `stress_strain_W1_joint_300K.dat`
- `stress_strain_W2_joint_300K.dat`
- `stress_strain_W3_joint_300K.dat`

Each file contains the following columns:

```text
strain
stress_z_GPa
stress_x_GPa
stress_y_GPa
temp_K
pe_eV_atom
lx
ly
lz
```

The stress–strain data were written every 500 molecular dynamics steps.

### Raw trajectories

- `dump_W1_joint_300K.zip`
- `dump_W2_joint_300K.zip`
- `dump_W3_joint_300K.zip`

The ZIP archives contain the LAMMPS trajectories generated during tensile
loading. The original trajectories contain atom IDs, atomic types, wrapped
coordinates, and unwrapped coordinates.

### Processing script

- `extract_stress_strain.py`: Reads the three direct LAMMPS stress–strain
  files, exports complete numerical data, generates Origin-compatible files,
  applies five-point moving-average smoothing, and summarizes the tensile
  curves.

### Processed data

The `origin_stress_strain` directory contains the processed numerical data:

- `W1_joint_300K_raw.csv`
- `W2_joint_300K_raw.csv`
- `W3_joint_300K_raw.csv`
- `W1_joint_300K_smooth.csv`
- `W2_joint_300K_smooth.csv`
- `W3_joint_300K_smooth.csv`
- `W1_joint_300K_origin.csv`
- `W2_joint_300K_origin.csv`
- `W3_joint_300K_origin.csv`
- `W1_joint_300K_origin_smooth.csv`
- `W2_joint_300K_origin_smooth.csv`
- `W3_joint_300K_origin_smooth.csv`
- `all_curves_for_origin.csv`
- `stress_strain_summary.csv`
- `300K.xls`

The `300K.xls` file is an additional working file used for comparison and
plotting in Origin. It was not generated directly by
`extract_stress_strain.py`.

## 5. Running the simulations

Run the three simulations from the `05_tensile_300K` directory using:

```bash
lmp -in in.tensile_W1_joint_300K
lmp -in in.tensile_W2_joint_300K
lmp -in in.tensile_W3_joint_300K
```

The potential should be called using the relative path:

```text
pair_style deepmd ../02_trained_potential/graph-compress.pb
pair_coeff * *
```

## 6. Processing the stress–strain data

Run the processing script from the `05_tensile_300K` directory:

```bash
python extract_stress_strain.py
```

The script searches for files matching:

```text
stress_strain_*.dat
```

and writes the processed results to:

```text
origin_stress_strain/
```

The script requires Python 3 and pandas.

## 7. Data-processing procedure

### Complete raw CSV files

The `*_raw.csv` files preserve the numerical values extracted from the direct
LAMMPS outputs, including engineering strain, axial and transverse stresses,
temperature, potential energy per atom, and simulation-cell dimensions.

### Smoothed CSV files

The `*_smooth.csv` files were generated using a centered moving-average filter
with a window of five data points. The filter was applied to:

- Axial tensile stress
- Transverse stresses
- Temperature
- Potential energy per atom

Engineering strain and the simulation-cell dimensions were not smoothed.

### Origin-compatible CSV files

The `*_origin.csv` files contain only engineering strain and tensile stress.
The `*_origin_smooth.csv` files contain the corresponding five-point
moving-average curves.

The `all_curves_for_origin.csv` file combines the smoothed W1, W2, and W3
curves in a single long-format table for direct import into Origin.

The `stress_strain_summary.csv` file reports:

- Maximum tensile stress
- Engineering strain at maximum tensile stress
- Final engineering strain
- Final tensile stress
- Mean simulation temperature

The maximum tensile stress and its corresponding strain were determined from
the five-point smoothed stress–strain curves.

## 8. Reproducibility

This directory provides the 300 K tensile input files, direct stress–strain
outputs, raw trajectories, data-processing script, and processed numerical
data for all three weld-metal compositions. Together with the trained deep
potential in `02_trained_potential`, these files enable reproduction and
verification of the 300 K tensile results.

The present directory is limited to the 300 K tensile simulations. Any tensile
results reported at other temperatures require their corresponding input files
and source data to be archived separately.
