import requests
from bs4 import BeautifulSoup
import pandas as pd

class get_table():
    @staticmethod
    def score(name, id, pwd, e_list, num_of_days, result):
        session = requests.session()
        try:
            # セッションを開始
            url_login = "https://ssl.tabelog.com/owner_account/login/"
            response = session.get(url_login)
            res = session.get(url_login)
            soup = BeautifulSoup(res.text,"html.parser")
            auth_token = soup.find('input', {'name': 'authenticity_token'}).get('value')
            response_cookie = response.cookies
            # ログイン
            login_info = {
                "utf8":"✓",
                "authenticity_token":auth_token,
                "login_id":id,  #"login_id":id
                "password":pwd, #"password":pwd
                "login":"1",
                "Target":""
            }
            # action
            res = session.post(url_login, data=login_info, cookies=response_cookie)
            res.raise_for_status() # エラーならここで例外を発生させる
            soup_1 = BeautifulSoup(res.text,"html.parser")
            mp_link = soup_1.select('#wrapper > div.op-rst-navi.op-rst-navi--owner > ul > li:nth-child(1)')[0].select('a')[0].get('href')
            res = session.get(mp_link)
            res.raise_for_status()
            soup_2 = BeautifulSoup(res.text,"html.parser")
            score_link = soup_2.select('#wrapper > div.ol-container > div > div > div.ol-column2__side > div > div.op-side-nav > ul > li:nth-child(7)')[0].select('a')[0].get('href')
            #jisseki
            res = session.get(score_link)
            res.raise_for_status()
            #tableの取得
            raw_table=pd.DataFrame()
            table = pd.DataFrame()
            raw_table = pd.read_html(res.text)
            #実績のtable取得
            table = raw_table[1]
            table.reset_index(inplace=True)
            #実績tableのランチディナーの実績組数をlistにappend
            lunch_and_dinner = []
            l_sum = 0
            d_sum = 0
            for i in range(num_of_days):
                l = table.iat[i+1,2]
                d = table.iat[i+1,4]
                l_idx = l.find("組")
                d_idx = d.find("組")
                try:
                    lunch = int(l[:l_idx])
                    dinner = int(d[:d_idx])
                except:
                    lunch = 0
                    dinner = 0
                lunch_and_dinner.append([name,lunch,dinner])
            l_sum = table.iat[0,2]
            lsum_idx = l_sum.find("組")
            lunch_sum = int(l_sum[:lsum_idx])
            d_sum = table.iat[0,4]
            dsum_idx = d_sum.find("組")
            dinner_sum = int(d_sum[:dsum_idx])
            lunch_and_dinner.append([name,lunch_sum,dinner_sum])
            result.append(lunch_and_dinner)
            
            #logout
            soup_table = BeautifulSoup(res.text,"html.parser")
            logout_link = soup_table.select('#owner-headline > ul > li:nth-child(3) > a')[0].get('href')
            res = session.get(logout_link)
            soup_out = BeautifulSoup(res.text,"html.parser")
            relogin_link = soup_out.select('#js-body > div.ol-container.ol-container--mat > div.ol-contents.ol-contents--fixed > div > p:nth-child(2) > a')[0].get('href')
            session.get(relogin_link)
            session.close()
        except:
            print(RuntimeError)
            result.append(['none','none'])
            e_list.append([name, id, pwd])
            session.close()
    def get_idpwd(path):
        df =pd.read_csv(path, encoding="utf_8_sig")
        df = df[[
                '店舗名',
                't_id',
                't_pass',]].dropna(subset=['t_id','t_pass']).reset_index(drop=True)
        return df