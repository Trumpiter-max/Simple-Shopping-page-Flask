DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS account;
DROP TABLE IF EXISTS cart;

PRAGMA foreign_keys = ON;

CREATE TABLE product (
    productID INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    product_name TEXT NOT NULL,
    price FLOAT NOT NULL,
    quantity BIGINT NOT NULL,
    discount INTEGER
);

CREATE TABLE account (
    userID INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    userPassword TEXT NOT NULL,
    email TEXT NOT NULL,
    firstname TEXT,
    lastname TEXT,
    useraddress TEXT,
    avatarname TEXT,
    balance FLOAT NOT NULL,
    tier INTEGER NOT NULL,
    phone TEXT
);

CREATE TABLE cart (
    cartID INTEGER PRIMARY KEY AUTOINCREMENT,
    userID INTEGER,
    productQuantity INTEGER,
    productID INTEGER,
    total FLOAT,
    FOREIGN KEY (userID) REFERENCES account(userID),   
    FOREIGN KEY (productID) REFERENCES product(productID)
);