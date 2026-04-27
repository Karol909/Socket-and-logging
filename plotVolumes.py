import matplotlib.pyplot as plt
import numpy as np
import plotSG
import re

def extract_measure_buffer(file_path):
    results = []

    # Regular expressions
    pair_re = re.compile(r"(\d+),(\d+)")
    size_re = re.compile(r"of size (\d+)")

    content = plotSG.clean_log(file_path).replace("\n","")
    
    for i, section in enumerate(content.split("Sending buffer ")[1:]):
        section = section.split('return')[0]

        # Extract buffer pairs
        pairs = pair_re.findall(section)
        buffer = [(int(a), int(b), i+1, 0) for a, b in pairs]
        
        # Check buffer size
        size_match = size_re.search(section)
        if size_match:
            size = int(size_match.group(1))
            if len(buffer) != size:
                print(f'Incomplete buffer: {len(buffer)} != {size} for idx {i} in file {file_path}')
                continue
            results.extend(buffer[5:])
        
    return np.array(results)

def extract_points(sg):
    points = []
    for i in np.unique(sg[:,2]):
        sg_i = sg[sg[:,2]==i]
        dispensePoint = plotSG.pressurePointFromBuffer(sg_i[:,1])
        contactPoint = plotSG.pressurePointFromBuffer(sg_i[:dispensePoint,1], 40)
        points.append([sg_i[dispensePoint,0], sg_i[contactPoint,0]])
    return np.array(points)

if __name__ == "__main__":
    vol_100 = './volumes/SMT10_100.txt'
    vol_50 = './volumes/SMT10_50.txt'
    vol_10 = './volumes/SMT10_10.txt'
    window_size = None

    sg_100 = extract_measure_buffer(vol_100)
    sg_50 = extract_measure_buffer(vol_50)
    sg_10 = extract_measure_buffer(vol_10)

    sg_100_points = np.median(extract_points(sg_100),axis=0)
    sg_50_points = np.median(extract_points(sg_50),axis=0)
    sg_10_points = np.median(extract_points(sg_10),axis=0)

    fig, axs = plt.subplots(3,1, sharex=True)
    estimates, means100 = plotSG.analyse_sg_buffer(sg_100, axs[0], window_size)
    estimates, means50 = plotSG.analyse_sg_buffer(sg_50, axs[1], window_size)
    estimates, means10 = plotSG.analyse_sg_buffer(sg_10, axs[2], window_size)
    
    axs[0].axvline(x=sg_100_points[1], color='green', linestyle='--', linewidth=2)
    axs[1].axvline(x=sg_50_points[1], color='green', linestyle='--', linewidth=2)
    axs[2].axvline(x=sg_10_points[1], color='green', linestyle='--', linewidth=2)
    msteps100 = means100[0,2]-sg_100_points[1]
    idealmsteps = 3200
    axs[0].text(sg_100_points[1]+10, 250, f"100%: {sg_100_points[1]:.0f}\n{msteps100:.0f}({msteps100/idealmsteps*100:.2f}%)")
    msteps50 = means50[0,2]-sg_50_points[1]
    axs[1].text(sg_50_points[1]+10, 250, f"50%: {sg_50_points[1]:.0f}\n{msteps50:.0f}({msteps50/idealmsteps*100:.2f}%)")
    msteps10 = means10[0,2]-sg_10_points[1]
    axs[2].text(sg_10_points[1]+10, 250, f"10%: {sg_10_points[1]:.0f}\n{msteps10:.0f}({msteps10/idealmsteps*100:.2f}%)")

    plt.tight_layout()
    plt.show()
