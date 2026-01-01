#
# Created 8/15/18 by DJ.
# Modified 10/26/22 by HS -- Update image dimensions
#                         -- Implement a dataframe in words_of_pages
# Modified 10/10/23 by HS - update words_of_pages function
# Updated on 10/31/23 by HS - directly read in eye features if they have alraedy
#                           - been parsed and saved
# Updated on 2/13/24 by HS - use eye samples for pupil analyses
# Updated 4/16/24 by HS - interpolate pupil size during blink
# 
# New script name: utils.py
# The script now contains all helper functions that parse and load data, analyze features, and 
# convert units among different coordinate systems. 
# Created 11/7/24 by HS
# updated 12/29/25 by HS - modify interpolate_blink function to use saccades that overlap blinks

# Import packages
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import warnings

def preprocess_pupil(dfSamples, dfBlink, dfSaccade):
    """
    Run a standard pupil preprocessing pipeline on raw sample data.

    Steps performed:
    - Interpolate pupil (and position) values across blink periods using
      saccade boundaries via `interpolate_blink`.
    - Detect rapid drops (dips) in the left and right pupil traces and
      interpolate over those regions using `detect_and_interpolate_dips`.
    - Remove outliers from each pupil trace using `remove_outliers`.

    Parameters
    ----------
    dfSamples : pandas.DataFrame
        Sample-level eye data containing at minimum the columns
        `tSample`, `LPupil`, `RPupil`, `LX`, `LY`, `RX`, `RY`, etc.
    dfBlink : pandas.DataFrame
        Blink events with columns `tStart`, `tEnd`, and `eye`.
    dfSaccade : pandas.DataFrame
        Saccade events with columns `tStart`, `tEnd`, and `eye` used to
        determine interpolation boundaries.

    Returns
    -------
    pandas.DataFrame
        A copy of `dfSamples` with `LPupil` and `RPupil` cleaned in-place.

    Notes
    -----
    This function modifies and returns the provided samples dataframe; it
    does not create a separate deep copy before processing.
    """
    # interpolate blink
    dfSamples = interpolate_blink(dfSamples, dfBlink, dfSaccade)

    # remove dips and outliers
    LPupil = dfSamples['LPupil']
    LPupil = detect_and_interpolate_dips(LPupil)
    dfSamples['LPupil'] = remove_outliers(LPupil)

    RPupil = dfSamples['RPupil']
    RPupil = detect_and_interpolate_dips(RPupil)
    dfSamples['RPupil'] = remove_outliers(RPupil)

    return dfSamples



def truncate_df_by_time(dfSamples, dfFix, dfSacc, dfBlink, win_start, win_end):
    """
    Truncate multiple event/sample dataframes to a common time window.

    Parameters
    ----------
    dfSamples : pandas.DataFrame
        Sample-level eye data containing a `tSample` column (milliseconds).
    dfFix : pandas.DataFrame
        Fixation events with `tStart` and `tEnd` in milliseconds.
    dfSacc : pandas.DataFrame
        Saccade events with `tStart` and `tEnd` in milliseconds.
    dfBlink : pandas.DataFrame
        Blink events with `tStart` and `tEnd` in milliseconds.
    win_start : float
        Window start time in seconds (converted to ms inside function).
    win_end : float
        Window end time in seconds (converted to ms inside function).

    Returns
    -------
    tuple
        Filtered `(dfSamples, dfFix, dfSacc, dfBlink)` where every row in
        each dataframe falls fully within the requested window.
    """

    # blinks
    blink_indices = (dfBlink['tStart'] >= win_start*1000) & \
                    (dfBlink['tEnd'] <= win_end*1000)
    dfBlink = dfBlink.loc[blink_indices].copy()

    # fixatoins
    fix_indices = (dfFix['tStart'] >= win_start*1000) & \
                    (dfFix['tEnd'] <= win_end*1000)
    dfFix = dfFix.loc[fix_indices].copy()

    # saccades
    sacc_indices = (dfSacc['tStart'] >= win_start*1000) & \
                    (dfSacc['tEnd'] <= win_end*1000)
    dfSacc = dfSacc.loc[sacc_indices].copy()
    
    # eye samples (pupil info)
    pupil_indices = (dfSamples['tSample'] >= win_start*1000) & \
                    (dfSamples['tSample'] <= win_end*1000)
    dfSamples = dfSamples.loc[pupil_indices].copy()

    return dfSamples, dfFix, dfSacc, dfBlink


