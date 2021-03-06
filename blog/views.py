from flask import render_template, request, redirect, url_for, flash
from werkzeug.security import check_password_hash
from .database import User

from . import app
from .database import session, Entry
from flask_login import login_required, current_user,login_user, logout_user, user_logged_in

#Shows 10 entries on default otherwise based on select tag in entries.html
#No greater than 50 entries at a time
@app.route("/")
@app.route("/page/<int:page>/?limit=20")

def entries(page=1):
    #Zero-indexed page
    try: 
        PAGINATE_BY=int(request.args.get('limit'))
        
        if PAGINATE_BY > 50:
            PAGINATE_BY = 10
            
        
        page_index = page-1
        
        count = session.query(Entry).count()
        
        start = page_index*PAGINATE_BY
        end=start + PAGINATE_BY
        
        total_pages = (count-1) // PAGINATE_BY + 1
        has_next = page_index < total_pages-1
        has_prev = page_index > 0
        
        entries = session.query(Entry)
        entries = entries.order_by(Entry.datetime.desc())
        entries = entries[start:end]
    except:
        PAGINATE_BY=10
        page_index = page-1
        
        count = session.query(Entry).count()
        
        start = page_index*PAGINATE_BY
        end=start + PAGINATE_BY
        
        total_pages = (count-1) // PAGINATE_BY + 1
        has_next = page_index < total_pages-1
        has_prev = page_index > 0
        
        entries = session.query(Entry)
        entries = entries.order_by(Entry.datetime.desc())
        entries = entries[start:end]
    return render_template("entries.html",
    paginate_by=PAGINATE_BY,
    entries=entries,
    has_next=has_next,
    has_prev=has_prev,
    page=page,
    total_pages=total_pages,
    )


@app.route("/entry/add", methods=["GET"])
@login_required
def add_entry_get():
    return render_template("add_entry.html")
    
@app.route("/entry/add", methods=["POST"])
@login_required
def add_entry_post():
    entry=Entry(
        title=request.form["title"],
        content=request.form["content"],
        author=current_user
    )
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))


@app.route("/entry/<id>")
def view_entry(id):
    entry=session.query(Entry).filter(Entry.id==id).one()
    return render_template("view_entry.html", entry=entry)
    
@app.route("/entry/<id>/edit", methods=["GET"])
def edit_entry_get(id):
    entry=session.query(Entry).filter(Entry.id==id).one()
    if  current_user.is_anonymous or entry.author.email != current_user.email:
        flash("You do not have authorization to edit this entry.", "danger")
        return redirect('/')
    return render_template("edit_entry.html",entry=entry)
    
@app.route("/entry/<id>/edit", methods=["POST"])
def edit_entry_put(id, title=None, content=None):
        entry=session.query(Entry).filter(Entry.id==id).one()
        entry.title=request.form['title'],
        entry.content=request.form["content"]
        session.add(entry)
        session.commit()
        return redirect(url_for("entries"))
        
#deletes entry
@app.route("/entry/<id>/delete")
def delete_entry(id):
    entry=session.query(Entry).filter(Entry.id==id).one()
    session.delete(entry)
    session.commit()
    return redirect(url_for("entries"))
    
@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")
    
@app.route("/login", methods=["POST"])    
def login_post():
    email=request.form["email"]
    password=request.form["password"]
    user=session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))
        
    login_user(user)
    return redirect(request.args.get('next') or url_for("entries"))
@app.route("/logout")
def logout():
    logout_user()
    return redirect('/')

    
