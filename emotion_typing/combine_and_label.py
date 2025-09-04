import pandas as pd
import os

def process_file(filename, label):
    df = pd.read_csv(filename)
    df["delay"] = df["time"].diff().fillna(0)
    df["label"] = label
    return df[["delay", "label"]]

all_data = []

for emotion in ["happy", "sad", "angry", "confused"]:
    file = f"keystrokes_{emotion}.csv"
    if os.path.exists(file):
        df = process_file(file, emotion)
        all_data.append(df)

df_combined = pd.concat(all_data)
df_combined.to_csv("combined_labeled_data.csv", index=False)
print("✅ Combined data saved to combined_labeled_data.csv")