def calc_interblink_interval(dfSamples, dfBlink):
    """
    Calculate the interblink interval (IBI) and interpolate it over a given time series.

    Parameters:
    -----------
    dfSamples 
        DataFrame containing the samples with a 'tSample' column representing the time (in milliseconds).

    dfBlink 
        DataFrame containing blink data with columns 'tStart', 'tEnd', and 'eye'.
        - 'tStart': Blink start time (in milliseconds).
        - 'tEnd': Blink end time (in milliseconds).
        - 'eye': Eye identifier (use 'R' for the right eye).

    Returns:
    --------
        Updated dfSamples with an additional column 'interblink_interval' containing the interpolated IBI values.

    """
    # Use right eye's blink information
    dfBlink = dfBlink[dfBlink['eye'] == 'R']

    # Calculate the blink time as the midpoint between start and end
    blink_time = (dfBlink['tStart'] + dfBlink['tEnd']) / 2

    # Compute interblink interval (IBI) in seconds
    ibi = blink_time.diff() / 1000

    # Build a Series indexed by blink times
    ibi_series = pd.Series(ibi.values, index=blink_time.values).sort_index()

    # Create a Series indexed by tSample (sample timestamps)
    new_times = dfSamples['tSample']
    ibi_interp = (
        ibi_series.reindex(new_times, method='ffill')  # forward fill
                .bfill()                            # optional: fill initial NaNs
                .values
    )

    # Step 5: Assign to dfSamples
    dfSamples['interblink_interval'] = ibi_interp

    return dfSamples


def interpolate_blink(dfSamples, dfBlink, dfSaccade):
    """
    Interpolate left and right pupil sizes over blink periods. Modifies the
    dataframe of samples in place to change pupil dilation values to interpolated
    values, effectively removing blink artifacts. Saves interpolated data as csv.
    
    Uses saccades as t1 and t4. Contains adjustments recommended through conversation
    with Dr. J. Performs the interpolation over the normalized pupil dilation values.
    
    Parameters
    ----------
    dfSamples : pandas.DataFrame
        Sample-level eye data containing timestamp column `tSample` and
        columns for each eye named like `LX`, `LY`, `LPupil`, `RX`, `RY`, `RPupil`.
    dfBlink : pandas.DataFrame
        Blink events with columns `tStart`, `tEnd`, and `eye` (values 'L'/'R').
    dfSaccade : pandas.DataFrame
        Saccade events with columns `tStart`, `tEnd`, and `eye` used to
        identify saccades that overlap or surround blinks.

    Returns
    -------
    pandas.DataFrame
        The input `dfSamples` with pupil and position columns replaced by
        interpolated values during blink-related intervals.

    Notes
    -----
    - Interpolation points are chosen using saccades that overlap the blink
      when available; otherwise the nearest surrounding saccades are used.
    - Interpolation is performed independently for position (`X`,`Y`) and
      pupil size columns for each eye.
    """
    # extracted from reading_analysis.py (author: HS)
    # interpolate the pupil size during the blink duration
    # http://dx.doi.org/10.6084/m9.figshare.688002
    

    # get time array from dfSamples
    sample_time = dfSamples['tSample'].to_numpy()

    # interpolate data for LEFT and RIGHT eye separately
    for eye in ['L', 'R']:
        # extract blink and saccade information for one eye
        dfBlink_ = dfBlink[dfBlink['eye']==eye]
        dfSaccade_ = dfSaccade[dfSaccade['eye']==eye]

        # truncate blink dataframe using the saccade information
        t_start = dfSaccade_['tStart'].min()
        t_end = dfSaccade_['tEnd'].max()
        mask = (dfBlink_['tStart'] > t_start) & (dfBlink_['tEnd'] < t_end)
        dfBlink_ = dfBlink_[mask]

        # convert df columns to np.arrays for interpolation
        col_names = [f'{eye}X', f'{eye}Y', f'{eye}Pupil']
        data_to_interpolate = []
        for col_name in col_names:
            data_to_interpolate.append(np.array(dfSamples[col_name]))

        # iterate throu each row of blink dataframe
        for index in np.arange(len(dfBlink_)):
            row = dfBlink_.iloc[index]
            # get the start and end time
            b_start = row['tStart'] 
            b_end = row['tEnd']
            # skip blinks out of range of dfSamples
            if (b_start < sample_time[0]) and (b_end > sample_time[-1]):
                continue
            
            # commented out by HS on 12/29/2025
            # # set t1 to be the end time of the last saccade before the blink
            # #get all saccades before this blink
            # previous_sac = dfSaccade_[dfSaccade_["tEnd"] < b_start]
            # # get last saccade before this blink
            # t1 = previous_sac["tEnd"].max()
            # # set t2 to be the start time of the first saccade after the blink
            # # get all saccades after this blink
            # after_sac = dfSaccade_[dfSaccade_["tStart"] > b_end]
            # # get the first saccade after this blink
            # t2 = after_sac["tStart"].min()

            # 12/29/2025 - added by HS
            # set t1 and t2 to be the start and end time of the saccade that surrounds the blink
            # this is to avoid the long fixation between saccades that may lead to large interpolation errors

            # saccades that overlap the blink
            sac = dfSaccade_[
                (dfSaccade_["tStart"] < b_start) &
                (dfSaccade_["tEnd"] > b_end)
            ]

            if not sac.empty:
                # use overlapping saccade
                t1 = sac["tStart"].iloc[-1]
                t2 = sac["tEnd"].iloc[-1]

            else:
                warnings.warn(
                    f"No saccade overlaps blink window [{b_start}, {b_end}]. "
                    "Using nearest surrounding saccades instead.",
                    UserWarning
                )
                # previous saccade before blink
                previous_sac = dfSaccade_[dfSaccade_["tEnd"] < b_start]
                if previous_sac.empty:
                    t1 = np.nan
                    raise ValueError("t1 are Na")
                else:
                    t1 = previous_sac["tEnd"].max()

                # first saccade after blink
                after_sac = dfSaccade_[dfSaccade_["tStart"] > b_end]
                if after_sac.empty:
                    t2 = np.nan
                    raise ValueError("t2 are Na")
                else:
                    t2 = after_sac["tStart"].min()

            # check for missing vals in t1 or t2 and use fallback if needed
            # if pd.isna(t1) or pd.isna(t2):
            #     raise ValueError("t1/t2 are Na")
            
            # check the timing of saccades are within the time array for samples
            if (t1 > sample_time[0]) and (t2 < sample_time[-1]):
                # choose data points for interpolation function
                x = [t1,t2]
                y_ind = []
                for t in x:
                    y_ind.append(np.where(sample_time==t)[0][0])

                # loop thru all columns
                for col_name, col_data in zip(col_names, data_to_interpolate):
                    # create the 1D function for interpolation
                    y = col_data[y_ind]
                    interp_f = interp1d(x, y)           
                    #spl = CubicSpline(x, y)
                    
                    # generate mask for blink duration
                    mask = (sample_time > t1) & (sample_time < t2)
                    time_to_interpolate = sample_time[mask]
                    # use spl model to interpolate data during blink duration
                    interp_data = interp_f(time_to_interpolate)
                    
                    # update the dfSamples in place
                    dfSamples.loc[mask, col_name] = interp_data

    return dfSamples


