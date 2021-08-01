from flask import Flask, request, render_template, send_file, g, redirect, session, url_for
import pyodbc
import chart_studio.plotly as py
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import os
import csv
import glob
import sys


class User:
    def __init__(self, id, email, username, password):
        self.id = id
        self.email = email
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'

users = []
users.append(User(id=1, email='a@mail.com', username='Anthony', password='password'))
users.append(User(id=2, email='b@mail.com', username='Becca', password='secret'))
users.append(User(id=3, email='c@mail.com', username='Carlos', password='somethingsimple'))



app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'


connection = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=cscloudcomp.database.windows.net;Database=AzureDB;uid=cscloud;pwd=testing12345!')

cursor = connection.cursor()

cursor.execute("""
               SELECT TOP 10000 a.*,b.*,c.*
               FROM households a
               INNER JOIN transactions b 
                ON a.[HSHD_NUM] = b.[HSHD_NUM]
               INNER JOIN products c
                ON b.[PRODUCT_NUM] = c.[PRODUCT_NUM]
               """)                                

rows = cursor.fetchall()
str(rows)[0:10000]

cleanDF = pd.DataFrame( [[ij for ij in i] for i in rows] )
cleanDF.rename(columns={0: 'HSHD_NUM', 1: 'L', 2: 'AGE_RANGE', 3: 'MARITAL', 4: 'INCOME_RANGE', 5: 'HOMEOWNER', 
                        6: 'HSHD_COMPOSITION', 7: 'HH_SIZE', 8: 'CHILDREN', 9: 'BASKET_NUM', 10: 'HSHD_NUM2',
                        11: 'PURCHASE_',12: 'PRODUCT_NUM',13: 'SPEND',14: 'UNITS',15: 'STORE_R',16: 'WEEK_NUM',
                        17: 'YEAR', 18:'PRODUCT_NUM2', 19: 'DEPARTMENT',20:'COMMODITY',21: 'BRAND_TY',
                        22: 'NATURAL_ORGANIC_FLAG'}, inplace=True)
                        
cleanDF.drop(cleanDF.columns[[10,18]], axis=1, inplace=True)

cleanDF.columns = cleanDF.columns.str.replace(' ', '')

cleanDF = cleanDF[['HSHD_NUM','BASKET_NUM','PURCHASE_','PRODUCT_NUM','DEPARTMENT','COMMODITY','SPEND','UNITS','STORE_R','WEEK_NUM','YEAR','NATURAL_ORGANIC_FLAG','AGE_RANGE','MARITAL','INCOME_RANGE','HOMEOWNER','HSHD_COMPOSITION','HH_SIZE','CHILDREN']]


@app.before_request
def before_request():
    g.user = None
    

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']]
        g.user = user
        

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            return redirect(url_for('register'))

        user = [x for x in users if x.username == username][0]

        if user and user.password == password:
            session['user_id'] = user.id
            return redirect('/')

        return redirect(url_for('login'))

    return render_template('login.html')

# @app.route('/profile',methods=['GET', 'POST'])
# def profile():
    # if not g.user:
        # return redirect(url_for('login'))

    # return render_template('index.html')

