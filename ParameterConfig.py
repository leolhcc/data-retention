import pandas as pd

class ParameterConfig:
    def __init__ (self, baseyear, numyears=1, loomistoggle=False):
        self.baseyear = baseyear - 1 # base year is an int (SY2425 is represented with year 2025)
        self.numyears = numyears
        self.targetyear = baseyear + numyears
        self.loomistoggle = loomistoggle

        self.base20th = pd.Timestamp(year=baseyear, month=10, day=1)
        self.target20th = pd.Timestamp(year=self.targetyear, month=10, day=1)
