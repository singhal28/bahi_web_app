from flask import Flask, render_template, request, redirect, url_for,session,jsonify,send_file,flash
from database import get_users, get_user_by_email, get_ledger_accounts, add_transaction
from dbConnector import connectToS2MS,db_con,get_connection
from datetime import date
import pandas as pd
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'keep it secret, keep it safe'


# Simulate a database (for simplicity)
users_db = get_users()
ledger_accounts_db = get_ledger_accounts()

# Route for Login
@app.route('/')
def login():
    return render_template('login.html')

# Handle Login POST request
@app.route('/login', methods=['POST'])
def login_post():
    # *** LOGIN ***
    # Retrieve user with email
    s2ms = connectToS2MS('db_web_app')
    query = "SELECT * FROM users WHERE email = %(email)s;"
    data = {"email" : request.form['email']}
    CurrUser = s2ms.query_db(query, data)
    if CurrUser == ():
        logerror = "This email has not been registered. Please register or try again!"
        return render_template('index.html', logerror = logerror)
    else:
        # check password
        if CurrUser[0]["password"] != request.form['PwToCheck'] :
            logerror = "The password is incorrect - please try again!"
            return render_template('index.html', logerror = logerror)
    
        # Set this user's id in session before redirecting
        session['userId'] = CurrUser[0]['userId']
        print(session['userId'])
        return redirect("/dashboard")
    

def func_getCurrUser(CurrSessionId):
   

    # *** DASHBOARD 1 ***
    # Retrieve Current User
    print("retrieving user --- ",CurrSessionId)
    s2ms = connectToS2MS('db_web_app')
    query = "select * from users where userId = %(curruserid)s;"
    data = {"curruserid" : CurrSessionId}
    # print ('Data is ---------- > ',data)
    CurrUser = s2ms.query_db(query, data)

    return CurrUser

# Dashboard Route
@app.route('/dashboard')
def dashboard():
     
    CurrSessionId = str(session['userId'])

    CurrUser = func_getCurrUser(CurrSessionId)
        
    # *** DASHBOARD 2 ***
    # Retrieve Current User's ToDos
    print("retriving todos")
    s2ms = connectToS2MS('db_web_app')
    query = "SELECT * FROM products WHERE userId = %(userid)s;"
    data = {"userid" : CurrSessionId}
    AllProducts = s2ms.query_db(query, data)
    
    s2ms = connectToS2MS('db_web_app')
    query_customer = "SELECT * FROM customers WHERE userId = %(userid)s;"
    data_customers = {"userid" : CurrSessionId}
    Allcustomers = s2ms.query_db(query_customer, data_customers)

    s2ms = connectToS2MS('db_web_app')
    query_sales_today = "SELECT sum(totalAmount) as today_sales FROM sales WHERE userId = %(userid)s and salesDate = curdate();"
    data_customers = {"userid" : CurrSessionId}
    today_sales = s2ms.query_db(query_sales_today, data_customers)
    
    # print ('------------- ', today_sales[0]['today_sales'])

    s2ms = connectToS2MS('db_web_app')
    query_sales_total = "SELECT sum(totalAmount) as total_sales FROM sales WHERE userId = %(userid)s;"
    data_customers = {"userid" : CurrSessionId}
    total_sales = s2ms.query_db(query_sales_total, data_customers)
    
    product_row_count = 0
    product_row_count = len(AllProducts)
    customer_row_count = 0
    customer_row_count = len(Allcustomers)
    
    # print ('----------  ',row_count)
    
    return render_template('dashboard.html', CurrUser = CurrUser, dynamic_products = product_row_count,dynamic_customers = customer_row_count,today_sales= today_sales[0]['today_sales'],total_sales=total_sales[0]['total_sales'])

@app.route('/logout') 
def logout():
    session.clear()
    return redirect("/")


@app.route('/addProductRender') 
def addProductRender(regerror=''):
    CurrSessionId = str(session['userId'])
    
    CurrUser = func_getCurrUser(CurrSessionId)

    print("retriving todos")
    s2ms = connectToS2MS('db_web_app')
    query = "SELECT * FROM products WHERE userId = %(userid)s;"
    data = {"userid" : CurrSessionId}
    AllProducts = s2ms.query_db(query, data)
    # print('========== > ',AllProducts)
    return render_template('addProduct.html', CurrUser = CurrUser,AllProducts = AllProducts,regerror=regerror)


@app.route('/addProduct', methods=['POST'])
def addProduct():
    print("sdasdadadasd")
    if request.form['productName'] == '' :
        todoerror = "Please include all required fields."
    else :
        # *** CREATE TODO ***
        # Create New ToDo
        query_check = "select * from products where productName = %(productName)s and userId = %(userId)s;"
        data = {
            "productName" : request.form['productName'],
            "userId" : session['userId']
        }
        s2ms = connectToS2MS('db_web_app')
        UserExist = s2ms.query_db(query_check, data)
        if UserExist==():
            s2ms = connectToS2MS('db_web_app')
            query = "INSERT INTO products (productName, userId) VALUES (%(productName)s, %(userId)s);"
            CurrUser = s2ms.query_db(query, data)
            
    return redirect("/addProductRender")

                
    


