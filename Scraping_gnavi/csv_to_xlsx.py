import pandas as pd
import glob
import os

def excelize(folder_path):
    files = glob.glob(folder_path + "/*.csv")
    lists = []
    for file in files:
        df = pd.read_csv(file, encoding='shift-jis')
        t = '_'
        name = os.path.split(file)[1]
        idx = file.find(t)  # 半角空白文字のインデックスを検索
        nameonly = name[:idx]  # スライスで半角空白文字のインデックス＋1以降を抽出
        if(nameonly != "error"):
            df.insert(0,'name',nameonly)
            lists.append(df)
    df = pd.concat(lists, axis=0)
    df.to_excel(folder_path + "/output.xlsx", encoding='shift-jis', index=False)
