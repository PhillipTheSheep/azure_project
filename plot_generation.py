import pyodbc
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

connection = pyodbc.connect('Driver={SQL Server};Server=cscloudcomp.database.windows.net;Database=AzureDB;uid=cscloud;pwd=testing12345!')

cursor = connection.cursor()

cursor.execute("""
               SELECT a.*,b.*,c.*
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





#Displays a piechart of products by commodity
def products_by_commodities():
    # cursor.execute('select PRODUCT_NUM, COMMODITY from products')
    # rows = cursor.fetchall()
    # str(rows)[0:400]

    # df = pd.DataFrame( [[ij for ij in i] for i in rows] )
    # df.rename(columns={0: 'PRODUCT_NUM', 1: 'COMMODITY'}, inplace=True)


    fig = px.pie(cleanDF, values='PRODUCT_NUM',names = 'COMMODITY', title='Products Sold by Commodity')
    # py.plot(fig, filename='MS_products_by_commodities', sharing='public')
    fig.write_html('products_by_commodities.html')

#Displays a line graph of household spending over time
def household_spending_over_time():
    cursor.execute('select PURCHASE_, SUM(SPEND) from transactions GROUP BY PURCHASE_')
    rows = cursor.fetchall()
    str(rows)[0:10000]
    
    df = pd.DataFrame( [[ij for ij in i] for i in rows] )
    df.rename(columns={0: 'DATE', 1: 'SPEND'}, inplace=True)
    
    fig = px.line(df, x='DATE', y='SPEND', title='Household Expenditures Over Time')
    fig.write_html('household_spending_over_time.html')

#Diplays a bar graph of Expidentures by Age Range
def spending_by_age_range():
    cursor.execute("""   
                     SELECT households.HSHD_NUM, households.AGE_RANGE, SUM(transactions.SPEND)
                     FROM households, transactions
                     WHERE households.HSHD_NUM = transactions.HSHD_NUM
                     GROUP BY households.HSHD_NUM, households.AGE_RANGE
                     ORDER BY households.HSHD_NUM
                   """)
                   
    rows = cursor.fetchall()
    str(rows)[0:400]
    
    df = pd.DataFrame( [[ij for ij in i] for i in rows] )
    df.rename(columns={0: 'HSHD_NUM', 1: 'AGE_RANGE', 2:'SPEND'}, inplace=True)
    
    fig = px.bar(df, x='AGE_RANGE',y='SPEND',title='Household Expidentures by Age Range')
    fig.write_html('spending_by_age_range.html')

#Diplays a bar graph of Expidentures by Income Range
def spending_by_income_range():
    cursor.execute("""   
                     SELECT households.HSHD_NUM, households.INCOME_RANGE, SUM(transactions.SPEND)
                     FROM households, transactions
                     WHERE households.HSHD_NUM = transactions.HSHD_NUM
                     GROUP BY households.HSHD_NUM, households.INCOME_RANGE
                     ORDER BY households.HSHD_NUM
                   """)
                   
    rows = cursor.fetchall()
    str(rows)[0:400]
    
    df = pd.DataFrame( [[ij for ij in i] for i in rows] )
    df.rename(columns={0: 'HSHD_NUM', 1: 'INCOME_RANGE', 2:'SPEND'}, inplace=True)
    
    fig = px.bar(df, x='INCOME_RANGE',y='SPEND',title='Household Expidentures by Income Range')
    fig.write_html('spending_by_income_range.html')


#Diplays a bar graph of Expidentures by Household Size
def spending_by_household_size():
    cursor.execute("""   
                    SELECT households.HSHD_NUM, households.HH_SIZE, SUM(transactions.SPEND)
                    FROM households, transactions
                    WHERE households.HSHD_NUM = transactions.HSHD_NUM
                    GROUP BY households.HSHD_NUM, households.HH_SIZE
                    ORDER BY households.HSHD_NUM
                """)
                   
    rows = cursor.fetchall()
    str(rows)[0:400]
    
    df = pd.DataFrame( [[ij for ij in i] for i in rows] )
    df.rename(columns={0: 'HSHD_NUM', 1: 'HH_SIZE', 2:'SPEND'}, inplace=True)
    
    fig = px.bar(df, x='HH_SIZE',y='SPEND',title='Household Expidentures by Household Size')
    fig.write_html('spending_by_household_size.html')

#Diplays a bar graph of household spending by year
def household_spending_by_year():
    cursor.execute('select YEAR, SUM(SPEND) from transactions GROUP BY YEAR')
    rows = cursor.fetchall()
    str(rows)[0:10000]
    
    df = pd.DataFrame( [[ij for ij in i] for i in rows] )
    df.rename(columns={0: 'YEAR', 1: 'SPEND'}, inplace=True)
    
    fig = px.bar(df, x='YEAR', y='SPEND', title='Household Expidentures By Year')
    fig.write_html('household_spending_by_year.html')

#Displays a bar chart of customer retention over time
def customer_retention_over_time():
    cursor.execute('select count(distinct transactions.HSHD_NUM), transactions.PURCHASE_ FROM transactions GROUP BY transactions.PURCHASE_')
    rows = cursor.fetchall()
    str(rows)[0:10000]
    
    df = pd.DataFrame( [[ij for ij in i] for i in rows] )
    df.rename(columns={0: 'HSHD_NUM', 1: 'PURCHASE_'}, inplace=True)

    fig = px.bar(df, x='PURCHASE_', y='HSHD_NUM', title='Distinct Customer Retention Over Time')
    fig.write_html('customer_retention_over_time.html')

products_by_commodities()
household_spending_over_time()
spending_by_age_range()
spending_by_income_range()
spending_by_household_size()
household_spending_by_year()
customer_retention_over_time()