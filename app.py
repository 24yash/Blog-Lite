from flask import Flask, render_template, redirect, request

from models import *
from resources import *

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///datablog.sqlite3"
app.app_context().push()
db.init_app(app)
api.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == "POST":
    form = request.form
    check_user = User.query.filter_by(username=str(request.form['username'])).first()

    if check_user is not None:
      if str(form['password']) == check_user.password:
        return redirect(f'/feed/{check_user.id}/{check_user.password}')
      else:
        return "Invalid password"
    else:
      return "Invalid user"
  else:
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
  if request.method == "POST":
    user_exists =User.query.filter_by(username=str(request.form['username'])).first()
    if user_exists is None:
      response = request.form
      if response['username'] and response['password']:
        new_user = User(username=response['username'], password=response['password'])
  
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect('/')
        except:
            return "There was an issue while creating your account, please try again later"
      else:
        return "Username or Password not provided. Go back please!"
    else:
      return "Username is used already. Go back please!"
  else:
    return render_template('signup.html')

@app.route('/feed/<int:id>/<string:password>', methods=['GET', 'POST'])
def feed(id, password):
  if request.method == "POST":
    response = request.form
    user = User.query.filter(User.username==response['username']).first()
    if user is not None:
      userid = user.id
      return redirect(f"/view_user/{id}/{password}/{userid}")
    else:
      return "Invalid username. Please, go back!"
  else:
    return render_template("feed.html", posts=Post.query.all(), id=id, password=password)

@app.route('/only/<int:id>/<string:password>', methods=['GET', 'POST'])
def only(id, password):
  following = Follow.query.filter(Follow.follower_id==id).with_entities(Follow.followed_id).all()
  length = len(following)
  results = []
  posti = Post.query.filter(Post.user_id==id).all()
  for k in posti:
    results.append(k)
  if (length>0):
    res = [i[0] for i in following]
    for i in res:
      postx = Post.query.filter(Post.user_id==i).all()
      for j in postx:
        results.append(j)
  return render_template("only.html", posts=results, id=id, password=password, length=length)

@app.route('/create_post/<int:id>/<string:password>', methods=['GET', 'POST'])
def create_post(id, password):
  if request.method == "POST":
    response = request.form
    if response['title']:
      new_post = Post(title=response['title'], content=response['content'], image=response['image'], creator=User.query.filter_by(id=id).first().username, user_id=id)
      try:
        db.session.add(new_post)
        db.session.commit()
        return redirect(f"/feed/{id}/{password}")
      except:
        return "There was a problem processing. Please go Back!"
    else:
      return "No Title provided. Go Back!"
  else:
    return render_template("new_post.html", id=id, password=password)

@app.route('/update_post/<int:id>/<string:password>/<int:post_id>', methods=['GET', 'POST'])
def update_post(id, password,post_id):
  post = Post.query.filter(Post.id==post_id).first()
  if request.method == "POST":
    response = request.form
    if(post.user_id==id):
      if response['title']:
        post.title = response['title']
      if response['content']:
        post.content = response['content']
      if response['image']:
        post.image = response['image']
      db.session.commit()
      return redirect(f"/view_post/{id}/{password}/{post_id}")
    else:
      return "Post is not made by you. Please go back!"
  else:
    return render_template("update_post.html", id=id, password=password,post=post, post_id=post_id)

@app.route('/delete_post/<int:id>/<string:password>/<int:post_id>', methods=['GET', 'POST'])
def delete_post(id, password, post_id):
  post = Post.query.filter(Post.id==post_id).first()
  if request.method == "POST":
    db.session.delete(post)
    db.session.commit()
    return redirect(f"/feed/{id}/{password}")
  else:
    return render_template("delete_post.html", id=id, password=password, post=post)

@app.route('/update_name/<int:id>/<string:password>', methods=['GET', 'POST'])
def update_name(id, password):
  if request.method == "POST":
    response = request.form
    user = User.query.filter(User.id==id).first()
    posts = Post.query.filter(Post.user_id==id).all()
    if(response['name'] or response['password']):
      if(response['name']):
        for i in posts:
          i.creator = response['name']
        user.username = response['name']
      if(response['password']):
        user.password = response['password']
      db.session.commit()
      return redirect(f"/")
    else:
      return redirect(f"/feed/{id}/{password}")
  else:
    return render_template("update_name.html", id=id, password=password)
  