@app.route('/delete/<productid>') 
def delete(productid):
    # *** DELETE TODO ***
    # Delete Todo
    s2ms = connectToS2MS('db_web_app')
    query = "DELETE FROM products WHERE productId = %(productid)s;"
    print('==================== ',query)
    data = {"productid" : productid}
    s2ms.query_db(query, data)

    return redirect("/addProductRender")

@app.route('/addCustomerRender') 
def addCustomerRender(regerror=''):
    CurrSessionId = str(session['userId'])
    
    CurrUser = func_getCurrUser(CurrSessionId)

    print("retriving todos")
    s2ms = connectToS2MS('db_web_app')
    query = "SELECT * FROM customers WHERE userId = %(userid)s;"
    data = {"userid" : CurrSessionId}
    AllCustomers = s2ms.query_db(query, data)
    # print('========== > ',AllProducts)
    return render_template('addCustomer.html', CurrUser = CurrUser,AllCustomers = AllCustomers,regerror=regerror)


@app.route('/addCustomer', methods=['POST'])
def addCustomer():
    print("sdasdadadasd")
    if request.form['customerName'] == '' :
        todoerror = "Please include all required fields."
    else :
        # *** CREATE TODO ***
        # Create New ToDo
        query_check = "select * from customers where customerName = %(customerName)s and userId = %(userId)s and customerContact = %(customerContact)s;"
        data = {
            "customerName" : request.form['customerName'],
            "customerContact" : request.form['customerContact'],
            "customerAddress" : request.form['customerAddress'],
            "userId" : session['userId']
        }
        s2ms = connectToS2MS('db_web_app')
        UserExist = s2ms.query_db(query_check, data)
        if UserExist==():
            s2ms = connectToS2MS('db_web_app')
            query = "INSERT INTO customers (customerName,customerContact,customerAddress, userId) VALUES (%(customerName)s, %(customerContact)s,%(customerAddress)s, %(userId)s);"
            CurrUser = s2ms.query_db(query, data)
            
    return redirect("/addCustomerRender")

                
    


@app.route('/delete_customer/<customerid>') 
def delete_customer(customerid):
    # *** DELETE TODO ***
    # Delete Todo
    s2ms = connectToS2MS('db_web_app')
    query = "DELETE FROM customers WHERE customerId = %(customerid)s;"
    print('==================== ',query)
    data = {"customerid" : customerid}
    s2ms.query_db(query, data)

    return redirect("/addCustomerRender")


def funcMasterOptions(master_is):
    CurrSessionId = str(session['userId'])
    if master_is == 'product':
       query = "select productId as id,productName as name FROM products where userId = %(userid)s;"    
    else:
        query = "select customerId as id,concat(customerName, ' - ', customerAddress) as name FROM customers where userId = %(userid)s;"

    s2ms = connectToS2MS('db_web_app')
    print('==================== ',query)
    data = {"userid" : CurrSessionId}
    query_Output= s2ms.query_db(query, data)
    print("Master data is ======== > ",query_Output)
    return query_Output

@app.route("/addLedgerRender", methods=["GET", "POST"])
def addLedgerRender():
    CurrSessionId = str(session['userId'])
    
    CurrUser = func_getCurrUser(CurrSessionId)
    options_customer = funcMasterOptions('customer')
    today = date.today().strftime('%Y-%m-%d')

    if request.method == "POST":
        selected_options = request.form.getlist("choices")
        return f"Selected options: {', '.join(selected_options)}"
    return render_template("ledger.html",CurrUser = CurrUser,customers=options_customer,today = today)

@app.route("/getProductOptions", methods=["GET"])
def getProductOptions():
    options_product = funcMasterOptions('product')
    return jsonify(options_product)

