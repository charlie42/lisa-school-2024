import pandas as pd 
import pingouin as pg

def find_all_sets_of_overlapping_students(data, n_teachers_overlap):
    # Iterate over all combinations of n_teachers_overlap students and save
    # students rated by this combintaion of teachers. Can use these sets
    # of students for inter-rater reliability between the teachers.
    # Returns a list of dicts with each possible combination of n_teachers_overlap teachers
    # and students they rated

    teachers = list(data["Respondent Hash"].unique())

    overlaps = []

    import itertools
    teacher_sets = list(itertools.combinations(teachers, n_teachers_overlap))
    for teacher_set in teacher_sets:
        sets_of_students = []
        for teacher in teacher_set:
            students_per_teacher = set(data[data["Respondent Hash"] == teacher]["Subject ID"].unique())
            sets_of_students.append(students_per_teacher)
        overlapping_students = set.intersection(*sets_of_students)
        
        overlaps.append({"Teachers": teacher_set, "Students": overlapping_students})

    return overlaps

def find_largest_overlapping_student_set(overlaps):
    # Among identified student overlaps find the largest -- to use for IRR
    max_n = 0
    result_teachers = None
    result_students = None

    for overlap in overlaps:
        if len(overlap["Students"]) > max_n:
            max_n = len(overlap["Students"])
            result_teachers = overlap["Teachers"]
            result_students = overlap["Students"]

    return result_teachers, result_students

def id_overlapping_teachers_and_students(data, n_teachers_overlap):
    # ID list of students and teachers with the largest overlap, for irr

    overlaps = find_all_sets_of_overlapping_students(data, n_teachers_overlap)
    teachers, students = find_largest_overlapping_student_set(overlaps)

    return teachers, students

def get_icc_row(col, data, target, raters):
    icc = pg.intraclass_corr(
        data=data, 
        targets=target, 
        raters=raters, 
        ratings=col,
        nan_policy='omit'
    ).set_index('Type').loc["ICC1"][["ICC", "pval", "CI95%"]]
    return [col, icc["ICC"], icc["pval"], icc["CI95%"]]

def irr_icc(data, facets_cols, n_teachers_overlap, filename_base):
    teachers, students = id_overlapping_teachers_and_students(data, n_teachers_overlap)
    data = data[(data["Subject ID"].isin(students)) & (data["Respondent Hash"].isin(teachers))]
    
    rows = []
    for col in facets_cols:
        print(col)
        row = get_icc_row(col, data, target = "Subject ID", raters="Respondent Hash")
        rows.append(row)
    icc_df = pd.DataFrame(rows, columns = ["Item", "ICC", "PVal", "CI95"]).sort_values("PVal")
    icc_df.to_csv(f"output/irr_{filename_base}.csv", float_format='%.3f')
    return icc_df

def transform_for_trr(teacher_data):
    # Create new column for administration count - first or second    
    teacher_data["N Admin"] = teacher_data.groupby("Subject ID").cumcount()+1
    return teacher_data

def trr_icc(data, facets_cols, filename_base):
    # Calculate TRR for each teacher
    teachers = list(data["Respondent Hash"].unique())
    
    for i, teacher in enumerate(teachers):
        teacher_data = data[data["Respondent Hash"] == teacher]
        teacher_data = transform_for_trr(teacher_data)
        if len(teacher_data["Subject ID"].unique()) >= 22:
            print(teacher, len(teacher_data["Subject ID"].unique()))
            rows = []
            for col in facets_cols:
                print(col)
                row = get_icc_row(col, teacher_data, target = "Subject ID", raters="N Admin")
                rows.append(row)
            icc_df = pd.DataFrame(rows, columns = ["Item", "ICC", "PVal", "CI95"]).sort_values("PVal")
            icc_df.to_csv(f"output/trr_{filename_base}_teacher{i}.csv", float_format='%.3f')

if __name__ == "__main__":

    clichy = pd.read_csv("data/clichy_formatted.csv", index_col=0)
    suger = pd.read_csv("data/suger_formatted.csv", index_col=0)

    facets_cols = [x for x in clichy.columns if x not in [
        "Entry ID", "Actor type", "Subject ID", "Study ID", "Group ID", "Time", "Respondent Hash"
    ]]

    #irr_icc(clichy, facets_cols, n_teachers_overlap=3, filename_base="clichy")
    #irr_icc(suger, facets_cols, n_teachers_overlap=4, filename_base="suger")

    trr_icc(clichy, facets_cols, filename_base="clichy")    
    #trr_icc(suger, facets_cols, filename_base="suger")    
