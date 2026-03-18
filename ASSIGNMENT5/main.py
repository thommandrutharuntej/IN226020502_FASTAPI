from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

app = FastAPI(title="FastAPI Assignment 5 - Day 6")

# Add CORS middleware to handle browser requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================
# SAMPLE DATA
# ================================

products = [
    {"product_id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics"},
    {"product_id": 2, "name": "USB Hub", "price": 799, "category": "Electronics"},
    {"product_id": 3, "name": "Notebook", "price": 99, "category": "Stationery"},
    {"product_id": 4, "name": "Pen Set", "price": 49, "category": "Stationery"},
]

orders = []  # Will store orders placed by users
order_counter = 0  # To auto-increment order IDs


# ================================
# Q1 - SEARCH ENDPOINT (Existing - No new code needed)
# ================================
@app.get("/products/search")
def search_products(keyword: str = Query(..., description="Search keyword")):
    """
    Search products by keyword (case-insensitive)
    Returns matching products or friendly message if none found
    """
    results = [
        p for p in products
        if keyword.lower() in p['name'].lower()
    ]
    
    if not results:
        return {"message": f"No products found for: {keyword}"}
    
    return {
        "keyword": keyword,
        "total_found": len(results),
        "products": results
    }


# ================================
# Q2 - SORT ENDPOINT (Existing - No new code needed)
# ================================
@app.get("/products/sort")
def sort_products(
    sort_by: str = Query("price", description="Sort by 'price' or 'name'"),
    order: str = Query("asc", description="'asc' or 'desc'")
):
    """
    Sort products by price or name in ascending/descending order
    """
    # Validate sort_by parameter
    if sort_by not in ["price", "name"]:
        return {"error": f"sort_by must be 'price' or 'name', got '{sort_by}'"}
    
    # Validate order parameter
    if order not in ["asc", "desc"]:
        return {"error": f"order must be 'asc' or 'desc', got '{order}'"}
    
    # Sort products
    reverse = (order == "desc")
    sorted_products = sorted(products, key=lambda p: p[sort_by], reverse=reverse)
    
    return {
        "sort_by": sort_by,
        "order": order,
        "total": len(sorted_products),
        "products": sorted_products
    }


# ================================
# Q3 - PAGINATION ENDPOINT (Existing - No new code needed)
# ================================
@app.get("/products/page")
def paginate_products(
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    limit: int = Query(2, ge=1, le=20, description="Items per page")
):
    """
    Paginate through products list
    """
    total = len(products)
    
    # Calculate total pages using ceiling division
    total_pages = -(- total // limit)  # Ceiling division trick
    
    # Calculate start index
    start = (page - 1) * limit
    
    # Get products for this page
    paged_products = products[start : start + limit]
    
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "products": paged_products
    }


# ================================
# Q5 - SORT PRODUCTS BY CATEGORY THEN PRICE
# ⭐ MUST BE BEFORE /products/{product_id} to avoid route conflict
# ================================
@app.get("/products/sort-by-category")
def sort_by_category():
    """
    Sort products first by category alphabetically (A→Z),
    then by price ascending within each category
    """
    # sorted() with tuple key: sorts by category first, then by price
    sorted_products = sorted(products, key=lambda p: (p['category'], p['price']))
    
    return {
        "products": sorted_products,
        "total": len(sorted_products)
    }


# ================================
# Q6 - ADVANCED BROWSE: SEARCH + SORT + PAGINATE IN ONE
# ⭐ MUST BE BEFORE /products/{product_id} to avoid route conflict
# ================================
@app.get("/products/browse")
def browse_products(
    keyword: Optional[str] = None,
    sort_by: str = Query("price", description="Sort by 'price' or 'name'"),
    order: str = Query("asc", description="'asc' or 'desc'"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(4, ge=1, le=20, description="Items per page")
):
    """
    All-in-one endpoint: search → sort → paginate
    Everything is optional except it applies in order
    """
    # Step 1: SEARCH - Filter by keyword if provided
    result = products
    if keyword:
        result = [
            p for p in result
            if keyword.lower() in p['name'].lower()
        ]
    
    # Step 2: SORT - Sort by specified field
    if sort_by in ['price', 'name']:
        result = sorted(result, key=lambda p: p[sort_by], reverse=(order == 'desc'))
    else:
        return {"error": f"sort_by must be 'price' or 'name', got '{sort_by}'"}
    
    # Step 3: PAGINATE - Get the page slice
    total_found = len(result)
    total_pages = -(- total_found // limit)  # Ceiling division
    start = (page - 1) * limit
    paged_products = result[start : start + limit]
    
    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total_found,
        "total_pages": total_pages,
        "products": paged_products
    }


# ================================
# EXISTING ENDPOINT - Get single product by ID
# ⭐ MUST BE AFTER ALL specific /products/* routes
# ================================
@app.get("/products/{product_id}")
def get_product(product_id: int):
    """Get a single product by ID"""
    for p in products:
        if p["product_id"] == product_id:
            return p
    return {"error": f"Product with ID {product_id} not found"}


# ================================
# Q4 - SEARCH ORDERS BY CUSTOMER NAME
# ================================
@app.get("/orders/search")
def search_orders(customer_name: str = Query(..., description="Customer name to search")):
    """
    Search orders by customer name (case-insensitive)
    Returns all matching orders or friendly message if none found
    """
    results = [
        o for o in orders
        if customer_name.lower() in o['customer_name'].lower()
    ]
    
    if not results:
        return {"message": f"No orders found for: {customer_name}"}
    
    return {
        "customer_name": customer_name,
        "total_found": len(results),
        "orders": results
    }


# ================================
# BONUS - PAGINATE ORDERS
# ================================
@app.get("/orders/page")
def paginate_orders(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(3, ge=1, le=20, description="Items per page")
):
    """
    Paginate through orders list
    """
    total = len(orders)
    total_pages = -(- total // limit)  # Ceiling division
    start = (page - 1) * limit
    
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "orders": orders[start : start + limit]
    }


# ================================
# CREATE ORDER - POST ENDPOINT
# Helper endpoint to create test orders
# ================================
@app.post("/orders")
def create_order(customer_name: str = Query(...), product_id: int = Query(...)):
    """
    Create a new order
    Used to generate test data for Q4 and BONUS questions
    """
    global order_counter
    
    # Find product
    product = None
    for p in products:
        if p["product_id"] == product_id:
            product = p
            break
    
    if not product:
        return {"error": f"Product ID {product_id} not found"}
    
    order_counter += 1
    new_order = {
        "order_id": order_counter,
        "customer_name": customer_name,
        "product_id": product_id,
        "product_name": product["name"],
        "price": product["price"],
        "category": product["category"]
    }
    
    orders.append(new_order)
    return {
        "message": "Order created successfully",
        "order": new_order
    }


# ================================
# ROOT ENDPOINT
# ================================
@app.get("/")
def root():
    return {
        "message": "FastAPI Assignment 5 - Day 6",
        "assignment": "Search, Sort, and Pagination",
        "docs": "Visit /docs for Swagger UI"
    }
