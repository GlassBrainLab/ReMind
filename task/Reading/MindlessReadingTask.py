#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy3 Experiment Builder (v2021.1.4),
    on Mon Nov 22 10:49:55 2021
If you publish work using this script the most relevant publication is:

    Peirce J, Gray JR, Simpson S, MacAskill M, Höchenberger R, Sogo H, Kastman E, Lindeløv JK. (2019)
        PsychoPy2: Experiments in behavior made easy Behav Res 51: 195.
        https://doi.org/10.3758/s13428-018-01193-y

EEG label convention:
    1: Reading Start (after instructions and eye calibration)
    10: Cross Fixation
    20: Reading Page Displayed
    30: Reading Page END
    5: Comprehension Questions

Updated 08/13/2023 by HS    - add self-report
"""

from __future__ import absolute_import, division

from psychopy import locale_setup
from psychopy import prefs
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)

import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle, choice as randchoice
import os  # handy system and path functions
import sys  # to get file system encoding
import random as r # for randomizing error trial positions
from psychopy.hardware import keyboard


# === EEG === #
import serial # For sending signals to eeg

# === EYELINK CODE === #

import pylink
import platform
import random
import time
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy
from PIL import Image  # for preparing the Host backdrop image
from string import ascii_letters, digits

# Switch to the script folder
script_path = os.path.dirname(sys.argv[0])
if len(script_path) != 0:
    os.chdir(script_path)

# Show only critical log message in the PsychoPy console
#from psychopy import logging
#logging.console.setLevel(logging.CRITICAL)

# Set this variable to True if you use the built-in retina screen as your
# primary display device on macOS. If have an external monitor, set this
# variable True if you choose to "Optimize for Built-in Retina Display"
# in the Displays preference settings.
use_retina = False

# Set this variable to True to run the script in "Dummy Mode"
#dummy_mode = False This is now set from expInfo['is_tracker_connected']

# Set this variable to True to run the task in full screen mode
# It is easier to debug the script in non-fullscreen mode
# full_screen = True
full_screen = False # DJ switched

# Store the parameters of all trials in a list, [condition, image]
#trials = [
#    ['cond_1', 'img_1.jpg'],
#    ['cond_2', 'img_2.jpg'],
#    ]

# Set up EDF data file name and local data folder
#
# The EDF data filename should not exceed 8 alphanumeric characters
# use ONLY number 0-9, letters, & _ (underscore) in the filename
edf_fname = 'TEST'

# Prompt user to specify an EDF data filename
# before we open a fullscreen window
dlg_title = 'Enter EDF File Name'
dlg_prompt = 'Please enter a file name with 8 or fewer characters\n' + \
             '[letters, numbers, and underscore].'

# loop until we get a valid filename
while True:
    dlg = gui.Dlg(dlg_title)
    dlg.addText(dlg_prompt)
    dlg.addField('File Name:', edf_fname)
    # show dialog and wait for OK or Cancel
    ok_data = dlg.show()
    if dlg.OK:  # if ok_data is not None
        print('EDF data filename: {}'.format(ok_data[0]))
    else:
        print('user cancelled')
        core.quit()
        sys.exit()

    # get the string entered by the experimenter
    tmp_str = dlg.data[0]
    # strip trailing characters, ignore the ".edf" extension
    edf_fname = tmp_str.rstrip().split('.')[0]

    # check if the filename is valid (length <= 8 & no special char)
    allowed_char = ascii_letters + digits + '_'
    if not all([c in allowed_char for c in edf_fname]):
        print('ERROR: Invalid EDF filename')
    elif len(edf_fname) > 8:
        print('ERROR: EDF filename should not exceed 8 characters')
    else:
        break

# Set up a folder to store the EDF data files and the associated resources
# e.g., files defining the interest areas used in each trial
results_folder = 'data'
if not os.path.exists(results_folder):
    os.makedirs(results_folder)

# We download EDF data file from the EyeLink Host PC to the local hard
# drive at the end of each testing session, here we rename the EDF to
# include session start date/time
time_str = time.strftime("_%Y_%m_%d_%H_%M", time.localtime())
session_identifier = edf_fname + time_str

# create a folder for the current testing session in the "results" folder
session_folder = os.path.join(results_folder, session_identifier)
if not os.path.exists(session_folder):
    os.makedirs(session_folder)

# === END EYELINK CODE === #


# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

# Store info about the experiment session
psychopyVersion = '2021.1.4'
expName = 'MindlessReading'  # from the Builder filename that created this script
expInfo = {'participant': '', 'session': '1','type': ['eye tracking','eeg','fmri', 'self-report'],'is_tracker_connected': True}
dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
if dlg.OK == False:
    core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName
expInfo['psychopyVersion'] = psychopyVersion

if expInfo['type'] == 'eye tracking' or 'self-report':
    instructionsFile = 'instructions_eye_tracking.xlsx'
    advanceKeys = ['space']
    errorKey = 'x'
    triggerKey = 't'
    wait_message = f'That’s the end of calibration.\n\nPlease place your left finger on X and right finger on the Spacebar.\n\nExperimenter, press {triggerKey} to begin the experiment.'
elif expInfo['type'] == 'eeg':
    instructionsFile = 'instructions_eeg.xlsx'
    advanceKeys = ['space']
    errorKey = '_' # none
    triggerKey = 't'
    wait_message = f'That’s the end of calibration.\n\nPlease place your right finger on the Spacebar.\n\nExperimenter, press {triggerKey} to begin the experiment.'

    # === BIOSEMI CONNECTION ===
    deviceName = '/dev/cu.usbserial-DN2Q03JQ' # Name of callout device
    baudeRate = 115200 # baude rate value

    # Initialize callout device for sending messages
    ser = serial.Serial(deviceName, baudeRate, timeout=10)

elif expInfo['type'] == 'fmri':
    instructionsFile = 'instructions_fmri.xlsx'
    advanceKeys = ['6','7','8','9','0']
    errorKey = '_' # none
    triggerKey = 's'
    wait_message = f'That’s the end of calibration.\n\nPlease place your right finger on any button of the button box.\n\nExperimenter, start the scanner or press {triggerKey} to begin the experiment.'

# if the eye tracker isn't connected, use "dummy mode" where there's no communication with the tracker
dummy_mode = not expInfo['is_tracker_connected']

# Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
filename = _thisDir + os.sep + u'data/%s_%s_%s' % (expInfo['participant'], expName, expInfo['date'])

# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(name=expName, version='',
    extraInfo=expInfo, runtimeInfo=None,
    originPath='/Users/brainlab/Documents/GitHub/MindlessReading/Reading/ReadingOnline-test.py',
    savePickle=True, saveWideText=True,
    dataFileName=filename)
# save a log file for detail verbose info
logFile = logging.LogFile(filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

endExpNow = False  # flag for 'q' or other condition => quit the exp
frameTolerance = 0.001  # how close to onset before 'same' frame

# Start Code - component code to be run after the window creation

# Setup the Window
win = visual.Window(
    size=[1440, 900], fullscr=True, screen=0,
    winType='pyglet', allowGUI=False, allowStencil=False,
    monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
    blendMode='avg', useFBO=True,
    units='height')
# store frame rate of monitor if we can measure it
expInfo['frameRate'] = win.getActualFrameRate()
if expInfo['frameRate'] != None:
    frameDur = 1.0 / round(expInfo['frameRate'])
else:
    frameDur = 1.0 / 60.0  # could not measure, so guess

# create a default keyboard (e.g. to check for q)
defaultKeyboard = keyboard.Keyboard()

# Initialize components for Routine "init"
initClock = core.Clock()
instructions_height = 0.05
probe_text_height = 0.03
probe_choice_height = 0.025
# fix_dur = 0 for testing
fix_dur = 2
page_dur = 80
fade_dur = 5
error_count = 3

# fMRI task has four readings (Serena Williams excluded)
if expInfo['type'] == 'fmri':
    reading_count = 4
    reading_condition_file = 'fmri_reading_condition_file.xlsx'
else:
    reading_count = 5
    reading_condition_file = 'reading_condition_file.xlsx'

# page numbers for each reading
pages_count = [10 for _ in range(reading_count)]
# error types
page_error_type = ['lexical', 'gibberish', 'control', 'no_error']
# get the participant and session number
participant = int(expInfo['participant'])
# since the session starts from 1, we minus 1 to meet the indexing convention
session = int(expInfo['session']) - 1
# skip the instructions if the session is not 1
instrReps = 1.0 if session == 0 else 0.0
# randomize the reading order for each subject
np.random.seed(participant)
reading_order = np.arange(reading_count)
np.random.shuffle(reading_order)

# === set up variables for eye-tracking ===
# indicate whether eye-tracking's recording
isETRecording = False
# initialize trial index
page = 0

# Initialize components for Routine "instructions"
instructionsClock = core.Clock()
text_instructions_top = visual.TextStim(win=win, name='text_instructions_top',
    text='',
    font='Open Sans',
    pos=(0, 0.4), height=instructions_height, wrapWidth=1.3, ori=0.0,
    color='white', colorSpace='rgb', opacity=None,
    languageStyle='LTR',
    depth=0.0);
instructions_image = visual.ImageStim(
    win=win,
    name='instructions_image',
    image='sin', mask=None,
    ori=0.0, pos=(0, -0.08), size=(1.24, 0.7),
    color=[1,1,1], colorSpace='rgb', opacity=None,
    flipHoriz=False, flipVert=False,
    texRes=128.0, interpolate=True, depth=-1.0)
text_instructions_bottom = visual.TextStim(win=win, name='text_instructions_bottom',
    text='',
    font='Open Sans',
    pos=(0, -.45), height=instructions_height, wrapWidth=1.3, ori=0.0,
    color='white', colorSpace='rgb', opacity=None,
    languageStyle='LTR',
    depth=-2.0);
key_resp_instructions = keyboard.Keyboard()

# Initialize components for Routine "start_cali"
start_caliClock = core.Clock()
cali_text = visual.TextStim(win=win, name='cali_text',
    text='Press ENTER to start calibration.',
    font='Open Sans',
    pos=(0, 0), height=instructions_height, wrapWidth=None, ori=0.0,
    color='white', colorSpace='rgb', opacity=None,
    languageStyle='LTR',
    depth=0.0);

# --- Initialize components for Routine "wait_for_scanner" ---
wait_resp = keyboard.Keyboard()
wait_text = visual.TextStim(win=win, name='wait_text',
    text=wait_message,
    font='Open Sans',
    pos=(0, 0), height=0.05, wrapWidth=None, ori=0.0,
    color='white', colorSpace='rgb', opacity=None,
    languageStyle='LTR',
    depth=-1.0);

# Initialize components for Routine "start_task"
start_taskClock = core.Clock()
beginning_text = visual.TextStim(win=win, name='beginning_text',
    text='Please wait. Your reading task will start in a few seconds.',
    font='Open Sans',
    pos=(0, 0), height=instructions_height, wrapWidth=None, ori=0.0,
    color='white', colorSpace='rgb', opacity=None,
    languageStyle='LTR',
    depth=0.0);

# Initialize components for Routine "init_reading"
init_readingClock = core.Clock()

# Initialize components for Routine "init_error"
init_errorClock = core.Clock()

# Initialize components for Routine "trial"
trialClock = core.Clock()
reading_image = visual.ImageStim(
   win=win,
   name='reading_image',
   image='sin', mask=None,
   ori=0.0, pos=(0, 0), size=(1.30, 0.99),
   color=[1,1,1], colorSpace='rgb', opacity=None,
   flipHoriz=False, flipVert=False,
   texRes=128.0, interpolate=True, depth=0.0)
cross = visual.TextStim(win=win, name='cross',
   text='+',
   font='Open Sans',
   units='height', pos=(-0.5, 0.45), height=0.1, wrapWidth=None, ori=0.0,
   color='black', colorSpace='rgb', opacity=None,
   languageStyle='LTR',
   depth=-1.0);
key_resp = keyboard.Keyboard()
text_page_bottom = visual.TextStim(win=win, name='text_page_bottom',
   text='',
   font='Open Sans',
   pos=(0, -.485), height=instructions_height/2, wrapWidth=1.3, ori=0.0,
   color='white', colorSpace='rgb', opacity=None,
   languageStyle='LTR',
   depth=-4.0);
this_page_dur = page_dur

# Initialize components for Routine "error"
errorClock = core.Clock()
error_background = visual.Rect(
    win=win, name='error_background',
    width=(1.4, 1)[0], height=(1.4, 1)[1],
    ori=0.0, pos=(0, 0),
    lineWidth=1.0,     colorSpace='rgb',  lineColor=(0.5294, 0.0000, 0.0000), fillColor=(0.5294, 0.0000, 0.0000),
    opacity=None, depth=0.0, interpolate=True)
reading_image_error = visual.ImageStim(
    win=win,
    name='reading_image_error',
    image='sin', mask=None,
    ori=0.0, pos=(0, 0.05), size=(1.12, 0.85),
    color=[1,1,1], colorSpace='rgb', opacity=None,
    flipHoriz=False, flipVert=False,
    texRes=128.0, interpolate=True, depth=-1.0)
text_error_bottom = visual.TextStim(win=win, name='text_error_bottom',
    text='',
    font='Open Sans',
    pos=(0, -.45), height=instructions_height/2, wrapWidth=1.3, ori=0.0,
    color='white', colorSpace='rgb', opacity=None,
    languageStyle='LTR',
    depth=-2.0);
mouse_error = event.Mouse(win=win)
x, y = [None, None]
mouse_error.mouseClock = core.Clock()
key_resp_error = keyboard.Keyboard()

# Initialize components for Routine "probes"
probesClock = core.Clock()
text_probe_instructions = visual.TextStim(win=win, name='text_probe_instructions',
    text='Click each slider to describe your thoughts while you were reading the last page. When you’re done, click the button at the bottom.',
    font='Open Sans',
    pos=(0, 0.375), height=instructions_height, wrapWidth=1.4, ori=0.0,
    color='white', colorSpace='rgb', opacity=None,
    languageStyle='LTR',
    depth=0.0);
text_task = visual.TextStim(win=win, name='text_task',
    text='My thoughts were related to the text I was reading.',
    font='Open Sans',
    pos=(0, 0.25), height=probe_text_height, wrapWidth=None, ori=0.0,
    color='white', colorSpace='rgb', opacity=None,
    languageStyle='LTR',
    depth=-1.0);
slider_task = visual.Slider(win=win, name='slider_task',
    size=(1.0, 0.03), pos=(0, 0.2), units=None,
    labels=('Not at all','Completely'), ticks=(0,1), granularity=0.01,
    style='rating', styleTweaks=('triangleMarker',), opacity=None,
    color='LightGray', fillColor='Red', borderColor='White', colorSpace='rgb',
    font='Open Sans', labelHeight=probe_choice_height,
    flip=False, depth=-2, readOnly=False)
text_detailed = visual.TextStim(win=win, name='text_detailed',
    text='My thoughts were detailed and specific.',
    font='Open Sans',
    pos=(0, 0.1), height=probe_text_height, wrapWidth=None, ori=0.0,
    color='white', colorSpace='rgb', opacity=None,
    languageStyle='LTR',
    depth=-3.0);
slider_detailed = visual.Slider(win=win, name='slider_detailed',
    size=(1.0, 0.03), pos=(0, 0.05), units=None,
    labels=('Not at all','Completely'), ticks=(0,1), granularity=0.01,
    style='rating', styleTweaks=('triangleMarker',), opacity=None,
    color='LightGray', fillColor='Red', borderColor='White', colorSpace='rgb',
    font='Open Sans', labelHeight=probe_choice_height,
    flip=False, depth=-4, readOnly=False)
text_words = visual.TextStim(win=win, name='text_words',
    text='My thoughts were in the form of words.',
    font='Open Sans',
    pos=(0, -0.05), height=probe_text_height, wrapWidth=None, ori=0.0,
    color='white', colorSpace='rgb', opacity=None,
    languageStyle='LTR',
    depth=-5.0);
slider_words = visual.Slider(win=win, name='slider_words',
    size=(1.0, 0.03), pos=(0, -0.1), units=None,
    labels=('Not at all','Completely'), ticks=(0,1), granularity=0.01,
    style='rating', styleTweaks=('triangleMarker',), opacity=None,
    color='LightGray', fillColor='Red', borderColor='White', colorSpace='rgb',
    font='Open Sans', labelHeight=probe_choice_height,
    flip=False, depth=-6, readOnly=False)
text_emotion = visual.TextStim(win=win, name='text_emotion',
    text='My thoughts were…',
    font='Open Sans',
    pos=(0, -0.2), height=probe_text_height, wrapWidth=None, ori=0.0,
    color='white', colorSpace='rgb', opacity=None,
    languageStyle='LTR',
    depth=-7.0);
slider_emotion = visual.Slider(win=win, name='slider_emotion',
    size=(1.0, 0.03), pos=(0, -0.25), units=None,
    labels=('Very Negative','Very Positive'), ticks=(0,1), granularity=0.01,
    style='rating', styleTweaks=('triangleMarker',), opacity=None,
    color='LightGray', fillColor='Red', borderColor='White', colorSpace='rgb',
    font='Open Sans', labelHeight=probe_choice_height,
    flip=False, depth=-8, readOnly=False)
button_probe = visual.ButtonStim(win,
   text='Click here when done', font='Open Sans',
   pos=(0, -0.4),
   letterHeight=probe_text_height,
   size=(0.5,0.05), borderWidth=0.0,
   fillColor='darkgrey', borderColor=None,
   color='white', colorSpace='rgb',
   opacity=None,
   bold=True, italic=False,
   padding=None,
   anchor='center',
   name='button_probe')
button_probe.buttonClock = core.Clock()

# Initialize components for Routine "trial"
trialClock = core.Clock()
reading_image = visual.ImageStim(
    win=win,
    name='reading_image',
    image='sin', mask=None,
    ori=0.0, pos=(0, 0), size=(1.30, 0.99),
    color=[1,1,1], colorSpace='rgb', opacity=None,
    flipHoriz=False, flipVert=False,
    texRes=128.0, interpolate=True, depth=0.0)
cross = visual.TextStim(win=win, name='cross',
    text='+',
    font='Open Sans',
    units='height', pos=(-0.63, 0.47), height=0.05, wrapWidth=None, ori=0.0,
    color='black', colorSpace='rgb', opacity=None,
    languageStyle='LTR',
    depth=-1.0);
key_resp = keyboard.Keyboard()
text_page_bottom = visual.TextStim(win=win, name='text_page_bottom',
    text='',
    font='Open Sans',
    pos=(0, -.55), height=instructions_height/2, wrapWidth=1.3, ori=0.0,
    color='white', colorSpace='rgb', opacity=None,
    languageStyle='LTR',
    depth=-4.0); # PLACED OFF-SCREEN FOR NOW
this_page_dur = page_dur

# Initialize components for Routine "comp_instructions"
comp_instructionsClock = core.Clock()
text_instructions_top_2 = visual.TextStim(win=win, name='text_instructions_top_2',
    text='That’s the end of the reading in this run.\n\nYou will now be asked some questions about what you read. Please respond using the number keys.',
    font='Open Sans',
    pos=(0, 0.35), height=instructions_height, wrapWidth=1.3, ori=0.0,
    color='white', colorSpace='rgb', opacity=None,
    languageStyle='LTR',
    depth=0.0);
instructions_image_2 = visual.ImageStim(
    win=win,
    name='instructions_image_2',
    image='sin', mask=None,
    ori=0.0, pos=(0, -0.08), size=(0.9, 0.5),
    color=[1,1,1], colorSpace='rgb', opacity=None,
    flipHoriz=False, flipVert=False,
    texRes=128.0, interpolate=True, depth=-1.0)
text_instructions_bottom_2 = visual.TextStim(win=win, name='text_instructions_bottom_2',
    text='',
    font='Open Sans',
    pos=(0, -.45), height=instructions_height, wrapWidth=1.3, ori=0.0,
    color='white', colorSpace='rgb', opacity=None,
    languageStyle='LTR',
    depth=-2.0);
key_resp_instructions_2 = keyboard.Keyboard()

# Initialize components for Routine "comp_question"
comp_questionClock = core.Clock()
text_question = visual.TextStim(win=win, name='text_question',
    text='',
    font='Open Sans',
    pos=(0, 0.4), height=instructions_height, wrapWidth=1.3, ori=0.0,
    color='white', colorSpace='rgb', opacity=None,
    languageStyle='LTR',
    depth=-1.0);
text_options = visual.TextStim(win=win, name='text_options',
    text='',
    font='Open Sans',
    pos=(0, -0.1), height=instructions_height, wrapWidth=1.3, ori=0.0,
    color='white', colorSpace='rgb', opacity=None,
    languageStyle='LTR',
    depth=-2.0);
key_resp_question = keyboard.Keyboard()
text_question_instructions = visual.TextStim(win=win, name='text_question_instructions',
    text='',
    font='Open Sans',
    pos=(0, -0.42), height=instructions_height/2, wrapWidth=1.3, ori=0.0,
    color='white', colorSpace='rgb', opacity=None,
    languageStyle='LTR',
    depth=-4.0);

# Initialize components for Routine "new_reading"
new_readingClock = core.Clock()
if expInfo['type'] == 'fmri':
    new_reading_text = 'You will be reading another passage. In 15 seconds, eye calibration will start, or press ANY KEY to continue.'
else:
    new_reading_text = 'That\'s the end of the comprehension questions.\n\nPlease wait for experimenter to terminate the task.'
next_reading_text = visual.TextStim(win=win, name='next_reading_text',
    text=new_reading_text,
    font='Open Sans',
    pos=(0, 0), height=instructions_height, wrapWidth=None, ori=0.0,
    color='white', colorSpace='rgb', opacity=None,
    languageStyle='LTR',
    depth=0.0);
key_resp_next_reading = keyboard.Keyboard()

# Initialize components for Routine "goodbye"
goodbyeClock = core.Clock()
# generate hash code
hash_num = (int(expInfo['participant'])*77069) % (10**5)

# Generate random number specific to this run
random_id = randint(0,9999);

# format code
hash_str="%05d"%(hash_num) + "-%04d"%(random_id)

# update log
thisExp.addData('hash_code',hash_str);

# set hash_str as an empty string for in-person tasks
hash_str = ''

goodbye_text_top = visual.TextStim(win=win, name='goodbye_text_top',
    text='Thank you for participating!',
    font='Open Sans',
    pos=(0, 0.35), height=instructions_height, wrapWidth=1.3, ori=0.0,
    color='white', colorSpace='rgb', opacity=None,
    languageStyle='LTR',
    depth=-1.0);
hash_text = visual.TextStim(win=win, name='hash_text',
    text=hash_str,
    font='Open Sans',
    pos=(0, 0.0), height=instructions_height*2, wrapWidth=1.3, ori=0.0,
    color='black', colorSpace='rgb', opacity=None,
    languageStyle='LTR',
    depth=-2.0);
goodbye_text_bottom = visual.TextStim(win=win, name='goodbye_text_bottom',
    text='Press X to end the experiment.',
    font='Open Sans',
    pos=(0, -0.4), height=instructions_height, wrapWidth=1.3, ori=0.0,
    color='white', colorSpace='rgb', opacity=None,
    languageStyle='LTR',
    depth=-3.0);
key_resp_goodbye = keyboard.Keyboard()

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine


# === EYELINK SEND FILE VISUALS CODE === #

# Initialize components for Routine "stop_eyelink"
stop_eyelinkClock = core.Clock()
text_sending = visual.TextStim(win=win, name='text_sending',
    text='Closing eye tracking file and sending data… Please wait.',
    font='Open Sans',
    units='height', pos=(0, 0), height=0.075, wrapWidth=1.3, ori=0.0,
    color='black', colorSpace='rgb', opacity=None,
    languageStyle='LTR',
    depth=0.0);

# === EYELINK START TRACKER CODE === #

# Step 1: Connect to the EyeLink Host PC
#
# The Host IP address, by default, is "100.1.1.1".
# the "el_tracker" objected created here can be accessed through the Pylink
# Set the Host PC address to "None" (without quotes) to run the script
# in "Dummy Mode"
if dummy_mode:
    el_tracker = pylink.EyeLink(None)
else:
    try:
        el_tracker = pylink.EyeLink("100.1.1.1")
    except RuntimeError as error:
        print('ERROR:', error)
        core.quit()
        sys.exit()

# Step 2: Open an EDF data file on the Host PC
edf_file = edf_fname + ".EDF"
try:
    el_tracker.openDataFile(edf_file)
except RuntimeError as err:
    print('ERROR:', err)
    # close the link if we have one open
    if el_tracker.isConnected():
        el_tracker.close()
    core.quit()
    sys.exit()

# Add a header text to the EDF file to identify the current experiment name
# This is OPTIONAL. If your text starts with "RECORDED BY " it will be
# available in DataViewer's Inspector window by clicking
# the EDF session node in the top panel and looking for the "Recorded By:"
# field in the bottom panel of tfhe Inspector.
preamble_text = 'RECORDED BY %s' % os.path.basename(__file__)
el_tracker.sendCommand("add_file_preamble_text '%s'" % preamble_text)


# === DEFINE EYELINK FUNCTIONS === #

def terminate_task():
    """ Terminate the task gracefully and retrieve the EDF data file

    file_to_retrieve: The EDF on the Host that we would like to download
    win: the current window used by the experimental script
    """

    el_tracker = pylink.getEYELINK()

    if el_tracker.isConnected():
        # Terminate the current trial first if the task terminated prematurely
        error = el_tracker.isRecording()
        if error == pylink.TRIAL_OK:
             el_tracker.abort()
        # Put tracker in Offline mode
        el_tracker.setOfflineMode()

        # Clear the Host PC screen and wait for 500 ms
        el_tracker.sendCommand('clear_screen 0')
        pylink.msecDelay(500)

        # Close the edf data file on the Host
        el_tracker.closeDataFile()

        # Show a file transfer message on the screen
        msg = 'EDF data is transferring from EyeLink Host PC...'
        # show_msg(win, msg, wait_for_keypress=False)
        print(msg)

        # Download the EDF data file from the Host PC to a local data folder
        # parameters: source_file_on_the_host, destination_file_on_local_drive
        local_edf = os.path.join(session_folder, session_identifier + '.EDF')
        try:
            el_tracker.receiveDataFile(edf_file, local_edf)
        except RuntimeError as error:
            print('ERROR:', error)

        # Close the link to the tracker.
        el_tracker.close()

    # close the PsychoPy window
    win.close()

    # quit PsychoPy
    core.quit()
    sys.exit()

# === EYELINK PASS VISUALS === #

# Step 3: Configure the tracker
#
# Put the tracker in offline mode before we change tracking parameters
el_tracker.setOfflineMode()

# Get the software version:  1-EyeLink I, 2-EyeLink II, 3/4-EyeLink 1000,
# 5-EyeLink 1000 Plus, 6-Portable DUO
eyelink_ver = 0  # set version to 0, in case running in Dummy mode
if not dummy_mode:
    vstr = el_tracker.getTrackerVersionString()
    eyelink_ver = int(vstr.split()[-1].split('.')[0])
    # print out some version info in the shell
    print('Running experiment on %s, version %d' % (vstr, eyelink_ver))

# File and Link data control
# what eye events to save in the EDF file, include everything by default
file_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT'
# what eye events to make available over the link, include everything by default
link_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON,FIXUPDATE,INPUT'
# what sample data to save in the EDF data file and to make available
# over the link, include the 'HTARGET' flag to save head target sticker
# data for supported eye trackers
if eyelink_ver > 3:
    file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,HTARGET,GAZERES,BUTTON,STATUS,INPUT'
    link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,HTARGET,STATUS,INPUT'
else:
    file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,GAZERES,BUTTON,STATUS,INPUT'
    link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,INPUT'
el_tracker.sendCommand("file_event_filter = %s" % file_event_flags)
el_tracker.sendCommand("file_sample_data = %s" % file_sample_flags)
el_tracker.sendCommand("link_event_filter = %s" % link_event_flags)
el_tracker.sendCommand("link_sample_data = %s" % link_sample_flags)

# Optional tracking parameters
# Sample rate, 250, 500, 1000, or 2000, check your tracker specification
# if eyelink_ver > 2:
#     el_tracker.sendCommand("sample_rate 1000")
# Choose a calibration type, H3, HV3, HV5, HV13 (HV = horizontal/vertical),
el_tracker.sendCommand("calibration_type = HV9")
# Set a gamepad button to accept calibration/drift check target
# You need a supported gamepad/button box that is connected to the Host PC
el_tracker.sendCommand("button_function 5 'accept_target_fixation'")

# Step 4: set up a graphics environment for calibration
#
# Open a window, be sure to specify monitor parameters
#mon = monitors.Monitor('myMonitor', width=53.0, distance=70.0) # DJ commented out
# mon = monitors.Monitor('BigBubba') # DJ added
#print(mon) # DJ added
#win = visual.Window(fullscr=full_screen,
#                    size=(1920,1080),
#                    winType='pyglet',
#                    units='pix')

# get the native screen resolution used by PsychoPy
scn_width, scn_height = win.size
# print screen size
print(f'DETECTED screen width: {scn_width}, height: {scn_height}')
# resolution fix for Mac retina displays
if 'Darwin' in platform.system():
    if use_retina:
        scn_width = int(scn_width/2.0)
        scn_height = int(scn_height/2.0)

# Pass the display pixel coordinates (left, top, right, bottom) to the tracker
# see the EyeLink Installation Guide, "Customizing Screen Settings"
el_coords = "screen_pixel_coords = 0 0 %d %d" % (scn_width - 1, scn_height - 1)
el_tracker.sendCommand(el_coords)

# Write a DISPLAY_COORDS message to the EDF file
# Data Viewer needs this piece of info for proper visualization, see Data
# Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
dv_coords = "DISPLAY_COORDS  0 0 %d %d" % (scn_width - 1, scn_height - 1)
el_tracker.sendMessage(dv_coords)

# Configure a graphics environment (genv) for tracker calibration
genv = EyeLinkCoreGraphicsPsychoPy(el_tracker, win)
print(genv)  # print out the version number of the CoreGraphics library

# Set background and foreground colors for the calibration target
# in PsychoPy, (-1, -1, -1)=black, (1, 1, 1)=white, (0, 0, 0)=mid-gray
foreground_color = (-1, -1, -1)
background_color = win.color
genv.setCalibrationColors(foreground_color, background_color)

# Set up the calibration target
#
# The target could be a "circle" (default), a "picture", a "movie" clip,
# or a rotating "spiral". To configure the type of calibration target, set
# genv.setTargetType to "circle", "picture", "movie", or "spiral", e.g.,
# genv.setTargetType('picture')
#
# Use a picture as the calibration target
# genv.setTargetType('picture')
# genv.setPictureTarget(os.path.join('images', 'fixTarget.bmp'))

# The target could be a "circle" (default), a "picture", a "movie" clip,
# or a rotating "spiral".
genv.setTargetType('circle')
# Configure the size of the calibration target (in pixels)
# this option applies only to "circle" and "spiral" targets
genv.setTargetSize(24)

# Beeps to play during calibration, validation and drift correction
# parameters: target, good, error
#     target -- sound to play when target moves
#     good -- sound to play on successful operation
#     error -- sound to play on failure or interruption
# Each parameter could be ''--default sound, 'off'--no sound, or a wav file
genv.setCalibrationSounds('', '', '')

# resolution fix for macOS retina display issues
if use_retina:
    genv.fixMacRetinaDisplay()

# Request Pylink to use the PsychoPy window we opened above for calibration
pylink.openGraphicsEx(genv)

# === END EYELINK CODE === #


# === START ROUTINES === #

# ------Prepare to start Routine "init"-------
continueRoutine = True
# update component parameters for each repeat
# keep track of which components have finished
initComponents = []
for thisComponent in initComponents:
    thisComponent.tStart = None
    thisComponent.tStop = None
    thisComponent.tStartRefresh = None
    thisComponent.tStopRefresh = None
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED
# reset timers
t = 0
_timeToFirstFrame = win.getFutureFlipTime(clock="now")
initClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
frameN = -1

# -------Run Routine "init"-------
while continueRoutine:
    # get current time
    t = initClock.getTime()
    tThisFlip = win.getFutureFlipTime(clock=initClock)
    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame

    # check for quit (typically the Esc key)
    if endExpNow or defaultKeyboard.getKeys(keyList=["q"]):
        terminate_task()

    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in initComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished

    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "init"-------
for thisComponent in initComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
# the Routine "init" was not non-slip safe, so reset the non-slip timer
routineTimer.reset()

# set up handler to look after randomisation of conditions etc
instructionsLoop = data.TrialHandler(nReps=instrReps, method='sequential',
    extraInfo=expInfo, originPath=-1,
    trialList=data.importConditions(instructionsFile),
    seed=None, name='instructionsLoop')
thisExp.addLoop(instructionsLoop)  # add the loop to the experiment
thisInstructionsLoop = instructionsLoop.trialList[0]  # so we can initialise stimuli with some values
# abbreviate parameter names if possible (e.g. rgb = thisInstructionsLoop.rgb)
if thisInstructionsLoop != None:
    for paramName in thisInstructionsLoop:
        exec('{} = thisInstructionsLoop[paramName]'.format(paramName))

for thisInstructionsLoop in instructionsLoop:
    currentLoop = instructionsLoop
    # abbreviate parameter names if possible (e.g. rgb = thisInstructionsLoop.rgb)
    if thisInstructionsLoop != None:
        for paramName in thisInstructionsLoop:
            exec('{} = thisInstructionsLoop[paramName]'.format(paramName))

    # ------Prepare to start Routine "instructions"-------
    continueRoutine = True
    # update component parameters for each repeat
    text_instructions_top.setText(text_top)
    instructions_image.setImage(image)
    text_instructions_bottom.setText(text_bottom
)
    key_resp_instructions.keys = []
    key_resp_instructions.rt = []
    _key_resp_instructions_allKeys = []
    # keep track of which components have finished
    instructionsComponents = [text_instructions_top, instructions_image, text_instructions_bottom, key_resp_instructions]
    for thisComponent in instructionsComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    instructionsClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1

    # -------Run Routine "instructions"-------
    while continueRoutine:
        # get current time
        t = instructionsClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=instructionsClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame

        # *text_instructions_top* updates
        if text_instructions_top.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_instructions_top.frameNStart = frameN  # exact frame index
            text_instructions_top.tStart = t  # local t and not account for scr refresh
            text_instructions_top.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_instructions_top, 'tStartRefresh')  # time at next scr refresh
            text_instructions_top.setAutoDraw(True)

        # *instructions_image* updates
        if instructions_image.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            instructions_image.frameNStart = frameN  # exact frame index
            instructions_image.tStart = t  # local t and not account for scr refresh
            instructions_image.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(instructions_image, 'tStartRefresh')  # time at next scr refresh
            instructions_image.setAutoDraw(True)

        # *text_instructions_bottom* updates
        if text_instructions_bottom.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_instructions_bottom.frameNStart = frameN  # exact frame index
            text_instructions_bottom.tStart = t  # local t and not account for scr refresh
            text_instructions_bottom.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_instructions_bottom, 'tStartRefresh')  # time at next scr refresh
            text_instructions_bottom.setAutoDraw(True)

        # *key_resp_instructions* updates
        waitOnFlip = False
        if key_resp_instructions.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            key_resp_instructions.frameNStart = frameN  # exact frame index
            key_resp_instructions.tStart = t  # local t and not account for scr refresh
            key_resp_instructions.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(key_resp_instructions, 'tStartRefresh')  # time at next scr refresh
            key_resp_instructions.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(key_resp_instructions.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(key_resp_instructions.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if key_resp_instructions.status == STARTED and not waitOnFlip:
            theseKeys = key_resp_instructions.getKeys(keyList=advanceKeys, waitRelease=False)
            _key_resp_instructions_allKeys.extend(theseKeys)
            if len(_key_resp_instructions_allKeys):
                key_resp_instructions.keys = _key_resp_instructions_allKeys[-1].name  # just the last key pressed
                key_resp_instructions.rt = _key_resp_instructions_allKeys[-1].rt
                # a response ends the routine
                continueRoutine = False

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["q"]):
            terminate_task()

        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in instructionsComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished

        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # -------Ending Routine "instructions"-------
    for thisComponent in instructionsComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    instructionsLoop.addData('text_instructions_top.started', text_instructions_top.tStartRefresh)
    instructionsLoop.addData('text_instructions_top.stopped', text_instructions_top.tStopRefresh)
    instructionsLoop.addData('instructions_image.started', instructions_image.tStartRefresh)
    instructionsLoop.addData('instructions_image.stopped', instructions_image.tStopRefresh)
    instructionsLoop.addData('text_instructions_bottom.started', text_instructions_bottom.tStartRefresh)
    instructionsLoop.addData('text_instructions_bottom.stopped', text_instructions_bottom.tStopRefresh)
    # check responses
    if key_resp_instructions.keys in ['', [], None]:  # No response was made
        key_resp_instructions.keys = None
    instructionsLoop.addData('key_resp_instructions.keys',key_resp_instructions.keys)
    if key_resp_instructions.keys != None:  # we had a response
        instructionsLoop.addData('key_resp_instructions.rt', key_resp_instructions.rt)
    instructionsLoop.addData('key_resp_instructions.started', key_resp_instructions.tStartRefresh)
    instructionsLoop.addData('key_resp_instructions.stopped', key_resp_instructions.tStopRefresh)
    # the Routine "instructions" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
# completed 1.0 repeats of 'instructionsLoop'

# set up handler to look after randomisation of conditions etc
readingLoop = data.TrialHandler(nReps=1.0, method='sequential',
    extraInfo=expInfo, originPath=-1,
    trialList=data.importConditions(reading_condition_file, selection=reading_order[np.arange(session, reading_count)]),
    seed=None, name='readingLoop')
thisExp.addLoop(readingLoop)  # add the loop to the experiment
thisReadingLoop = readingLoop.trialList[0]  # so we can initialise stimuli with some values
# abbreviate parameter names if possible (e.g. rgb = thisReadingLoop.rgb)
if thisReadingLoop != None:
    for paramName in thisReadingLoop:
        exec('{} = thisReadingLoop[paramName]'.format(paramName))

for thisReadingLoop in readingLoop:
    currentLoop = readingLoop
    # abbreviate parameter names if possible (e.g. rgb = thisReadingLoop.rgb)
    if thisReadingLoop != None:
        for paramName in thisReadingLoop:
            exec('{} = thisReadingLoop[paramName]'.format(paramName))


    # ------Prepare to start Routine "start_cali"-------
    continueRoutine = True
    # the eyelink calibration routine was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    routineTimer.add(0.500000)
    # update component parameters for each repeat
    # keep track of which components have finished
    start_caliComponents = [cali_text]
    for thisComponent in start_caliComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    start_caliClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1

    # -------Run Routine "start_cali"-------
    while continueRoutine and routineTimer.getTime() > 0:
        # get current time
        t = start_caliClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=start_caliClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame

        # *cali_text* updates
        if cali_text.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            cali_text.frameNStart = frameN  # exact frame index
            cali_text.tStart = t  # local t and not account for scr refresh
            cali_text.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(cali_text, 'tStartRefresh')  # time at next scr refresh
            cali_text.setAutoDraw(True)
        if cali_text.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > cali_text.tStartRefresh + 0.5-frameTolerance:
                # keep track of stop time/frame for later
                cali_text.tStop = t  # not accounting for scr refresh
                cali_text.frameNStop = frameN  # exact frame index
                win.timeOnFlip(cali_text, 'tStopRefresh')  # time at next scr refresh
                cali_text.setAutoDraw(False)

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=['q']):
            terminate_task()

        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in start_caliComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished

        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # -------Ending Routine "start_cali"-------
    for thisComponent in start_caliComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    routineTimer.reset()

    # === EYELINK RUN CALIBRATION === #

    # === RUN CALIBRATION === #
    # skip this step if running the script in Dummy Mode
    if not dummy_mode:
        print('Running calibration...')
        try:
            el_tracker.doTrackerSetup() # calibrate, validate
        except RuntimeError as err:
            print('ERROR:', err)
            el_tracker.exitCalibration()

    # === START RECORDING === #
    # skip this step if eye-tracker's recording
    if not isETRecording:
        print('Starting recording...')
        # put tracker in idle/offline mode before recording
        el_tracker.setOfflineMode()

        # Start recording
        # arguments: sample_to_file, events_to_file, sample_over_link,
        # event_over_link (1-yes, 0-no)
        try:
            el_tracker.startRecording(1, 1, 1, 1)
        except RuntimeError as error:
            print("ERROR:", error)
        #    abort_trial()
        #    return pylink.TRIAL_ERROR

        # Allocate some time for the tracker to cache some samples
        pylink.pumpDelay(100)

        print('Done with start_recording script')

        # set var to true after start recording
        isETRecording = True

    # === END EYELINK CALIBRATION === #


    # --- Prepare to start Routine "wait_for_scanner" ---
    continueRoutine = True
    routineForceEnded = False
    # update component parameters for each repeat
    wait_resp.keys = []
    wait_resp.rt = []
    _wait_resp_allKeys = []
    # keep track of which components have finished
    wait_for_scannerComponents = [wait_resp, wait_text]
    for thisComponent in wait_for_scannerComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1

    # --- Run Routine "wait_for_scanner" ---
    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame

        # *wait_resp* updates
        waitOnFlip = False
        if wait_resp.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            wait_resp.frameNStart = frameN  # exact frame index
            wait_resp.tStart = t  # local t and not account for scr refresh
            wait_resp.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(wait_resp, 'tStartRefresh')  # time at next scr refresh
            wait_resp.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(wait_resp.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(wait_resp.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if wait_resp.status == STARTED and not waitOnFlip:
            theseKeys = wait_resp.getKeys(keyList=[triggerKey], waitRelease=False)
            _wait_resp_allKeys.extend(theseKeys)
            if len(_wait_resp_allKeys):
                wait_resp.keys = _wait_resp_allKeys[-1].name  # just the last key pressed
                wait_resp.rt = _wait_resp_allKeys[-1].rt
                # a response ends the routine
                continueRoutine = False

        # *wait_text* updates
        if wait_text.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            wait_text.frameNStart = frameN  # exact frame index
            wait_text.tStart = t  # local t and not account for scr refresh
            wait_text.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(wait_text, 'tStartRefresh')  # time at next scr refresh
            wait_text.setAutoDraw(True)

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["q"]):
            core.quit()

        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in wait_for_scannerComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished

        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # --- Ending Routine "wait_for_scanner" ---
    for thisComponent in wait_for_scannerComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.addData('wait_resp.started', wait_resp.tStartRefresh)
    thisExp.addData('wait_text.started', wait_text.tStartRefresh)
    # check responses
    if wait_resp.keys in ['', [], None]:  # No response was made
        wait_resp.keys = None
    thisExp.addData('wait_resp.keys',wait_resp.keys)
    if wait_resp.keys != None:  # we had a response
        thisExp.addData('wait_resp.rt', wait_resp.rt)
    thisExp.nextEntry()
    # the Routine "wait_for_scanner" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()


    # ------Prepare to start Routine "start_task"-------
    continueRoutine = True
    # the eyelink calibration routine was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    routineTimer.add(10.000000)
    # update component parameters for each repeat
    # keep track of which components have finished
    start_taskComponents = [beginning_text]
    for thisComponent in start_taskComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    start_taskClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1

    # -------Run Routine "start_task"-------
    while continueRoutine and routineTimer.getTime() > 0:
        # get current time
        t = start_taskClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=start_taskClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame

        # *beginning_text* updates
        if beginning_text.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            beginning_text.frameNStart = frameN  # exact frame index
            beginning_text.tStart = t  # local t and not account for scr refresh
            beginning_text.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(beginning_text, 'tStartRefresh')  # time at next scr refresh
            beginning_text.setAutoDraw(True)
        if beginning_text.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > beginning_text.tStartRefresh + 10.0-frameTolerance:
                # keep track of stop time/frame for later
                beginning_text.tStop = t  # not accounting for scr refresh
                beginning_text.frameNStop = frameN  # exact frame index
                win.timeOnFlip(beginning_text, 'tStopRefresh')  # time at next scr refresh
                beginning_text.setAutoDraw(False)

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=['q']):
            terminate_task()

        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in start_taskComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished

        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # -------Ending Routine "start_task"-------
    for thisComponent in start_taskComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.addData('beginning_text.started', beginning_text.tStartRefresh)
    thisExp.addData('beginning_text.stopped', beginning_text.tStopRefresh)
    # the Routine "init" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()


    # ------Prepare to start Routine "init_reading"-------
    continueRoutine = True

    # update component parameters for each repeat
    # get the current trial index
    index = readingLoop.thisTrialN
    # get the page number of current reading
    page_count = pages_count[index]

    if expInfo['type'] == 'eye tracking':
        # generate the error page indices ========================
        error_page = []
        error_fs = 2    # error occurs at most every 3 pages
        p1 = 1      # starts from the second page
        p2 = p1 + error_fs
        # page_count + 3 to include the last few pages
        while p2 < page_count + 3:
            # random draw a page between p1 and p2
            error_index = np.random.randint(p1, p2+1)
            # update p1 and p2
            p1 = error_index + 1        # consecutive error page is allowed
            p2 = p1 + error_fs
            # only record valid error_index
            if error_index < page_count:
                error_page.append(error_index)
        # ========================================================

        # determine the error type for each error page
        # 0: lexical
        # 1: gibberish
        # 2: no error
        error_type = [i % error_count for i in range(len(error_page))]
        np.random.shuffle(error_type)

        # set the page index
        error_page_index = 0
    # use seudo error page for probes
    elif expInfo['type'] == 'self-report':
        error_page = np.arange(page_count)
        error_type = [2] * page_count
        error_page_index = 0
    else:
        error_page = [] # no errors in brain imaging versions.

    # reading trial break
    if readingLoop.nRemaining != 0:
        isNextReading = 1
    else:
        isNextReading = 0

    # keep track of which components have finished
    init_readingComponents = []
    for thisComponent in init_readingComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    init_readingClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1

    # -------Run Routine "init_reading"-------
    while continueRoutine:
        # get current time
        t = init_readingClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=init_readingClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["q"]):
            terminate_task()

        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in init_readingComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished

        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # -------Ending Routine "init_reading"-------
    for thisComponent in init_readingComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    error_page_index = 0
    # the Routine "init_reading" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()

    # === set up variables for eye-tracking ===
    # initialize trial index
    page = 0

    # === EYELINK SEND MESSAGE ON SCREEN CHANGE === #
    el_tracker.sendMessage('Reading START')

    # === EEG MESSAGE ===
    if expInfo['type'] == 'eeg':
        eeg_msg = 'Reading START'
        #ser.write(bytes(eeg_msg, 'utf-8'))
        ser.write(bytearray([1]))

    # set up handler to look after randomisation of conditions etc
    # trialLoop = data.TrialHandler(nReps=readingnReps, method='sequential',

    # set up handler to look after randomisation of conditions etc
    trials = data.TrialHandler(nReps=1.0, method='sequential',
        extraInfo=expInfo, originPath=-1,
        trialList=data.importConditions(readingCond),
        seed=None, name='trials')
    thisExp.addLoop(trials)  # add the loop to the experiment
    thisTrial = trials.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
    if thisTrial != None:
        for paramName in thisTrial:
            exec('{} = thisTrial[paramName]'.format(paramName))

    for thisTrial in trials:
        currentLoop = trials
        # abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
        if thisTrial != None:
            for paramName in thisTrial:
                exec('{} = thisTrial[paramName]'.format(paramName))

        # ------Prepare to start Routine "init_error"-------
        continueRoutine = True
        # update component parameters for each repeat
        # default constants
        do_probes = 0
        image_displayed = image
        error_type_int = 2
        # update the error image based on their types of error
        # 0: image_lexical
        # 1: image_gibberish
        if (expInfo['type']=='eye tracking' or 'self-report') and (trials.thisTrialN == error_page[error_page_index]):
            # if the subject didn't find the error, show probe questions only
            do_probes = 1
            error_type_int = error_type[error_page_index]
            if error_type_int == 0:
                image_displayed = image_lexical
            elif error_type_int == 1:
                image_displayed = image_gibberish

            if error_page_index < (len(error_page)-1):
                error_page_index += 1
        # update log
        thisExp.addData('error_type', page_error_type[error_type_int]);
        # keep track of which components have finished
        init_errorComponents = []
        for thisComponent in init_errorComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        init_errorClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        frameN = -1

        # -------Run Routine "init_error"-------
        while continueRoutine:
            # get current time
            t = init_errorClock.getTime()
            tThisFlip = win.getFutureFlipTime(clock=init_errorClock)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame

            # check for quit (typically the Esc key)
            if endExpNow or defaultKeyboard.getKeys(keyList=["q"]):
                terminate_task()

            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in init_errorComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished

            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()

        # -------Ending Routine "init_error"-------
        for thisComponent in init_errorComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # the Routine "init_error" was not non-slip safe, so reset the non-slip timer
        routineTimer.reset()

        # ------Prepare to start Routine "trial"-------
        continueRoutine = True
        # update component parameters for each repeat
        reading_image.setImage(image_displayed)
        key_resp.keys = []
        key_resp.rt = []
        _key_resp_allKeys = []
        if expInfo['type'] == 'eye tracking':
            text_page_bottom.setText('Press SPACE to continue or X to report an error.\n')
        elif expInfo['type'] == 'self-report':
            text_page_bottom.setText('Press SPACE to continue or X to self-report mind wandering.\n')
        elif expInfo['type'] == 'eeg':
            text_page_bottom.setText('Press SPACE to continue.\n')
        elif expInfo['type'] == 'fmri':
            text_page_bottom.setText('Press the right-most button to continue.\n')

        repeat_page = 0
        # keep track of which components have finished
        trialComponents = [reading_image, cross, key_resp, text_page_bottom]
        for thisComponent in trialComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        trialClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        frameN = -1


        # === SEND EVENTS TO EYELINK === #
        print('Sending events to eyelink...')
        # send a "TRIALID" message to mark the start of a trial, see Data
        # Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
        page += 1
        el_tracker.sendMessage('TRIALID %d' % page)

        # record_status_message : show some info on the Host PC
        # here we show how many trial has been tested
        status_msg = 'TRIAL number %d' % page
        el_tracker.sendCommand("record_status_message '%s'" % status_msg)

        # === END EYELINK CODE === #

        # -------Run Routine "trial"-------
        while continueRoutine:
            # get current time
            t = trialClock.getTime()
            tThisFlip = win.getFutureFlipTime(clock=trialClock)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame

            # *reading_image* updates
            if reading_image.status == NOT_STARTED and tThisFlip >= fix_dur-frameTolerance:
                # keep track of start time/frame for later
                reading_image.frameNStart = frameN  # exact frame index
                reading_image.tStart = t  # local t and not account for scr refresh
                reading_image.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(reading_image, 'tStartRefresh')  # time at next scr refresh
                reading_image.setAutoDraw(True)

                # === EYELINK SEND MESSAGE ON SCREEN CHANGE === #
                el_tracker.sendMessage(f'displayed {image_displayed}')

                # === EEG MESSAGE ===
                if expInfo['type'] == 'eeg':
                    ser.write(bytearray([20]))


            if reading_image.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > reading_image.tStartRefresh + this_page_dur-frameTolerance:
                    # keep track of stop time/frame for later
                    reading_image.tStop = t  # not accounting for scr refresh
                    reading_image.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(reading_image, 'tStopRefresh')  # time at next scr refresh
                    reading_image.setAutoDraw(False)

            # *cross* updates
            if cross.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                cross.frameNStart = frameN  # exact frame index
                cross.tStart = t  # local t and not account for scr refresh
                cross.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(cross, 'tStartRefresh')  # time at next scr refresh
                cross.setAutoDraw(True)

                # === EYELINK SEND MESSAGE ON SCREEN CHANGE === #
                el_tracker.sendMessage('displayed cross')

                # === EEG MESSAGE ===
                if expInfo['type'] == 'eeg':
                    ser.write(bytearray([10]))

            if cross.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > cross.tStartRefresh + fix_dur-frameTolerance:
                    # keep track of stop time/frame for later
                    cross.tStop = t  # not accounting for scr refresh
                    cross.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(cross, 'tStopRefresh')  # time at next scr refresh
                    cross.setAutoDraw(False)

            # *key_resp* updates
            waitOnFlip = False
            if key_resp.status == NOT_STARTED and tThisFlip >= fix_dur-frameTolerance:
                # keep track of start time/frame for later
                key_resp.frameNStart = frameN  # exact frame index
                key_resp.tStart = t  # local t and not account for scr refresh
                key_resp.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(key_resp, 'tStartRefresh')  # time at next scr refresh
                key_resp.status = STARTED
                # keyboard checking is just starting
                waitOnFlip = True
                win.callOnFlip(key_resp.clock.reset)  # t=0 on next screen flip
                win.callOnFlip(key_resp.clearEvents, eventType='keyboard')  # clear events on next screen flip
            if key_resp.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > key_resp.tStartRefresh + this_page_dur-frameTolerance:
                    # keep track of stop time/frame for later
                    key_resp.tStop = t  # not accounting for scr refresh
                    key_resp.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(key_resp, 'tStopRefresh')  # time at next scr refresh
                    key_resp.status = FINISHED
            if key_resp.status == STARTED and not waitOnFlip:
                theseKeys = key_resp.getKeys(keyList = advanceKeys + [errorKey], waitRelease=False)
                _key_resp_allKeys.extend(theseKeys)
                if len(_key_resp_allKeys):
                    key_resp.keys = _key_resp_allKeys[-1].name  # just the last key pressed
                    key_resp.rt = _key_resp_allKeys[-1].rt
                    # a response ends the routine
                    continueRoutine = False
            if t>(fix_dur+this_page_dur-fade_dur):
                reading_image.opacity = (fix_dur+this_page_dur-t)/fade_dur
            else:
                reading_image.opacity = 1

            # *text_page_bottom* updates
            if text_page_bottom.status == NOT_STARTED and tThisFlip >= fix_dur-frameTolerance:
                # keep track of start time/frame for later
                text_page_bottom.frameNStart = frameN  # exact frame index
                text_page_bottom.tStart = t  # local t and not account for scr refresh
                text_page_bottom.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(text_page_bottom, 'tStartRefresh')  # time at next scr refresh
                text_page_bottom.setAutoDraw(True)
            if text_page_bottom.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > text_page_bottom.tStartRefresh + this_page_dur-frameTolerance:
                    # keep track of stop time/frame for later
                    text_page_bottom.tStop = t  # not accounting for scr refresh
                    text_page_bottom.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(text_page_bottom, 'tStopRefresh')  # time at next scr refresh
                    text_page_bottom.setAutoDraw(False)

            # check for quit (typically the Esc key)
            if endExpNow or defaultKeyboard.getKeys(keyList=["q"]):
                terminate_task()

            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in trialComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished

            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()

        # === EYELINK SEND MESSAGE ON SCREEN CHANGE === #
        el_tracker.sendMessage('Current Page END')

        # === EEG MESSAGE ===
        if expInfo['type'] == 'eeg':
            ser.write(bytearray([30]))

        # -------Ending Routine "trial"-------
        for thisComponent in trialComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        trials.addData('reading_image.started', reading_image.tStartRefresh)
        trials.addData('reading_image.stopped', reading_image.tStopRefresh)
        trials.addData('cross.started', cross.tStartRefresh)
        trials.addData('cross.stopped', cross.tStopRefresh)
        # check responses
        if key_resp.keys in ['', [], None]:  # No response was made
            key_resp.keys = None
        trials.addData('key_resp.keys',key_resp.keys)
        if key_resp.keys != None:  # we had a response
            trials.addData('key_resp.rt', key_resp.rt)
        trials.addData('key_resp.started', key_resp.tStartRefresh)
        trials.addData('key_resp.stopped', key_resp.tStopRefresh)
        trials.addData('text_page_bottom.started', text_page_bottom.tStartRefresh)
        trials.addData('text_page_bottom.stopped', text_page_bottom.tStopRefresh)
        print(key_resp.keys)
        if (key_resp.keys == errorKey) and (expInfo['type'] == 'eye tracking' or 'self-report'):
            do_probes = 1
            detect_error = True
            repeat_page = 1
            this_page_dur = fix_dur + page_dur - t
        else:
            if expInfo['type'] == 'self-report':
                detect_error = True
            else:
                detect_error = False
            repeat_page = 0
            this_page_dur = page_dur

        # the Routine "trial" was not non-slip safe, so reset the non-slip timer
        routineTimer.reset()

        # set up handler to look after randomisation of conditions etc
        probesLoop = data.TrialHandler(nReps=do_probes, method='sequential',
            extraInfo=expInfo, originPath=-1,
            trialList=[None],
            seed=None, name='probesLoop')
        thisExp.addLoop(probesLoop)  # add the loop to the experiment
        thisProbesLoop = probesLoop.trialList[0]  # so we can initialise stimuli with some values
        # abbreviate parameter names if possible (e.g. rgb = thisProbesLoop.rgb)
        if thisProbesLoop != None:
            for paramName in thisProbesLoop:
                exec('{} = thisProbesLoop[paramName]'.format(paramName))

        for thisProbesLoop in probesLoop:
            currentLoop = probesLoop
            # abbreviate parameter names if possible (e.g. rgb = thisProbesLoop.rgb)
            if thisProbesLoop != None:
                for paramName in thisProbesLoop:
                    exec('{} = thisProbesLoop[paramName]'.format(paramName))

            # ------Prepare to start Routine "error"-------
            continueRoutine = True
            # update component parameters for each repeat
            reading_image_error.setImage(image_displayed)
            if expInfo['type'] == 'self-report':
                text_error_bottom.setText('Click on where you zoned out or Press SPACE if NO Mind Wandering')
            else:
                text_error_bottom.setText('Click on the error or Press SPACE if there is no error.')
            # setup some python lists for storing info about the mouse_error
            mouse_error.clicked_name = []
            gotValidClick = False  # until a click is received
            key_resp_error.keys = []
            key_resp_error.rt = []
            _key_resp_error_allKeys = []
            # keep track of which components have finished
            errorComponents = [error_background, reading_image_error, text_error_bottom, mouse_error, key_resp_error]
            for thisComponent in errorComponents:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            errorClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
            frameN = -1

            # Make mouse visible
            win.mouseVisible = True

            el_tracker.sendMessage('Enter error page')
            # -------Run Routine "error"-------
            while (continueRoutine and detect_error):
                # get current time
                t = errorClock.getTime()
                tThisFlip = win.getFutureFlipTime(clock=errorClock)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame

                # *error_background* updates
                if error_background.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    error_background.frameNStart = frameN  # exact frame index
                    error_background.tStart = t  # local t and not account for scr refresh
                    error_background.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(error_background, 'tStartRefresh')  # time at next scr refresh
                    error_background.setAutoDraw(True)

                # *reading_image_error* updates
                if reading_image_error.status == NOT_STARTED and tThisFlip >= 0.5-frameTolerance:
                    # keep track of start time/frame for later
                    reading_image_error.frameNStart = frameN  # exact frame index
                    reading_image_error.tStart = t  # local t and not account for scr refresh
                    reading_image_error.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(reading_image_error, 'tStartRefresh')  # time at next scr refresh
                    reading_image_error.setAutoDraw(True)

                    # === EYELINK SEND MESSAGE ON SCREEN CHANGE === #
                    el_tracker.sendMessage(f'displayed errorimage {image_displayed}')

                # *text_error_bottom* updates
                if text_error_bottom.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    text_error_bottom.frameNStart = frameN  # exact frame index
                    text_error_bottom.tStart = t  # local t and not account for scr refresh
                    text_error_bottom.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(text_error_bottom, 'tStartRefresh')  # time at next scr refresh
                    text_error_bottom.setAutoDraw(True)
                # *mouse_error* updates
                if mouse_error.status == NOT_STARTED and t >= 0.5-frameTolerance:
                    # keep track of start time/frame for later
                    mouse_error.frameNStart = frameN  # exact frame index
                    mouse_error.tStart = t  # local t and not account for scr refresh
                    mouse_error.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(mouse_error, 'tStartRefresh')  # time at next scr refresh
                    mouse_error.status = STARTED
                    mouse_error.mouseClock.reset()
                    prevButtonState = mouse_error.getPressed()  # if button is down already this ISN'T a new click
                if mouse_error.status == STARTED:  # only update if started and not finished!
                    buttons = mouse_error.getPressed()
                    if buttons != prevButtonState:  # button state changed?
                        prevButtonState = buttons
                        if sum(buttons) > 0:  # state changed to a new click
                            # check if the mouse was inside our 'clickable' objects
                            gotValidClick = False
                            for obj in [reading_image_error,]:
                                if obj.contains(mouse_error):
                                    gotValidClick = True
                                    mouse_error.clicked_name.append(obj.name)
                            if gotValidClick:  # abort routine on response
                                continueRoutine = False

                # *key_resp_error* updates
                waitOnFlip = False
                if key_resp_error.status == NOT_STARTED and tThisFlip >= 0.5-frameTolerance:
                    # keep track of start time/frame for later
                    key_resp_error.frameNStart = frameN  # exact frame index
                    key_resp_error.tStart = t  # local t and not account for scr refresh
                    key_resp_error.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(key_resp_error, 'tStartRefresh')  # time at next scr refresh
                    key_resp_error.status = STARTED
                    # keyboard checking is just starting
                    waitOnFlip = True
                    win.callOnFlip(key_resp_error.clock.reset)  # t=0 on next screen flip
                    win.callOnFlip(key_resp_error.clearEvents, eventType='keyboard')  # clear events on next screen flip
                if key_resp_error.status == STARTED and not waitOnFlip:
                    theseKeys = key_resp_error.getKeys(keyList=advanceKeys, waitRelease=False)
                    _key_resp_error_allKeys.extend(theseKeys)
                    if len(_key_resp_error_allKeys):
                        key_resp_error.keys = _key_resp_error_allKeys[-1].name  # just the last key pressed
                        key_resp_error.rt = _key_resp_error_allKeys[-1].rt
                        # a response ends the routine
                        continueRoutine = False

                # check for quit (typically the Esc key)
                if endExpNow or defaultKeyboard.getKeys(keyList=["q"]):
                    terminate_task()

                # check if all components have finished
                if not continueRoutine:  # a component has requested a forced-end of Routine
                    break
                continueRoutine = False  # will revert to True if at least one component still running
                for thisComponent in errorComponents:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished

                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()

            # === EYELINK SEND MESSAGE ON SCREEN CHANGE === #
            el_tracker.sendMessage('Current Page END')

            # -------Ending Routine "error"-------
            if detect_error:
                for thisComponent in errorComponents:
                    if hasattr(thisComponent, "setAutoDraw"):
                        thisComponent.setAutoDraw(False)
                probesLoop.addData('error_background.started', error_background.tStartRefresh)
                probesLoop.addData('error_background.stopped', error_background.tStopRefresh)
                probesLoop.addData('reading_image_error.started', reading_image_error.tStartRefresh)
                probesLoop.addData('reading_image_error.stopped', reading_image_error.tStopRefresh)
                probesLoop.addData('text_error_bottom.started', text_error_bottom.tStartRefresh)
                probesLoop.addData('text_error_bottom.stopped', text_error_bottom.tStopRefresh)
                # store data for probesLoop (TrialHandler)
                x, y = mouse_error.getPos()
                buttons = mouse_error.getPressed()
                if sum(buttons):
                    # check if the mouse was inside our 'clickable' objects
                    gotValidClick = False
                    for obj in [reading_image_error,]:
                        if obj.contains(mouse_error):
                            gotValidClick = True
                            mouse_error.clicked_name.append(obj.name)
                probesLoop.addData('mouse_error.x', x)
                probesLoop.addData('mouse_error.y', y)
                probesLoop.addData('mouse_error.leftButton', buttons[0])
                probesLoop.addData('mouse_error.midButton', buttons[1])
                probesLoop.addData('mouse_error.rightButton', buttons[2])
                if len(mouse_error.clicked_name):
                    probesLoop.addData('mouse_error.clicked_name', mouse_error.clicked_name[0])
                probesLoop.addData('mouse_error.started', mouse_error.tStart)
                probesLoop.addData('mouse_error.stopped', mouse_error.tStop)
                # check responses
                if key_resp_error.keys in ['', [], None]:  # No response was made
                    key_resp_error.keys = None
                probesLoop.addData('key_resp_error.keys',key_resp_error.keys)
                if key_resp_error.keys != None:  # we had a response
                    probesLoop.addData('key_resp_error.rt', key_resp_error.rt)
                probesLoop.addData('key_resp_error.started', key_resp_error.tStartRefresh)
                probesLoop.addData('key_resp_error.stopped', key_resp_error.tStopRefresh)
            # the Routine "error" was not non-slip safe, so reset the non-slip timer
            routineTimer.reset()

            # ------Prepare to start Routine "probes"-------
            continueRoutine = True
            # update component parameters for each repeat
            slider_task.reset()
            slider_detailed.reset()
            slider_words.reset()
            slider_emotion.reset()
            # keep track of which components have finished
            probesComponents = [text_probe_instructions, text_task, slider_task, text_detailed, slider_detailed, text_words, slider_words, text_emotion, slider_emotion, button_probe]
            for thisComponent in probesComponents:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            probesClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
            frameN = -1

            # === EYELINK SEND MESSAGE ON SCREEN CHANGE === #
            el_tracker.sendMessage('displayed probes')
            # -------Run Routine "probes"-------
            while continueRoutine:
                # get current time
                t = probesClock.getTime()
                tThisFlip = win.getFutureFlipTime(clock=probesClock)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame

                # *text_probe_instructions* updates
                if text_probe_instructions.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    text_probe_instructions.frameNStart = frameN  # exact frame index
                    text_probe_instructions.tStart = t  # local t and not account for scr refresh
                    text_probe_instructions.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(text_probe_instructions, 'tStartRefresh')  # time at next scr refresh
                    text_probe_instructions.setAutoDraw(True)

                # *text_task* updates
                if text_task.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    text_task.frameNStart = frameN  # exact frame index
                    text_task.tStart = t  # local t and not account for scr refresh
                    text_task.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(text_task, 'tStartRefresh')  # time at next scr refresh
                    text_task.setAutoDraw(True)

                # *slider_task* updates
                if slider_task.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    slider_task.frameNStart = frameN  # exact frame index
                    slider_task.tStart = t  # local t and not account for scr refresh
                    slider_task.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(slider_task, 'tStartRefresh')  # time at next scr refresh
                    slider_task.setAutoDraw(True)

                # *text_detailed* updates
                if text_detailed.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    text_detailed.frameNStart = frameN  # exact frame index
                    text_detailed.tStart = t  # local t and not account for scr refresh
                    text_detailed.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(text_detailed, 'tStartRefresh')  # time at next scr refresh
                    text_detailed.setAutoDraw(True)

                # *slider_detailed* updates
                if slider_detailed.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    slider_detailed.frameNStart = frameN  # exact frame index
                    slider_detailed.tStart = t  # local t and not account for scr refresh
                    slider_detailed.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(slider_detailed, 'tStartRefresh')  # time at next scr refresh
                    slider_detailed.setAutoDraw(True)

                # *text_words* updates
                if text_words.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    text_words.frameNStart = frameN  # exact frame index
                    text_words.tStart = t  # local t and not account for scr refresh
                    text_words.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(text_words, 'tStartRefresh')  # time at next scr refresh
                    text_words.setAutoDraw(True)

                # *slider_words* updates
                if slider_words.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    slider_words.frameNStart = frameN  # exact frame index
                    slider_words.tStart = t  # local t and not account for scr refresh
                    slider_words.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(slider_words, 'tStartRefresh')  # time at next scr refresh
                    slider_words.setAutoDraw(True)

                # *text_emotion* updates
                if text_emotion.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    text_emotion.frameNStart = frameN  # exact frame index
                    text_emotion.tStart = t  # local t and not account for scr refresh
                    text_emotion.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(text_emotion, 'tStartRefresh')  # time at next scr refresh
                    text_emotion.setAutoDraw(True)

                # *slider_emotion* updates
                if slider_emotion.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    slider_emotion.frameNStart = frameN  # exact frame index
                    slider_emotion.tStart = t  # local t and not account for scr refresh
                    slider_emotion.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(slider_emotion, 'tStartRefresh')  # time at next scr refresh
                    slider_emotion.setAutoDraw(True)

                # *button_probe* updates
                if button_probe.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    button_probe.frameNStart = frameN  # exact frame index
                    button_probe.tStart = t  # local t and not account for scr refresh
                    button_probe.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(button_probe, 'tStartRefresh')  # time at next scr refresh
                    button_probe.setAutoDraw(True)
                if button_probe.status == STARTED:
                    # check whether button_probe has been pressed
                    if button_probe.isClicked:
                        if not button_probe.wasClicked:
                            button_probe.timesOn.append(button_probe.buttonClock.getTime()) # store time of first click
                            button_probe.timesOff.append(button_probe.buttonClock.getTime()) # store time clicked until
                        else:
                            button_probe.timesOff[-1] = button_probe.buttonClock.getTime() # update time clicked until
                        if not button_probe.wasClicked:
                            continueRoutine = False  # end routine when button_probe is clicked
                            None
                        button_probe.wasClicked = True  # if button_probe is still clicked next frame, it is not a new click
                    else:
                        button_probe.wasClicked = False  # if button_probe is clicked next frame, it is a new click
                else:
                    button_probe.buttonClock.reset() # keep clock at 0 if button hasn't started / has finished
                    button_probe.wasClicked = False  # if button_probe is clicked next frame, it is a new click

                # check for quit (typically the Esc key)
                if endExpNow or defaultKeyboard.getKeys(keyList=["q"]):
                    terminate_task()

                # check if all components have finished
                if not continueRoutine:  # a component has requested a forced-end of Routine
                    break
                continueRoutine = False  # will revert to True if at least one component still running
                for thisComponent in probesComponents:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished

                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()

            # -------Ending Routine "probes"-------
            for thisComponent in probesComponents:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            probesLoop.addData('text_probe_instructions.started', text_probe_instructions.tStartRefresh)
            probesLoop.addData('text_probe_instructions.stopped', text_probe_instructions.tStopRefresh)
            probesLoop.addData('text_task.started', text_task.tStartRefresh)
            probesLoop.addData('text_task.stopped', text_task.tStopRefresh)
            probesLoop.addData('slider_task.response', slider_task.getRating())
            probesLoop.addData('slider_task.rt', slider_task.getRT())
            probesLoop.addData('slider_task.started', slider_task.tStartRefresh)
            probesLoop.addData('slider_task.stopped', slider_task.tStopRefresh)
            probesLoop.addData('text_detailed.started', text_detailed.tStartRefresh)
            probesLoop.addData('text_detailed.stopped', text_detailed.tStopRefresh)
            probesLoop.addData('slider_detailed.response', slider_detailed.getRating())
            probesLoop.addData('slider_detailed.rt', slider_detailed.getRT())
            probesLoop.addData('slider_detailed.started', slider_detailed.tStartRefresh)
            probesLoop.addData('slider_detailed.stopped', slider_detailed.tStopRefresh)
            probesLoop.addData('text_words.started', text_words.tStartRefresh)
            probesLoop.addData('text_words.stopped', text_words.tStopRefresh)
            probesLoop.addData('slider_words.response', slider_words.getRating())
            probesLoop.addData('slider_words.rt', slider_words.getRT())
            probesLoop.addData('slider_words.started', slider_words.tStartRefresh)
            probesLoop.addData('slider_words.stopped', slider_words.tStopRefresh)
            probesLoop.addData('text_emotion.started', text_emotion.tStartRefresh)
            probesLoop.addData('text_emotion.stopped', text_emotion.tStopRefresh)
            probesLoop.addData('slider_emotion.response', slider_emotion.getRating())
            probesLoop.addData('slider_emotion.rt', slider_emotion.getRT())
            probesLoop.addData('slider_emotion.started', slider_emotion.tStartRefresh)
            probesLoop.addData('slider_emotion.stopped', slider_emotion.tStopRefresh)
            probesLoop.addData('button_probe.started', button_probe.tStartRefresh)
            probesLoop.addData('button_probe.stopped', button_probe.tStopRefresh)
            probesLoop.addData('button_probe.numClicks', button_probe.numClicks)
            if button_probe.numClicks:
               probesLoop.addData('button_probe.timesOn', button_probe.timesOn)
               probesLoop.addData('button_probe.timesOff', button_probe.timesOff)
            else:
               probesLoop.addData('button_probe.timesOn', "")
               probesLoop.addData('button_probe.timesOff', "")
            # the Routine "probes" was not non-slip safe, so reset the non-slip timer
            routineTimer.reset()
            thisExp.nextEntry()

        # completed do_probes repeats of 'probesLoop'

        # Make mouse invisible
        win.mouseVisible = False

        # set up handler to look after randomisation of conditions etc
        repeatLoop = data.TrialHandler(nReps=repeat_page, method='sequential',
            extraInfo=expInfo, originPath=-1,
            trialList=[None],
            seed=None, name='repeatLoop')
        thisExp.addLoop(repeatLoop)  # add the loop to the experiment
        thisRepeatLoop = repeatLoop.trialList[0]  # so we can initialise stimuli with some values
        # abbreviate parameter names if possible (e.g. rgb = thisRepeatLoop.rgb)
        if thisRepeatLoop != None:
            for paramName in thisRepeatLoop:
                exec('{} = thisRepeatLoop[paramName]'.format(paramName))

        for thisRepeatLoop in repeatLoop:
            currentLoop = repeatLoop
            # abbreviate parameter names if possible (e.g. rgb = thisRepeatLoop.rgb)
            if thisRepeatLoop != None:
                for paramName in thisRepeatLoop:
                    exec('{} = thisRepeatLoop[paramName]'.format(paramName))

            # ------Prepare to start Routine "trial"-------
            continueRoutine = True
            # update component parameters for each repeat
            reading_image.setImage(image_displayed)
            key_resp.keys = []
            key_resp.rt = []
            _key_resp_allKeys = []
            text_page_bottom.setText('Press SPACE to continue or X to report an error.\n')
            repeat_page = 0
            # keep track of which components have finished
            trialComponents = [reading_image, cross, key_resp, text_page_bottom]
            for thisComponent in trialComponents:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            trialClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
            frameN = -1

            # -------Run Routine "trial"-------
            while continueRoutine:
                # get current time
                t = trialClock.getTime()
                tThisFlip = win.getFutureFlipTime(clock=trialClock)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame

                # *reading_image* updates
                if reading_image.status == NOT_STARTED and tThisFlip >= fix_dur-frameTolerance:
                    # keep track of start time/frame for later
                    reading_image.frameNStart = frameN  # exact frame index
                    reading_image.tStart = t  # local t and not account for scr refresh
                    reading_image.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(reading_image, 'tStartRefresh')  # time at next scr refresh
                    reading_image.setAutoDraw(True)
                    el_tracker.sendMessage(f'RE: displayed {image_displayed}')
                if reading_image.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > reading_image.tStartRefresh + this_page_dur-frameTolerance:
                        # keep track of stop time/frame for later
                        reading_image.tStop = t  # not accounting for scr refresh
                        reading_image.frameNStop = frameN  # exact frame index
                        win.timeOnFlip(reading_image, 'tStopRefresh')  # time at next scr refresh
                        reading_image.setAutoDraw(False)

                # *cross* updates
                if cross.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    cross.frameNStart = frameN  # exact frame index
                    cross.tStart = t  # local t and not account for scr refresh
                    cross.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(cross, 'tStartRefresh')  # time at next scr refresh
                    cross.setAutoDraw(True)
                    el_tracker.sendMessage('RE: displayed cross')
                if cross.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > cross.tStartRefresh + fix_dur-frameTolerance:
                        # keep track of stop time/frame for later
                        cross.tStop = t  # not accounting for scr refresh
                        cross.frameNStop = frameN  # exact frame index
                        win.timeOnFlip(cross, 'tStopRefresh')  # time at next scr refresh
                        cross.setAutoDraw(False)

                # *key_resp* updates
                waitOnFlip = False
                if key_resp.status == NOT_STARTED and tThisFlip >= fix_dur-frameTolerance:
                    # keep track of start time/frame for later
                    key_resp.frameNStart = frameN  # exact frame index
                    key_resp.tStart = t  # local t and not account for scr refresh
                    key_resp.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(key_resp, 'tStartRefresh')  # time at next scr refresh
                    key_resp.status = STARTED
                    # keyboard checking is just starting
                    waitOnFlip = True
                    win.callOnFlip(key_resp.clock.reset)  # t=0 on next screen flip
                    win.callOnFlip(key_resp.clearEvents, eventType='keyboard')  # clear events on next screen flip
                if key_resp.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > key_resp.tStartRefresh + this_page_dur-frameTolerance:
                        # keep track of stop time/frame for later
                        key_resp.tStop = t  # not accounting for scr refresh
                        key_resp.frameNStop = frameN  # exact frame index
                        win.timeOnFlip(key_resp, 'tStopRefresh')  # time at next scr refresh
                        key_resp.status = FINISHED
                if key_resp.status == STARTED and not waitOnFlip:
                    theseKeys = key_resp.getKeys(keyList = advanceKeys + [errorKey], waitRelease=False)
                    _key_resp_allKeys.extend(theseKeys)
                    if len(_key_resp_allKeys):
                        key_resp.keys = _key_resp_allKeys[-1].name  # just the last key pressed
                        key_resp.rt = _key_resp_allKeys[-1].rt
                        # a response ends the routine
                        continueRoutine = False
                if t>(fix_dur+this_page_dur-fade_dur):
                    reading_image.opacity = (fix_dur+this_page_dur-t)/fade_dur
                else:
                    reading_image.opacity = 1

                # *text_page_bottom* updates
                if text_page_bottom.status == NOT_STARTED and tThisFlip >= fix_dur-frameTolerance:
                    # keep track of start time/frame for later
                    text_page_bottom.frameNStart = frameN  # exact frame index
                    text_page_bottom.tStart = t  # local t and not account for scr refresh
                    text_page_bottom.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(text_page_bottom, 'tStartRefresh')  # time at next scr refresh
                    text_page_bottom.setAutoDraw(True)
                if text_page_bottom.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > text_page_bottom.tStartRefresh + this_page_dur-frameTolerance:
                        # keep track of stop time/frame for later
                        text_page_bottom.tStop = t  # not accounting for scr refresh
                        text_page_bottom.frameNStop = frameN  # exact frame index
                        win.timeOnFlip(text_page_bottom, 'tStopRefresh')  # time at next scr refresh
                        text_page_bottom.setAutoDraw(False)

                # check for quit (typically the Esc key)
                if endExpNow or defaultKeyboard.getKeys(keyList=["q"]):
                    terminate_task()

                # check if all components have finished
                if not continueRoutine:  # a component has requested a forced-end of Routine
                    break
                continueRoutine = False  # will revert to True if at least one component still running
                for thisComponent in trialComponents:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished

                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()

            # === EYELINK SEND MESSAGE ON SCREEN CHANGE === #
            el_tracker.sendMessage('Current Page END')

            # -------Ending Routine "trial"-------
            for thisComponent in trialComponents:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            repeatLoop.addData('reading_image.started', reading_image.tStartRefresh)
            repeatLoop.addData('reading_image.stopped', reading_image.tStopRefresh)
            repeatLoop.addData('cross.started', cross.tStartRefresh)
            repeatLoop.addData('cross.stopped', cross.tStopRefresh)
            # check responses
            if key_resp.keys in ['', [], None]:  # No response was made
                key_resp.keys = None
            repeatLoop.addData('key_resp.keys',key_resp.keys)
            if key_resp.keys != None:  # we had a response
                repeatLoop.addData('key_resp.rt', key_resp.rt)
            repeatLoop.addData('key_resp.started', key_resp.tStartRefresh)
            repeatLoop.addData('key_resp.stopped', key_resp.tStopRefresh)
            repeatLoop.addData('text_page_bottom.started', text_page_bottom.tStartRefresh)
            repeatLoop.addData('text_page_bottom.stopped', text_page_bottom.tStopRefresh)
            print(key_resp.keys)
            this_page_dur = page_dur

            # the Routine "trial" was not non-slip safe, so reset the non-slip timer
            routineTimer.reset()
            thisExp.nextEntry()

        # completed do_probes repeats of 'repeatLoop'

        thisExp.nextEntry()

    # completed 1.0 repeats of 'trials'


    if (expInfo['type']=='eye tracking' or 'self-report') or expInfo['type']=='eeg':
        # ------Prepare to start Routine "comp_instructions"-------
        continueRoutine = True
        # update component parameters for each repeat
        instructions_image_2.setImage('instructions/questions.png')
        text_instructions_bottom_2.setText('Press SPACE to begin.')
        key_resp_instructions_2.keys = []
        key_resp_instructions_2.rt = []
        _key_resp_instructions_2_allKeys = []
        # keep track of which components have finished
        comp_instructionsComponents = [text_instructions_top_2, instructions_image_2, text_instructions_bottom_2, key_resp_instructions_2]
        for thisComponent in comp_instructionsComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        comp_instructionsClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        frameN = -1

        # -------Run Routine "comp_instructions"-------
        while continueRoutine:
            # get current time
            t = comp_instructionsClock.getTime()
            tThisFlip = win.getFutureFlipTime(clock=comp_instructionsClock)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame

            # *text_instructions_top_2* updates
            if text_instructions_top_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                text_instructions_top_2.frameNStart = frameN  # exact frame index
                text_instructions_top_2.tStart = t  # local t and not account for scr refresh
                text_instructions_top_2.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(text_instructions_top_2, 'tStartRefresh')  # time at next scr refresh
                text_instructions_top_2.setAutoDraw(True)

            # *instructions_image_2* updates
            if instructions_image_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                instructions_image_2.frameNStart = frameN  # exact frame index
                instructions_image_2.tStart = t  # local t and not account for scr refresh
                instructions_image_2.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(instructions_image_2, 'tStartRefresh')  # time at next scr refresh
                instructions_image_2.setAutoDraw(True)

            # *text_instructions_bottom_2* updates
            if text_instructions_bottom_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                text_instructions_bottom_2.frameNStart = frameN  # exact frame index
                text_instructions_bottom_2.tStart = t  # local t and not account for scr refresh
                text_instructions_bottom_2.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(text_instructions_bottom_2, 'tStartRefresh')  # time at next scr refresh
                text_instructions_bottom_2.setAutoDraw(True)

            # *key_resp_instructions_2* updates
            waitOnFlip = False
            if key_resp_instructions_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                key_resp_instructions_2.frameNStart = frameN  # exact frame index
                key_resp_instructions_2.tStart = t  # local t and not account for scr refresh
                key_resp_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(key_resp_instructions_2, 'tStartRefresh')  # time at next scr refresh
                key_resp_instructions_2.status = STARTED
                # keyboard checking is just starting
                waitOnFlip = True
                win.callOnFlip(key_resp_instructions_2.clock.reset)  # t=0 on next screen flip
                win.callOnFlip(key_resp_instructions_2.clearEvents, eventType='keyboard')  # clear events on next screen flip
            if key_resp_instructions_2.status == STARTED and not waitOnFlip:
                theseKeys = key_resp_instructions_2.getKeys(keyList=advanceKeys, waitRelease=False)
                _key_resp_instructions_2_allKeys.extend(theseKeys)
                if len(_key_resp_instructions_2_allKeys):
                    key_resp_instructions_2.keys = _key_resp_instructions_2_allKeys[-1].name  # just the last key pressed
                    key_resp_instructions_2.rt = _key_resp_instructions_2_allKeys[-1].rt
                    # a response ends the routine
                    continueRoutine = False

            # check for quit (typically the Esc key)
            if endExpNow or defaultKeyboard.getKeys(keyList=["q"]):
                terminate_task()

            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in comp_instructionsComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished

            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()

        # -------Ending Routine "comp_instructions"-------
        for thisComponent in comp_instructionsComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # the Routine "comp_instructions" was not non-slip safe, so reset the non-slip timer
        routineTimer.reset()

        # set up handler to look after randomisation of conditions etc
        questionsLoop = data.TrialHandler(nReps=1.0, method='sequential',
            extraInfo=expInfo, originPath=-1,
            trialList=data.importConditions(questionCond),
            seed=None, name='questionsLoop')
        thisExp.addLoop(questionsLoop)  # add the loop to the experiment
        thisQuestionsLoop = questionsLoop.trialList[0]  # so we can initialise stimuli with some values
        # abbreviate parameter names if possible (e.g. rgb = thisQuestionsLoop.rgb)
        if thisQuestionsLoop != None:
            for paramName in thisQuestionsLoop:
                exec('{} = thisQuestionsLoop[paramName]'.format(paramName))

        for thisQuestionsLoop in questionsLoop:
            currentLoop = questionsLoop
            # abbreviate parameter names if possible (e.g. rgb = thisQuestionsLoop.rgb)
            if thisQuestionsLoop != None:
                for paramName in thisQuestionsLoop:
                    exec('{} = thisQuestionsLoop[paramName]'.format(paramName))

            # ------Prepare to start Routine "comp_question"-------
            continueRoutine = True
            # update component parameters for each repeat
            options_text = '1. ' + option1 + '\n2. ' + option2 + '\n3. ' + option3 + '\n4. ' + option4 + '\n5. ' + option5
            text_options.alignText = 'left'
            text_question.setText(question_text)
            text_options.setText(options_text)
            key_resp_question.keys = []
            key_resp_question.rt = []
            _key_resp_question_allKeys = []
            text_question_instructions.setText('Press the number key of your answer.')
            # keep track of which components have finished
            comp_questionComponents = [text_question, text_options, key_resp_question, text_question_instructions]
            for thisComponent in comp_questionComponents:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            comp_questionClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
            frameN = -1

            el_tracker.sendMessage('displayed comprehension questions')

            # === EEG MESSAGE ===
            if expInfo['type'] == 'eeg':
                ser.write(bytearray([5]))

            # -------Run Routine "comp_question"-------
            while continueRoutine:
                # get current time
                t = comp_questionClock.getTime()
                tThisFlip = win.getFutureFlipTime(clock=comp_questionClock)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame

                # *text_question* updates
                if text_question.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    text_question.frameNStart = frameN  # exact frame index
                    text_question.tStart = t  # local t and not account for scr refresh
                    text_question.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(text_question, 'tStartRefresh')  # time at next scr refresh
                    text_question.setAutoDraw(True)
                # *text_options* updates
                if text_options.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    text_options.frameNStart = frameN  # exact frame index
                    text_options.tStart = t  # local t and not account for scr refresh
                    text_options.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(text_options, 'tStartRefresh')  # time at next scr refresh
                    text_options.setAutoDraw(True)

                # *key_resp_question* updates
                waitOnFlip = False
                if key_resp_question.status == NOT_STARTED and tThisFlip >= 0.5-frameTolerance:
                    # keep track of start time/frame for later
                    key_resp_question.frameNStart = frameN  # exact frame index
                    key_resp_question.tStart = t  # local t and not account for scr refresh
                    key_resp_question.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(key_resp_question, 'tStartRefresh')  # time at next scr refresh
                    key_resp_question.status = STARTED
                    # keyboard checking is just starting
                    waitOnFlip = True
                    win.callOnFlip(key_resp_question.clock.reset)  # t=0 on next screen flip
                    win.callOnFlip(key_resp_question.clearEvents, eventType='keyboard')  # clear events on next screen flip
                if key_resp_question.status == STARTED and not waitOnFlip:
                    theseKeys = key_resp_question.getKeys(keyList=['1', '2', '3', '4', '5'], waitRelease=False)
                    _key_resp_question_allKeys.extend(theseKeys)
                    if len(_key_resp_question_allKeys):
                        key_resp_question.keys = _key_resp_question_allKeys[-1].name  # just the last key pressed
                        key_resp_question.rt = _key_resp_question_allKeys[-1].rt
                        # a response ends the routine
                        continueRoutine = False

                # *text_question_instructions* updates
                if text_question_instructions.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    text_question_instructions.frameNStart = frameN  # exact frame index
                    text_question_instructions.tStart = t  # local t and not account for scr refresh
                    text_question_instructions.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(text_question_instructions, 'tStartRefresh')  # time at next scr refresh
                    text_question_instructions.setAutoDraw(True)

                # check for quit (typically the Esc key)
                if endExpNow or defaultKeyboard.getKeys(keyList=["q"]):
                    terminate_task()

                # check if all components have finished
                if not continueRoutine:  # a component has requested a forced-end of Routine
                    break
                continueRoutine = False  # will revert to True if at least one component still running
                for thisComponent in comp_questionComponents:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished


                # === EYELINK SEND MESSAGE ON SCREEN CHANGE === #

                # This code sends eyelink messages when the screen is about to change. The if statements are borrowed from the
                # psychopy auto-generated python code for the times when each stimulus is supposed to start.
                # Be sure to edit the start times (0.0, fix_dur below) to match those of the stimuli in your routine.

                # send *text_probe_instructions* updates to eye tracker
                if text_question.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance: # when it's about to be displayed
                    win.callOnFlip(el_tracker.sendMessage, 'displayed comprehension questions')  # send msg at next scr refresh

                # === END EYELINK CODE === #


                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()

            # -------Ending Routine "comp_question"-------
            for thisComponent in comp_questionComponents:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            questionsLoop.addData('text_question.started', text_question.tStartRefresh)
            questionsLoop.addData('text_question.stopped', text_question.tStopRefresh)
            questionsLoop.addData('text_options.started', text_options.tStartRefresh)
            questionsLoop.addData('text_options.stopped', text_options.tStopRefresh)
            # check responses
            if key_resp_question.keys in ['', [], None]:  # No response was made
                key_resp_question.keys = None
            questionsLoop.addData('key_resp_question.keys',key_resp_question.keys)
            if key_resp_question.keys != None:  # we had a response
                questionsLoop.addData('key_resp_question.rt', key_resp_question.rt)
            questionsLoop.addData('key_resp_question.started', key_resp_question.tStartRefresh)
            questionsLoop.addData('key_resp_question.stopped', key_resp_question.tStopRefresh)
            questionsLoop.addData('text_question_instructions.started', text_question_instructions.tStartRefresh)
            questionsLoop.addData('text_question_instructions.stopped', text_question_instructions.tStopRefresh)
            # the Routine "comp_question" was not non-slip safe, so reset the non-slip timer
            routineTimer.reset()
            thisExp.nextEntry()

        # completed 1.0 repeats of 'questionsLoop'
    # end if task type is eye tracking

    # set up handler to look after randomisation of conditions etc
    newReadingLoop = data.TrialHandler(nReps=isNextReading, method='sequential',
        extraInfo=expInfo, originPath=-1,
        trialList=[None],
        seed=None, name='newReadingLoop')
    thisExp.addLoop(newReadingLoop)  # add the loop to the experiment
    thisNewReadingLoop = newReadingLoop.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisNewReadingLoop.rgb)
    if thisNewReadingLoop != None:
        for paramName in thisNewReadingLoop:
            exec('{} = thisNewReadingLoop[paramName]'.format(paramName))

    for thisNewReadingLoop in newReadingLoop:
        currentLoop = newReadingLoop
        # abbreviate parameter names if possible (e.g. rgb = thisNewReadingLoop.rgb)
        if thisNewReadingLoop != None:
            for paramName in thisNewReadingLoop:
                exec('{} = thisNewReadingLoop[paramName]'.format(paramName))

        # ------Prepare to start Routine "new_reading"-------
        continueRoutine = True
        routineTimer.add(15.000000)
        # update component parameters for each repeat
        key_resp_next_reading.keys = []
        key_resp_next_reading.rt = []
        _key_resp_next_reading_allKeys = []
        # keep track of which components have finished
        new_readingComponents = [next_reading_text, key_resp_next_reading]
        for thisComponent in new_readingComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        new_readingClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        frameN = -1

        # -------Run Routine "new_reading"-------
        while continueRoutine and routineTimer.getTime() > 0:
            # get current time
            t = new_readingClock.getTime()
            tThisFlip = win.getFutureFlipTime(clock=new_readingClock)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame

            # *next_reading_text* updates
            if next_reading_text.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                next_reading_text.frameNStart = frameN  # exact frame index
                next_reading_text.tStart = t  # local t and not account for scr refresh
                next_reading_text.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(next_reading_text, 'tStartRefresh')  # time at next scr refresh
                next_reading_text.setAutoDraw(True)
            if next_reading_text.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > next_reading_text.tStartRefresh + 15-frameTolerance:
                    # keep track of stop time/frame for later
                    next_reading_text.tStop = t  # not accounting for scr refresh
                    next_reading_text.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(next_reading_text, 'tStopRefresh')  # time at next scr refresh
                    next_reading_text.setAutoDraw(False)

            # *key_resp_next_reading* updates
            waitOnFlip = False
            if key_resp_next_reading.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                key_resp_next_reading.frameNStart = frameN  # exact frame index
                key_resp_next_reading.tStart = t  # local t and not account for scr refresh
                key_resp_next_reading.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(key_resp_next_reading, 'tStartRefresh')  # time at next scr refresh
                key_resp_next_reading.status = STARTED
                # keyboard checking is just starting
                waitOnFlip = True
                win.callOnFlip(key_resp_next_reading.clock.reset)  # t=0 on next screen flip
                win.callOnFlip(key_resp_next_reading.clearEvents, eventType='keyboard')  # clear events on next screen flip
            if key_resp_next_reading.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > key_resp_next_reading.tStartRefresh + 15-frameTolerance:
                    # keep track of stop time/frame for later
                    key_resp_next_reading.tStop = t  # not accounting for scr refresh
                    key_resp_next_reading.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(key_resp_next_reading, 'tStopRefresh')  # time at next scr refresh
                    key_resp_next_reading.status = FINISHED
            if key_resp_next_reading.status == STARTED and not waitOnFlip:
                theseKeys = key_resp_next_reading.getKeys(keyList=advanceKeys, waitRelease=False)
                _key_resp_next_reading_allKeys.extend(theseKeys)
                if len(_key_resp_next_reading_allKeys):
                    key_resp_next_reading.keys = _key_resp_next_reading_allKeys[-1].name  # just the last key pressed
                    key_resp_next_reading.rt = _key_resp_next_reading_allKeys[-1].rt
                    # a response ends the routine
                    if expInfo['type'] == 'fmri':
                        continueRoutine = False
                    else:
                        continueRoutine = True

            # check for quit (typically the Esc key)
            if endExpNow or defaultKeyboard.getKeys(keyList=["q"]):
                terminate_task()

            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in new_readingComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished

            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()

        # -------Ending Routine "new_reading"-------
        for thisComponent in new_readingComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)

        newReadingLoop.addData('next_reading_text.started', next_reading_text.tStartRefresh)
        newReadingLoop.addData('next_reading_text.stopped', next_reading_text.tStopRefresh)
        # check responses
        if key_resp_next_reading.keys in ['', [], None]:  # No response was made
            key_resp_next_reading.keys = None
        newReadingLoop.addData('key_resp_next_reading.keys',key_resp_next_reading.keys)
        if key_resp_next_reading.keys != None:  # we had a response
            newReadingLoop.addData('key_resp_next_reading.rt', key_resp_next_reading.rt)
        newReadingLoop.addData('key_resp_next_reading.started', key_resp_next_reading.tStartRefresh)
        newReadingLoop.addData('key_resp_next_reading.stopped', key_resp_next_reading.tStopRefresh)
    # completed isNextReading repeats of 'newReadingLoop'

    thisExp.nextEntry()

# completed 1.0 repeats of 'readingLoop'



# === EYELINK STOP-EYE-TRACKER CODE === #

# ------Prepare to start Routine "stop_eyelink"-------
continueRoutine = True
routineTimer.add(0.300000)
# update component parameters for each repeat
# keep track of which components have finished
stop_eyelinkComponents = [text_sending]
for thisComponent in stop_eyelinkComponents:
    thisComponent.tStart = None
    thisComponent.tStop = None
    thisComponent.tStartRefresh = None
    thisComponent.tStopRefresh = None
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED
# reset timers
t = 0
_timeToFirstFrame = win.getFutureFlipTime(clock="now")
stop_eyelinkClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
frameN = -1

# -------Run Routine "stop_eyelink"-------
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = stop_eyelinkClock.getTime()
    tThisFlip = win.getFutureFlipTime(clock=stop_eyelinkClock)
    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame

    # *text_sending* updates
    if text_sending.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        text_sending.frameNStart = frameN  # exact frame index
        text_sending.tStart = t  # local t and not account for scr refresh
        text_sending.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(text_sending, 'tStartRefresh')  # time at next scr refresh
        text_sending.setAutoDraw(True)
    if text_sending.status == STARTED:
        # is it time to stop? (based on global clock, using actual start)
        if tThisFlipGlobal > text_sending.tStartRefresh + 0.3-frameTolerance:
            # keep track of stop time/frame for later
            text_sending.tStop = t  # not accounting for scr refresh
            text_sending.frameNStop = frameN  # exact frame index
            win.timeOnFlip(text_sending, 'tStopRefresh')  # time at next scr refresh
            text_sending.setAutoDraw(False)

    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in stop_eyelinkComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished

    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "stop_eyelink"-------
for thisComponent in stop_eyelinkComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
thisExp.addData('text_sending.started', text_sending.tStartRefresh)
thisExp.addData('text_sending.stopped', text_sending.tStopRefresh)
#"""
# End EyeLink recording: add 100 msec of data to catch final events
pylink.endRealTimeMode()
pylink.pumpDelay(100)
el_tracker.stopRecording()
while el_tracker.getkey(): # not sure what this is for
    pass

