import pandas as pd
import matplotlib.pyplot as plt

class RetentionCalculator:
    def __init__(self, df, config):
        self.df = df # dataframe from DataCSV
        self.config = config # config object from ParameterConfig

        # to be populated
        self.eligible_entries = set()
        self.retained_entries = set()
        self.final_retained = set()

        self.retention_rates = None

    def build_eligible_entries(self):
        # filter entries where current year = base year
        baseyear_df = self.df[self.df['school_year'] == self.config.baseyear] 

        # check that entry date <= Oct 1 and exit date >= Oct 1
        enrolled = baseyear_df[
            (baseyear_df['ENTRY_DATE'] <= self.config.base20th) &
            (baseyear_df['EXIT_DATE'] >= self.config.base20th)]

        # check current grade level < high grade of the school (exclude graduates)
        eligible = enrolled[enrolled['GRADE_LEVEL'] < enrolled['HIGH_GRADE']]

        # get student ID and school name
        self.eligible_entries = set(zip(eligible['STUDENT_ID'], eligible['SCHOOL_NAME']))

    def build_retained_entries(self):
        # filter entries where current year = target year
        targetyear_df = self.df[self.df['school_year'] == self.config.targetyear]

        # check that entry date <= Oct 1 and exit date >= Oct 1 (of target year)
        enrolled = targetyear_df[
            (targetyear_df['ENTRY_DATE'] <= self.config.target20th) &
            (targetyear_df['EXIT_DATE'] >= self.config.target20th)
        ]

        # get student ID and school name
        self.retained_entries = set(zip(enrolled['STUDENT_ID'], enrolled['SCHOOL_NAME']))

        # intersect the two sets (students in both are retained)
        self.final_retained = self.eligible_entries & self.retained_entries

    def school_count(self):
        # eligible students per school
        school_eligible = {}
        for student_id, school_name in self.eligible_entries:
            if school_name not in school_eligible:
                school_eligible[school_name] = 0
            school_eligible[school_name] += 1

        # retained students per school
        school_retained = {}
        for student_id, school_name in self.final_retained:
            if school_name not in school_retained:
                school_retained[school_name] = 0
            school_retained[school_name] += 1        

        return school_eligible, school_retained

    def calculate_retention_rates(self):
        # per school counts
        school_eligible, school_retained = self.school_count()

        # retention rate for each school
        rates = []
        for school_name, eligible_count in school_eligible.items(): 
            retained_count = school_retained.get(school_name, 0) # the 0 means default to 0

            rate = (retained_count / eligible_count) * 100

            rates.append((school_name, rate))

        self.retention_rates = pd.DataFrame(rates, columns=['SCHOOL_NAME', 'RETENTION_RATE'])

    def graph(self):    
        fig, ax = plt.subplots()

        baseyear = self.config.baseyear
        targetyear = self.config.targetyear

        years = list(range(baseyear, targetyear))
        historical_retention = {}

        # collect retention rates across the years
        for i in range(self.config.numyears):
            self.config.baseyear = baseyear + i
            self.config.targetyear = baseyear + i + 1
            self.config.base20th = pd.Timestamp(year=self.config.baseyear, month=10, day=1)
            self.config.target20th = pd.Timestamp(year=self.config.targetyear, month=10, day=1)

            rates_df = self.run()

            for _, row in rates_df.iterrows():
                school = row['SCHOOL_NAME']
                rate = row['RETENTION_RATE']
                historical_retention.setdefault(school, [None] * self.config.numyears)[i] = rate
            self.config.baseyear += 1       

        print(f"\n--- historical_retention ---")
        for school, rates in historical_retention.items():
            print(f"{school}: {rates}")

        # reset values
        self.config.baseyear = baseyear
        self.config.targetyear = targetyear
        self.config.base20th = pd.Timestamp(year=baseyear, month=10, day=1)
        self.config.target20th = pd.Timestamp(year=targetyear, month=10, day=1)
        
        # skip schools without a retention rate for each year
        for school_name, rates in historical_retention.items():
            if None not in rates:
                ax.plot(years, rates, marker='o', label=school_name)

        # configure graph
        ax.set_xlim(baseyear - 1, targetyear)
        ax.set_ylim(0, 100)
        ax.set_xticks(years)
        ax.set_title(f"Yearly Retention from SY{baseyear}-{targetyear}")
        ax.set_xlabel("Year")
        ax.set_ylabel("Retention Rate (%)")
        ax.legend()

        return fig

    def run(self):
        self.build_eligible_entries()
        self.build_retained_entries()
        self.calculate_retention_rates()

        return self.retention_rates