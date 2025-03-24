import time
import pandas as pd
import seaborn as sns
import streamlit as st
from matplotlib import pyplot as plt
from sqlalchemy import create_engine


def establish_connection() -> pd.DataFrame:
    """
    Establish a connection to the MySQL database and fetch movie data.

    Returns:
        pd.DataFrame: A DataFrame containing movie data from the database.
    """
    engine = create_engine(
        "mysql+mysqldb://root:tony123@localhost:3306/imdb_2024_genres"
    )
    conn = None
    try:
        conn = engine.connect()
        df = pd.read_sql('SELECT * FROM imdb_2024_genres.`movie_data`', conn)
        return df
    except Exception as e:
        st.write("Error: ", e)
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()


# Configure Streamlit page
st.set_page_config(
    layout="wide",
    page_icon=":material/directions_bus:",
    page_title="IMDB",
    initial_sidebar_state="expanded"
)

# Custom CSS for background styling
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://images.rawpixel.com/image_800/cHJpdmF0ZS9sci9pbWFnZXMvd2Vic2l0ZS8yMDIzLTA0L2pvYjE4MjktYmFja2dyb3VuZC1tay0wMDhnLmpwZw.jpg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        height: 100vh;
        width: 100vw;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Fetch data from the database
df = establish_connection()
if df.empty:
    st.stop()

# Display the brand banner image
st.image('IMDb_BrandBanner_1920x425.jpg', use_column_width=True)

# Create Tabs for Navigation
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ['Home', 'Genre Analysis', 'Duration Insights', 'Voting Trends', 'Rating Distribution']
)

# Group the DataFrame by 'Genre' and calculate averages
rating_avg = df.groupby('Genre')['Rating'].mean()
voting_avg = df.groupby('Genre')['Votes'].mean()
duration_avg = df.groupby('Genre')['Duration'].mean()

with tab1:
    st.header('IMDB 2024 Data Scraping and Visualizations')
    st.write(
        """
        This project focuses on extracting and analyzing movie data from IMDb for the year 2024.
        The task involves scraping data such as movie names, genres, ratings, voting counts,
        and durations from IMDb's 2024 movie list using Selenium. The data will then be organized
        genre-wise, saved as individual CSV files, and combined into a single dataset stored in
        an SQL database. Finally, the project will provide interactive visualizations and filtering
        functionality using Streamlit to answer key questions and allow users to customize their
        exploration of the dataset.
        """
    )

    st.subheader("Advanced Title Search")
    with st.form("my_form", clear_on_submit=True):
        select_genre = st.multiselect(
            "Select multiple genres:",
            df['Genre'].unique()
        )
        rating_start, rating_end = st.select_slider(
            "Select the rating:",
            options=sorted(df['Rating'].unique()),
            value=(df['Rating'].min(), df['Rating'].max())
        )
        duration_start, duration_end = st.select_slider(
            "Select the duration (minutes):",
            options=sorted(df['Duration'].unique()),
            value=(df['Duration'].min(), df['Duration'].max())
        )
        voting_start, voting_end = st.select_slider(
            "Select the voting:",
            options=sorted(df['Votes'].unique()),
            value=(df['Votes'].min(), df['Votes'].max())
        )

        filtered_df = df[
            (df['Genre'].isin(select_genre)) &
            (df['Rating'] >= rating_start) & (df['Rating'] <= rating_end) &
            (df['Duration'] >= duration_start) & (df['Duration'] <= duration_end) &
            (df['Votes'] >= voting_start) & (df['Votes'] <= voting_end)
        ]

        st.write("Click the submit button for the filtered dataframe:")
        if st.form_submit_button("Submit"):
            with st.status("Data fetched for you!!", expanded=True):
                time.sleep(1)
                st.dataframe(
                    filtered_df,
                    hide_index=True,
                    use_container_width=True
                )
                if filtered_df.empty:
                    st.error(
                        'Oops!! No data found for the selected filters. Please try again with different filters.'
                    )
                else:
                    st.success(
                        'Successfully retrieved movies data for you!!!', icon="✅"
                    )

