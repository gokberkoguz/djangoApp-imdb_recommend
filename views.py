from __future__ import unicode_literals
from django.shortcuts import render
import subprocess
import os
import sys
import sqlite3 as lite
import json
from django.http import HttpResponse
from imdb import IMDb
from django.shortcuts import redirect
import time
from rest_framework.response import Response
from rest_framework.views import APIView



ia = IMDb()



def absPath():
    return os.path.dirname(os.path.realpath(__import__("__main__").__file__))
def main(request):

    user=request.user
    #get user info
    userInfo=getUserInfo(user)
    userName=userInfo[0]['user_id']
    #get watch lists
    watchedList=getUserWatchedLists(userName)
    watchList=getUserWatchLists(userName)

    if request.method == "POST":
        filmLink = request.POST.get("filmLink")
        print(filmLink)
        filmLink=filmLink.replace(' ','_')
        return redirect('app2/search/'+filmLink)
    return render(request, 'imdb_recommend/index.html',{'watchedList':watchedList,'watchList':watchList,'user':userInfo})


def searchMovie(request, title):
    movies=searchIMDB(title)
    print('movies')
    return render(request, 'imdb_recommend/search.html',{'movies':movies})

def getMovie(request, title):
    print('getMovie')
    title=title.replace('_',' ')
    movies = ia.search_movie(title)
    movie = ia.get_movie(movies[0].movieID)
    try:
        postDb(movie['title'], movie['cover url'], movie['plot outline'])
    except:
        print('already exist')
    user=request.user
    userInfo=getUserInfo(user)
    userID=userInfo[0]['user_id']

    if request.method == "POST":
        if "watchedList" in request.POST:
            pushWatchedMovie(movie['title'],userID)
            return redirect('/home/movies')

        if "watchList" in request.POST:
            pushWatchMovie(movie['title'],userID)
            return redirect('/home/movies')




    return render(request, 'imdb_recommend/getMovie.html',{'title':movie['title'],'cover_url':movie['cover url'],'plot':movie['plot outline']})

def searchIMDB(title):
    movies = ia.search_movie(title)
    return movies

#oldMethod
def postDb(title,cover_url,text):
    con = lite.connect('imdb_recommend/movies.db')
    cur = con.cursor()
    command=("""INSERT INTO movies (title,cover_url,text) VALUES ('%s','%s','text')""" %(title,cover_url))
    print(command)
    cur.execute(command)
    con.commit()
    con.close()

def watchedList(request):
    con = lite.connect('imdb_recommend/movies.db')
    cur = con.cursor()
    command=("""SELECT * FROM movies""")
    cur.execute(command)
    data =[{'title': row[1],
            'cover_url': row[2],
            'text':row[3]}
               for row in cur.fetchall()]
    con.commit()
    con.close()
    return render(request,'imdb_recommend/printWatchedList.html', {'data': data})

def getUserInfo(user):
    con = lite.connect('imdb_recommend/movies.db')
    cur = con.cursor()
    command=("""SELECT * FROM users WHERE user_name='%s' """ %(str(user)))
    print(command)
    cur.execute(command)
    data =[{'user_id': row[0],
            'user_name': row[1],
            'mail':row[2]} for row in cur.fetchall()]
    con.commit()
    con.close()
    return data

def getUserWatchedLists(user_id):
    print(user_id)
    con = lite.connect('imdb_recommend/movies.db')
    cur = con.cursor()
    command=("""SELECT movie_id,name,point FROM watched_list WHERE user_id=%s""" %(user_id))
    cur.execute(command)
    data =[{'movie_id': row[0],
            'name': row[1],
            'point':row[2]} for row in cur.fetchall()]
    con.commit()
    con.close()
    return data

def getUserWatchLists(user_id):
    con = lite.connect('imdb_recommend/movies.db')
    cur = con.cursor()
    command=("""SELECT movie_id,name FROM watch_list WHERE user_id=%s""" %(user_id))
    cur.execute(command)
    data =[{'movie_id': row[0],
            'name': row[1]} for row in cur.fetchall()]
    con.commit()
    con.close()
    return data

def pushWatchedMovie(title,id):

    con = lite.connect('imdb_recommend/movies.db')
    cur = con.cursor()
    command=("""SELECT id,title FROM movies WHERE title='%s' """ %(title))
    cur.execute(command)
    data =[{'movie_id': row[0],
            'title': row[1]} for row in cur.fetchall()]
    con.commit()
    print(data)

    command=("""INSERT INTO watched_list (movie_id,name,user_id) VALUES(%s,'%s',%s) """ % (data[0]['movie_id'],data[0]['title'],id))
    print(command)
    cur.execute(command)
    con.commit()
    con.close()


def pushWatchMovie(title,id):
    print(title)
    con = lite.connect('imdb_recommend/movies.db')
    cur = con.cursor()
    command=("""SELECT id,title FROM movies WHERE title='%s' """ %(title))
    cur.execute(command)
    data =[{'movie_id': row[0],
            'title': row[1]} for row in cur.fetchall()]
    con.commit()
    print(data)

    command=("""INSERT INTO watch_list (movie_id,name,user_id) VALUES(%s,'%s',%s) """ % (data[0]['movie_id'],data[0]['title'],id))
    print(command)
    cur.execute(command)
    con.commit()
    con.close()

def clickwatched(request,title):

    if '_' in title:
        title=title.replace('_',' ')

    con = lite.connect('imdb_recommend/movies.db')
    cur = con.cursor()
    command=("""SELECT id FROM movies WHERE title='%s' """ %(title))
    cur.execute(command)
    data =[{'movie_id': row[0]} for row in cur.fetchall()]
    command=("""SELECT movie_id,name,user_id FROM watch_list WHERE movie_id='%s' """ %(data[0]['movie_id']))
    cur.execute(command)
    data =[{'movie_id': row[0],
            'name': row[1],
            'user_id': row[2]
             } for row in cur.fetchall()]

    command=("""DELETE FROM watch_list WHERE movie_id='%s' """ %(data[0]['movie_id']))
    cur.execute(command)

    command=("""INSERT INTO watched_list (movie_id,name,user_id) VALUES(%s,'%s',%s)  """ %(data[0]['movie_id'],data[0]['name'],data[0]['user_id']))
    cur.execute(command)

    con.commit()
    return redirect('/home/movies/')

def siradaki(request):
    return render(request,'imdb_recommend/siradaki.html')

