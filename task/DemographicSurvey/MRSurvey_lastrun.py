#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy3 Experiment Builder (v2021.2.3),
    on Wed Nov 15 15:34:27 2023
If you publish work using this script the most relevant publication is:

    Peirce J, Gray JR, Simpson S, MacAskill M, Höchenberger R, Sogo H, Kastman E, Lindeløv JK. (2019) 
        PsychoPy2: Experiments in behavior made easy Behav Res 51: 195. 
        https://doi.org/10.3758/s13428-018-01193-y

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

from psychopy.hardware import keyboard



# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

# Store info about the experiment session
psychopyVersion = '2021.2.3'
expName = 'MRSurvey'  # from the Builder filename that created this script
expInfo = {'participant': '', 'session': '001'}
dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
if dlg.OK == False:
    core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName
expInfo['psychopyVersion'] = psychopyVersion

# Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
filename = _thisDir + os.sep + u'data/%s_%s_%s' % (expInfo['participant'], expName, expInfo['date'])

# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(name=expName, version='',
    extraInfo=expInfo, runtimeInfo=None,
    originPath='/Users/hsun11/Documents/GlassBrainLab/MindlessReading/GitHub/MindlessReading/DemographicSurvey/MRSurvey_lastrun.py',
    savePickle=True, saveWideText=True,
    dataFileName=filename)
