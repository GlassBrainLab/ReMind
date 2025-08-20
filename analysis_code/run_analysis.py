# -*- coding: utf-8 -*-
"""
This is the main function that calls moduels and extracts eye features.   

Created on 10/29/24 by HS

"""
import glob
import argparse
import numpy as np
import src.extract_eye_features as ef
import warnings
warnings.simplefilter("error", RuntimeWarning)

def main(sub_id, win_type, task_type, alpha):
    # define raw data path
    # change this to your folder path
    data_path = r"/Users/hsun11/Desktop/raw_data"

    # Get list of subject folders or create single subject folder path
    if sub_id == 'all':
        # get all subject folders in the root path
        subject_folders = glob.glob(f'{data_path}/s[0-9]*')
    else:
        subject_folders = [f'{data_path}/s{sub_id}']
    
    # Determine the window types to process
    if win_type == 'all':
        win_types = ['default', 'mw_fixed', 'page_fixed', 'end2', 'end5']
        # win_types = ['default', 'mw_fixed', 'page_fixed', 'end5']
        # win_types = ['mw_fixed', 'page_fixed', 'end5', 'end2']
    elif win_type == 'slide':
        # win_types = ['slide2.0', 'slide5.0']
        win_types = [f"slide{w}" for w in np.arange(1, 6.5, 0.5)]
    else:
        win_types = [win_type]

    # determine the task type to process
    # for sliding window approach, ignore task type
    if 'slide' in win_type:
        task_type = 'sr'
        
    valid_types = ['sr', 'tp', 'both']
    if task_type not in valid_types:
        raise ValueError(f"Invalid task_type: '{task_type}'. Must be one of {valid_types}")
    if task_type == 'both':
        task_types = ['sr', 'tp']
    else:
        task_types = [task_type]
    
    # loop through individual subject, each window type, and task type
    for sub_folder in subject_folders:
        for win in win_types:
            for task_type in task_types:
                ef.extract_subject_features(sub_folder, win, task_type, alpha)

    return


if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Extract eye features for specified subjects.")
    parser.add_argument(
        "--sub_id", 
        type=str, 
        default="all", 
        help="Subject ID to extract features for (use 'all' for all subjects)"
    )
    parser.add_argument(
        "--win_type", 
        type=str, 
        default="all", 
        help="Window type for feature extraction"
    )
    parser.add_argument(
        "--task_type", 
        type=str, 
        default="both", 
        help="Task type (sr: self-report / tp: though-probe) for feature extraction"
    )

    parser.add_argument(
        "--alpha", 
        type=float, 
        default=2.0, 
        help="Response time to exclude at the end of each page"
    )

    # Parse arguments
    args = parser.parse_args()

    # Call main with parsed arguments
    main(sub_id=args.sub_id, win_type=args.win_type, task_type=args.task_type, alpha=args.alpha)