import pymysql
from werkzeug.security import generate_password_hash, check_password_hash

myDB = pymysql.connect(host="localhost", user="root", password="120604")
myCursor = myDB.cursor()

myCursor.execute("drop database if exists palestinian_airlines")
myCursor.execute("create database palestinian_airlines")
myCursor.execute("use palestinian_airlines")
myCursor.execute("set SQL_SAFE_UPDATES=0")

myCursor.execute("""
-- user
Create Table User_ (
	user_id INT primary key auto_increment,
	first_name VARCHAR(50),
	last_name VARCHAR(50),
	date_of_birth DATE,
	email VARCHAR (100),
	phone_number VARCHAR(15),
	hashed_password VARCHAR(10000)
);

""")


myCursor.execute("""
-- Airplane
CREATE TABLE Airplane (
	airplane_id INT PRIMARY KEY AUTO_INCREMENT,
	number_of_seats INT,
	model VARCHAR(50),
	capacity INT,
	year_of_manufacture YEAR
);
""")

myCursor.execute("""
-- Airport
CREATE TABLE Airport (
	airport_id INT PRIMARY KEY AUTO_INCREMENT,
	name VARCHAR(100),
	location VARCHAR(100),
	country VARCHAR(50),
	IATA_code CHAR(3) -- International Air Transport Association code
);
""")

myCursor.execute("""
-- Flight
CREATE TABLE Flight (
	flight_id INT PRIMARY KEY AUTO_INCREMENT,
	flight_number VARCHAR(20),
	departure_airport_id INT,
	arrival_airport_id INT,
	departure_date DATE,
	departure_time TIME,
	arrival_date DATE,
	arrival_time TIME,
	flight_duration TIME,
	available_seats  int,
	airplane_id INT,
	price REAL,
	FOREIGN KEY (departure_airport_id) REFERENCES Airport(airport_id),
	FOREIGN KEY (arrival_airport_id) REFERENCES Airport(airport_id),
	FOREIGN KEY (airplane_id) REFERENCES Airplane(airplane_id)
);
""")

myCursor.execute("""
-- Passenger
CREATE TABLE Passenger (
	passenger_ssn INT PRIMARY KEY,
	first_name VARCHAR(50),
	last_name VARCHAR(50),
	gender VARCHAR(100),
	date_of_birth DATE,
	nationality VARCHAR(50)
);
""")

myCursor.execute("""
-- Booking
CREATE TABLE Booking (
	booking_id INT PRIMARY KEY AUTO_INCREMENT,
	booking_date DATE,
	payment_status VARCHAR(20),
	total_amount REAL,
	booking_status VARCHAR(20) DEFAULT "Active"
);
""")

myCursor.execute("""
CREATE TABLE Bill (
    bill_id INT PRIMARY KEY AUTO_INCREMENT,
    payment_date DATE,
    payment_time TIME,
    payment_method VARCHAR(50),
    amount REAL,
    booking_id INT,
    flight_id INT,
    user_id INT,
    card_type VARCHAR(50),
    card_number VARCHAR(20),
    expiry_month INT,
    expiry_year INT,
    cvv VARCHAR(4),
    cardholder_name VARCHAR(100),
    FOREIGN KEY (booking_id) REFERENCES Booking(booking_id),
    FOREIGN KEY (flight_id) REFERENCES Flight(flight_id),
    FOREIGN KEY (user_id) REFERENCES user_(user_id)
);
""")

myCursor.execute("""
-- Passenger_Flight_Booking
CREATE TABLE Passenger_Flight_Booking (
    passenger_ssn INT,
    flight_id INT,
    booking_id INT,
    ticket_id INT,
    is_deleted INT default 0,
    FOREIGN KEY (passenger_ssn) REFERENCES Passenger(passenger_ssn),
    FOREIGN KEY (flight_id) REFERENCES Flight(flight_id),
    FOREIGN KEY (booking_id) REFERENCES Booking(booking_id),
    primary key(booking_id,flight_id,passenger_ssn)
);
""")



myCursor.execute("""
-- Passenger_User
CREATE TABLE Passenger_User (
	passenger_ssn INT,
	user_id INT,
	FOREIGN KEY (passenger_ssn) REFERENCES Passenger(passenger_ssn),
	FOREIGN KEY (user_id) REFERENCES User_(user_id),
	primary key(passenger_ssn, user_id)
);
""")

