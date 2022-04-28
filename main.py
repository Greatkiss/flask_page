from calendar import week
import os
from flask import Flask, request, redirect, url_for, flash, render_template, send_file
from werkzeug.utils import secure_filename
import shutil
import zipfile
from Scraping_gnavi import scrape
from flask_sslify import SSLify

# アップロード先のディレクトリ
UPLOAD_FOLDER = './uploads'
TEMP_FOLDER = './temp'
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
    work_list = ["scraping", "test", "test1"]
    if request.method == 'POST':
        action = request.form["what_to_do"]
        if action == "scraping":
            return redirect(url_for('uploads_files'))
    return render_template("homepage.html", title="home", work_list = work_list)

@app.route('/scrape', methods=['GET', 'POST'])
def uploads_files():
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
            os.mkdir(TEMP_FOLDER)
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
            return redirect(url_for('confirm_info'))
    return render_template("uploadpage.html", title="upload", name="Hoge")

@app.route('/scrape/confirm_info', methods=['GET','POST'])
def confirm_info():
    path = './uploads'
    files = []
    for filename in os.listdir(path):
        if os.path.isfile(os.path.join(path, filename)): #ファイルのみ取得
            files.append(filename)
    idpasslist = files
    if request.method == 'POST':
        ipfilename = request.form['idpassfilename']
        n = request.form['data_num']
        weekdate = request.form['weekdate']
        if ipfilename == '':
            flash('ファイルがありません')
            return redirect(request.url)
        return redirect(url_for('run_da_scrape',num = n, excelname = ipfilename, weekdate = weekdate))
    return render_template("confirm.html", title="confirm", idpasslist = idpasslist)

@app.route('/scrape/run/<excelname>/<weekdate>/<num>')
def run_da_scrape(num, excelname, weekdate):
    print("RUN DA SCRAPE with the {}".format(excelname))
    scrape.main(int(num), "./uploads/{}".format(excelname), str(weekdate))
    return redirect(url_for('dl_da_results'))

@app.route('/scrape/download', methods=['GET','POST'])
def dl_da_results():
    if request.method == 'POST':
        filepath = "./results.zip"
        send_file(filepath, as_attachment = True, attachment_filename = os.path.basename(filepath))
        #os.remove(filepath)
        return redirect(url_for('home'))
    return render_template("dl_zip.html")

if __name__ == "__main__":
    app.run(debug=True)