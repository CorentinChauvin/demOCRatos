#!/usr/bin/env python3
"""
    Process the saved data and display it nicely
"""

from matplotlib import pyplot as plt
import numpy as np
import csv


# =============================================================================
# CONFIGURATION
#
data_file_path = "output/output_large.csv"


# =============================================================================
# PARSING AND PLOTTING
#
data = {}
keys = []

with open(data_file_path) as csv_file:
    reader = csv.reader(csv_file, delimiter=',', quotechar='"')
    k = -1

    for row in reader:
        k += 1

        # Header
        if k == 0:
            keys = row[:]
            data = {key: [] for key in row}
            continue

        # Data
        for l in range(len(row)):
            try:
                value = float(row[l])

                if keys[l] == "t":
                    value /= 25.0
            except ValueError:
                value = data[keys[l]][-1]

            data[keys[l]].append(value)



nbr_fields = len(keys) - 1
# fig, axs = plt.subplots(nbr_fields)
fig = plt.figure()
gs = fig.add_gridspec(nbr_fields, hspace=0)
axs = gs.subplots(sharex=True, sharey=False)
k = 0

for key in keys:
    if key == "t":
        continue

    axs[k].plot(data["t"], data[key])
    axs[k].set(xlabel="Time (s)", ylabel=key)
    axs[k].label_outer()

    if key == "temperature":
        axs[k].set_yticks(np.arange(np.min(data[key]), np.max(data[key]), 10.0))
        axs[k].set_yticks(np.arange(np.min(data[key]), np.max(data[key]), 2.0), minor=True)
        axs[k].grid(which="minor", alpha=0.3)

    axs[k].set_xticks(np.arange(0, np.max(data["t"]), 60.0))
    axs[k].set_xticks(np.arange(0, np.max(data["t"]), 10.0), minor=True)
    axs[k].grid(which="minor", alpha=0.3)
    axs[k].grid(True)
    k += 1

# plt.show()
plt.waitforbuttonpress()
