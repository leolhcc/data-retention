import tkinter as tk
from tkinter import filedialog
import pandas as pd
import plotly.graph_objects as go

from datetime import datetime
from data_csv import DataCSV
from parameter_config import ParameterConfig
from retention_calculator import RetentionCalculator
from tenure_calculator import TenureCalculator

# hide the main root window
root = tk.Tk()
root.withdraw()

# open the file picker window
filepath = filedialog.askopenfilename(
    title="Select your enrollment data file (CSV only)",
    filetypes=[("CSV files", "*.csv")] # to only show csv files
)

if filepath:
    file = DataCSV(filepath)
    file.load()
    file.clean()

    print(f"Loaded: {filepath}")

    # get the dataframe
    df = file.getdf()

    # inputs (base year, number of years forward)
    baseyear = int(input("Enter the base year (2025 for SY24-25): "))
    numyears = int(input("Enter the number of years forward: "))
    loomistoggle = input("Loomis K-2, Longwood 3-8? (y/n) Otherwise Loomis K-3, Longwood 4-8: ").lower() == 'y'
    gradefilter = int(input("Enter the grade level (e.g., 0, 1, 2, 3, etc.): "))
    config = ParameterConfig(baseyear, numyears, loomistoggle, gradefilter)

    retention_calculator = RetentionCalculator(df, config)
    retention_graph = retention_calculator.graph()

    graduating_classes = TenureCalculator(df, config)
    graduating_tenure = graduating_classes.calculate_rates()
    tenure_graph = graduating_classes.graph()

else:
    print("No file was selected.")