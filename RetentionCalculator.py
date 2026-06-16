import pandas as pd

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

        self.retention_rates = pd.DataFrame(rates, columns=['SCHOOL_NAME', 'RETENTION_RATE']).sort_values(by='RETENTION_RATE', ascending=False)

    def run(self):
        self.build_eligible_entries()
        self.build_retained_entries()
        self.calculate_retention_rates()

        return self.retention_rates