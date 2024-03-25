import pandas as pd 
import pingouin as pg
from pathlib import Path

def keep_only_rated_twice(df):
    df["Admin Cumul Count"] = df.groupby(["Subject ID", "Respondent Hash"]).cumcount()+1
    print(df[["Subject ID", "Respondent Hash", "Admin Cumul Count"]])

    # Drop third administrations
    print("Rated more than twice: ", len(df[df["Admin Cumul Count"] >= 3]))
    
    # Remove participant-rater pair if only rated once
    rated_twice = df.groupby(["Subject ID", "Respondent Hash"]).filter(lambda x: len(x)==2)
    
    return rated_twice

def get_icc_row(col, data, target, raters):
    icc = pg.intraclass_corr(
        data=data, 
        targets=target, 
        raters=raters, 
        ratings=col,
        nan_policy='omit'
    ).set_index('Type').loc[f"ICC2k"][["ICC", "pval", "CI95%"]]
    return [col, icc["ICC"], icc["pval"], icc["CI95%"]]

def get_icc_df(data, facets_cols, raters_col):
    rows = []
    for col in facets_cols:
        row = get_icc_row(
            col, 
            data, 
            target="Subject ID", 
            raters=raters_col)
        rows.append(row)
    icc_df = pd.DataFrame(rows, columns = ["Item", "ICC", "PVal", "CI95"]).sort_values("PVal")
    return icc_df

def transform_for_trr_per_teacher(teacher_data):
    # Create new column for administration count - first or second    
    teacher_data["N Admin"] = teacher_data.groupby("Subject ID").cumcount()+1
    return teacher_data

def trr_icc_per_teacher(data, facets_cols, filename_base):
    # Calculate TRR for each teacher
    teachers = list(data["Respondent Hash"].unique())

    Path("output/reliability/trr_per_teacher/").mkdir(parents=True, exist_ok=True)

    icc_dfs = {}
    
    for i, teacher in enumerate(teachers):
        teacher_data = data[data["Respondent Hash"] == teacher]
        teacher_data = transform_for_trr_per_teacher(teacher_data)
        if len(teacher_data["Subject ID"].unique()) >= 10:
            print(filename_base, i, len(teacher_data["Subject ID"].unique()))
            icc_df = get_icc_df(teacher_data, facets_cols, raters_col="Admin Cumul Count")
            icc_df.to_csv(f"output/reliability/trr_per_teacher/{filename_base}_teacher{i}.csv", float_format='%.3f')
            icc_dfs[teacher] = icc_df

    return icc_dfs

def get_avg_icc_from_df(df):
    df.loc[df["ICC"]<0, "ICC"] = 0 # Replace negative values by 0
    return df["ICC"].mean()

def save_data_with_high_trr(data, teacher_icc_dfs, filename_base="clichy"):
    # Filter data to teachers with high average ICC

    good_icc_teachers = []
    for teacher in teacher_icc_dfs:
        avg_icc = get_avg_icc_from_df(teacher_icc_dfs[teacher])
        print(teacher, avg_icc)
        if avg_icc > 0.5:
            good_icc_teachers.append(teacher)

    good_icc_teachers_data = data[data["Respondent Hash"].isin(good_icc_teachers)]
    good_icc_teachers_data.to_csv(f"data/{filename_base}_good_trr.csv")

def transform_for_trr_across_teachers(data):
    pass

def trr_icc_across_teachers(data, facets_cols, filename_base):
    data = transform_for_trr_across_teachers(data)



if __name__ == "__main__":

    clichy = pd.read_csv("data/clichy_formatted.csv", index_col=0)
    suger = pd.read_csv("data/suger_formatted.csv", index_col=0)

    save_path = "output/reliability/"
    Path(save_path).mkdir(parents=True, exist_ok=True)

    facets_cols = [x for x in clichy.columns if x not in [
        "Entry ID", "Actor type", "Subject ID", "Study ID", "Group ID", "Time", "Respondent Hash"
    ]]

    clichy = keep_only_rated_twice(clichy)
    suger = keep_only_rated_twice(suger)

    trr_icc_per_teacher_clichy_dfs = trr_icc_per_teacher(clichy, facets_cols, filename_base="clichy")    
    trr_icc_per_teacher_suger_dfs = trr_icc_per_teacher(suger, facets_cols, filename_base="suger")    

    save_data_with_high_trr(clichy, trr_icc_per_teacher_clichy_dfs, filename_base="clichy")
    save_data_with_high_trr(suger, trr_icc_per_teacher_suger_dfs, filename_base="suger")

    trr_icc_across_teachers(clichy, facets_cols, filename_base="clichy")    
    trr_icc_across_teachers(suger, facets_cols, filename_base="suger")    
