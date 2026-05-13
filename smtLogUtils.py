import re
import os
import time
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Extract points from sg readings (done on the arduino)
def pressurePointFromBuffer(sg_buffer, window=40):
    if len(sg_buffer) < 3*window:
        print('Buffer to small for point finding')
        return 0, 0
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
        if diff > max_diff:
        # if diff > max_diff and len(sg_buffer) - idx < 160:
            max_diff = diff
            max_diff_idx = idx
    return max_diff_idx, max_diff

# Clean the logs from strings added by the log receiver
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

# Find the StallGuard measurements in the log
def extract_sg_buffer(file_path, print_warnings=True):
    results = []

    # regular expressions
    buffer_re = re.compile(r"(?:\d{1,4},\d{1,3};){10,}")
    pair_re = re.compile(r"(\d{1,4}),(\d{1,3})")
    size_re = re.compile(r"of size (\d{1,3})")
    estimate_re = re.compile(r"Estimate (\d{1,2})")
    dispense_re = re.compile(r"Found dispense position: \[µm\] (\d+)")

    # make it one line
    data = clean_log(file_path).replace("\n","")
    
    # extract buffers
    loop_num = 0
    last_estimate_no = -1
    last_buffer_end_idx = 0

    results = []
    dispense_positions = []
    for i, match in enumerate(buffer_re.finditer(data)):
        buffer_start_idx = match.start()
        buffer_end_idx   = match.end()

        # the buffer command returns data;....
        if data[buffer_start_idx-5:buffer_start_idx] == "data;":
            estimate_no = i
        
        # buffers returned from the find command
        else:
            start_idx = data.find("Estimate", last_buffer_end_idx, buffer_start_idx)
            if start_idx < 0:
                if print_warnings: print(f'Buffer without estimate number (guessing {last_estimate_no+1}): {file_path}, loop:{loop_num}, last_estimate:{last_estimate_no}')
                estimate_no = last_estimate_no +1
            else:
                try:
                    estimate_no = int(estimate_re.search(data[start_idx:buffer_start_idx]).group(1))
                except Exception as e:
                    if print_warnings: print(f'Failed to read estimate number (guessing {last_estimate_no+1}): {file_path}, loop:{loop_num}, last_estimate:{last_estimate_no}, {e}')
                    estimate_no = last_estimate_no + 1

            # Look for final dispense pos
            disp_idx = data.find("Found dispense position", buffer_end_idx)
            next_idx = data.find("Estimate", buffer_end_idx)
            if disp_idx > 0 and (next_idx < 0 or next_idx > disp_idx):
                match = dispense_re.search(data, buffer_end_idx)
                if match:
                    dispense_positions.append((loop_num, int(match.group(1))))
        
        if last_estimate_no > estimate_no:
            loop_num += 1

        values = np.array([(int(step), int(sg), estimate_no, loop_num) for step, sg in pair_re.findall(data[buffer_start_idx:buffer_end_idx])])
        
        # Remove duplicate steps
        _, idx = np.unique(values[:, 0], return_index=True)
        duplicate_steps = len(values) - len(idx)
        if duplicate_steps > 0:
            # if print_warnings: print(f'Duplicate steps found in buffer ({duplicate_steps} removed): {file_path}, i:{i}, loop:{loop_num}, estimate:{estimate_no}')
            values = values[idx]

        size_match = size_re.search(data, buffer_start_idx-20, buffer_end_idx + 20)
        if not size_match:
            if print_warnings: print(f'No buffer size found: {file_path}, i:{i}, loop:{loop_num}, estimate:{estimate_no}')
        else:
            buf_size = int(size_match.group(1))
            if buf_size - len(values) != 0:
                if print_warnings: print(f'Incomplete buffer ({buf_size-len(values)} missing): {file_path}, i:{i}, loop:{loop_num}, estimate:{estimate_no}')
                if buf_size - len(values) > 100:
                    if print_warnings: print(f'Removing small buffer ({len(values)}): {file_path}, i:{i}, loop:{loop_num}, estimate:{estimate_no}')
                    if last_estimate_no > estimate_no:
                        loop_num -= 1
                    estimate_no = last_estimate_no
                    last_buffer_end_idx = buffer_end_idx
                    continue
        
        last_estimate_no = estimate_no
        last_buffer_end_idx = buffer_end_idx
        results.extend(values)
    results = np.array(results)

    # Check for missing values
    missing_idx = np.where(np.abs(np.diff(results[:,2]+results[:,3]*10))>1)[0]
    for idx in missing_idx:
        if print_warnings: print(f'Missing values at (estimate_no, loop_num): {file_path}\n{results[idx:idx+2, 2:]}')
    
    for loop_num in np.unique(results[:,3]):
        estimate_num = len(np.unique(results[results[:,3] == loop_num][:,2]))
        if estimate_num < 10:
            if print_warnings: print(f'Only {estimate_num} estimates for loop {loop_num}: {file_path}')
    

    return results, np.array(dispense_positions)

