# Import the packages:
import pandas as pd
import psycopg2
from datetime import date
import streamlit as st
import plotly.express as px
# DB connection
def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="earthquakedb",
        user="postgres",
        password="AJV06",
        port="5432"
    )

# run_querry cmd:
def run_query(sql):
    conn=get_connection() # get connect to DB
    cur=conn.cursor()  # to get query get variable

    cur.execute(sql)  # run the query given
    result= cur.fetchone()[0] # fetch a single single row
    
    cur.close()
    conn.close()
    return result

# Read CSV file as dataframe:
df = pd.read_csv("earthquake_clean_data1.csv")

##### SQL QUERIES ####
# MAGNITUDE & DEPTH:

def sql_qry_mag_dep():
    conn=get_connection()
    queries={
          "0. All Data":"SELECT * FROM earthquake_clean_data",
          "1. Strongest Earthquake":"SELECT * FROM earthquake_clean_data WHERE mag BETWEEN 6.0 AND 6.9 ORDER BY mag DESC LIMIT 10",
          "2. Deepest Earthquake":"SELECT * FROM earthquake_clean_data WHERE depth_km>300.00 ORDER BY depth_km DESC LIMIT 10",
          "3. Shallow Earthquake":"SELECT country, mag FROM earthquake_clean_data WHERE depth_cat = 'Shallow' GROUP BY country,mag ORDER BY country DESC",
          "4. Avergae Depth per Continent":"SELECT Continent,ROUND(AVG(depth_km),2) AS depth_avg FROM earthquake_clean_data WHERE type='earthquake' GROUP BY Continent ORDER BY depth_avg",
          "5. Average Magnitude per magType":"SELECT magtype, AVG(mag) FROM earthquake_clean_data GROUP BY magtype ORDER BY magtype ",
}
    st.title("ANALYSIS THROUGH MAGNITUDE & DEPTH:")
    select_qry=st.selectbox("Select Magnitude & Depth Analysis Report",list(queries.keys()))
    df=pd.read_sql(queries[select_qry],conn)
    st.dataframe(df)

# TIME ANALYSIS:

def sql_qry_time_analysis():
    conn=get_connection()
    queries={
          "1. Year with most Earthquakes":"SELECT year,COUNT(type) AS earthquake_count FROM earthquake_clean_data WHERE type='earthquake'GROUP BY year ORDER BY year DESC", 
          "2. Most of the Earthquake in Months":"SELECT month_name,COUNT(*) FROM earthquake_clean_data WHERE type='earthquake' GROUP BY month_name ORDER BY count DESC",
          "3. Day with Most Earthquake":"SELECT year,day_name,COUNT(day_name) AS total_earthquake FROM earthquake_clean_data WHERE type='earthquake'GROUP BY year,day_name ORDER BY total_earthquake DESC",
          "4. No.of Earthquake/hr":"SELECT EXTRACT(HOUR FROM time) AS hour, time::date AS date, COUNT(*) AS earthquake_count FROM earthquake_clean_data WHERE type = 'earthquake' GROUP BY hour, date ORDER BY date",
          "5. Most Active Network": "SELECT net,COUNT(net) AS active_net FROM earthquake_clean_data WHERE type='earthquake' GROUP BY net ORDER BY active_net DESC LIMIT 3"
    }

    st.title("TIME ANALYSIS")
    select_qry=st.selectbox("Select Time Analysis",list(queries.keys()))
    df=pd.read_sql(queries[select_qry],conn)
    st.dataframe(df)

# CASUALITIES:
def sql_qry_casualities():
    conn=get_connection()
    queries={
        "1. Highest Casulities (Top 5)":"""SELECT Country,mag FROM earthquake_clean_data 
                                           WHERE type='earthquake' AND mag>6.0 
                                           AND Country IN (SELECT Country FROM earthquake_clean_data
                                                      WHERE type='earthquake' AND depth_km > 300.00)
                                           ORDER BY mag DESC""" 
    }

    st.title("CASUALITIES")
    select_qry=st.selectbox("Select Analysis",list(queries.keys()))
    df=pd.read_sql(queries[select_qry],conn)
    st.dataframe(df)
    
# EVENT TYPE & QUALITY METRICS:
def sql_qry_event_quality():
    conn=get_connection()
    queries={
          "1. Reviewed & Automatic Count":"SELECT status,COUNT(status) AS status_count FROM earthquake_clean_data WHERE type='earthquake' GROUP BY status",
          "2. Count of Earthquake Type":"SELECT type,COUNT(*) FROM earthquake_clean_data WHERE type='earthquake' GROUP BY type",
          "3. Count of Earthquake Data Types":"SELECT types,COUNT(types) AS types_count FROM earthquake_clean_data WHERE type='earthquake' GROUP BY types",
          "4. Average RMS and Gap":"SELECT Country, AVG(rms) AS avg_rms, AVG(gap) AS avg_gap FROM earthquake_clean_data WHERE type='earthquake' GROUP BY Country ORDER BY Country DESC",
          "5. Events with High Station Coverage":"SELECT Country, nst FROM earthquake_clean_data WHERE mag>=6.0 GROUP BY Country,nst ORDER BY nst DESC"
    }

    st.title("EVENT TYPE & QUALITY METRICS")
    select_qry=st.selectbox("Select Event Type & Quality Metrics",list(queries.keys()))
    df=pd.read_sql(queries[select_qry],conn)
    st.dataframe(df)

