import tkinter as tk
from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from datetime import datetime
from DataCSV import DataCSV
from ParameterConfig import ParameterConfig
from RetentionCalculator import RetentionCalculator
from GraduatingClassesCalculator import GraduatingClassesCalculator

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

    retention_calculator = RetentionCalculator(df, config)
    retention_rates = retention_calculator.run()
    print(retention_rates)
    
    # graph trends for 1-year retention
    retention_graph = retention_calculator.graph()
    # plt.show()

    # display the graduating classes
    graduating_classes = GraduatingClassesCalculator(df, config)
    graduating_tenure = graduating_classes.calculate_years()
    print(graduating_tenure)

    tenure_graph = graduating_classes.graph()
    plt.show()

else:
    print("No file was selected.")