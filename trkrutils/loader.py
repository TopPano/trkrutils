import os
import cv2

import downloader
from .core import Frame, Video, Dataset
from .consts import DEFAULT_DOWNLOAD_VERBOSE

DATASET_LIST = [
    'otb_v1.0'
]

class OTBVideo(Video):
    # Init function
    def __init__(self, dataset_name, name, path):
        Video.__init__(self, dataset_name, name, path)

    # Load frames from disk
    def load_frames(self):
        frames = []

        # Load the groundtruth file
        gt_file = open(os.path.join(self.path, 'groundtruth_rect.txt')).readlines()

        # Load images from folder and bounding boxes from the groudtruth file
        spliter = ','
        for idx, gt in enumerate(gt_file):
            # Format of each bounding box one of following:
            # x,y,box_width,box_height
            # x\ty\tbox_width\tbox_height
            pos = gt.split(spliter)
            if len(pos) != 4:
                spliter = '\t'
                pos = gt.split(spliter)
            pos = [int(x) for x in pos]
            # Image is in the "img" folder and start from "0001.jpg"
            img_path = os.path.join(self.path, 'img', '{:04d}.jpg'.format(idx + 1))
            img = cv2.imread(img_path)
            # Now add the new frame to the list
            frames.append(Frame(img, pos[0], pos[1], pos[0] + pos[2], pos[1] + pos[3]))

        return frames

def load(dataset_name, path = None, verbose = DEFAULT_DOWNLOAD_VERBOSE):
    assert dataset_name in DATASET_LIST, 'Dataset "{}" is not supported'.format(dataset_name)

    dataset_path = downloader.download(dataset_name, verbose = verbose) if path is None else path

    video_class = Video
    videos_info = []

    if dataset_name.startswith('otb'):
        video_class = OTBVideo
        for video_name in os.listdir(dataset_path):
            video_path = os.path.join(dataset_path, video_name)
            if os.path.isdir(video_path):
                videos_info.append((video_name, video_path))

    videos = [video_class(dataset_name, info[0], info[1]) for info in videos_info]

    return Dataset(dataset_name, dataset_path, videos)
