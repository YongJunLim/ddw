from flask import Flask, render_template, request, url_for, redirect, flash
from model import Database, RegressionModel
from datetime import datetime

app = Flask(__name__)
database = Database()
app.secret_key = b'iloveDDW'

database.create_db()
model = RegressionModel()


@app.route('/', methods=["GET"])
def index():
    """
    Render the index page.

    Returns:
        HTML template for the index page.
    """
    if request.method == "GET":
        return render_template('index.html', request=request)


@app.route('/add/', methods=["GET", "POST"])
def add():
    """
    Handle GET and POST requests for the add page.

    GET: Render the add page.
    POST: Process form submission, validate numeric input, predict amount of food wasted, and insert data into the database.

    Returns:
        Redirects to the add page on error, or the view page on success.
    """
    if request.method == "GET":
        return render_template('add.html', request=request)
    elif request.method == "POST":
        formdata = dict(request.form)
        try:
            guestno = int(formdata.get('guestno', '').strip())
            serveno = int(formdata.get('serveno', '').strip())
            price = float(formdata.get('price', '').strip())
            prep = int(formdata.get('prep', '').strip())
            regular = int(formdata.get('regular', '').strip())
        except ValueError:
            flash("Invalid input: please enter valid numbers.", "error")
            return redirect(url_for('add'))
        if guestno <= 0 or serveno <= 0 or price <= 0 or prep < 0 or regular < 0:
            flash("Values must be positive numbers.", "error")
            return redirect(url_for('add'))

        if guestno == 0 or serveno == 0:
            predicted_val = 0
        else:
            predicted_val = model.predict_val(formdata)
        if predicted_val < 0:
            predicted_val = 0

        dt = datetime.now()
        epoch = int(dt.timestamp())
        formatted_dt = dt.strftime("%B %d, %Y %I:%M %p")

        res = [
            epoch,
            formdata['guestno'],
            formdata['serveno'],
            formdata['price'],
            formdata['prep'],
            formdata['regular'],
            predicted_val,
            formatted_dt
        ]

        database.insert(res)
        flash('Data added successfully!', 'success')
        return redirect('/view')


@app.route('/view/', methods=["GET", "POST"])
def view():
    """
    Render the view page with data from the database.

    Returns:
        HTML template for the view page with database items.
    """
    if request.method == "GET":
        vals = database.get()
        print(vals)
        return render_template('view.html', items=vals, request=request)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)