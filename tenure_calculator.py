import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

class TenureCalculator:
    def __init__(self, df, config):
        self.df = df
        self.config = config
        self.tenure_data = None

    # TO IMPLEMENT GRADE LEVEL FILTERING
    def build_eligible(self):
        # students in the base year (will be going backwards)
        baseyear_df = self.df[self.df['school_year'] == self.config.baseyear]

        enrolled = baseyear_df[
            (baseyear_df['ENTRY_DATE'] <= self.config.base20th) &
            (baseyear_df['EXIT_DATE'] >= self.config.base20th)]
        
        print(f"Eligible students in base year: {len(enrolled)}")

        eligible = enrolled[enrolled['GRADE_LEVEL'] == self.config.grade]

        return set(zip(eligible['STUDENT_ID'], eligible['SCHOOL_NAME']))
    
    

    def count_years_enrolled(self, eligible_students):
        years_enrolled = dict.fromkeys(eligible_students, 1) # initializes tenure to 1 for each student

        # set maximum tenure for Loomis based on toggle
        loomis_max = 3 if self.config.loomistoggle else 4
        max_tenures = {}
        for _, school_name in eligible_students:
            if school_name not in max_tenures:
                if school_name == "Loomis":
                    max_tenures[school_name] = loomis_max
                else:
                    school_rows = self.df[self.df['SCHOOL_NAME'] == school_name]
                    if not school_rows.empty:
                        high_grade = school_rows['HIGH_GRADE'].iloc[0]
                        low_grade = school_rows['LOW_GRADE'].iloc[0]
                        max_tenures[school_name] = high_grade - low_grade + 1

        current_year = self.config.baseyear - 1

        while True: # go backwards until no more eligible students match
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
            enrolled_eligible = set(zip(enrolled['STUDENT_ID'], enrolled['SCHOOL_NAME']))

            current_year_matches = 0 # num eligible students enrolled in this school this year
            for student in eligible_students:
                
                student_id, school_name = student

                max_tenure = max_tenures.get(school_name, 999)

                if student in enrolled_eligible and years_enrolled[student] < max_tenure:
                    years_enrolled[student] += 1
                    current_year_matches += 1

            if current_year_matches == 0: # if no eligible students were at their school this year
                break

            current_year -= 1 # move to the previous year

        return years_enrolled

    def calculate_rates(self):
        eligible_students = self.build_eligible()
        years_enrolled = self.count_years_enrolled(eligible_students)

        school_class_tenure = {} # dictionary structure is { school: { tenure: num students} }
        for (_, school_name), tenure in years_enrolled.items():
            if school_name not in school_class_tenure:
                school_class_tenure[school_name] = {}
            school_class_tenure[school_name][tenure] = school_class_tenure[school_name].get(tenure, 0) + 1

        schools = []
        for school_name, tenure_counts in school_class_tenure.items():
            total = sum(tenure_counts.values())
            for tenure, count in tenure_counts.items():
                tenure_percentage = (count / total) * 100
                schools.append({"school": school_name, "tenure": tenure, "percentage": tenure_percentage})

        self.tenure_data = pd.DataFrame(schools)
        return self.tenure_data

    def graph(self):
        if self.tenure_data is None:
            self.calculate_rates()

        # pivot data so each row is a different campus
        pivot_df = self.tenure_data.pivot(
            index='school',
            columns='tenure',
            values='percentage'
        ).fillna(0)

        pivot_df = pivot_df.sort_index(ascending=False)

        # graph
        fig = go.Figure()

        colors = px.colors.sample_colorscale('viridis', len(pivot_df.columns))

        for i, tenure_year in enumerate(pivot_df.columns):
            fig.add_trace(go.Bar(
                y=pivot_df.index,
                x=pivot_df[tenure_year],
                marker_color=colors[i],
                orientation='h',
                name=str(i+1),
                hovertemplate=(
                    f"Tenure: {tenure_year}<br>"
                    f"Percentage: %{{x:.2f}}%"
                    "<extra></extra>"
                )
            ))

        # configuration
        fig.update_layout(title=f"Graduating Class Tenure Distribution (SY {self.config.baseyear + 1})")
        fig.update_layout(
            xaxis=dict(
                title="Percentage of Graduating Class (%)",
                range=[0, 100]
            ),
            yaxis=dict(
                title="School"
            ),
            barmode='stack',
            width=1000,
            height=500,
            legend_title_text="Tenure (years)"
        )

        fig.show()