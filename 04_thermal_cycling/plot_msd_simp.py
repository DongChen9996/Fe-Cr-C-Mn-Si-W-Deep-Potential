import pandas as pd
import matplotlib.pyplot as plt

def read_msd(file):
    rows = []
    with open(file, "r") as f:
        for line in f:
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 5:
                try:
                    rows.append([float(x) for x in parts[:5]])
                except ValueError:
                    pass

    df = pd.DataFrame(rows, columns=["Step", "MSD_x", "MSD_y", "MSD_z", "MSD_total"])
    return df

# 读取
df1 = read_msd("msd_1850K_hold.dat")
df2 = read_msd("msd_final_300K_hold.dat")

# 单独图：1850 K
plt.figure(figsize=(6,4))
plt.plot(df1["Step"], df1["MSD_total"], linewidth=1.5)
plt.xlabel("Step")
plt.ylabel("MSD (Å$^2$)")
plt.tight_layout()
plt.savefig("fig_2_4_msd_1850K_hold.png", dpi=300)
plt.close()

# 单独图：最终300 K
plt.figure(figsize=(6,4))
plt.plot(df2["Step"], df2["MSD_total"], linewidth=1.5)
plt.xlabel("Step")
plt.ylabel("MSD (Å$^2$)")
plt.tight_layout()
plt.savefig("fig_2_4_msd_final_300K_hold.png", dpi=300)
plt.close()

# 对比图
plt.figure(figsize=(6,4))
plt.plot(df1["Step"], df1["MSD_total"], label="1850 K hold", linewidth=1.5)
plt.plot(df2["Step"], df2["MSD_total"], label="Final 300 K hold", linewidth=1.5)
plt.xlabel("Step")
plt.ylabel("MSD (Å$^2$)")
plt.legend()
plt.tight_layout()
plt.savefig("fig_2_4_msd_compare.png", dpi=300)
plt.close()

print("MSD图已生成。")