# save a log file for detail verbose info
logFile = logging.LogFile(filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

endExpNow = False  # flag for 'escape' or other condition => quit the exp
frameTolerance = 0.001  # how close to onset before 'same' frame

# Start Code - component code to be run after the window creation

# Setup the Window
win = visual.Window(
    size=(1024, 768), fullscr=True, screen=0, 
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

# Setup eyetracking
ioDevice = ioConfig = ioSession = ioServer = eyetracker = None

# create a default keyboard (e.g. to check for escape)
defaultKeyboard = keyboard.Keyboard()

# Initialize components for Routine "survey1"
survey1Clock = core.Clock()
age_textbox = visual.TextBox2(
     win, text='What’s your age?', font='Open Sans',
     pos=(0, 0.45),units='height',     letterHeight=0.05,
     size=None, borderWidth=2.0,
     color='white', colorSpace='rgb',
     opacity=None,
     bold=False, italic=False,
     lineSpacing=1.0,
     padding=None,
     anchor='center',
     fillColor=None, borderColor=None,
     flipHoriz=False, flipVert=False,
     editable=True,
     name='age_textbox',
     autoLog=True,
)
gender_textbox = visual.TextBox2(
     win, text='What’s your gender?', font='Open Sans',
     pos=(0, 0.1),units='height',     letterHeight=0.05,
     size=None, borderWidth=2.0,
     color='white', colorSpace='rgb',
     opacity=None,
     bold=False, italic=False,
     lineSpacing=1.0,
     padding=None,
     anchor='center',
     fillColor=None, borderColor=None,
     flipHoriz=False, flipVert=False,
     editable=True,
     name='gender_textbox',
     autoLog=True,
)
handedness_textbox = visual.TextBox2(
     win, text='What’s your handedness?', font='Open Sans',
     pos=(0, -0.25),units='height',     letterHeight=0.05,
     size=None, borderWidth=2.0,
     color='white', colorSpace='rgb',
     opacity=None,
     bold=False, italic=False,
     lineSpacing=1.0,
     padding=None,
     anchor='center',
     fillColor=None, borderColor=None,
     flipHoriz=False, flipVert=False,
     editable=True,
     name='handedness_textbox',
     autoLog=True,
)
cont_button = visual.ButtonStim(win, 
    text='Click here to continue', font='Arvo',
    pos=(0, -0.45),units='height',
    letterHeight=0.03,
    size=None, borderWidth=0.0,
    fillColor='darkgrey', borderColor=None,
    color='white', colorSpace='rgb',
    opacity=None,
    bold=True, italic=False,
    padding=None,
    anchor='center',
    name='cont_button'
)
cont_button.buttonClock = core.Clock()

# Initialize components for Routine "survey2"
survey2Clock = core.Clock()
ADHD_textbox = visual.TextBox2(
     win, text='Have you been diagnosed with ADHD?', font='Open Sans',
     pos=(0, 0.3),units='height',     letterHeight=0.05,
     size=None, borderWidth=2.0,
     color='white', colorSpace='rgb',
     opacity=None,
     bold=False, italic=False,
     lineSpacing=1.0,
     padding=None,
     anchor='center',
     fillColor=None, borderColor=None,
     flipHoriz=False, flipVert=False,
     editable=True,
     name='ADHD_textbox',
     autoLog=True,
)
reading_disabilities_textbox = visual.TextBox2(
     win, text='Have you been diagnosed with any reading disabilities?', font='Open Sans',
     pos=(0, -0.2),units='height',     letterHeight=0.05,
     size=None, borderWidth=2.0,
     color='white', colorSpace='rgb',
     opacity=None,
     bold=False, italic=False,
     lineSpacing=1.0,
     padding=None,
     anchor='center',
     fillColor=None, borderColor=None,
     flipHoriz=False, flipVert=False,
     editable=True,
     name='reading_disabilities_textbox',
     autoLog=True,
)
close_button = visual.ButtonStim(win, 
    text='Click here when done', font='Arvo',
    pos=(0, -0.45),units='height',
    letterHeight=0.03,
    size=None, borderWidth=0.0,
    fillColor='darkgrey', borderColor=None,
    color='white', colorSpace='rgb',
    opacity=None,
    bold=True, italic=False,
    padding=None,
    anchor='center',
    name='close_button'
)
close_button.buttonClock = core.Clock()

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine 

# ------Prepare to start Routine "survey1"-------
continueRoutine = True
# update component parameters for each repeat
age_textbox.reset()
gender_textbox.reset()
handedness_textbox.reset()
# keep track of which components have finished
survey1Components = [age_textbox, gender_textbox, handedness_textbox, cont_button]
for thisComponent in survey1Components:
    thisComponent.tStart = None
    thisComponent.tStop = None
    thisComponent.tStartRefresh = None
    thisComponent.tStopRefresh = None
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED
# reset timers
t = 0
_timeToFirstFrame = win.getFutureFlipTime(clock="now")
survey1Clock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
frameN = -1

# -------Run Routine "survey1"-------
while continueRoutine:
    # get current time
    t = survey1Clock.getTime()
    tThisFlip = win.getFutureFlipTime(clock=survey1Clock)
    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *age_textbox* updates
    if age_textbox.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        age_textbox.frameNStart = frameN  # exact frame index
        age_textbox.tStart = t  # local t and not account for scr refresh
        age_textbox.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(age_textbox, 'tStartRefresh')  # time at next scr refresh
        age_textbox.setAutoDraw(True)
    
    # *gender_textbox* updates
    if gender_textbox.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        gender_textbox.frameNStart = frameN  # exact frame index
        gender_textbox.tStart = t  # local t and not account for scr refresh
        gender_textbox.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(gender_textbox, 'tStartRefresh')  # time at next scr refresh
        gender_textbox.setAutoDraw(True)
    
    # *handedness_textbox* updates
    if handedness_textbox.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        handedness_textbox.frameNStart = frameN  # exact frame index
        handedness_textbox.tStart = t  # local t and not account for scr refresh
        handedness_textbox.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(handedness_textbox, 'tStartRefresh')  # time at next scr refresh
        handedness_textbox.setAutoDraw(True)
    
    # *cont_button* updates
    if cont_button.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        cont_button.frameNStart = frameN  # exact frame index
        cont_button.tStart = t  # local t and not account for scr refresh
        cont_button.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(cont_button, 'tStartRefresh')  # time at next scr refresh
        cont_button.setAutoDraw(True)
    if cont_button.status == STARTED:
        # check whether cont_button has been pressed
        if cont_button.isClicked:
            if not cont_button.wasClicked:
                cont_button.timesOn.append(cont_button.buttonClock.getTime()) # store time of first click
                cont_button.timesOff.append(cont_button.buttonClock.getTime()) # store time clicked until
            else:
                cont_button.timesOff[-1] = cont_button.buttonClock.getTime() # update time clicked until
            if not cont_button.wasClicked:
                continueRoutine = False  # end routine when cont_button is clicked
                None
            cont_button.wasClicked = True  # if cont_button is still clicked next frame, it is not a new click
        else:
            cont_button.wasClicked = False  # if cont_button is clicked next frame, it is a new click
    else:
        cont_button.wasClicked = False  # if cont_button is clicked next frame, it is a new click
    
    # check for quit (typically the Esc key)
    if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
        core.quit()
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in survey1Components:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "survey1"-------
for thisComponent in survey1Components:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
thisExp.addData('age_textbox.text',age_textbox.text)
thisExp.addData('age_textbox.started', age_textbox.tStartRefresh)
thisExp.addData('age_textbox.stopped', age_textbox.tStopRefresh)
thisExp.addData('gender_textbox.text',gender_textbox.text)
thisExp.addData('gender_textbox.started', gender_textbox.tStartRefresh)
thisExp.addData('gender_textbox.stopped', gender_textbox.tStopRefresh)
thisExp.addData('handedness_textbox.text',handedness_textbox.text)
thisExp.addData('handedness_textbox.started', handedness_textbox.tStartRefresh)
thisExp.addData('handedness_textbox.stopped', handedness_textbox.tStopRefresh)
thisExp.addData('cont_button.started', cont_button.tStartRefresh)
thisExp.addData('cont_button.stopped', cont_button.tStopRefresh)
thisExp.addData('cont_button.numClicks', cont_button.numClicks)
if cont_button.numClicks:
   thisExp.addData('cont_button.timesOn', cont_button.timesOn)
   thisExp.addData('cont_button.timesOff', cont_button.timesOff)
else:
   thisExp.addData('cont_button.timesOn', "")
   thisExp.addData('cont_button.timesOff', "")
# the Routine "survey1" was not non-slip safe, so reset the non-slip timer
routineTimer.reset()

# ------Prepare to start Routine "survey2"-------
continueRoutine = True
# update component parameters for each repeat
ADHD_textbox.reset()
reading_disabilities_textbox.reset()
# keep track of which components have finished
survey2Components = [ADHD_textbox, reading_disabilities_textbox, close_button]
for thisComponent in survey2Components:
    thisComponent.tStart = None
    thisComponent.tStop = None
    thisComponent.tStartRefresh = None
    thisComponent.tStopRefresh = None
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED
# reset timers
t = 0
_timeToFirstFrame = win.getFutureFlipTime(clock="now")
survey2Clock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
frameN = -1

# -------Run Routine "survey2"-------
while continueRoutine:
    # get current time
    t = survey2Clock.getTime()
    tThisFlip = win.getFutureFlipTime(clock=survey2Clock)
    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *ADHD_textbox* updates
    if ADHD_textbox.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        ADHD_textbox.frameNStart = frameN  # exact frame index
        ADHD_textbox.tStart = t  # local t and not account for scr refresh
        ADHD_textbox.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(ADHD_textbox, 'tStartRefresh')  # time at next scr refresh
        ADHD_textbox.setAutoDraw(True)
    
    # *reading_disabilities_textbox* updates
    if reading_disabilities_textbox.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        reading_disabilities_textbox.frameNStart = frameN  # exact frame index
        reading_disabilities_textbox.tStart = t  # local t and not account for scr refresh
        reading_disabilities_textbox.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(reading_disabilities_textbox, 'tStartRefresh')  # time at next scr refresh
        reading_disabilities_textbox.setAutoDraw(True)
    
    # *close_button* updates
    if close_button.status == NOT_STARTED and tThisFlip >= 1.0-frameTolerance:
        # keep track of start time/frame for later
        close_button.frameNStart = frameN  # exact frame index
        close_button.tStart = t  # local t and not account for scr refresh
        close_button.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(close_button, 'tStartRefresh')  # time at next scr refresh
        close_button.setAutoDraw(True)
    if close_button.status == STARTED:
        # check whether close_button has been pressed
        if close_button.isClicked:
            if not close_button.wasClicked:
                close_button.timesOn.append(close_button.buttonClock.getTime()) # store time of first click
                close_button.timesOff.append(close_button.buttonClock.getTime()) # store time clicked until
            else:
                close_button.timesOff[-1] = close_button.buttonClock.getTime() # update time clicked until
            if not close_button.wasClicked:
                continueRoutine = False  # end routine when close_button is clicked
                None
            close_button.wasClicked = True  # if close_button is still clicked next frame, it is not a new click
        else:
            close_button.wasClicked = False  # if close_button is clicked next frame, it is a new click
    else:
        close_button.wasClicked = False  # if close_button is clicked next frame, it is a new click
    
    # check for quit (typically the Esc key)
    if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
        core.quit()
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in survey2Components:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "survey2"-------
for thisComponent in survey2Components:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
thisExp.addData('ADHD_textbox.text',ADHD_textbox.text)
thisExp.addData('ADHD_textbox.started', ADHD_textbox.tStartRefresh)
thisExp.addData('ADHD_textbox.stopped', ADHD_textbox.tStopRefresh)
thisExp.addData('reading_disabilities_textbox.text',reading_disabilities_textbox.text)
thisExp.addData('reading_disabilities_textbox.started', reading_disabilities_textbox.tStartRefresh)
thisExp.addData('reading_disabilities_textbox.stopped', reading_disabilities_textbox.tStopRefresh)
thisExp.addData('close_button.started', close_button.tStartRefresh)
thisExp.addData('close_button.stopped', close_button.tStopRefresh)
thisExp.addData('close_button.numClicks', close_button.numClicks)
if close_button.numClicks:
   thisExp.addData('close_button.timesOn', close_button.timesOn)
   thisExp.addData('close_button.timesOff', close_button.timesOff)
else:
   thisExp.addData('close_button.timesOn', "")
   thisExp.addData('close_button.timesOff', "")
# the Routine "survey2" was not non-slip safe, so reset the non-slip timer
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
