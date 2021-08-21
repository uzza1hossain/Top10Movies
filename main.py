import os

import response as response
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie-db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250))
    year = db.Column(db.INTEGER)
    description = db.Column(db.String(250))
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(250))
    img_url = db.Column(db.String(250))


db.create_all()


class UpdateMovie(FlaskForm):
    rating = StringField(label='Your Rating out of 10 e.g. 7.5', validators=[DataRequired()])
    review = StringField(label='Your review', validators=[DataRequired(), Length(max=250)])
    submit = SubmitField(label='Done')


class AddMovie(FlaskForm):
    title = StringField(label='Movie Title', validators=[DataRequired(), Length(max=250)])
    submit = SubmitField(label='Add Movie')


# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
#
# db.session.add(new_movie)
# db.session.commit()

def search_movies(movie_name):
    search_response = requests.get(
        f"https://api.themoviedb.org/3/search/movie?api_key={os.environ.get('API')}&query={movie_name}").json()  # {os.environ.get('API')}
    return search_response


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies_list=all_movies)


@app.route('/update', methods=['GET', 'POST'])
def update():
    update_form = UpdateMovie()
    movie_id = request.args.get('id')
    movie_to_update = Movie.query.get(movie_id)
    if update_form.validate_on_submit():
        movie_to_update.rating = float(update_form.rating.data)
        movie_to_update.review = update_form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form=update_form, movie_id=movie_to_update)


@app.route('/delete')
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/add', methods=['GET', 'POST'])
def add():
    add_form = AddMovie()
    if add_form.validate_on_submit():
        search_result = search_movies(add_form.title.data)
        search_result = search_result['results']
        return render_template('select.html', movies=search_result)
    return render_template('add.html', form=add_form)


@app.route('/find')
def find_movie():
    movie_api_id = request.args.get('id')
    find_response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_api_id}?api_key={os.environ.get("API")}').json()
    new_movie = Movie(
        title=find_response['original_title'],
        description=find_response['overview'],
        year=find_response['release_date'].split('-')[0],
        img_url=f"https://image.tmdb.org/t/p/w500{find_response['poster_path']}"
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('home'))


    # print(f"Title - {find_response['original_title']}\n"
    #       f"Description - {find_response['overview']}\n"
    #       f"Year - {find_response['release_date'].split('-')[0]}")


if __name__ == '__main__':
    app.run(debug=True)