query = """INSERT INTO User_(first_name, last_name, email, phone_number, date_of_birth, hashed_password) 
VALUES (%s, %s, %s, %s, %s, %s);"""

data = [
    ('Ahmed', 'Hassan', 'ahmedhassan@gmail.com', '+201012345678', '1990-04-15', generate_password_hash('1234567890')),
    ('Taleed', 'Hamadneh', 'taleedhamadneh12@gmail.com', '+972598762395', '2004-06-12', generate_password_hash('taleedhamadneh')),
    ('Qasim', 'Batrawi', 'qasim@gmail.com', '0595398111', '2004-05-15', generate_password_hash('qasim1234')),
    ('Salah', 'Dawabsheh', 'salahsami@gmail.com', '+970595974496', '2003-03-15', generate_password_hash('salah12345678'))
]

myCursor.executemany(query, data)


myCursor.execute("""
INSERT INTO Airport (name, location, country, IATA_code) VALUES
('Cairo International Airport', 'Cairo', 'Egypt', 'CAI'),
('King Abdulaziz International Airport', 'Jeddah', 'Saudi Arabia', 'JED'),
('Dubai International Airport', 'Dubai', 'UAE', 'DXB'),
('Beirut–Rafic Hariri International Airport', 'Beirut', 'Lebanon', 'BEY'),
('Doha International Airport', 'Doha', 'Qatar', 'DOH'),
('Kuwait International Airport', 'Kuwait City', 'Kuwait', 'KWI'),
('King Khalid International Airport', 'Riyadh', 'Saudi Arabia', 'RUH'),
('Abu Dhabi International Airport', 'Abu Dhabi', 'UAE', 'AUH'),
('Queen Alia International Airport', 'Amman', 'Jordan', 'AMM'),
('Muscat International Airport', 'Muscat', 'Oman', 'MCT'),
('O.R. Tambo International Airport', 'Johannesburg', 'South Africa', 'JNB'),
('Cape Town International Airport', 'Cape Town', 'South Africa', 'CPT'),
('Port Elizabeth International Airport', 'Port Elizabeth', 'South Africa', 'PLZ'),
('King Shaka International Airport', 'Durban', 'South Africa', 'DUR'),
('East London Airport', 'East London', 'South Africa', 'ELS'); 
""")


myCursor.execute("""
INSERT INTO Airplane (number_of_seats, model, capacity, year_of_manufacture) VALUES
(100,'Boeing 737', 160, 2015),
(200,'Airbus A320', 180, 2017),
(300, 'Boeing 777', 396, 2013),
(400, 'Airbus A330', 277, 2016),
(500, 'Embraer E190', 106, 2018),
(50, 'Boeing 747', 416, 2010);
""")


