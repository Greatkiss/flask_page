import pandas as pd
import glob
import openpyxl
folder_path = r"results"
files = glob.glob(folder_path + "\*.csv")
lists = []
for file in files:
    df = pd.read_csv(file, encoding='shift-jis')
    print(df)
    t2 = '_'
    t1 = '\\'
    idx_1 = file.find(t1)  # 半角空白文字のインデックスを検索
    idx_2 = file.find(t2)
    name = file[idx_1+1:idx_2]  # スライスで半角空白文字のインデックス＋1以降を抽出
    df.insert(0,'name',name)
    lists.append(df)
df = pd.concat(lists, axis=0)
df.to_excel("output.xlsx", encoding='shift-jis', index=False)