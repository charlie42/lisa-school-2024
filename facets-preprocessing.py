import pandas as pd
import numpy as np
import json

class FACETSFormatter():

    def __init__(self):
        self.json = None
        self.df = None
        self.item_names = None

    def _parse_entries(self):
        print("Available fields: ", self.json["assessment_response_list_anonymized"][0].keys())
        rows = []
        print("Entries in json: ", len(self.json["assessment_response_list_anonymized"]))
        for entry in self.json["assessment_response_list_anonymized"]:
            # Have to filter by gruop id here to get latest version of FACETS
            #if entry["subject_group_id"] == "d71289b4-d743-475a-a7cc-166898569d62": 138
            #if entry["subject_group_id"] == "ed5e3cf6-67f0-405c-be85-f33d3184ec3a": # 135
            #if (entry["subject_group_id"] in ["e9ad5793-1862-4787-b0d8-d024c11519be", # 138
            #                                  "d71289b4-d743-475a-a7cc-166898569d62" # 75
            #]):
            for section in entry["assessment_response_sections"]:
                section_id = section["lisapedia_section_id"]
                for item in section["assessment_response_items"]:
                    item_id = item["lisapedia_item_id"]
                    value = item["value"]
                    rows.append([
                        entry["subject_id"]+entry["last_updated_at"],
                        entry["lisapedia_respondent_actor_id"],
                        entry["subject_id"],
                        entry["subject_group_id"],
                        entry["last_updated_at"],
                        entry["respondent_hash"],
                        section_id,
                        item_id,
                        value    
                    ])
                
        facets_df = pd.DataFrame(rows, columns=[
            "Entry ID",
            "Actor type", 
            "Subject ID", 
            "Group ID", 
            "Time", 
            "Respondent Hash",
            "Section ID",
            "Item ID", 
            "Value"
        ])
        
        self.df = facets_df

    def _replace_item_ids_with_values(self):
        # item_translation = pd.read_csv("facets_item_translation.csv", 
        #                                sep=",", 
        #                                index_col="assessment_item_id")
        item_translation = pd.read_csv("resources/facets_item_translation.csv", 
                                       sep=",")
        item_translation_en = item_translation[item_translation["locale_code"] == "en"]
        item_translation_en.set_index("assessment_item_id", inplace=True)
        self.item_names = item_translation_en["slug"]

        self.df["Item ID"] = self.df["Item ID"].map(
            item_translation_en["slug"]).fillna(self.df["Item ID"])
        
    def _map_ids(self):
        try:
            id_mapping = pd.read_csv("data/id_mapping_facets.csv", index_col="subject_id")
            self.df["Study ID"] = self.df["Subject ID"].map(
            id_mapping["dislay_label"]
        )
        except FileNotFoundError:
            print("No id_mapping_facets.csv file found, keeping Study ID empty")
            self.df["Study ID"] = np.nan

    def _transpose_items(self):
        df_to_transpose = self.df.drop("Section ID", axis=1)
        df_to_transpose = df_to_transpose.reset_index().pivot(index = [
            "Entry ID", "Actor type", "Subject ID", "Study ID", "Group ID", "Time", "Respondent Hash"
        ], columns = "Item ID", values = "Value").reset_index()

        self.df = df_to_transpose

    def _get_cat_names(self):
        cats = []
        for col in self.df.columns:
            if "_" in col:
                cat = col.split("_")
                cats.append(cat)
        cats = set(cat)
        return cats

    def transform(self, data):
        self.json = data
        self._parse_entries()
        self._replace_item_ids_with_values()
        self._map_ids()
        print(self.df)
        self._transpose_items()
        return self.df
        
if __name__ == "__main__":
    suger_data = json.load(open("data/suger.json", encoding='latin-1'), strict=False)
    clichy_data = json.load(open("data/clichy.json", encoding='latin-1'), strict=False)

    formatter = FACETSFormatter()
    suger_df = formatter.transform(suger_data)
    clichy_df = formatter.transform(clichy_data)

    suger_df.to_csv("data/suger_formatted.csv")
    clichy_df.to_csv("data/clichy_formatted.csv")