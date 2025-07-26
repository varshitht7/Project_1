import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from data_loader import load_data
import re

# --- Initialize App and Load Data ---
app = Flask(__name__)
CORS(app)
ecommerce_data = load_data()

# --- Chatbot Logic Functions ---

def get_top_products():
    """Calculates the top 5 most sold products."""
    order_items_df = ecommerce_data['order_items']
    products_df = ecommerce_data['products']
    distribution_items_df = ecommerce_data['distribution_items']
    inventory_items_df = ecommerce_data['inventory_items']
    orders_df = ecommerce_data['orders']
    users_df = users['users']
    
    
    # Count sales per product
    product_sales = order_items_df.groupby('product_id').size().reset_index(name='sales_count')
    
    # Merge with products to get names
    merged_df = pd.merge(product_sales, products_df, left_on='product_id', right_on='id')
    
    # Sort and get top 5
    top_5 = merged_df.sort_values(by='sales_count', ascending=False).head(5)
    
    response = "The top 5 most sold products are:\n"
    for index, row in top_5.iterrows():
        response += f"- {row['name']} (Sold {row['sales_count']} times)\n"
    return response

def get_order_status(order_id):
    """Finds the status of a specific order."""
    orders_df = ecommerce_data['orders']
    
    # Find the order by its ID
    order = orders_df[orders_df['order_id'] == int(order_id)]
    
    if not order.empty:
        status = order.iloc[0]['status']
        return f"The status of order ID {order_id} is: {status}."
    else:
        return f"Sorry, I couldn't find an order with ID {order_id}."

def get_stock_level(product_name):
    """Checks the inventory for a specific product."""
    products_df = ecommerce_data['products']
    inventory_df = ecommerce_data['inventory_items']
    
    # Find product ID by name (case-insensitive)
    product = products_df[products_df['name'].str.lower() == product_name.lower()]
    
    if not product.empty:
        product_id = product.iloc[0]['id']
        # Sum stock from all inventory locations for that product
        total_stock = inventory_df[inventory_df['product_id'] == product_id]['quantity'].sum()
        return f"We have {total_stock} units of '{product.iloc[0]['name']}' in stock."
    else:
        return f"Sorry, I couldn't find a product named '{product_name}'."

# --- Main API Endpoints ---

@app.route('/')
def home():
    return "Welcome to the E-Commerce Chatbot Backend! 🚀"

@app.route('/chat', methods=['POST'])
def chat():
    """Main endpoint to process user messages."""
    if not ecommerce_data:
        return jsonify({"error": "Dataset not loaded."}), 500

    message = request.json.get('message', '').lower()
    response = "Sorry, I didn't understand that. You can ask about 'top 5 products', 'order status', or 'stock levels'."

    # Intent matching using keywords
    if "top" in message and "products" in message:
        response = get_top_products()
        
    elif "status of order" in message:
        # Extract order ID using regex
        match = re.search(r'\d+', message)
        if match:
            order_id = match.group(0)
            response = get_order_status(order_id)
        else:
            response = "Please provide an order ID to check the status."

    elif "how many" in message and "left" in message:
        # Extract product name (simple approach)
        # Assumes format "How many [Product Name] are left"
        try:
            product_name = message.split("how many ")[1].split(" are left")[0].strip()
            response = get_stock_level(product_name)
        except IndexError:
            response = "Please ask in the format: 'How many [Product Name] are left?'"

    return jsonify({"response": response})


if __name__ == '__main__':
    app.run(debug=True)
