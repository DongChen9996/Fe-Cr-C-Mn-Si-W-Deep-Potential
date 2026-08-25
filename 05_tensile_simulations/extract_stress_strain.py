import os
import glob
import pandas as pd

# =========================
# 参数设置
# =========================
input_pattern = "stress_strain_*.dat"
output_dir = "origin_stress_strain"
smooth_window = 5

os.makedirs(output_dir, exist_ok=True)

# =========================
# 读取单个 stress-strain 文件
# =========================
def read_stress_strain_file(file_path):
    rows = []

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            # 跳过标题行和注释行
            if line.startswith("#"):
                continue
            if line.startswith("strain"):
                continue

            parts = line.split()

            # 兼容两种格式：
            # 1) strain stress_z stress_x stress_y temp pe lx ly lz
            # 2) strain stress_z temp pe lx ly lz
            try:
                nums = [float(x) for x in parts]
            except ValueError:
                continue

            if len(nums) == 9:
                strain, stress_z, stress_x, stress_y, temp, pe, lx, ly, lz = nums
            elif len(nums) == 7:
                strain, stress_z, temp, pe, lx, ly, lz = nums
                stress_x = None
                stress_y = None
            else:
                continue

            rows.append({
                "strain": strain,
                "stress_z_GPa": stress_z,
                "stress_x_GPa": stress_x,
                "stress_y_GPa": stress_y,
                "temp_K": temp,
                "pe_eV_atom": pe,
                "lx": lx,
                "ly": ly,
                "lz": lz,
            })

    if not rows:
        return None

    df = pd.DataFrame(rows)

    # 按应变排序，避免输出顺序异常
    df = df.sort_values("strain").reset_index(drop=True)

    return df


# =========================
# 平滑处理
# =========================
def smooth_curve(df, window=5):
    df_s = df.copy()

    for col in ["stress_z_GPa", "stress_x_GPa", "stress_y_GPa", "temp_K", "pe_eV_atom"]:
        if col in df_s.columns:
            df_s[col] = df_s[col].rolling(window=window, center=True, min_periods=1).mean()

    return df_s


# =========================
# 主程序
# =========================
files = sorted(glob.glob(input_pattern))

if not files:
    print(f"没有找到文件：{input_pattern}")
    exit()

all_curves = []
summary_rows = []

for file_path in files:
    base = os.path.basename(file_path)
    name = base.replace("stress_strain_", "").replace(".dat", "")

    print(f"读取：{base}")

    df = read_stress_strain_file(file_path)

    if df is None or df.empty:
        print(f"  跳过：{base}，没有有效数据")
        continue

    df_smooth = smooth_curve(df, smooth_window)

    # 输出完整数据
    raw_csv = os.path.join(output_dir, f"{name}_raw.csv")
    smooth_csv = os.path.join(output_dir, f"{name}_smooth.csv")

    df.to_csv(raw_csv, index=False, encoding="utf-8-sig")
    df_smooth.to_csv(smooth_csv, index=False, encoding="utf-8-sig")

    # 输出 Origin 简化版：只要应变和拉伸应力
    origin_df = df[["strain", "stress_z_GPa"]].copy()
    origin_df.columns = ["Engineering strain", "Tensile stress (GPa)"]

    origin_smooth_df = df_smooth[["strain", "stress_z_GPa"]].copy()
    origin_smooth_df.columns = ["Engineering strain", "Tensile stress (GPa)"]

    origin_csv = os.path.join(output_dir, f"{name}_origin.csv")
    origin_smooth_csv = os.path.join(output_dir, f"{name}_origin_smooth.csv")

    origin_df.to_csv(origin_csv, index=False, encoding="utf-8-sig")
    origin_smooth_df.to_csv(origin_smooth_csv, index=False, encoding="utf-8-sig")

    # 汇总到一个大表，方便 Origin 一次导入
    temp_df = origin_smooth_df.copy()
    temp_df["sample"] = name
    all_curves.append(temp_df)

    # 计算峰值应力和峰值应变
    idx_max = df_smooth["stress_z_GPa"].idxmax()

    summary_rows.append({
        "sample": name,
        "max_stress_GPa": df_smooth.loc[idx_max, "stress_z_GPa"],
        "strain_at_max_stress": df_smooth.loc[idx_max, "strain"],
        "final_strain": df_smooth["strain"].iloc[-1],
        "final_stress_GPa": df_smooth["stress_z_GPa"].iloc[-1],
        "mean_temp_K": df_smooth["temp_K"].mean(),
    })

# 输出所有曲线长表
if all_curves:
    all_df = pd.concat(all_curves, ignore_index=True)
    all_df.to_csv(
        os.path.join(output_dir, "all_curves_for_origin.csv"),
        index=False,
        encoding="utf-8-sig"
    )

# 输出峰值汇总
summary_df = pd.DataFrame(summary_rows)
summary_df.to_csv(
    os.path.join(output_dir, "stress_strain_summary.csv"),
    index=False,
    encoding="utf-8-sig"
)

print("\n处理完成！")
print(f"输出文件夹：{output_dir}")
print("主要文件：")
print("  *_origin.csv：单条曲线，Origin可直接画图")
print("  *_origin_smooth.csv：平滑后的单条曲线")
print("  all_curves_for_origin.csv：所有曲线汇总")
print("  stress_strain_summary.csv：峰值应力、峰值应变汇总")