@app.route('/registration', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        users.append(User(id=4, email=email, username=username, password=password))

        return redirect(url_for('login'))

    return render_template('registration.html')


#Data Pull Search
@app.route('/')
def search_data_pull():
    # if not g.user:
        # return redirect(url_for('login'))
        
    return render_template('index.html')

#Data Pull Search Post
@app.route('/', methods=['POST'])
def search_data_pull_post():
    text = request.form['u']
    
    specificDF = cleanDF[cleanDF['HSHD_NUM'] == int(text)]
    return render_template('index.html',  tables=[specificDF.to_html(classes='data')], titles=specificDF.columns.values)

#Data Pull #10
@app.route('/data')
def data_pull_ten():
    return render_template('datapull10.html')

#Data Pull #10 Post
@app.route('/data',methods=['POST'])
def data_pull_ten_post():
    if request.method == 'POST':
        if request.form['submit_button'] == 'Display Datapull #10':
            specificDF = cleanDF[cleanDF['HSHD_NUM'] == int(10)]
            return render_template('datapull10.html',  tables=[specificDF.to_html(classes='data')], titles=specificDF.columns.values)

#Import new data
@app.route('/importdata')
def import_data():
    return render_template('importnewdata.html')

#Import new data Post
@app.route('/importdata', methods=['GET', 'POST'])
def import_data_post():
    if request.method == 'POST':
        files = request.files.getlist('file')     
        
        for file in files:
        
            filepath = os.path.join('static', file.filename)
            file.save(filepath)
        
            print(file, file=sys.stderr)
            if "hou" in str(file):
                houseDF = pd.read_csv(filepath)
                
                houseDF.rename(columns={0: 'HSHD_NUM', 1: 'L', 2: 'AGE_RANGE', 3: 'MARITAL', 4: 'INCOME_RANGE', 5: 'HOMEOWNER', 
                                        6: 'HSHD_COMPOSITION', 7: 'HH_SIZE', 8: 'CHILDREN'},inplace=True)
      
            elif "tra" in str(file):
                transDF = pd.read_csv(filepath)
                
                transDF.rename(columns={0: 'BASKET_NUM', 1: 'HSHD_NUM',
                                        2: 'PURCHASE_',3: 'PRODUCT_NUM',4: 'SPEND',5: 'UNITS',6: 'STORE_R',7: 'WEEK_NUM',
                                        8: 'YEAR'}, inplace=True)
                
            elif "pro" in str(file):
                prodDF = pd.read_csv(filepath)  
                
                prodDF.rename(columns={0:'PRODUCT_NUM', 1: 'DEPARTMENT',2:'COMMODITY',3: 'BRAND_TY',
                                       4: 'NATURAL_ORGANIC_FLAG'}, inplace=True)
                                       
        houseDF.columns = houseDF.columns.str.replace(' ', '')
        transDF.columns = transDF.columns.str.replace(' ', '')
        prodDF.columns = prodDF.columns.str.replace(' ', '')
        
        newDF = pd.merge(houseDF,transDF, how='inner', on='HSHD_NUM')
        newDF = pd.merge(newDF, prodDF, how='inner', on='PRODUCT_NUM')
    
        newDF = newDF[['HSHD_NUM','BASKET_NUM','PURCHASE_','PRODUCT_NUM','DEPARTMENT','COMMODITY','SPEND','UNITS','STORE_R','WEEK_NUM','YEAR','NATURAL_ORGANIC_FLAG','AGE_RANGE','MARITAL','INCOME_RANGE','HOMEOWNER','HSHD_COMPOSITION','HH_SIZE','CHILDREN']]
        
        # Adding newly imported data to the original data
        global cleanDF
        cleanDF = pd.concat([cleanDF, newDF], ignore_index=True)
        
        return render_template('shownewdata.html',  tables=[newDF.to_html(classes='data')], titles=newDF.columns.values)
    return render_template('importnewdata.html')

#Read CSV
def read_CSV(file):
    df_columns = ['BASKET_NUM','HSHD_NUM','PURCHASE_','PRODUCT_NUM','SPEND','UNITS','STORE_R','WEEK_NUM','YEAR']
    rows = pd.read_csv(file, names=df_columns, header=None)
    csvDF = pd.DataFrame( [[ij for ij in i] for i in rows] )
    csvDF.rename(columns={0: 'BASKET_NUM', 1: 'HSHD_NUM', 2: 'PURCHASE_', 3: 'PRODUCT_NUM', 4: 'SPEND', 5: 'UNITS', 6: 'STORE_R', 7: 'WEEK_NUM', 8: 'YEAR'}, inplace = True)

    return csvDF

#Fig 1
@app.route('/plots/products_by_commodities.html')
def fig1():
    return send_file('products_by_commodities.html')

#Fig 2
@app.route('/plots/household_spending_over_time.html')
def fig2():
    return send_file('household_spending_over_time.html')

#Fig 3
@app.route('/plots/spending_by_age_range.html')
def fig3():
    return send_file('spending_by_age_range.html')

#Fig 4
@app.route('/plots/spending_by_income_range.html')
def fig4():
    return send_file('spending_by_income_range.html')

#Fig 5
@app.route('/plots/spending_by_household_size.html')
def fig5():
    return send_file('spending_by_household_size.html')

#Fig 6
@app.route('/plots/household_spending_by_year.html')
def fig6():
    return send_file('household_spending_by_year.html')

#Fig 7
@app.route('/plots/customer_retention_over_time.html')
def fig7():
    return send_file('customer_retention_over_time.html')



if __name__=="__main__":
    app.run(debug=True)