#TSUNAMI & ALERTS:
def sql_qry_tsunami_alert():
    conn=get_connection()
    queries={
          "1. No.of Tsunami Alerts":"SELECT Country,year,COUNT(tsunami) AS tsunami_count FROM earthquake_clean_data GROUP BY Country,year ORDER BY year",
          "2. Count Earthquake By Alert Levels":"""SELECT
                                                    CASE 
	                                                    WHEN mag <= 5.4 AND depth_km>70 THEN 'GREEN'
	                                                    WHEN mag>=5.5 AND mag<=6.4 AND depth_km<=70 THEN 'YELLOW'
	                                                    WHEN mag >=6.5 AND mag<=7.0 AND depth_km<=70 THEN 'ORANGE'
	                                                    WHEN mag>=6.5 AND mag<=7.0 AND depth_km>70 THEN 'YELLOW'
	                                                    WHEN mag >7.0 AND depth_km>70 THEN 'ORANGE'
	                                                    ELSE 'RED'
                                                        END AS earthquake_alert,
                                                        COUNT(*) AS alert_signal
                                                    FROM earthquake_clean_data
                                                    WHERE type='earthquake'
                                                    GROUP BY earthquake_alert
                                                    ORDER BY alert_signal DESC"""
    }
    st.title("TSUNAMI & ALERTS")
    select_qry=st.selectbox("Select Tsunami Alerts",list(queries.keys()))
    df=pd.read_sql(queries[select_qry],conn)
    st.dataframe(df)

#SEISMIC PATTERN & TREND ANALYSIS:

def sql_qry_trend_ana():
    conn=get_connection()
    queries={
          "1. TOP 5 Country with AVG_MAG":"SELECT Country, AVG(mag) AS mag_avg FROM earthquake_clean_data WHERE type='earthquake' GROUP BY Country ORDER BY mag_avg DESC LIMIT 5",
          "2. Country with Shallow & Deep in same month":"SELECT Country,month_name,COUNT(*) FILTER (WHERE depth_cat = 'Shallow') AS shallow_count, COUNT(*) FILTER (WHERE depth_cat = 'Deep') AS deep_count FROM earthquake_clean_data WHERE type = 'earthquake' GROUP BY Country, month, month_name HAVING COUNT(*) FILTER (WHERE depth_cat = 'Shallow') > 0 AND COUNT(*) FILTER (WHERE depth_cat = 'Deep') > 0 ORDER BY month ASC",
          "3. Tot.Earthquake over by over year":"SELECT year, COUNT(*) AS total_earthquakes FROM earthquake_clean_data WHERE type = 'earthquake'GROUP BY year ORDER BY year",
          "4. Seismically Active Earthquake(3)":"SELECT Country,COUNT(Country) AS frequency, ROUND(AVG(mag),3) AS mag_avg FROM earthquake_clean_data WHERE type='earthquake' GROUP BY Country ORDER BY frequency DESC LIMIT 3"

    }

    st.title("SEISMIC PATTERN & TREND ANALYSIS")
    select_qry=st.selectbox("Select Pattern & Trend Analysis",list(queries.keys()))
    df=pd.read_sql(queries[select_qry],conn)
    st.dataframe(df)

# DEPTH, DIST, LOCATION - ANALYSIS:

def consecutive_pair():
    return """ SELECT o.Country,o.consecutive_pair
                           FROM(
                           SELECT
                            Country, event_date,pre_date,event_time,pre_time,pre_id,distance_km, pre_dist,
                                CASE
                                    WHEN event_date = pre_date
                                    THEN event_time - pre_time
                                    ELSE NULL
                                END AS time_interval,
	                            CASE
	                                WHEN event_date=pre_date 
		                            THEN distance_km - pre_dist
	                            END AS btw_dist,
	                            CASE 
		                            WHEN event_date=pre_date THEN CONCAT(pre_id,' & ',id)
	                            END AS consecutive_pair
                                FROM (
                                        SELECT id, Country, event_date,event_time, distance_km,

                                        LAG(event_date) OVER (
                                                PARTITION BY Country,event_date
                                                ORDER BY event_date, event_time
                                        ) AS pre_date,

                                        LAG(event_time) OVER (
                                                PARTITION BY Country
                                                ORDER BY event_date, event_time
                                        ) AS pre_time,

   		                                LAG(distance_km) OVER( PARTITION BY Country
		                                        ORDER BY event_date,distance_km) AS pre_dist,

		                                LAG(id) OVER( PARTITION BY Country
		                                        ORDER BY event_date) AS pre_id
                                        FROM earthquake_clean_data  WHERE type='earthquake') AS t )AS o
                                    WHERE o.event_date=o.pre_date AND o.btw_dist < 50 AND o.time_interval < INTERVAL '1 Hour'
                                    ORDER BY Country, event_date, event_time;"""
    
