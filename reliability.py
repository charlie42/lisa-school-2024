import pandas as pd 
import pingouin as pg

if __name__ == "__main__":

    clichy = pd.read_csv("data/clichy_formatted.csv")
    suger = pd.read_csv("data/suger_formatted.csv")

    print(len(clichy), len(clichy["Subject ID"].unique()), len(clichy["Respondent Hash"].unique()))
    print(clichy["Respondent Hash"].unique())
    