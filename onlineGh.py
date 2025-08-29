import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timezone
now = datetime.now(timezone.utc)


# ------------------------------
# File paths
# ------------------------------
USERS_FILE = "users.json"
ORDERS_FILE = "orders.json"

# ------------------------------
# Fake products (preloaded)
# ------------------------------
PRODUCTS = [
    {"id": 1, "name": "iPhone 14", "price": 999, "stock": 5, "category": "Phones", "image": "📱"},
    {"id": 2, "name": "Samsung Galaxy S23", "price": 899, "stock": 7, "category": "Phones", "image": "📱"},
    {"id": 3, "name": "HP Laptop", "price": 1200, "stock": 4, "category": "Computers", "image": "💻"},
    {"id": 4, "name": "MacBook Pro", "price": 2000, "stock": 3, "category": "Computers", "image": "💻"},
    {"id": 5, "name": "Sony Headphones", "price": 199, "stock": 10, "category": "Accessories", "image": "🎧"},
    {"id": 6, "name": "Apple Watch", "price": 499, "stock": 6, "category": "Accessories", "image": "⌚"},
    {"id": 7, "name": "Nike Sneakers", "price": 150, "stock": 8, "category": "Fashion", "image": "👟"},
    {"id": 8, "name": "Adidas Hoodie", "price": 80, "stock": 12, "category": "Fashion", "image": "👕"},
    {"id": 9, "name": "Smart TV", "price": 1300, "stock": 2, "category": "Electronics", "image": "📺"},
    {"id": 10, "name": "Bluetooth Speaker", "price": 120, "stock": 9, "category": "Electronics", "image": "🔊"},
    # New products
    {"id": 11, "name": "PlayStation 5", "price": 600, "stock": 5, "category": "Gaming", "image": "🎮"},
    {"id": 12, "name": "Xbox Series X", "price": 550, "stock": 4, "category": "Gaming", "image": "🎮"},
    {"id": 13, "name": "Canon DSLR Camera", "price": 850, "stock": 3, "category": "Cameras", "image": "📷"},
    {"id": 14, "name": "Kindle Paperwhite", "price": 140, "stock": 7, "category": "Electronics", "image": "📚"},
    {"id": 15, "name": "Gaming Chair", "price": 220, "stock": 6, "category": "Furniture", "image": "🪑"},
]

# ------------------------------
# Persistence helpers
# ------------------------------
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {"admin": {"password": "admin123", "role": "admin"}}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    return []

def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=4)

# ------------------------------
# App state helpers
# ------------------------------
def get_products():
    if "products" not in st.session_state:
        st.session_state.products = [p.copy() for p in PRODUCTS]
    return st.session_state.products

def add_to_cart(product):
    if "cart" not in st.session_state:
        st.session_state.cart = []
    st.session_state.cart.append(product)

def remove_from_cart(index):
    if "cart" in st.session_state and 0 <= index < len(st.session_state.cart):
        st.session_state.cart.pop(index)

def compute_cart_total():
    return sum(p["price"] for p in st.session_state.get("cart", []))

