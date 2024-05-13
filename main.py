from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies.db"
Bootstrap5(app)

MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
#url = "https://api.themoviedb.org/3/search/movie?query=phone%20booth&include_adult=false&language=en-US&page=1"


headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyYzU5ZmE0NGRmMDRiNzE1NDg1NmM3YmE2YTY2NGUxMiIsInN1YiI6IjY2Mzk0M2QxOTU5MGUzMDEyNmJkOGQxZSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.8oSmQq7msmNtM6nJLcooK2_zapqFoJ7wpA-Mv-XST68"
}


# CREATE DB
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CREATE TABLE
class Movie(db.Model):
    id = mapped_column(Integer, primary_key=True)
    title = mapped_column(String(100), unique=True)
    year = mapped_column(Integer)
    description = mapped_column(String(250))
    rating = mapped_column(Float, nullable=False)
    ranking = mapped_column(Integer, nullable=True)
    review = mapped_column(String(250))
    img_url = mapped_column(String(150))

class Update_Form(FlaskForm):
    rating = StringField(label="Your Rating Out of 10 e.g. 7.5", validators=[DataRequired()])
    review = StringField(label="Your Review", validators=[DataRequired()])
    submit = SubmitField(label="Done")


class Add_movie(FlaskForm):
    title = StringField(label="Movie Title", validators=[DataRequired()])
    add = SubmitField(label="Add Movie")

with app.app_context():
    db.create_all()




@app.route("/")
def home():
    movies = Movie.query.order_by(Movie.ranking).all()
    return render_template("index.html", movies=movies)


@app.route("/edit", methods=["GET", "POST"])
def update():
    form = Update_Form()
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movie, movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)

@app.route("/delete", methods=["GET", "POST"])
def delete():
    movie_id = request.args.get("id")
    movie_to_delete = db.get_or_404(Movie, movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/add", methods=['POST', 'GET'])
def add():
    add_form = Add_movie()
    if add_form.validate_on_submit():
        title = add_form.title.data.lower()
        title_str = title.replace(" ", "%20")
        query_url = f"{MOVIE_DB_SEARCH_URL}?query={title_str}&include_adult=false&language=en-US&page=1"
        response = requests.get(query_url, headers=headers)
        data = response.json()['results']
        return render_template("select.html", options=data)
    return render_template("add.html", form=add_form)


@app.route("/find", methods=['POST', 'GET'])
def select(id):
    query_url = f"https://api.themoviedb.org/3/movie/{id}?language=en-US"
    response = requests.get(query_url, headers=headers)
    data = response.json()
    title = data['original_title']
    img_url = data['poster_path']
    year = data['release_data'].split('-')[0]
    description = data['overview']
    new_movie = Movie(
        title=title,
        year=year,
        img_url=img_url,
        description=description
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('/home'))


@app.route("/find", methods=['POST','GET'])
def find():

    return render_template("select.html")

if __name__ == '__main__':
    app.run()
