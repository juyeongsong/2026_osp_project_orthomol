import os
import uuid
import hashlib

from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    session,
    abort
)
from database import DBhandler


app = Flask(__name__)
app.config["SECRET_KEY"] = "for_test"
DB = DBhandler()


UPLOAD_DIR = os.path.join(app.root_path, "static", "images")
os.makedirs(UPLOAD_DIR, exist_ok=True)

PER_PAGE = 4
ALLOWED_IMG_EXT = {"png", "jpg", "jpeg"}


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/login_confirm", methods=["POST"])
def login_confirm():
    id = request.form["id"]
    pw = request.form["pw"]

    user = DB.get_user_by_id(id)

    pw_hash = hashlib.sha256(
        pw.encode("utf-8")
    ).hexdigest()

    if user is not None and user["pw"] == pw_hash:
        session["id"] = id
        return redirect(url_for("hello"))

    else:
        flash("Wrong ID or PW!")
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.pop("id", None)
    return redirect(url_for("hello"))


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/signup_post", methods=["POST"])
def register_user():
    data = request.form
    print(data)

    pw = request.form["pw"]

    pw_hash = hashlib.sha256(
        pw.encode("utf-8")
    ).hexdigest()

    if DB.insert_user(data, pw_hash):
        return render_template("login.html")

    else:
        return render_template(
            "signup.html",
            error="User ID already exists!"
        )


@app.route("/list")
def list_products():
    page = request.args.get("page", 1, type=int)

    data = DB.get_items() or {}
    items = sorted(data.items(), key=lambda kv: (int(kv[1]["price"]), kv[0])) 

    total_pages = max(
        1,
        -(-len(items) // PER_PAGE)
    )

    page = min(
        max(page, 1),
        total_pages
    )

    start = (page - 1) * PER_PAGE
    items = items[start:start + PER_PAGE]

    return render_template(
        "list.html",
        items=items,
        page=page,
        total_pages=total_pages
    )

@app.route("/view_detail/<name>")
def view_item_detail(name):
    data = DB.get_item_byname(name)
    if not data:
        abort(404)
    return render_template("detail.html", name=name, p=data)

@app.route("/review")
def view_review():
    return render_template("review.html")


@app.route("/reg_items")
def reg_item():
    return render_template("reg_items.html")


# ---------- 후기 작성 (Team Practice 1) ----------
@app.route("/reg_reviews")
def reg_review():
    # 상품 상세의 "후기 작성" 버튼에서 ?name=상품명 으로 들어오면 상품명이 채워짐
    return render_template(
        "reg_reviews.html",
        product=request.args.get("name", ""),
        user_id=session.get("id")
    )


@app.route("/submit_review_post", methods=["POST"])
def reg_review_submit_post():
    data = request.form
    image_file = request.files.get("file_input")

    filename = ""
    if image_file and image_file.filename:
        ext = image_file.filename.rsplit(".", 1)[-1].lower() if "." in image_file.filename else ""
        if ext not in ALLOWED_IMG_EXT:
            flash("png, jpg 사진만 올릴 수 있어요.")
            return redirect(url_for("reg_review", name=data.get("product", "")))

        # 서버(static/images)에 사진 저장, DB에는 파일 이름만 저장
        filename = f"review_{uuid.uuid4().hex[:12]}.{ext}"
        image_file.save(os.path.join(UPLOAD_DIR, filename))

    DB.insert_review(data, filename)

    return redirect(url_for("view_review"))


@app.route("/submit_item_post", methods=["POST"])
def reg_item_submit_post():
    image_file = request.files["file_input"]

    image_file.save(
        os.path.join(
            UPLOAD_DIR,
            image_file.filename
        )
    )

    data = request.form

    DB.insert_item(
        data["name"],
        data,
        image_file.filename
    )

    return render_template(
        "result.html",
        data=data,
        img_path="images/" + image_file.filename
    )


if __name__ == "__main__":
    app.run(debug=True)
