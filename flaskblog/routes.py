from flask import render_template, url_for, flash, redirect,request
from flaskblog import app,db,bcrypt
from flaskblog.forms import RegistrationForm, LoginForm,UpdateAccountForm,ReviewForm
from flaskblog.models import User,Post
import json
import requests 
import secrets
import os
from PIL import Image 
from flask_login import login_user,current_user,logout_user,login_required
import cgi




new_list=[]
tmdb_api_key="4f64aca2fe9849ea1c8723daee649b0f"


@app.route("/")
@app.route("/home",methods=['GET','POST'])
def home():
    posts=Post.query.all()
    response = requests.get('https://api.themoviedb.org/3/trending/movie/week?api_key=4f64aca2fe9849ea1c8723daee649b0f')
    display = response.json()
    display_movies=display['results']
    r = json.dumps(display_movies)
    loaded_r = json.loads(r)
    movie_info={}
    for i in loaded_r:
        l=[]
        movie_title=i['original_title']
        l.append(i['poster_path'])
        l.append(i['id'])
        movie_info[movie_title]=l

    #return render_template('test.html',movie_info=movie_info)
    return render_template('home.html',movie_info=movie_info)

@app.route("/")

@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,email=form.email.data,password=hashed_password,
            fav_actor=form.fav_actor.data,fav_director=form.fav_director.data,fav_genre=form.fav_genre.data,
            fav_movie=form.fav_movie.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def get_actor(id):
    movie_id=str(id)
    response = requests.get('https://api.themoviedb.org/3/movie/'+movie_id+'/credits?api_key=4f64aca2fe9849ea1c8723daee649b0f')
    display = response.json()
    display_movies=display['cast']
    crew=[]
    i=0
    for char in display_movies:
        l=[]
        if i==4:
            break
        l.append(char['name'])
        l.append(char['profile_path'])
        crew.append(l)
        i=i+1
    return crew


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _,f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex+f_ext
    picture_path = os.path.join(app.root_path,'static/profile_pics',picture_fn)
    output_size = (125,125)
    i=Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route("/account",methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    actor_info='Christane Bale'
    #response=requests.get('http://api.tmdb.org/3/search/person?api_key='+tmdb_api_key '&query='+current_user.fav_actor)
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.fav_actor = form.fav_actor.data
        current_user.fav_director = form.fav_director.data
        current_user.fav_genre = form.fav_genre.data
        current_user.fav_movie = form.fav_movie.data
        db.session.commit()
        flash('Your account has been updated!','success')
        return redirect(url_for('account'))
    elif request.method== 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.fav_actor.data = current_user.fav_actor
        form.fav_director.data = current_user.fav_director
        form.fav_genre.data = current_user.fav_genre
        form.fav_movie.data = current_user.fav_movie

    image_file = url_for('static',filename='profile_pics/'+ current_user.image_file)
    #response=requests.get('http://api.tmdb.org/3/search/person?api_key='+tmdb_api_key '&query='+current_user.fav_actor)
    information=actor_bio(current_user.fav_actor)
    return render_template('account.html',title="Account",image_file=image_file,form=form,information=information,new_list=new_list)

def actor_information(actor_info):
    response=requests.get('https://api.themoviedb.org/3/search/person?api_key=4f64aca2fe9849ea1c8723daee649b0f&language=en-US&query='+actor_info+'&page=1&include_adult=false')
    display = response.json()
    display_info=display['results']
    r = json.dumps(display_info)
    loaded_r = json.loads(r)
    actor_info={}
    for i in loaded_r:
        l=[]
        actor_name=i['name']
        l.append(i['profile_path'])
        l.append(i['known_for'])
        l.append(i['id'])
        actor_info[actor_name]=l
    return actor_info

def actor_bio(actor_name):
    actor_info={}
    actor_info=actor_information(actor_name)
    info=[]
    for i,l in actor_info.items():
        info.append(i)
        info.append(l[0])
        info.append(l[2])
        for k in l[1]:
            for key,value in k.items():
                if key=='original_title':
                    info.append(value)

    id=str(info[2])
    response=requests.get('https://api.themoviedb.org/3/person/'+id+'?api_key=4f64aca2fe9849ea1c8723daee649b0f&language=en-US')
    display1 = response.json()
    for key,value in display1.items():
        if key=='birthday':
            info.append(value)
        elif key=='biography':
            info.append(value)

    return info


@app.route("/movie_details<id>",methods=['GET','POST'])
def movie_details(id):
    movie_id=str(id)
    response=requests.get('https://api.themoviedb.org/3/movie/'+movie_id+'?api_key=4f64aca2fe9849ea1c8723daee649b0f&language=en-US')
    i = response.json()
    l=[]
    movie={}
    movie_name=i["original_title"]
    l.append(i["poster_path"])
    l.append(i["overview"])
    l.append(i["vote_average"])
    l.append(i["genres"])
    l.append(i["release_date"])
    l.append(i["id"])
    movie[movie_name]=l
    key=trailer_key(id)
    sim_movies=similar_movies(id)
    actors=get_actor(id)
    return render_template('movie_details.html',movie=movie,key=key,sim_movies=sim_movies,movie_name=movie_name,actors=actors)

def similar_movies(id):
    movie_id=str(id)
    response=requests.get('https://api.themoviedb.org/3/movie/'+movie_id+'/similar?api_key=4f64aca2fe9849ea1c8723daee649b0f&language=en-US&page=1')
    display = response.json()
    display_info=display['results']
    i=0
    sim_info=[]
    for movie in display_info:
        l=[]
        if i==8:
            break
        for key,value in movie.items():
            if key=='id':
                l.append(value)
            if key=='poster_path':
                l.append(value)
            if key=='original_title':
                l.append(value)
        sim_info.append(l)
        i=i+1
    return sim_info

def recommend_movies(id):
    movie_id=str(id)
    response=requests.get('https://api.themoviedb.org/3/movie/'+movie_id+'/recommendations?api_key=4f64aca2fe9849ea1c8723daee649b0f&language=en-US&page=1')
    display = response.json()
    display_info=display['results']
    i=0
    rec_info=[]
    for movie in display_info:
        l=[]
        if i==12:
            break
        for key,value in movie.items():
            if key=='id':
                l.append(value)
            if key=='poster_path':
                l.append(value)
            if key=='original_title':
                l.append(value)
        rec_info.append(l)
        i=i+1
    return rec_info

def trailer_key(id):
    res=requests.get('https://api.themoviedb.org/3/movie/'+id+'/videos?api_key=4f64aca2fe9849ea1c8723daee649b0f&language=en-US')
    dis=res.json()
    dis_info=dis['results']
    for i in dis_info:
        l=[]
        for k,v in i.items():
            if k=='type' and v=='Trailer':
                return i['key']
    return 0

@app.route("/search",methods=["GET","POST"])
def search():
    movie=request.form["searchText"]
    search_movie=str(movie)
    loaded_r = search_movie_by_name(search_movie)
    movie_info={}
    for i in loaded_r:
        l=[]
        movie_title=i['original_title']
        l.append(i['poster_path'])
        l.append(i['overview'])
        l.append(i['vote_average'])
        l.append(i['id'])
        id=str(i['id'])
        key=trailer_key(id)
        l.append(key)
        movie_info[movie_title]=l
    return render_template('search.html',movie_info=movie_info,search_movie=search_movie)
    #return render_template('about.html')

#@app.route("/watchlist",method=['GET', 'POST'])
#def watchlist():

def movies_similar_to_fav_movie():
    loaded_r=search_movie_by_name(str(current_user.fav_movie))
    id=0
    for i in loaded_r:
        id=i['id']
        break
    rec_info=recommend_movies(id)
    return rec_info



def search_movie_by_name(movie_name):
    response = requests.get('https://api.themoviedb.org/3/search/movie?api_key=4f64aca2fe9849ea1c8723daee649b0f&language=en-US&query='+movie_name+'&page=1&include_adult=false')
    display = response.json()
    display_movies=display['results']
    r = json.dumps(display_movies)
    return json.loads(r)

@app.route("/create_review/new<movie_name>",methods=['GET', 'POST'])    
@login_required
def create_review(movie_name):
    form = ReviewForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,content=form.content.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your Review about the movie has been posted!','success')
        return redirect(url_for('home'))
    return render_template('create_review.html',title='New Review',form=form,movie_name=movie_name)

@app.route("/add_movie_to_watchlist<movie_name>",methods=['GET', 'POST'])    
@login_required
def add_movie_to_watchlist(movie_name):
    mn=movie_name+","
    list_of_movies=None
    l=current_user.watchlist
    lm=str(l)
    if lm=='None':
        lm=" "
    list_of_movies=mn+lm
    current_user.watchlist=list_of_movies
    db.session.commit()
    flash(f'{ movie_name } has been added to your Watchlist!','success')
    return redirect(url_for('home'))

@app.route("/your_watchlist",methods=['GET', 'POST'])
@login_required
def your_watchlist():
    list_of_movies=str(current_user.watchlist)
    if list_of_movies=='None':
        flash('You have not added anything to your Watchlist yet.','danger')
        return redirect(url_for('home'))
    new_list = list(list_of_movies.split(","))
    new_list = list(set(new_list)) 
    new_list.remove(" ")
    movie_dict={}
    for name in new_list:
        loaded_r=search_movie_by_name(name)
        l=[]
        count=0
        for i in loaded_r:
            if count==1:
                break
            l.append(i['poster_path'])
            l.append(i['id'])
            count=count+1
            movie_dict[name]=l

    return render_template('watchlist.html',movie_dict=movie_dict)

@app.route('/recommended_movies',methods=['GET','POST'])
@login_required
def recommended_movies():
    loaded_r=search_movie_by_name(str(current_user.fav_movie))
    id=0
    for i in loaded_r:
        id=i['id']
        break
    rec_info=recommend_movies(id)
    return render_template('recommended_movies.html',rec_info=rec_info)

@app.route('/reviews',methods=['GET','POST'])
@login_required
def reviews():
    posts=Post.query.all()
    if posts is None:
        flash('No reviews available right now.','danger')
        return redirect(url_for('home'))
    return render_template('review.html',posts=posts)

