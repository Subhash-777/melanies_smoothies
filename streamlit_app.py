# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

from snowflake.snowpark import Session

connection_parameters = {
    "account": "UYWIPHW-QBB73348",      # e.g. xy12345.ap-south-1
    "user": "SUBHASH",
    "password": "Subhash@74327432",
    "role": "SYSADMIN",            # e.g. ACCOUNTADMIN
    "warehouse": "COMPUTE_WH",  # e.g. COMPUTE_WH
    "database": "SMOOTHIES",
    "schema": "PUBLIC"
}

session = Session.builder.configs(connection_parameters).create()

# App Title
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Fetch fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Multi-select (max 5)
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

# When ingredients selected
if ingredients_list:

    # Convert Row objects → clean string
    ingredients_string = ', '.join([row['FRUIT_NAME'] for row in ingredients_list])

    # Submit button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:

        # Insert safely using parameters
        session.sql(
            "INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES (?, ?)",
            params=[ingredients_string, name_on_order]
        ).collect()

        # Success message
        st.success(f'✅ Your Smoothie is ordered, {name_on_order}!')
