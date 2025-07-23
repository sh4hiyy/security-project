# import datetime as dt
# from dbmanager import *
# from user import User
# from listing import Listing
# from transaction import Transaction
#
#
# # users = [
# #     User(username="admin", email="ecothrift@admin.com", password="admin123", is_admin=1),
# #     User(username="ex1", email="ex1@example.com", password="password123", profile_pic='https://i.pinimg.com/originals/c5/fb/d4/c5fbd488e4eb8c73a1fd3a2c0c407af7.jpg'),
# # ]
#
# # listings_categories = [
# #     "Blouse", "Jeans", "Outerwear", "Dresses", "Sweaters", "Others"
# # ]
#
# listings = [
#     Listing(user_id=5, title="yellow blouse", description="size: L, condition: like new, colour: yellow", category="blouse", price=13.00,image_path="img/Screenshot 2025-01-27 at 11.54.47 AM.png"),
#     Listing(user_id=5, title="blue boyfriend jeans", description="size: M, condition: well used, colour: blue", category="jeans", price=16.00,image_path="img/Screenshot 2025-02-16 at 3.23.43 PM.png"),
#     Listing(user_id=5, title="black pea coat", description="size: L, condiition: like new, colour: black", category="outerwear", price=19.50,image_path="img/Screenshot 2025-02-16 at 3.23.17 PM.png"),
#     Listing(user_id=5, title="blue whtie flower top", description="size: M, condition: like new, colour: white", category="blouse", price=11.00,image_path="img/Screenshot 2025-02-16 at 3.24.47 PM.png"),
#     Listing(user_id=5, title="flannel shirt", description="size: L, condition: well used, colour: blue", category="blouse", price=13.00,image_path="img/Screenshot 2025-01-27 at 11.54.47 AM.png"),
#     Listing(user_id=5, title="dark green high nesk blouse", description="size: S, condition: well used, colour: green", category="blouse", price=13.00,image_path="img/Screenshot 2025-02-16 at 5.44.57 PM.png"),
#     Listing(user_id=5, title="white plain blouse", description="size: S, condition: like new, colour: white", category="blouse", price=10.00,image_path="img/Screenshot 2025-02-16 at 5.45.17 PM.png"),
#     Listing(user_id=2, title="blue vneck blouse", description="size: M, condition: well used, colour: blue", category="blouse", price=15.00,image_path="img/Screenshot 2025-02-16 at 5.45.46 PM.png"),
#     Listing(user_id=5, title="navy sleeve blouse", description="size: M, condition: like new, colour: blue", category="blouse", price=18.50,image_path="img/Screenshot 2025-02-16 at 5.46.40 PM.png"),
#     Listing(user_id=5, title="green button down blouse", description="size: L, condition: heaviliy used, colour: green", category="blouse", price=6.00,image_path="img/Screenshot 2025-02-16 at 6.00.44 PM.png"),
#     Listing(user_id=5, title="khaki outerwear", description="size: M, condition: well used, colour: brown", category="outerwear", price=35.00,image_path="img/Screenshot 2025-02-16 at 6.04.35 PM.png"),
#     Listing(user_id=5, title="black turtle neck jacket", description="size: L, condition: like new, colour: black", category="outerwear", price=15.00,image_path="img/Screenshot 2025-02-16 at 6.07.58 PM.png"),
#     Listing(user_id=5, title="blue cropped jacket", description="size: M, condition: well used, colour: blue", category="outerwear", price=13.50,image_path="img/Screenshot 2025-02-16 at 6.10.04 PM.png"),
#     Listing(user_id=5, title="love bonito yellow cropped jacket", description="size: XL, condition: like new, colour: yellow", category="outerwear", price=12.00,image_path="img/Screenshot 2025-02-16 at 6.12.17 PM.png"),
#     Listing(user_id=5, title="red button down stud jacket", description="size: L, condition: well used, colour: red", category="outerwear", price=8.00,image_path="img/Screenshot 2025-02-16 at 6.13.51 PM.png"),
#     Listing(user_id=5, title="dark blue straight jeans", description="size: M, condition: like new, colour: blue", category="jeans", price=17.00,image_path="img/Screenshot 2025-02-16 at 6.16.30 PM.png"),
#     Listing(user_id=5, title="blue denim jeans", description="size: M, condition: like new, colour: blue", category="jeans", price=25.00,image_path="img/Screenshot 2025-02-16 at 6.18.57 PM.png"),
#     Listing(user_id=5, title="pink denim jeans", description="size: M, condition: well used, colour: pink", category="jeans", price=12.00,image_path="img/Screenshot 2025-02-16 at 6.20.26 PM.png"),
#     Listing(user_id=5, title="blue denim skinny jeans", description="size: L, condition: like new, colour: blue", category="jeans", price=15.00,image_path="img/Screenshot 2025-02-16 at 6.21.19 PM.png"),
#     Listing(user_id=5, title="black contrast stitch jeans", description="size: M, condition: well used, colour: black", category="jeans", price=16.50,image_path="img/Screenshot 2025-02-16 at 6.22.10 PM.png"),
# ]
#
# #
# # transactions = [
# #     Transaction(listing_id = 1, buyer_id = 2, transaction_date="2024-03-01 01:01:01"),
# #     Transaction(listing_id = 2, buyer_id = 2, transaction_date="2024-06-01 16:03:24")
# # ]
#
#
#
# #
# # for user in users:
# #     user.create_user()
#
# for listing in listings:
#     listing.create_listing()
#
# # for transaction in transactions:
# #     transaction.create_transaction()
#
# print('Users Table')
# print(DBManager().get_table("users").to_string(index=False))
#
# print('Listings Table')
# print(DBManager().get_table("listings").to_string(index=False))
#
# print('Transactions Table')
# print(DBManager().get_table("transactions").to_string(index=False))

