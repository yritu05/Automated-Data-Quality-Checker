import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pandas.api.types import is_numeric_dtype

# Set page config
st.set_page_config(
    page_title="Advanced Data Quality Checker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #c3e6cb;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Import check functions from checker.py
def check_missing(df):
    missing = df.isnull().sum()
    return missing[missing > 0]

def check_duplicates(df):
    return df[df.duplicated()]

def check_schema(df, expected_columns):
    missing = [col for col in expected_columns if col not in df.columns]
    extra = [col for col in df.columns if col not in expected_columns]
    return missing, extra

def check_outliers(df, numeric_cols):
    outliers = {}
    for col in numeric_cols:
        q1, q3 = df[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        lower, upper = q1 - 1.5*iqr, q3 + 1.5*iqr
        outliers[col] = df[(df[col] < lower) | (df[col] > upper)]
    return outliers

# Cleaning functions
def clean_duplicates(df):
    return df.drop_duplicates()

def fill_missing(df, method='mean'):
    if method == 'mean':
        return df.fillna(df.select_dtypes(include=['number']).mean())
    elif method == 'median':
        return df.fillna(df.select_dtypes(include=['number']).median())
    elif method == 'mode':
        return df.fillna(df.mode().iloc[0])
    elif method == 'forward':
        return df.fillna(method='ffill')
    elif method == 'backward':
        return df.fillna(method='bfill')
    else:
        return df

def remove_outliers(df, numeric_cols):
    for col in numeric_cols:
        q1, q3 = df[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        lower, upper = q1 - 1.5*iqr, q3 + 1.5*iqr
        df = df[(df[col] >= lower) & (df[col] <= upper)]
    return df

# Data profiling functions
def get_data_profile(df):
    profile = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'numeric_columns': len(df.select_dtypes(include=['number']).columns),
        'categorical_columns': len(df.select_dtypes(include=['object']).columns),
        'missing_values': df.isnull().sum().sum(),
        'duplicate_rows': len(df[df.duplicated()]),
        'memory_usage': df.memory_usage(deep=True).sum() / 1024 / 1024  # MB
    }
    return profile

def get_column_info(df):
    info = []
    for col in df.columns:
        col_info = {
            'Column': col,
            'Type': str(df[col].dtype),
            'Non-Null Count': df[col].notnull().sum(),
            'Null Count': df[col].isnull().sum(),
            'Unique Values': df[col].nunique()
        }

        if is_numeric_dtype(df[col]):
            col_info.update({
                'Mean': round(df[col].mean(), 2),
                'Std': round(df[col].std(), 2),
                'Min': round(df[col].min(), 2),
                'Max': round(df[col].max(), 2)
            })
        else:
            col_info.update({
                'Most Frequent': df[col].mode().iloc[0] if not df[col].mode().empty else 'N/A'
            })

        info.append(col_info)
    return pd.DataFrame(info)

# Streamlit app
st.markdown('<h1 class="main-header">📊 Advanced Data Quality Checker</h1>', unsafe_allow_html=True)

# Initialize session state for multiple datasets
if 'datasets' not in st.session_state:
    st.session_state.datasets = {}
if 'current_dataset' not in st.session_state:
    st.session_state.current_dataset = None

st.sidebar.header("🎯 Dataset Management")

# Upload multiple files
uploaded_files = st.sidebar.file_uploader("Choose CSV or Excel files (up to 3)", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        if len(st.session_state.datasets) < 3:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.session_state.datasets[uploaded_file.name] = df

# Dataset selector
if st.session_state.datasets:
    dataset_names = list(st.session_state.datasets.keys())
    selected_dataset = st.sidebar.selectbox("📁 Select Dataset", dataset_names, index=dataset_names.index(st.session_state.current_dataset) if st.session_state.current_dataset in dataset_names else 0)
    st.session_state.current_dataset = selected_dataset
    df = st.session_state.datasets[selected_dataset]

    # Remove dataset option
    if st.sidebar.button(f"🗑️ Remove {selected_dataset}"):
        del st.session_state.datasets[selected_dataset]
        if st.session_state.current_dataset == selected_dataset:
            st.session_state.current_dataset = list(st.session_state.datasets.keys())[0] if st.session_state.datasets else None
        st.rerun()

    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Overview", "🔍 Data Quality", "📊 Visualizations", "🧹 Data Cleaning", "📈 Advanced Analysis"])

    with tab1:
        st.markdown(f'<h2 class="section-header">Dataset Overview - {selected_dataset}</h2>', unsafe_allow_html=True)

        # Dataset metrics
        profile = get_data_profile(df)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Rows", f"{profile['total_rows']:,}")
        with col2:
            st.metric("Total Columns", profile['total_columns'])
        with col3:
            st.metric("Missing Values", f"{profile['missing_values']:,}")
        with col4:
            st.metric("Duplicate Rows", f"{profile['duplicate_rows']:,}")

        # Data preview
        st.subheader("📊 Data Preview")
        st.dataframe(df.head(10), width='stretch')

        # Column information
        st.subheader("📋 Column Information")
        col_info = get_column_info(df)
        st.dataframe(col_info, width='stretch')

        # Descriptive statistics
        st.subheader("📈 Descriptive Statistics")
        st.dataframe(df.describe(include='all'), width='stretch')

    with tab2:
        st.markdown('<h2 class="section-header">Data Quality Analysis</h2>', unsafe_allow_html=True)

        # Missing values analysis
        st.subheader("❓ Missing Values Analysis")
        missing = check_missing(df)
        if not missing.empty:
            fig = px.bar(x=missing.index, y=missing.values, title="Missing Values by Column",
                        labels={'x': 'Column', 'y': 'Missing Count'})
            st.plotly_chart(fig, width='stretch')
            st.dataframe(missing.to_frame('Missing Count'), width='stretch')
        else:
            st.success("✅ No missing values found!")

        # Duplicates analysis
        st.subheader("🔄 Duplicate Analysis")
        duplicates = check_duplicates(df)
        if not duplicates.empty:
            st.warning(f"⚠️ Found {len(duplicates)} duplicate rows.")
            st.dataframe(duplicates.head(), width='stretch')
        else:
            st.success("✅ No duplicate rows found!")

        # Outliers analysis
        st.subheader("📊 Outlier Detection")
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            selected_cols = st.multiselect("Select numeric columns for outlier detection", numeric_cols, default=numeric_cols[:3])
            if selected_cols:
                outliers = check_outliers(df, selected_cols)
                for col in selected_cols:
                    if not outliers[col].empty:
                        st.warning(f"⚠️ Outliers detected in {col}: {len(outliers[col])} rows")

                        # Box plot for outliers
                        fig = px.box(df, y=col, title=f"Box Plot of {col} (Outliers Highlighted)")
                        st.plotly_chart(fig, width='stretch')

                        st.dataframe(outliers[col].head(), width='stretch')
        else:
            st.info("ℹ️ No numeric columns found for outlier detection.")

    with tab3:
        st.markdown('<h2 class="section-header">Data Visualizations</h2>', unsafe_allow_html=True)

        # Missing values pie chart
        st.subheader("🍰 Missing Values Distribution")
        missing_data = df.isnull().sum()
        if missing_data.sum() > 0:
            fig = px.pie(values=missing_data[missing_data > 0], names=missing_data[missing_data > 0].index,
                        title="Missing Values Distribution")
            st.plotly_chart(fig, width='stretch')
        else:
            st.success("✅ No missing values to visualize!")

        # Correlation heatmap
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if len(numeric_cols) > 1:
            st.subheader("🔗 Correlation Heatmap")
            corr = df[numeric_cols].corr()
            fig = px.imshow(corr, text_auto=True, aspect="auto", title="Correlation Matrix")
            st.plotly_chart(fig, width='stretch')

        # Distribution plots
        if numeric_cols:
            st.subheader("📊 Distribution Analysis")
            selected_dist_col = st.selectbox("Select column for distribution analysis", numeric_cols)
            fig = px.histogram(df, x=selected_dist_col, title=f"Distribution of {selected_dist_col}",
                             marginal="box", nbins=50)
            st.plotly_chart(fig, width='stretch')

    with tab4:
        st.markdown('<h2 class="section-header">Data Cleaning</h2>', unsafe_allow_html=True)

        # Cleaning options
        cleaned_df = df.copy()

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🧹 Remove Duplicates"):
                cleaned_df = clean_duplicates(cleaned_df)
                st.success("✅ Duplicates removed successfully!")

        with col2:
            fill_method = st.selectbox("Fill missing values method", ["None", "mean", "median", "mode", "forward", "backward"])
            if fill_method != "None" and st.button("🔧 Fill Missing Values"):
                cleaned_df = fill_missing(cleaned_df, fill_method)
                st.success(f"✅ Missing values filled using {fill_method} method!")

        if numeric_cols and st.button("📊 Remove Outliers"):
            cleaned_df = remove_outliers(cleaned_df, numeric_cols)
            st.success("✅ Outliers removed successfully!")

        # Cleaned data preview
        st.subheader("🧼 Cleaned Data Preview")
        st.dataframe(cleaned_df.head(10), width='stretch')

        # Download cleaned data
        st.subheader("💾 Download Cleaned Data")
        csv = cleaned_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"cleaned_{selected_dataset}",
            mime="text/csv"
        )

    with tab5:
        st.markdown('<h2 class="section-header">Advanced Analysis</h2>', unsafe_allow_html=True)

        # Dataset comparison
        if len(st.session_state.datasets) > 1:
            st.subheader("⚖️ Dataset Comparison")
            compare_datasets = st.multiselect("Select datasets to compare", list(st.session_state.datasets.keys()),
                                            default=list(st.session_state.datasets.keys())[:2])

            if len(compare_datasets) > 1:
                comparison_data = []
                for name in compare_datasets:
                    dataset_df = st.session_state.datasets[name]
                    profile = get_data_profile(dataset_df)
                    comparison_data.append({
                        'Dataset': name,
                        'Rows': profile['total_rows'],
                        'Columns': profile['total_columns'],
                        'Missing Values': profile['missing_values'],
                        'Duplicates': profile['duplicate_rows'],
                        'Memory (MB)': round(profile['memory_usage'], 2)
                    })
                comparison_df = pd.DataFrame(comparison_data)
                st.dataframe(comparison_df, width='stretch')

                # Comparison visualizations
                st.subheader("📊 Comparison Charts")
                fig = go.Figure()

                # Add traces for each metric
                metrics = ['Rows', 'Columns', 'Missing Values', 'Duplicates']
                for metric in metrics:
                    fig.add_trace(go.Bar(
                        name=metric,
                        x=comparison_df['Dataset'],
                        y=comparison_df[metric],
                        offsetgroup=0
                    ))

                fig.update_layout(
                    title="Dataset Comparison",
                    xaxis_title="Dataset",
                    yaxis_title="Count",
                    barmode='group'
                )
                st.plotly_chart(fig, width='stretch')

        # Data type distribution
        st.subheader("🏷️ Data Types Distribution")
        dtype_counts = df.dtypes.value_counts()
        fig = px.pie(values=dtype_counts.values, names=dtype_counts.index.astype(str),
                    title="Data Types Distribution")
        st.plotly_chart(fig, width='stretch')

        # Memory usage
        st.subheader("💾 Memory Usage Analysis")
        memory_usage = df.memory_usage(deep=True) / 1024 / 1024  # MB
        memory_df = pd.DataFrame({
            'Column': memory_usage.index,
            'Memory (MB)': memory_usage.values
        }).sort_values('Memory (MB)', ascending=False)

        fig = px.bar(memory_df, x='Column', y='Memory (MB)', title="Memory Usage by Column")
        st.plotly_chart(fig, width='stretch')

else:
    st.info("📤 Please upload CSV or Excel files to get started with data analysis!")