myCursor.execute("""
INSERT INTO Flight (flight_number, departure_airport_id, arrival_airport_id, departure_date, departure_time, arrival_date, arrival_time, flight_duration, available_seats,  airplane_id, price) VALUES
('CAI123', 1, 3, '2024-12-17', '08:00:00', '2024-12-17', '11:00:00', '03:00:00', 100, 1, 300.50),
('JED234', 2, 1, '2024-12-18', '13:00:00', '2024-12-18', '14:32:00', '01:32:00', 200, 2, 200.00),
('DXB345', 3, 7, '2024-12-19', '10:00:00', '2024-12-19', '12:03:00', '02:03:00', 300, 3, 400.75),
('BEY456', 4, 9, '2024-12-25', '06:00:00', '2024-12-25', '08:28:00', '02:28:00', 400, 4, 250.00),

('DXB567', 5, 6, '2025-1-9', '12:00:00', '2025-1-9', '17:47:00', '05:47:00', 500, 5, 150.00),

('DOH567', 5, 6, '2025-1-10', '20:00:00', '2025-1-10', '21:47:00', '01:47:00', 500, 5, 150.00),
('RUH678', 7, 8, '2025-1-10', '15:00:00', '2025-1-10', '16:02:00', '01:02:00', 50, 6, 350.50),
('DXB111', 6, 5, '2025-1-15', '11:00:00', '2025-1-15', '13:04:00', '02:04:00', 50, 6, 405.50),


('CAI567', 1, 3, '2025-2-12', '09:00:00', '2025-2-12', '12:01:00', '03:01:00', 200, 2, 310.00),
('CAI890', 1, 3, '2025-2-12', '13:00:00', '2025-2-12', '16:02:00', '03:02:00', 300, 3, 320.50),
('CAI901', 1, 3, '2025-2-12', '17:00:00', '2025-2-12', '20:04:00', '03:04:00', 400, 4, 315.75),


('JED789', 3, 1, '2025-2-18', '14:00:00', '2025-2-18', '15:33:00', '01:33:00', 400, 4, 210.75),
('JED101', 3, 1, '2025-2-18', '17:00:00', '2025-2-18', '18:34:00', '01:34:00', 500, 5, 205.00),
('JED202', 3, 1, '2025-2-18', '20:00:00', '2025-2-18', '21:37:00', '01:37:00', 50, 6, 215.50),


('DXB222', 3, 7, '2025-1-20', '15:00:00', '2025-1-20', '17:02:00', '02:02:00', 100, 1, 400.00),
('DXB333', 3, 7, '2025-1-20', '19:00:00', '2025-1-20', '21:05:00', '02:05:00', 200, 2, 395.00),


('BEY333', 4, 9, '2025-1-22', '07:00:00', '2025-1-22', '09:34:00', '02:34:00', 200, 2, 260.50),
('BEY444', 4, 9, '2025-1-22', '12:00:00', '2025-1-22', '14:33:00', '02:33:00', 300, 3, 255.75),
('BEY555', 4, 9, '2025-1-22', '17:00:00', '2025-1-22', '19:31:00', '02:31:00', 400, 4, 250.25),


('DOH555', 9, 4, '2025-1-29', '21:00:00', '2025-1-29', '22:48:00', '01:48:00', 400, 4, 155.00),
('DOH666', 9, 4, '2025-1-29', '06:00:00', '2025-1-29', '07:46:00', '01:46:00', 500, 5, 152.25),
('DOH777', 9, 4, '2025-1-29', '10:00:00', '2025-1-29', '11:42:00', '01:42:00', 50, 6, 160.00),


('RUH777', 7, 8, '2025-2-5', '16:00:00', '2025-2-5', '17:03:00', '01:03:00', 50, 6, 355.00),
('RUH888', 7, 8, '2025-2-5', '19:00:00', '2025-2-5', '20:01:00', '01:01:00', 100, 1, 350.00),
('RUH999', 7, 8, '2025-2-5', '22:00:00', '2025-2-5', '23:02:00', '01:02:00', 200, 2, 345.75),


('CAI741', 3, 1, '2025-02-20', '13:00:00', '2025-2-20', '16:03:00', '03:03:00', 300, 3, 320.50),
('CAI951', 3, 1, '2025-02-20', '17:00:00', '2025-2-20', '20:02:00', '03:02:00', 400, 4, 315.75),
('JED669', 5, 2, '2025-02-22', '14:00:00', '2025-2-22', '15:34:00', '01:34:00', 400, 4, 210.75),
('JED781', 5, 2, '2025-02-22', '17:00:00', '2025-2-22', '18:35:00', '01:35:00', 500, 5, 205.00),
('JED632', 5, 2, '2025-02-23', '20:00:00', '2025-2-23', '21:37:00', '01:37:00', 50, 6, 215.50),
('DXB592', 7, 3, '2025-02-25', '11:00:00', '2025-2-25', '13:04:00', '02:04:00', 50, 6, 405.50),
('CAI124', 1, 2, '2025-02-19', '08:00:00', '2025-2-19', '10:00:00', '02:00:00', 100, 1, 150.00),
('JED235', 2, 3, '2025-02-20', '09:00:00', '2025-2-20', '11:15:00', '02:15:00', 200, 2, 200.00),
('DXB346', 3, 4, '2025-02-21', '07:30:00', '2025-2-21', '09:45:00', '02:15:00', 300, 3, 250.00),

('BEY457', 4, 5, '2025-03-22', '10:00:00', '2025-3-22', '12:30:00', '02:30:00', 400, 4, 300.00),
('DOH568', 5, 6, '2025-03-23', '14:00:00', '2025-3-23', '15:50:00', '01:50:00', 500, 5, 180.00),
('RUH679', 6, 7, '2025-03-24', '18:00:00', '2025-3-24', '19:45:00', '01:45:00', 50, 6, 220.00),
('CAI125', 1, 3, '2025-03-25', '08:30:00', '2025-3-25', '11:30:00', '03:00:00', 100, 1, 320.50),
('JED236', 2, 4, '2025-03-26', '09:00:00', '2025-3-26', '11:45:00', '02:45:00', 200, 2, 240.00),
('DXB347', 3, 5, '2025-03-27', '07:45:00', '2025-3-27', '10:00:00', '02:15:00', 300, 3, 270.00),
('BEY458', 4, 6, '2025-03-28', '12:00:00', '2025-3-28', '14:30:00', '02:30:00', 400, 4, 320.00),
('DOH569', 5, 7, '2025-04-29', '13:00:00', '2025-4-29', '14:50:00', '01:50:00', 500, 5, 210.00),
('RUH680', 6, 8, '2025-04-30', '15:00:00', '2025-4-30', '16:45:00', '01:45:00', 50, 6, 250.00),
('CAI126', 1, 9, '2025-04-30', '09:30:00', '2025-4-30', '12:30:00', '03:00:00', 100, 1, 350.50),



('JED237', 2, 10, '2025-01-13', '10:00:00', '2025-01-13', '12:30:00', '02:30:00', 200, 2, 360.00),
('DXB348', 3, 11, '2025-01-14', '08:45:00', '2025-01-14', '11:00:00', '02:15:00', 300 ,3, 300.00),
('BEY459', 4, 12, '2025-01-14', '14:00:00', '2025-01-14', '16:30:00', '02:30:00', 400 ,4, 350.00),
('DOH570', 5, 13, '2025-01-12', '12:00:00', '2025-01-12', '13:50:00', '01:50:00', 500 ,5, 260.00);


""")


