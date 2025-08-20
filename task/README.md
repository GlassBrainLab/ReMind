# ReMind Task Folder

## Stimulus Creation script 

The stimulus creation script takes in text file, font size, and lines per page and writes the text from the file to individual pages saved as images. The position on the page of each word is recorded and written to a csv file for each page. 

## Updates in this branch: 

 - Dynamic Error replacement and image generation. In the load_text function, the script parses the text file for "@Error" messages which include what to replace and the type of error. During replacement and image generation, if an error cannot be implemented, the script should show which text section and error. 

## Text file formatting

 For this dynamic error implementation to work, the text file needs to be in a specific format. See the [example_text.txt](StimulusCreation/example_text/example_text.txt) for a complete example. **IMPORTANT: Formatting must be followed exactly!**

## Known issues 

 - Text File **must** be in the format shown in the example file. 

 - Multiline comments **do not** work. Only one comment allowed per section for now. 
