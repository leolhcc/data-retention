from DataCSV import DataCSV
from ParameterConfig import ParameterConfig
from RetentionCalculator import RetentionCalculator

# load test csv
file = DataCSV('test_enroll.csv')
file.load()
file.clean()
print('Data loaded and cleaned')

df = file.getdf()

config = ParameterConfig(2024, 1)

calculator = RetentionCalculator(df, config)
result = calculator.run()

print(result)
