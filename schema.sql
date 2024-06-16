CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    pwd VARCHAR(300) NOT NULL,
    admin BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE "account" (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    balance FLOAT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES "user"(id)
);

CREATE TABLE "category" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE "transaction" (
    id SERIAL PRIMARY KEY,
    description VARCHAR(200) NOT NULL,
    amount FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL,
    account_id INTEGER NOT NULL,
    recurring BOOLEAN DEFAULT false,
    FOREIGN KEY (user_id) REFERENCES "user"(id),
    FOREIGN KEY (account_id) REFERENCES "account"(id)
);

CREATE TABLE "transaction_category" (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES "transaction"(id),
    FOREIGN KEY (category_id) REFERENCES "category"(id)
);