@app.route('/view_post/<int:user_id>/<string:password>/<int:post_id>', methods=['GET', 'POST'])
def view_post(user_id, password, post_id):
  post = Post.query.filter_by(id=post_id).first()
  number = 0
  if(post.user_id==user_id):
    number = 2
  return render_template('view_post.html', user_id=user_id, password=password, post=post, number = number)

@app.route('/view_user/<int:user_id>/<string:password>/<int:post_user_id>', methods=['GET', 'POST'])
def view_user(user_id, password, post_user_id):
  post = Post.query.filter(Post.user_id==post_user_id).all()
  count = Post.query.filter(Post.user_id==post_user_id).count()
  user = User.query.filter(User.id==post_user_id).one()
  req_id=user.id
  creator = user.username
  followers = Follow.query.filter(Follow.followed_id==req_id).all()
  following = Follow.query.filter(Follow.follower_id==req_id).all()
  number_followers = len(followers)
  number_followed = len(following)
  followers2 = Follow.query.filter(Follow.followed_id==req_id).with_entities(Follow.follower_id).all()
  res = [i[0] for i in followers2]
  result=[]
  for i in res:
    result.append(i)
  if(user_id==post_user_id):
    number = 0
  elif(user_id in result):
    number = 1
  else:
    number = 2
  if request.method == "POST":
    if(number==1):
      follow = Follow.query.filter(Follow.follower_id==user_id, Follow.followed_id==req_id).one()
      db.session.delete(follow)
      db.session.commit()
    if(number==2):
      follow = Follow(follower_id = user_id, followed_id = req_id)
      db.session.add(follow)
      db.session.commit()
    return redirect(f"/view_user/{user_id}/{password}/{req_id}")
  else:
    return render_template('view_user.html',post=post, req_id=req_id, id=user_id,password=password, creator = creator, number_followers=number_followers, number_followed=number_followed, number=number, count=count)

@app.route('/user_followers/<int:id>/<string:password>/<int:req_id>', methods=['GET', 'POST'])
def user_followers(id, password, req_id):
  followers = Follow.query.filter(Follow.followed_id==req_id).with_entities(Follow.follower_id).all()
  length = len(followers)
  res = [i[0] for i in followers]
  result=[]
  for i in res:
    user = User.query.filter(User.id==i).one()
    username=user.username
    username=str(username)
    result.append(username)
  if request.method == "POST":
    return redirect(f"/view_user/{id}/{password}/{req_id}")
  else:
    return render_template('followers.html', number=length, id=id, password=password, result=result, req_id=req_id)

@app.route('/user_following/<int:id>/<string:password>/<int:req_id>', methods=['GET', 'POST'])
def user_following(id, password, req_id):
  following = Follow.query.filter(Follow.follower_id==req_id).with_entities(Follow.followed_id).all()
  length = len(following)
  if (length>0):
    res = [i[0] for i in following]
    results=[]
    for i in res:
      user = User.query.filter(User.id==i).one()
      username=user.username
      username=str(username)
      results.append(username)
  else:
    results=[]
  if request.method == "POST":
    return redirect(f"/view_user/{id}/{password}/{req_id}")
  else:
    return render_template('following.html', number=length, id=id, password=password, result=results,req_id=req_id)

@app.route('/delete_user/<int:id>/<string:password>', methods=['GET', 'POST'])
def delete_user(id, password):
  if request.method == "POST":
    response=request.form
    if(response['password'] == password):
      user = User.query.filter(User.id==id).one()
      username = user.username
      posts = Post.query.filter(Post.creator==username).delete()
      follows = Follow.query.filter(Follow.followed_id==id).delete()
      followers = Follow.query.filter(Follow.follower_id==id).delete()
      db.session.delete(user)
      db.session.commit()
      return redirect("/")
    else:
      return "Wrong Password. Go back!"
  else:
    return render_template('delete_user.html', id=id, password=password)

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)