import os
import cv2

import downloader
from trkrutils.core import Frame, Video, Dataset
from trkrutils.config import datasets as DATASETS
from trkrutils.consts import DEFAULT_DOWNLOAD_VERBOSE

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

class VOTVideo(Video):
    # Init function
    def __init__(self, dataset_name, name, path):
        Video.__init__(self, dataset_name, name, path)

    # Load frames from disk
    def load_frames(self):
        frames = []

        # Load the groundtruth file
        gt_file = open(os.path.join(self.path, 'groundtruth.txt')).readlines()

        # Load images from folder and bounding boxes from the groudtruth file
        spliter = ','
        for idx, gt in enumerate(gt_file):
            # Format of bounding box:
            # x1, y1, x2, y2, x3, y3, x4, y4
            # TODO: Use rotated rectangle
            pos = gt.split(spliter)
            pos = [int(float(x)) for x in pos]
            x1, y1 = pos[0], pos[1]
            x2, y2 = pos[2], pos[3]
            x3, y3 = pos[4], pos[5]
            x4, y4 = pos[6], pos[7]
            # Image is in the "img" folder and start from "00000001.jpg"
            img_path = os.path.join(self.path, '{:08d}.jpg'.format(idx + 1))
            img = cv2.imread(img_path)
            # Now add the new frame to the list
            frame = Frame(
                img,
                min(x1, x2, x3, x4) - 1,
                min(y1, y2, y3, y4) - 1,
                max(x1, x2, x3, x4) - 1,
                max(y1, y2, y3, y4) - 1
            )
            frames.append(frame)

        return frames

def load(dataset_name, path = None, verbose = DEFAULT_DOWNLOAD_VERBOSE):
    assert dataset_name in DATASETS.keys(), 'Dataset "{}" is not supported'.format(dataset_name)

    dataset_path = downloader.download(dataset_name, verbose = verbose) if path is None else path

    video_class = Video
    videos_info = []

    if dataset_name.startswith('otb'):
        video_class = OTBVideo
    elif dataset_name.startswith('vot'):
        video_class = VOTVideo

    for video_name in os.listdir(dataset_path):
        video_path = os.path.join(dataset_path, video_name)
        if os.path.isdir(video_path):
            videos_info.append((video_name, video_path))

    videos = [video_class(dataset_name, info[0], info[1]) for info in videos_info]

    return Dataset(dataset_name, dataset_path, videos)
