from dbmanager import DBManager

#edit listings attribute to make it less sus

class Listing(DBManager):

    def __init__(self, listing_id=None, user_id=None, title=None, description=None, category=None, price=None, image_path=None, is_sold=None):
        super().__init__()  # Call the parent class constructor (DatabaseManager)
        self.listing_id = listing_id
        self.user_id = user_id
        self.title = title
        self.description = description
        self.category = category
        self.price = price
        self.image_path = image_path
        self.is_sold = is_sold

    def create_listing(self):

        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO listings (user_id, title, description, category, price, image_path) VALUES (?, ?, ?, ?, ?, ?)''',
                       (self.user_id, self.title, self.description, self.category, self.price, self.image_path))
        self.conn.commit()
        self.listing_id = cursor.lastrowid
        cursor.close()

    def edit_listing(self):

        if not self.listing_id:
          print("Error: Listing ID not set. Please load a listing before editing.")
          return
        cursor = self.conn.cursor()
        cursor.execute("""UPDATE listings SET title = ?, description = ?, category = ?, price = ?, image_path = ? WHERE listing_id = ?""",
                       (self.title, self.description, self.category, self.price, self.image_path, self.listing_id))
        self.conn.commit()
        cursor.close()

    def delete_listing(self):
        if not self.listing_id:
          print("Error: Listing ID not set. Please load a listing before deleting.")
          return
        cursor = self.conn.cursor()
        cursor.execute("""DELETE FROM listings WHERE listing_id = ?""", (self.listing_id,))
        self.conn.commit()
        cursor.close()

    def sold_listing(self):
        if not self.listing_id:
            print("Error: Listing ID not set. Please load a case before deleting.")
            return
        cursor = self.conn.cursor()
        cursor.execute("UPDATE listings SET is_sold = 1 WHERE listing_id = ?", (self.listing_id,))
        self.conn.commit()
        cursor.close()


    def get_listing_by_id(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM listings WHERE listing_id = ?", (self.listing_id,))
        listing_data = cursor.fetchone()
        cursor.close()  # Check if data exists before populating attributes
        self.listing_id = listing_data[0]
        self.user_id = listing_data[1]
        self.title = listing_data[2]
        self.description = listing_data[3]
        self.category = listing_data[4]
        self.price = listing_data[5]
        self.image_path = listing_data[6]
        return listing_data
