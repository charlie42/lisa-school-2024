import pandas as pd
import glob

def get_avg_icc_from_df(df):
    df.loc[df["ICC"]<0, "ICC"] = 0 # Replace negative values by 0
    return df["ICC"].mean()

def append_means(path):
    for filename in glob.iglob(path + '**/*.csv', recursive=True):
        df = pd.read_csv(filename)
        df.loc["mean", "ICC"] = get_avg_icc_from_df(df)
        df.to_csv(filename)

if __name__ == "__main__":
    append_means("output/reliability/")