from ctypes import sizeof
from tracemalloc import start
from Tabelog_visitors import scrape_score
import pandas as pd
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import shutil
def main(path):
    #idpass.csv、errors.csvの保存先
    #path = "./"
    today = datetime.date.today()
    date = '{}_{}'.format(today.year,today.month)
    if(today.month == (3 or 6 or 9 or 11)):
        num_of_days = 30
    elif(today.month == 2):
        num_of_days = 28
    else:
        num_of_days = 31
    res_score = []
    e_list = []

    #認証
    scope =['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret_spread.json', scope)
    client = gspread.authorize(creds)
    #ブック名の指定
    book = client.open("Tabelog予約実績")
    #シート名の指定
    try:
        sheet = book.worksheet("{}".format(date))
    except:
        book.add_worksheet(title="{}".format(date), rows=7000, cols = 100)
        sheet = book.worksheet("{}".format(date))
    #id,passをdfに格納
    df = scrape_score.get_table.get_idpwd(path)
    shutil.rmtree("uploads")
    #print(df)
    #各店舗のscoreをresultに格納
    start_num = 1
    for i in range(len(df)):
        print(df['店舗名'][i])
        name = df['店舗名'][i]
        id = df['t_id'][i]
        pwd = df['t_pass'][i]
        scrape_score.get_table.score(name, id, pwd,e_list, num_of_days,res_score)
        if(len(res_score[i])>3):
            end_num = start_num + len(res_score[i])-1
        else:
            print("error at {}".format(df['店舗名'][i]))
            end_num = start_num + 31
        cell_list = sheet.range('A'+'{}'.format(start_num)+':C'+'{}'.format(end_num))
        #print(cell_list)
        for cell in cell_list:
            try:
                cell.value = res_score[i][cell.row - start_num][cell.col - 1]
            except:
                cell.value = df['店舗名'][i]
        sheet.update_cells(cell_list)
        start_num = end_num+1
        time.sleep(1)
    new_path = "./Scraping_gnavi/results_{}".format(today)
    pd.DataFrame(e_list).to_csv(new_path+"/errorlist_{}.csv".format(today),encoding='shift-jis')
    #results_{}フォルダのzip化
    shutil.make_archive('results', 'zip', root_dir=new_path)
    shutil.rmtree(new_path)

if __name__ == "__main__":
    main("uploads/idpass.csv")
