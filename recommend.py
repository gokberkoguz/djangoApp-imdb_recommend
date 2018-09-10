import pandas as pd
import os
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import json
from ast import literal_eval
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def readData():
    absPath=os.path.dirname(os.path.realpath(__import__("__main__").__file__))
    dataSets='\dataset\\tmdb_5000_movies.csv'
    dataSets=absPath+dataSets
    print(dataSets)
    metadata = pd.read_csv(dataSets, low_memory=False)
    return metadata

class titleBasedRecommendation():
    def __init__(self):
        self.metadata = readData()
        tfidf = TfidfVectorizer(stop_words='english')
        self.metadata['overview'] = self.metadata['overview'].fillna('')
        tfidf_matrix = tfidf.fit_transform(self.metadata['overview'])
        print(tfidf_matrix.shape)
        self.cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
        self.indices = pd.Series(self.metadata.index, index=self.metadata['title']).drop_duplicates()
        print(self.get_recommendations('The Dark Knight Rises'))
        # Function that takes in movie title as input and outputs most similar movies

    def get_recommendations(self, title):
        # Get the index of the movie that matches the title
        idx = self.indices[title]

        # Get the pairwsie similarity scores of all movies with that movie
        sim_scores = list(enumerate(self.cosine_sim[idx]))

        # Sort the movies based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get the scores of the 10 most similar movies
        sim_scores = sim_scores[1:11]

        # Get the movie indices
        movie_indices = [i[0] for i in sim_scores]

        # Return the top 10 most similar movies
        return self.metadata['title'].iloc[movie_indices]

class contentBasedRecommendation():
    def __init__(self,title):
        metadata=readData()
        #print(metadata['credits'])
        genres=metadata[['title','genres','keywords']]
        metadata=genres
        features = ['genres', 'keywords']
        for feature in features:
            metadata[feature] = metadata[feature].apply(literal_eval)
        features = ['genres', 'keywords']
        for feature in features:
            metadata[feature] = metadata[feature].apply(self.get_list)
        features = ['keywords', 'genres']
        for feature in features:
            metadata[feature] = metadata[feature].apply(self.clean_data)
        metadata['soup'] = metadata.apply(self.create_soup, axis=1)
        count = CountVectorizer(stop_words='english')
        count_matrix = count.fit_transform(metadata['soup'])
        self.cosine_sim2 = cosine_similarity(count_matrix, count_matrix)
        self.metadata = metadata.reset_index()
        self.indices = pd.Series(metadata.index, index=metadata['title'])
        print(self.get_recommendations(title, self.cosine_sim2))

    def get_list(self,x):
            if isinstance(x, list):
                names = [i['name'] for i in x]
                #Check if more than 3 elements exist. If yes, return only first three. If no, return entire list.
                if len(names) > 3:
                    names = names[:3]
                return names

            #Return empty list in case of missing/malformed data
            return []

    def clean_data(self,x):
        if isinstance(x, list):
            return [str.lower(i.replace(" ", "")) for i in x]
        else:
            #Check if director exists. If not, return empty string
            if isinstance(x, str):
                return str.lower(x.replace(" ", ""))
            else:
                return ''

    def create_soup(self,x):
        return ' '.join(x['keywords'])  + ' '.join(x['genres'])

    def get_recommendations(self,title, cosine_sim):
        # Get the index of the movie that matches the title
        idx = self.indices[title]

        # Get the pairwsie similarity scores of all movies with that movie
        sim_scores = list(enumerate(cosine_sim[idx]))

        # Sort the movies based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get the scores of the 10 most similar movies
        sim_scores = sim_scores[1:11]

        # Get the movie indices
        movie_indices = [i[0] for i in sim_scores]

        # Return the top 10 most similar movies
        return self.metadata['title'].iloc[movie_indices]


if __name__ == '__main__':
    contentBasedRecommendation("The Godfather")