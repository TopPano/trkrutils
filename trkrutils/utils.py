def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

def merge_dict(dict0, dict1):
    result = dict0.copy()
    result.update(dict1)
    return result
