import cv2

DEFAULT_WITH_GT = True
DEFAULT_GT_COLOR = (255, 255, 255)
DEFAULT_FPTS = 20

class BoundingBox:
    # Init function
    def __init__(self, x1, y1, x2, y2):
        self.set(x1, y1, x2, y2)

    # Setter
    def set(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    # Draw bouding box on an image
    def draw(self, img, color):
        cv2.rectangle(img, (self.x1, self.y1), (self.x2, self.y2), color, 3)

class Frame:
    # Init function
    def __init__(self, img, x1, y1, x2, y2):
        self.img = img
        self.gt = BoundingBox(x1, y1, x2, y2)

    # Get the frame with/without drawn groud truth
    def get(self, with_gt = DEFAULT_WITH_GT, gt_color = DEFAULT_GT_COLOR):
        if with_gt:
            self.gt.draw(self.img, gt_color)
            return self.img
        else:
            return self.img

class Video:
    # Init function
    def __init__(self, dataset_name, name, path):
        self.dataset_name = dataset_name
        self.name = name
        self.path = path

    # Load frames from disk
    def load_frames(self):
        return []

    # Show the video
    def show(self, with_gt = DEFAULT_WITH_GT, gt_color = DEFAULT_GT_COLOR, fps = DEFAULT_FPTS):
        window_name = '{}/{}'.format(self.dataset_name, self.name)
        # The period (in milliseconds) to show a frame
        frame_period = 1000 / fps
        # Load and show video frame by frame
        for frame in self.load_frames():
            cv2.imshow(window_name, frame.get(with_gt, gt_color))
            cv2.waitKey(frame_period)

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