def funcSubmitSales(customer,date,selected_options,input_data,paymentMode_value):
    CurrSessionId = int(session['userId'])
    query = "select customerId as id FROM customers where concat(customerName, ' - ', customerAddress) = '{}' and userId = {};".format(customer,CurrSessionId)
    s2ms = connectToS2MS('db_web_app')
    #data = {"userid" : CurrSessionId}
    query_Output= s2ms.query_db(query)


    product_id,product_qty,product_amount,amount_total = [],[],[],[]

    input_data = {}
    for option in selected_options:
        input_data[option] = {
            'input1': request.form.get(f'input1_{option}', ''),
            'input2': request.form.get(f'input2_{option}', '')
        }

    for key, values in input_data.items():
        product_id.append(int(key))
        product_qty.append(float(values['input1']))
        product_amount.append(float(values['input2']))
    
    # print('###################  ',query_Output['id'])

    amount_total = [qty * amount for qty, amount in zip(product_qty, product_amount)]

    df_sales = pd.DataFrame({'customerId':int(query_Output[0]['id']),'productId':product_id,'productQty':product_qty,'productAmount':product_amount,'totalAmount':amount_total,'salesDate':date,'userId':CurrSessionId,'paymentMode':paymentMode_value})

    print (df_sales)

    conn = db_con('db_web_app')
    df_sales.to_sql(name='sales',con=conn,if_exists='append',index=False)


@app.route('/ledgerSubmit', methods=['POST'])
def ledgerSubmit():
    # Get selected options from the form (choices)
    selected_options = request.form.getlist('choices')
    print("&&&&&&&&&&&&&&&&&&&",selected_options)
    # Collect input data for each selected option
    input_data = {}
    for option in selected_options:
        input_data[option] = {
            'input1': request.form.get(f'input1_{option}', ''),
            'input2': request.form.get(f'input2_{option}', '')
        }
    
    # Get the total sum
    total_sum = request.form.get('total_sum', '0')
    customer = request.form.get('customerSearch', '')
    paymentMode = request.form.get('paymentMode', '')
    date = request.form.get('datePicker', '')
    # Process the form data (e.g., save to database, calculate, etc.)'
    paymentMode_value=0

    print(f"Customer: {customer}")
    print(f"Date: {date}")
    print(f"Selected Options ================> : {selected_options}")
    print(f"Input Data ==============> : {input_data}")
    print(f"Total Sum ============> : {total_sum}")
    print(f"Payment Mode ============> : {paymentMode}")

    if paymentMode.lower == 'cash':
        paymentMode_value = 0
    else:
        paymentMode_value = 1
    
    # Example of returning a JSON response
    funcSubmitSales(customer,date,selected_options,input_data,paymentMode_value)

    return jsonify({
        "status": "success",
        "message": "Form submitted successfully",
        "customer": customer,
        "date": date,
        "selected_options": selected_options,
        "input_data": input_data,
        "total_sum": total_sum
    })
    # return redirect("/addLedgerRender")


@app.route('/report', methods=['GET'])
def report():
    # Get filters
    CurrSessionId = str(session['userId'])
    engine = db_con('db_web_app')
    customer_id = request.args.get("customerId", "")
    start_date = request.args.get("startDate", "")
    end_date = request.args.get("endDate", "")
    page = int(request.args.get("page", 1))
    payment_mode = request.args.get("paymentMode", None)
    per_page = 10

    # Build SQL query
    query = """
        SELECT 
            salesId,
            concat(customers.customerName, ' - ',customers.customerAddress ) customerName,
            products.productName as productName,
            productQty,
            productAmount,
            totalAmount,
            salesDate,
            case when paymentMode = 0 then 'Cash' else 'Credit' end as paymentMode
        FROM sales inner join customers inner join products on products.productId = sales.productId and customers.customerId = sales.customerId where sales.userId = {}
    """.format( CurrSessionId)

    filters = []
    # if payment_mode:
    #     query += " AND paymentMode = %(payment_mode)s"
    #     filters["payment_mode"] = payment_mode
    if start_date:
        filters.append(f"salesDate >= '{start_date}'")
    if end_date:
        filters.append(f"salesDate <= '{end_date}'")
    if filters:
        query += " WHERE " + " AND ".join(filters)
    query += " ORDER BY salesDate DESC"

    # Pagination
    offset = (page - 1) * per_page
    query += f" LIMIT {per_page} OFFSET {offset}"

    # Fetch data
    df_sales = pd.read_sql(query, engine)

    # Get total sales grouped by customer and payment type
    summary_query = """
        SELECT 
            concat(customers.customerName, ' - ',customers.customerAddress ) customerName,
            case when paymentMode = 0 then 'Cash' else 'Credit' end as paymentMode ,
            SUM(totalAmount) AS totalSales
        FROM sales
        inner join customers on customers.customerId = sales.customerId where sales.userId = {}
        GROUP BY customerName, paymentMode
    """.format(CurrSessionId)
    summary_data = pd.read_sql(summary_query, engine)

    # Prepare data for rendering
    data = df_sales.to_dict(orient="records")
    summary = summary_data.to_dict(orient="records")

    # Total pages for pagination
    total_records_query = "SELECT COUNT(*) as total FROM sales where userId = {}".format(CurrSessionId)
    if filters:
        total_records_query += " WHERE " + " AND ".join(filters)
    total_records = pd.read_sql(total_records_query, engine).iloc[0]["total"]
    total_pages = (total_records + per_page - 1) // per_page

    return render_template(
        "report.html",
        data=data,
        summary=summary,
        filters={"paymentMode": payment_mode, "startDate": start_date, "endDate": end_date},
        current_page=page,
        total_pages=total_pages
    )

