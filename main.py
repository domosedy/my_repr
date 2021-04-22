from flask import *
from fl_wtf import *
import os
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
#from data import db_session
from data.base import Base
from sqlalchemy import create_engine
from data.users import User
from data.posts import Post
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'chupakabra'

file = "db/blogs.sqlite"
engine = create_engine(f'sqlite:///{file.strip()}', echo=True)
Session = sessionmaker(bind=engine)


def main():
    Base.metadata.create_all(engine)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


@app.route('/')
def mai():
    global Session
    db_sess = Session()
    news = db_sess.query(Post).order_by(-Post.likes)
    l2 = 0
    for i in news:
        l2 += 1
    if not current_user.is_authenticated:
        return render_template('index.html', news=news, l2=l2)

    posts = []
    xl = db_sess.query(User).filter(User.id == current_user.id).first()
    lp = []
    lp1 = []
    for i in news:
        if i in current_user.liked:
            lp.append('убрать лайк')
        else:
            lp.append('лайкнуть')
    for user in xl.followed:
        xd = user.news
        for d in xd:
            posts.append(d)
    posts.sort()
    for i in posts:
        if i in current_user.liked:
            lp1.append('убрать лайк')
        else:
            lp1.append('лайкнуть')

    l2 = len(lp1)
    l1 = len(lp)
    lp = lp[::-1]
    lp1 = lp1[::-1]
    print(lp)
    return render_template('index.html', news=news, post=posts, lp=lp, lp1=lp1, l1=l1, l2=l2)


@app.route('/home')
@app.route('/profile')
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    liked = current_user.liked
    my_news = current_user.news
    lp = []
    for i in my_news:
        if i in liked:
            lp.append('убрать лайк')
        else:
            lp.append('лайкнуть')
    return render_template('profile.html', news=my_news, liked=liked, lp=lp)


@app.route('/profile/<int:id>')
def profil(id):
    global Session
    db_sess = Session()
    user = db_sess.query(User).filter(User.id == id).first()
    xl = 0
    if current_user.is_authenticated and user in current_user.followed:
        xl = 1
    df = 0
    for i in user.news:
        df += 1
    lp = ['лайкнуть' for i in range(df)]
    if not current_user.is_authenticated:
        return render_template('profile_of_people.html', user=user, news=user.news, df=df, xl=xl, lp=lp)
    k = 0
    for i in user.news:
        if i in current_user.liked:
            lp[k] = 'убрать лайк'
        k += 1
    return render_template('profile_of_people.html', user=user, news=user.news, df=df, xl=xl, lp=lp)


@app.route('/like/<int:id>')
def like(id):
    global Session
    db_sess = Session()
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    post = db_sess.query(Post).filter(Post.id == id).first()
    xd = db_sess.query(User).filter(User.id == current_user.id).first()
    xd.like(post)
    db_sess.commit()
    return '<script>document.location.href = document.referrer</script>'


@app.route('/follow/<int:id>')
def follow(id):
    global Session
    db_sess = Session()
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    usr = db_sess.query(User).filter(User.id == id).first()
    xd = db_sess.query(User).filter(User.id == current_user.id).first()
    xd.follow(usr)
    db_sess.commit()
    return '<script>document.location.href = document.referrer</script>'


@app.route('/make_article', methods=["GET", "POST"])
def artcile():
    global Session
    db_sess = Session()
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    form = NewsForm()
    if form.validate_on_submit():
        post = Post()
        post.name = form.title.data
        post.text = form.content.data
        date = datetime.now().date()
        year = date.year
        mon = date.month
        day = date.day
        time = datetime.now().time()
        mi = time.minute
        hour = time.hour
        sec = int(time.second)
        post.date = datetime(year, mon, day, hour, mi, sec)
        xd = db_sess.query(User).filter(User.id == current_user.id).first()
        xd.news.append(post)
        if post in xd.liked:
            xd.liked.remove(post)
        db_sess.add(post)
        db_sess.commit()
        return redirect(url_for('profile'))
    return render_template('news.html', form=form)


@app.route('/change_article/<int:id>', methods=["GET", "POST"])
def change_article(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    global Session
    db_sess = Session()
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(Posts).filter(and_(Posts.id == id,
                                                Posts.user == current_user)).first()
        if news:
            form.title.data = news.name
            form.content.data = news.text
        else:
            abort(404)

    if form.validate_on_submit():
        post = db_sess.query(Post).filter(
            and_(Post.id == id, Post.user == current_user)).first()
        if not post:
            abort(404)
        else:
            post.name = form.title.data
            post.text = form.content.data
            db_ses.commit()
            return '<script>document.location.href = document.referrer</script>'
    return render_template('change.html', form=form)


@app.route('/delete_news/<int:id>', methods=["GET", "POST"])
def delete(id):
    global Session
    db_sess = Session()

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    post = db_sess.query(Post).filter(
        and_(Post.id == id, Post.user == current_user)).first()
    if not post:
        abort(404)
    else:
        db_sess.delete(post)
        db_sess.commit()
        return '<script>document.location.href = document.referrer</script>'


@login_manager.user_loader
def load_user(user_id):
    db_sess = Session()
    us1 = db_sess.query(User).filter(User.id == user_id).first()
    if not us1:
        return None
    else:
        return us1


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/change_information', methods=["GET", "POST"])
def change():
    global Session
    db_sess = Session()
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    form = ChangeForm()
    if form.validate_on_submit():
        us = db_sess.query(User).filter(
            User.nickname == form.title.data).first()
        if us:
            return render_template('change.html', form=form, message='1222')
        current_user.nickname = form.title.data
        current_user.about = form.content.data
        db_sess.commit()
        return '<script>document.location.href = document.referrer</script>'
    return render_template('change.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    global Session
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = Session()
        user = db_sess.query(User).filter(
            User.nickname == form.email.data).first()
        if not user:
            return render_template('login.html', form=form, message='Такого пользователя нет')
        if not user.check_password(form.password.data):
            return render_template('login.html', form=form, message='Неверный пароль')
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('profile'))
    return render_template('login.html', form=form)


@app.route('/sign_up', methods=["GET", "POST"])
def sign_up():
    global Session
    db_sess = Session()
    form = RegisterForm()
    if form.validate_on_submit():
        user = db_sess.query(User).filter(
            User.nickname == form.username.data).first()
        if user:
            return render_template('sign.html', form=form, message='Пользователь с таким ником уже существует')

        if form.password.data != form.password_again.data:
            return render_template('sign.html', form=form, message='Пароли не совпадают')
        us = User()
        us.nickname = form.username.data
        us.about = form.about.data
        us.set_password(form.password.data)
        db_sess.add(us)
        db_sess.commit()
        return redirect('/login')
    return render_template('sign.html', form=form)


#db_sess = Session()
if __name__ == '__main__':
    main()
