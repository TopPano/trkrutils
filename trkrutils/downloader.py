import os
import urllib
import wget
import zipfile
from .config import datasets as DATASETS
from .consts import DEFAULT_DOWNLOAD_VERBOSE, DEFAULT_DOWNLOAD_PATH

DONE_FILE_NAME = '.done'

def _download_url(url, out, verbose = DEFAULT_DOWNLOAD_VERBOSE):
    # If the file exists, do nothing
    if os.path.exists(out):
        return

    # Create a new folder is the folder of output file does not exist
    path = os.path.dirname(out)
    if not os.path.isdir(path):
        os.makedirs(path)

    # Now, download the file
    out = os.path.join(path, out)
    if not verbose:
        wget.download(url, out, bar = None)
    else:
        print 'Download {} to {}...'.format(url, out)
        wget.download(url, out)
        # The bar in wget does not have new line, we should add a new line manually
        print ""

def _unzip_file(filename, verbose = DEFAULT_DOWNLOAD_VERBOSE):
    # Print message for verbose mode
    if verbose:
        print 'Extracting {}...'.format(filename)

    # Now, extract the zipped file
    path = os.path.dirname(filename)
    zip_ref = zipfile.ZipFile(filename, 'r')
    zip_ref.extractall(path)
    zip_ref.close()

def _is_downloaded(path):
    return os.path.isdir(path) and os.path.exists(os.path.join(path, DONE_FILE_NAME))

def _mark_downloaded(path):
    open(os.path.join(path, DONE_FILE_NAME), 'w').close()

def download(dataset_name, root_path = DEFAULT_DOWNLOAD_PATH, verbose = DEFAULT_DOWNLOAD_VERBOSE):
    assert dataset_name in DATASETS.keys(), 'Dataset "{}" is not supported'.format(dataset_name)

    dataset_path = os.path.join(root_path, dataset_name)

    if dataset_name == 'otb_v1.0':
        url_prefix = DATASETS[dataset_name]['url_prefix']
        videos = DATASETS[dataset_name]['videos']
        for video in videos:
            url = '{}/{}.zip'.format(url_prefix, video)
            video_dir = os.path.join(dataset_path, video)
            zip_name = '{}.zip'.format(video_dir)
            if not _is_downloaded(video_dir):
                _download_url(url, zip_name, verbose)
                _unzip_file(zip_name, dataset_path)
                _mark_downloaded(video_dir)

    return dataset_path
