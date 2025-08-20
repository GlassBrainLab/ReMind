'''
StimulusCreation.py

To use this script in practice, create a new script, import StimulusCreation, and call StimulusCreation.create_stimulus(text file, num chars, lines per page) passing in just the text file name as a string. Process shown below...

import StimulusCreation
StimulusCreation.create_stimulus('file_name.txt', num chars on line, lines per page)

also shown in driver file

Created 4/2021 by Spencer Dooley
Updated 6/30/21 by DJ - debugging, cleanup, comments, added conditions file.
Updated 9/19/21 by George Spearing - use image width and font size to determine character spacing
                                    - Line spacing derived from the lines_per_page and image height
Updated 9/19/21 by Haorui Sun - indent the first line of a paragraph without
                                manually placing '?' sign
Updated 09/23/21 by George Spearing - Adding in Error parsing from text file, errors will now change
                                        the text in the corresponding page and save the page as that error type
Updated 09/26/21 by George Spearing - Adding Error display and comments to show which errors could not be implemented

Updated 10/20/21 by George Spearing - Added ability to automatically detect, record, and replace errors in text
                                    - Error symbol in text is "%" at the start of the word. gets replaced for output
TODO: better comments for changes
TODO: reliability and full testing (when does it break)
'''

# Import packages
from PIL import Image, ImageDraw, ImageFont
import textwrap
import cv2
from pytesseract import pytesseract
from pytesseract import Output
import numpy as np, pandas as pd
import os

# Function to take in text file ad return a list of strings - each string contains n characters
def load_text(text_file, characters_per_line):
    """
    convert a text file to a list of strings, removing comment lines (starting with ###) and replacing question marks (denoting new paragraphs) with 3 spaces.

    Parameters
    ----------
    text_file : str
        Path to text file to be turned into strings.
    characters_per_line : int
        Number of characters per line.

    Returns
    -------
    text_lines : list
        List of strings of length <=characters_per_line.

    """

    # read in text file to a list of strings
    try:
        with open(text_file, "r",encoding='utf-8') as doc:
            text_lines = doc.readlines()
    except UnicodeDecodeError:
        print(f'Reading {text_file} with UTF-8 encoding failed. Trying UTF-16 encoding...')
        with open(text_file, "r",encoding='utf-16') as doc:
            text_lines = doc.readlines()
    text_lines = list(text_lines)

    # remove comments
    for line in text_lines:
        if line.startswith("###"):
            text_lines.remove(line)


    # create an array of errors
    text_errors = t = [ [0]*6 for i in range(len(text_lines))]
    line_index = -1
    col_index = 0
    for line in text_lines:
        if line.startswith("@"):
            error_line = line.split("; ")
            text_errors[line_index][col_index+1] = error_line
            col_index += 1
            if col_index > 4:
                col_index = 0
        else:
            line_index += 1

    # remove the error trackers
    total_lines = len(text_lines)
    removed_lines = 0
    index = 0
    while((index+removed_lines <total_lines)):
        # print(text_lines[index])
        if text_lines[index].startswith("@"):
            del(text_lines[index])
            removed_lines += 1
        else:
            index += 1


    # format paragraphs
    for line_index, line in enumerate(text_lines):
        if line.startswith("?"):
            line = "   " + line[1:]  # replace ? (code for new paragraph) with 3 spaces
            text_lines[line_index] = line
        if (line == "\n"):  # indent the first line of a paragraph
            text_lines[line_index + 1]


    # create multiple versions of the text with replacing errors
    # array to hold the different texts (control + 5 error types per paragraph)
    multi_text_lines = [ [0]*6 for i in range(len(text_lines))]

    # start with the control (no implated errors)
    column_index = 0
    for line_index, line in enumerate(text_lines):
        multi_text_lines[line_index][column_index] = line


    # add one type of error to each paragrph
    # counter for total errors added
    error_counter = 0
    failed_index = []
    loc_count = 0
    error_word_index = []


    # error type one for each paragrph
    for column_index in range(1,6):
        for line_index, line in enumerate(text_lines):
            if text_errors[line_index][column_index] != 0:
                search_key = text_errors[line_index][column_index][1]
                replace_key = text_errors[line_index][column_index][2]

                # if the search key exists, replace it
                if (search_key != 'none' and search_key in line):
                    # add to counter
                    error_counter += 1
                    multi_text_lines[line_index][column_index] = text_lines[line_index].replace(search_key, replace_key)

                # else, add to failed index and use the control
                else:
                    failed_index.append(f'Paragraph: {line_index//2+1}, error type: {text_errors[line_index][column_index][3]}')
                    multi_text_lines[line_index][column_index] = text_lines[line_index]


    # if failed to implant errors, show which ones
    print(f'Errors Implanted: {error_counter}')
    if(len(failed_index)>0):
        print("Failed Indexes")
        for failed in failed_index:
            print(failed)

    # list for full readings
    full_readings_with_multi_errors = [0]*6

    # wrap the text
    for column_final in range(6):
        wrapped_text = []
        for line_index in range(len(text_lines)):
            if (multi_text_lines[line_index][column_final]!=0):
                texto = multi_text_lines[line_index][column_final]

                line = textwrap.wrap(texto, width=characters_per_line)
                wrapped_text.append(line)

        #combined full wrapped text to one list
        full_text = [item for sublist in wrapped_text for item in sublist]

        # add error line to master list
        full_readings_with_multi_errors[column_final] = full_text


    return full_readings_with_multi_errors


