You are an expert AI assistant that generates:

1. Natural-language questions
2. Correct PostgreSQL queries that answer those questions

Use ONLY the database schema and filter parameters provided.

DATABASE SCHEMA (Tables, Columns, Descriptions):
TABLE: products
SCHEMA:
CREATE TABLE "products" (
  "product_id" int PRIMARY KEY NOT NULL,
  "product_name" varchar(255) NOT NULL,
  "product_description" text NOT NULL,
  "product_price" decimal(10, 2) NOT NULL,
  "product_created_at" timestamp NOT NULL,
  "product_updated_at" timestamp NOT NULL
);
DESCRIPTION:
The products table holds detailed records of all items available for sale in the system. Each entry represents a unique product, identified by a product_id. The product_name field specifies the title of the item, while product_description provides comprehensive information about its features or specifications. The product_price column stores the cost of the item in U.S. dollars (USD). The product_created_at field records when the product entry was first added, and product_updated_at indicates the most recent modification.

---

TABLE: reviews
SCHEMA:
CREATE TABLE "reviews" (
  "review_id" int PRIMARY KEY NOT NULL,
  "review_product_id" int NOT NULL,
  "review_user_id" int NOT NULL,
  "review_rating" int NOT NULL,
  "review_comment" text NOT NULL,
  "review_created_at" timestamp NOT NULL,
  "review_updated_at" timestamp NOT NULL
);
DESCRIPTION:
The reviews table stores customer feedback and ratings for products available in the system. Each record represents a unique review, identified by a review_id. The review_product_id column references the product being reviewed, while review_user_id identifies the customer who submitted the feedback. The review_rating field captures the user’s evaluation of the product (1-10). The review_comment column contains the written feedback or opinion provided by the user. The review_created_at field logs when the review was initially submitted, and review_updated_at records the most recent time it was modified.

---

TABLE: product_vendors
SCHEMA:
CREATE TABLE "product_vendors" (
  "product_vendor_id" int PRIMARY KEY NOT NULL,
  "product_vendor_product_id" int NOT NULL,
  "product_vendor_vendor_id" int NOT NULL
);
DESCRIPTION:
The product_vendors table defines the relationship between products and the vendors who supply them. Each record represents a unique association, identified by a product_vendor_id. The product_vendor_product_id column references the specific product offered, while the product_vendor_vendor_id column identifies the vendor responsible for supplying that product. This structure allows the system to manage multiple vendors for the same product and maintain accurate mappings between suppliers and their corresponding items.

---

TABLE: vendors
SCHEMA:
CREATE TABLE "vendors" (
  "vendor_id" int PRIMARY KEY NOT NULL,
  "vendor_name" varchar(255) NOT NULL,
  "vendor_email" varchar(255) NOT NULL,
  "vendor_created_at" timestamp NOT NULL,
  "vendor_updated_at" timestamp NOT NULL
);
DESCRIPTION:
The vendors table stores information about suppliers who provide products to the system. Each record represents a unique vendor, identified by a vendor_id. The vendor_name column specifies the name of the supplier or business entity, while vendor_email contains the contact email address for communication or order coordination. The vendor_created_at field records when the vendor entry was first added to the database, and vendor_updated_at indicates the most recent time the vendor’s information was modified. This table enables efficient management of supplier details and supports linking vendors to their associated products.

---

TABLE: tags
SCHEMA:
CREATE TABLE "tags" (
  "tag_id" int PRIMARY KEY NOT NULL,
  "tag_name" varchar(255) NOT NULL
);
DESCRIPTION:
The tags table stores short descriptive labels used to classify or group products by shared attributes or themes. Each record represents a unique tag, identified by a tag_id, with its name stored in the tag_name column. Tags are typically lightweight identifiers that allow flexible product filtering and quick categorization across multiple contexts.

---

TABLE: product_tags
SCHEMA:
CREATE TABLE "product_tags" (
  "product_tag_id" int PRIMARY KEY NOT NULL,
  "product_tag_product_id" int NOT NULL,
  "product_tag_tag_id" int NOT NULL
);
DESCRIPTION:
The product_tags table establishes the relationship between products and their associated tags. Each record represents a unique link between a specific product and a tag, identified by a product_tag_id. The product_tag_product_id column references the product being labeled, while the product_tag_tag_id column identifies the corresponding tag.

---

TABLE: categories
SCHEMA:
CREATE TABLE "categories" (
  "category_id" int PRIMARY KEY NOT NULL,
  "category_name" varchar(255) NOT NULL,
  "category_description" text NOT NULL,
  "category_created_at" timestamp NOT NULL,
  "category_updated_at" timestamp NOT NULL
);
DESCRIPTION:
The categories table organizes products into structured groups based on their type or purpose. Each record represents a distinct product category, identified by a category_id. The category_name column defines the title of the category, while category_description provides a detailed explanation of what the category includes.

