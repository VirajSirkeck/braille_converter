import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import alphaToBraille, brailleToAlpha

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

class Braille(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inp = db.Column(db.String(200), nullable=False)
    out = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Entry %r>' % self.id


@app.route('/', methods=['POST', 'GET'])

def index():
    if request.method == 'POST':
        text_inp = request.form['inp']
        text_out = alphaToBraille.translate(text_inp)
        new = Braille(inp=text_inp, out=text_out)

        try:
            db.session.add(new)
            db.session.commit()
            return redirect('/')
        except:
            return "There was an issue"
    else:
        text = Braille.query.order_by(Braille.id.desc()).first()
        return render_template('index.html', text=text)

@app.route('/braille_to_alpha', methods=['POST', 'GET'])

def braille_to_alpha():
    if request.method == 'POST':
        text_inp = request.form['inp']
        text_out = brailleToAlpha.translate(text_inp)
        new = Braille(inp=text_inp, out=text_out)

        try:
            db.session.add(new)
            db.session.commit()
            return redirect('/braille_to_alpha')
        except:
            return "There was an issue"
    else:
        text = Braille.query.order_by(Braille.id.desc()).first()
        return render_template('braille_to_alpha.html', text=text)

@app.route('/history')

def history():
        texts = Braille.query.order_by(Braille.id.desc()).all()
        return render_template('history.html', texts=texts)

if __name__ == "__main__":
    app.run(debug=True)