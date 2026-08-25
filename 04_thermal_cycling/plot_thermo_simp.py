import pandas as pd
import matplotlib.pyplot as plt

logfile = "log_simp_npt_cycle.lammps"

rows = []
columns = None
reading = False

with open(logfile, "r") as f:
    for line in f:
        line = line.strip()

        if line.startswith("Step"):
            columns = line.split()
            reading = True
            continue

        if reading:
            if line == "" or line.startswith("Loop time") or line.startswith("ERROR"):
                reading = False
                continue

            parts = line.split()
            if columns is not None and len(parts) == len(columns):
                try:
                    rows.append([float(x) for x in parts])
                except ValueError:
                    pass

df = pd.DataFrame(rows, columns=columns)
df.to_csv("thermo_simp_npt_cycle.csv", index=False)

# 逐张图输出
plot_items = [
    ("Temp", "Temperature (K)", "fig_2_4_temp_vs_step.png"),
    ("PotEng", "Potential Energy (eV)", "fig_2_4_poteng_vs_step.png"),
    ("TotEng", "Total Energy (eV)", "fig_2_4_toteng_vs_step.png"),
    ("Press", "Pressure (bar)", "fig_2_4_press_vs_step.png"),
    ("Volume", "Volume (Å$^3$)", "fig_2_4_volume_vs_step.png"),
]

for col, ylabel, outfile in plot_items:
    if col in df.columns:
        plt.figure(figsize=(6,4))
        plt.plot(df["Step"], df[col], linewidth=1.2)
        plt.xlabel("Step")
        plt.ylabel(ylabel)
        plt.tight_layout()
        plt.savefig(outfile, dpi=300)
        plt.close()

# 体积-温度散点图
if "Temp" in df.columns and "Volume" in df.columns:
    plt.figure(figsize=(6,4))
    plt.scatter(df["Temp"], df["Volume"], s=8)
    plt.xlabel("Temperature (K)")
    plt.ylabel("Volume (Å$^3$)")
    plt.tight_layout()
    plt.savefig("fig_2_4_volume_vs_temperature.png", dpi=300)
    plt.close()

# 六联图
fig, axes = plt.subplots(3, 2, figsize=(10, 10))

items = [
    ("Temp", "Temperature (K)", "(a)"),
    ("PotEng", "Potential Energy (eV)", "(b)"),
    ("TotEng", "Total Energy (eV)", "(c)"),
    ("Volume", "Volume (Å$^3$)", "(d)"),
    ("Press", "Pressure (bar)", "(e)"),
]

for i, (col, ylabel, label) in enumerate(items):
    ax = axes.flat[i]
    ax.plot(df["Step"], df[col], linewidth=1.0)
    ax.set_xlabel("Step")
    ax.set_ylabel(ylabel)
    ax.text(0.02, 0.92, label, transform=ax.transAxes, fontsize=14)

# 第6张：体积-温度
ax = axes.flat[5]
ax.scatter(df["Temp"], df["Volume"], s=8)
ax.set_xlabel("Temperature (K)")
ax.set_ylabel("Volume (Å$^3$)")
ax.text(0.02, 0.92, "(f)", transform=ax.transAxes, fontsize=14)

plt.tight_layout()
plt.savefig("fig_2_4_thermo_combined.png", dpi=300)
plt.close()

print("热力学响应图已生成。")