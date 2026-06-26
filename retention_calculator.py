import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

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
        eligibility = (
          (self.df["school_year"] == self.config.baseyear) # filter entries where current year = base year
          & (self.df["ENTRY_DATE"] <= self.config.base20th) # check that entry date <= Oct 1
          & (self.df["EXIT_DATE"] >= self.config.base20th) # check that exit date >= Oct 1
          & (self.df["GRADE_LEVEL"] < self.df["HIGH_GRADE"]) # check current grade level < high grade of the school (exclude graduates)
        )

        eligible = self.df.loc[eligibility]

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
                if school not in historical_retention:
                    historical_retention[school] = [None] * self.config.numyears
                historical_retention[school][i] = rate
            self.config.baseyear += 1

        # reset values
        self.config.baseyear = baseyear
        self.config.targetyear = targetyear
        self.config.base20th = pd.Timestamp(year=baseyear, month=10, day=1)
        self.config.target20th = pd.Timestamp(year=targetyear, month=10, day=1)

        # graph
        fig = go.Figure()

        schools = sorted(historical_retention.keys())
        colors = px.colors.qualitative.Prism
        color_map = {school: colors[i % len(colors)] for i, school in enumerate(schools)}

        # skip None retention rates
        for school_name, rates in sorted(historical_retention.items()):
            color = color_map[school_name]
            points = [(yr, r) for yr, r in zip(years, rates) if r is not None]
            if not points:
                continue
            x_vals, y_vals = zip(*points)

            fig.add_trace(go.Scatter(
                x=x_vals,
                y=y_vals,
                mode='lines+markers',
                line=dict(width=2,color=color),
                name=school_name,
                hovertemplate=(
                    f"School: {school_name}<br>"
                    "Year: %{x:.0f}<br>"
                    "Retention: %{y:.1f}%"
                    "<extra></extra>"
                ),
                hoveron='points', # hover only on points
                hoverinfo='all',
            ))

        # configure graph
        fig.update_layout(title_xanchor='center')
        fig.update_layout(
          xaxis=dict(
              title='School Year',
              range=[baseyear - 1, targetyear],
              tickmode='array',
              tickvals=x_vals
          ),
          yaxis=dict(
              title='Retention Rate (%)',
              range=[0, 100]
          ),
          title=f"Yearly Retention from {baseyear}-{targetyear}",
          width=1000,
          height=600,
          legend_title_text="Schools"
        )

        fig.show()

    def run(self):
        self.build_eligible_entries()
        self.build_retained_entries()
        self.calculate_retention_rates()

        return self.retention_rates