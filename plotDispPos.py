import matplotlib.pyplot as plt
import pandas as pd

data = [
    31315,
    30450,
    31130,
    30255,
    30405,
    30775,
    31050,
    31100
]

data2 = [
    31250,
    30380,
    30885,
    30085,
    30200,
    30630,
    30885,
    30960
]

data3 = [
    31270,
    30540,
    31100,
    30160,
    30330,
    30765,
    31025,
    31090
]

pipettes = ["SMT1", "SMT2", "SMT3", "SMT4", "SMT5", "SMT6", "SMT7", "SMT8"]

label = f"Data 18 Feb, spread = {(max(data)-min(data))/1000} mm"
label2 = f"Data 24 Feb, spread = {(max(data2)-min(data2))/1000} mm"
label3 = f"Data 25 Feb, spread = {(max(data3)-min(data3))/1000} mm"
plt.plot(pipettes, data, marker="o", linestyle="",markerfacecolor="green", markeredgecolor="black", alpha=0.8, label=label)
plt.plot(pipettes, data2, marker="o", linestyle="",markerfacecolor="blue", markeredgecolor="black", alpha=0.8, label=label2)
plt.plot(pipettes, data3, marker="o", linestyle="",markerfacecolor="red", markeredgecolor="black", alpha=0.8, label=label3)
ax = plt.gca()

plt.xlabel("Pipette")
plt.grid(True, linestyle=":", alpha=0.7)
plt.title("Piston position found in (um)")
plt.legend()
plt.show()