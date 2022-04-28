import os
from flask import Flask, request, redirect, url_for, flash, render_template
from werkzeug.utils import secure_filename
from flask import send_from_directory
from Scraping_gnavi import scrape

# 画像のアップロード先のディレクトリ
UPLOAD_FOLDER = './uploads'
# アップロードされる拡張子の制限
ALLOWED_EXTENSIONS = set(['xlsx', 'csv', 'pdf'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allwed_file(filename):
    # .があるかどうかのチェックと、拡張子の確認
    # OKなら１、だめなら0
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def uploads_file():
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
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # アップロード後のページに転送
            return redirect(url_for('confirm_info'))
    return render_template("uploadpage.html", title="upload", name="Hoge")

@app.route('/confirm_info', methods=['GET','POST'])
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
        if ipfilename == '':
            flash('ファイルがありません')
            return redirect(request.url)
        return redirect(url_for('run_da_scrape',num = n, excelname = ipfilename))
    return render_template("confirm.html", title="confirm", idpasslist = idpasslist)

@app.route('/run/<excelname>/<num>')
def run_da_scrape(num, excelname):
    print("RUN DA SCRAPE with the {}".format(excelname))
    scrape.main(int(num), "./uploads/{}".format(excelname))
    return render_template("scraping.html", title="confirm")

if __name__ == "__main__":
    app.run(debug=True)