def detect_and_interpolate_dips(signal, v_thresh=800, max_duration=0.01, fs=1000):
    """
    Detect rapid amplitude drops (dips) in a 1D time series and interpolate
    over the detected dip regions.

    Parameters
    ----------
    signal : array_like
        1D array of pupil (or other) data samples.
    v_thresh : float, optional
        Velocity threshold (units per second) used to consider a sample as a
        rapid drop or rise. Defaults to 800.
    max_duration : float, optional
        Maximum allowed dip duration in seconds. Dips longer than this are
        ignored. Defaults to 0.01 (10 ms).
    fs : int, optional
        Sampling frequency in Hz. Defaults to 1000.

    Returns
    -------
    tuple
        `(cleaned_signal, dip_mask)` where `cleaned_signal` is a 1D numpy
        array with dip regions replaced by linear interpolation, and
        `dip_mask` is a boolean array marking the interpolated regions.
    """
    t_sample = np.arange(len(signal)) / fs
    dt = 1 / fs
    margin = 5

    # Velocity
    velocity = np.gradient(signal) / dt

    drop_idxs = np.where(velocity < -v_thresh)[0]
    rise_idxs = np.where(velocity > v_thresh)[0]

    dip_mask = np.zeros_like(signal, dtype=bool)
    used = np.zeros_like(signal, dtype=bool)
    max_samples = int(max_duration * fs)

    for drop_idx in drop_idxs:
        if used[drop_idx]:
            continue

        # Look for rise after drop within max duration
        candidates = rise_idxs[(rise_idxs > drop_idx) & (rise_idxs - drop_idx <= max_samples)]
        if len(candidates) == 0:
            continue

        rise_idx = candidates[0]
        start = max(0, drop_idx - margin)
        end = min(len(dip_mask), rise_idx + margin + 1)

        dip_mask[start:end] = True
        used[start:end] = True

    # Interpolate over dip regions
    cleaned_signal = signal.copy()
    valid = ~dip_mask
    if np.sum(valid) > 1:
        interp_func = interp1d(
            t_sample[valid], signal[valid],
            kind='linear', bounds_error=False, fill_value='extrapolate'
        )
        cleaned_signal[dip_mask] = interp_func(t_sample[dip_mask])

    # return cleaned_signal, dip_mask commented out by HS on 12/29/25
    return cleaned_signal

