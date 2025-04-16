import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from api_callers import UN_Population

st.set_page_config(
    page_title="UN Population Data Visualization",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stMultiSelect [data-baseweb="select"] {
        min-width: 350px;
        width: 100%;
    }
    .stMultiSelect [data-baseweb="tag"] {
        min-width: 200px;
        max-width: 1500px;
    }
    .stMultiSelect [data-baseweb="tag"] span {
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        display: inline-block !important;
        max-width: 100% !important;
    }
    div[data-testid="stVerticalBlock"] div[style*="flex-direction: column;"] div[data-testid="stVerticalBlock"] {
        width: 100%;
    }
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* Header styling */
    h1, h2, h3 {
        margin-bottom: 0.5rem;
    }
    /* Card styling for indicators */
    .stCard {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌍 UN Population Data Visualization")
st.markdown(
    """
    This dashboard visualizes data from the United Nations Population Division API. 
    Select indicators from the sidebar to explore population trends and demographics.
    """
)

if 'all_indicators' not in st.session_state:
    with st.spinner("Loading indicators from UN Population API..."):
        try:
            un_population = UN_Population()
            st.session_state.all_indicators = un_population.get_indicator_names()
            st.session_state.selected_locations = [900]
        except Exception as e:
            st.error(f"Error loading indicators: {str(e)}")
            st.session_state.all_indicators = {}
            st.session_state.selected_locations = [900]

with st.sidebar:
    st.header("📊 Data Selection")

    search_term = st.text_input("🔍 Search indicators", "")

    if not isinstance(st.session_state.all_indicators, dict):
        st.session_state.all_indicators = {}
        st.error("Failed to load indicators properly. Please refresh the page.")

    filtered_indicators = {
        name: id for name, id in st.session_state.all_indicators.items() if search_term.lower() in name.lower()}

    selected_indicators = st.multiselect(
        "Select indicators to visualize",
        options=list(filtered_indicators.keys()),
        default=list(filtered_indicators.keys())[
            :3] if filtered_indicators else [],
        key="indicator_selector"
    )

    st.sidebar.markdown("---")

    st.subheader("📈 Visualization Options")
    chart_type = st.selectbox(
        "Chart Type",
        ["Line Chart", "Bar Chart", "Area Chart", "Scatter Plot"],
        index=0
    )

    show_grid = st.checkbox("Show Grid", value=True)
    enable_animations = st.checkbox("Enable Animations", value=True)

    st.sidebar.markdown("---")

    st.sidebar.subheader("ℹ️ About")
    st.sidebar.info(
        """
        This dashboard uses data from the UN Population Division API.
        Data is fetched in real-time and visualized using Plotly and Streamlit.
        """
    )


def fetch_and_visualize(selected_indicators):
    """Fetch and visualize data for the selected indicators"""
    if not selected_indicators:
        st.warning(
            "👆 Please select at least one indicator from the sidebar to visualize.")
        return

    un_population = UN_Population()

    tab1, tab2 = st.tabs(["Individual Indicators", "Comparative View"])

    with tab1:
        for indicator in selected_indicators:
            with st.spinner(f"Fetching data for {indicator}..."):
                try:
                    df = un_population.get_data_for_indicator(
                        indicator, locations=st.session_state.selected_locations)

                    if df.empty:
                        st.warning(f"No data available for {indicator}")
                        continue

                    st.markdown(f"### {indicator}")

                    col1, col2 = st.columns([3, 1])

                    with col1:
                        if chart_type == "Line Chart":
                            fig = px.line(
                                df,
                                x="year",
                                y="value",
                                color="location" if len(
                                    df['location'].unique()) > 1 else None,
                                markers=True,
                                title=f"{indicator} Over Time",
                                labels={"value": "Value", "year": "Year",
                                        "location": "Location"},
                                template="plotly_white"
                            )
                        elif chart_type == "Bar Chart":
                            fig = px.bar(
                                df,
                                x="year",
                                y="value",
                                color="location" if len(
                                    df['location'].unique()) > 1 else None,
                                title=f"{indicator} Over Time",
                                labels={"value": "Value", "year": "Year",
                                        "location": "Location"},
                                template="plotly_white"
                            )
                        elif chart_type == "Area Chart":
                            fig = px.area(
                                df,
                                x="year",
                                y="value",
                                color="location" if len(
                                    df['location'].unique()) > 1 else None,
                                title=f"{indicator} Over Time",
                                labels={"value": "Value", "year": "Year",
                                        "location": "Location"},
                                template="plotly_white"
                            )
                        else:
                            fig = px.scatter(
                                df,
                                x="year",
                                y="value",
                                color="location" if len(
                                    df['location'].unique()) > 1 else None,
                                size="value",
                                title=f"{indicator} Over Time",
                                labels={"value": "Value", "year": "Year",
                                        "location": "Location"},
                                template="plotly_white"
                            )

                        fig.update_layout(
                            xaxis=dict(showgrid=show_grid),
                            yaxis=dict(showgrid=show_grid),
                            legend=dict(orientation="h", yanchor="bottom",
                                        y=1.02, xanchor="right", x=1),
                            height=500,
                        )

                        if enable_animations:
                            fig.update_layout(transition_duration=500)

                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        st.subheader("Summary Statistics")

                        latest_year = df['year'].max(
                        ) if not df.empty else "N/A"
                        latest_value = df[df['year'] == latest_year]['value'].mean(
                        ) if not df.empty else "N/A"

                        st.metric(
                            label="Latest Value",
                            value=f"{latest_value:.2f}" if isinstance(
                                latest_value, (int, float)) else latest_value,
                            delta=None
                        )

                        st.metric(
                            label="Latest Year",
                            value=latest_year,
                            delta=None
                        )

                        if not df.empty and len(df) > 1:
                            first_value = df.iloc[0]['value'] if not df.empty else 0
                            last_value = df.iloc[-1]['value'] if not df.empty else 0
                            change = last_value - first_value
                            change_pct = (change / first_value * 100) if first_value != 0 else 0  # noqa

                            delta_color = "normal" if change >= 0 else "inverse"
                            st.metric(
                                label="Overall Change",
                                value=f"{change:.2f}",
                                delta=f"{change_pct:.1f}%",
                                delta_color=delta_color
                            )

                        with st.expander("View Raw Data"):
                            st.dataframe(df, use_container_width=True)

                except Exception as e:
                    st.error(f"Error processing {indicator}: {e}")

    with tab2:
        if len(selected_indicators) > 1:
            try:
                st.subheader("Comparative View of Selected Indicators")

                all_data = []
                for indicator in selected_indicators:
                    df = un_population.get_data_for_indicator(
                        indicator, locations=st.session_state.selected_locations)
                    if not df.empty:
                        df['indicator'] = indicator
                        df['normalized_value'] = (df['value'] - df['value'].min()) / (df['value'].max(
                        ) - df['value'].min()) if df['value'].max() != df['value'].min() else df['value']
                        all_data.append(df)

                if all_data:
                    combined_df = pd.concat(all_data)

                    fig = px.line(
                        combined_df,
                        x="year",
                        y="value",
                        color="indicator",
                        facet_col="location" if len(
                            combined_df['location'].unique()) > 1 else None,
                        title="Comparison of Selected Indicators",
                        labels={"value": "Value", "year": "Year",
                                "indicator": "Indicator"},
                        template="plotly_white"
                    )

                    fig.update_layout(
                        height=600,
                        legend=dict(orientation="h", yanchor="bottom",
                                    y=1.02, xanchor="right", x=1),
                        xaxis=dict(showgrid=show_grid),
                        yaxis=dict(showgrid=show_grid)
                    )

                    if enable_animations:
                        fig.update_layout(transition_duration=500)

                    st.plotly_chart(fig, use_container_width=True)

                    st.subheader("Normalized Comparison (0-1 scale)")

                    fig2 = px.line(
                        combined_df,
                        x="year",
                        y="normalized_value",
                        color="indicator",
                        facet_col="location" if len(
                            combined_df['location'].unique()) > 1 else None,
                        title="Normalized Comparison of Selected Indicators",
                        labels={
                            "normalized_value": "Normalized Value (0-1)", "year": "Year", "indicator": "Indicator"},
                        template="plotly_white"
                    )

                    fig2.update_layout(
                        height=600,
                        legend=dict(orientation="h", yanchor="bottom",
                                    y=1.02, xanchor="right", x=1),
                        xaxis=dict(showgrid=show_grid),
                        yaxis=dict(showgrid=show_grid)
                    )

                    if enable_animations:
                        fig2.update_layout(transition_duration=500)

                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.warning("No data available for comparison.")
            except Exception as e:
                st.error(f"Error creating comparative view: {e}")
        else:
            st.info("Select at least two indicators to see a comparative view.")


fetch_and_visualize(selected_indicators)

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>Data source: <a href="https://population.un.org/dataportal/" target="_blank">United Nations Population Division</a> | API: <a href="https://population.un.org/dataportal/about/dataapi" target="_blank">Documentation</a></p>
    </div>
    """,
    unsafe_allow_html=True
)