with tab2:
    st.header('Genre Analysis')
    st.write(
        """
        Welcome! This page explores the distribution of movies across different genres,
        revealing which types of films dominate the industry. The data, visualized in the chart below,
        clearly illustrates the popularity of certain genres while highlighting the underrepresentation
        of others. Dive in to see the trends and discover the fascinating landscape of movie genres.
        """
    )

    if 'Genre' in df.columns:
        st.subheader("Identify the unique genres in the dataset.")
        nunique_genres = df['Genre'].nunique()
        st.write(
            "The number of unique genres in the dataset are:",
            nunique_genres)
        unique_values = df['Genre'].value_counts().sort_index()

        col1, col2 = st.columns(2)
        with col1:
            st.write("Genres and their respective counts:")
            st.dataframe(unique_values, width=250)
        with col2:
            with st.expander("Insights:"):
                st.write(
                    "1. **Drama is the most:** There are way more drama movies than any other type listed.")
                st.write(
                    "2. **Comedy is second:** Comedy is the next most common type of movie.")
                st.write(
                    "3. **Action is also up there:** Action movies are fairly popular too.")
                st.write("4. **Many genres have few movies:** Genres like Game-Show, News, Talk-Show, War, and Western have very few movies compared to Drama, Comedy, and Action.")

        st.subheader(
            "Visualize the distribution of movies across genres using a bar plot.")
        fig, ax = plt.subplots()
        ax.bar(unique_values.index, unique_values.values)
        ax.set_xlabel('Genre')
        ax.set_ylabel('No. of Movies')
        ax.set_title('Distribution of Movies Across Genres')
        ax.set_xticklabels(unique_values.index, rotation=45)
        ax.legend(['Movies'])
        ax.bar_label(ax.containers[0], fontsize=8, padding=3)
        st.pyplot(fig)
        with st.expander("Insights"):
            st.write(
                "1. **Lots of drama movies:** The biggest takeaway is that there are way more drama movies than any other type.")
            st.write(
                "2. **Comedy is also popular:** Comedy movies are the second most common.")
            st.write(
                "3. **Few movies in other genres:** Things like Westerns, War movies, and News movies are made much less often.")
            st.write(
                "4. **Drama is king:** Drama is by far the most popular genre shown in this graph.")

        st.subheader(
            "Calculate the average rating and voting count for each genre.")
        col1, col2 = st.columns(2)
        with col1:
            st.write("The average rating for each genre is:")
            st.dataframe(rating_avg, width=250)
        with col2:
            st.write("The average voting count for each genre is:")
            st.dataframe(voting_avg, width=250)

        st.subheader("Display the top 5 genres based on average rating.")
        col1, col2 = st.columns(2)
        with col1:
            top_rating = rating_avg.sort_values(ascending=False).head(5)
            st.dataframe(top_rating, width=250)
        with col2:
            with st.expander("Insights:"):
                st.write(
                    "*Talk-Show* has the highest average rating, followed by news and game-show.")

        st.subheader("Display the top 5 genres based on highest voting count.")
        col1, col2 = st.columns(2)
        with col1:
            top_voting = voting_avg.sort_values(ascending=False).head(5)
            st.dataframe(top_voting, width=250)
        with col2:
            with st.expander("Insights:"):
                st.write(
                    "The genres with the highest average voting counts are *Action*, followed by crime.")
    else:
        st.write("The 'Genre' column does not exist in the dataset.")

with tab3:
    st.header('Duration Insights')
    st.write(
        """
        Welcome to our exploration of movie durations! Have you ever wondered why some films feel just right
        while others drag on or end too quickly? This page delves into the fascinating world of movie runtimes,
        examining how length impacts storytelling, audience engagement, and even the business of filmmaking.
        From epic sagas to concise comedies, we'll uncover the trends, averages, and secrets behind how long
        movies really are.
        """
    )

    if 'Duration' in df.columns:
        st.subheader("Analyze the average duration of movies across genres.")
        col1, col2 = st.columns(2)
        with col1:
            st.write("The average duration for each genre is:")
            st.dataframe(duration_avg, width=250)
        with col2:
            with st.expander("Insights:"):
                st.write(
                    "1. **Action & Crime are longest:** Action and Crime movies tend to have the longest runtimes.")
                st.write(
                    "2. **Family & Comedy are shortest:** Family and Comedy movies are generally shorter.")
                st.write(
                    "3. **Big difference in Game-Show:** Game-Show durations are unusually long compared to others.")
                st.write(
                    "4. **News is short:** News programs have the shortest average duration.")
                st.write(
                    "5. **Similar lengths for many:** Action, Crime, Drama, and War movies have fairly similar average lengths.")

        st.subheader(
            "Analyze the relationship between movie duration and rating.")
        fig, ax = plt.subplots()
        sns.scatterplot(data=df, x="Duration", y="Rating", alpha=0.5, ax=ax)
        plt.xlabel("Movie Duration (minutes)")
        plt.ylabel("Rating")
        plt.title("Relationship between Movie Duration and Rating")
        plt.autoscale()
        st.pyplot(fig)
        with st.expander("Insights:"):
            st.write(
                "1. **No clear pattern:** There doesn't seem to be a strong relationship between movie duration and rating.")
            st.write(
                "2. **Mostly clustered:** Movies are mostly clustered between 90-150 minutes.")
            st.write(
                "3. **Few outliers:** There are a few outliers with very high ratings and durations.")
            st.write(
                "4. **No clear trend:** There is no clear trend between movie duration and rating.")

        st.subheader(
            "Identify the longest and shortest movies in the dataset.")
        longest_movie = df.sort_values(by='Duration', ascending=False).head(5)
        st.write("The longest movie in the dataset is:")
        st.dataframe(longest_movie, use_container_width=True, hide_index=True)
        with st.expander("Insights:"):
            st.write(
                """
                ***Phantosmia** is a drama film with a rating of 7.4 based on 24 votes, and it has a notably long duration of 250 minutes.
                This extended runtime suggests a potentially epic or deeply developed narrative, which may be contributing to its relatively
                positive reception among the small group of voters. However, the limited number of votes indicates that it might not be widely
                known or watched, despite the decent rating.
                """
            )
        shortest_movie = df.sort_values(by='Duration', ascending=True).head(5)
        st.write("The shortest movie in the dataset is:")
        st.dataframe(shortest_movie, use_container_width=True, hide_index=True)
        with st.expander("Insights:"):
            st.write(
                "1. This data snippet reveals five action movies with varying levels of popularity and critical reception.")
            st.write('2. "Big City Greens the Movie: Spacecation" stands out with the most votes (509) and a decent rating of 6.2, suggesting wider viewership and generally positive feedback.')
            st.write('3. "The Unbreakable Bunch" and "Wolf Warriors" received higher ratings (7.7 and 7.8 respectively), but with significantly fewer votes, indicating a smaller audience base, though those who watched them seemed to enjoy them more.')
            st.write('4. "How to Make a Werewolf" garnered a modest 5.9 rating with 78 votes, while "Framed" received the lowest rating (4.8) and a moderate number of votes (67), suggesting mixed-to-negative reception from its viewers. Notably, all movies have a duration of 0, which likely indicates missing data rather than actual film length.')
    else:
        st.write("The 'Duration' column does not exist in the dataset.")

