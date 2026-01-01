# sales_dashboard.py

import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# -------------------------------
# Step 1: Load & Clean Data
# -------------------------------


file_path = "sales_data.csv"

# Try reading with a different encoding
sales = pd.read_csv(file_path, encoding='cp1252')  # or encoding='latin1'


# Convert ORDERDATE to datetime
sales['ORDERDATE'] = pd.to_datetime(sales['ORDERDATE'], errors='coerce')
sales['Month'] = sales['ORDERDATE'].dt.month
sales['Year'] = sales['ORDERDATE'].dt.year

# Ensure numeric columns
numeric_cols = ['QUANTITYORDERED', 'PRICEEACH', 'SALES', 'MSRP']
sales[numeric_cols] = sales[numeric_cols].apply(pd.to_numeric, errors='coerce')
sales.fillna(0, inplace=True)

# -------------------------------
# Step 2: Initialize Dash App
# -------------------------------
app = dash.Dash(__name__)
app.title = "Sales Dashboard"

# -------------------------------
# Step 3: Layout
# -------------------------------
app.layout = html.Div([
    html.H1("Interactive Sales Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Select Year:"),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': y, 'value': y} for y in sorted(sales['Year'].unique())],
            value=sorted(sales['Year'].unique())[0]
        )
    ], style={'width': '25%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Select Product Line:"),
        dcc.Dropdown(
            id='product-dropdown',
            options=[{'label': p, 'value': p} for p in sales['PRODUCTLINE'].unique()],
            value=sales['PRODUCTLINE'].unique()[0]
        )
    ], style={'width': '30%', 'display': 'inline-block', 'marginLeft': '2%'}),

    dcc.Graph(id='monthly-sales-trend'),
    dcc.Graph(id='sales-by-country'),
    dcc.Graph(id='sales-by-dealsize')
])

# -------------------------------
# Step 4: Callbacks for Interactivity
# -------------------------------
@app.callback(
    [Output('monthly-sales-trend', 'figure'),
     Output('sales-by-country', 'figure'),
     Output('sales-by-dealsize', 'figure')],
    [Input('year-dropdown', 'value'),
     Input('product-dropdown', 'value')]
)
def update_graphs(selected_year, selected_product):
    # Filter data
    filtered = sales[(sales['Year'] == selected_year) & (sales['PRODUCTLINE'] == selected_product)]

    # 1. Monthly Sales Trend
    monthly_sales = filtered.groupby('Month')['SALES'].sum().reset_index()
    fig1 = px.line(monthly_sales, x='Month', y='SALES', markers=True,
                   title=f"Monthly Sales Trend ({selected_product}, {selected_year})")

    # 2. Sales by Country
    country_sales = filtered.groupby('COUNTRY')['SALES'].sum().reset_index()
    fig2 = px.bar(country_sales, x='COUNTRY', y='SALES',
                  title=f"Sales by Country ({selected_product}, {selected_year})",
                  text='SALES')

    # 3. Sales by Deal Size
    deal_sales = filtered.groupby('DEALSIZE')['SALES'].sum().reset_index()
    fig3 = px.bar(deal_sales, x='DEALSIZE', y='SALES',
                  title=f"Sales by Deal Size ({selected_product}, {selected_year})",
                  text='SALES')

    return fig1, fig2, fig3

# -------------------------------
# Step 5: Run App
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)

