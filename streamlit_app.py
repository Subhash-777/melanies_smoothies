# Import packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
# UI
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input
name_on_order = st.text_input('Name on Smoothie:')

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit data
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Multi-select
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

# Process selection
if ingredients_list:

    # Convert Row → string
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ''
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
        sf_df= st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # Submit button
    if st.button('Submit Order'):

        # Insert safely
        session.sql(
            "INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES (?, ?)",
            params=[ingredients_string, name_on_order]
        ).collect()

        st.success(f'✅ Your Smoothie is ordered, {name_on_order}!')

# New section to display smoothiefroot nutrition information
