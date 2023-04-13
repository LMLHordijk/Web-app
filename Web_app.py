# Web app to show some insights on how we performed last year (2022) in some large cities:
# Amsterdam, Rotterdam & Groningen:

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine

DB_USER = "deliverable_taskforce"
DB_PASSWORD = "learn_sql_2023"
DB_HOSTNAME = "training.postgres.database.azure.com"
DB_NAME = "deliverable"


# Retrieve data from database
@st.cache_data()
def get_data():
    engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOSTNAME}:5432/{DB_NAME}")
    df = pd.read_sql_query(
        """
        select rv.restaurant_id, rv.datetime, rv.rating_delivery, rv.rating_food, rs.location_city
        from reviews as rv
        inner join restaurants rs on rv.restaurant_id=rs.restaurant_id
        where rs.location_city in ('Amsterdam', 'Rotterdam', 'Groningen') and rv.datetime between '2022-01-01' and '2023-01-01';
        """,
        con=engine,
    )
    return df


# Get the data from df and cov_df
df = get_data()

# Calculate the count of reviews per day
df["datetime"] = pd.to_datetime(df["datetime"])
df["date"] = df["datetime"].dt.date
df2 = df.groupby(["date", "location_city"]).count().reset_index()

# Add slider to filter on time period
st.sidebar.title("Filter on time period:")
start_date = st.sidebar.date_input("Start date", value=df["datetime"].min())
end_date = st.sidebar.date_input("End date", value=df["datetime"].max())
if start_date < df["datetime"].min():
    st.sidebar.error("Error: Start date must fall after 2022-01-01.")
elif end_date > df["datetime"].max():
    st.sidebar.error("Error: End date must fall before 2023-01-01.")
elif start_date > end_date:
    st.sidebar.error("Error: End date must fall after start date.")
else:
    st.sidebar.success("Start date: `%s end date:`%s" % (start_date, end_date))

# Filter the data
df3 = df2[(df2["date"] >= start_date) & (df2["date"] <= end_date)]

# Plot the results in a streamlit app
st.title("Reviews in Amsterdam, Rotterdam & Groningen:")
fig = px.line(
    df3,
    x="date",
    y="restaurant_id",
    color="location_city",
    labels={"restaurant_id": "Count of reviews", "date": "Date", "location_city": "City"},
)
st.plotly_chart(fig, theme=None)


@st.cache_data()
def get_data2():
    engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOSTNAME}:5432/{DB_NAME}")
    cov_df = pd.read_sql_query(
        """
        select municipality_name, date_of_publication, total_reported
        from municipality_totals_daily
        where municipality_name in ('Amsterdam', 'Rotterdam', 'Groningen') and date_of_publication between '2022-01-01' and '2023-01-01';
        """,
        con=engine,
    )
    return cov_df


cov_df = get_data2()

# Filter the dataframe based on the sidebar
cov_df["date_of_publication"] = pd.to_datetime(cov_df["date_of_publication"])
cov_df["date"] = cov_df["date_of_publication"].dt.date
cov_df2 = cov_df.groupby(["date", "municipality_name"]).sum().reset_index()

cov_df3 = cov_df2[(cov_df2["date"] >= start_date) & (cov_df2["date"] <= end_date)]

# Plot the results in a streamlit app
st.title("Covid cases in Amsterdam, Rotterdam & Groningen:")
cov_fig = px.line(
    cov_df3,
    x="date",
    y="total_reported",
    color="municipality_name",
    labels={
        "total_reported": "Count of covid cases",
        "date": "Date",
        "municipality_name": "City",
    },
)
st.plotly_chart(cov_fig, theme=None)