with tab4:
    st.header('Voting Trends')
    st.write(
        """
        Welcome to our hub for movie voting! Your opinion matters. Here, you can rate and review films,
        contributing to a collective voice that helps others discover great cinema and understand what resonates
        with audiences. Explore our listings, cast your votes, and see how your favorites stack up against the rest.
        """
    )

    if 'Votes' in df.columns:
        st.subheader(
            "Analyze the relationship between movie duration and voting count.")
        fig, ax = plt.subplots()
        sns.scatterplot(data=df, x="Duration", y="Votes", alpha=0.5, ax=ax)
        plt.xlabel("Movie Duration (minutes)")
        plt.ylabel("Voting Count")
        plt.title("Relationship between Movie Duration and voting count")
        plt.autoscale()
        st.pyplot(fig)
        with st.expander("Insights:"):
            st.write(
                "1. **No clear trend:** How long a movie is doesn't clearly predict how many votes it gets.")
            st.write(
                "2. **Most movies clustered:** Most movies are between 80-120 minutes long and receive fewer votes.")
            st.write(
                "3. **A few long movies get lots of votes:** Some movies over 150 minutes have high vote counts.")
            st.write(
                "4. **One very long, popular movie:** One movie around 160 minutes has an exceptionally high vote count.")
            st.write(
                "5. **Short movies get few votes:** Movies under 80 minutes generally have low vote counts.")

        st.subheader("Identify the movies with the highest voting counts.")
        sorting_vote = df.sort_values(by='Votes', ascending=False).head(5)
        st.write("The highest voted in the dataset is:")
        st.dataframe(sorting_vote, use_container_width=True, hide_index=True)
        with st.expander("Insights:"):
            st.write(
                "1. **Dune is most popular:** 'Dune: Part Two' has the most votes.")
            st.write(
                "2. **Dune has high rating:** 'Dune: Part Two' also has the highest rating.")
            st.write(
                "3. **Deadpool is second:** 'Deadpool & Wolverine' is second most popular, second highest rated.")
            st.write(
                "4. **Furiosa is in the mix:** 'Furiosa' has decent votes and rating.")
            st.write(
                "5. **Dune is long:** 'Dune: Part Two' is the longest movie listed.")

        st.subheader("Display the top 5 movies with the lowest voting counts.")
        sorting_low_vote = df.sort_values(by='Votes', ascending=True).head(5)
        st.write("The highest voted in the dataset is:")
        st.dataframe(
            sorting_low_vote,
            use_container_width=True,
            hide_index=True)
        with st.expander("Insights:"):
            st.write(
                "1. **Dune is most popular:** 'Dune: Part Two' has the most votes.")
            st.write(
                "2. **Dune has high rating:** 'Dune: Part Two' also has the highest rating.")
            st.write(
                "3. **Deadpool is second:** 'Deadpool & Wolverine' is second most popular, second highest rated.")
            st.write(
                "4. **Furiosa is in the mix:** 'Furiosa' has decent votes and rating.")
            st.write(
                "5. **Dune is long:** 'Dune: Part Two' is the longest movie listed.")

        st.subheader(
            "Visualize the voting distribution using a histogram along with genres.")
        fig, ax = plt.subplots()
        sns.barplot(data=df, x="Genre", y="Votes", hue="Genre", ax=ax)
        plt.ylabel("Voting Count")
        plt.xlabel("Genre")
        plt.title("Voting Distribution by Genre")
        plt.xticks(rotation=45)
        plt.autoscale()
        st.pyplot(fig)
        with st.expander("Insights:"):
            st.write(
                "1. **Action most votes:** Action movies get the most votes overall.")
            st.write(
                "2. **Comedy, Crime next:** Comedy and Crime also have a lot of votes.")
            st.write(
                "3. **Drama, Family similar:** Drama and Family genres have comparable vote counts.")
            st.write(
                "4. **Everything else low:** Game-Show, News, Talk-Show, War, and Western get very few votes.")
            st.write(
                "5. **Big drop-off:** There's a huge difference in votes between the top genres and the bottom ones.")
    else:
        st.write("The 'Votes' column does not exist in the dataset.")

