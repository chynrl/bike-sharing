import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
)
# Load the data
data_hour = pd.read_csv("hour_data.csv")
data_day = pd.read_csv("day_data.csv")

data_hour['dteday'] = pd.to_datetime(data_hour['dteday'])
data_day['dteday'] = pd.to_datetime(data_day['dteday'])

# Title for the dashboard
st.title("Bike Sharing Usage Dashboard")

tab1, tab2, tab3, tab4 = st.tabs(['Daily Sharing', 'Weekday vs Weekend', 'Hourly usage', 'Seasonal effect'])

with tab1:
    min_date= data_hour['dteday'].min()
    max_date= data_hour['dteday'].max()
    
    # take start_date & end_date dari date_input
    start_date, end_date = st.date_input(
    label='To see bike usage over time, you can choose time span here',min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
    )

    if start_date > end_date:
        st.error("The end date must be greater than or equal to the start date.")
    else:
    # Filter data based time span that choose
        mask = (data_hour['dteday'] >= pd.to_datetime(start_date)) & (data_hour['dteday'] <= pd.to_datetime(end_date))
        filtered_data = data_hour.loc[mask]


    # Daily sharing
    st.subheader('Daily sharing')

    total_users = filtered_data.cnt.sum()
    st.metric("Total users", value=total_users)

    monthly_usage = filtered_data.groupby('dteday').agg({'cnt': 'sum'}).reset_index()

    st.line_chart(monthly_usage, 
                x='dteday', 
                y='cnt', 
                x_label='Time',
                y_label='Total Users',
                color='#ffaa00'
                )

with tab2:
    # Weekday vs Weekend
    st.subheader('Bike Usage: Weekday vs Weekend')

    col1, col2 = st.columns(2)

    with col1:
        Weekday_total = data_day[data_day['workingday'] == 1]['cnt'].sum()
        st.metric("Total Bike Usage in Weekday", value=Weekday_total)

    with col2:
        Weekend_total = data_day[data_day['workingday'] == 0]['cnt'].sum()
        st.metric("Total Bike Usage in Weekend", value=Weekend_total)
        
    # Group by workingday and calculate mean of casual and registered users
    usage_by_workingday = data_day.groupby('workingday').agg({'casual': 'sum', 'registered': 'sum'}).reset_index()
        
    # Melt the DataFrame for easier plotting
    usage_melted = usage_by_workingday.melt(id_vars='workingday', value_vars=['casual', 'registered'], 
                                                var_name='User Type', value_name='Sum Users')

    chart = alt.Chart(usage_melted).mark_bar().encode(
        x=alt.X('workingday:N', title='Working Day (1 = Yes, 0 = No)'),
        y=alt.Y('Sum Users:Q', title='Number of Users'),
        color='User Type:N'
    ).properties(
        width=700,
        height=400
    )

    st.altair_chart(chart)



with tab3 :
    # Group by hour and calculate total users
    st.subheader('Total Bike Usage Throughout the Day')
    hourly_usage = data_hour.groupby('hr').agg({'cnt': 'sum'}).reset_index()

    st.line_chart(hourly_usage, 
                x='hr', 
                y='cnt', 
                x_label='Hour of the Day',
                y_label='Total Users'
                )

with tab4:
    #Seasonal Effect
    st.subheader('Seasonal Effect on Bike Usage')
    st.markdown('Season has an impact on many users who rent')
    # Group by season and calculate mean users
    seasonal_usage = data_day.groupby('season').agg({
        'casual': 'sum',
        'registered': 'sum',
        'cnt': 'sum'
    }).reset_index()

    # Map season to readable labels
    seasonal_usage['season'] = seasonal_usage['season'].map({1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Fall'})
        
    # Melt the DataFrame for easier plotting
    seasonal_melted = seasonal_usage.melt(id_vars='season', value_vars=['casual', 'registered', 'cnt'], 
                                            var_name='User Type', value_name='Average Users')

    # Set 'season' as index for better visualization
    seasonal_usage.set_index('season', inplace=True)

    # Plot using st.bar_chart
    st.bar_chart(seasonal_usage)



