import sqlite3

connection = sqlite3.connect('test.db')

# excute script in schema.sql for making new table
with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# insert into database with some sample 
cur.execute("INSERT INTO product (product_name, price, quantity) VALUES (?, ?, ?)",
            ('Product A', 10, 10)
            )

cur.execute("INSERT INTO product (product_name, price, quantity) VALUES (?, ?, ?)",
            ('Product B', 10, 10)
            )

cur.execute("INSERT INTO product (product_name, price, quantity) VALUES (?, ?, ?)",
            ('Product C', 10, 10)
            )


connection.commit()
connection.close()