with tab5:
    st.header('Rating Distribution')
    st.write(
        """
        Welcome to our comprehensive guide to movie ratings! Here, you'll find everything you need to know about
        how movies are rated, from understanding the different rating systems to exploring the impact ratings have
        on audiences and the film industry. Dive into our resources and become a rating expert.
        """
    )

    if 'Rating' in df.columns:
        st.subheader(
            "Analyze the relationship between movie rating and voting count.")
        fig, ax = plt.subplots()
        sns.scatterplot(data=df, x="Rating", y="Votes", alpha=0.5, ax=ax)
        plt.xlabel("Rating")
        plt.ylabel("Voting Count")
        plt.title("Relationship between Movie Rating and voting count")
        plt.autoscale()
        st.pyplot(fig)
        with st.expander("Insights:"):
            st.write(
                "1. **Higher ratings get more votes:** Movies with higher ratings tend to get more votes.")
            st.write(
                "2. **Mostly clustered:** Most movies are rated between 6-8 and have fewer votes.")
            st.write(
                "3. **Few outliers:** There are a few movies with very high ratings and vote counts.")
            st.write(
                "4. **No clear trend:** There is no clear trend between movie rating and voting count.")

        st.subheader(
            "Identify the movies with the highest and lowest ratings.")
        rating_bar = df.sort_values(by='Rating', ascending=False)
        st.write("The highest rated movie in the dataset is:")
        st.dataframe(
            rating_bar.head(5),
            use_container_width=True,
            hide_index=True)
        with st.expander("Insights:"):
            st.write(
                "1. **Talk-Show is top:** 'The Talk' is the highest rated movie.")
            st.write(
                "2. **News is second:** 'The News' is the second highest rated movie.")
            st.write(
                "3. **Game-Show is third:** 'The Game Show' is the third highest rated movie.")
            st.write(
                "4. **Drama is fourth:** 'The Drama' is the fourth highest rated movie.")
            st.write(
                "5. **Action is fifth:** 'The Action' is the fifth highest rated movie.")

        st.write("The lowest rated movie in the dataset is:")
        st.dataframe(
            rating_bar.tail(5),
            use_container_width=True,
            hide_index=True)
        with st.expander("Insights:"):
            st.write(
                "1. **Western is lowest:** 'The Western' is the lowest rated movie.")
            st.write(
                "2. **War is second:** 'The War' is the second lowest rated movie.")
            st.write(
                "3. **Talk-Show is third:** 'The Talk-Show' is the third lowest rated movie.")
            st.write(
                "4. **News is fourth:** 'The News' is the fourth lowest rated movie.")
            st.write(
                "5. **Game-Show is fifth:** 'The Game-Show' is the fifth lowest rated movie.")

        st.subheader("Visualize the rating distribution in genres.")
        fig, ax = plt.subplots()
        sns.barplot(data=df, x="Genre", y="Rating", hue="Genre", ax=ax)
        plt.ylabel("Rating")
        plt.xlabel("Genre")
        plt.title("Average Rating Distribution by Genre")
        plt.xticks(rotation=45)
        plt.autoscale()
        st.pyplot(fig)
        with st.expander("Insights:"):
            st.write(
                "1. **Talk-Show highest:** Talk-Show movies have the highest average rating.")
            st.write(
                "2. **News is second:** News movies are the second highest rated.")
            st.write(
                "3. **Game-Show is third:** Game-Show movies are the third highest rated.")
            st.write(
                "4. **Drama is fourth:** Drama movies are the fourth highest rated.")
            st.write(
                "5. **Action is fifth:** Action movies are the fifth highest rated.")
    else:
        st.write("The 'Rating' column does not exist in the dataset.")
