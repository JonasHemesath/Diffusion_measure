import cv2
import os
import json
import numpy as np
import matplotlib.pyplot as plt

def image_analysis(aquisition):
    fp = aquisition["file_path"] + "images\\"
    sp = aquisition["file_path"] + "analysis\\"

    if not os.path.isdir(sp):
        os.makedirs(sp)

    image_groups = {f[0:6]: [] for f in os.listdir(fp)}
    for f in os.listdir(fp):
        image_groups[f[0:6]].append(cv2.imread(fp + f))

    times = []
    avg_images = []
    avg_offset = []
    for k, v in image_groups.items():
        if k != "offset":
            temp = np.mean(v, axis=0)
            avg_images.append(temp.astype(np.uint8))
            for i, c in enumerate(k):
                if c != 0:
                    times.append(int(k[i:]))
                    break
        else:
            avg_offset = np.mean(v, axis=0)
            avg_offset = avg_offset.astype(np.uint8)

    times_min = [i/60 for i in times]

    # Calculate pixel-wise difference to offset
    images_offset = [image-avg_offset for image in avg_images]

    for i, image in enumerate(images_offset):
        cv2.imwrite(sp + str(times[i]) + ".png",image)

    readout = np.zeros((4, len(images_offset)))

    for i, image in enumerate(images_offset):
        for j in range(3):
            readout[j,i] = np.sum(image[:,:,j]) / (image.shape[0] * image.shape[1])
            readout[3,i] += abs(readout[j,i])


    # Plot pixel-wise comparison to offset
    fig, ax = plt.subplots(4,1)
    labels = ["R", "G", "B", "Combined absolute difference"]
    colors = ["tab:red", "tab:green", "tab:blue", "k"]

    for i in range(4):
        ax[i].plot(times_min, readout[i,:], colors[i])
        ax[i].set(xlabel = "Time [min]", ylabel = "Mean pixel-wise difference")
        ax[i].set_title(labels[i])

    fig.set_size_inches(6, 10)
    fig.tight_layout()
    fig.savefig(sp + "plot_pixelwise.png")

    #Calculate overall difference to offset
    readout_overall = np.zeros((4, len(avg_images)))

    for i, image in enumerate(avg_images):
        for j in range(3):
            readout_overall[j,i] = (np.mean(image[:,:,j]) - np.mean(avg_offset[:,:,j]))
            readout_overall[3,i] += abs(readout_overall[j,i])

    # Plot overall difference
    fig, ax = plt.subplots(4,1)

    for i in range(4):
        ax[i].plot(times_min, readout_overall[i,:], colors[i])
        ax[i].set(xlabel = "Time [min]", ylabel = "Overall difference")
        ax[i].set_title(labels[i])

    fig.set_size_inches(6, 10)
    fig.tight_layout()
    fig.savefig(sp + "plot_overall.png")

if __name__ == '__main__':
    aquisition_file = input("Enter path to aquisition file:\n")
    
    with open(aquisition_file) as f:
        aquisition = json.load(f)
    image_analysis(aquisition)