# Terminate the current trial first if the task terminated prematurely
error = el_tracker.isRecording()
if error == pylink.TRIAL_OK:
    el_tracker.abort()

# Put tracker in Offline mode
el_tracker.setOfflineMode()

# Clear the Host PC screen and wait for 500 ms
el_tracker.sendCommand('clear_screen 0')
pylink.msecDelay(500)

# Close the edf data file on the Host
el_tracker.closeDataFile()

# Show a file transfer message on the screen
#msg = 'EDF data is transferring from EyeLink Host PC...'
#show_msg(win, msg, wait_for_keypress=False)

# Download the EDF data file from the Host PC to a local data folder
# parameters: source_file_on_the_host, destination_file_on_local_drive
local_edf = os.path.join(session_folder, session_identifier + '.EDF')
try:
    el_tracker.receiveDataFile(edf_file, local_edf)
except RuntimeError as error:
    print('ERROR:', error)

# Close the link to the tracker.
el_tracker.close()

#"""

# After saving, continue on to next screen
continueRoutine = False

# === END EYELINK CODE === #


# ------Prepare to start Routine "goodbye"-------
continueRoutine = True
# update component parameters for each repeat
key_resp_goodbye.keys = []
key_resp_goodbye.rt = []
_key_resp_goodbye_allKeys = []
# keep track of which components have finished
goodbyeComponents = [goodbye_text_top, hash_text, goodbye_text_bottom, key_resp_goodbye]
for thisComponent in goodbyeComponents:
    thisComponent.tStart = None
    thisComponent.tStop = None
    thisComponent.tStartRefresh = None
    thisComponent.tStopRefresh = None
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED
# reset timers
t = 0
_timeToFirstFrame = win.getFutureFlipTime(clock="now")
goodbyeClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
frameN = -1

