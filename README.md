# ReMind
This repository contains the code for the task and analysis used in the ReMind paper.

## Repository Structure  

- **task/**  
  Contains the code for generating and running the ReMind task.  
  See the [README](task/README.md) inside the folder for detailed instructions.  

- **analysis_code/**  
  Contains scripts for analyzing eye-tracking data collected during the task.  

## Getting Started  

1. **Clone this repository**:  
   ```bash
   git clone https://github.com/your-username/ReMind.git
   cd ReMind

2. **Download data**  
Download and unzip the dataset from OSF: <https://osf.io/ajme7/>

3. **Install required packages and extract features (can skip)**
Required packages are listed in `requirements.txt`. To preprocess raw data and generate subject-level eye-tracking features:  
    - First, run `setup.py` from the `analysis_code/` folder to set up the `textblob` package.  
    - You may need to adjust path variables defined in the repo to match your local setup.  
    - The main script for feature extraction is `run_analysis.py`.
  
    **Example usage:**  
      ```
      python run_analysis.py --sub_id 10014 --win_type default --task_type sr --alpha 2
      ```
    
    **Arguments for `run_analysis.py`:**
    
    - `--sub_id`: 5-digit subject ID.  
      Use `all` to analyze all subjects within the folder.
    
    - `--win_type`: Time window type for extracting eye features. Options:  
      - `default`: using self-reported MW onset and offset  
      - `mw_fixed`: self-reported MW onset → page end – alpha  
      - `page_fixed`: page start → page end – alpha  
      - `end2`: last 2 seconds prior to page end – alpha  
      - `end5`: last 5 seconds prior to page end – alpha  
      - `slide[0-9]`: sliding window approach with length `[0-9]`  
        *(see paper for details on the window type)*
    
    - `--task_type`: Task paradigm type. Options:  
      - `sr`: self-report paradigm  
      - `tp`: simulated thought-probe paradigm  
      - `both`: both self-report and thought-probe paradigms  
        *(see paper for details on the simulated thought-probes)*
    
    - `--alpha`: Button press buffer/time period in seconds (default = `2`).
  
4. **Analysis and figures**
  - All analyses based on extracted features were performed in the `notebooks/` folder.  
  - Figures included in the paper were generated using `brm_figures.ipynb`.

## Citation
Citation details for this GitHub repository will be updated upon acceptance of the ReMind paper.
   
