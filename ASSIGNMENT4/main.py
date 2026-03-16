from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Shopping Cart System", version="1.0")

# ==================== DATA MODELS ====================

class CartItem(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: int
    subtotal: int

class Cart(BaseModel):
    items: List[dict]
    item_count: int
    grand_total: int

class CheckoutRequest(BaseModel):
    customer_name: str
    delivery_address: str

class Order(BaseModel):
    order_id: int
    customer_name: str
    product: str
    product_id: int
    quantity: int
    unit_price: int
    total_price: int
    delivery_address: str

# ==================== PRODUCT DATABASE ====================

products = {
    1: {"id": 1, "name": "Wireless Mouse", "price": 499, "in_stock": True},
    2: {"id": 2, "name": "Notebook", "price": 99, "in_stock": True},
    3: {"id": 3, "name": "USB Hub", "price": 299, "in_stock": False},
    4: {"id": 4, "name": "Pen Set", "price": 49, "in_stock": True},
}

# ==================== GLOBAL STATE ====================

cart = []
orders = []
order_counter = 0

# ==================== HELPER FUNCTIONS ====================

def get_product(product_id: int):
    """Get product by ID or raise 404"""
    if product_id not in products:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")
    return products[product_id]

def calculate_total(product: dict, quantity: int) -> int:
    """Calculate subtotal for a product"""
    return product["price"] * quantity

# ==================== CART ENDPOINTS ====================

@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):
    """Add item to cart or update quantity if already in cart"""
    global cart
    
    # Get product (raises 404 if not found)
    product = get_product(product_id)
    
    # Check if product is in stock
    if not product["in_stock"]:
        raise HTTPException(
            status_code=400,
            detail=f"{product['name']} is out of stock"
        )
    
    # Check if product already in cart
    for item in cart:
        if item["product_id"] == product_id:
            # Product exists - update quantity
            item["quantity"] += quantity
            item["subtotal"] = calculate_total(product, item["quantity"])
            return {
                "message": "Cart updated",
                "cart_item": item
            }
    
    # Product not in cart - add new item
    new_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": calculate_total(product, quantity)
    }
    cart.append(new_item)
    
    return {
        "message": "Added to cart",
        "cart_item": new_item
    }

@app.get("/cart")
def view_cart():
    """View current cart"""
    if not cart:
        return {"message": "Cart is empty"}
    
    grand_total = sum(item["subtotal"] for item in cart)
    
    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }

@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):
    """Remove item from cart"""
    global cart
    
    # Find and remove the item
    for i, item in enumerate(cart):
        if item["product_id"] == product_id:
            removed_item = cart.pop(i)
            return {
                "message": f"Removed {removed_item['product_name']} from cart",
                "removed_item": removed_item
            }
    
    raise HTTPException(
        status_code=404,
        detail=f"Product with id {product_id} not found in cart"
    )

@app.post("/cart/checkout")
def checkout(checkout_data: CheckoutRequest):
    """Checkout - create orders for all cart items"""
    global cart, orders, order_counter
    
    # Check if cart is empty
    if not cart:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty — add items first"
        )
    
    # Create order for each cart item
    orders_placed = []
    grand_total = 0
    
    for item in cart:
        order_counter += 1
        order = {
            "order_id": order_counter,
            "customer_name": checkout_data.customer_name,
            "product": item["product_name"],
            "product_id": item["product_id"],
            "quantity": item["quantity"],
            "unit_price": item["unit_price"],
            "total_price": item["subtotal"],
            "delivery_address": checkout_data.delivery_address
        }
        orders.append(order)
        orders_placed.append(order)
        grand_total += item["subtotal"]
    
    # Clear cart after checkout
    cart = []
    
    return {
        "message": "Checkout successful",
        "customer_name": checkout_data.customer_name,
        "delivery_address": checkout_data.delivery_address,
        "orders_placed": orders_placed,
        "grand_total": grand_total
    }

@app.get("/orders")
def get_orders():
    """Get all orders"""
    return {
        "orders": orders,
        "total_orders": len(orders)
    }

# ==================== ROOT ENDPOINT ====================

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Shopping Cart System",
        "endpoints": {
            "POST /cart/add": "Add item to cart (query params: product_id, quantity)",
            "GET /cart": "View cart",
            "DELETE /cart/{product_id}": "Remove item from cart",
            "POST /cart/checkout": "Checkout (body: customer_name, delivery_address)",
            "GET /orders": "View all orders"
        },
        "products": products
    }
