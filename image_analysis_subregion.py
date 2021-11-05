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
                    times.append(int(k[i:-1]))   #change
                    break
        else:
            avg_offset = np.mean(v, axis=0)
            avg_offset = avg_offset.astype(np.uint8)

    times_min = [i/60 for i in times]

    # Get subregions
    srs = define_subregions(avg_offset)

    for idx, sr in enumerate(srs):

        # Calculate pixel-wise difference to offset
        images_offset = [image[sr[1]:sr[3], sr[0]:sr[2], :]-avg_offset[sr[1]:sr[3], sr[0]:sr[2], :] for image in avg_images]

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
        fig.savefig(sp + "plot_pixelwise_" + str(idx) + ".png")

        #Calculate overall difference to offset
        readout_overall = np.zeros((4, len(avg_images)))

        for i, image in enumerate(avg_images):
            for j in range(3):
                readout_overall[j,i] = (np.mean(image[sr[1]:sr[3], sr[0]:sr[2],j]) - np.mean(avg_offset[sr[1]:sr[3], sr[0]:sr[2],j]))
                readout_overall[3,i] += abs(readout_overall[j,i])

        # Plot overall difference
        fig, ax = plt.subplots(4,1)

        for i in range(4):
            ax[i].plot(times_min, readout_overall[i,:], colors[i])
            ax[i].set(xlabel = "Time [min]", ylabel = "Overall difference")
            ax[i].set_title(labels[i])

        fig.set_size_inches(6, 10)
        fig.tight_layout()
        fig.savefig(sp + "plot_overall_" + str(idx) + ".png")



def define_subregions(img):
    print("Image size:", img.shape[0:2])
    img_out = img.copy()
    img_temp = img.copy()
    rects = []

    cv2.namedWindow("Subregions")
    cv2.imshow("Subregions",img_out)
    cv2.waitKey(0)
    cv2.destroyWindow("Subregions")

    while True:
        if "y" == input("\nDefine a subregion? y/n\n"):
            while True:
                ps_text = input("\nPlease define two opposite corners of a rectangle in the following format: x1,y1,x2,y2\n")
                ps = [int(i) for i in ps_text.split(',')]
                cv2.rectangle(img_temp, (ps[0], ps[1]), (ps[2], ps[3]), 255)
                cv2.imshow("Subregions",img_temp)
                cv2.waitKey(0)
                cv2.destroyWindow("Subregions")
                if "y" == input("\nCorrect region selected? y/n\n"):
                    img_out = img_temp.copy()
                    rects.append(ps)
                    break
                else:
                    img_temp = img_out.copy()
        else:
            return rects
        

if __name__ == '__main__':
    aquisition_file = input("Enter path to aquisition file:\n")
    
    with open(aquisition_file) as f:
        aquisition = json.load(f)
    image_analysis(aquisition)