myCursor.execute("""
INSERT INTO Passenger (passenger_ssn, first_name, last_name, date_of_birth, nationality, gender) 
VALUES
('223456785', 'Jane', 'Smith', '1985-03-25', 'Canadian', 'Female'),
('323456785', 'Ali', 'Khan', '1998-07-15', 'Pakistani', 'Male'),
('423456785', 'Sara', 'Ahmed', '1992-11-20', 'Egyptian', 'Female'),
('523456785', 'Carlos', 'Gomez', '1995-01-30', 'Mexican', 'Male'),
('623456785', 'Emma', 'Brown', '2000-09-10', 'British', 'Female'),
('823456785', 'Sophia', 'Li', '1993-04-18', 'Chinese', 'Female'),
('923456785', 'Ahmed', 'Hamadneh', '1997-08-22', 'Jordanian', 'Male'),
('723456785', 'Layla', 'Hussein', '2001-02-14', 'Lebanese', 'Female'),
(123456785, 'Ahmed', 'Hassan', '1990-05-15', 'Egyptian', 'Female'),
(123456786, 'Qasim', 'Batrawi', '1995-07-20', 'Palestinian', 'Male'),
(123456787, 'Mohammad', 'Yaseen',  '2020-07-20', 'Palestinian', 'Male');
""")


myCursor.execute( """ 
INSERT INTO Booking (booking_date, payment_status, total_amount, booking_status)
VALUES
('2024-12-01', 'Paid', 1041.50,'Active'),
('2024-12-02', 'Paid', 600.00,'Active'),
('2024-12-02', 'Paid', 210.75,'Active'),
('2025-01-01', 'Paid', 150.75, 'Active'),
('2024-12-28', 'Paid', 200.50, 'Active'),
('2024-12-15', 'Paid', 120.00, 'Cancelled'),
('2024-11-20', 'Paid', 300.25, 'Active'),
('2025-01-05', 'Paid', 100.00, 'Active'),
('2024-12-05', 'Paid', 180.00, 'Cancelled'),
('2025-01-06', 'Paid', 400.50, 'Active'),
('2025-01-07', 'Paid', 400.50, 'Active'),
('2025-01-08', 'Paid', 400.50, 'Active'),
('2024-11-25', 'Paid', 220.75, 'Active');
""")


