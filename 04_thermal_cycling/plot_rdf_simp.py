import numpy as np
import matplotlib.pyplot as plt

def read_lammps_rdf(filename):
    """
    读取 LAMMPS fix ave/time + compute rdf[*] + mode vector 输出文件
    返回最后一个 block 的数据矩阵
    """
    blocks = []
    current = []

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()

            if line == "" or line.startswith("#"):
                continue

            parts = line.split()

            # block头部：通常为 timestep 和 Nrows
            if len(parts) == 2:
                if current:
                    blocks.append(np.array(current, dtype=float))
                    current = []
                continue

            try:
                vals = [float(x) for x in parts]
                current.append(vals)
            except ValueError:
                pass

    if current:
        blocks.append(np.array(current, dtype=float))

    if not blocks:
        raise RuntimeError(f"未能从 {filename} 读取RDF数据")

    return blocks[-1]  # 默认取最后一个block


def plot_rdf_stage_compare():
    files = {
        "300 K equil.": "rdf_300K_equil.dat",
        "1850 K hold": "rdf_1850K_hold.dat",
        "Final 300 K hold": "rdf_final_300K_hold.dat"
    }

    plt.figure(figsize=(6,4))

    for label, file in files.items():
        data = read_lammps_rdf(file)
        # data列说明：
        # col0 = bin_id
        # col1 = r
        # 后面是 g(r), coord(r), g(r), coord(r)...
        r = data[:, 1]
        g = data[:, 2]   # 默认先画第一组g(r)，通常可作为总RDF/第一原子对
        plt.plot(r, g, label=label, linewidth=1.5)

    plt.xlabel("r (Å)")
    plt.ylabel("g(r)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("fig_2_4_rdf_stage_compare.png", dpi=300)
    plt.close()

    print("RDF阶段对比图已生成：fig_2_4_rdf_stage_compare.png")


def plot_selected_pairs(filename, outfile_prefix):
    """
    根据RDF输出文件，选择若干原子对的 g(r) 作图
    compute rdf 中每一对对应两列：g(r), coordination
    所以：
    第一对g(r) 在 col2
    第二对g(r) 在 col4
    第三对g(r) 在 col6 ...
    """
    data = read_lammps_rdf(filename)
    r = data[:, 1]

    # 这里按你的pair顺序，自行对应命名
    pair_map = {
        "Pair1": 2,
        "Pair2": 4,
        "Pair3": 6,
        "Pair4": 8,
    }

    plt.figure(figsize=(6,4))
    for label, col in pair_map.items():
        if col < data.shape[1]:
            plt.plot(r, data[:, col], label=label, linewidth=1.2)

    plt.xlabel("r (Å)")
    plt.ylabel("g(r)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{outfile_prefix}.png", dpi=300)
    plt.close()

    print(f"{outfile_prefix}.png 已生成。")


if __name__ == "__main__":
    plot_rdf_stage_compare()

    # 如需单独画某个阶段的多个原子对RDF，可取消注释
    # plot_selected_pairs("rdf_300K_equil.dat", "rdf_pairs_300K_equil")
    # plot_selected_pairs("rdf_1850K_hold.dat", "rdf_pairs_1850K_hold")
    # plot_selected_pairs("rdf_final_300K_hold.dat", "rdf_pairs_final_300K")