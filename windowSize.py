import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from scipy.interpolate import interp1d
from scipy.signal import butter, filtfilt

def read_log(file):
    with open(file) as f:
        lines = f.readlines()
    log = {'cmd': [], 'return': [], 'dt': []}
    data = {}
    for i, l in enumerate(lines):
        try:
            msg, dt = l.replace(r"bytearray(b'", "").split(r"\r\n'), ")
            msg = msg.split(";")
            dt = dt.strip() #datetime.strptime(dt.strip(), "%H:%M:%S")
            if msg[0] == "return":
                log['cmd'].append(msg[1])
                log['return'].append(msg[2])
            elif msg[0] == "data":
                log['cmd'].append("data")
                log['return'].append("-")
                data.update({dt: {'step': [int(m.split(',')[0]) for m in msg[1:-1]], 'sg': [int(m.split(',')[1]) for m in msg[1:-1]]}})
            log['dt'].append(dt)
        except Exception as e:
            print(f'Line {i+1} failed: {e}')
    return log, data

def pressurePointStepFromBuffer(window, step_buffer, sg_buffer):
    ret = {'sum1': [], 'sum2': [], 'step': [], 'diff': []}
    if len(sg_buffer) != len(step_buffer):
        print("buffer not same length")
        return 0, ret
    if (2*window >= len(step_buffer)):
        print("Not enough data!")
        return 0, ret
    sum1 = 0
    sum2 = 0
    max_diff = 0
    max_diff_idx = 0
    start_idx = window
    # Calc first windows
    for idx in range(start_idx,window + start_idx):
        sum1 += sg_buffer[idx]
        sum2 += sg_buffer[idx+window]
    # Running windows to get the max difference
    for idx in range(window + start_idx,len(sg_buffer) - window):
        sum1 -= sg_buffer[idx-window]
        sum1 += sg_buffer[idx]
        sum2 -= sg_buffer[idx]
        sum2 += sg_buffer[idx+window]
        diff = sum1 - sum2
        if (abs(diff) > max_diff):
            max_diff = diff
            max_diff_idx = idx
        ret['sum1'].append(sum1)
        ret['sum2'].append(sum2)
        ret['diff'].append(diff)
        ret['step'].append(step_buffer[idx])
        
    # Serial.println("Max diff " + String(max_diff) + " at step " + String(_step_buffer[max_diff_idx]));
    return step_buffer[max_diff_idx], ret

def plot_estimates(estimate, ret, axs=None, title=""):
    if not isinstance(axs, np.ndarray):
        fig, axs = plt.subplots(2,1, sharex=True)
    axs[0].plot(ret['step'], ret['sum1'], label="sum1")
    axs[0].plot(ret['step'], ret['sum2'], label="sum2")
    axs[0].set_title(title)
    axs[1].plot(ret['step'], ret['diff'], label="diff")
    axs[1].set_title(f"estimate = {estimate} msteps")
    for ax in axs:
        ax.grid()
        ax.legend()

def plot_over_window_size(data):
    means = []
    stds = []
    minmaxs = []
    windows = np.arange(10,100)
    for w in windows:
        e = []
        for i, (k, d) in enumerate(data.items()):
            estimate, ret = pressurePointStepFromBuffer(w,d['step'], d['sg'])
            e.append(estimate)
        means.append(np.mean(e))
        stds.append(np.std(e))
        minmaxs.append(np.max(e)-np.min(e))
    fig, axs = plt.subplots(3,1, sharex=True)
    axs[0].plot(windows, means, label=f"mean")
    axs[1].plot(windows, stds, label="std")
    axs[2].plot(windows, minmaxs, label="minmax")
    for ax in axs:
        ax.grid()
        ax.legend()
    ax.set_xlabel("window size")

def moving_avg(data, window):
    ret = np.zeros_like(data)
    for i in range(len(data)):
        ret[i] = np.average(data[max(0,i-window):i+1])
    return ret

def uniform_step_mean(data, steps_uniform):
    sg_all = []
    for k, d in data.items():
        step = np.array(d['step'])
        sg = np.array(d['sg'])
        interp = interp1d(step, sg, kind='cubic', fill_value="extrapolate")
        sg_uniform = interp(steps_uniform)
        sg_all.append(sg_uniform)
    sg_all = np.array(sg_all)
    sg_mean = sg_all.mean(axis=0)
    return sg_mean

def main():
    # data without pipette as reference
    log, data = read_log('Logs/2026-01-29 144244 G41987H (no pipette)_5000uL_100%.txt')

    # create uniform step range
    steps_uniform = np.arange(2450, 6798, 1)
    
    # get mean reference
    mean_ref = uniform_step_mean(data, steps_uniform)

    # get moving average 
    window = 200
    mean_ref_avg = moving_avg(mean_ref, window)

    # low pass butterworth for comparison
    cutoff = 0.005 # equal to 200 msteps
    b, a = butter(4, cutoff / (1 / 2), btype='low')
    mean_ref_lp = filtfilt(b, a, mean_ref)
    
    
    # load actual pipette data
    # log, data = read_log('Logs/2026-01-29 120729 G41987H_5000uL_10%.txt')
    log, data = read_log('Logs/2026-01-29 122423 P22795J_1000uL_10%.txt')
    # log, data = read_log('Logs/2026-01-29 122042 P22795J_1000uL_50%.txt')
    # log, data = read_log('Logs/2026-01-29 144653 G41987H (pipette in)_5000uL_100%.txt')
    
    # calculate mean, moving average and lp
    mean_pip = uniform_step_mean(data, steps_uniform)
    mean_pip_avg = moving_avg(mean_pip, window)
    mean_pip_lp = filtfilt(b, a, mean_pip)

    # plot data
    plt.figure()
    plt.plot(steps_uniform, mean_ref, label="ref mean", alpha=0.5)
    plt.plot(steps_uniform, mean_ref_avg, label="ref avg")
    plt.plot(steps_uniform, mean_ref_lp, label="ref lp")
    plt.plot(steps_uniform, mean_pip, label="pip mean", alpha=0.5)
    plt.plot(steps_uniform, mean_pip_avg, label="pip avg")
    plt.plot(steps_uniform, mean_pip_lp, label="pip lp")
    plt.xlabel("msteps")
    plt.ylabel("SG value")
    plt.grid()
    plt.legend(ncols=2)
    # plt.show()
    
    # frequency analysis FFT
    F = np.fft.rfft(mean_ref - np.mean(mean_ref))
    k = np.fft.rfftfreq(len(mean_ref), 1)
    plt.figure()
    plt.plot(k, np.abs(F), '-')
    plt.xlabel("Spatial frequency (cycles / mstep)")
    plt.ylabel("SG value")
    plt.grid()
    plt.title(f"first peak at a little more than 0.01 ~ 100 msteps")
    # plt.show()
    
    # plot point estimates of first measurement for selected window sizes
    windows = np.array([5,10,20,40,60,100])
    fig, axs = plt.subplots(2,len(windows), sharex=True)
    d = data[list(data.keys())[0]]
    for i, w in enumerate(windows):
        plot_estimates(*pressurePointStepFromBuffer(w,d['step'],d['sg']), axs[:,i], title=f"window {w}")
    # plt.show()

    # continuous windows
    plot_over_window_size(data)

    plt.show()

if __name__ == "__main__":
    main()