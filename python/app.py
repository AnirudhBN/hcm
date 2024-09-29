import mysql.connector as py
from flask import Flask, render_template, request, redirect

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/employees', methods=['POST', 'GET'])
def employees():
    search_term = request.form.get('search_term')

    sql = "select e.employee_id, e.first_name, e.last_name, sc.status_text from employees e inner join status_codes sc on e.status_code = sc.status_code"
    if search_term:
        sql = sql + f" where e.first_name like '%{search_term}%' OR e.last_name like '%{search_term}%'"
    sql = sql + " ORDER BY e.employee_id"

    list = get_data(sql)

    return render_template('employees_list.html', employees = list, len = len(list), search_term = search_term or '')

@app.route('/upsert-employee', methods=['POST', 'GET'])
def upsert_employees():
    error = ''
    error_fields = []
    emp = {}
    
    if request.method == 'GET' and request.args.get('id') :
        sql = f"select employee_id, first_name, last_name, date_of_birth, date_of_joining, marital_status_code, status_code, phone_number, date_of_leaving from employees where employee_id = {request.args.get('id')}"
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
        else:
            error = f'Employee with ID {id} not found.'
    elif request.method == 'POST':
        emp['first_name'] = request.form.get('first_name')
        emp['last_name'] = request.form.get('last_name')
        emp['date_of_birth'] = request.form.get('date_of_birth')
        emp['date_of_joining'] = request.form.get('date_of_joining')
        emp['marital_status'] = request.form.get('marital_status')
        emp['status'] = request.form.get('status')
        emp['phone_number'] = request.form.get('phone_number')
        emp['date_of_leaving'] = request.form.get('date_of_leaving')

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

            if request.form.get('employee_id'):
                sql= f"UPDATE employees SET first_name = '{first_name}', last_name = '{last_name}', date_of_birth = '{date_of_birth}', date_of_joining = '{date_of_joining}', status_code = {status}, marital_status_code = {marital_status}"
                if not date_of_leaving:
                    sql = sql + f", date_of_leaving = NULL"
                else:
                    sql = sql + f", date_of_leaving = '{date_of_leaving}'"

                if phone_number:
                    sql = sql + f", phone_number = '{phone_number}'"
                sql = sql + f" WHERE employee_id = {request.form.get('employee_id')};"
            else:    
                sql= f"INSERT INTO employees (first_name, last_name, date_of_birth, date_of_joining, status_code, marital_status_code, phone_number) VALUES('{first_name}', '{last_name}', '{date_of_birth}', '{date_of_joining}', {status}, {marital_status}, '{phone_number}');"

            print(sql)            
            exec_sql(sql)
            return redirect("/employees")

    maritals = get_data("SELECT marital_status_code, marital_status_text FROM marital_status_codes")
    statuses = get_data("SELECT status_code, status_text FROM status_codes")

    if error_fields:
        error = 'Please enter a value for the following fields: ' + ", ".join(error_fields)
    return render_template('upsert_employee.html', maritals = maritals, maritals_len = len(maritals), statuses = statuses, statuses_len = len(statuses), error = error, emp=emp)

@app.route('/delete-employee', methods=['GET'])
def delete_employees():
    if request.args.get('id'):
        exec_sql(f"DELETE from employees where employee_id = {request.args.get('id')}")
        return redirect("/employees")

@app.route('/terminate-employee', methods=['GET'])
def terminate_employees():
    if request.args.get('id'):
        exec_sql(f"UPDATE employees SET status_code = 2, date_of_leaving = now() where employee_id = {request.args.get('id')}")
        return redirect("/employees")

if __name__ == '__main__':
    app.run(debug=True)



print(list)