import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Viet's Music", 
                   page_icon=":notes:", 
                   layout='wide')

@st.cache
def get_data():
    music_df = pd.read_csv('Apple Music Play Activity.csv')

    # add UTC offset to correct timezone
    music_df['UTC Offset In Seconds Delta'] = pd.to_timedelta(music_df['UTC Offset In Seconds'], 's')
    music_df['Event End Timestamp'] = pd.to_datetime(music_df['Event End Timestamp'], format='%Y-%m-%dT%H:%M:%S') + music_df['UTC Offset In Seconds Delta']
    music_df['Event Received Timestamp'] = pd.to_datetime(music_df['Event Received Timestamp'], format='%Y-%m-%dT%H:%M:%S') + music_df['UTC Offset In Seconds Delta']
    music_df['Event Start Timestamp'] = pd.to_datetime(music_df['Event Start Timestamp'], format='%Y-%m-%dT%H:%M:%S') + music_df['UTC Offset In Seconds Delta']

    return music_df

music_df = get_data()

st.header("""My personal music taste on Apple music over the years""")
st.markdown("Well, I do not use Apple music for years, but they provide the data available for downloading")
st.markdown("Inspriration from [Ashish Karhade/Apple Music Streaming analysis](https://deepnote.com/@ashish-karhade/Apple-Music-Streaming-analysis-RZehtt6QT5q1nWDC6mwXrQ)")

#
# METADATA
#
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

st.header("Overall info")

st.markdown(f"**File name**: `Apple Music Play Activity.csv`")
st.markdown(f"**Total data rows**: {len(music_df)}")
st.markdown(f"**Total songs**: {len(music_df['Content Name'].unique())}")
st.markdown(f"**Time from**: {music_df['Event Start Timestamp'].min().strftime(TIME_FORMAT)}")
st.markdown(f"**Time end**: {music_df['Event Start Timestamp'].max().strftime(TIME_FORMAT)}")

def top_agg(df, col, number=10):
    top_data = (music_df.groupby(col)[[col]]
              .agg(count=(col, 'count'))
              .sort_values(by='count', ascending=False)[:number]
             )
    return top_data

st.subheader("Peak into data")
st.dataframe(music_df.head(20))

#
# Details
#
st.subheader("Top songs")
top_15_song = top_agg(music_df, 'Content Name', 15)
st.bar_chart(top_15_song, height=500)

st.subheader("Top artists")
top_15_artist = top_agg(music_df, 'Artist Name', 15)
st.bar_chart(top_15_artist, height=500)

st.subheader("Songs listend for longest time")
top_longest_played = (music_df
    .groupby('Content Name')['Play Duration Milliseconds']
    .sum().sort_values(ascending=False)
    )[:15].to_frame("Minutes")
top_longest_played /= 60000
st.bar_chart(top_longest_played, height=666)


st.subheader("Genre")
top_15_genres = (music_df.groupby("Genre")
    .agg(songs=("Content Name", "nunique"))
    .sort_values(by="songs", ascending=False)
    )[:15]
st.bar_chart(top_15_genres, height=500)


st.subheader("Reasons to end")
select_genre = st.multiselect('Genre', music_df['Genre'].unique())
filter_df = music_df[music_df['Genre'].isin(select_genre)] if select_genre else music_df
fig = px.pie(filter_df, 
    names='End Reason Type')
st.plotly_chart(fig, use_container_width=True)
filter_df_agg = (filter_df
    .groupby('End Reason Type')
    .agg(songs=("Content Name", "nunique"))
    .sort_values(by="songs", ascending=False)
    )
st.dataframe(filter_df_agg)


st.subheader("Online / Offline")
fig = px.pie(filter_df, 
    names='Offline')
st.plotly_chart(fig, use_container_width=True)


st.subheader("Hours of day listened")
hours = music_df.groupby(music_df["Event Start Timestamp"].dt.hour).agg(count=("Event Start Timestamp", "count"))
st.bar_chart(hours, height=500)


st.subheader("Months listened")
months = music_df["Event Start Timestamp"].groupby(music_df["Event Start Timestamp"].dt.month).count()
md = months.to_dict()
data = {}
for key in range(1, 13):
    if key not in md:
        data[key] = 0
    else:
        data[key] = md[key]
df_months = pd.DataFrame.from_dict(data, orient='index', columns=['count'])

m = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov','Dec']
fig = px.bar(df_months, title="Most active Months", 
    text=m, 
    labels={"value": "count"})
fig.update_xaxes(dtick=1)
st.plotly_chart(fig, use_container_width=True)


st.subheader("Time spent")
total_time = music_df['Play Duration Milliseconds'].sum()
total_mins = total_time/60000
st.text("Total minutes spent: {:.2f} mins".format(total_mins))
total_hours = total_mins/60
st.text("Total hours spent: {:.2f} hours".format(total_hours))












