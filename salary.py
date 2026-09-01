from flask import Flask, render_template, request, flash, redirect, url_for
import calendar
from datetime import datetime

app = Flask(__name__)
app.secret_key = "compact_payroll_secret"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-invoice', methods=['POST'])
def generate_invoice():
    try:
        month_name = request.form.get('month', '').strip().capitalize()
        year = int(request.form.get('year', datetime.today().year))
        base_salary = float(request.form.get('salary') or 0)
        employee_name = request.form.get('employee_name', 'Employee').strip()

        datetime_object = datetime.strptime(month_name, "%B")
        month_num = datetime_object.month

        # Find total days in month
        total_days = calendar.monthrange(year, month_num)[1]

        attendance_list = []
        leaves_count = 0
        day_shift = 0
        night_shift = 0
        T_double_shift = 0
        weekoffs_count = 0

        for day in range(1, total_days + 1):
            status = request.form.get(f'status_{day}', 'P')
            if status == 'A':
                leaves_count += 1
            elif status == 'NS':
                night_shift += 1
            elif status == 'DS':
                day_shift += 1
            elif status == 'BS':
                T_double_shift += 2
            elif status == 'W':
                weekoffs_count += 1

            attendance_list.append({
                "sr_no": day,
                "status": status
            })
        all_day = (day_shift+night_shift)+T_double_shift
        payable_days = all_day
        double_shift = T_double_shift//2
        daily_rate = base_salary / total_days
        final_salary = daily_rate * payable_days

        invoice_data = {
            "employee_name": employee_name,
            "period": f"{month_name} {year}",
            "total_days": total_days,
            "total_day_shift": day_shift,
            "total_night_shift": night_shift,
            "total_double_shift": double_shift,
            "weekoffs": weekoffs_count,
            "leaves": leaves_count,
            "payable_days": payable_days,
            "base_salary": round(base_salary, 2),
            "final_salary": round(final_salary, 2),
            "invoice_date": datetime.today().strftime('%Y-%m-%d'),
            "attendance": attendance_list
        }

        return render_template('invoice.html', invoice=invoice_data)

    except ValueError as e:
        flash(f"Error: {str(e)}")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