# -------Run Routine "goodbye"-------
while continueRoutine:
    # get current time
    t = goodbyeClock.getTime()
    tThisFlip = win.getFutureFlipTime(clock=goodbyeClock)
    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame

    # *goodbye_text_top* updates
    if goodbye_text_top.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        goodbye_text_top.frameNStart = frameN  # exact frame index
        goodbye_text_top.tStart = t  # local t and not account for scr refresh
        goodbye_text_top.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(goodbye_text_top, 'tStartRefresh')  # time at next scr refresh
        goodbye_text_top.setAutoDraw(True)

    # *hash_text* updates
    if hash_text.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        hash_text.frameNStart = frameN  # exact frame index
        hash_text.tStart = t  # local t and not account for scr refresh
        hash_text.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(hash_text, 'tStartRefresh')  # time at next scr refresh
        hash_text.setAutoDraw(True)

    # *goodbye_text_bottom* updates
    if goodbye_text_bottom.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        goodbye_text_bottom.frameNStart = frameN  # exact frame index
        goodbye_text_bottom.tStart = t  # local t and not account for scr refresh
        goodbye_text_bottom.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(goodbye_text_bottom, 'tStartRefresh')  # time at next scr refresh
        goodbye_text_bottom.setAutoDraw(True)

    # *key_resp_goodbye* updates
    waitOnFlip = False
    if key_resp_goodbye.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        key_resp_goodbye.frameNStart = frameN  # exact frame index
        key_resp_goodbye.tStart = t  # local t and not account for scr refresh
        key_resp_goodbye.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(key_resp_goodbye, 'tStartRefresh')  # time at next scr refresh
        key_resp_goodbye.status = STARTED
        # keyboard checking is just starting
        waitOnFlip = True
        win.callOnFlip(key_resp_goodbye.clock.reset)  # t=0 on next screen flip
        win.callOnFlip(key_resp_goodbye.clearEvents, eventType='keyboard')  # clear events on next screen flip
    if key_resp_goodbye.status == STARTED and not waitOnFlip:
        theseKeys = key_resp_goodbye.getKeys(keyList=['x'], waitRelease=False)
        _key_resp_goodbye_allKeys.extend(theseKeys)
        if len(_key_resp_goodbye_allKeys):
            key_resp_goodbye.keys = _key_resp_goodbye_allKeys[-1].name  # just the last key pressed
            key_resp_goodbye.rt = _key_resp_goodbye_allKeys[-1].rt
            # a response ends the routine
            continueRoutine = False

    # check for quit (typically the Esc key)
    if endExpNow or defaultKeyboard.getKeys(keyList=["q"]):
        terminate_task()

    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in goodbyeComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished

    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "goodbye"-------
