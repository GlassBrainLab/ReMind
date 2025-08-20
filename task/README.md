# ReMind task Folder
## reading
This folder contains the PsychoPy task (`Reading/MindlessReadingTaskSelfReport.py`) along with the required image and text files.  
To run the task, open the Python file in PsychoPy and execute it from there.  

## demographics
This folder contains a PsychoPy survey script for collecting demographic information. 

## stimulus_creation
The stimulus creation script takes in text file, font size, and lines per page and writes the text from the file to individual pages saved as images. The position on the page of each word is recorded and written to a csv file for each page. 

### Text file formatting

 For this dynamic error implementation to work, the text file needs to be in a specific format. See the [example_text.txt](StimulusCreation/example_text/example_text.txt) for a complete example. **IMPORTANT: Formatting must be followed exactly!**

### Known issues 

 - Text File **must** be in the format shown in the example file. 

 - Multiline comments **do not** work. Only one comment allowed per section for now. 
