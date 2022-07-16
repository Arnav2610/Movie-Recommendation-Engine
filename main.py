from flask import Flask, render_template, flash, request, url_for, redirect
import pandas as pd
from math import sqrt
import numpy as np


app = Flask(__name__)
app.secret_key = "Arnav"


def recommend(userInput):
  #using panda library to read file
  movies_df = pd.read_csv('dataset/movies.csv')
  ratings_df = pd.read_csv('dataset/ratings.csv')
  
  movies_df['year'] = movies_df.title.str.extract('(\(\d\d\d\d\))',expand=False)
  movies_df['year'] = movies_df.year.str.extract('(\d\d\d\d)',expand=False)
  movies_df['title'] = movies_df.title.str.replace('(\(\d\d\d\d\))', '')
  movies_df['title'] = movies_df['title'].apply(lambda x: x.strip())
  
  movies_df['genres'] = movies_df.genres.str.split('|')
  moviesWithGenres_df = movies_df.copy()
  
  #turning the dataset into a matrix displaying the genres
  for index, row in movies_df.iterrows():
      for genre in row['genres']:
          moviesWithGenres_df.at[index, genre] = 1
  moviesWithGenres_df = moviesWithGenres_df.fillna(0)
  
  #removing timestamp because its unnecessary
  ratings_df = ratings_df.drop('timestamp', 1)

  inputMovies = pd.DataFrame(userInput)
  
  inputId = movies_df[movies_df['title'].isin(inputMovies['title'].tolist())]
  inputMovies = pd.merge(inputId, inputMovies)
  inputMovies = inputMovies.drop('genres', 1).drop('year', 1)
  userMovies = moviesWithGenres_df[moviesWithGenres_df['movieId'].isin(inputMovies['movieId'].tolist())]
  
  userMovies = userMovies.reset_index(drop=True)
  userGenreTable = userMovies.drop('movieId', 1).drop('title', 1).drop('genres', 1).drop('year', 1)
  
  userProfile = userGenreTable.transpose().dot(inputMovies['rating'])
  
  genreTable = moviesWithGenres_df.set_index(moviesWithGenres_df['movieId'])
  genreTable = genreTable.drop('movieId', 1).drop('title', 1).drop('genres', 1).drop('year', 1)
  
  recommendationTable_df = ((genreTable*userProfile).sum(axis=1))/(userProfile.sum())
  
  recommendationTable_df = recommendationTable_df.sort_values(ascending=False)
  final_table = movies_df.loc[movies_df['movieId'].isin(recommendationTable_df.head(15).keys())]
  final_table = final_table.drop('movieId', 1)
  
  return final_table



@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    userInput = [
                {'title':'', 'rating':5},
                {'title':'', 'rating':5},
                {'title':'', 'rating':5},
                {'title':'', 'rating':5},
                {'title':'', 'rating':5}
             ] 
    userInput[0]['title'] = request.form.get('name1')
    userInput[0]['rating'] = int(request.form.get('rating1'))
    userInput[1]['title'] = request.form.get('name2')
    userInput[1]['rating'] = int(request.form.get('rating2'))
    userInput[2]['title'] = request.form.get('name3')
    userInput[2]['rating'] = int(request.form.get('rating3'))
    userInput[3]['title'] = request.form.get('name4')
    userInput[3]['rating'] = int(request.form.get('rating4'))
    userInput[4]['title'] = request.form.get('name5')
    userInput[4]['rating'] = int(request.form.get('rating5'))
    print(userInput)
    results = recommend(userInput)
    print(results)
    print(results['title'])
    return render_template('recommendations.html', titles = results['title'])
    
  return render_template('index.html')


@app.route('/recommendations')
def recommendations():
  return render_template('recommendations.html')


if __name__ == "__main__":
  app.run(host='0.0.0.0', port='8080', debug=True)