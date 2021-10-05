CREATE DATABASE Report;
CREATE USER report WITH ENCRYPTED PASSWORD 'XN5ZjSLPW8b6Nxs4';
GRANT ALL PRIVILEGES ON DATABASE Report TO report;


CREATE TABLE Visitor(
    id VARCHAR(255) PRIMARY KEY,
    date TIMESTAMP NOT NULL,
    durationSecs INT NOT NULL,
    isNew BOOL NOT NULL
);

CREATE TABLE Product(
    id INT PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    name VARCHAR(255),
    activityType VARCHAR(255) NOT NULL
);

CREATE TABLE Sell(
    id INT PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    visitorId VARCHAR(255) NOT NULL,
    productId INT NOT NULL,
    FOREIGN KEY (visitorId) REFERENCES Visitor(id),
    FOREIGN KEY (productId) REFERENCES Product(id)
);