# Function that creates n (user input) blank pages
def create_pages(page_count, error_type, image_width=1050,image_height=900,image_prefix='page'):
    """
    Create and save blank pages with naming convention

    Parameters
    ----------
    page_count : int
        Number of pages to save.
    image_width : int
        Width of image to create, in pixels. The default is 1050.
    image_height : int
        Height of image to create, in pixels. The default is 900.
    image_prefix : str
        Start of output image filename. 2-digit page number and .png will be appended to the end.

    Returns
    -------
    filenames : list
        List of filenames where the images were saved.

    """
    # set up
    filenames = []

    # # set up folder
    # if not(os.path.isdir(f'{image_prefix}/{error_type}')):
    #     print(image_prefix)
    #     os.makedirs(f'{image_prefix}/{error_type}', exist_ok=True)

    # Step through images and create files
    for page_index in range(page_count):
        # filename=f"{image_prefix}{page_index:02d}_{error_type}.png"
        filename=f"{image_prefix}{page_index:02d}.png"  # error type is now embedded in prefix
        image = Image.new(mode = "RGB", size = (image_width,image_height), color = "gray")
        filenames.append(filename)
        image.save(filename)


    return filenames


# Function that takes in text from load_text function, the filename of the page it is writing to
# the number of lines wanted on the page, and the space between lines of text
def write_to_page(text_lines, image_file, index_offset, lines_per_page, line_spacing, font_name='courier.ttf',font_size=40,is_error_checking_on=False):
    """
    Write the next few lines in a list of strings to an image

    Parameters
    ----------
    text_lines : list
        List of strings to be printed to an image.
    image_file : str
        Filename of image to be written.
    lines_per_page : int
        Number of lines to be written to the page.
    line_spacing : int
        Space between lines, in pixels.
    font_name : str, optional
        Filename of font. The default is 'courier.ttf'.
    font_size : float, optional
        Size of font in points. The default is 40.
    is_error_checking_on: bool, optional
        Whether a % sign means an error and should be removed.

    Returns
    -------
    None.

    """

    # Set up image
    lines_to_write = min(len(text_lines),lines_per_page) # write no more than the number of lines remaining.
    im = Image.open(image_file)
    draw = ImageDraw.Draw(im)
    pos=0
    font = ImageFont.truetype(font_name,font_size)

    # Write text to image
    for line_index in range(lines_to_write):
        draw.text((0,pos), text_lines[line_index], font=font, fill=(10,10,0))
        pos += line_spacing

    # Save the image
    im.save(image_file)

    ## Read back in to replace errors and get indexes
    img = cv2.imread(image_file)
    d = pytesseract.image_to_data(img, output_type=Output.DICT) # get info

    # remove the empty lines
    d['text'] = list(filter(None, d['text']))


    error_indexes = []
    index_count = index_offset
    for word in d['text']:

        if is_error_checking_on and ('%' in word):
            error_indexes.append(index_count)
        index_count += 1

    # if we have errors, we need to re-write the pages
    # this is a brute force of just deleting and redoing the page.
    # very time consuming
    if (len(error_indexes)>0):
        # delete the file
        if os.path.exists(image_file):
            # get the image shape from the saved image
            image_height, image_width, channels = img.shape
            # remove the current file (so we can write the same name file)
            os.system(f"rm {image_file}")
            # create the image
            image = Image.new(mode = "RGB", size = (image_width, image_height), color = "gray")
            # save the image
            image.save(image_file)

        # create new image and add concents
        im = Image.open(image_file)
        draw = ImageDraw.Draw(im)
        pos=0
        # Write text to image
        for line_index in range(lines_to_write):
            # print(text_lines[line_index])
            # print(word)
            if is_error_checking_on and ('%' in text_lines[line_index]):
                # print(text_lines[line_index])
                text_lines[line_index] = text_lines[line_index].replace('%', "")
                # print(text_lines[line_index])

            draw.text((0,pos), text_lines[line_index], font=font, fill=(10,10,0))
            pos += line_spacing
        # Save the image
        im.save(image_file)

        # print(error_indexes)

    return index_count, error_indexes






