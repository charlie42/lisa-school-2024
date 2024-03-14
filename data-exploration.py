import pandas as pd 
import pingouin as pg

def print_stats(data):
    print(f"""{len(data)} FACETS filled, 
          {len(data["Subject ID"].unique())} students, 
          {len(data["Respondent Hash"].unique())} teachers""")
    
def check_protocol(data, n_teachers_overlep):
    check_no_more_than_two(data)
    check_sample_sizes(data, n_teachers_overlep)
    
def check_no_more_than_two(data):
    print("Checking if more than 2 entries for teacher-student pair...")
    teachers = list(data["Respondent Hash"].unique())
    for teacher in teachers:
        students_per_teacher = list(data[data["Respondent Hash"] == teacher]["Subject ID"].unique())
        for student in students_per_teacher:
            bool_mask = (data["Respondent Hash"] == teacher) & (data["Subject ID"] == student)
            if len(data[bool_mask]["Time"]) > 2:
                print(data[bool_mask][["Respondent Hash", "Subject ID", "Time"]])

def check_sample_sizes(data, n_teachers_overlep):
    check_irr_teachers_ss(data, n_teachers_overlep)
    check_trr_ss(data)

def check_irr_teachers_ss(data, n_teachers_overlep):
    # How many students were rated by the same 4 teachers? Should be 15-24
    teachers = list(data["Respondent Hash"].unique())
    
    # Get all sets of n_teachers_overlep teachers out of all teachers
    import itertools
    teacher_sets = list(itertools.combinations(teachers, n_teachers_overlep))
    for teacher_set in teacher_sets:
        sets_of_students = []
        for teacher in teacher_set:
            students_per_teacher = set(data[data["Respondent Hash"] == teacher]["Subject ID"].unique())
            sets_of_students.append(students_per_teacher)
        overlapping_students = set.intersection(*sets_of_students)
        print(f"{len(overlapping_students)} are rated by {n_teachers_overlep} teachers")

    # Print list of teachers that rated each student
    # student_list = list(data["Subject ID"].unique())
    # for student in student_list:
    #     teachers_for_student = list(data[data["Subject ID"] == student]["Respondent Hash"].unique())
    #     print(f"Student {student} was rated by teachers {teachers_for_student}")
        
def check_trr_ss(data):
    # Check hwo many students were rated twice by the same teacher (need 30-48)
    administration_count_df = data.groupby(["Respondent Hash", "Subject ID"])["Time"].describe()["count"]
    print(administration_count_df)
    rated_twice = len(administration_count_df[administration_count_df == 2])
    print(f"{rated_twice} students rated twice")

if __name__ == "__main__":

    clichy = pd.read_csv("data/clichy_formatted.csv")
    suger = pd.read_csv("data/suger_formatted.csv")
    print(clichy.columns)

    print("Clichy:")
    print_stats(clichy)
    check_protocol(clichy, 3)

    print("Suger:")
    print_stats(suger)
    check_protocol(suger, 4)
    