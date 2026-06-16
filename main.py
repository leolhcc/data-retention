import tkinter as tk
from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt
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
    loomistoggle = input("Loomis K-2, Longwood 3-8? (y/n) Otherwise Loomis K-3, Longwood 4-8: ").lower() == 'y'

    config = ParameterConfig(baseyear, numyears, loomistoggle)

    calculator = RetentionCalculator(df, config)
    retention_rates = calculator.run()

    print(retention_rates)
    
    # graph trends for 1-year retention
    graph = calculator.graph()
    plt.show()

else:
    print("No file was selected.")