def draw_mean_std_bars(x_min, x_max, mean_vals, std_vals, ax, mean_color, std_color):
    mean_max = mean_vals.max()
    mean_min = mean_vals[mean_vals != 0].min()
    std_max = std_vals.max()
    std_min = std_vals[std_vals != 0].min()
    ax.fill_between((x_min, x_max), mean_min, mean_max, color=mean_color, alpha=0.5, zorder=10)
    ax.fill_between((x_min, x_max), mean_max + std_max, mean_min + std_min, color=std_color, alpha=0.5, zorder=9)
    ax.fill_between((x_min, x_max), mean_min - std_max, mean_max - std_min, color=std_color, alpha=0.5, zorder=9)
    
def analyse_sg_buffer(sg_buf, disp_pos=[], ax=None, moving_avg_window=None, min_contact_ratio=0.3, x_in_um=True, step_offset=4):
    
    if x_in_um:
        sg_buf[:,0] = (sg_buf[:,0] - step_offset) * 1000 * 0.01 / 2

    buffer_data = []
    for loop_num in np.unique(sg_buf[:,3]):
        loop_data = sg_buf[sg_buf[:,3] == loop_num]

        for iter_num in np.unique(loop_data[:,2]):
            iter_data = loop_data[loop_data[:,2] == iter_num]

            disp_idx, disp_val = pressurePointFromBuffer(iter_data[:,1])
            disp_step = iter_data[disp_idx,0]

            contact_idx, contact_val = pressurePointFromBuffer(iter_data[:disp_idx, 1])
            contact_ratio = contact_val/(disp_val+1e-8)
            if contact_ratio < min_contact_ratio:
                contact_idx = 0
            contact_step = iter_data[contact_idx, 0]

            mean_air     = np.mean(iter_data[0:contact_idx,1]) if contact_idx > 0 else 0
            mean_contact = np.mean(iter_data[contact_idx:disp_idx,1])
            mean_blow    = np.mean(iter_data[disp_idx:,1])
            std_air      = np.std(iter_data[0:contact_idx,1]) if contact_idx > 0 else 0
            std_contact  = np.std(iter_data[contact_idx:disp_idx,1])
            std_blow     = np.std(iter_data[disp_idx:,1])

            buffer_data.append((loop_num, iter_num, disp_step, contact_step, contact_ratio, mean_air, std_air, mean_contact, std_contact, mean_blow, std_blow))
    buffer_data = np.array(buffer_data)

    if ax is None:
        return buffer_data
    
    # Plotting
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    color_idx = 0
    
    for loop_num in np.unique(sg_buf[:,3]):
        loop_data = sg_buf[sg_buf[:,3] == loop_num]
        color = colors[color_idx]
        color_idx = (color_idx + 1) % len(colors)

        for iter_num in np.unique(loop_data[:,2]):
            iter_data = loop_data[loop_data[:,2] == iter_num]

            if moving_avg_window is not None:
                mavg = np.convolve(iter_data[:,1], np.ones(moving_avg_window) / moving_avg_window, mode='valid')
                ax.plot(iter_data[moving_avg_window//2-1:-moving_avg_window//2,0], mavg, color=color)
                # # plot difference
                # ax.plot(iter_data[moving_avg_window:-moving_avg_window+1,0], mavg[:-moving_avg_window:]-mavg[moving_avg_window:], color=color, alpha=0.2)
            else:
                ax.plot(iter_data[:,0], iter_data[:,1], '.-', color=color, alpha=0.2)
        
        ax.vlines(buffer_data[buffer_data[:,0]==loop_num][:,2].mean(), ymin=ax.get_ylim()[0], ymax=ax.get_ylim()[1], color=color, alpha=0.5, zorder=20)

    # Add max and min lines
    disp_max = buffer_data[:,2].max()
    disp_min = buffer_data[:,2].min()
    ax.axvspan(disp_min, disp_max, color='r', alpha=0.5, zorder=10)

    # Check if contact point is found
    if np.mean(buffer_data[:,4]) > min_contact_ratio:
        contact_max = buffer_data[:,3].max()
        contact_min = buffer_data[:,3][buffer_data[:,5] != 0].min()
        ax.axvspan(contact_min, contact_max, color='g', alpha=0.5, zorder=10)

        draw_mean_std_bars(iter_data[:,0].min(), contact_min, buffer_data[:,5], buffer_data[:,6], ax, 'm', 'y')
        draw_mean_std_bars(contact_max, disp_min, buffer_data[:,7], buffer_data[:,8], ax, 'm', 'y')

    else:
        # Draw contact mean and std
        draw_mean_std_bars(iter_data[:,0].min(), disp_min, buffer_data[:,7], buffer_data[:,8], ax, 'm', 'y')
    # Draw blow mean and std
    draw_mean_std_bars(disp_max, iter_data[:,0].max(), buffer_data[:,9], buffer_data[:,10], ax, 'm', 'y')

    # Add title
    ax.set_title(f'Result: {buffer_data[:,2].mean():.2f}' + (f', {(buffer_data[:,2].mean()-step_offset)*1000*0.01/2:.2f}µm ' if not x_in_um else 'µm ') + f'(disp: {np.mean(disp_pos[:,1]):.2f}µm)')
    ax.set_ylabel('SG value')
    ax.set_xlabel('mstep')
    if x_in_um:
        ax.set_xlabel('µm')
    ax.grid()

    # Add text
    ax.text(
        0.01, 0.4, f"n: {len(disp_pos)}\nmedian: {np.median(buffer_data[:,2]):.0f}\nmax-min: {disp_max-disp_min:.0f}",
        transform=ax.transAxes,
        fontsize=12,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8)
    )
    
    return buffer_data

def get_data_from_sg_buf(sg_buf, in_mu=True, step_offset=4, min_contact_ratio=0.3):
    buf_data = analyse_sg_buffer(sg_buf, x_in_um=False, min_contact_ratio=min_contact_ratio)
    disp_pos = []
    contact_pos = []
    sg_values = []
    for loop_num in np.unique(buf_data[:,0]):
        loop_data = buf_data[buf_data[:,0] == loop_num]
        step = loop_data[:,2].sum()//len(loop_data)
        if step_offset is not None:
            step -= step_offset
        if in_mu:
            step = step * 1000*0.01/2
        disp_pos.append((loop_num, step))
        # Check contact point
        step = loop_data[:,3].sum()//len(loop_data)
        if in_mu:
            step = step * 1000*0.01/2
        contact_pos.append((loop_num, step))
        # Add sg values
        sg_values.append(np.hstack(([loop_num],loop_data[:,4:].mean(axis=0))))


    return np.array(disp_pos, dtype=int), np.array(contact_pos, dtype=int), np.array(sg_values)

def get_data_from_file(file_path, step_offset=4):
    sg_buf, disp_pos = extract_sg_buffer(file_path)
    disp, contact, sg_values = get_data_from_sg_buf(sg_buf, step_offset=step_offset)
    if len(disp_pos) == 0:
        disp_pos = np.zeros_like(disp)
    if len(disp_pos) != len(disp):
        print(f'Found disp pos ({len(disp_pos)}) does not match loop nums ({len(disp)}): {file_path}')
        keep_idx = []
        min_len = min(len(disp_pos), len(disp_pos))
        for i in range(min_len):
            loop_num = disp_pos[i,0]
            idx = np.argwhere(disp[:,0] == loop_num)[0][0]
            keep_idx.append(idx)
        disp_pos = disp_pos[:min_len]
        keep_idx = np.array(keep_idx)
        disp = disp[keep_idx]
        contact = contact[keep_idx]
        sg_values = sg_values[keep_idx]
        
    # loop_num, found_pos, loop_num, mean_pos, contact_pos, ratio, air_mean, air_std, contact_mean, contact_std, blow_mean, blow_std
    return np.hstack((disp_pos, disp, contact[:,1:], sg_values[:,1:]))

def get_data_from_folder(folder_path, step_offset=4):
    name_re = re.compile(r"([A-Za-z]+)(\d+)")
    vol_re = re.compile(r"(\d+)%")

    data = {}
    repeated = {}
    for filename in os.listdir(folder_path):
        if not filename.endswith(".txt"):
            continue
        try:
            name_match = name_re.search(filename)
            name = name_match.group(1)
            id = int(name_match.group(2))
            vol = int(vol_re.search(filename).group(1))
        except Exception as e:
            print(f'{filename} invalid: {e}')
            continue
        file_data = get_data_from_file(os.path.join(folder_path, filename), step_offset)
        if len(file_data) == 0:
            print(f'Empty file {filename}')
            continue
        key = f'{name}{id}@{vol}%'
        if key in data:
            if key in repeated:
                repeated[key] += 1
            else:
                repeated[key] = 1
            key += f'_{repeated[key]}'
        data[key]=file_data
    if len(repeated) > 0:
        print(repeated)
    return data

def find_file(folder, smt, vol, idx=0):
    found = []
    for file in Path(folder).rglob("*"):
        if file.is_file():
            name = file.name
            if smt in name and vol in name:
                found.append(file)
    if idx < len(found):
        return found[idx]
    print(f'Found only {len(found)} files. Idx: {idx}')
    return None

if __name__ == "__main__":
    measure_example = './MeasureFullStrokes/SMT10_100.txt'
    find_example = './Clean data dispense position testing TOOL 3/Tool full logs/2026-04-27 165357 SMT9_rack_5_volume100%.txt'
    rainin_example = './Rainin/rainin200_10%.txt'
    folder1 = './Clean data dispense position testing TOOL 1/Tool full logs'
    folder3 = './Clean data dispense position testing TOOL 3/Tool full logs'
    folder4 = './Clean data dispense position testing TOOL 4/Tool full logs'
    file = find_file(folder3, "SMT4", '10%')
    
    # clean_log(find_example, find_example + ".clean")
    
    sg_buf, disp_pos = extract_sg_buffer(file)
    dpos, cpos, sg_vals = get_data_from_sg_buf(sg_buf)
    # print(disp_pos-dpos)
    # print(sg_vals)
    fdata = get_data_from_file(file)
    # print(data[:,1].mean())
    data = get_data_from_folder(folder3)
    print(data['SMT4@10%']-fdata)

    smt = 'SMT4'
    file_num = 0
    moving_avg = 20
    folder = folder1
    fig, axs = plt.subplots(3,1, sharex=True)
    file = find_file(folder1, smt, '100%', file_num)
    print(file)
    sg_buf, disp_pos = extract_sg_buffer(file)
    analyse_sg_buffer(sg_buf, disp_pos, axs[0], moving_avg)
    # axs[0].set_title("100%")
    file = find_file(folder3, smt, '100%', file_num)
    print(file)
    sg_buf, disp_pos = extract_sg_buffer(file)
    analyse_sg_buffer(sg_buf, disp_pos, axs[1], moving_avg)
    # axs[1].set_title("50%")
    file = find_file(folder4, smt, '100%', file_num)
    print(file)
    sg_buf, disp_pos = extract_sg_buffer(file)
    analyse_sg_buffer(sg_buf, disp_pos, axs[2], moving_avg)
    # axs[2].set_title("10%")

    plt.tight_layout()
    plt.show()
