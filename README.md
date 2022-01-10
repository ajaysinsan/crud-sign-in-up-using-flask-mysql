# My Flask APP

 CRUD in Flask using MySQL DB

## Clone

Clone the repo to your system

```bash
git clone https://github.com/ajaysinsan/crud-sign-in-up-using-flask-mysql.git
```

## Installation

Create a virtual environment to run the project:

```bash
python3 -m venv venv
```


activate the virtual environment:

```bash
source venv/bin/activate
```

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dependencies.

```bash
pip install -r requirements.txt
```


## Setup MySQL Database

Create a new database and create two tables named users and articles:

```bash
create table users( id int(11) auto_increment primary key,
name varchar(100), email varchar(100),username varchar(30),
register_date timestamp default current_timestamp);


create table articles( id int(11) auto_increment primary key, title varchar(255), author varchar(100), content text, created_at timestamp default current_timestamp);
```

Add DB config to app.py

## Running Project

Change your directory to project directory and run the following command:

```python
python app.py 
```

## Usage
Please navigate to http://localhost:5000.
