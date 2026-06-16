import pandas as pd

class ParameterConfig:
    def __init__ (self, baseyear, loomistoggle=False):
        self.baseyear = baseyear # base year is an int (SY2425 is represented with year 2024)
        self.loomistoggle = loomistoggle

        self.base20th = pd.Timestamp(year=baseyear, month=10, day=1)
        self.target_years = None
    
    def get_target_years(self, df):
        all_years = sorted(df['school_year'].unique())
        self.target_years = [year for year in all_years if year >= self.baseyear]

    # dynamic years --> 20th day for each year
    def get_target_20th(self, year):
        return pd.Timestamp(year=year, month=10, day=1)