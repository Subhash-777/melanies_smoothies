# Import packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Title
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit data (WITH SEARCH_ON)
my_dataframe = session.table("smoothies.public.fruit_options") \
    .select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert to pandas
pd_df = my_dataframe.to_pandas()

# Multiselect (show only FRUIT_NAME)
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'],
    max_selections=5
)

# Process selection
if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += ', ' + fruit_chosen
        # Get SEARCH_ON value
        search_on = pd_df.loc[
            pd_df['FRUIT_NAME'] == fruit_chosen,
            'SEARCH_ON'
        ].iloc[0]

        st.write(f"The search value for {fruit_chosen} is {search_on}")

        # API Call using SEARCH_ON
        st.subheader(f"{fruit_chosen} Nutrition Information")

        response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        if response.status_code == 200:
            st.dataframe(response.json(), use_container_width=True)
        else:
            st.warning(f"No data found for {fruit_chosen}")

    # Submit Order
    if st.button('Submit Order'):

        session.sql(
            """
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES (?, ?)
            """,
            params=[ingredients_string, name_on_order]
        ).collect()

        st.success(f'✅ Your Smoothie is ordered, {name_on_order}!')
