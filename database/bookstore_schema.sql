
-- Create table for books
CREATE TABLE books (
    isbn CHAR(10) PRIMARY KEY,
    author VARCHAR(100),
    title VARCHAR(200),
    price FLOAT,
    subject VARCHAR(100)
);

-- Create table for members
CREATE TABLE members (
    userid SERIAL PRIMARY KEY,
    fname VARCHAR(50),
    lname VARCHAR(50),
    address VARCHAR(50),
    city VARCHAR(30),
    zip INT,
    phone VARCHAR(15),
    email VARCHAR(40) UNIQUE NOT NULL,
    password VARCHAR(200)
);

-- Create table for orders
CREATE TABLE orders (
    orderid SERIAL PRIMARY KEY,
    userid INT NOT NULL REFERENCES bookstore.members(userid),
    ono INT UNIQUE NOT NULL,
    created DATE NOT NULL,
    shipAddress VARCHAR(50),
    shipCity VARCHAR(30),
    shipZip INT
);

-- Create table for order details
CREATE TABLE orderdetails (
    ono INT NOT NULL REFERENCES bookstore.orders(ono),
    isbn CHAR(10) NOT NULL REFERENCES bookstore.books(isbn),
    qty INT NOT NULL,
    amount FLOAT,
    PRIMARY KEY (ono, isbn)
);

-- Create table for cart
CREATE TABLE thecart (
    userid INT NOT NULL REFERENCES bookstore.members(userid),
    isbn CHAR(10) NOT NULL REFERENCES bookstore.books(isbn),
    qty INT NOT NULL,
    PRIMARY KEY (userid, isbn)
);
