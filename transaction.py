from dbmanager import DBManager
from listing import Listing
from datetime import datetime

class Transaction(DBManager):

  def __init__(self, transaction_id=None, listing_id=None, buyer_id=None, seller_id=None, transaction_date=None):
    super().__init__()  # Call the parent class constructor (DatabaseManager)
    self.transaction_id = transaction_id
    self.listing_id = listing_id
    self.buyer_id = buyer_id
    self.seller_id = seller_id
    self.transaction_date = transaction_date

  def create_transaction(self):
    cursor = self.conn.cursor()
    # Check if open date is specified, if not set as current timestamp
    if self.transaction_date is None:
        self.transaction_date = datetime.now().strftime(r'%Y-%m-%d %H:%M:%S')
        
    cursor.execute("INSERT INTO transactions (listing_id, buyer_id, transaction_date) VALUES (?, ?, ?)",
                   (self.listing_id, self.buyer_id, self.transaction_date))

    self.conn.commit()
    self.transaction_id = cursor.lastrowid
    cursor.close()
    listing = Listing(listing_id=self.listing_id)
    listing.sold_listing()

  def delete_transaction(self):
    if not self.transaction_id:
      print("Error: Transaction ID not set. Please load a transaction before deleting.")
      return
    cursor = self.conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE transaction_id = ?", (self.transaction_id,))
    self.conn.commit()

  def update_transaction(self, transaction_id, new_data):
  #   # Implement logic to update transaction based on new_data
  #   # Example:
     try:
         cursor = self.conn.cursor()
         update_fields = []
         update_values = []
         for key, value in new_data.items():
             update_fields.append(key + " = ?")
             update_values.append(value)
         update_query = f"UPDATE transactions SET {', '.join(update_fields)} WHERE transaction_id = ?"
         update_values.append(transaction_id)
         cursor.execute(update_query, update_values)
         self.conn.commit()
         return True
     except Exception as e:
         print(f"Error updating transaction: {e}")
         return False
