#!/usr/bin/env python3

import sqlite3
import json
import os
from datetime import datetime, timedelta
import random

def create_shopify_style_ecommerce():
    """Create a Shopify-style e-commerce database"""
    db_path = "samples/shopify_style_ecommerce.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.executescript("""
    -- Shopify-style schema
    CREATE TABLE shops (
        shop_id INTEGER PRIMARY KEY AUTOINCREMENT,
        shop_name TEXT NOT NULL,
        shop_domain TEXT UNIQUE NOT NULL,
        owner_email TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        shop_id INTEGER NOT NULL,
        email TEXT NOT NULL,
        first_name TEXT,
        last_name TEXT,
        phone TEXT,
        total_spent DECIMAL(10,2) DEFAULT 0.00,
        orders_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (shop_id) REFERENCES shops(shop_id)
    );
    
    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        shop_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        handle TEXT NOT NULL,
        body_html TEXT,
        vendor TEXT,
        product_type TEXT,
        published BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (shop_id) REFERENCES shops(shop_id)
    );
    
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        shop_id INTEGER NOT NULL,
        order_number TEXT NOT NULL,
        customer_id INTEGER,
        email TEXT,
        financial_status TEXT DEFAULT 'pending',
        subtotal_price DECIMAL(10,2) NOT NULL,
        total_price DECIMAL(10,2) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (shop_id) REFERENCES shops(shop_id),
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );
    
    -- Insert sample data
    INSERT INTO shops (shop_name, shop_domain, owner_email) VALUES 
        ('Demo Store', 'demo.myshopify.com', 'owner@demo.com');
    
    INSERT INTO customers (shop_id, email, first_name, last_name, total_spent, orders_count) VALUES
        (1, 'john@example.com', 'John', 'Doe', 150.00, 2),
        (1, 'jane@example.com', 'Jane', 'Smith', 75.50, 1);
    
    INSERT INTO products (shop_id, title, handle, vendor, product_type) VALUES
        (1, 'T-Shirt', 't-shirt', 'Fashion Co', 'Apparel'),
        (1, 'Jeans', 'jeans', 'Fashion Co', 'Apparel');
    
    INSERT INTO orders (shop_id, order_number, customer_id, email, financial_status, subtotal_price, total_price) VALUES
        (1, 'ORD-001', 1, 'john@example.com', 'paid', 50.00, 55.00),
        (1, 'ORD-002', 2, 'jane@example.com', 'paid', 75.50, 82.50);
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ Shopify-style database created: {db_path}")
    return db_path

def create_magento_style_ecommerce():
    """Create a Magento-style e-commerce database"""
    db_path = "samples/magento_style_ecommerce.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.executescript("""
    -- Magento-style schema
    CREATE TABLE customer_entity (
        entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        firstname TEXT,
        lastname TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE catalog_product_entity (
        entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE sales_order (
        entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        increment_id TEXT,
        status TEXT,
        grand_total DECIMAL(12,4),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customer_entity(entity_id)
    );
    
    -- Insert sample data
    INSERT INTO customer_entity (email, firstname, lastname) VALUES
        ('alice@example.com', 'Alice', 'Johnson'),
        ('bob@example.com', 'Bob', 'Smith');
    
    INSERT INTO catalog_product_entity (sku) VALUES
        ('PROD-001'),
        ('PROD-002');
    
    INSERT INTO sales_order (customer_id, increment_id, status, grand_total) VALUES
        (1, '100000001', 'complete', 99.99),
        (2, '100000002', 'processing', 149.99);
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ Magento-style database created: {db_path}")
    return db_path

def create_woocommerce_style_ecommerce():
    """Create a WooCommerce-style e-commerce database"""
    db_path = "samples/woocommerce_style_ecommerce.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.executescript("""
    -- WooCommerce/WordPress-style schema
    CREATE TABLE wp_users (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        user_login TEXT NOT NULL UNIQUE,
        user_email TEXT NOT NULL,
        display_name TEXT NOT NULL,
        user_registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE wp_posts (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        post_author INTEGER NOT NULL,
        post_title TEXT,
        post_content TEXT,
        post_status TEXT DEFAULT 'publish',
        post_type TEXT DEFAULT 'post',
        post_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (post_author) REFERENCES wp_users(ID)
    );
    
    CREATE TABLE wp_wc_customer_lookup (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        email TEXT,
        orders_count INTEGER DEFAULT 0,
        total_spent DECIMAL(26,8) DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES wp_users(ID)
    );
    
    -- Insert sample data
    INSERT INTO wp_users (user_login, user_email, display_name) VALUES
        ('customer1', 'customer1@example.com', 'Customer One'),
        ('customer2', 'customer2@example.com', 'Customer Two');
    
    INSERT INTO wp_posts (post_author, post_title, post_content, post_type) VALUES
        (1, 'Sample Product', 'Product description here', 'product'),
        (1, 'Another Product', 'Another product description', 'product');
    
    INSERT INTO wp_wc_customer_lookup (user_id, email, orders_count, total_spent) VALUES
        (1, 'customer1@example.com', 2, 199.99),
        (2, 'customer2@example.com', 1, 99.99);
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ WooCommerce-style database created: {db_path}")
    return db_path

def create_all_ecommerce_variants():
    """Create all e-commerce database variants"""
    print("🏪 Creating Multiple E-commerce Database Implementations")
    print("=" * 60)
    
    databases = []
    
    print("📦 Creating Shopify-style database...")
    shopify_db = create_shopify_style_ecommerce()
    databases.append(('shopify_style', shopify_db))
    
    print("🛍️ Creating Magento-style database...")
    magento_db = create_magento_style_ecommerce()
    databases.append(('magento_style', magento_db))
    
    print("🌐 Creating WooCommerce-style database...")
    woocommerce_db = create_woocommerce_style_ecommerce()
    databases.append(('woocommerce_style', woocommerce_db))
    
    print(f"\n✅ Created {len(databases)} e-commerce database variants")
    return databases

if __name__ == "__main__":
    create_all_ecommerce_variants()
