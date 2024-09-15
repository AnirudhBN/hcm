create database hcm;

use hcm;

create table employees(
	employee_id INT PRIMARY KEY,
	first_name CHAR(50) NOT NULL,
	last_name CHAR(50) NOT NULL,
	date_of_birth DATE NOT NULL,
	date_of_joining DATE NOT NULL,
	manager_id INT REFERENCES employees(employee_id),
	date_of_leaving DATE,
	status_code INT NOT NULL REFERENCES status_codes(status_code),
	marital_status_code INT NOT NULL REFERENCES marital_status_codes(marital_status_code)
    );

create table status_codes(
	status_code INT PRIMARY KEY,
	status_text VARCHAR(20) NOT NULL
);

create table marital_status_codes(
	marital_status_code INT PRIMARY KEY,
	marital_status_text VARCHAR(20) NOT NULL
);

create table job_details(
	job_id INT PRIMARY KEY,
	job_title VARCHAR(50) NOT NULL,
	job_location VARCHAR(100) NOT NULL,
	cost_to_company INT NOT NULL,
	employee_id INT NOT NULL REFERENCES employees(employee_id)
);

create table address_details(
	adress_id INT PRIMARY KEY,
	employee_id INT NOT NULL REFERENCES employees(employee_id),
	adress_line1 VARCHAR(100) NOT NULL,
	adress_line2 VARCHAR(100),
	city VARCHAR(50) NOT NULL,
	state VARCHAR(50) NOT NULL,
	pincode VARCHAR(6) NOT NULL
);
