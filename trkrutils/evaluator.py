from trkrutils.consts import DEFAULT_ESTIMATED_COLOR, DEFAULT_GT_COLOR
from trkrutils.core import Score

DEFAULT_VISUALIZED = False
DEFAULT_WAIT_PREIOD = 1
METRICS = [
    'success_plot'
]

def compute_success_plot_score(overlap_scores):
    curr_threshold = 0.0
    thresholds = [curr_threshold]
    success_rates = []

    # Sort the overlapp scores for computing success rates and thresholds
    sorted_overlap_scores = sorted(overlap_scores)
    # Compute success rates and thresholds
    total_count = len(overlap_scores)
    for idx, overlap_score in enumerate(sorted_overlap_scores):
        if curr_threshold < overlap_score:
            success_rates.append(float(total_count - idx) / float(total_count))
            curr_threshold = overlap_score
            thresholds.append(curr_threshold)
    # Handle edge cases
    if len(thresholds) > 1:
        thresholds[-1] = 1.0
        success_rates.append(0.0)
    else:
        thresholds.append(1.0)
        success_rates.extend([0.0, 0.0])

    # Compute auc (area under curve)
    auc = 0.0
    for idx in range(1, len(thresholds)):
        base = thresholds[idx] - thresholds[idx - 1]
        height = (success_rates[idx] + success_rates[idx - 1]) / 2.0
        auc += base * height

    return {
        'overlap_scores': overlap_scores,
        'thresholds': thresholds,
        'success_rates': success_rates,
        'auc': auc
    }

def eval_video(
    trackers,
    video,
    metrics = METRICS,
    visualized = DEFAULT_VISUALIZED,
    gt_color = DEFAULT_GT_COLOR,
    estimated_color = DEFAULT_ESTIMATED_COLOR,
    wait_preiod = DEFAULT_WAIT_PREIOD):
    score = Score(video.name)

    # Loop over all trackers
    for tracker in trackers:
        overlap_scores = []

        # Load and evalute video frame by frame
        for idx, frame in enumerate(video.load_frames()):
            img = frame.get_img(with_gt = False)
            gt = frame.get_gt()
            if idx == 0:
                # Setup first frame
                tracker.load_first_frame(img, gt)
            else:
                # Estimate the rest frames
                estimated_bbox = tracker.estimate(img)
                estimated_area = estimated_bbox.area()
                gt_area = gt.area()
                intersection_area = gt.intersection(estimated_bbox)
                union_area = estimated_area + gt_area - intersection_area
                overlap_score = float(intersection_area) / float(union_area)
                overlap_scores.append(overlap_score)
                if visualized:
                    gt.draw(img, gt_color)
                    estimated_bbox.draw(img, estimated_color)
                    video.show_img(img, wait_preiod)

        # Insert result
        tracker_name = tracker.__class__.__name__
        for metric in metrics:
            value = None
            if metric == 'success_plot':
                value = compute_success_plot_score(overlap_scores)
            else:
                # TODO
                '''Handle non-existed metric'''
            if value is not None:
                score.insert(tracker_name, metric, value)

    return score

def eval_dataset(
    trackers,
    dataset,
    metrics = METRICS,
    visualized = DEFAULT_VISUALIZED,
    gt_color = DEFAULT_GT_COLOR,
    estimated_color = DEFAULT_ESTIMATED_COLOR,
    wait_preiod = DEFAULT_WAIT_PREIOD):
    scores = []

    for video in dataset.get_videos():
        score = eval_video(trackers, video, metrics, visualized, gt_color, estimated_color, wait_preiod)
        scores.append(score)

    overall_score = Score(dataset.name)
    for metric in metrics:
        if metric == 'success_plot':
            for tracker in trackers:
                tracker_name = tracker.__class__.__name__
                overall_overlap_scores = []
                for score in scores:
                    overall_overlap_scores.extend(score.get_val(tracker_name, metric)['overlap_scores'])
                value = compute_success_plot_score(overall_overlap_scores)
                overall_score.insert(tracker_name, metric, value)
        else:
            # TODO
            '''Handle non-existed metric'''
    scores = [overall_score] + scores

    return scores

def eval(
    trackers,
    dataset,
    metrics = METRICS,
    video_name = None,
    visualized = DEFAULT_VISUALIZED,
    gt_color = DEFAULT_GT_COLOR,
    estimated_color = DEFAULT_ESTIMATED_COLOR,
    wait_preiod = DEFAULT_WAIT_PREIOD):
    if video_name is not None:
        return eval_video(trackers, dataset.get_video(video_name), metrics, visualized, gt_color, estimated_color, wait_preiod)
    else:
        return eval_dataset(trackers, dataset, metrics, visualized, gt_color, estimated_color, wait_preiod)
