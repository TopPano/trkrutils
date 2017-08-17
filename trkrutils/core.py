import abc
import cv2
from trkrutils.consts import DEFAULT_GT_COLOR

DEFAULT_WITH_GT = True
DEFAULT_FPTS = 20

class Tracker:
    @abc.abstractmethod
    def init_frame(self, img, gt):
        '''Load initialized frame and ground truth location
        of tracked object in video'''

    @abc.abstractmethod
    def estimate(self, img):
        '''Given an image and return the estimated
        location of tracked object'''

class Region:
    @abc.abstractmethod
    def area(self):
        '''Compute the area of the bounding box'''

    @abc.abstractmethod
    def intersection(self, region):
        '''Compute the intersection area between
        this and another region'''

    # Compute the union area with this and another region
    def union(self, region):
        return self.area() + region.area() - self.intersection(region)

    def overlap_ratio(self, region):
        intersection_area = float(self.intersection(region))
        union_area = float(self.union(region))
        if union_area <= 0:
            return 0
        else:
            return intersection_area / union_area

class SpecialRegion(Region):
    # The codes for special region
    UNDEFINED = 0
    INIT = 1
    FAILURE = 2

    # Init function
    def __init__(self, code):
        self.code = code

    # The area of special region is always 0
    def area(self):
        return 0

    # The intersection  area of special regions is always 0
    def intersection(self, special_region):
        return 0

class BoundingBox(Region):
    # Init function
    def __init__(self, x1, y1, x2, y2):
        self.set(x1, y1, x2, y2)

    # Setter
    def set(self, x1, y1, x2, y2):
        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2)
        self.y2 = max(y1, y2)

    # Draw bouding box on an image
    def draw(self, img, color):
        cv2.rectangle(img, (self.x1, self.y1), (self.x2, self.y2), color, 3)

    # Compute the width of the bounding box
    def width(self):
        return self.x2 - self.x1

    # Compute the height of the bounding box
    def height(self):
        return self.y2 - self.y1

    # Compute the area of the bounding box
    def area(self):
        return self.width() * self.height()

    # Compute the intersection area between this and another bounding box
    def intersection(self, bbox):
        return max(0.0, min(self.x2, bbox.x2) - max(self.x1, bbox.x1)) * max(0.0, min(self.y2, bbox.y2) - max(self.y1, bbox.y1))

class Frame:
    # Init function
    def __init__(self, img, x1, y1, x2, y2):
        self.img = img
        self.gt = BoundingBox(x1, y1, x2, y2)

    # Get the frame with/without drawn groud truth
    def get_img(self, with_gt = DEFAULT_WITH_GT, gt_color = DEFAULT_GT_COLOR):
        if with_gt:
            self.gt.draw(self.img, gt_color)
            return self.img
        else:
            return self.img

    # Get the ground truth
    def get_gt(self):
        return self.gt

class Video:
    # Init function
    def __init__(self, dataset_name, name, path):
        self.dataset_name = dataset_name
        self.name = name
        self.path = path

    # Show an image
    def show_img(self, img, period):
        window_name = '{}/{}'.format(self.dataset_name, self.name)
        cv2.imshow(window_name, img)
        cv2.waitKey(period)

    # Load frames from disk
    def load_frames(self):
        return []

    # Show the video
    def show(self, with_gt = DEFAULT_WITH_GT, gt_color = DEFAULT_GT_COLOR, fps = DEFAULT_FPTS):
        # The period (in milliseconds) to show a frame
        frame_period = 1000 / fps
        # Load and show video frame by frame
        for frame in self.load_frames():
            self.show_img(frame.get_img(with_gt, gt_color), frame_period)

class Dataset:
    # Init function
    def __init__(self, name, path, videos):
        self.name = name
        self.path = path
        self.videos = videos

    # Get a specified video from the dataset
    def get_video(self, video_name):
        for video in self.videos:
            if video.name == video_name:
                return video
        raise Exception('Video "{}" is not in dataset "{}"'.format(video_name, self.name))

    # Get all videos from the dataset
    def get_videos(self):
        return self.videos

    # Show a specified video
    def show_video(self, video_name, with_gt = DEFAULT_WITH_GT, gt_color = DEFAULT_GT_COLOR, fps = DEFAULT_FPTS):
        self.get_video(video_name).show(with_gt, gt_color, fps)

    # Show all specified video
    def show_videos(self, with_gt = DEFAULT_WITH_GT, gt_color = DEFAULT_GT_COLOR, fps = DEFAULT_FPTS):
        for video in self.videos:
            video.show(with_gt, gt_color, fps)

class Score:
    # Init function
    def __init__(self, target_name, results = None):
        self.target_name = target_name
        self.results = dict() if results is None else results

    # Insert value of a tracker and metric
    def insert(self, tracker_name, metric_name, metric_value):
        if metric_name not in self.results:
            self.results[metric_name] = dict()
        self.results[metric_name][tracker_name] = metric_value

    # Get value of a specified tracker and metric
    def get_val(self, tracker_name, metric_name):
        if metric_name in self.results and tracker_name in self.results[metric_name]:
            return self.results[metric_name][tracker_name]
        return None

    # Get list of all metrics names
    def get_metrics(self):
        return self.results.iterkeys()
