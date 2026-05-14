#!/bin/bash

#SBATCH --partition=general
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=80G
#SBATCH --time=24:00:00
#SBATCH --job-name=run_remind_analysis
#SBATCH --output=%x_%j.out
#SBATCH --mail-type=END

source ~/.bashrc
conda activate remind

cd /path/to/ReMind/analysis_code
python -u run_analysis.py

