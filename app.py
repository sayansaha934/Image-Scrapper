from flask import Flask, request, render_template, send_file
from Scrapper.imageScrapper import imageScrapping
from application_logging.logger import app_log
import shutil
import os
app=Flask(__name__)
lg=app_log(username='image', password='image')

@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        zipFiles=[file for file in os.listdir(os.getcwd()) if file.endswith('.zip')]
        for file in zipFiles:
            os.remove(file)
    except Exception as e:
        lg.log(tag='ERROR', message=f'Something went wrong to remove zip file')
        return render_template('index.html', message='Something went wrong')
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    try:
        scrap=imageScrapping()
        search_term=request.form['search_term']
        img_number=int(request.form['img_number'])

        search_term=search_term.replace(' ','-')

        scrap.search_and_download(search_term=search_term, expected_img_number=img_number)
        lg.log(tag='INFO', message='Image scrapping Successful!!')
        shutil.make_archive(search_term,'zip', search_term)
        lg.log(tag='INFO', message='.zip File created successfully')
        shutil.rmtree(search_term)
        return send_file(search_term+'.zip', as_attachment=True)
    except Exception as e:
        lg.log(tag='ERROR', message=f'Something went wrong: {e}')
        return render_template('index.html', message='Something went wrong')

if __name__=='__main__':
    app.run()