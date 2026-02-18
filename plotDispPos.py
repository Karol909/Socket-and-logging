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

pipettes = ["SMT1", "SMT2", "SMT3", "SMT4", "SMT5", "SMT6", "SMT7", "SMT8"]

label = f"spread = {max(data)-min(data)} um = {(max(data)-min(data))/1000} mm"
plt.plot(pipettes, data, marker="o", linestyle="", label=label)
ax = plt.gca()
ax.axhline(max(data), color="gray", linestyle="--", alpha=0.7)  
ax.axhline(min(data), color="gray", linestyle="--", alpha=0.7)  
plt.xlabel("Sample index")
plt.grid(True, linestyle=":", alpha=0.7)
plt.title("Piston position found in (um)")
plt.legend()
plt.show()