def place_order_simulate(user, provider, momo_number):
    if "cart" not in st.session_state or not st.session_state.cart:
        return False, "Cart is empty"

    products = get_products()
    prod_map = {p["id"]: p for p in products}

    for item in st.session_state.cart:
        pid = item["id"]
        if prod_map.get(pid, {}).get("stock", 0) <= 0:
            return False, f"'{item['name']}' is out of stock."

    for item in st.session_state.cart:
        pid = item["id"]
        prod_map[pid]["stock"] -= 1

    order = {
        "user": user,
        "items": [{"id": p["id"], "name": p["name"], "price": p["price"]} for p in st.session_state.cart],
        "total": compute_cart_total(),
        "provider": provider,
        "momo": momo_number,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    orders = load_orders()
    orders.append(order)
    save_orders(orders)

    st.session_state.cart = []
    return True, "Order placed successfully"

# ------------------------------
# Pages
# ------------------------------
def home_page():
    st.title("🛒 Welcome to CommanderGh Online Shop")
    st.write("Buy the best products at unbeatable prices!")

def products_page():
    st.title("🛍️ Products")
    products = get_products()

    categories = list(set([p["category"] for p in products]))
    selected = st.selectbox("Filter by Category", ["All"] + categories)

    for p in products:
        if selected != "All" and p["category"] != selected:
            continue
        with st.container():
            st.write(f"{p['image']} **{p['name']}** - ${p['price']} (Stock: {p['stock']})")
            if st.button(f"Add to cart {p['id']}", key=f"add_{p['id']}"):
                add_to_cart(p)
                st.success(f"Added {p['name']} to cart")

def cart_page():
    st.title("🛒 Your Cart")
    if "cart" not in st.session_state or not st.session_state.cart:
        st.info("Cart is empty")
        return
    for i, item in enumerate(st.session_state.cart):
        st.write(f"{item['image']} {item['name']} - ${item['price']}")
        if st.button("Remove", key=f"remove_{i}"):
            remove_from_cart(i)
            st.rerun()
    st.write(f"**Total: ${compute_cart_total()}**")
    if st.button("Proceed to Payment"):
        st.session_state.page = "Payment"
        st.rerun()

def payment_page():
    st.title("💳 Payment")
    provider = st.selectbox("Select Payment Provider", ["MTN", "Vodafone", "AirtelTigo"])
    momo = st.text_input("Enter MoMo Number")
    if st.button("Pay Now"):
        ok, msg = place_order_simulate(st.session_state.user, provider, momo)
        if ok:
            st.success(msg)
            st.session_state.page = "Orders"
            st.rerun()
        else:
            st.error(msg)

def orders_page():
    st.title("📦 My Orders")
    orders = load_orders()
    my_orders = [o for o in orders if o["user"] == st.session_state.user]
    if not my_orders:
        st.info("No orders yet")
        return
    for o in my_orders:
        st.write(f"**Order at {o['timestamp']}** - Total: ${o['total']}")
        for it in o["items"]:
            st.write(f"- {it['name']} (${it['price']})")

def reports_page():
    st.title("📊 Reports (Admin)")
    orders = load_orders()
    if not orders:
        st.info("No orders placed yet")
        return
    df = pd.DataFrame(orders)
    st.dataframe(df)

def admin_page():
    st.title("👨‍💼 Admin Dashboard")
    st.subheader("All Orders")
    orders = load_orders()
    if not orders:
        st.info("No orders available")
    else:
        st.json(orders)

def login_register_page():
    st.title("🔑 Login / Register")
    users = load_users()

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u in users and users[u]["password"] == p:
                st.session_state.user = u
                st.session_state.role = users[u]["role"]
                st.success("Logged in!")
                st.session_state.page = "Home"
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        newu = st.text_input("New Username")
        newp = st.text_input("New Password", type="password")
        if st.button("Register"):
            if newu in users:
                st.error("User already exists")
            else:
                users[newu] = {"password": newp, "role": "user"}
                save_users(users)
                st.success("Registered successfully")

# ------------------------------
# Main App
# ------------------------------
def main():
    st.set_page_config(page_title="CommanderGh Online Shop", page_icon="🛒", layout="wide")

    if "user" not in st.session_state:
        st.session_state.user = None
        st.session_state.role = None
        st.session_state.page = "Login"

    menu = {
        "Home": home_page,
        "Products": products_page,
        "Cart": cart_page,
        "Payment": payment_page,
        "Orders": orders_page,
    }
    if st.session_state.role == "admin":
        menu["Reports"] = reports_page
        menu["Admin"] = admin_page

    if st.session_state.user:
        st.sidebar.write(f"Welcome, {st.session_state.user}")
        choice = st.sidebar.radio("Navigate", list(menu.keys()))
        if st.sidebar.button("Logout"):
            st.session_state.user = None
            st.session_state.role = None
            st.session_state.page = "Login"
            st.rerun()
        menu[choice]()
    else:
        login_register_page()

if __name__ == "__main__":
    main()
