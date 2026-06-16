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
        self.yearly_rates = None

    def build_eligible_entries(self, year):
        year_20th = self.config.get_target_20th(year)

        # filter entries where current year = base year
        year_df = self.df[self.df['school_year'] == year] 

        # check that entry date <= Oct 1 and exit date >= Oct 1
        enrolled = year_df[
            (year_df['ENTRY_DATE'] <= year_20th) &
            (year_df['EXIT_DATE'] >= year_20th)]

        # check current grade level < high grade of the school (exclude graduates)
        eligible = enrolled[enrolled['GRADE_LEVEL'] < enrolled['HIGH_GRADE']]

        # get student ID and school name
        self.eligible_entries = set(zip(eligible['STUDENT_ID'], eligible['SCHOOL_NAME']))

    def build_retained_entries(self, year):
        year_20th = self.config.get_target_20th(year)

        # filter entries where current year = target year
        year_df = self.df[self.df['school_year'] == year]

        # check that entry date <= Oct 1 and exit date >= Oct 1 (of target year)
        enrolled = year_df[
            (year_df['ENTRY_DATE'] <= year_20th) &
            (year_df['EXIT_DATE'] >= year_20th)
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

    def calculate_retention_rates(self, base_year, target_year):
        # per school counts
        school_eligible, school_retained = self.school_count()

        # retention rate for each school
        rates = []
        for school_name, eligible_count in school_eligible.items(): 
            retained_count = school_retained.get(school_name, 0) # the 0 means default to 0

            rate = (retained_count / eligible_count) * 100

            rates.append({
                'SCHOOL_NAME': school_name,
                'BASE_YEAR': base_year,
                'TARGET_YEAR': target_year,
                'SCHOOL_YEAR': f"{str(base_year)[-2:]}{str(target_year)[-2:]}",
                'RETENTION_RATE': rate
            })
        
        return pd.DataFrame(rates).sort_values(by='RETENTION_RATE', ascending=False)

    def calculate_yearly_retention(self):
        years = self.config.target_years
        yearly_rates = []

        # loop through each year pair
        for y in range(len(years) - 1):
            base_year = years[y]
            target_year = years[y + 1]

            self.build_eligible_entries(base_year)
            self.build_retained_entries(target_year)
            yearly_rates.append(self.calculate_retention_rates(base_year, target_year))
        
        self.yearly_rates = pd.concat(yearly_rates, ignore_index=True)
        return self.yearly_rates
    


    def run(self):
        self.calculate_yearly_retention()
        return self.yearly_rates