# Route to Export Data
@app.route('/export', methods=['GET'])
def export_data():
    CurrSessionId = str(session['userId'])
    
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Fetch all sales data
            query = "SELECT * FROM sales where userId = {} ORDER BY salesDate DESC".format(CurrSessionId)
            cursor.execute(query)
            results = cursor.fetchall()

        # Convert to DataFrame
        df = pd.DataFrame(results)

        # Export to Excel
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Sales Report')
        writer.save()
        output.seek(0)
    finally:
        connection.close()

    # Return the file as a response
    return send_file(output, attachment_filename='Sales_Report.xlsx', as_attachment=True)

@app.route('/clear_filters', methods=['GET'])
def clear_filters():
    return redirect("/report")

@app.route('/report/customer/<customer_id>', methods=['GET'])
def customer_report(customer_id):
    CurrSessionId = str(session['userId'])
    
    engine = db_con('db_web_app')
    
    page = int(request.args.get("page", 1))
    per_page = 10

    # Query for customer-specific data
    query = f"""
        SELECT 
             salesId,
            concat(customers.customerName, ' - ',customers.customerAddress ) customerName,
            products.productName as productName,
            productQty,
            productAmount,
            totalAmount,
            salesDate,
            case when paymentMode = 0 then 'Cash' else 'Credit' end as paymentMode
        FROM sales 
        inner join customers inner join products on products.productId = sales.productId and customers.customerId = sales.customerId
        WHERE concat(customers.customerName, ' - ',customers.customerAddress ) = '{customer_id}' and sales.userId = {CurrSessionId}
        ORDER BY salesDate DESC
        LIMIT {per_page} OFFSET {(page - 1) * per_page}
    """

    df_sales = pd.read_sql(query, engine)

    # Summary query
    summary_query = f"""
        SELECT 
            case when paymentMode = 0 then 'Cash' else 'Credit' end as paymentMode,
            SUM(totalAmount) AS totalSales
        FROM sales
        inner join customers on customers.customerId = sales.customerId
        WHERE concat(customers.customerName, ' - ',customers.customerAddress ) = '{customer_id}' and sales.userId = {CurrSessionId}
        GROUP BY paymentMode
    """
    summary_data = pd.read_sql(summary_query, engine)

    # Pagination logic
    total_records_query = f"""SELECT COUNT(*) as total FROM sales inner join customers on customers.customerId = sales.customerId
        WHERE concat(customers.customerName, ' - ',customers.customerAddress ) = '{customer_id}' and sales.userId = {CurrSessionId}"""
    
    total_records = pd.read_sql(total_records_query, engine).iloc[0]["total"]
    total_pages = (total_records + per_page - 1) // per_page

    # Render customer-specific report
    return render_template(
        "customer_report.html",
        data=df_sales.to_dict(orient="records"),
        summary=summary_data.to_dict(orient="records"),
        customer_name=customer_id,
        current_page=page,
        total_pages=total_pages
    )

@app.route('/clear_credit', methods=['POST'])
def clear_credit():
    CurrSessionId = str(session['userId'])
    
    # engine = db_con('db_web_app')

    engine = get_connection()

    customer_id = request.form.get('customerId')
    sales_id = request.form.get('salesId')
    


    if customer_id:
        query = "select customerId as id FROM customers where concat(customerName, ' - ', customerAddress) = '{}' and userId = {};".format(customer_id,CurrSessionId)
        s2ms = connectToS2MS('db_web_app')
        query_Output= s2ms.query_db(query)
        customerId_is = int(query_Output[0]['id'])

        # Clear all credit sales for the given customer
        update_query = """
            UPDATE sales 
            SET paymentMode = 0 
            WHERE customerId = {} AND paymentMode = 1
        """.format(customerId_is)

        s2ms = connectToS2MS('db_web_app')
        # data = {"productid" : productid}
        s2ms.query_db(update_query)

        # engine.execute(update_query, {"customerId": customer_id})
        flash(f"All credit sales for Customer ID {customer_id} have been cleared to cash.", "success")

    elif sales_id:
        # Clear a specific credit sale
        update_query = """
            UPDATE sales 
            SET paymentMode = 0 
            WHERE salesId = %(salesId)s AND paymentMode = 1
        """
        s2ms = connectToS2MS('db_web_app')
        s2ms.query_db(update_query,{"salesId": sales_id})

        # engine.execute(update_query, {"salesId": sales_id})
        flash(f"Credit sale ID {sales_id} has been cleared to cash.", "success")

    return redirect(request.referrer)

if __name__ == '__main__':
    app.run(debug=True)
