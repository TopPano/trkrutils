from trkrutils.consts import DEFAULT_ESTIMATED_COLOR, DEFAULT_GT_COLOR
from trkrutils.core import Score, SpecialRegion
from trkrutils.estimator import estimate_success_plot, estimate_ar_plot

DEFAULT_VISUALIZED = False
DEFAULT_WAIT_PREIOD = 1

DEFAULT_STOCHASTIC = False
DEFAULT_STOCHASTIC_REPETITIONS = 15
DEFAULT_DETERMINISTIC_REPETITIONS = 1

DEFAULT_RESET = True
DEFAULT_FAILURE_THRESHOLD = 0.0
DEFAULT_REINITIALIZE_STEP = 10

METRICS = [
    'success_plot',
    'ar_plot'
]

class _Experiment:
    # Init function
    def __init__(self, settings = {}):
        self.settings = settings
        self.metrics = []

    # Insert a metric
    def insert_metric(self, metric):
        if metric not in self.metrics:
            self.metrics.append(metric)

def _reshape_list(scores, tracker_name, metric, value_name, repetitions):
    reshaped_list = [[] for x in range(repetitions)]

    for score in scores:
        value_list = score.get_val(tracker_name, metric)[value_name]
        for idx, value in enumerate(value_list):
            reshaped_list[idx].extend(value)

    return reshaped_list

def _run_tracker(
    tracker,
    video,
    reset = DEFAULT_RESET,
    failure_threshold = DEFAULT_FAILURE_THRESHOLD,
    reinitialize_step = DEFAULT_REINITIALIZE_STEP,
    visualized = DEFAULT_VISUALIZED,
    gt_color = DEFAULT_GT_COLOR,
    estimated_color = DEFAULT_ESTIMATED_COLOR,
    wait_preiod = DEFAULT_WAIT_PREIOD):

    # Check the values of failure_threshold and reinitialize_step
    if reset:
        assert failure_threshold >= 0.0, 'Failure threshold must be >= 0.0, but get {}'.format(failure_threshold)
        assert reinitialize_step >= 0, 'Reinitialize step must be >= 0, but get {}'.format(reinitialize_step)

    trajectory = []
    overlap_ratios = []
    is_init = False
    rest_step = 0

    # Load the video frame by frame
    frames = video.load_frames()
    for idx, frame in enumerate(frames):
        img = frame.get_img(with_gt = False)
        gt = frame.get_gt()
        overlap_ratio = float('nan')

        if not is_init:
            # (Re-)Initialize with the frame and ground truth
            tracker.init_frame(img, gt)
            is_init = True
            # Assign the region to be a special region for initialization
            region = SpecialRegion(SpecialRegion.INIT)
        elif reset and (rest_step > 0):
            # It is after a failure, just skip the frame
            rest_step -= 1
            if rest_step == 0:
                is_init = False
            # Assign the region to be a undefined special region
            region = SpecialRegion(SpecialRegion.UNDEFINED)
        else:
            estimated_region = tracker.estimate(img)
            _overlap_ratio = gt.overlap_ratio(estimated_region)
            if reset and (_overlap_ratio <= failure_threshold):
                # Failure detected
                if reinitialize_step > 0:
                    # Skip some frames after failure
                    rest_step = reinitialize_step
                else:
                    # If reinitialize_step is zero, skip all the rest frames
                    rest_step = len(frames) - reinitialize_step - 1
                # Assign the region to be a special region for failure
                region = SpecialRegion(SpecialRegion.FAILURE)
            else:
                # Assign the region to be the estimated region
                region = estimated_region
                overlap_ratio = _overlap_ratio
                if visualized:
                    gt.draw(img, gt_color)
                    estimated_region.draw(img, estimated_color)
                    video.show_img(img, wait_preiod)

        trajectory.append(region)
        overlap_ratios.append(overlap_ratio)

    return trajectory, overlap_ratios