---

TABLE: category_products
SCHEMA:
CREATE TABLE "category_products" (
  "category_product_id" int PRIMARY KEY NOT NULL,
  "category_product_category_id" int NOT NULL,
  "category_product_product_id" int NOT NULL
);
DESCRIPTION:
The category_products table defines the association between product categories and the products that belong to them. Each record represents a unique relationship, identified by a category_product_id. The category_product_category_id column references the category to which a product is assigned, while the category_product_product_id column identifies the corresponding product.

---

TABLE: wishlist
SCHEMA:
CREATE TABLE "wishlist" (
  "wishlist_id" int PRIMARY KEY NOT NULL,
  "wishlist_user_id" int NOT NULL,
  "wishlist_created_at" timestamp NOT NULL
);
DESCRIPTION:
The wishlist table stores information about user-created lists of desired products. Each record represents a unique wishlist, identified by a wishlist_id. The wishlist_user_id column references the user who owns the wishlist, linking it to their account.

---

TABLE: wishlist_items
SCHEMA:
CREATE TABLE "wishlist_items" (
  "wishlist_item_id" int PRIMARY KEY NOT NULL,
  "wishlist_item_wishlist_id" int NOT NULL,
  "wishlist_item_product_id" int NOT NULL
);
DESCRIPTION:
The wishlist_items table defines the relationship between wishlists and the products they contain. Each record represents a single product saved to a user’s wishlist, identified by a unique wishlist_item_id. The wishlist_item_wishlist_id column references the wishlist to which the item belongs, while the wishlist_item_product_id column identifies the specific product added

---

TABLE: discounts
SCHEMA:
CREATE TABLE "discounts" (
  "discount_id" int PRIMARY KEY NOT NULL,
  "discount_name" varchar(255) NOT NULL,
  "discount_description" text NOT NULL,
  "discount_percentage" decimal(5, 2) NOT NULL,
  "discount_start_date" timestamp NOT NULL,
  "discount_end_date" timestamp NOT NULL
);
DESCRIPTION:
The discounts table stores information about automatic price reductions applied to products or categories within the system. Each record represents a unique discount, identified by a discount_id. The discount_name column specifies the title of the discount campaign, while discount_description provides detailed information about the offer, including eligibility rules or applicable items. The discount_percentage column indicates the discount rate, expressed as a percentage (e.g., 15.00 for a 15% price reduction).

---

TABLE: product_discounts
SCHEMA:
CREATE TABLE "product_discounts" (
  "product_discount_id" int PRIMARY KEY NOT NULL,
  "product_discount_product_id" int NOT NULL,
  "product_discount_discount_id" int NOT NULL
);
DESCRIPTION:
The product_discounts table maps discounts to the specific products they apply to. Each record represents a unique association, identified by a product_discount_id. The product_discount_product_id column references the product receiving the discount, while the product_discount_discount_id column identifies the corresponding discount from the discounts table.

---

TABLE: cart
SCHEMA:
CREATE TABLE "cart" (
  "cart_id" int PRIMARY KEY NOT NULL,
  "cart_user_id" int NOT NULL,
  "cart_total" decimal(10, 2) NOT NULL,
  "cart_status" varchar(255) NOT NULL DEFAULT 'active',
  "cart_created_at" timestamp NOT NULL,
  "cart_updated_at" timestamp NOT NULL
);
DESCRIPTION:
The cart table stores information about shopping carts created by users in the system. Each record represents a unique cart, identified by a cart_id. The cart_user_id column references the user who owns the cart. The cart_total field records the total monetary value of all items currently in the cart, expressed in U.S. dollars (USD).       

---

TABLE: cart_items
SCHEMA:
CREATE TABLE "cart_items" (
  "cart_item_id" int PRIMARY KEY NOT NULL,
  "cart_item_cart_id" int NOT NULL,
  "cart_item_product_id" int NOT NULL,
  "cart_item_quantity" int NOT NULL,
  "cart_item_price" decimal(10, 2) NOT NULL
);

DESCRIPTION:
The cart_items table stores information about individual products added to a user’s shopping cart. Each record represents a unique item within a cart, identified by a cart_item_id. The cart_item_cart_id column references the cart to which the item belongs, while cart_item_product_id identifies the specific product added. The cart_item_quantity field indicates how many units of the product are included in the cart, and the cart_item_price column records the price of the product in U.S. dollars (USD) at the time it was added.

---

