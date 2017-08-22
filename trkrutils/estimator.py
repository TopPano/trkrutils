import math
from trkrutils.utils import mean, merge_dict
from trkrutils.core import SpecialRegion

DEFAULT_SENSITIVITY = 100

DEFAULT_PRECISION_MAX_THRESHOLD = 50
DEFAULT_PRECISION_SCORE_THRESHOLD = 20

def _compute_per_frame_ratios(overlap_ratios_list):
    per_frame_ratios = []

    # Compute per-frame overlap ratio by averaging the frame in different sequence
    # XXX: We assume the list contains at least 1 sequence and all sequence have the same length
    for frame_idx in range(len(overlap_ratios_list[0])):
        ratios = []
        for sequence_idx in range(len(overlap_ratios_list)):
            overlap_ratio = overlap_ratios_list[sequence_idx][frame_idx]
            if not math.isnan(overlap_ratio):
                ratios.append(overlap_ratio)
        if len(ratios) > 0:
            per_frame_ratio = mean(ratios)
            per_frame_ratios.append(per_frame_ratio)

    return per_frame_ratios

def estimate_success_plot(overlap_ratios_list):
    per_frame_ratios = _compute_per_frame_ratios(overlap_ratios_list)
    curr_threshold = 0.0
    thresholds = [curr_threshold]
    success_rates = []

    # Sort the overlapp scores for computing success rates and thresholds
    sorted_per_frame_ratios = sorted(per_frame_ratios)
    # Compute success rates and thresholds
    total_count = len(per_frame_ratios)
    for idx, per_frame_ratio in enumerate(sorted_per_frame_ratios):
        if curr_threshold < per_frame_ratio:
            success_rates.append(float(total_count - idx) / float(total_count))
            curr_threshold = per_frame_ratio
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
        'thresholds': thresholds,
        'success_rates': success_rates,
        'auc': auc,
        'per_frame_ratios': per_frame_ratios,
        'overlap_ratios_list': overlap_ratios_list
    }

def estimate_precision_plot(
    center_distances_list,
    max_threshold = DEFAULT_PRECISION_MAX_THRESHOLD,
    score_threshold = DEFAULT_PRECISION_SCORE_THRESHOLD):
    per_frame_distances = _compute_per_frame_ratios(center_distances_list)
    thresholds = range(max_threshold + 1)
    precisions = []

    # Compute the precision for each threshold
    for threshold in thresholds:
        precision = float(len([d for d in per_frame_distances if d < threshold])) / len(per_frame_distances)
        precisions.append(precision)

    # Get the precision score, which is the precision under score_threshold
    precision_score = precisions[score_threshold]

    return {
        'thresholds': thresholds,
        'precisions': precisions,
        'precision_score': precision_score,
        'max_threshold': max_threshold,
        'score_threshold': score_threshold,
        'per_frame_distances': per_frame_distances,
        'center_distances_list': center_distances_list
    }

def estimate_accuracy(overlap_ratios_list):
    per_frame_ratios = _compute_per_frame_ratios(overlap_ratios_list)
    accuracy = mean(per_frame_ratios)

    return {
        'accuracy': accuracy,
        'per_frame_ratios': per_frame_ratios,
        'overlap_ratios_list': overlap_ratios_list
    }

def estimate_robustness(trajectory_list, sensitivity = DEFAULT_SENSITIVITY):
    failures_rate_list = []
    # XXX: We assume the list contains at least 1 sequence and all sequence have the same length
    trajectory_len = len(trajectory_list[0])

    # Compute failures and failure rate for each sequence
    for trajectory in trajectory_list:
        failures = len([region for region in trajectory if isinstance(region, SpecialRegion) and (region.code == SpecialRegion.FAILURE)])
        failures_rate_list.append(float(failures) / trajectory_len)

    avg_failures_rate = mean(failures_rate_list)
    reliability = math.exp(-sensitivity * avg_failures_rate)

    return {
        'reliability': reliability,
        'avg_failures_rate': avg_failures_rate,
        'sensitivity': sensitivity,
        'trajectory_list': trajectory_list
    }

def estimate_ar_plot(overlap_ratios_list, trajectory_list):
    accuracy = estimate_accuracy(overlap_ratios_list)
    robustness = estimate_robustness(trajectory_list)

    return merge_dict(accuracy, robustness)
