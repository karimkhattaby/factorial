# Factorial e-commerce assessment

## Task
Building a simple e-commerce store for a small business offering a single product, that can be scaled in the future to support multiple products

## Requirements

### High Priority
1. Store will be used to sell bicycles
2. Should support the following customization options
    1. Wheels
        1. Road Wheels
        2. Mountain Wheels
        3. Fat Bike Wheels
    2. Frame Type
        1. Full-suspension
        2. Diamond
        3. Step-through
    3. Frame Finish
        1. Matte
        2. Shiny
    4. Rim Color
        1. Red
        2. Black
        3. Blue
    5. Chain
        1. Single-speed Chain
        2. 8-speed Chain
3. Some combinations of customization options are prohibited
    1. `Mountain Wheels` only support `Full-suspension` Frame Type
    2. `Fat Bike Wheels` only support `Black` and `Blue` Rim Colors
4. Some customization options can be marked as out of stock
5. Price is calculated by adding the prices of all individual parts together
6. Price of some parts depends on previously selected parts (example: `Matte` Frame Finish costs more for the `Full-suspension` Frame Type)

### Mid-Low Priority
1. Add new products
2. Add/Modify customization options and varities
3. Add/Modify prohibited combinations

## Assumptions
1. Dependencies happen in 1 direction (e.g. `Frame Type` depends on `Wheels` and `Frame Finish` depends on `Frame Type`, therefore `Wheels` can't depend on any of those 2, this includes pricing).
2. Delivery will be handled by a logistics company (e.g. DHL) that provides APIs for shipment tracking.

## Customer Journey
Based on the requirements and assumptions above, this is the customer's journey (i.e. user flow):

![User Flow Diagram](https://i.imgur.com/mAZyBor.jpeg "User Flow Diagram")

## Product Development Roadmap

### V1

#### Customer Interface (Store)
1. Simple interface with 1 product (bicycle)
2. Customer journey
3. User authentication
4. Integrate with stripe for online payments

#### Seller Interface (Dashboard)
1. User Authentication to access the dashboard
2. List of parts and variations with the option to mark/unmark each variation as out of stock
3. Fixed customization options, customer journey, prohibited combinations, and prices (to be confirmed by client, any required additions/modifications have to be done manually)

### V2

#### Customer Interface (Store)
1. Track order

#### Seller Interface (Dashboard)
1. Add and modify customization options
2. Add and modify prohibited combinations
3. Modify prices
4. Control customer journey and dependencies (modify the order)

### V3

#### Customer Interface (Store)
1. Reviews
2. Customer support

#### Seller Interface (Dashboard)
1. Add product
2. Inventory management (automate out of stock)

### V4

#### Seller Interface (Dashboard)
1. Analytics within the dashboard
2. Dashboard user management (with different roles for employees)

### Potential Improvements and Additions
1. Integrating LLMs for customer support and to automate some tasks
2. Adding a category layer

## Architecture

Upon release, the platform is expected to serve 100s of simultaneous customers at most for the first 2-3 years so a monolith would be fine. However for the sake of the assessment, let's assume our goal is to build a scalable system to serve millions of simultaneous customers. In that case, here's my approach:

![System Architecture Diagram](https://i.imgur.com/6B1Jljq.png "System Architecture Diagram")

Services:
1. Authentication
2. Store (Catalog + Inventory + Cart)
3. Checkout/Payment
4. Back Office

Jobs:
1. Order processing (including inventory updates and sending confirmation emails to customers). Can be fired by `Service 3`
2. Automatically update analytics every 30 minutes. Can be fired by `Service 4`
3. Payment validation check (including sending confirmation emails to customers). Can be fired by `Service 4`
4. Update catalog (products, parts, variations, pricing, inventory, and customer flow). Can be fired by `Service 4`

The implementation should optimize for Availability over Consistency with a target minimum Avaialbility of 3 nines (99.9% availability, which translates to a maximum of 41.83 minutes of downtime per month).

Despite heavily optimizing for availability, there's 1 functionality that requires optimizing for consistency and that is inventory updates. The eventually consistent property of NoSQL databases might result in orders for out of stock items that can't be fulfilled. To tackle this challenge in a distributed system environment, we'll assign 1 Database node as a master node that receives all inventory update writes from `Job 1` above before propagating to replicas. Also we'll make sure the checkout service checks the main database before placing the order.

## Tech Stack
1. `React` for frontend
    - dynamic, responsive, well-supported, efficient
2. `Nodejs` and `Express` for web servers
    - fast, non-blocking, and scalable
3. `KeyCloak` (open source auth server) for auth service
    - open-source, well-maintained, secure, and supports OAuth2, OpenID and SSO
4. `PostgreSQL` for auth service
    - integrates well with `KeyCloak`
5. `MongoDB` for all other services
    - perfect for storing unstructured data, availability, and scalability
    - can configure write concern for more strict consistency at document level
    - note: mongodb documentation says it provides consistency and not eventual consistency. however this isn't true in the context of a distributed system as it can't guarantee 100% consistency over all distributed replicas
6. `Nginx` for load balancing
    - fast, lightweight, and scalable
7. `Redis` for caching
    - fast and scalable
8. `Bull` as the job queue
    - has advanced features (such as prioritization, repeating, and scheduling),  integrates well with redis, scalable, and well maintained and supported
9. `S3` for cloud storage
10. `Kafka` as the message broker
    - handles high-throughput streams (such as activity logs) better than `RabbitMQ`
11. `Apache Spark` for ETL
    - handles large-scale batch processing, scalable, and suitable for complex data analytics. Consider adding `Apache Flink` if real-time processing is required at some point
12. `Tableau` for analytics/BI
    - easy interaction with data for non-technical users
13. `Airflow` for orchestration
    - scalable, extensible, well-maintained, suitable for batch processing (every 30 minutes updates)
14. `Datadog` for metrics and infrastructure monitoring
    - provides full-observability over the system
15. `Sentry` for error tracking
    - focused error tracking and debugging, suitable for identifying, capturing, and resolving errors, provides detailed stack traces

## Data Model

### Store Service
Here are the collections present in the store service database:

1. Products
    - Stores information about products and associated customization parts
    - Has a one to many relationship with `Parts`
    ```json
    {
        "_id": ObjectId("..."), // MongoDB automatically generates this
        "name": "Bicycle",
        "description": "Customizable bicycle",
        "images": [ // Links to product images on s3 bucket
            "https://s3.amazonaws.com/bucket-name/product1-image1.jpg",
            "https://s3.amazonaws.com/bucket-name/product1-image2.jpg",
        ],
        "parts": [ // IDs of parts related to this product
            ObjectId("..."),
            ObjectId("..."),
        ],
        "available_stock": 1,
    }
    ```

2. Parts
    - Stores information about customization parts and the associated variations
    - Has a one to many relationship with `Variations`
    ```json
    {
        "_id": ObjectId("..."),
        "product_id": ObjectId("..."), // Reference to the parent product
        "name": "Frame Type",
        "icon": "https://s3.amazonaws.com/bucket-name/frame-icon.png",
        "variations": [ // IDs of variations related to this part
            ObjectId("..."), 
        ],
    }
    ```

3. Variations
    - Contains variants of parts, prohibited dependencies, and dependency-based pricing
    ```json
    {
        "_id": ObjectId("..."),
        "part_id": ObjectId("..."), // Reference to the parent part
        "name": "Matte",
        "images": [
            "https://s3.amazonaws.com/bucket-name/matte-finish.jpg",
        ],
        "prohibited_dependencies": [
            ObjectId("..."), // IDs of variations that this variation CANNOT be combined with
        ],
        "prices": [
            {   // Default price
                "dependency_part_id": null,
                "price": 35,
            },
            {   // Price when a specific dependency is selected
                "dependency_part_id": ObjectId("..."),
                "price": 50,
            },
        ],
        "available_stock": 1,
    }
    ```

4. Flow
    - Stores the customer's journey (order in which parts will show to the user)
    ```json
    {
        "_id": ObjectId("..."),
        "product_id": ObjectId("..."), // Reference to the product that this flow represents
        "parts": [
            ObjectId("..."), // ID of the first customizable part
            ObjectId("..."), // ID of the second customizable part
        ]
    }
    ```

5. Reviews
    - Stores customer's reviews
    ```json
    {
        "_id": ObjectId("..."),
        "product_id": ObjectId("..."), // Reference to the product
        "order_id": ObjectId("..."), // Reference to the order to verify the purchase
        "rating": 5,
        "title": "Amazing bicycle and fully customizable",
        "description": "Bought a customized bicycle with full-suspension and mountain wheels. Received it in 2 days. Perfect quality. Thank you bicycle store",
        "author": ObjectId("..."), // Reference to the user who wrote the review
        "created_at": ISODate("2024-10-05T12:00:00Z"),
        "helpful_count": 10, // Number of times other users liked the review
        "report_count": 0, // Number of times other users reported the review
    }
    ```

6. Orders
    - List of orders placed by customers, price, and status
    ```json
    {
        "_id": ObjectId("..."),
        "user_id": ObjectId("..."), // Reference to the user placing the order
        "items": [
            {
                "product_id": ObjectId("..."), // Reference to the product
                "selected_variations": [ // IDs and prices of selected variations
                    {
                        "selected_variation": ObjectId("..."),
                        "price": 200
                    },
                    {
                        "selected_variation": ObjectId("..."),
                        "price": 180
                    },
                ],
            }
        ],
        "status": "pending", // Order status (e.g., "pending", "shipped", etc.)
        "total_price": 380, // Total price of the order
        "created_at": ISODate("2024-10-01T12:00:00Z"),
        "updated_at": ISODate("2024-10-01T13:00:00Z"),
    }
    ```

### Checkout Service
Here are the collections present in the checkout service database:

1. Transactions
    - List of transactions performed by users
    ```json
    {
        "_id": ObjectId("..."),
        "order_id": ObjectId("..."), // Reference to the order this transaction is associated with
        "payment_method": "stripe", // Payment method (e.g., "stripe", "paypal", "cash")
        "payment_status": "completed", // Status of the payment (e.g., "completed", "pending", "failed")
        "transaction_id": "txn_12345", // Unique transaction ID (provided by payment gateway)
        "transaction_date": ISODate("2024-10-01T15:00:00Z"), // Date of the transaction as provided by payment gateway
        "amount": 380, // Amount of the transaction
        "currency": "USD", // Currency used (e.g., "USD", "EUR", etc.)
        "payment_details": {
            "card_last4": "1234", // Last 4 digits of the card (if payment method is credit card)
            "card_type": "Visa", // Type of card (if payment method is credit card)
            "paypal_email": "customer@example.com", // Email for PayPal payments
        },
        "payment_gateway": "stripe", // Payment gateway used (e.g., "stripe", "paypal", "square", "null")
        "created_at": ISODate("2024-10-01T15:00:00Z"), // Timestamp when the transaction was created
        "updated_at": ISODate("2024-10-01T15:05:00Z") // Timestamp when the transaction was last updated
    }
    ```

### Back Office Service
1. Support
    - Tracks customer support cases and stores exchanged messages
    ```json
    {
        "_id": ObjectId("..."),
        "subject": "Issue with product selection",
        "category": "Product Inquiry", // Category of the issue (e.g., "Technical", "Order Issues")
        "owner_id": ObjectId("..."), // ID of the support agent handling the case
        "customer_id": ObjectId("..."), // ID of the customer who submitted the case
        "status": "open", // Case status (e.g., "open", "closed", "in-progress")
        "messages": [
            "Customer: I'm having trouble selecting the correct part.",
            "Support: Can you provide more details about the issue?",
        ],
        "created_at": ISODate("2024-10-01T12:00:00Z"),
        "updated_at": ISODate("2024-10-01T13:00:00Z"),
    }
    ```

### Other
1. Logs
    - Stores logs of users actions
    - Part of data hose
    ```json
    {
        "_id": ObjectId("..."),
        "user_id": ObjectId("..."), // Reference to the user who performed the action
        "action": "viewed product", // Action performed by the user
        "timestamp": ISODate("2024-10-01T12:00:00Z"),
    }
    ```

## Main User Actions

### Customers
1. View Product
    - Includes product details, pictures, and reviews
    - Pulls data from store service database for catalog, inventory, and reviews
2. Customize Product
    - Choose which parts to assemble the bicycle
    - Pulls data from store service database for parts and variations
3. Add to Cart
    - Add customized bicycle to cart
    - Stores the data into session store (debating whether pushing this session to backend is necessary, I think that's unnecessary)
4. View Cart
    - List of items in cart, price breakdown, and total price
    - Uses data stored in session store
    - Pulls price data from store service database to check for updates
5. Checkout
    - Checks items availability, then takes customer through payment flow, before placing the order and processing it
    - Queries store service to check inventory, and checkout service for payment and order processing
6. Signup
    - Handled by auth service
7. Login
    - Handled by auth service
8. View orders
    - Views already placed orders, price breakdown, and delivery status
    - Handled by store service
9. Submit claims
    - Contact customer support to request order cancellation, refunds, and more
    - Handled by back office service
10. Review a product
    - Handled by store service
11. Change Email
    - Handled by auth service
12. Change Password
    - Handled by auth service
13. Reset Password
    - Handled by auth service

### Seller
1. Manage products
    - Handled by back office service
2. Manage parts
    - Handled by back office service
3. Manage variations
    - Handled by back office service
4. Manage users
    - Handled by auth service
5. Manage inventory
    - Handled by back office service
6. Manage customer flow
    - Drag and drop screen to change the order of customization parts based on dependencies. Done this way to reduce the complexity and liability.
7. Manage pricing
    - Handled by back office service

## FAQ

### Product Page

- `How would you present this UI?`

As explained in `Customer Journey`, the main page will have a list of products. When a user selects a product they will see images and reviews. If they want to add the item to cart, they will go through the customization options before reaching the cart page. When the user decides to checkout, they will go through the payment flow from Stripe before reaching the success/failure screen.

- `How would you calculate which options are available?`

This is done on 3 stages. At first when the catalog is loading, the app will check the `available_stock` key in the product's document to determine if the product is in stock. Then when the user is going through each of the customization options, the app will check the `available_stock` key in the product's document to determine if the variation is in stock. At last when the user tries to checkout, the app will check the `available_stock` on all products and variations to ensure everything is still in stock before charging the user. If the last step is found to be adding an overhead on the server, it can be modified into one of the following options:
1. Delay the payment and use a job fired by the checkout service to determine whether the order can be placed in the background without affecting the user experience.
2. Implement a reservation model so when a user adds an item to cart, the system will reserve the items for a period of time and will release it back to inventory if the order isn't finalized within this time frame.

- `How would you calculate the price depending on the customer's selections?`

The approach I used was to offload the dependency management as the responsibility of the seller to minimize liability and complexity. So the seller has to decide which variations should be selected by the user before others in a simple drag and drop UI that I call the `Customer Flow`. The seller also has to enter the correct pricing in the manage catalog page, and select the correct dependencies for each item.

Another UX approach can be releasing another drag and drop UI that has both dependency management and pricing in 1 place.


### Add to Cart Action

- `What happens when the customer clicks this button?`

Currently, the item will be added in the cart object stored on the browser's session-store.

- `What is persisted in the database?`

Logs of user actions go to the data hose where analytics are performed. Aside from that cart isn't persisted in the database, but only in the browser's session-store. I think persisting the items in cart by storing them in the cache or database on the server is unnecessary and adds an unnecessary overhead. In case of taking the reservation model approach mentioned above in the `Product Page` section, the cart will be stored on redis with the proper timeout. However, this will add an extra overhead on the server since there will be an additional request per cart action. This overhead can actually be mitigated by merging the request with the log request.

### Administrative Workflows

#### New Product Creation

- `What information is required to create a new product? How does the database change?`

The required information are name and images. However, to complete the product, parts and variations and required to be added and linked to the product. A new document is added to the `Products` collection when a new product is added.

#### Adding a New Part Choice

- `How can Marcus introduce a new rim color? Describe the UI and how the database changes.`

Marcus can simply add a new rim color by logging into the `Seller Dashboard`, navigating to list of products, and clicking on `add a new variation` in the `Rim Colors` sections and filling in the information. Once submitted, new document is added to the `Variations` collection when a new variation is added. In terms of UI changes, the `Seller Dashboard` will have the new rim color, and it will show to the users when customizing the bicycle next to the other rim colors.

#### Setting Prices

- `How can Marcus change the price of a specific part or specify particular pricing for combinations of choices? How does the UI and database handle this?`

Marcus can change the price of a specific part by logging into the `Seller Dashboard`, navigating to list of products, selecting the part, then change the price variable. Once submitted, the appropriate document in the `Variations` collection will be modified to reflect the new price and the UI will simply reflect the new price on the next refresh (both automatic and manual refreshes).

In the same screen, Marcus can select a dependency and add its own price, to choose the price of the variation when another variation is selected. Same effects apply upon submission.


# Notes
What's remaining:<br>
1- frontend code: didn't have enough time to implement it, but here's an old project to compensate (hosted version is no longer working): https://github.com/karimkhattaby/smart-brain <br>
2- implementing interface methods between api and mongodb <br>
3- implementing api endpoints, here's an old project to compensate (hosted version is no longer working): https://github.com/karimkhattaby/smart-brain-api and https://github.com/karimkhattaby/smart-brain-api-deno <br>
I can show you more projects during the presentation if required. <br>
