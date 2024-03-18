-- Create Users table
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL
);

-- Create Orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    order_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Create NoPrimaryKey table
CREATE TABLE IF NOT EXISTS NoPrimaryKey (
    product_name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS AllTypes (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    datetime_col DATETIME,
    date_col DATE,
    time_col TIME,
    string_col TEXT,
    int_col INTEGER,
    float_col REAL,
    bool_col INTEGER
);

INSERT INTO AllTypes (datetime_col, date_col, time_col, string_col, int_col, float_col, bool_col) 
VALUES 
('2024-03-14 15:00:00', '2024-03-14', '15:00:00', 'First Entry', 1, 1.1, 1),
('2024-03-15 16:30:00', '2024-03-15', '16:30:00', 'Second Entry', 2, 2.2, 0),
('2024-03-16 17:45:00', '2024-03-16', '17:45:00', 'Third Entry', 3, 3.3, 1);


-- Insert data into Users table
INSERT INTO users (username, email) VALUES
    ('John Doe', 'john.doe@example.com'),
    ('Jane Smith', 'jane.smith@example.com'),
    ('Bob Jones', 'bob.jones@example.com'),
    ('Alice Wonder', 'alice.wonder@example.com'),
    ('Charlie Brown', 'charlie.brown@example.com'),
    ('Diana Rogers', 'diana.rogers@example.com'),
    ('Edward White', 'edward.white@example.com'),
    ('Fiona Miller', 'fiona.miller@example.com'),
    ('George Smith', 'george.smith@example.com'),
    ('Helen Brown', 'helen.brown@example.com');

-- Insert data into Orders table
INSERT INTO orders (user_id, product_name, quantity, total_price, order_date) VALUES
    (1, 'Laptop', 2, 1500.00, '2023-01-15'),
    (1, 'Mouse', 1, 25.50, '2023-02-05'),
    (2, 'Keyboard', 1, 50.00, '2023-03-12'),
    (3, 'Headphones', 2, 75.00, '2023-04-20'),
    (3, 'Monitor', 1, 300.00, '2023-05-01'),
    (4, 'Tablet', 1, 200.00, '2023-06-08'),
    (5, 'Printer', 1, 120.00, '2023-07-15'),
    (6, 'External HDD', 1, 80.00, '2023-08-22'),
    (7, 'Camera', 1, 350.00, '2023-09-30'),
    (8, 'Smartphone', 1, 600.00, '2023-10-10');

-- Insert data into NoPrimaryKey table
INSERT INTO NoPrimaryKey (product_name, quantity) VALUES
    ('Laptop', 2),
    ('Mouse', 1),
    ('Keyboard', 1),
    ('Headphones', 2),
    ('Monitor', 1),
    ('Tablet', 1),
    ('Printer', 1),
    ('External HDD08-22', 1),
    ('Camera', 1),
    ('Smartphone', 1);
