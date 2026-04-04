-- PostgreSQL schema (with foreign keys per ER diagram)
-- Use with: python app.py --init-db

CREATE TABLE IF NOT EXISTS Airport (
  airport_code VARCHAR(3) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  city VARCHAR(50) NOT NULL,
  country VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS Aircraft (
  plane_type VARCHAR(30) PRIMARY KEY,
  capacity INT NOT NULL CHECK (capacity >= 0)
);

CREATE TABLE IF NOT EXISTS FlightService (
  flight_number VARCHAR(10) PRIMARY KEY,
  airline_name VARCHAR(50) NOT NULL,
  origin_code VARCHAR(3) NOT NULL,
  dest_code VARCHAR(3) NOT NULL,
  departure_time TIME NOT NULL,
  duration INTERVAL NOT NULL,
  FOREIGN KEY (origin_code) REFERENCES Airport (airport_code),
  FOREIGN KEY (dest_code) REFERENCES Airport (airport_code)
);

CREATE TABLE IF NOT EXISTS Flight (
  flight_number VARCHAR(10) NOT NULL,
  departure_date DATE NOT NULL,
  plane_type VARCHAR(30) NOT NULL,
  PRIMARY KEY (flight_number, departure_date),
  FOREIGN KEY (flight_number) REFERENCES FlightService (flight_number),
  FOREIGN KEY (plane_type) REFERENCES Aircraft (plane_type)
);

CREATE TABLE IF NOT EXISTS Passenger (
  pid INT PRIMARY KEY,
  passenger_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS Booking (
  pid INT NOT NULL,
  flight_number VARCHAR(10) NOT NULL,
  departure_date DATE NOT NULL,
  seat_number INT NOT NULL,
  PRIMARY KEY (pid, flight_number, departure_date),
  FOREIGN KEY (pid) REFERENCES Passenger (pid),
  FOREIGN KEY (flight_number, departure_date)
    REFERENCES Flight (flight_number, departure_date)
);
