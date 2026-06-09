import tkinter as tk
from tkinter import filedialog
import pandas as pd
from datetime import datetime
from DataCSV import DataCSV
from ParameterConfig import ParameterConfig
from RetentionCalculator import RetentionCalculator

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
    baseyear = int(input("Enter the base year (2024 for SY24-25): "))
    numyears = int(input("Enter the number of years forward: "))

    config = ParameterConfig(baseyear, numyears)

    calculator = RetentionCalculator(df, config)
    retention_rates = calculator.run()

    print(retention_rates)
else:
    print("No file was selected.")



