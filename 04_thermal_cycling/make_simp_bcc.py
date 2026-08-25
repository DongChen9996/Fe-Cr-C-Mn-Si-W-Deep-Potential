import random
import numpy as np

random.seed(20260428)
np.random.seed(20260428)

a = 2.84
nx, ny, nz = 20, 20, 20

# type: 1 Fe, 2 Cr, 3 C, 4 Mn, 5 Si, 6 W
masses = {
    1: 55.845,
    2: 51.9961,
    3: 12.011,
    4: 54.938,
    5: 28.0855,
    6: 183.84,
}

n_cr = 1540
n_si = 317
n_mn = 194
n_w  = 73
n_c  = 148

atoms = []
atom_id = 1

# BCC lattice sites
for i in range(nx):
    for j in range(ny):
        for k in range(nz):
            atoms.append([atom_id, 1, i*a, j*a, k*a])
            atom_id += 1
            atoms.append([atom_id, 1, (i+0.5)*a, (j+0.5)*a, (k+0.5)*a])
            atom_id += 1

n_sites = len(atoms)
print("BCC lattice atoms:", n_sites)

indices = list(range(n_sites))
random.shuffle(indices)

cr_ids = indices[:n_cr]
si_ids = indices[n_cr:n_cr+n_si]
mn_ids = indices[n_cr+n_si:n_cr+n_si+n_mn]
w_ids  = indices[n_cr+n_si+n_mn:n_cr+n_si+n_mn+n_w]

for idx in cr_ids:
    atoms[idx][1] = 2
for idx in si_ids:
    atoms[idx][1] = 5
for idx in mn_ids:
    atoms[idx][1] = 4
for idx in w_ids:
    atoms[idx][1] = 6

# BCC octahedral interstitial candidate sites
oct_sites = []

for i in range(nx):
    for j in range(ny):
        for k in range(nz):
            x0, y0, z0 = i*a, j*a, k*a

            # octahedral-like positions in BCC cell
            candidates = [
                (x0 + 0.5*a, y0,         z0),
                (x0,         y0 + 0.5*a, z0),
                (x0,         y0,         z0 + 0.5*a),
                (x0 + 0.5*a, y0 + 0.5*a, z0),
                (x0 + 0.5*a, y0,         z0 + 0.5*a),
                (x0,         y0 + 0.5*a, z0 + 0.5*a),
            ]

            for c in candidates:
                x, y, z = c
                if 0 <= x < nx*a and 0 <= y < ny*a and 0 <= z < nz*a:
                    oct_sites.append(c)

random.shuffle(oct_sites)
c_sites = oct_sites[:n_c]

for x, y, z in c_sites:
    atoms.append([atom_id, 3, x, y, z])
    atom_id += 1

# composition check
mass_total = sum(masses[t] for _, t, _, _, _ in atoms)
counts = {}
for _, t, _, _, _ in atoms:
    counts[t] = counts.get(t, 0) + 1

print("Atom counts:", counts)
print("Total atoms:", len(atoms))

name_map = {
    1: "Fe",
    2: "Cr",
    3: "C",
    4: "Mn",
    5: "Si",
    6: "W",
}

for t in sorted(counts):
    wt = counts[t] * masses[t] / mass_total * 100
    print(f"{name_map[t]}: {counts[t]} atoms, {wt:.4f} wt%")

# write LAMMPS data
with open("simp_20x20x20.data", "w") as f:
    f.write("SIMP Fe-Cr-C-Mn-Si-W BCC 20x20x20 with C octahedral interstitials\n\n")
    f.write(f"{len(atoms)} atoms\n")
    f.write("6 atom types\n\n")

    f.write(f"0.0 {nx*a:.10f} xlo xhi\n")
    f.write(f"0.0 {ny*a:.10f} ylo yhi\n")
    f.write(f"0.0 {nz*a:.10f} zlo zhi\n\n")

    f.write("Masses\n\n")
    f.write("1 55.845   # Fe\n")
    f.write("2 51.9961  # Cr\n")
    f.write("3 12.011   # C\n")
    f.write("4 54.938   # Mn\n")
    f.write("5 28.0855  # Si\n")
    f.write("6 183.84   # W\n\n")

    f.write("Atoms # atomic\n\n")
    for atom in atoms:
        aid, atype, x, y, z = atom
        f.write(f"{aid} {atype} {x:.10f} {y:.10f} {z:.10f}\n")

print("Written: simp_20x20x20.data")