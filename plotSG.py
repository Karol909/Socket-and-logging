import matplotlib.pyplot as plt
import numpy as np
import re
import os

extra_labels = {
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

def pressurePointFromBuffer(sg_buffer, window=40):
    sum1 = 0
    sum2 = 0
    max_diff = 0
    max_diff_idx = 0
    start_idx = window
    # Calc first windows
    for idx in range(start_idx, window+start_idx):
        sum1 += sg_buffer[idx]
        sum2 += sg_buffer[idx+window]
    # Running windows to get the max difference
    for idx in range(window + start_idx, len(sg_buffer) - window):
        sum1 -= sg_buffer[idx-window]
        sum1 += sg_buffer[idx]
        sum2 -= sg_buffer[idx]
        sum2 += sg_buffer[idx+window]
        diff = sum1 - sum2 if sum1 > sum2 else -(sum2 - sum1)
        # if diff > max_diff:
        if diff > max_diff and len(sg_buffer) - idx < 160:
            max_diff = diff
            max_diff_idx = idx
    return max_diff_idx

def clean_log(file_path, out_path=None):
    timestamp_re = re.compile(r"(\d{2}:\d{2}:\d{2})")
    with open(file_path, "r") as f:
        content = f.read()
    content = content.replace("\n","").replace("\r","").replace("bytearray(b'","").replace("'), ", "").replace("\\r\\n","\n")
    content = content.replace("\\xc2\\xb5","µ")
    content = timestamp_re.sub("", content) # remove all timestamps
    if out_path is not None:
        with open(out_path, 'w', encoding="utf-8") as f:
            f.write(content)
    return content

def extract_sg_buffer(file_path):
    results = []

    # Regular expressions
    timestamp_re = re.compile(r"(\d{2}:\d{2}:\d{2})")
    pair_re = re.compile(r"(\d+),(\d+)")
    size_re = re.compile(r"of size (\d+)")

    content = clean_log(file_path).replace("\n","")
    
    loop_idx = 0
    last_estimate = 0
    for estimate in content.split(" Estimate ")[1:]:
        # Extract no
        estimate_no = estimate[:estimate.find(':')]
        try:
            estimate_no = int(estimate_no)
        except:
            print(f'Error on estimate number: {estimate_no} in {file_path}')
            continue
        
        # Track loops
        if last_estimate > estimate_no:
            loop_idx+=1
        last_estimate = estimate_no

        # Cut off end
        end_idx = estimate.find("of size ")
        if end_idx < 0:
            print(f'Incomplete buffer data: Estimate {estimate_no} in file: {file_path}')
            continue
        estimate = estimate[:end_idx+13]

        # Extract buffer pairs
        pairs = pair_re.findall(estimate)
        buffer = [(int(a), int(b), estimate_no, loop_idx) for a, b in pairs]
        
        # Check buffer size
        size_match = size_re.search(estimate)
        if size_match:
            size = int(size_match.group(1))
            if len(buffer) != size:
                print(f'Incomplete buffer: {len(buffer)} != {size} for estimate {estimate_no} in file {file_path}')
                continue
            results.extend(buffer)
        
    return np.array(results)

def analyse_sg_buffer(sg, ax=None, moving_avg_window=None):
    loop_numbers = np.unique(sg[:,3])

    # Get sg values, estimates and means before and after
    estimates = []
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    color_idx = 0
    for loop_no in loop_numbers:
        sg_i = sg[sg[:,3]==loop_no]
        for estimate_no in np.unique(sg_i[:,2]):
            sg_e = sg_i[sg_i[:,2] == estimate_no]
            if estimate_no == 1:
                color = colors[color_idx]
                color_idx = (color_idx + 1) % len(colors)
            if ax is not None:
                ax.plot(sg_e[:,0], sg_e[:,1], '.-', color=color, alpha=0.2)
                if moving_avg_window is not None:
                    mavg = np.convolve(sg_e[:,1], np.ones(moving_avg_window) / moving_avg_window, mode='valid')
                    ax.plot(sg_e[moving_avg_window-1:,0], mavg)
            estimate_idx = pressurePointFromBuffer(sg_e[:,1])
            sg_before = sg_e[:estimate_idx,1]
            sg_after  = sg_e[estimate_idx:,1]
            estimates.append([loop_no, estimate_no, sg_e[estimate_idx,0], np.mean(sg_before), np.mean(sg_after), np.var(sg_before), np.var(sg_after)])
    estimates = np.array(estimates)

    # Calc means
    means = []
    for loop_no in loop_numbers:
        est = estimates[estimates[:,0] == loop_no]
        means.append(list(est.mean(axis=0)) + [len(est)])
    means = np.array(means)

    if ax is None:
        return estimates, means
    
    # Add max and min lines
    est_max = np.max(estimates[:,2])
    est_min = np.min(estimates[:,2])
    ax.axvspan(est_min, est_max, color='r', alpha=0.5, zorder=10)
    mean_before_max = np.max(estimates[:,3])
    mean_before_min = np.min(estimates[:,3])
    ax.fill_between((np.min(sg[:,0]), est_min), mean_before_min, mean_before_max, color='m', alpha=0.5, zorder=10)
    mean_after_max = np.max(estimates[:,4])
    mean_after_min = np.min(estimates[:,4])
    ax.fill_between((est_max, np.max(sg[:,0])), mean_after_min, mean_after_max, color='g', alpha=0.5, zorder=10)
    std_before_max = np.sqrt(np.max(estimates[:,5]))
    std_before_min = np.sqrt(np.min(estimates[:,5]))
    ax.fill_between((np.min(sg[:,0]), est_min), mean_before_max + std_before_max, mean_before_min + std_before_min, color='y', alpha=0.5, zorder=9)
    ax.fill_between((np.min(sg[:,0]), est_min), mean_before_min - std_before_max, mean_before_max - std_before_min, color='y', alpha=0.5, zorder=9)
    std_after_max = np.sqrt(np.max(estimates[:,6]))
    std_after_min = np.sqrt(np.min(estimates[:,6]))
    ax.fill_between((est_max, np.max(sg[:,0])), mean_after_max + std_after_min, mean_after_min + std_after_max, color='b', alpha=0.5, zorder=9)
    ax.fill_between((est_max, np.max(sg[:,0])), mean_after_min - std_after_min, mean_after_max - std_after_max, color='b', alpha=0.5, zorder=9)
    
    # Add title
    ax.set_title(f'Point Finding Results: {(means[:,2].mean() - 20) * 1000 * 0.01 / 2:.2f}µm')
    ax.set_ylabel('SG value')
    ax.set_xlabel('mstep')
    ax.grid()

    # Add text
    ax.text(
        0.01, 0.4, f"n: {len(loop_numbers)}\nmean: {np.mean(estimates[:,2]):.1f}\nmax-min: {est_max-est_min:.0f}",
        transform=ax.transAxes,
        fontsize=12,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8)
    )

    return estimates, means

