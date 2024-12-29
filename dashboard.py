import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import numpy as np
import seaborn as sns
import kaleido 
import zipfile
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings('ignore')

image_dir = "plot_images"
os.makedirs(image_dir, exist_ok=True)

st.set_page_config(page_title="Dinesh_dashboards !!! ",page_icon=": bar_chart:", layout="wide")

st.title(":bar_chart: Dinesh_Dashboards EDA")
st.subheader( "DATASET : prepared to only work with Sales Report")

file_path = "Sample_Data.csv"
with open(file_path, "rb") as file:
    file_content = file.read()
st.download_button(
    label="Download Sample_Data.csv",
    data=file_content,
    file_name="Sample_Data.csv",
    mime="text/csv"
)


st.markdown('<style>div.block-container{padding-top:3rem}</style>',unsafe_allow_html=True)


#for the user to browse the CSV file and upload 
f1=st.file_uploader(":file_folder: Upload file ", type=(["csv","txt","xlsx", "xls"]))
if f1  is not None:
    filename = f1.name
    st.write(filename)
    df=pd.read_csv(filename, encoding= "ISO-8859-1",on_bad_lines='skip')
else:
    os.chdir(r"D:\Project\Data Analytics")
    df=pd.read_csv("Sample_Data.csv")


col1, col2 =st.columns((2))
df["Order Date"] =pd.to_datetime(df["Order Date"])

#how to decide the date
#by getting hte min and max of the data from the table
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1=pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 =pd.to_datetime(st.date_input("End Date", endDate))

df=df[(df["Order Date"]>=date1) & (df["Order Date"]<=date2)].copy()

st.sidebar.header("choose filter")
region = st.sidebar.multiselect("Pick your Region ", df["Region"].unique())
if not region:
    df2=df.copy()
else:
    df2=df[df["Region"].isin(region)]


#creating for the state
state =st.sidebar.multiselect("Pick State", df2["State"].unique())
if not state:
    df3 =df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]


#Create City

city= st.sidebar.multiselect("Pick City", df3["City"].unique())


#filter the data based on city state and region

if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]

category_df = filtered_df.groupby(by = ["Category"], as_index = False)["Sales"].sum()

# Show filtered row count
st.write(f"Filtered data contains {filtered_df.shape[0]} rows.")


# Sales Trend Over Time
st.subheader(":point_right: Sales Trend Over Time")
sales_trend = (
    filtered_df.groupby(filtered_df["Order Date"].dt.to_period("M"))["Sales"]
    .sum()
    .reset_index()
)
sales_trend["Order Date"] = sales_trend["Order Date"].dt.to_timestamp()
fig = px.line(sales_trend, x="Order Date", y="Sales", title="Monthly Sales Trend", markers=True)
st.plotly_chart(fig, use_container_width=True)


with col1:
    st.subheader(" Category wise Sales")
    fig =px.bar(category_df, x="Category" , y="Sales", text = ['${:,.2f}'.format(x) for x in category_df["Sales"]], template="seaborn")
    st.plotly_chart(fig,use_container_width=True, height=200)

with col2:
    st.subheader(" Region wise Sales")
    fig =px.pie(filtered_df, values= "Sales", names= "Region", hole= 0.5)
    fig.update_traces(text = filtered_df["Region"],textposition = "outside")
    st.plotly_chart(fig, use_container_width=True)

# Month-wise Sub-Category Sales Summary
st.subheader(":point_right: Month-wise Sub-Category Sales Summary")
filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
sub_category_Year = pd.pivot_table(
    data=filtered_df,
    values="Sales",
    index=["Sub-Category"],
    columns="month"
)
st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample = df[0:5][["Region","State","City","Category","Sales","Profit","Quantity"]]
    fig = ff.create_table(df_sample, colorscale = "Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data = filtered_df, values = "Sales", index = ["Sub-Category"],columns = "month")
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))



# Distribution Analysis
st.subheader(":point_right: Distribution of Sales and Profit")
col1, col2 = st.columns(2)
with col1:
    fig = px.histogram(df, x="Sales", nbins=50, title="Sales Distribution", marginal="box")
    st.plotly_chart(fig, use_container_width=True)
with col2:
    fig = px.histogram(df, x="Profit", nbins=50, title="Profit Distribution", marginal="box")
    st.plotly_chart(fig, use_container_width=True)


# Ensure required columns are present
if "latitude" in df.columns and "longitude" in df.columns:
    st.subheader(":point_right: Sales by Geography")
    
    # Verify the column names for consistency
    sales_col = "sales" if "sales" in df.columns else "Sales"
    region_col = "region" if "region" in df.columns else "Region"
    city_col = "city" if "city" in df.columns else "City"
    
    # Plot the geographical sales data
    fig = px.scatter_geo(
        df,
        lat="latitude",
        lon="longitude",
        color=region_col,
        size=sales_col,
        hover_name=city_col,
        title="Sales by Geography",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Latitude and Longitude columns are missing in the dataset.")

col3, col4 = st.columns(2)
# Region-wise Sales
with col3:
    st.subheader("Region-wise Sales")
if "Region" in filtered_df.columns:
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
    st.plotly_chart(fig, use_container_width=True)

# Top N Analysis
st.subheader(":point_right: Top States by Sales")
top_states = df.groupby("State")["Sales"].sum().nlargest(10).reset_index()
fig = px.bar(top_states, x="State", y="Sales", title="Top 10 States by Sales", text="Sales")
st.plotly_chart(fig, use_container_width=True)

# Create a scatter plot
data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
data1['layout'].update(
    title="Relationship between Sales and Profits using Scatter Plot.",
    titlefont=dict(size=20),
    xaxis=dict(title="Sales", titlefont=dict(size=19)),
    yaxis=dict(title="Profit", titlefont=dict(size=19))
)
st.plotly_chart(data1, use_container_width=True, key="scatter_plot")

with st.expander("View Data", expanded=False):
    st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap="Oranges"))



# For example, saving a sales trend plot as an image
fig1 = px.line(sales_trend, x="Order Date", y="Sales", title="Monthly Sales Trend", markers=True)
fig1.write_image(f"{image_dir}/sales_trend.png")

# Saving the Category wise Sales bar chart
fig2 = px.bar(category_df, x="Category", y="Sales", text=['${:,.2f}'.format(x) for x in category_df["Sales"]], template="seaborn")
fig2.write_image(f"{image_dir}/category_sales.png")

# Saving the Region wise Sales pie chart
fig3 = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
fig3.update_traces(text=filtered_df["Region"], textposition="outside")
fig3.write_image(f"{image_dir}/region_sales.png")

# Saving the Month-wise Sub-Category Sales Summary table (converted to an image)
sub_category_table_fig = ff.create_table(df_sample, colorscale="Cividis")
sub_category_table_fig.write_image(f"{image_dir}/sub_category_sales_summary.png")

# Create a zip file with all the images
zip_filename = "graphs.zip"
with zipfile.ZipFile(zip_filename, "w") as zipf:
    for root, _, files in os.walk(image_dir):
        for file in files:
            zipf.write(os.path.join(root, file), file)

# Provide a download button for the zip file
with open(zip_filename, "rb") as zip_file:
    st.download_button(
        label="Download All Graphs as Images",
        data=zip_file,
        file_name=zip_filename,
        mime="application/zip"
    )