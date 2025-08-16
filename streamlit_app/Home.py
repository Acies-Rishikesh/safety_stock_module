import streamlit as st

st.set_page_config(page_title="Safety Stock Application", layout="wide")

# Title with emoji
st.title("Safety Stock Application")
st.markdown("---")

# Short description
st.markdown("""
Welcome to the **Safety Stock Application** — your tool for calculating 
and analyzing safety stock using **Rule-based** and **Machine Learning (ML)** methods.  

Follow the guided steps in the **sidebar** to get started.
""")

# Steps in a nice format
st.markdown("### How It Works")
st.markdown("""
1. ** Method Selection** — Specify whether you have past sales & forecast data, and choose your calculation method.  
2. ** Data Upload** — Upload the required datasets for the chosen method.  
3. ** Results** — View, filter, and download your calculated safety stock values.  
4. ** Dashboard & Scenario Planner**— Compare different stocking scenarios and visualize trends.  
""")

# Tip box
st.info("""
 **Tip:** Ensure your data files include all required columns 
to get the most accurate results.
""")

# Footer message
st.markdown("---")
st.caption("Developed for optimized inventory planning and smarter safety stock decisions.")