# !/usr/bin/env python3
# add_data.py - Clothing-specific data population script

# !/usr/bin/env python3
# add_data.py - Fixed version for MySQL compatibility

# !/usr/bin/env python3
# add_data.py - Perfectly aligned with your MySQL listings table

from dbmanager import DBManager
import random
from datetime import datetime, timedelta

# Categories exactly matching your CreateListingForm
CATEGORIES = [
    "blouse",
    "jeans",
    "outerwear",
    "dresses",
    "sweaters",
    "others"
]

# Sample brands for realistic listings
BRANDS = {
    "blouse": ["Zara", "H&M", "Forever 21", "Anthropologie"],
    "jeans": ["Levi's", "Madewell", "AG", "7 For All Mankind"],
    "outerwear": ["The North Face", "Patagonia", "Columbia"],
    "dresses": ["Reformation", "& Other Stories", "ASOS"],
    "sweaters": ["J.Crew", "Banana Republic", "Uniqlo"],
    "others": ["Vintage", "Handmade", "Designer"]
}


def generate_listings(user_ids, count=50):
    """Generate listings that perfectly match your schema"""
    listings = []
    conditions = ["New", "Like New", "Good", "Fair", "Worn"]

    for _ in range(count):
        category = random.choice(CATEGORIES)
        brand = random.choice(BRANDS[category])

        listings.append({
            'user_id': random.choice(user_ids),
            'title': f"{brand} {category.capitalize()}",
            'description': f"Quality {category} from {brand}. {random.choice(['Great condition!', 'Minor wear.', 'Classic style.'])}",
            'category': category,
            'price': round(random.uniform(10, 200), 2),
            'image_path': f"https://picsum.photos/id/{random.randint(1, 1000)}/600/400",
            'is_sold': random.random() < 0.2  # 20% chance of being sold
        })
    return listings


def main():
    print("=== Populating EcoThrift Listings ===")
    db = DBManager()

    try:
        # Verify users exist first
        users = db.fetch_all("SELECT user_id FROM users")
        if not users:
            print("Error: No users found. Create users first.")
            return

        user_ids = [u['user_id'] for u in users]

        # Generate and insert listings
        listings = generate_listings(user_ids)
        success = 0

        for l in listings:
            query = """
            INSERT INTO listings 
            (user_id, title, description, category, price, image_path, is_sold)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                l['user_id'],
                l['title'],
                l['description'],
                l['category'],
                l['price'],
                l['image_path'],
                l['is_sold']
            )

            if db.execute_query(query, params):
                success += 1
            else:
                print(f"Failed to add: {l['title']}")

        print(f"\nSuccessfully added {success}/{len(listings)} listings")
        print("Categories used:", ", ".join(CATEGORIES))

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        db.close_connection()


if __name__ == "__main__":
    main()