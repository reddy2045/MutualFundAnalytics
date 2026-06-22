import pandas as pd
import os

folder="data/raw"

for file in os.listdir(folder):

    if file.endswith(".csv"):

        path=os.path.join(folder,file)

        df=pd.read_csv(path)

        print("\n"+"="*50)

        print("File:",file)

        print("\nShape")
        print(df.shape)

        print("\nData Types")
        print(df.dtypes)

        print("\nHead")
        print(df.head())

        print("\nMissing Values")
        print(df.isnull().sum())

        print("\nDuplicate Rows")
        print(df.duplicated().sum())