# Function that creates csv file with position & size of each word.
def generate_data(image_files, error_indexes, coordinate_file='coordinates.csv'):
    """
    Create csv file with position & size of each word

    Parameters
    ----------
    image_files : list of strings
        Image files to be read.
    coordinate_file : str, optional
        Path to coordinate file you wish to write. The default is 'coordinates.csv'.

    Returns
    -------
    None.

    """
    # Set up
    words=[]
    left=[]
    top=[]
    width=[]
    height=[]
    page=[]

    # Read file and get info about each word using OCR
    for page_index,image_file in enumerate(image_files):
        img = cv2.imread(image_file)
        d = pytesseract.image_to_data(img, output_type=Output.DICT) # get info
        words_temp, left_temp, top_temp, width_temp, height_temp = d["text"], d["left"], d["top"], d["width"], d["height"] # extract info
        words.extend(words_temp), left.extend(left_temp), top.extend(top_temp), width.extend(width_temp), height.extend(height_temp) # add to lists
        page.extend(np.ones_like(left_temp)*page_index)

    # Place results in a dataframe
    cords = pd.DataFrame(list(zip(words, left, top, width, height, page)),columns =['words', 'left', 'top', 'width', 'height', 'page'])
    cords = cords[cords.words != ''] # remove empty words
    cords.reset_index(inplace=True,drop=True) # reset indices use "inplace" to modify the list without having to return anything

    # Add columns for center and proportion of image
    cords['center_x'] = cords['left']+(cords['width']/2)
    cords['center_y'] = cords['top']+(cords['height']/2)
    print(f'image shape: {img.shape} (expected 900, 1050)')
    cords['prop_height'] = cords['height']/img.shape[0]
    cords['prop_width'] = cords['width']/img.shape[1]

    # generate error column list
    word_indexes = list(cords['words'].index)
    error_column = [0]*len(cords['words'])
    for word_index, index in enumerate(word_indexes):
        if index in error_indexes:
            error_column[word_index] = 1

    # add the error column to the coordinates file
    cords['is_error'] = error_column
    cords.to_csv(coordinate_file)


# Wrapper function to create stimuli for reading task.
def create_stimulus(text_file, lines_per_page, image_width=1050,
                    image_height=900, font_name='courier.ttf',font_size=40,
                    image_prefix='page',conditions_file='images.csv',
                    coordinate_file='coordinates.csv',max_page_count=np.inf):
    """
    Wrapper function to create stimuli.

    Parameters
    ----------
    text_file : str
        Path to text file to be turned into strings.
    lines_per_page : int
        Number of lines to be written to each page.
    image_width : int
        Width of image to create, in pixels. The default is 1050.
    image_height : int
        Height of image to create, in pixels. The default is 900.
    font_name : str, optional
        Filename of font. The default is 'courier.ttf'.
    font_size : float, optional
        Size of font in points. The default is 40.
    image_prefix : str
        Start of output image filename. 2-digit page number and .png will be appended to the end.
    conditions_file : str, optional
        Path to PsychoPy conditions file (list of images) you wish to write. The default is 'images.csv'.
    coordinate_file : str, optional
        Path to coordinate file you wish to write. The default is 'coordinates.csv'.
    max_page_count : int, optional
        Max number of pages to make. The default is np.inf (no max).

    Returns
    -------
    None.

    """
    # Set up
    # pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # Path to tesseract.exe, required for windows computers?

    error_options = ['control','lexical','syntact','semantic','discourse','gibberish']

    # wrap text using input for max number of characters per line
    # get the width of a single character
    font = ImageFont.truetype(font_name,font_size)
    single_character_width = font.getsize(' ') # get the width of one chracter

    # use width of single letter to determine characters per line to fit
    characters_per_line = int(image_width / single_character_width[0])
    print(f'   {characters_per_line} characters per line.')

    # Read in text file
    full_readings_with_errors = load_text(text_file, characters_per_line)

    # calculate number of pages
    page_count = np.ceil(len(full_readings_with_errors[0])/lines_per_page).astype(int)

    # enforce max pages per reading
    if page_count>max_page_count:
        page_count = max_page_count
        full_readings_with_errors = full_readings_with_errors[:(lines_per_page*max_page_count)]

    # calculate the line spacing from lines per page and image height
    line_spacing = image_height / lines_per_page

    # Create blank page images
    print(f'Creating {page_count} pages...')
    image_files = []
    for error_col_index, error_type in enumerate(error_options):
        if (len(full_readings_with_errors[error_col_index])>0):
            new_image_files = create_pages(page_count, error_type, image_width,image_height,image_prefix)
            image_files.extend(new_image_files)

    # Add text to pages
    print('Adding text...')

    error_index = 0
    page_index = 0
    word_offset = 0 # set to before the control page, the first errors would be after the control
    error_indexes = []
    for file_index, file in enumerate(image_files):
        word_offset, found_errors = write_to_page(full_readings_with_errors[error_index], file, word_offset, lines_per_page, line_spacing, font_name, font_size)
        error_indexes += found_errors
        full_readings_with_errors[error_index] = full_readings_with_errors[error_index][lines_per_page:] # Remove lines you just wrote to an image

        # keep track of which type of error we're doing
        page_index += 1
        if page_index >= page_count:
            page_index = 0 # reset page index for file names
            error_index += 1 # move to the next error type in the list
            # word_offset += 1 # add one for the page offset for each page
    print(f'error indices = {error_indexes}')

    # Save conditions dataframe listing these files
    print(f'Writing conditions file {conditions_file}...')
    dfFilenames = pd.DataFrame()
    dfFilenames['image'] = image_files
    dfFilenames.to_csv(conditions_file,index_label='page')

    # create coordinate file
    print('Generating coordinate file...')
    generate_data(image_files, error_indexes, coordinate_file)
    print('Done!')