def analyse_folder(folder_path):
    data = []
    for filename in os.listdir(folder_path):
        if not filename.endswith(".txt"):
            continue
        id_re = re.compile(r"SMT(\d+)")
        vol_re = re.compile(r"(\d+)%")
        try:
            id = int(id_re.search(filename).group(1))
            vol = int(vol_re.search(filename).group(1))
        except:
            print(f'{filename} invalid')
            continue
        sg = extract_sg_buffer(os.path.join(folder_path, filename))
        if len(sg) == 0:
            print(f'Empty file {filename}')
            continue
        est, _ = analyse_sg_buffer(sg)
        for loop in np.unique(est[:,0]):
            # print(id, vol, loop, est[est[:,0]==loop][:,2])
            d = est[est[:,0]==loop]
            # data.append([id, vol, loop] + [np.sum(d[:,2])//len(d)] + list(np.mean(d[:,3:], axis=0)))
            data.append([id, vol, loop] + [np.median(d[:,2])] + list(np.mean(d[:,3:], axis=0)))
    data = np.array(data)
    return data

def compare_tools(paths):
    fig, axs = plt.subplots(2,1, sharex=True)
    markers = ['o','s','v']
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    color_idx = 0
    for path in paths:
        data = np.loadtxt(path, skiprows=1)
        color = colors[color_idx]
        color_idx = (color_idx + 1) % len(colors)
        axs[0].plot([],[], '.', color=color, label=f"tool {path.split('/')[-2].split(' ')[-1]}")
        for id in np.unique(data[:,0]):
            d = data[data[:,0] == id]
            for vol in np.sort(np.unique(d[:,1])):
                i = 0 if vol == 100 else 1 if vol == 50 else 2
                dvol = d[d[:,1] == vol]
                axs[0].plot([id-0.2+i*0.2]*len(dvol), dvol[:,2], markers[i], color=color)
                axs[1].plot([id-0.2+i*0.2]*len(dvol), dvol[:,3], markers[i], color=color)

    axs[1].set_xticks(range(1,15))
    combined_labels = [
        f"SMT{id:.0f}\n{extra_labels.get(f'SMT{id:.0f}', '')}"
        for id in range(1,15)
    ]
    axs[1].set_xticklabels(combined_labels)

    for ax in axs:
        ax.grid()

    axs[0].set_title("Mean")
    axs[0].set_ylabel("Position [µm]")
    axs[1].set_title("Spread")
    axs[1].set_ylabel("Max-Min [msteps]")

    axs[0].legend(loc="upper right")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    folders = [
        './Clean data dispense position testing TOOL 1',
        './Clean data dispense position testing TOOL 3',
        './Clean data dispense position testing TOOL 4'
    ]
    compare_tools([f'{f}/export_data.txt' for f in folders])
    exit()

    folder = './Clean data dispense position testing TOOL 3/Tool full logs'
    data = analyse_folder(folder)
    
    max_spread = 0
    max_spread_at = None
    min_spread = 100
    min_spread_at = None
    fig, axs = plt.subplots(3,1, sharex=True)
    pos = 0
    export_data = []
    for id in np.unique(data[:,0]):
        d = data[data[:,0] == id]
        for vol in np.sort(np.unique(d[:,1])):
            i = 0 if vol == 100 else 1 if vol == 50 else 2
            dvol = d[d[:,1] == vol]
            num_estimates = len(dvol)
            if num_estimates != 10:
                print(f'id:{id:.0f}, vol:{vol:.0f}: does not have 10 loops: {num_estimates:.0f}')
            # print(id, vol , dvol[:,3])
            ax = axs[0]
            spread = np.max(dvol[:,3])-np.min(dvol[:,3])
            if spread > max_spread:
                max_spread = spread
                max_spread_at = (id, vol)
            if spread < min_spread:
                min_spread = spread
                min_spread_at = (id, vol)
            export_data.append([id,vol,np.mean(dvol[:,3]),spread])
            ax.scatter([pos-0.2+i*0.2]*len(dvol), (dvol[:,3] - 20) * 1000 * 0.01 / 2, marker="o", s=40,
                       color=["#8B0000","#E53935","#FFB7BE"][i],
                       label=f"{vol:.0f}%",
                       edgecolor="black", alpha=0.8)
            ax = axs[1]
            ax.scatter([pos-0.2+i*0.2]*len(dvol), dvol[:,4], marker="o", s=40,
                       color=["#008B23","#35E561","#B7FFBF"][i],
                       edgecolor="black", alpha=0.8)
            
            ax.scatter([pos-0.2+i*0.2]*len(dvol), dvol[:,5], marker="o", s=40,
                       color=["#43008B","#6135E5","#BBB7FF"][i],
                       edgecolor="black", alpha=0.8)
            ax = axs[2]
            ax.scatter([pos-0.2+i*0.2]*len(dvol), dvol[:,6], marker="o", s=40,
                       color=["#008B23","#35E561","#B7FFBF"][i],
                       edgecolor="black", alpha=0.8)
            ax.scatter([pos-0.2+i*0.2]*len(dvol), dvol[:,7], marker="o", s=40,
                       color=["#43008B","#6135E5","#BBB7FF"][i],
                       edgecolor="black", alpha=0.8)
        pos += 1
    print('max spread', max_spread, max_spread_at)
    print('min spread', min_spread, min_spread_at)
    np.savetxt('export_data.txt',np.array(export_data),fmt="%d %d %f %f",header="ID VOL mean spread")

    ax.set_xticks(range(pos))
    combined_labels = [
        f"SMT{id:.0f}\n{extra_labels.get(f'SMT{id:.0f}', '')}"
        for id in np.unique(data[:,0])
    ]
    ax.set_xticklabels(combined_labels)
    for ax in axs:
        ax.grid(True, linestyle=":", alpha=0.6)

    handles, labels = axs[0].get_legend_handles_labels()
    unique = dict(zip(labels, handles))  # removes duplicates
    axs[0].legend(unique.values(), unique.keys())
    
    axs[0].set_title("Dispense Position (DP)")
    axs[0].set_ylabel("Position [µm]")

    axs[1].scatter([], [],  marker="o", s=40, label="before DP", color="#35E561", edgecolor="black", alpha=0.8)
    axs[1].scatter([], [],  marker="o", s=40, label="after DP", color="#6135E5", edgecolor="black", alpha=0.8)
    axs[1].legend(loc="center right")
    axs[1].set_title("Mean SG value")
    axs[1].set_ylabel("StallGuard [-]")

    axs[2].scatter([], [],  marker="o", s=40, label="before DP", color="#35E561", edgecolor="black", alpha=0.8)
    axs[2].scatter([], [],  marker="o", s=40, label="after DP", color="#6135E5", edgecolor="black", alpha=0.8)
    axs[2].legend(loc="upper right")
    axs[2].set_title("Std.Dev. of SG value")
    axs[2].set_ylabel("StallGuard [-]")
    # plt.show()
    # exit()

    path = './Clean data dispense position testing TOOL 3/Tool full logs/2026-04-27 111111 SMT2_rack_0_volume10%.txt'
    sg = extract_sg_buffer(path)
    fig, ax = plt.subplots(1,1)
    estimates, means = analyse_sg_buffer(sg, ax)
    wrong_estimates = []
    for est in estimates:
        if est[2] < 6000:
            wrong_estimates.append(est)
    print(len(wrong_estimates), len(estimates))

    plt.show()
