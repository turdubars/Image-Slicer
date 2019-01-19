import os
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory, send_file
from werkzeug.utils import secure_filename
import image_slicer
import io
import zipfile
from PIL import Image, ImageDraw, ImageFont
import glob

# def absolute_file_paths(directory):
#    for dirpath,_,filenames in os.walk(directory):
#        for f in filenames:
#            yield os.path.abspath(os.path.join(dirpath, f))

def slice_picture(picture_path, rows, columns):
    tiles = image_slicer.slice(picture_path, (rows * columns))
    return tiles

def zip_pictures(tiles, save_path):
    with zipfile.ZipFile(save_path, 'w') as zip:
        for tile in tiles:
            with io.BytesIO() as data:
                tile.save(data)
                zip.writestr(tile.generate_filename(path=False),
                             data.getvalue())
    print("Zip is created")

def save_pictures(tiles, save_path):
    try:
        os.mkdir(save_path)
    except:
        print("Folder is already exists")
    save_path = "%s/" % save_path
    # print(save_path)

    image_slicer.save_tiles(tiles, directory=save_path, prefix='slice')

    return save_path


UPLOAD_FOLDER = '/home/arstan/Desktop/Flask/uploaded_pictures'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# basedir = os.path.abspath(os.path.dirname(__file__))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index_page():
    return redirect(url_for('upload_file'))
#
# @app.route('/', methods=['POST'])
# def go_upload_page():
#     return redirect(url_for('upload_file'))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        rows = request.form.get('rows', type=int)
        columns = request.form.get('columns', type=int)
        print("rows =", rows)
        print("columns =", columns)
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            global file_name
            file_name = secure_filename(file.filename)
            global file_name_without_extenction
            file_name_without_extenction = (os.path.splitext(file_name)[0])
            picture_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
            file.save(picture_path)
            global tiles
            tiles = slice_picture(picture_path, rows, columns)
            slices_path = save_pictures(tiles, ("static/pictures/%s" % file_name_without_extenction))
            global zip_path
            zip_path = ("static/picture_archives/%s.zip" % file_name_without_extenction)
            print(zip_path)
            zip_pictures(tiles, zip_path)
            return redirect(url_for('show_pictures', slices_path=slices_path, rows=rows, columns=columns))
            # return redirect(url_for('slice_picture'))
            # return get_pictures(tiles)

    return render_template('index.html')

@app.route('/show_pictures', methods=['GET', 'POST'])
def show_pictures():

    slices_path = request.args['slices_path']
    rows = int(request.args['rows'])
    # print(rows)
    columns = int(request.args['columns'])
    # print(columns)
    # prev_path = slices_path
    print("slices_path before = %s" % slices_path)
    # slices = absolute_file_paths(slices_path)
    slices = os.listdir(slices_path)

    index = 0
    while(index < len(slices)):
        # print(slices_path)
        # print(slices[index])
        slices[index] = slices_path + slices[index]
        # print(slices[index])
        index += 1

    return render_template('get_pictures.html', slices=slices, rows=rows, columns=columns)

@app.route('/download_pictures', methods=['GET', 'POST'])
def download_pictures():
    if request.method == 'POST':
        print(file_name_without_extenction)
        print(zip_path)
        # send_from_directory(directory=zip_path, filename='%s.zip' % file_name_without_extenction)
        return send_file(zip_path, attachment_filename="%s.zip" % file_name_without_extenction, as_attachment=True)
    # return 'Download page'

if __name__ == "__main__":
    app.run(debug=True)
