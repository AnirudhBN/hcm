create database hcm;

use hcm;

create table employees(
	employee_id INT PRIMARY KEY AUTO_INCREMENT,
	first_name VARCHAR(50) NOT NULL,
	last_name VARCHAR(50) NOT NULL,
	date_of_birth DATE NOT NULL,
	date_of_joining DATE NOT NULL,
	manager_id INT REFERENCES employees(employee_id),
	date_of_leaving DATE,
	status_code INT NOT NULL REFERENCES status_codes(status_code),
	marital_status_code INT NOT NULL REFERENCES marital_status_codes(marital_status_code),
	phone_number VARCHAR(10),
	job_title VARCHAR(50),
	job_location VARCHAR(100),
	cost_to_company INT
    );

ALTER TABLE employees AUTO_INCREMENT=10001;

create table status_codes(
	status_code INT PRIMARY KEY,
	status_text VARCHAR(20) NOT NULL
);

create table marital_status_codes(
	marital_status_code INT PRIMARY KEY,
	marital_status_text VARCHAR(20) NOT NULL
);


create table users(
	user_id VARCHAR(50) PRIMARY KEY,
	password VARCHAR(50) NOT NULL
);

INSERT INTO users VALUES ('admin', 'password')

INSERT INTO status_codes(status_code, status_text) VALUES (0, 'Inactive');
INSERT INTO status_codes(status_code, status_text) VALUES (1, 'Active');
INSERT INTO status_codes(status_code, status_text) VALUES (2, 'Leaver');

INSERT INTO marital_status_codes(marital_status_code, marital_status_text) VALUES (1, 'Single');
INSERT INTO marital_status_codes(marital_status_code, marital_status_text) VALUES (2, 'Married');
INSERT INTO marital_status_codes(marital_status_code, marital_status_text) VALUES (3, 'Divorced');



INSERT INTO employees (first_name, last_name, date_of_birth, date_of_joining, status_code, marital_status_code)
VALUES('Roman', 'Reins', '2008-01-01', '2014-3-21', 1, 1);

INSERT INTO employees (first_name, last_name, date_of_birth, date_of_joining, status_code, marital_status_code)
VALUES('Steve', 'Austin', '2014-02-02', '2016-3-21', 1, 1);

INSERT INTO employees (first_name, last_name, date_of_birth, date_of_joining, status_code, marital_status_code)
VALUES('Dwayne', 'Johnson', '1978-03-03', '2000-3-21', 1, 2);

INSERT INTO employees (first_name, last_name, date_of_birth, date_of_joining, status_code, marital_status_code)
VALUES('Brock', 'Lesner', '1980-04-04', '2002-3-21', 2, 2);

