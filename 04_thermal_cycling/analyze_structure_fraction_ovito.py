from ovito.io import import_file
from ovito.modifiers import PolyhedralTemplateMatchingModifier
import numpy as np
import pandas as pd

traj = "dump_simp_npt_cycle.lammpstrj"

pipeline = import_file(traj)

ptm = PolyhedralTemplateMatchingModifier()
pipeline.modifiers.append(ptm)

rows = []

for frame in range(pipeline.source.num_frames):
    data = pipeline.compute(frame)
    stype = data.particles["Structure Type"]

    total = len(stype)

    row = {
        "frame": frame,
        "Other": int(np.sum(stype == 0)),
        "FCC": int(np.sum(stype == 1)),
        "HCP": int(np.sum(stype == 2)),
        "BCC": int(np.sum(stype == 3)),
        "ICO": int(np.sum(stype == 4)),
        "Total": total
    }

    for key in ["Other", "FCC", "HCP", "BCC", "ICO"]:
        row[key + "_frac"] = row[key] / total

    rows.append(row)

df = pd.DataFrame(rows)
df.to_csv("structure_fraction_ptm.csv", index=False)

print("结构比例数据已保存：structure_fraction_ptm.csv")