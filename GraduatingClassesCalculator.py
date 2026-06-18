import pandas as pd
import matplotlib.pyplot as plt

class GraduatingClassesCalculator:
    def __init__(self, df, config):
        self.df = df
        self.config = config
        self.tenure_data = None

    def build_graduating(self):
        # students in the base year (will be going backwards)
        baseyear_df = self.df[self.df['school_year'] == self.config.baseyear]

        enrolled = baseyear_df[
            (baseyear_df['ENTRY_DATE'] <= self.config.base20th) &
            (baseyear_df['EXIT_DATE'] >= self.config.base20th)]
        
        graduating = enrolled[enrolled['GRADE_LEVEL'] == enrolled['HIGH_GRADE']]
        
        return set(zip(graduating['STUDENT_ID'], graduating['SCHOOL_NAME']))
    
    def count_years_enrolled(self, graduating_class):
        years_enrolled = dict.fromkeys(graduating_class, 1) # initializes tenure to 1 for each student

        current_year = self.config.baseyear - 1

        while True: # go backwards until no more graduating students match
            year_df = self.df[self.df['school_year'] == current_year]

            # no more entries in csv
            if year_df.empty:
                break

            year_20th = pd.Timestamp(year=current_year, month=10, day=1)

            # students enrolled on 20th day of this year
            enrolled = year_df[
                (year_df['ENTRY_DATE'] <= year_20th) &
                (year_df['EXIT_DATE'] >= year_20th)
            ]
            enrolled_grads = set(zip(enrolled['STUDENT_ID'], enrolled['SCHOOL_NAME']))

            current_year_matches = 0 # num grads enrolled in this school this year
            for student in graduating_class:
                if student in enrolled_grads:
                    years_enrolled[student] += 1
                    current_year_matches += 1
            
            if current_year_matches == 0: # if no graduating students were at their school this year
                break

            current_year -= 1 # move to the previous year

        return years_enrolled
    
    def calculate_years(self):
        graduating_class = self.build_graduating()
        years_enrolled = self.count_years_enrolled(graduating_class)

        school_grad_tenure = {} # dictionary structure is { school: { tenure: num students} }
        for (_, school_name), tenure in years_enrolled.items():
            if school_name not in school_grad_tenure:
                school_grad_tenure[school_name] = {}
            school_grad_tenure[school_name][tenure] = school_grad_tenure[school_name].get(tenure, 0) + 1

        schools = []
        for school_name, tenure_counts in school_grad_tenure.items():
            total = sum(tenure_counts.values())
            for tenure, count in tenure_counts.items():
                tenure_percentage = (count / total) * 100
                schools.append({"school": school_name, "tenure": tenure, "percentage": tenure_percentage})

        self.tenure_data = pd.DataFrame(schools)
        return self.tenure_data
    
    def graph(self):
        if self.tenure_data is None:
            self.calculate_years()

        # pivot data so each row is a different campus
        pivot_df = self.tenure_data.pivot(
            index='school', 
            columns='tenure', 
            values='percentage'
        ).fillna(0)

        pivot_df = pivot_df.sort_index(ascending=False)

        fig, ax = plt.subplots()
        
        pivot_df.plot(
            kind='barh', 
            stacked=True, 
            ax=ax, 
            cmap='viridis', 
        )

        # configuration
        ax.set_title(f"Graduating Class Tenure Distribution (SY {self.config.baseyear})")
        ax.set_xlabel("Percentage of Graduating Class (%)")
        ax.set_ylabel("Campus")
        ax.set_xlim(0, 100)

        ax.legend(
            title="Years Enrolled", 
            loc='upper left', 
            title_fontsize='11', 
            fontsize='10'
        )

        plt.tight_layout()
        return fig