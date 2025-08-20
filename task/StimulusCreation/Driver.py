import os
import StimulusCreation as s

# Declare text file you want to turn into images
# folder = 'example_text'
# text = f'{folder}/{folder}.txt'
# input_folder = 'input2software'
topics = ['history_of_film','pluto','prisoners_dilemma','serena_williams','the_voynich_manuscript']
errors = ['control','gibberish','lexical']
for topic in topics:
    for error in errors:
        # get input and output locations
        folder = f'{topic}_{error}'
        text = f'wikipedia/{error}/{folder}.txt'
        # update the user
        print(f'==={folder}===')
        # make folder if it doesnt' exist
        if not os.path.exists(folder):
            print(f'Making folder {folder}...')
            os.makedirs(folder)
        # 1. Assuming a 30x25deg display, to get .67x2deg per character x line, we
        # will need 30/.67=45 chars/line and 25/2=12 lines/page.
        # 2. Assuming a 1920x1080 display in which 1080 pixels = 25deg,
        s.create_stimulus(text_file=text, lines_per_page=16,
                          image_width=1900, image_height=1442,
                          font_name='courier.ttf', font_size=37,
                          image_prefix=f'{folder}/{folder}_page',
                          conditions_file=f'{folder}/{folder}.csv',
                          coordinate_file=f'{folder}/{folder}_coordinates.csv',
                          max_page_count = 10)