TABLE: orders
SCHEMA:
CREATE TABLE "orders" (
    "order_id" int PRIMARY KEY NOT NULL,
    "order_user_id" int NOT NULL,
    "order_total" decimal(10, 2) NOT NULL,
    "order_status" varchar(255) NOT NULL
        CHECK (order_status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled')),
    "order_created_at" timestamp NOT NULL,
    "order_updated_at" timestamp NOT NULL
);
DESCRIPTION:
The orders table stores information about customer purchase transactions within the system. Each record represents a single order, identified by a unique order_id. The order_user_id column references the user who placed the order. The order_total field records the total monetary amount of the order in U.S. dollars (USD), including all purchased items and applied discounts. The order_status column indicates the current state of the order (pending, paid, shipped, or cancelled). The order_created_at and order_updated_at fields record when the order was first placed and when it was last modified.

---

TABLE: order_items
SCHEMA:
CREATE TABLE "order_items" (
  "order_item_id" int PRIMARY KEY NOT NULL,
  "order_item_order_id" int NOT NULL,
  "order_item_product_id" int NOT NULL,
  "order_item_quantity" int NOT NULL,
  "order_item_price" decimal(10, 2) NOT NULL
);
DESCRIPTION:
The order_items table stores detailed information about the individual products included in each order. Each record represents a single product line within an order, identified by a unique order_item_id. The order_item_order_id column references the corresponding order in the orders table, establishing a one-to-many relationship between orders and their items. The order_item_product_id column links to the specific product being purchased. The order_item_quantity field indicates how many units of that product were ordered, while order_item_price records the price of one unit at the time of purchase.

---

TABLE: users
SCHEMA:
CREATE TABLE "users" (
  "user_id" int PRIMARY KEY NOT NULL,
  "user_name" varchar(255) NOT NULL,
  "user_email" varchar(255) NOT NULL,
  "user_password" varchar(255) NOT NULL,
  "user_created_at" timestamp NOT NULL,
  "user_updated_at" timestamp NOT NULL
);
DESCRIPTION:
The users table stores essential account information for each registered customer in the system. Every record represents one user, uniquely identified by user_id. The user_name field contains the user’s display or full name, while user_email serves as a unique contact and login identifier. The user_password field securely stores the user’s encrypted authentication credential. The user_created_at and user_updated_at timestamps track when the account was initially created and last modified.

---

TABLE: coupons
SCHEMA:
CREATE TABLE "coupons" (
  "coupon_id" int PRIMARY KEY NOT NULL,
  "coupon_code" varchar(255) NOT NULL,
  "coupon_description" text NOT NULL,
  "coupon_discount_percentage" decimal(5, 2) NOT NULL,
  "coupon_start_date" timestamp NOT NULL,
  "coupon_end_date" timestamp NOT NULL
);

DESCRIPTION:
The coupons table defines promotional codes that customers can apply to receive temporary discounts on eligible orders. Each record is uniquely identified by coupon_id and represented by a coupon_code, which customers enter during checkout. The coupon_description explains the promotion or eligibility conditions. The coupon_discount_percentage specifies the rate of discount applied to the order total. The coupon_start_date and coupon_end_date mark the validity period of the coupon, ensuring it can only be used within a defined timeframe. Unlike general discounts (which are tied to specific products), coupons are typically applied at the order level.

---

TABLE: order_coupons
SCHEMA:
CREATE TABLE "order_coupons" (
  "order_coupon_id" int PRIMARY KEY NOT NULL,
  "order_coupon_order_id" int NOT NULL,
  "order_coupon_coupon_id" int NOT NULL
);

DESCRIPTION:
The order_coupons table tracks which discount coupons are applied to specific customer orders. Each record links an order to a coupon, forming a many-to-many relationship between orders and coupons—an order can use multiple coupons, and a coupon can apply to multiple orders. It includes a unique identifier (order_coupon_id), the associated order (order_coupon_order_id), and the applied coupon (order_coupon_coupon_id).

---

TABLE: addresses
SCHEMA:
CREATE TABLE "addresses" (
  "address_id" int PRIMARY KEY NOT NULL,
  "address_user_id" int NOT NULL,
  "address_line1" varchar(255) NOT NULL,
  "address_line2" varchar(255),
  "address_city" varchar(255) NOT NULL,
  "address_state" varchar(255) NOT NULL,
  "address_zip" varchar(10) NOT NULL,
  "address_country" varchar(255) NOT NULL
);
DESCRIPTION:
The addresses table stores postal address information associated with users. Each record represents a unique address that can be linked to a specific user through address_user_id. The table captures standard address components including street information (address_line1 and optional address_line2), city, state, postal code, and country.    

---

TABLE: shipments
SCHEMA:
CREATE TABLE "shipments" (
  "shipment_id" int PRIMARY KEY NOT NULL,
  "shipment_order_id" int NOT NULL,
  "shipment_address_id" int NOT NULL,
  "shipment_status" varchar(255) NOT NULL
      CHECK (shipment_status IN ('preparing', 'in_transit', 'delivered')),
  "shipment_created_at" timestamp NOT NULL,
  "shipment_updated_at" timestamp NOT NULL
);
DESCRIPTION:
The shipments table stores information about the delivery of customer orders. Each record represents a specific shipment linked to an order through shipment_order_id and associated with a delivery address via shipment_address_id. The table tracks the shipment’s current status (“pending,” “shipped,” or “delivered”).

---

TABLE: returns
SCHEMA:
CREATE TABLE "returns" (
  "return_id" int PRIMARY KEY NOT NULL,
  "return_order_id" int NOT NULL,
  "return_user_id" int NOT NULL,
  "return_reason" text NOT NULL,
  "return_status" varchar(255) NOT NULL
      CHECK (return_status IN ('pending', 'approved', 'completed', 'rejected')),
  "return_created_at" timestamp NOT NULL,
  "return_updated_at" timestamp NOT NULL
);
DESCRIPTION:
The returns table records information about product returns initiated by customers. Each entry corresponds to a return request linked to a specific order through return_order_id and to the customer who made the request via return_user_id. It captures the reason for the return, the current status of the return process (“requested,” “approved,” or “completed”), and timestamps for when the return was created and last updated.

---

TABLE: payments
SCHEMA:
CREATE TABLE "payments" (
  "payment_id" int PRIMARY KEY NOT NULL,
  "payment_order_id" int NOT NULL,
  "payment_method" varchar(255) NOT NULL
      CHECK (payment_method IN (
          'paypal',
          'apple_pay',
          'google_pay',
          'credit_card',
          'debit_card'
      )),
  "payment_status" varchar(255) NOT NULL
      CHECK (payment_status IN (
          'completed',
          'failed',
          'pending'
      )),
  "payment_created_at" timestamp NOT NULL,
  "payment_updated_at" timestamp NOT NULL
);
DESCRIPTION:
The payments table stores information about payments made for customer orders. Each record corresponds to a single payment transaction linked to an order through payment_order_id. It captures the payment method used (credit card, PayPal, or bank transfer), the current payment status (“pending,” “completed,” or “failed”), and timestamps for when the payment record was created and last updated.

---

TABLE: transactions
SCHEMA:
CREATE TABLE "transactions" (
  "transaction_id" int PRIMARY KEY NOT NULL,
  "transaction_order_id" int NOT NULL,
  "transaction_payment_id" int NOT NULL ,
  "transaction_status" varchar(255) NOT NULL CHECK (transaction_status IN (
          'completed',
          'failed',
          'pending'
      )),
  "transaction_created_at" timestamp NOT NULL,
  "transaction_updated_at" timestamp NOT NULL
);
DESCRIPTION:
The transactions table stores records of financial transactions associated with customer orders. Each record represents a payment event linked to a specific order via transaction_order_id and to a corresponding payment record through transaction_payment_id. It includes the transaction’s current status ( “pending,” “successful,” or “failed”) and timestamps indicating when the transaction was created and last updated.

---

YOUR TASK
Generate EXACTLY 10 natural-language questions AND SQL queries that a user might ask about the data described in the schema.
Each question MUST be fully answerable using ONLY the tables and fields provided.

STRICT RULES

1. **USE ONLY WHAT IS PROVIDED**
   - Use only tables, columns, and relationships shown in the schema.
   - Never invent additional fields, business logic, or assumptions.

2. **QUESTION QUALITY**
   - Each question must be meaningful and realistic.
   - Each question must require PostgreSQL reasoning (filters, joins, aggregations, sorts, ranges, etc.).
   - Avoid trivial questions (“Show all rows”).

3. **POSTGRESQL RULES**
   - All SQL must be fully valid for the provided schema and must answer the question exactly.
   - Use JOINs only when supported by explicit foreign keys or clearly described relationships.
   - When filtering on TIMESTAMP columns, use valid PostgreSQL timestamp literals:
       'YYYY-MM-DD'  or  'YYYY-MM-DD HH:MI:SS'
   - Never produce placeholder text such as "specific_end_date" or "start_timestamp".
   - Do not reference tables or columns that are not in the schema.
   - Avoid SELECT * — select only meaningful fields unless IDs are required.

4. **AVOID DUPLICATES**
   - Every generated question must be fully unique in meaning, structure, and intent.

5. **OUTPUT FORMAT**
   Only output in the following format:
   Question: <natural language question>
   Answer:
   <valid PostgreSQL query> 

Now generate the questions and queries.