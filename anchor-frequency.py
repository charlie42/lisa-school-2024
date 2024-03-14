import pandas as pd
import numpy as np

# Read in data
df = pd.read_csv("data/facets_formatted.csv", header=0, index_col=0)

print(df.describe()[["emotion_stress-management", 
                     "cognition_attention-concentration", 
                     "somatic-and-sensory-functions_sexual-identity-behavior",
                     "daily-routines_screen-time",
                     "cognition_thinking-speed"]].T)

# Only keep columns with item responses
df = df.drop(["Entry ID","Actor type","Subject ID","Study ID","Group ID","Time","Respondent Hash"], axis=1)
# Drop binary cols
binary_cols = [x for x in df.columns if "other-special-issues" in x]+["toileting"] 
df = df.drop(binary_cols, axis=1)

df = df.apply(pd.to_numeric, errors='coerce')

# Shift all values from -0.5 to 0.5 (originally 0 to 1)
df = df.apply(lambda x: x-0.5)

means = [] # [ [name, average], [name, average] ]

for col in df.columns:
    col_name_left = col + "_LEFT"
    col_name_right = col + "_RIGHT"
    
    only_left_values = -(df[df[col] <= 0][col])
    only_right_values = (df[df[col] >= 0][col])
    
    print("DEBUG", col, np.mean(only_left_values), np.mean(only_right_values), np.mean(df[col]))

    means.append([col_name_left, np.mean(only_left_values)])
    means.append([col_name_right, np.mean(only_right_values)])

anchor_col_name = "Anchor"
mean_col_name = "Mean score (0-0.5)"
df_means = pd.DataFrame(means, columns=[anchor_col_name, mean_col_name])

df_means.dropna(how='any', inplace=True)
df_means = df_means.sort_values(by=mean_col_name, ascending=False)
df_means = df_means.set_index(anchor_col_name)

df_means.to_csv("data/output/prevalent_anchors.csv")

### Analyse binary cols separately
df = pd.read_csv("data/facets_formatted.csv", header=0, index_col=0)[binary_cols]
df.mean().T.sort_values().to_csv("data/output/prevalent_anchors_binary.csv")