def remove_outliers(signal, maxdev=2.5, invalid=-1, interpolate=True, allowp=0.05):
    """
    Detect outliers based on standard-deviation bounds and optionally
    interpolate across the invalid regions.

    Parameters
    ----------
    signal : array_like
        1D array of signal values to clean.
    maxdev : float, optional
        Number of standard deviations from the mean that defines the
        outlier threshold. Defaults to 2.5.
    invalid : float, optional
        Temporary placeholder value assigned to detected outliers before
        interpolation. Defaults to -1.
    interpolate : bool, optional
        If True, perform linear interpolation across invalid samples.
        Defaults to True.
    allowp : float, optional
        If `std < allowp * abs(mean)`, skip outlier detection because the
        signal is too stable. Defaults to 0.05.

    Returns
    -------
    numpy.ndarray
        Cleaned signal with outliers replaced (and interpolated, if
        requested).
    """
    if signal.ndim != 1:
        raise ValueError("Signal must be 1D.")

    signal = signal.copy()
    mean_val = np.mean(signal)
    std_val = np.std(signal)

    if std_val < allowp * abs(mean_val):
        return signal  # too stable to meaningfully detect outliers

    # Define outlier bounds
    lower_bound = mean_val - maxdev * std_val
    upper_bound = mean_val + maxdev * std_val

    # Mark outliers with invalid placeholder
    outliers = (signal < lower_bound) | (signal > upper_bound)
    signal[outliers] = invalid

    # Interpolate if requested
    if interpolate:
        # signal = interpolate_missing(signal, mode=mode, invalid=invalid)
        
        x = np.arange(len(signal))
        valid = signal != invalid

        if valid.sum() < 2:
            return signal  # not enough valid points to interpolate

        interp_func = interp1d(
            x[valid], signal[valid], kind='linear',
            bounds_error=False, fill_value='extrapolate'
        )
        signal = interp_func(x)
        
    return signal


def downsample_data(df, downsample_factor=10):
    """
    Downsample a dataframe or list of dataframes by selecting every Nth row.

    Parameters
    ----------
    df : pandas.DataFrame or list
        DataFrame to downsample or a list of DataFrames. When a list is
        provided, each element is downsampled in-place.
    downsample_factor : int, optional
        Factor by which to downsample (keep every `downsample_factor`-th
        row). Defaults to 10.

    Returns
    -------
    pandas.DataFrame or list
        The downsampled DataFrame or list of DataFrames.
    """
    # check if input var is a list of dataframe
    if isinstance(df, list):
        for each_df in df:
            each_df = each_df.iloc[::downsample_factor, :]
    else:
        df = df.iloc[::downsample_factor, :]
    
    # return downsampled dataframe/list
    return df

            

def create_zipf_dict(zipf_filename = './res/word_sensitivity_table.xlsx'):
    """
    Load a Zipf frequency table from an Excel file and return a dictionary
    mapping words to their Zipf frequency (US lexicon).

    Parameters
    ----------
    zipf_filename : str, optional
        Path to an Excel file containing at minimum the columns `Word` and
        `FreqZipfUS`. Defaults to './res/word_sensitivity_table.xlsx'.

    Returns
    -------
    dict
        A dictionary mapping each word (string) to its Zipf frequency value
        (numeric) taken from the `FreqZipfUS` column.
    """
    return pd.read_excel(zipf_filename, usecols=['Word', 'FreqZipfUS']).set_index('Word').to_dict()['FreqZipfUS']

    
# The following functions convert coordinate among different systems (PsychoPy Height Unit, Image Pixel, Relative Position). 
# Refer to this post for understanding: https://wordpress.com/post/glassbrainlab.wordpress.com/623

