import requests
import datetime
from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user, login_required

from blog import db, app, bcrypt, mail
from blog.forms import LoginForm, PostForm, RegistrationForm, ContactForm
from blog.models import Post, User
from blog.utils import save_picture, title_slugifier

from flask_mail import Message


@app.route("/")
def homepage():
    page_number = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(page_number, 5, True)

    if posts.has_next:
        next_page = url_for("homepage", page=posts.next_num)
    else:
        next_page = None

    if posts.has_prev:
        previous_page = url_for("homepage", page=posts.prev_num)
    else:
        previous_page = None

    return render_template(
        "homepage.html",
        posts=posts,
        current_page=page_number,
        next_page=next_page,
        previous_page=previous_page,
    )


@app.route("/posts/<string:post_slug>")
def post_detail(post_slug):
    post_instance = Post.query.filter_by(slug=post_slug).first_or_404()
    return render_template("post_detail.html", post=post_instance)


@app.route("/create-post", methods=["GET", "POST"])
@login_required
def post_create():
    form = PostForm()
    if form.validate_on_submit():
        slug = title_slugifier(form.title.data)
        new_post = Post(
            title=form.title.data,
            body=form.body.data,
            slug=slug,
            description=form.description.data,
            author=current_user,
        )
        if form.image.data:
            try:
                image = save_picture(form.image.data)
                new_post.image = image
            except Exception:
                db.session.add(new_post)
                db.session.commit()
                flash(
                    "C'è stato un problema con l'upload dell'immagine. Cambia immagine e riprova."
                )
                return redirect(url_for("post_update", post_id=new_post.id))
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("post_detail", post_slug=slug))
    return render_template("post_editor.html", form=form)


@app.route("/posts/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def post_update(post_id):
    post_instance = Post.query.get_or_404(post_id)
    if post_instance.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post_instance.title = form.title.data
        post_instance.description = form.description.data
        post_instance.body = form.body.data

        if form.image.data:
            try:
                image = save_picture(form.image.data)
                post_instance.image = image
            except Exception:
                db.session.commit()
                flash(
                    "C'è stato un problema con l'upload dell'immagine. Cambia immagine e riprova."
                )
                return redirect(url_for("post_update", post_id=post_instance.id))

        db.session.commit()
        return redirect(url_for("post_detail", post_slug=post_instance.slug))
    elif request.method == "GET":
        form.title.data = post_instance.title
        form.description.data = post_instance.description
        form.body.data = post_instance.body
    post_image = post_instance.image or None
    return render_template("post_editor.html", form=form, post_image=post_image)


@app.route("/posts/<int:post_id>/delete", methods=["POST"])
@login_required
def post_delete(post_id):
    post_instance = Post.query.get_or_404(post_id)
    if post_instance.author != current_user:
        abort(403)
        db.session.delete(post_instance)
    db.session.commit()
    return redirect(url_for("homepage"))


@app.route("/about")
def about():
    return render_template("about_page.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("homepage"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not bcrypt.check_password_hash(
            user.password, form.password.data
        ):
            flash("username e password non combaciano!")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for("homepage"))
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("homepage"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("homepage"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            username=form.username.data, email=form.email.data, password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created! You are now able to log in", "success")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/tempe", methods=["POST"])
def tempe():
    weather = []
    if request.method == "POST":
        cityname = request.form["city"]
        if cityname == "":
            flash("Per favore inserire il nome di una città", "danger")
            return redirect(url_for("homepage"))
        else:
            url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=271d1234d3f497eed5b1d80a07b3fcd1"
        json_object = requests.get(url.format(cityname)).json()
        weather = {
            "city": cityname,
            "temperature": json_object["main"]["temp"],
            "pressure": json_object["main"]["pressure"],
            "humidity": json_object["main"]["humidity"],
            "speed": json_object["wind"]["speed"],
            "description": json_object["weather"][0]["description"],
            "icon": json_object["weather"][0]["icon"],
            "lon": json_object["coord"]["lon"],
            "lat": json_object["coord"]["lat"],
            "country": json_object["sys"]["country"],
            "sunrise": datetime.datetime.fromtimestamp(
                json_object["sys"]["sunrise"]
            ).strftime("%H:%M:%S"),
            "sunset": datetime.datetime.fromtimestamp(
                json_object["sys"]["sunset"]
            ).strftime("%H:%M:%S"),
        }
    return render_template("tempe.html", weather_data=weather)


@app.route("/contact", methods=["POST", "GET"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        print("-------------------------")
        print(request.form["name"])
        print(request.form["email"])
        print(request.form["subject"])
        print(request.form["message"])
        print("-------------------------")
        send_message(request.form)
        form.name.data = ""
        return redirect("/success")

    return render_template("contact_page.html", form=form)


@app.route("/success")
def success():
    flash("Your request has been sent!", "success")
    return redirect(url_for("homepage"))


def send_message(message):
    print(message.get("name"))
    msg = Message(
        message.get("subject"),
        sender=message.get("email"),
        recipients=["aoxoeoxoa@gmail.com"],
        body=message.get("email") + "  Ha richiesto \n\n" + message.get("message"),
    )
    mail.send(msg)
