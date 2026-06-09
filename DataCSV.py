import csv
import pandas as pd
from datetime import datetime

def calcSchoolYear(ENTRY_DATE):
    if pd.isnull(ENTRY_DATE):
        return None

    # ex: if entry date is 2022-08-22, year is 2022 (SY 22-23)
    if ENTRY_DATE.month >= 7: # if month is July or later, school year is current year
        return ENTRY_DATE.year
    else: # if month is before July, school year is previous year
        return ENTRY_DATE.year - 1

def loomis_longwood_names(entry):
    if "Loomis" in entry["SCHOOL_NAME"] and entry["GRADE_LEVEL"] > 2: # consider Loomis grades 3-8 as Longwood
        return "Longwood HS"
    else:
        return entry["SCHOOL_NAME"]

class DataCSV:
    def __init__(self, filepath):
        self.filepath = filepath # allows other methods access to the file path
        self.df = None # initializes an empty df to store the data

    def load(self):
        self.df = pd.read_csv(self.filepath) # read csv file and store in df

    def clean(self):
        self.df["ENTRY_DATE"] = pd.to_datetime(self.df["ENTRY_DATE"], errors='coerce') # cast entry date to datetime, coerce to turn unparsable into null
        self.df["EXIT_DATE"] = pd.to_datetime(self.df["EXIT_DATE"], errors='coerce') # cast exit  date to datetime

        self.df["HIGH_GRADE"] = pd.to_numeric(self.df["HIGH_GRADE"], errors='coerce') # cast high grade to numeric
        self.df["GRADE_LEVEL"] = pd.to_numeric(self.df["GRADE_LEVEL"], errors='coerce') # cast grade level to numeric

        # remove nulls
        self.df = self.df.dropna(subset=[
            "ENTRY_DATE",
            "EXIT_DATE",
            "HIGH_GRADE",
            "GRADE_LEVEL",
            "STUDENT_ID",
            "SCHOOL_NAME"
        ])

        # cast numeric into ints
        self.df["HIGH_GRADE"] = self.df["HIGH_GRADE"].astype(int) # cast high grade to int  
        self.df["GRADE_LEVEL"] = self.df["GRADE_LEVEL"].astype(int) # cast grade level to int

        self.df["school_year"] = self.df["ENTRY_DATE"].apply(calcSchoolYear) # get school year from entry date

        self.df["SCHOOL_NAME"] = self.df.apply(loomis_longwood_names, axis=1)

    def getdf(self):
        return self.df # to use cleaned df in other methods