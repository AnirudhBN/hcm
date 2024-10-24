import os
import mysql.connector as py
from flask import Flask, render_template, request, redirect, make_response, send_file
from upload import *


app = Flask(__name__)

def exec_sql(sql):
    con = py.connect(host='localhost',username='root',passwd='1234',database='hcm')
    cur = con.cursor()
    cur.execute(sql)
    con.commit()

def get_data(sql):
    con = py.connect(host='localhost',username='root',passwd='1234',database='hcm')
    cur = con.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    list = []
    for i in data:
        list.append(i)
    return list

@app.route('/logout', methods=['GET'])
def logout():
    resp = make_response(redirect("/"))
    resp.set_cookie('hcm', '', expires=0)
    return resp

@app.route('/', methods=['POST', 'GET'])
def index():
    error = ''
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        if user_id and password:
            list = get_data(f"SELECT password from users where user_id = '{user_id}'")
            if list and list[0][0] == password:
                resp = make_response(redirect("/employees"))
                resp.set_cookie('hcm', user_id)
                return resp
            else:
                error = "Incorrect user id and/or password."
        else:
            error = "Please enter login details."

    return render_template('index.html', error = error)

@app.route('/about', methods=['GET'])
def about():
        basedir = os.path.abspath(os.path.dirname(__file__))
        about_file_path = os.path.join(basedir, 'static/about/about.txt')
        content = []
        about_file = open(about_file_path,"r")
        for line in about_file.readlines():
            content.append(line.rstrip('\n'))

        return render_template('about.html', content = content, len=len(content))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not request.cookies.get('hcm') or request.cookies.get('hcm') != 'admin':
        return redirect("/");

    message = None
    error = None
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        if user_id and password:
            list = get_data(f"SELECT 1 from users WHERE user_id = '{user_id}'")
            if list:
                error = "Username already taken!"
            else:
                sql = f"INSERT INTO users(user_id, password) values ('{user_id}', '{password}')"
                exec_sql(sql)
                message = f'User Id {user_id} created successfully.'
        else:
            file = request.files['file']
            if file:
                file.save(file.filename)
                process_upload(file.filename)
                os.remove(file.filename)
                return redirect("/employees")



    return render_template('admin.html', error = error, message = message)


@app.route('/employees', methods=['POST', 'GET'])
def employees():
    if not request.cookies.get('hcm'):
        return redirect("/");

    search_term = request.form.get('search_term')
    status_filter = request.form.get('status_filter')
    titles_filter = request.form.get('titles_filter')
    managers_filter = request.form.get('managers_filter')
    order_by = request.form.get('order_by')

    sql = "select e.employee_id, e.first_name, e.last_name, e.job_title, sc.status_text, COALESCE(CONCAT(m.first_name, ' ', m.last_name), ' ') as manager_name, e.phone_number, DATE_FORMAT(e.date_of_birth, '%d-%m-%Y') as date_of_birth, DATE_FORMAT(e.date_of_joining, '%d-%m-%Y') as date_of_joining, TIMESTAMPDIFF(YEAR, e.date_of_joining, CURDATE()) as experience from employees e inner join status_codes sc on e.status_code = sc.status_code"
    sql = sql + " left join employees m on e.manager_id = m.employee_id where 1 = 1"
    if search_term:
        sql = sql + f" AND (e.first_name like '%{search_term}%' OR e.last_name like '%{search_term}%' OR e.phone_number like '%{search_term}%' OR e.employee_id like '%{search_term}%')"
    if status_filter:
        sql = sql + f" AND e.status_code = {status_filter}"
    if titles_filter:
        sql = sql + f" AND e.job_title = '{titles_filter}'"
    if managers_filter:
        sql = sql + f" AND m.employee_id = {managers_filter}"
    if order_by:
        if order_by == '0':
            sql = sql + " ORDER BY e.date_of_joining ASC"
        else:
            sql = sql + " ORDER BY e.date_of_joining DESC"
    else:
        sql = sql + " ORDER BY e.employee_id"
    print(sql)
    list = get_data(sql)
    statuses = get_data("SELECT status_code, status_text FROM status_codes")
    titles = get_data("SELECT DISTINCT job_title from employees where job_title is not null")
    managers = get_data("select DISTINCT m.employee_id, CONCAT(m.first_name, ' ', m.last_name) from employees e INNER JOIN employees m ON e.manager_id = m.employee_id")
    
    if request.form.get('export') and request.form.get('export') == "Export":
        basedir = os.path.abspath(os.path.dirname(__file__))
        file_path = os.path.join(basedir, 'static/export.csv')
        if os.path.exists(file_path):
            os.remove(file_path)
        about_file = open(file_path,"w")
        if list:
            about_file.write("Id, First Name, Last Name, Title, Status, Phone\n")
        for record in list:
            csv = f"{record[0]},{record[1]},{record[2]},{record[3]},{record[4]},{record[6] or ''}\n"
            about_file.write(csv)
        about_file.close()
        return send_file(file_path, as_attachment=True, download_name='export.csv')

    return render_template('employees_list.html', employees = list, len = len(list), search_term = search_term or '', statuses = statuses, statuses_len = len(statuses), titles = titles, titles_len = len(titles), managers = managers, managers_len = len(managers), status_filter = status_filter or '999999999', order_by = order_by or 99999, titles_filter = titles_filter or '', managers_filter = managers_filter or '')