def eval_video(
    trackers,
    video,
    metrics = METRICS,
    stochastic = DEFAULT_STOCHASTIC,
    visualized = DEFAULT_VISUALIZED,
    gt_color = DEFAULT_GT_COLOR,
    estimated_color = DEFAULT_ESTIMATED_COLOR,
    wait_preiod = DEFAULT_WAIT_PREIOD):
    score = Score(video.name, 'video')
    repetitions = DEFAULT_STOCHASTIC_REPETITIONS if stochastic else DEFAULT_DETERMINISTIC_REPETITIONS
    experiments = [
        # Experiment for success_plot
        _Experiment(settings = {'reset': False}),
        # Experiment for ar_plot
        _Experiment(settings = {'reset': True}),
    ]

    for metric in metrics:
        if metric == 'success_plot':
            experiments[0].insert_metric(metric)
        elif metric == 'ar_plot':
            experiments[1].insert_metric(metric)
        else:
            raise ValueError('Metric "{}" is not supported'.format(metric))

    # Loop over all trackers
    for tracker in trackers:
        for experiment in experiments:
            if len(experiment.metrics) > 0:
                reset = experiment.settings['reset']
                trajectory_list = []
                overlap_ratios_list = []
                for i in range(repetitions):
                    trajectory, overlap_ratios = _run_tracker(
                        tracker,
                        video,
                        reset = reset,
                        visualized = visualized,
                        gt_color = gt_color,
                        estimated_color = estimated_color,
                        wait_preiod = wait_preiod)
                    trajectory_list.append(trajectory)
                    overlap_ratios_list.append(overlap_ratios)

            # Insert result
            tracker_name = tracker.__class__.__name__
            for metric in experiment.metrics:
                if metric == 'success_plot':
                    value = estimate_success_plot(overlap_ratios_list)
                elif metric == 'ar_plot':
                    value = estimate_ar_plot(overlap_ratios_list, trajectory_list)
                score.insert(tracker_name, metric, value)

    return [score]

def eval_dataset(
    trackers,
    dataset,
    metrics = METRICS,
    stochastic = DEFAULT_STOCHASTIC,
    visualized = DEFAULT_VISUALIZED,
    gt_color = DEFAULT_GT_COLOR,
    estimated_color = DEFAULT_ESTIMATED_COLOR,
    wait_preiod = DEFAULT_WAIT_PREIOD):
    repetitions = DEFAULT_STOCHASTIC_REPETITIONS if stochastic else DEFAULT_DETERMINISTIC_REPETITIONS
    scores = []

    for video in dataset.get_videos():
        score = eval_video(trackers, video, metrics, stochastic, visualized, gt_color, estimated_color, wait_preiod)
        scores.extend(score)

    overall_score = Score(dataset.name, 'dataset')
    for metric in metrics:
        for tracker in trackers:
            tracker_name = tracker.__class__.__name__
            if metric == 'success_plot':
                overlap_ratios_list = _reshape_list(scores, tracker_name, metric, 'overlap_ratios_list', repetitions)
                value = estimate_success_plot(overlap_ratios_list)
                overall_score.insert(tracker_name, metric, value)
            elif metric == 'ar_plot':
                overlap_ratios_list = _reshape_list(scores, tracker_name, metric, 'overlap_ratios_list', repetitions)
                trajectory_list = _reshape_list(scores, tracker_name, metric, 'trajectory_list', repetitions)
                value = estimate_ar_plot(overlap_ratios_list, trajectory_list)
                overall_score.insert(tracker_name, metric, value)
            else:
                raise ValueError('Metric "{}" is not supported'.format(metric))

    scores = [overall_score] + scores

    return scores

def eval(
    trackers,
    dataset,
    metrics = METRICS,
    stochastic = DEFAULT_STOCHASTIC,
    video_name = None,
    visualized = DEFAULT_VISUALIZED,
    gt_color = DEFAULT_GT_COLOR,
    estimated_color = DEFAULT_ESTIMATED_COLOR,
    wait_preiod = DEFAULT_WAIT_PREIOD):
    if video_name is not None:
        return eval_video(trackers, dataset.get_video(video_name), metrics, stochastic, visualized, gt_color, estimated_color, wait_preiod)
    else:
        return eval_dataset(trackers, dataset, metrics, stochastic, visualized, gt_color, estimated_color, wait_preiod)
