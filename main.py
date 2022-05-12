from calendar import week
import os
from flask import Flask, request, redirect, url_for, flash, render_template, Response, make_response
from werkzeug.utils import secure_filename
import shutil
import zipfile
from Scraping_gnavi import scrape_golden
from Tabelog_visitors import scrape_visitor
from flask_sslify import SSLify

# アップロード先のディレクトリ
UPLOAD_FOLDER = './uploads'
TEMP_FOLDER = './temp'
action = ''
# アップロードされる拡張子の制限
ALLOWED_EXTENSIONS = set(['xlsx', 'csv', 'pdf','zip'])
app = Flask(__name__)
sslify = SSLify(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allwed_file(filename):
    # .があるかどうかのチェックと、拡張子の確認
    # OKなら１、だめなら0
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def home():
    work_list = ["golden time", "tabelog visitor", "test1"]
    if request.method == 'POST':
        action = request.form["what_to_do"]
        if action == "golden time":
            return redirect(url_for('uploads_files',action = action))
        if action == "tabelog visitor":
            return redirect(url_for('uploads_files',action = action))
        else:
            return redirect(request.url)
    return render_template("homepage.html", title="home", work_list = work_list)

@app.route('/scrape/<action>', methods=['GET', 'POST'])
def uploads_files(action):
    # リクエストがポストかどうかの判別
    if request.method == 'POST':
        # ファイルがなかった場合の処理
        if 'idpassfile' not in request.files:
            flash('ファイルがありません')
            return redirect(request.url)
        # データの取り出し
        file = request.files['idpassfile']
        # ファイル名がなかった時の処理
        if file.filename == '':
            flash('ファイルがありません')
            return redirect(request.url)
        # ファイルのチェック
        if file and allwed_file(file.filename):
            # 危険な文字を削除（サニタイズ処理）
            filename = secure_filename(file.filename)
            # ファイルの保存
            try:
                shutil.rmtree(TEMP_FOLDER)
                os.mkdir(TEMP_FOLDER)
            except:
                os.mkdir(TEMP_FOLDER)
            try:
                shutil.rmtree(UPLOAD_FOLDER)
                os.mkdir(UPLOAD_FOLDER)
            except:
                os.mkdir(UPLOAD_FOLDER)
            file.save(os.path.join(TEMP_FOLDER, filename))
            # ファイルの解凍
            with zipfile.ZipFile(TEMP_FOLDER+'/'+filename, "r") as zp:
                try:
                    zp.extractall(path = UPLOAD_FOLDER, pwd="kanekokeita".encode("utf-8"))
                    print("extract is complite")
                except RuntimeError as e:
                    print(e)
            shutil.rmtree(TEMP_FOLDER)
            # アップロード後のページに転送
            return redirect(url_for('confirm_info',action = action))
    return render_template("uploadpage.html", title="upload", name="Hoge")

@app.route('/scrape/<action>/confirm_info', methods=['GET','POST'])
def confirm_info(action):
    path = './uploads'
    files = []
    for filename in os.listdir(path):
        if os.path.isfile(os.path.join(path, filename)): #ファイルのみ取得
            files.append(filename)
    idpasslist = files
    if request.method == 'POST':
        ipfilename = request.form['idpassfilename']
        if ipfilename == '':
            print('no file')
            return redirect(request.url)
        if action == 'golden time':
            n = request.form['data_num']
            weekdate = request.form['weekdate']
            return redirect(url_for('run_da_scrape_golden',num = n, excelname = ipfilename, weekdate = weekdate))
        elif action == 'tabelog visitor':
            return redirect(url_for('run_da_scrape_visitor',excelname = ipfilename))
        else:
            print(action)
    if action == 'golden time':
        return render_template("confirm_golden.html", title="confirm", idpasslist = idpasslist)
    elif action == 'tabelog visitor':
        return render_template("confirm_visitor.html", title="confirm", idpasslist = idpasslist)

@app.route('/scrape/run/<excelname>/<weekdate>/<num>')
def run_da_scrape_golden(num, excelname, weekdate):
    try:
        os.remove("results.zip")
    except:
        print("there is no results.zip")
    print("RUN DA SCRAPE with the {}".format(excelname))
    scrape_golden.main(int(num), "./uploads/{}".format(excelname), str(weekdate))
    return redirect(url_for('dl_da_results'))

@app.route('/scrape/download', methods=['GET','POST'])
def dl_da_results():
    response = make_response()
    response.data  = open('results.zip', "rb").read()
    response.headers['Content-Type'] = 'application/octet-stream'
    response.headers['Content-Disposition'] = 'attachment; filename=results.zip'
    return response

@app.route('/scrape/run/<excelname>')
def run_da_scrape_visitor(excelname):
    try:
        os.remove("results.zip")
    except:
        print("there is no results.zip")
    print("RUN DA SCRAPE with the {}".format(excelname))
    scrape_visitor.main("./uploads/{}".format(excelname))
    return redirect(url_for('dl_da_results'))

if __name__ == "__main__":
    app.run(debug=True, host = '0.0.0.0', port = '5000')
