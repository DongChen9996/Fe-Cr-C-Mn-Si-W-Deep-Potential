import re
import argparse
from pathlib import Path

import pandas as pd


def parse_lammps_log(log_file: str) -> pd.DataFrame:
    """
    从 LAMMPS log 文件中提取 thermo_style custom 输出的数据。
    适用于类似：
    thermo_style custom step temp pe ke etotal press vol lx ly lz
    """

    log_file = Path(log_file)
    if not log_file.exists():
        raise FileNotFoundError(f"找不到文件: {log_file}")

    records = []
    columns = None
    reading = False

    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line_strip = line.strip()

            if not line_strip:
                continue

            # 识别 thermo 表头
            if re.match(r"^Step\s+", line_strip):
                columns = line_strip.split()
                reading = True
                continue

            # 结束当前 thermo block
            if reading and (
                line_strip.startswith("Loop time")
                or line_strip.startswith("WARNING")
                or line_strip.startswith("ERROR")
                or line_strip.startswith("Memory usage")
            ):
                reading = False
                continue

            # 读取 thermo 数字行
            if reading and columns is not None:
                parts = line_strip.split()

                if len(parts) != len(columns):
                    continue

                try:
                    values = [float(x) for x in parts]
                except ValueError:
                    continue

                records.append(values)

    if not records:
        raise ValueError(
            "没有在 log 文件中识别到 thermo 数据。请确认 log 中包含类似：\n"
            "Step Temp PotEng KinEng TotEng Press Volume Lx Ly Lz\n"
            "或 thermo_style custom step temp pe ke etotal press vol lx ly lz"
        )

    df = pd.DataFrame(records, columns=columns)

    # 统一列名为小写，便于后续处理
    df.columns = [c.lower() for c in df.columns]

    # 去除重复 step，多个 run 拼接时可能出现重复
    if "step" in df.columns:
        df = df.drop_duplicates(subset=["step"], keep="last")
        df = df.sort_values("step").reset_index(drop=True)

    return df


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    兼容 LAMMPS 不同 thermo_style 输出列名。
    将 PotEng 等列统一为 pe，Volume 统一为 vol。
    """

    rename_map = {
        "poteng": "pe",
        "kineng": "ke",
        "toteng": "etotal",
        "volume": "vol",
        "press": "press",
        "temp": "temp",
        "lx": "lx",
        "ly": "ly",
        "lz": "lz",
        "step": "step",
    }

    df = df.rename(columns={c: rename_map.get(c, c) for c in df.columns})
    return df


def add_time_and_stage(
    df: pd.DataFrame,
    timestep_ps: float = 0.001,
    t_eq1: float = 50.0,
    t_heat: float = 300.0,
    t_hold_high: float = 100.0,
    t_cool: float = 300.0,
    t_eq2: float = 50.0,
) -> pd.DataFrame:
    """
    添加模拟时间和热循环阶段。
    metal 单位下 timestep = 0.001 表示 0.001 ps。
    """

    if "step" not in df.columns:
        raise ValueError("数据中没有 step 列，无法计算模拟时间。")

    step0 = df["step"].min()
    df["time_ps"] = (df["step"] - step0) * timestep_ps

    t1 = t_eq1
    t2 = t1 + t_heat
    t3 = t2 + t_hold_high
    t4 = t3 + t_cool
    t5 = t4 + t_eq2

    def classify_stage(t):
        if t < t1:
            return "300K_equilibration"
        elif t < t2:
            return "heating_300_to_1850K"
        elif t < t3:
            return "1850K_holding"
        elif t < t4:
            return "cooling_1850_to_300K"
        elif t <= t5:
            return "final_300K_holding"
        else:
            return "after_cycle"

    df["stage"] = df["time_ps"].apply(classify_stage)

    return df


def add_per_atom_values(df: pd.DataFrame, natoms: int = None) -> pd.DataFrame:
    """
    如果给出原子数，则计算每原子能量和每原子体积。
    """

    if natoms is None:
        return df

    if "pe" in df.columns:
        df["pe_per_atom"] = df["pe"] / natoms

    if "etotal" in df.columns:
        df["etotal_per_atom"] = df["etotal"] / natoms

    if "vol" in df.columns:
        df["vol_per_atom"] = df["vol"] / natoms

    return df


def save_outputs(df: pd.DataFrame, output_dir: str):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 全部数据
    df.to_csv(output_dir / "thermo_all.csv", index=False)

    # 各阶段平均值和标准差
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    stage_mean = df.groupby("stage")[numeric_cols].mean()
    stage_std = df.groupby("stage")[numeric_cols].std()

    stage_summary = pd.concat(
        {"mean": stage_mean, "std": stage_std},
        axis=1
    )

    stage_summary.to_csv(output_dir / "thermo_stage_average.csv")

    # 体积-温度数据
    vt_cols = [c for c in ["time_ps", "stage", "temp", "vol", "vol_per_atom"] if c in df.columns]
    if "temp" in df.columns and "vol" in df.columns:
        df[vt_cols].to_csv(output_dir / "volume_temperature.csv", index=False)

    # 盒子尺寸
    box_cols = [c for c in ["time_ps", "stage", "lx", "ly", "lz"] if c in df.columns]
    if all(c in df.columns for c in ["lx", "ly", "lz"]):
        df[box_cols].to_csv(output_dir / "box_length.csv", index=False)

    # 压力数据
    press_cols = [c for c in ["time_ps", "stage", "press"] if c in df.columns]
    if "press" in df.columns:
        df[press_cols].to_csv(output_dir / "pressure.csv", index=False)

    print(f"数据已输出到: {output_dir.resolve()}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract thermo data from LAMMPS NPT thermal cycle log."
    )

    parser.add_argument(
        "-i", "--input",
        required=True,
        help="LAMMPS log 文件，例如 log.lammps"
    )

    parser.add_argument(
        "-o", "--output",
        default="extracted_thermo",
        help="输出文件夹，默认 extracted_thermo"
    )

    parser.add_argument(
        "--timestep",
        type=float,
        default=0.001,
        help="LAMMPS timestep，单位 ps。metal 单位下 0.001 = 0.001 ps"
    )

    parser.add_argument(
        "--natoms",
        type=int,
        default=16148,
        help="体系总原子数。默认 16148"
    )

    args = parser.parse_args()

    df = parse_lammps_log(args.input)
    df = normalize_columns(df)
    df = add_time_and_stage(df, timestep_ps=args.timestep)
    df = add_per_atom_values(df, natoms=args.natoms)

    save_outputs(df, args.output)

    print("\n识别到的列名:")
    print(df.columns.tolist())

    print("\n前5行数据:")
    print(df.head())

    print("\n各阶段数据点数量:")
    print(df["stage"].value_counts())


if __name__ == "__main__":
    main()