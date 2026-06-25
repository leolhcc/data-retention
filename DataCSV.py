import pandas as pd

def calc_school_year(ENTRY_DATE):
    if pd.isnull(ENTRY_DATE):
        return None

    # ex: if entry date is 2022-08-22, year is 2022 (SY 22-23)
    if ENTRY_DATE.month >= 7: # if month is July or later, school year is current year
        return ENTRY_DATE.year
    else: # if month is before July, school year is previous year
        return ENTRY_DATE.year - 1

def school_name(entry, loomistoggle):
    # Loomis K-2, Longwood ES 3-8
    if loomistoggle:
        if "Loomis" in entry["SCHOOL_NAME"] and entry["GRADE_LEVEL"] > 2: # consider Loomis grades 3-8 as Longwood ES
            return "Longwood ES"
        elif "Loomis" in entry["SCHOOL_NAME"] and entry["GRADE_LEVEL"] >= 0: # consider Loomis grades K-2 as Loomis
            return "Loomis"
        elif "Wrightwood" in entry["SCHOOL_NAME"]:
            return "Wrightwood"
        elif "Ellison" in entry["SCHOOL_NAME"]:
            return "Ralph Ellison Academy"
        else:
            return entry["SCHOOL_NAME"]

    # Loomis K-3, Longwood ES 4-8
    else:
        if "Loomis" in entry["SCHOOL_NAME"] and entry["GRADE_LEVEL"] > 3: # consider Loomis grades 4-8 as Longwood ES
            return "Longwood ES"
        elif "Loomis" in entry["SCHOOL_NAME"] and entry["GRADE_LEVEL"] >= 0: # consider Loomis grades K-3 as Loomis
            return "Loomis"
        elif "Wrightwood" in entry["SCHOOL_NAME"]:
            return "Wrightwood"
        elif "Ellison" in entry["SCHOOL_NAME"]:
            return "Ralph Ellison Academy"
        else:
            return entry["SCHOOL_NAME"]

class DataCSV:
    def __init__(self, filepath=None, loomistoggle=False, dataframe=None):
        self.filepath = filepath # allows other methods access to the file path
        self.df = dataframe # initializes an empty df to store the data
        self.loomistoggle = loomistoggle

    def load(self):
      if self.filepath is not None:
          self.df = pd.read_csv(self.filepath)

    def clean(self):
        self.df["ENTRY_DATE"] = pd.to_datetime(self.df["ENTRY_DATE"], errors='coerce') # cast entry date to datetime, coerce to turn unparsable into null
        self.df["EXIT_DATE"] = pd.to_datetime(self.df["EXIT_DATE"], errors='coerce') # cast exit  date to datetime
        self.df["LOW_GRADE"] = pd.to_numeric(self.df["LOW_GRADE"], errors='coerce') # cast low grade to numeric
        self.df["HIGH_GRADE"] = pd.to_numeric(self.df["HIGH_GRADE"], errors='coerce') # cast high grade to numeric
        self.df["GRADE_LEVEL"] = pd.to_numeric(self.df["GRADE_LEVEL"], errors='coerce') # cast grade level to numeric

        # remove nulls
        self.df = self.df.dropna(subset=[
            "ENTRY_DATE",
            "EXIT_DATE",
            "LOW_GRADE",
            "HIGH_GRADE",
            "GRADE_LEVEL",
            "STUDENT_ID",
            "SCHOOL_NAME"
        ]).copy()

        self.df["LOW_GRADE"] = self.df["LOW_GRADE"].astype(int) # cast low grade to int
        self.df["HIGH_GRADE"] = self.df["HIGH_GRADE"].astype(int) # cast high grade to int
        self.df["GRADE_LEVEL"] = self.df["GRADE_LEVEL"].astype(int) # cast grade level to int
        self.df["school_year"] = self.df["ENTRY_DATE"].apply(calc_school_year) # get school year from entry date
        self.df["SCHOOL_NAME"] = self.df.apply(lambda row: school_name(row, self.loomistoggle), axis=1)

        # remove graduated students
        self.df = self.df[self.df["SCHOOL_NAME"] != "Graduated Students"]

        # remove test cases
        self.df = self.df[~self.df["LASTFIRST"].str.contains("test", case=False, na=False)]

        # remove invalid schools
        self.df = self.df[~self.df["SCHOOL_NAME"].str.contains("DONT USE|Quest|Boy's Lab|Jackson|Larry|Global|Inactive|Summer|STRIDE", case=False)]

        # if toggle on, Loomis is K-2 so high grade should be 2
        if self.loomistoggle:
            self.df.loc[self.df["SCHOOL_NAME"] == "Loomis", "HIGH_GRADE"] = 2
        # if toggle off, Loomis is K-3 so high grade should be 3
        else:
            self.df.loc[self.df["SCHOOL_NAME"] == "Loomis", "HIGH_GRADE"] = 3

        # create a combined Loomis Longwood K-12 entry
        new_entries = self.df[self.df["SCHOOL_NAME"].str.contains("Longwood|Loomis", na=False)].copy()
        new_entries["SCHOOL_NAME"] = "Loomis Longwood K-12"
        new_entries["HIGH_GRADE"] = 12
        new_entries["LOW_GRADE"] = 0
        self.df = pd.concat([self.df, new_entries], ignore_index=True)

    def getdf(self):
        return self.df # to use cleaned df in other methods