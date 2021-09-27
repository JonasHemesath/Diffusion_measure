import cv2
import time
import json

from image_analysis import image_analysis

def run_script():

    # Aquisition_file: json file containing:
    #                       "ramp_frames": Number of frames to aquire to initialize the cameras brightness
    #                       "camera": Index of camera to use
    #                       "focus": Focus parameter for the camera (specified for LogiTech: https://stackoverflow.com/questions/19813276/manually-focus-webcam-from-opencv)
    #                       "file_path": Storage location for the images
    #                       "time_interval": Total time of the experiment in minutes
    #                       "time_increment": Time between to image aquisitions in seconds
    #                       "average": Number of images to average per timepoint
    #                       "exposure": Define exposure time of camera
    #                       "save_path": Location for saving analysis results

    print("Make sure to define file_path and save_path in your aquisition file!\n")
    aquisition_file = input("Enter path to aquisition file:\n")
    
    with open(aquisition_file) as f:
        aquisition = json.load(f)
    
    rampframes = aquisition["ramp_frames"]

    # initialize the camera
    cam = cv2.VideoCapture(aquisition["camera"])   # index of camera

    focus = aquisition["focus"]
    cam.set(28, focus)                      # Set focus
    cam.set(15, aquisition["exposure"])     # Set exposure

    for i in range(rampframes):
        temp = cam.read()

    # Preview
    s, img = cam.read()
    if s:    # frame captured without any errors
        cv2.namedWindow("cam-test")
        cv2.imshow("cam-test",img)
        cv2.waitKey(0)
        cv2.destroyWindow("cam-test")
        
    fp = aquisition["file_path"]
    a = aquisition["average"]
    
    start = input("Start experiment? y/n \n")

    if start == "y":
        start_time = time.time()
        for i in range(a):
            s, img = cam.read()
            if s:    # frame captured without any errors
                filename = fp + "offset" + "_" + str(i) + ".png"
                cv2.imwrite(filename,img) #save image
            else:
                print("Grabbing offset failed.")

        next_aquisition = aquisition["time_increment"]
        end_time = aquisition["time_interval"] * 60 + min(aquisition["time_increment"], 10)
        current_time = time.time() - start_time

        while current_time<end_time:

            if current_time > next_aquisition:
                ext = str(int(current_time))
                ext = (5-len(ext))*"0" + ext
                for i in range(a):
                    s, img = cam.read()

                    if s:    # frame captured without any errors
                        filename = fp + ext + "_" + str(i) + ".png"
                        cv2.imwrite(filename,img) #save image
                next_aquisition += aquisition["time_increment"]

            current_time = time.time() - start_time

    cam.release()
    cv2.destroyAllWindows()

    image_analysis(aquisition)

if __name__ == '__main__':
    run_script()
