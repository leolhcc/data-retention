import sys
import tkinter as tk
from tkinter import filedialog

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QCheckBox,
    QFileDialog
)

# import matplotlib.pyplot as plt

# import matplotlib into PySide
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from DataCSV import DataCSV
from ParameterConfig import ParameterConfig
from RetentionCalculator import RetentionCalculator
from GraduatingClassesCalculator import GraduatingClassesCalculator

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # choose/upload csv
        self.csv_button = QPushButton("Choose CSV File")
        self.csv_button.clicked.connect(self.choose_csv)
        layout.addWidget(self.csv_button)

        self.file_label = QLabel("No file selected")
        layout.addWidget(self.file_label)

        # input base year
        layout.addWidget(QLabel("Base Year:"))
        self.base_year_spinbox = QSpinBox()
        self.base_year_spinbox.setRange(2003, 2050)
        layout.addWidget(self.base_year_spinbox)

        # input number of years forward
        layout.addWidget(QLabel("Number of Years Forward:"))
        self.num_years_spinbox = QSpinBox()
        self.num_years_spinbox.setRange(1, 99)
        layout.addWidget(self.num_years_spinbox)

        # input loomis k-2 or k-3 toggle
        layout.addWidget(QLabel("Loomis K-2 (on), Longwood 3-8 (off)?"))
        self.loomis_checkbox = QCheckBox()
        layout.addWidget(self.loomis_checkbox)

        # calculate rates and generate graphs button
        self.calculate_button = QPushButton("Calculate Rates and Generate Graphs")
        self.calculate_button.clicked.connect(self.calculate_rates)
        layout.addWidget(self.calculate_button)

        self.setLayout(layout)
        self.filepath = None
        self.retention_vis = None
        self.tenure_vis = None

    def choose_csv(self):

        filepath, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")

        if filepath:
            self.filepath = filepath
            self.file_label.setText(f"Loaded: {filepath}")

    def calculate_rates(self):
        if not self.filepath:
            return

        # load csv data
        file = DataCSV(self.filepath)
        file.load()
        file.clean()
        df = file.getdf() # get the dataframe

        # inputs (base year, number of years forward)
        base_year = self.base_year_spinbox.value()
        num_years = self.num_years_spinbox.value()
        loomis_toggle = self.loomis_checkbox.isChecked()

        # create the parameter config
        config = ParameterConfig(base_year, num_years, loomis_toggle)

        # retention calculation
        retention_calculator = RetentionCalculator(df, config)
        retention_rates = retention_calculator.run()
        print(retention_rates)
        
        # graph trends for 1-year retentions
        retention_graph = retention_calculator.graph()
        if self.retention_vis:
            self.layout().removeWidget(self.retention_vis)
            self.retention_vis.deleteLater()

        self.retention_vis = FigureCanvas(retention_graph)
        self.layout().addWidget(self.retention_vis)
        
        # graduation tenure calculation
        graduating_calculator = GraduatingClassesCalculator(df, config)
        tenure_rates = graduating_calculator.calculate_years()
        print(tenure_rates)

        # graph tenure rates for graduating classes
        tenure_graph = graduating_calculator.graph()
        if self.tenure_vis:
            self.layout().removeWidget(self.tenure_vis)
            self.tenure_vis.deleteLater()

        self.tenure_vis = FigureCanvas(tenure_graph)
        self.layout().addWidget(self.tenure_vis)

app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()
