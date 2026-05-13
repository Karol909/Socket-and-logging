import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle
import smtLogUtils as smt
import numpy as np
import joblib

pipetteVolumes = {
    "SMT1": "10000 uL",
    "SMT2": "5000 uL",
    "SMT3": "1000 uL",
    "SMT4": "300 uL",
    "SMT5": "200 uL",
    "SMT6": "100 uL",
    "SMT7": "20 uL",
    "SMT8": "10 uL",
    "SMT9": "1000 uL",
    "SMT10": "1000 uL",
    "SMT11": "1000 uL",
    "SMT12": "200 uL",
    "SMT13": "200 uL",
    "SMT14": "200 uL",
}

colors = [
     mcolors.to_rgb("#E53535"),
     mcolors.to_rgb("#E58435"),
     mcolors.to_rgb("#CBE535"),
     mcolors.to_rgb("#00FB15"),
     mcolors.to_rgb("#35E5A1"),
     mcolors.to_rgb("#3564E5"),
     mcolors.to_rgb("#A435E5"),
     mcolors.to_rgb("#E535AA"),
     mcolors.to_rgb("#E53535"),
]

def shade_color(color, factor):
    color = np.array(color)
    # factor < 1 → darker (toward black)
    # factor > 1 → lighter (toward white)
    if factor < 1:
        return color * factor
    else:
        return color + (1 - color) * (factor - 1)

def set_xticks(ax, ticks):
    combined_labels = [
        f"{name}\n{vol}"
        for name, vol in ticks.items()
    ]
    ax.set_xticks(range(len(ticks)))
    ax.set_xticklabels(combined_labels)



def scatterPerVol(data_dict, col_idx=1, err_idx=None, ax=None, color=mcolors.to_rgb("#808080"), mean_std=False, print_spread=None):
    if ax is None:
        fig, ax = plt.subplots()
    
    pip_idata = {}
    pip_data = {}
    for pip, data in data_dict.items():
        pip_split = pip.split('@')
        pip_tag = pip_split[0]
        pip_vol = pipetteVolumes[pip_tag]
        pip_percentage = pip_split[1].split('%')[0]
        x_pos = list(pipetteVolumes.keys()).index(pip_tag)
        if pip_percentage == "100":
            x_pos -= 0.1
            c = shade_color(color, 0.6)
        elif pip_percentage == "50":
            c = color
        elif pip_percentage == "10":
            x_pos += 0.1
            c = shade_color(color, 1.4)
        else:
            print(f'Unknown percentage {pip_percentage} ({pip})')
        
        if err_idx is not None:
            ax.scatter([x_pos]*len(data), data[:,col_idx]+data[:,err_idx], marker=r'$\frown$', s=40, edgecolor=c, alpha=0.2)
            ax.scatter([x_pos]*len(data), data[:,col_idx]-data[:,err_idx], marker=r'$\smile$', s=40, edgecolor=c, alpha=0.2)
        ax.scatter([x_pos]*len(data), data[:,col_idx], marker="o", s=40, color=c, edgecolor="none" if mean_std else "black", alpha=0.2 if mean_std else 0.8)

        if mean_std:
            mean = data[:,col_idx].mean()
            if err_idx is not None:
                std = data[:,err_idx].mean()
            else:
                std = data[:,col_idx].std()
            ax.scatter([x_pos], mean+std, marker=r'$\frown$', s=40, edgecolor='black', alpha=1, zorder=10)
            ax.scatter([x_pos], mean-std, marker=r'$\smile$', s=40, edgecolor='black', alpha=1, zorder=10)
            ax.scatter([x_pos], mean,  marker="o", s=40, color=c, edgecolor="black", alpha=1, zorder=12)
            
            key = pip_tag + (pip.split('_')[1] if len(pip.split('_')) > 1 else '')
            if key not in pip_idata:
                pip_idata[key] = [[],[]]
            pip_idata[key][0].append(x_pos)
            pip_idata[key][1].append(mean)
            key = pip_tag
            if key not in pip_data:
                pip_data[key] = [[],[],[],[]]
            pip_data[key][0].append(x_pos)
            pip_data[key][1].append(mean)
            pip_data[key][2].append(data[:,col_idx].min())
            pip_data[key][3].append(data[:,col_idx].max())

    for pip, data in pip_idata.items():
        x_pos = np.array(data[0])
        y = np.array(data[1])
        order = np.argsort(x_pos)
        ax.plot(x_pos[order], y[order], "-", color=color)
    
    if mean_std and print_spread is not None:
        for pip, data in pip_data.items():
            x_pos = np.array(data[0])
            y_mean = np.mean(data[1])
            y_min = np.min(data[2])
            y_max = np.max(data[3])
            rect = Rectangle(
                (x_pos.min()-0.1, y_min),
                x_pos.max()-x_pos.min()+0.2,
                y_max-y_min,
                edgecolor=color,
                facecolor='none'
            )
            ax.add_patch(rect)
            x = (x_pos.min()-0.1) if print_spread // 2 == 0 else (x_pos.max()+0.1)
            ha = 'right' if print_spread // 2 == 0 else 'left'
            y = y_max if print_spread % 2 == 0 else y_min
            va = 'bottom' if print_spread % 2 == 0 else 'top'
            ax.text(
                x, y,
                f'{y_max-y_min:.0f}',
                fontsize=8,
                ha=ha,
                va=va,
                color=color
            )


    

