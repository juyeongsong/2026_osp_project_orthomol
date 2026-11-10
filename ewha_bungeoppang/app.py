from flask import Flask, render_template, abort, request

app = Flask(__name__)
app.secret_key = "change-me"  

PER_PAGE = 4  

SELLER_ID = "ewha_bep"
ADDRESS = "서울특별시 서대문구 이화여대길52"
EMAIL = "ewhabep@ewha.ac.kr"

PRODUCTS = [
    {"id": 1, "name": "팥 붕어빵", "price": 500, "status": "판매 중", "image": "redbean.png"},
    {"id": 2, "name": "슈크림 붕어빵", "price": 500, "status": "판매 중", "image": "cream.png"},
    {"id": 3, "name": "말차 붕어빵", "price": 800, "status": "준비 중", "image": "matcha.png"},
    {"id": 4, "name": "고구마 붕어빵", "price": 800, "status": "판매 중", "image": "sweetPotato.png"},
    {"id": 5, "name": "딸기슈크림 붕어빵", "price": 1000, "status": "품절", "image": "strawberry.png"},
    {"id": 6, "name": "피자 붕어빵", "price": 1000, "status": "판매 중", "image": "pizza.png"},
]
for p in PRODUCTS:
    p.update(seller=SELLER_ID, address=ADDRESS, email=EMAIL)


@app.route("/")
def index():
    return list_products()


@app.route("/list")
def list_products():
    page = request.args.get("page", 1, type=int)
    total_pages = max(1, -(-len(PRODUCTS) // PER_PAGE))
    page = min(max(page, 1), total_pages)
    start = (page - 1) * PER_PAGE
    items = PRODUCTS[start:start + PER_PAGE]
    return render_template("list.html", items=items, page=page,
                           total_pages=total_pages)


@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if product is None:
        abort(404)
    return render_template("detail.html", p=product)


if __name__ == "__main__":
    app.run(debug=True)
