import streamlit as st

from database import SQLite, DuckEngine, get_query_string

PORTFOLIO_DB = "data/portfolio.db"
QUERIES_DIR = "app/data/queries/"

db = SQLite(PORTFOLIO_DB)
duck_engine = DuckEngine(PORTFOLIO_DB)

class Sidebar(): 
    def header():
        st.header("Configurations")
    
    def select_box():
        rebalance_type = st.selectbox(
            "Select Rebalance Type",
            (
                "Investable Cash Dynamic",
                "Investable Cash Target",
                "Whole Portfolio"
            )
        )
        return rebalance_type
    
    def check_box():
        is_frac_shares = st.checkbox("Allow fractional share investing?")
        return is_frac_shares

class CashInput():
    def form():
        form  = st.form("cash_input")
        c1, c2, c3  = form.columns((1.5,1.5,1.5))
        operation   = c1.selectbox('Select Operation',('Add','Update','Delete'))
        account     = c2.text_input('Account Name')
        cash        = c3.number_input('Investable Cash ($)',min_value = 0.00)
        submitted   = form.form_submit_button("Submit")

        data = (
            operation,
            account.strip(),
            cash
        )
        db.query(get_query_string(QUERIES_DIR + 'create_cash_table')) 
        if submitted:
            if operation == "Add":
            # TO DO: Add error handling for invalid values (e.g. 0 shares)
                db.query(
                    get_query_string(QUERIES_DIR + "insert_cash_values"), 
                    [data[1:]]
                )
            if operation == "Delete":
                db.query(
                    get_query_string(QUERIES_DIR + "delete_cash"), 
                    [(data[1],)]
                )
            if operation == "Update":
                db.query(
                    get_query_string(QUERIES_DIR + "update_cash"), 
                    [data[:0:-1],]
                )
        return data
        

class HoldingsInput():    
    def form():
        form  = st.form("holdings_input")
        row_1 = form.container()
        row_2 = form.container()
        
        with row_1:
            c1, c2, c3  = row_1.columns((1.5,1.5,1.5))
            operation   = c1.selectbox('Select Operation',('Add','Update','Delete'))
            account     = c2.text_input('Account Name')
            ticker      = c3.text_input('Ticker')
        
        with row_2:
            c1, c2, c3, c4  = row_2.columns((1.25,1.25,1.25,1.25))
            shares          = c1.number_input('Shares',min_value = 0.00)
            target          = c2.number_input('Target Weight (%)')
            cost            = c3.number_input(
                                'Cost', 
                                min_value = 0.00, 
                                help = "Total Cost for all shares"
                            )

            price           = c4.number_input(
                                'Price',
                                min_value = 0.00,
                                help = """
                                Current stock price or price you plan on
                                purchasing the stock at
                                """
                            ) 
        
        submitted = form.form_submit_button("Submit")

        data = (
            operation,
            account.strip(),
            ticker.strip(),
            shares,
            target,
            cost,
            price
        )
        db.query(get_query_string(QUERIES_DIR + 'create_holdings_table')) 
        if submitted:
            if operation == "Add":
            # TO DO: Add error handling for invalid values (e.g. 0 shares)
                db.query(
                    get_query_string(QUERIES_DIR + "insert_holdings_values"), 
                    [data[1:]]
                )
            if operation == "Delete":
                db.query(
                    get_query_string(QUERIES_DIR + "delete_holding"), 
                    [data[1:3]]
                )
            if operation == "Update":
                db.query(
                    get_query_string(QUERIES_DIR + "update_holding"), 
                    [data[1:] + data[1:3]]
                )
        return data

class Portfolio():     
    def header():
        st.markdown("#### **Portfolio**")
    def cash():
        cash_columns = {
        "account_name": "Account",
        "cash": "Investable Cash ($)",
        }
        df = (db.fetch(get_query_string(QUERIES_DIR + 'select_cash'))
                .loc[:,list(cash_columns.keys())])
        return df

    def holdings():
        return duck_engine.fetch(get_query_string(QUERIES_DIR + 'select_holdings'))
    
    def dynamic_invest(account, cash, df_):
        symbol,price,target_diff = (df_[(df_.price <= cash)]
                                    .sort_values(by=['target_df'],ascending=False)
                                    .iloc[0]
                                    .to_list()
                                )  

        # TO DO 
        # dataframe columns (symbol,price,target_dif) {account: [cash,df_]}
        # investable cash per account, single value for all account
        # symbol, price,
        # add to whole shares to buy
        # call function again but subtract out price that it took to buy shared
        # have to run the loop for each separate account
        # TO DO: for dynamic there is going to be left over cash
        # Need to calculate total left over cash filter out tickers
        # where price is > then total left over cash then order by
        # tickers that are the most underweight and buy 1 more share
        # recursively call this function until not enough cash left 
        # to buy one share of another stock
        pass