def convert_error_page_pixel_to_py(x_image, y_image):
    '''
    !!!
    This function is used for old task paradigm where error words are implanted in the reading text.
    The new task paradigm displays the same reading page for participants to select MW onset and offset. 

    This function almost gave me a heart attack during review (7/27/25)
    !!!
    Convert error page pixel to psychopy height unit. Note that error page is not the same as normal reading page nor the whole screen.

    Parameters
    ----------
    x_image : float
        DESCRIPTION. position x in pixel
    y_image : float
        DESCRIPTION. position y in pixel

    Returns
    -------
    x_py : float
        DESCRIPTION. position x in height unit
    y_py : float
        DESCRIPTION. position y in height unit

    '''
    x_py = (x_image-1900/2)/1900 * 1.12
    y_py = (-y_image+1442/2)/1442 * 0.85 + 0.05
    
    return x_py, y_py


def convert_height_unit_to_pixel(x_height, y_height):
    '''
    Convert height unit to pixel for image (1900 x 1442 pixels) displayed at 
    pos (0, 0) w/ size (1.3, 0.99) in PsychoPy.

    Parameters
    ----------
    x_height : float
        DESCRIPTION. PsychoPy height unit
    y_height : float
        DESCRIPTION. PsychoPy height unit

    Returns
    -------
    x_pixel : float
        DESCRIPTION. Image pixel unit
    y_pixel : float 
        DESCRIPTION. Image pixel unit 

    '''
    x_pixel = x_height/1.3*1900 + 1900/2
    y_pixel = -y_height/0.99*1442 + 1442/2
    return x_pixel, y_pixel


def convert_pixel_to_eyelink(x_image,y_image):
    """
    converts image pixels to eyelink pixels

    inputs:

    x_image: float
    The term to convert x coordinates to eye link

    y_image: float
    The term to convert y coordinates to eyelink
​
    output:

    x_eyelink : float
    the converted x coordinate

    y_eyelink: float
    the converted y coordinate

    (Assuming we are converting from the dimensions 1209x918 to 1418x1070)(x,y)
    The dimensions for updated images: 1900x1440
    """

    #changes x to eyelink coordinates
    # x_eyelink = (1418/1209)*x_image+355.2
    x_eyelink = (1080 * 1.3/1900)*x_image+258

    #changes y to eyelink coordinates
    # y_eyelink = (1070/918)*y_image+27
    y_eyelink = (1080 * 0.99/1442)*y_image+5.4

    return x_eyelink,y_eyelink


def convert_py_to_eyelink( x_psycho , y_psycho ):
    """
    Converts py to eyelink terms

    Inputs:

    psycho_x float
    The term to convert psychopy x-coordinates

    psycho_y: float
    The term the psychopy y-coordinates

    output:

    x_pixel: float
    The converted x coordinate [py to eyelink]

    y_pixel: float
    the converted y coordinate [py to eyelink]

        (Assuming we are converting from the dimensions 1.12x0.85 to 1418x1070 (x,y)
    11/07/22 Updated: 1.3 x 0.99 to 1900x1442
     """

    #changes x to from psychopy to eyelink coordinates
    x_eyelink = (1209/1.3)*x_psycho+960

    #changes y to from psychopy to eyelink coordinates
    y_eyelink = -(918/0.99)*y_psycho+540

    return  x_eyelink, y_eyelink


def convert_pixel_to_py(x_image, y_image):
    '''
    Convert image pixel to psychopy height unit

    Parameters
    ----------
    x_image : float
        DESCRIPTION. position x in pixel
    y_image : float
        DESCRIPTION. position y in pixel

    Returns
    -------
    x_py : float
        DESCRIPTION. position x in height unit
    y_py : float
        DESCRIPTION. position y in height unit

    '''
    x_py = (x_image-1900/2)/1900 * 1.3
    y_py = (y_image-1440/2)/1440 * 0.99
    
    return x_py, y_py


def convert_eyelink_to_image_pixel(x_eyelink, y_eyelink):
        '''
        Convert eyeylink coords to pixel for image (1900 x 1442 pixels) 
        displayed at pos (0, 0) w/ size (1.3, 0.99) in PsychoPy.

        Parameters
        ----------
        x_eyelink : float
            DESCRIPTION. eyelink coord unit
        y_eyelink : float
            DESCRIPTION. eyelink coord unit

        Returns
        -------
        x_pixel : float
            DESCRIPTION. Image pixel unit
        y_pixel : float 
            DESCRIPTION. Image pixel unit 

        '''
        x_pixel = (x_eyelink-258) * 1900 / (1080*1.3)
        y_pixel = (y_eyelink-5.4) * 1442 / (1080*0.99)
        return x_pixel, y_pixel
