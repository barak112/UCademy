import cv2

def get_duration(file_path):
    cap = cv2.VideoCapture(file_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = 0
    if frame_count > 0:
        duration = frame_count / fps  # in seconds
    cap.release()
    return duration

print(get_duration("D:\\UCademy\\client\\media\\14.mp4"))
