from flask import Flask, render_template, abort
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from contextlib import closing
import os

app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Raziya#1176',
    'database': 'employeeDatabase'
}

if not os.path.exists('static'):
    os.makedirs('static')

def create_top_performers_chart(df):
    plt.figure(figsize=(8,5))
    sns.barplot(x='performance_score', y='emp_name', data=df, palette='Blues_d')
    plt.title('Top Performers')
    plt.xlabel('Performance Score')
    plt.ylabel('Employee Name')
    plt.tight_layout()
    plt.savefig('static/top_performers.png')
    plt.close()

def create_avg_salary_chart(df):
    plt.figure(figsize=(8,5))
    sns.barplot(x='department', y='avg_salary', data=df, palette='Greens_d')
    plt.title('Average Salary by Department')
    plt.xlabel('Department')
    plt.ylabel('Average Salary')
    plt.tight_layout()
    plt.savefig('static/avg_salary.png')
    plt.close()

def create_salary_perf_chart(df):
    plt.figure(figsize=(8,5))
    sns.scatterplot(x='salary', y='performance_score', data=df, hue='performance_score', palette='coolwarm', legend=False)
    plt.title('Salary vs Performance')
    plt.xlabel('Salary')
    plt.ylabel('Performance Score')
    plt.tight_layout()
    plt.savefig('static/salary_vs_performance.png')
    plt.close()

def create_hiring_trends_chart(df):
    plt.figure(figsize=(8,5))
    sns.lineplot(x='hire_year', y='hires', data=df, marker='o')
    plt.title('Employee Hiring Trends by Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Hires')
    plt.tight_layout()
    plt.savefig('static/hiring_trends.png')
    plt.close()

@app.route('/')
def dashboard():
    with closing(mysql.connector.connect(**db_config)) as conn:
        top_performers = pd.read_sql('''
            SELECT emp_id, emp_name, performance_score 
            FROM employee 
            ORDER BY performance_score DESC 
            LIMIT 5;
        ''', conn)

        avg_salary = pd.read_sql('''
            SELECT department, AVG(salary) as avg_salary 
            FROM employee 
            GROUP BY department;
        ''', conn)

        salary_perf = pd.read_sql('''
            SELECT salary, performance_score
            FROM employee;
        ''', conn)

        hiring_trends = pd.read_sql('''
            SELECT YEAR(hire_date) AS hire_year, COUNT(*) AS hires
            FROM employee
            GROUP BY hire_year
            ORDER BY hire_year;
        ''', conn)

    create_top_performers_chart(top_performers)
    create_avg_salary_chart(avg_salary)
    create_salary_perf_chart(salary_perf)
    create_hiring_trends_chart(hiring_trends)

    top_perf_list = top_performers.to_dict(orient='records')

    return render_template(
        'dashboard.html',
        top_perf_img='top_performers.png',
        avg_salary_img='avg_salary.png',
        salary_perf_img='salary_vs_performance.png',
        hiring_trends_img='hiring_trends.png',
        top_performers=top_perf_list
    )

@app.route('/employee/<int:emp_id>')
def employee_profile(emp_id):
    with closing(mysql.connector.connect(**db_config)) as conn:
        query = "SELECT * FROM employee WHERE emp_id = %s"
        employee = pd.read_sql(query, conn, params=(emp_id,))

    if employee.empty:
        abort(404)

    emp = employee.iloc[0].to_dict()

    return render_template('employee_profile.html', employee=emp)

if __name__ == '__main__':
    app.run(debug=True)