for thisComponent in goodbyeComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
thisExp.addData('goodbye_text_top.started', goodbye_text_top.tStartRefresh)
thisExp.addData('goodbye_text_top.stopped', goodbye_text_top.tStopRefresh)
thisExp.addData('hash_text.started', hash_text.tStartRefresh)
thisExp.addData('hash_text.stopped', hash_text.tStopRefresh)
thisExp.addData('goodbye_text_bottom.started', goodbye_text_bottom.tStartRefresh)
thisExp.addData('goodbye_text_bottom.stopped', goodbye_text_bottom.tStopRefresh)
# check responses
if key_resp_goodbye.keys in ['', [], None]:  # No response was made
    key_resp_goodbye.keys = None
thisExp.addData('key_resp_goodbye.keys',key_resp_goodbye.keys)
if key_resp_goodbye.keys != None:  # we had a response
    thisExp.addData('key_resp_goodbye.rt', key_resp_goodbye.rt)
thisExp.addData('key_resp_goodbye.started', key_resp_goodbye.tStartRefresh)
thisExp.addData('key_resp_goodbye.stopped', key_resp_goodbye.tStopRefresh)
thisExp.nextEntry()
# the Routine "goodbye" was not non-slip safe, so reset the non-slip timer
routineTimer.reset()

# Flip one final time so any remaining win.callOnFlip()
# and win.timeOnFlip() tasks get executed before quitting
win.flip()

# these shouldn't be strictly necessary (should auto-save)
thisExp.saveAsWideText(filename+'.csv', delim='auto')
thisExp.saveAsPickle(filename)
logging.flush()
# make sure everything is closed down
thisExp.abort()  # or data files will save again on exit
win.close()
core.quit()