if __name__ == "__main__":
    tool1 = './Clean data dispense position testing TOOL 1/Tool full logs'
    data1 = smt.get_data_from_folder(tool1, 20)
    tool4 = './Clean data dispense position testing TOOL 4/Tool full logs'
    data4 = smt.get_data_from_folder(tool4, 4)
    tool3 = './Clean data dispense position testing TOOL 3/Tool full logs'
    data3 = smt.get_data_from_folder(tool3, 4)
    # joblib.dump([data1, data4, data3], "tool_data.pkl")
    # joblib.dump([data1, data4, data3], "tool_data_find_limit.pkl")

    # data1, data4, data3 = joblib.load("tool_data.pkl")
    # data1, data4, data3 = joblib.load("tool_data_find_limit.pkl")
    # print(data4['SMT10@50%'])
    fig, axs = plt.subplots(2,1, sharex=True)
    scatterPerVol(data1, 3, ax=axs[0], color=colors[0], mean_std=True, print_spread=0)
    scatterPerVol(data4, 1, ax=axs[0], color=colors[3], mean_std=True, print_spread=1)
    scatterPerVol(data3, 3, ax=axs[0], color=colors[6], mean_std=True, print_spread=2)
    scatterPerVol(data1, 8, 9, ax=axs[1], color=colors[1], mean_std=True)
    scatterPerVol(data4, 8, 9, ax=axs[1], color=colors[4], mean_std=True)
    scatterPerVol(data3, 8, 9, ax=axs[1], color=colors[7], mean_std=True)
    scatterPerVol(data1, 10, 11, ax=axs[1], color=colors[2], mean_std=True)
    scatterPerVol(data4, 10, 11, ax=axs[1], color=colors[5], mean_std=True)
    scatterPerVol(data3, 10, 11, ax=axs[1], color=colors[8], mean_std=True)
    set_xticks(axs[1], pipetteVolumes)

    color=mcolors.to_rgb("#808080")
    axs[0].scatter([], [], marker="o", s=40, color=shade_color(color, 0.6), edgecolor="none", label="100%")
    axs[0].scatter([], [], marker="o", s=40, color=color, edgecolor="none", label="50%")
    axs[0].scatter([], [], marker="o", s=40, color=shade_color(color, 1.4), edgecolor="none", label="10%")
    axs[0].scatter([], [], marker="o", s=40, color=colors[0], edgecolor="black", label="TOOL 1")
    axs[0].scatter([], [], marker="o", s=40, color=colors[3], edgecolor="black", label="TOOL 4")
    axs[0].scatter([], [], marker="o", s=40, color=colors[6], edgecolor="black", label="TOOL 3")
    axs[0].legend(loc="upper right", ncols=1)
    
    axs[1].scatter([], [], marker="o", s=40, color=colors[1], edgecolor="black", label="TOOL 1 (cont)")
    axs[1].scatter([], [], marker="o", s=40, color=colors[2], edgecolor="black", label="TOOL 1 (blow)")
    axs[1].scatter([], [], marker="o", s=40, color=colors[4], edgecolor="black", label="TOOL 4 (cont)")
    axs[1].scatter([], [], marker="o", s=40, color=colors[5], edgecolor="black", label="TOOL 4 (blow)")
    axs[1].scatter([], [], marker="o", s=40, color=colors[7], edgecolor="black", label="TOOL 3 (cont)")
    axs[1].scatter([], [], marker="o", s=40, color=colors[8], edgecolor="black", label="TOOL 3 (blow)")
    axs[1].legend(loc="lower right", ncols=3)

    axs[0].set_ylabel("µm")
    axs[0].set_ylim((29800, 31400))
    axs[1].set_ylabel("StallGuard")
    axs[1].set_ylim((230, 330))

    plt.show()
