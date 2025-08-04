import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import datetime

try:
    import streamlit as st
    from prophet import Prophet
except ModuleNotFoundError as e:
    raise ModuleNotFoundError("Streamlit is not downloaded.") from e

st.set_page_config(page_title="Coffee Forecast ☕", layout="wide")

def run_app(df):
    st.sidebar.image("Coffee_Logo.png", width=200)


    st.sidebar.markdown(
    "<div style='position: fixed; bottom: 10px; width: 100%; font-style: italic; font-size: 12px; color: gray;'>"
    "Developed by Berkay Karadeniz."
    "</div>",
    unsafe_allow_html=True
)
    st.sidebar.title("Coffee Forecast Panel")

    min_date = df['date'].min().date()
    max_date = df['date'].max().date()

    selected_date = st.sidebar.date_input("Select a date (Past)", min_value=min_date, max_value=max_date)

    start_date = st.sidebar.date_input("Start Date", min_value=min_date, max_value=max_date, key='start')
    end_date = st.sidebar.date_input("End Date", min_value=start_date, max_value=max_date, key='end')

    st.header("Coffee Type Analysis ☕")
    coffee_list = ["-- Select a coffee --"] + sorted(df['coffee_name'].unique())
    selected_coffee = st.selectbox("Select a Coffee Type", coffee_list)

    show_analysis = st.sidebar.button("Show Analysis")

    if not show_analysis:
        st.info("Please select options on the sidebar and click 'Show Analysis' to see results.")
        return

    # Tarih kontrolleri
    if selected_date == min_date:
        st.warning("Please select a different Past Date.")
        return

    if start_date >= end_date:
        st.warning("Please select a valid Date Range (Start Date < End Date).")
        return

    if selected_coffee == "-- Select a coffee --":
        st.warning("Please select a coffee type.")
        return

    # --- Past Date Analysis ---
    st.header("Past Date Analysis")
    filtered_df = df[df['date'] == pd.to_datetime(selected_date)]
    if not filtered_df.empty:
        st.subheader(f"{selected_date} Summary of Date")
        total_income = filtered_df['money'].sum()
        most_common_coffee = filtered_df['coffee_name'].mode()[0]
        most_common_payment = filtered_df['cash_type'].mode()[0]

        st.metric("Total Income", f"{total_income:.2f} ₺")
        st.metric("Most Preferred Coffee", most_common_coffee)
        st.metric("Most Used Payment Method", most_common_payment)

        filtered_df = filtered_df.copy()
        filtered_df['hour'] = filtered_df['datetime'].dt.hour
        fig, ax = plt.subplots()
        sns.countplot(x='hour', data=filtered_df, ax=ax, palette='viridis')
        ax.set_title("Hourly Sales Distribution")
        st.pyplot(fig)
    else:
        st.warning("No data found for this date.")

    # --- Analysis by Date Range ---
    st.header("Analysis by Date Range")
    date_range_df = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]
    if not date_range_df.empty:
        st.subheader(f"{start_date} - {end_date} Range Summary")
        total_range_income = date_range_df['money'].sum()
        top_coffee_range = date_range_df['coffee_name'].mode()[0]
        top_cash_range = date_range_df['cash_type'].mode()[0]

        st.metric("Total Income", f"{total_range_income:.2f} ₺")
        st.metric("Most Preferred Coffee", top_coffee_range)
        st.metric("Most Used Payment Method", top_cash_range)
    else:
        st.info("No data found for this date range.")

    # --- Coffee Type Analysis ---
    st.header("Coffee Type Analysis")

    coffee_df = df[df['coffee_name'] == selected_coffee]
    if not coffee_df.empty:
        st.subheader(f"{selected_coffee} - Detailed Analysis")
        total_sales = coffee_df['money'].sum()
        most_common_hour = coffee_df['datetime'].dt.hour.mode()[0]
        most_common_day = coffee_df['datetime'].dt.day_name().mode()[0]
        most_used_payment = coffee_df['cash_type'].mode()[0]

        st.write(f"**Total Income from {selected_coffee}:** {total_sales:.2f} ₺")
        st.write(f"**Most Sold Hour:** {most_common_hour}:00")
        st.write(f"**Most Sold Day:** {most_common_day}")
        st.write(f"**Most Used Payment Method:** {most_used_payment}")

        fig3, ax3 = plt.subplots()
        sns.histplot(coffee_df['datetime'].dt.hour, bins=24, ax=ax3, color="saddlebrown")
        ax3.set_title(f"{selected_coffee} - Hourly Sales Distribution")
        ax3.set_xlabel("Hour of Day")
        st.pyplot(fig3)
    else:
        st.warning("No data found for this coffee.")

    # --- Future Forecasting ---
    future_date = st.sidebar.date_input("Select a Future Date", min_value=max_date + pd.Timedelta(days=1))
    if future_date <= max_date:
        st.warning("Please select a future date greater than last date in data.")
        return

    prophet_df = df.groupby('date')['money'].sum().reset_index()
    prophet_df.columns = ['ds', 'y']
    model = Prophet()
    model.fit(prophet_df)

    future = model.make_future_dataframe(periods=(future_date - max_date).days)
    forecast = model.predict(future)
    forecast_result = forecast[forecast['ds'] == pd.to_datetime(future_date)]

    if not forecast_result.empty:
        predicted_income = forecast_result['yhat'].values[0]
        st.subheader(f"{future_date} Future Income Forecast")
        st.metric("Predicted Income", f"{predicted_income:.2f} ₺")

        st.subheader("Forecast Chart")
        fig2 = model.plot(forecast)
        st.pyplot(fig2)
    else:
        st.warning("No forecast could be generated for this date.")

    df_ml = df.copy()
    df_ml['hour'] = df_ml['datetime'].dt.hour
    df_ml['dayofweek'] = df_ml['datetime'].dt.dayofweek
    df_ml['month'] = df_ml['datetime'].dt.month

    le = LabelEncoder()
    df_ml['coffee_name_encoded'] = le.fit_transform(df_ml['coffee_name'])

    X = df_ml[['hour', 'dayofweek', 'month']]
    y = df_ml['coffee_name_encoded']
    model_rf = RandomForestClassifier()
    model_rf.fit(X, y)

    st.subheader("Best-Selling Coffee Prediction for the Next Hour")
    selected_hour = st.slider("Select time for forecast", min_value=0, max_value=23, value=12)

    predict_date = pd.to_datetime(future_date)
    features = pd.DataFrame({
        'hour': [selected_hour],
        'dayofweek': [predict_date.dayofweek],
        'month': [predict_date.month]
    })

    predicted_label = model_rf.predict(features)[0]
    predicted_coffee = le.inverse_transform([predicted_label])[0]
    st.write(f"**{selected_hour}:00 Estimated Best-Selling Coffee:** {predicted_coffee}")


if __name__ == "__main__":
    df = pd.read_csv("index_1.csv")
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['date'] = pd.to_datetime(df['date'])
    run_app(df)
