DATASET_LIST = [
    'otb_v1.0'
]

def load(dataset, path):
    assert dataset in DATASET_LIST, 'Dataset "' + str(dataset) + '" is not supported'
    # TODO: Load dataset