myCursor.execute("""
INSERT INTO Bill (payment_date, payment_time, payment_method, amount, booking_id, flight_id, user_id, card_type, card_number, expiry_month, expiry_year, cvv, cardholder_name)
VALUES
('2025-01-01', '12:30:00', 'Credit Card', 150.75, 1, 1, 1, 'Visa', '4111111111111111', 12, 2025, '123', 'John Doe'),
('2025-01-02', '14:45:00', 'Credit Card', 200.50, 2, 2, 2, 'MasterCard', '5500000000000004', 11, 2024, '456', 'Jane Smith'),
('2025-01-03', '16:00:00', 'Debit Card', 120.00, 3, 3, 2, 'Visa', '4012888888881881', 10, 2026, '789', 'Ali Khan'),
('2025-01-04', '18:20:00', 'Credit Card', 175.00, 4, 4, 1, 'American Express', '378282246310005', 9, 2025, '321', 'Sara Ahmed'),
('2025-01-05', '09:10:00', 'Credit Card', 300.25, 5, 5, 2, 'Visa', '4111111111111111', 8, 2026, '654', 'Carlos Gomez'),
('2025-01-06', '11:00:00', 'Credit Card', 100.00, 6, 6, 2, 'MasterCard', '5105105105105100', 7, 2024, '987', 'Emma Brown'),
('2025-01-07', '13:30:00', 'Debit Card', 250.00, 7, 7, 1, 'Visa', '4012888888881881', 6, 2025, '654', 'Liam Ahmad'),
('2025-01-08', '15:15:00', 'Credit Card', 180.00, 8, 8, 2, 'American Express', '371449635398431', 5, 2025, '123', 'Sophia Li'),
('2025-01-09', '17:45:00', 'Credit Card', 400.50, 9, 9, 2, 'Visa', '4111111111111111', 4, 2026, '789', 'Ahmed Hamadneh'),
('2025-01-01', '12:30:00', 'Credit Card', 210.75, 3, 12, 3, 'Visa', '4111111111111111', 12, 2025, '123', 'Qasim'),
('2025-01-02', '14:45:00', 'Credit Card', 600.60, 2, 15, 3, 'MasterCard', '5500000000000004', 11, 2024, '456', 'Qasim'),
('2025-01-02', '14:45:00', 'Credit Card', 620.00, 1, 9, 3, 'MasterCard', '5500000000000004', 11, 2024, '456', 'Qasim'),
('2025-01-02', '14:45:00', 'Credit Card', 421.50, 1, 12, 3, 'MasterCard', '5500000000000004', 11, 2024, '456', 'Qasim');
        """)

myCursor.execute("""
INSERT INTO Passenger_Flight_Booking (passenger_ssn, flight_id, booking_id, ticket_id, is_deleted)
VALUES
(123456785, 10, 1, 100001, 0),
(123456785, 20, 2, 100002, 0),
(223456785, 15, 3, 100003, 0),
(223456785, 7, 4, 100004, 0),
(223456785, 13, 5, 100005, 0),
(323456785, 25, 6, 100006, 0),
(423456785, 30, 7, 100007, 0),
(423456785, 19, 8, 100008, 0),
(523456785, 1, 2, 100009, 0),
(623456785, 2, 1, 100010, 0),
(623456785, 14, 6, 100011, 0),
(723456785, 15, 9, 100012, 0),
(723456785, 22, 10, 100013, 0),
                 
(723456785, 12, 3, 100014,0),
(223456785, 15, 2, 100015,0),
(323456785, 15, 2, 100016,0),
(123456787, 15, 2, 100017,0),
(123456785, 9, 1, 100018,0),
(123456786, 9, 1, 100019,0),
(123456785, 12, 1, 100018,0),
(123456786, 12, 1, 100019,0),
                 
(723456785, 33, 3, 100020, 0); 
                 """)

myCursor.execute("""
INSERT INTO Passenger_User (passenger_ssn, user_id)
VALUES
(123456785, 3),
(123456786, 3),
(123456787, 3),
(723456785, 3),
(223456785, 3),
(323456785, 3);
    """)



myDB.commit()