# GET - Blank
# GET - with id
# POST - INSERT
# POST - UPDATE
@app.route('/upsert-employee', methods=['POST', 'GET'])
def upsert_employees():
    if not request.cookies.get('hcm'):
        return redirect("/");

    error = ''
    error_fields = []
    emp = {}
    
    if request.method == 'GET' and request.args.get('id') :
        sql = f"select employee_id, first_name, last_name, date_of_birth, date_of_joining, marital_status_code, status_code, phone_number, date_of_leaving, manager_id, job_title, job_location, cost_to_company from employees where employee_id = {request.args.get('id')}"
        list = get_data(sql)
        if list:
            emp['employee_id'] = list[0][0]
            emp['first_name'] = list[0][1]
            emp['last_name'] = list[0][2]
            emp['date_of_birth'] = list[0][3]
            emp['date_of_joining'] = list[0][4]
            emp['marital_status'] = list[0][5]
            emp['status'] = list[0][6]
            emp['phone_number'] = list[0][7]
            emp['date_of_leaving'] = list[0][8]
            emp['manager'] = list[0][9]

            emp['job_title'] = list[0][10]
            emp['job_location'] = list[0][11]
            emp['cost_to_company'] = list[0][12]
        else:
            error = f"Employee with ID {request.args.get('id')} not found."
    elif request.method == 'POST':
        emp['first_name'] = request.form.get('first_name')
        emp['last_name'] = request.form.get('last_name')
        emp['date_of_birth'] = request.form.get('date_of_birth')
        emp['date_of_joining'] = request.form.get('date_of_joining')
        emp['marital_status'] = request.form.get('marital_status')
        emp['status'] = request.form.get('status')
        emp['phone_number'] = request.form.get('phone_number')
        emp['date_of_leaving'] = request.form.get('date_of_leaving')
        emp['manager'] = request.form.get('manager')
        emp['job_title'] = request.form.get('job_title')
        emp['job_location'] = request.form.get('job_location')
        emp['cost_to_company'] = request.form.get('cost_to_company')

        if not emp['first_name']:
            error_fields.append('First Name')
        if not emp['last_name']:
            error_fields.append('Last Name')
        if not emp['date_of_birth']:
            error_fields.append('Date of Birth')
        if not emp['date_of_joining']:
            error_fields.append('Date of Joining')
        if not emp['marital_status']:
            error_fields.append('Marital Status')
        
        if not error_fields:
            first_name = emp['first_name']
            last_name = emp['last_name']
            date_of_birth = emp['date_of_birth']
            date_of_joining = emp['date_of_joining']
            marital_status = emp['marital_status']
            status = emp['status']
            phone_number = emp['phone_number']
            date_of_leaving = emp['date_of_leaving']
            manager = emp['manager']
            job_title = emp['job_title']
            job_location = emp['job_location']
            cost_to_company = emp['cost_to_company']

            if request.form.get('employee_id'):
                sql= f"UPDATE employees SET first_name = '{first_name}', last_name = '{last_name}', date_of_birth = '{date_of_birth}', date_of_joining = '{date_of_joining}', status_code = {status}, marital_status_code = {marital_status}"
                if date_of_leaving:
                    sql = sql + f", date_of_leaving = '{date_of_leaving}'"
                else:
                    sql = sql + f", date_of_leaving = NULL"

                if phone_number:
                    sql = sql + f", phone_number = '{phone_number}'"
                else:
                    sql = sql + f", phone_number = NULL"

                if manager:
                    sql = sql + f", manager_id = '{manager}'"
                else:
                    sql = sql + f", manager_id = NULL"

                if job_title:
                    sql = sql + f", job_title = '{job_title}'"
                else:
                    sql = sql + f", job_title = NULL"

                if job_location:
                    sql = sql + f", job_location = '{job_location}'"
                else:
                    sql = sql + f", job_location = NULL"

                if cost_to_company:
                    sql = sql + f", cost_to_company = {cost_to_company}"
                else:
                    sql = sql + f", cost_to_company = NULL"

                sql = sql + f" WHERE employee_id = {request.form.get('employee_id')};"
            else:    
                sql= f"INSERT INTO employees (first_name, last_name, date_of_birth, date_of_joining, status_code, marital_status_code"
                if phone_number:
                    sql = sql + f", phone_number"
                if manager:
                    sql = sql + f", manager_id"
                if job_title:
                    sql = sql + f", job_title"
                if job_location:
                    sql = sql + f", job_location"
                if cost_to_company:
                    sql = sql + f", cost_to_company"

                sql = sql + f") VALUES('{first_name}', '{last_name}', '{date_of_birth}', '{date_of_joining}', {status}, {marital_status}"
                if phone_number:
                    sql = sql + f", '{phone_number}'"
                if manager:                    
                    sql = sql + f", {manager}"
                if job_title:                    
                    sql = sql + f", '{job_title}'"
                if job_location:                    
                    sql = sql + f", '{job_location}'"
                if cost_to_company:                    
                    sql = sql + f", {cost_to_company}"

                sql = sql + ");"
            print(">>>>>>>", sql)            
            exec_sql(sql)
            return redirect("/employees")

    maritals = get_data("SELECT marital_status_code, marital_status_text FROM marital_status_codes")
    statuses = get_data("SELECT status_code, status_text FROM status_codes")
    managers = get_data("SELECT employee_id as manager_id, CONCAT(first_name, ' ', last_name) as manager_name FROM employees")

    if error_fields:
        error = 'Please enter a value for the following fields: ' + ", ".join(error_fields)
    return render_template('upsert_employee.html', maritals = maritals, maritals_len = len(maritals), statuses = statuses, statuses_len = len(statuses), error = error, emp=emp, managers = managers, managers_len = len(managers))

@app.route('/delete-employee', methods=['GET'])
def delete_employees():
    if not request.cookies.get('hcm'):
        return redirect("/");

    if request.args.get('id'):
        exec_sql(f"DELETE from employees where employee_id = {request.args.get('id')}")
        return redirect("/employees")

@app.route('/terminate-employee', methods=['GET'])
def terminate_employees():
    if not request.cookies.get('hcm'):
        return redirect("/");

    if request.args.get('id'):
        exec_sql(f"UPDATE employees SET status_code = 2, date_of_leaving = now() where employee_id = {request.args.get('id')}")
        return redirect("/employees")

if __name__ == '__main__':
    app.run(debug=True)



print(list)