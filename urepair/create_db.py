import sqlite3

# Establish connection to database
conn = sqlite3.connect('user_db.db')
cursor = conn.cursor()

# Create users_clients table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users_clients (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL,
  password TEXT NOT NULL,
  name TEXT NOT NULL, 
  email TEXT NOT NULL
)""")

# Create pro_users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS pro_users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL,
  password TEXT NOT NULL,
  name TEXT NOT NULL, 
  email TEXT NOT NULL
)""")

#Create services table
cursor.execute("""
CREATE TABLE IF NOT EXISTS services (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  professional_id INTEGER NOT NULL,
  service_name TEXT NOT NULL,
  service_description TEXT,
  price REAL,
  FOREIGN KEY (professional_id) REFERENCES pro_users(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS service_requests (
  request_id INTEGER PRIMARY KEY AUTOINCREMENT,
  client_id INTEGER NOT NULL, 
  professional_id INTEGER NOT NULL, 
  service_type TEXT NOT NULL,
  message TEXT,
  client_email TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  FOREIGN KEY (client_id) REFERENCES users_clients(id),
  FOREIGN KEY (professional_id) REFERENCES pro_users(id)              
  )

""")

# Insert data into users_clients table
cursor.execute("""
INSERT INTO users_clients (username, password, name, email) VALUES 
('user1', 'pass123', 'Mike Smith', 'mike@example.com'),
('user2', 'pass124', 'Mike Jordan', 'mikeJordan@example.com')
""")

# Insert data into repair_users table
cursor.execute("""
INSERT INTO pro_users (username, password, name, email) VALUES 
('pro1', 'repairPass1', 'John Doe', 'john@example.com'),
('pro2', 'repairPass2', 'Jane Doe', 'jane@example.com')
""")
cursor.execute("""
INSERT INTO services (professional_id, service_name, service_description, price) VALUES 
('1', 'plumbing', 'I do plumbing', '100.0'),
('2', 'carpentry', 'I do carpentry', '100.00')
""")

# Commit the transaction and close the connection
conn.commit()
conn.close()