def sql_qry_dist_loc():
    conn=get_connection()
    queries={
          "1. Depth of Earthquake between Latitude -5 to +5":"SELECT Country, ROUND(AVG(depth_km),3) AS avg_depth FROM earthquake_clean_data WHERE type='earthquake' AND latitude BETWEEN -5.0000 and 5.0000 GROUP BY Country ORDER BY avg_depth DESC",
          "2. Country with high ratio of Shallow and Deep":"SELECT Country,COUNT(depth_cat) AS dep_count FROM earthquake_clean_data WHERE type='earthquake' AND depth_cat IN('Shallow','Deep') GROUP BY Country ORDER BY Country" ,
          "3. Earthquake with/without Tsunami":"""SELECT DISTINCT tsunami_status,
                                                    ROUND(AVG(mag) OVER (PARTITION BY tsunami_status),3) AS avg_magnitude 
                                                    FROM (
                                                    SELECT 
                                                    CASE 
                                                        WHEN tsunami = 1 THEN 'Earthquake With Tsunami' 
                                                        WHEN tsunami = 0 THEN 'Earthquake Without Tsunami'
                                                        END AS tsunami_status, mag
                                                        FROM earthquake_clean_data
                                                        WHERE type = 'earthquake'
                                                    ) AS e""", 
          "4. Low Reliable Data(using gap & rms)":"""SELECT place, gap, ROUND(rms, 2) AS rms
                                                     FROM earthquake_clean_data
                                                     WHERE type = 'earthquake'
                                                        AND gap > (
                                                        SELECT AVG(gap)
                                                        FROM earthquake_clean_data
                                                        WHERE type = 'earthquake'
                                                        )
                                                        AND rms > (
                                                        SELECT AVG(rms)
                                                        FROM earthquake_clean_data
                                                        WHERE type = 'earthquake'
                                                        )
                                                     ORDER BY gap DESC, rms DESC""",
          "5. Pairs Of Consecutive Earthquake in 50km":consecutive_pair(),
          "6. Highest Deep Focus Earthquake Region":"SELECT Country, COUNT(depth_cat) AS freq_deep FROM earthquake_clean_data WHERE type='earthquake' AND depth_cat = 'Deep' GROUP BY Country ORDER BY freq_deep DESC LIMIT 3"
    }
    st.title("DEPTH, DIST, LOCATION - ANALYSIS")
    select_qry=st.selectbox("Select Geographical Feature Analysis",list(queries.keys()))
    df=pd.read_sql(queries[select_qry],conn)
    st.dataframe(df)

def select_ana():
    conn=get_connection()
    df_c=pd.read_sql("SELECT depth_cat,COUNT(depth_cat) AS depth_count FROM earthquake_clean_data WHERE type='earthquake' GROUP BY depth_cat",conn)
    st.subheader("***Depth Analysis of Seismic Wave***")
    fig= px.pie(df_c,
                    names="depth_cat",
                    values="depth_count",
                    hole=0.5
                    )
    fig.update_traces(textinfo="label+value")
    st.plotly_chart(fig,use_container_width=True)



# DASHBOARD:

#st.title("Welcome to Seismic Dashboard")
st.markdown("<h1 style='color:violet; font-family:Georgia; font-align:center;'>""Global Seismic Analysis 🌍📊""</h1>",
                   unsafe_allow_html=True )

# SIDE BAR DASHBOARD:

st.sidebar.markdown(
    "<h1 style='color:red; font-family:Arial; font-align:left; font-weight: bold; font-style: italic;'>""Welcome to Seismic Dashboard !""</h1>",
    unsafe_allow_html=True
)
#st.sidebar.write("Show Analysis Report for:")
report=["SELECT ANALYSIS","ANALYSIS THROUGH MAGNITUDE & DEPTH","TIME ANALYSIS","CASUALITIES","EVENT TYPE & QUALITY METRICS","TSUNAMI & ALERTS","SEISMIC PATTERN & TREND ANALYSIS","DEPTH, DIST, LOCATION - ANALYSIS"]
rep= st.sidebar.selectbox ("**Show Analysis Report for:**",report)

if rep == "SELECT ANALYSIS":
    col1,col2=st.columns(2)
    with col1:
        st.metric("Country", df["Country"].nunique())
    with col2:
        st.metric("Seismic Station",df["nst"].nunique())
    #st.dataframe(df)

    select_ana()

elif rep =="ANALYSIS THROUGH MAGNITUDE & DEPTH":
    sql_qry_mag_dep()
elif rep == "TIME ANALYSIS":
    sql_qry_time_analysis()
elif rep =="CASUALITIES":
    sql_qry_casualities()
elif rep == "EVENT TYPE & QUALITY METRICS":
    sql_qry_event_quality()
elif rep == "TSUNAMI & ALERTS":
    sql_qry_tsunami_alert()
elif rep == "SEISMIC PATTERN & TREND ANALYSIS":
    sql_qry_trend_ana()
else :
    sql_qry_dist_loc()










