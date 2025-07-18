import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

# Configure Streamlit page
st.set_page_config(
    page_title="Inside Airbnb Dashboard",
    page_icon="🏠",
    layout="wide"
)

# Load and clean data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("listings.csv")
        # Clean and preprocess the data
        df = df.dropna(subset=['price', 'latitude', 'longitude', 'room_type', 'neighbourhood_cleansed'])
        
        # Clean price column - remove $ and commas, convert to float
        df['price'] = df['price'].replace('[\\$,]', '', regex=True).astype(float)
        
        # Filter out extreme outliers (prices > $1000 or < $10)
        df = df[(df['price'] >= 10) & (df['price'] <= 1000)]
        
        return df
    except FileNotFoundError:
        st.error("❌ listings.csv file not found. Please make sure the file is in the same directory as this script.")
        return None
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return None

# Load data
df = load_data()

if df is not None:
    # Sidebar
    st.sidebar.title("🏠 Filters")
    st.sidebar.markdown("---")
    
    # Sidebar Filters
    st.sidebar.subheader("📍 Location")
    neighborhood = st.sidebar.selectbox(
        "Select Neighborhood", 
        ['All'] + sorted(df['neighbourhood_cleansed'].unique()),
        help="Choose a specific neighborhood or 'All' to see all areas"
    )
    
    st.sidebar.subheader("🏡 Property Type")
    room_type = st.sidebar.selectbox(
        "Select Room Type", 
        ['All'] + sorted(df['room_type'].unique()),
        help="Filter by type of accommodation"
    )
    
    st.sidebar.subheader("💰 Price Range")
    price_min, price_max = st.sidebar.slider(
        "Select Price Range (per night)", 
        int(df['price'].min()), 
        int(df['price'].max()), 
        (50, 300),
        help="Adjust the price range you're interested in"
    )
    
    # Apply filters
    filtered = df.copy()
    
    if neighborhood != 'All':
        filtered = filtered[filtered['neighbourhood_cleansed'] == neighborhood]
    
    if room_type != 'All':
        filtered = filtered[filtered['room_type'] == room_type]
    
    filtered = filtered[filtered['price'].between(price_min, price_max)]
    
    # Main content
    st.title("🏠 Inside Airbnb Dashboard")
    st.markdown("### Explore Airbnb listings with interactive visualizations")
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Listings", len(filtered))
    with col2:
        st.metric("Average Price", f"${filtered['price'].mean():.0f}")
    with col3:
        st.metric("Average Reviews", f"{filtered['number_of_reviews'].mean():.1f}")
    with col4:
        st.metric("Neighborhoods", filtered['neighbourhood_cleansed'].nunique())
    
    if len(filtered) == 0:
        st.warning("⚠️ No listings found with the current filters. Please adjust your criteria.")
    else:
        # Create tabs for different visualizations
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Price Analysis", "📈 Reviews vs Price", "🗺️ Geographic Map", "🏘️ Neighborhood Insights"])
        
        with tab1:
            st.subheader("Average Price by Room Type")
            
            # Calculate data for the neighborhood context
            comparison_data = df.copy() if neighborhood == 'All' else df[df['neighbourhood_cleansed'] == neighborhood]
            
            bar = alt.Chart(comparison_data).mark_bar().encode(
                x=alt.X('room_type:N', title='Room Type', sort='-y'),
                y=alt.Y('mean(price):Q', title='Average Price ($)'),
                color=alt.Color('room_type:N', scale=alt.Scale(scheme='category10')),
                tooltip=['room_type:N', 'mean(price):Q']
            ).properties(
                width='container',
                height=400,
                title=f"Average Price by Room Type{' - ' + neighborhood if neighborhood != 'All' else ''}"
            )
            
            st.altair_chart(bar, use_container_width=True)
        
        with tab2:
            st.subheader("Price vs Number of Reviews")
            
            scatter = alt.Chart(filtered).mark_circle(size=60, opacity=0.7).encode(
                x=alt.X('price:Q', title='Price per Night ($)'),
                y=alt.Y('number_of_reviews:Q', title='Number of Reviews'),
                color=alt.Color('room_type:N', scale=alt.Scale(scheme='category10')),
                size=alt.Size('accommodates:Q', scale=alt.Scale(range=[50, 200])),
                tooltip=['name:N', 'price:Q', 'number_of_reviews:Q', 'room_type:N', 'accommodates:Q']
            ).interactive().properties(
                width='container',
                height=500,
                title="Explore the relationship between price and popularity"
            )
            
            st.altair_chart(scatter, use_container_width=True)
        
        with tab3:
            st.subheader("Geographic Distribution of Listings")
            
            # Limit map data for performance
            map_data = filtered.sample(min(500, len(filtered))) if len(filtered) > 500 else filtered
            
            if len(map_data) > 0:
                # Create columns for the map and legend
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown("**🗺️ Interactive Map of Albany Airbnb Listings**")
                    
                    # Prepare data for Streamlit's native map
                    map_df = map_data[['latitude', 'longitude', 'price', 'name', 'neighbourhood_cleansed', 'number_of_reviews']].copy()
                    
                    # Create color mapping based on price ranges
                    def get_price_color(price):
                        if price < 75:
                            return '#2E8B57'  # Sea Green - Cheap
                        elif price < 150:
                            return '#FFD700'  # Gold - Medium
                        elif price < 250:
                            return '#FF8C00'  # Dark Orange - Expensive
                        else:
                            return '#DC143C'  # Crimson - Very Expensive
                    
                    map_df['color'] = map_df['price'].apply(get_price_color)
                    
                    # Use Streamlit's built-in map (shows actual geographic map)
                    st.map(map_df, latitude='latitude', longitude='longitude', size='price', color='color')
                
                with col2:
                    st.markdown("**📊 Map Legend**")
                    st.markdown("- **Size**: Proportional to price")
                    st.markdown("- **Zoom**: Use mouse wheel")
                    st.markdown("- **Pan**: Click and drag")
                    
                    # Color legend
                    st.markdown("**🎨 Price Colors**")
                    st.markdown("🟢 Under $75 - Budget")
                    st.markdown("🟡 $75-$149 - Medium")  
                    st.markdown("🟠 $150-$249 - Premium")
                    st.markdown("🔴 $250+ - Luxury")
                    
                    # Price distribution info
                    st.markdown("**💰 Price Stats**")
                    st.write(f"Min: ${map_data['price'].min():.0f}")
                    st.write(f"Max: ${map_data['price'].max():.0f}")
                    st.write(f"Avg: ${map_data['price'].mean():.0f}")
                
                # Alternative detailed map using Altair for more customization
                st.markdown("---")
                st.markdown("**📍 Detailed Interactive Chart**")
                
                # Create a more detailed scatter plot map
                detailed_map = alt.Chart(map_data).mark_circle(opacity=0.7).encode(
                    longitude='longitude:Q',
                    latitude='latitude:Q',
                    size=alt.Size('price:Q', 
                                scale=alt.Scale(range=[50, 400]), 
                                title='Price ($)'),
                    color=alt.Color('price:Q', 
                                  scale=alt.Scale(scheme='plasma'),
                                  title='Price ($)'),
                    stroke=alt.value('white'),
                    strokeWidth=alt.value(1),
                    tooltip=[
                        alt.Tooltip('name:N', title='Listing Name'),
                        alt.Tooltip('neighbourhood_cleansed:N', title='Neighborhood'),
                        alt.Tooltip('price:Q', title='Price ($)', format='$.0f'),
                        alt.Tooltip('number_of_reviews:Q', title='Reviews'),
                        alt.Tooltip('latitude:Q', title='Latitude', format='.4f'),
                        alt.Tooltip('longitude:Q', title='Longitude', format='.4f')
                    ]
                ).properties(
                    width='container',
                    height=400,
                    title="Albany Airbnb Listings - Hover for Details"
                ).resolve_scale(
                    size='independent'
                )
                
                st.altair_chart(detailed_map, use_container_width=True)
                
                if len(filtered) > 500:
                    st.info(f"ℹ️ Showing a sample of 500 listings out of {len(filtered)} for map performance.")
                    
                # Geographic insights
                st.markdown("**🏘️ Geographic Insights**")
                coord_col1, coord_col2 = st.columns(2)
                
                with coord_col1:
                    center_lat = map_data['latitude'].mean()
                    center_lon = map_data['longitude'].mean()
                    st.write(f"**Center Point**: {center_lat:.4f}°N, {center_lon:.4f}°W")
                    
                    # Most northern/southern/eastern/western listings
                    northernmost = map_data.loc[map_data['latitude'].idxmax()]
                    st.write(f"**Northernmost**: {northernmost['neighbourhood_cleansed']}")
                
                with coord_col2:
                    lat_range = map_data['latitude'].max() - map_data['latitude'].min()
                    lon_range = map_data['longitude'].max() - map_data['longitude'].min()
                    st.write(f"**Coverage Area**: {lat_range:.3f}° × {lon_range:.3f}°")
                    
                    southernmost = map_data.loc[map_data['latitude'].idxmin()]
                    st.write(f"**Southernmost**: {southernmost['neighbourhood_cleansed']}")
            else:
                st.warning("⚠️ No listings found with current filters to display on map.")
        
        with tab4:
            st.subheader("🏘️ Comprehensive Neighborhood Analysis")
            
            # Prepare neighborhood data
            neighborhood_data = df.groupby('neighbourhood_cleansed').agg({
                'price': ['mean', 'median', 'count'],
                'number_of_reviews': 'mean',
                'accommodates': 'mean',
                'availability_365': 'mean',
                'host_is_superhost': lambda x: (x == 't').sum() / len(x) * 100,
                'review_scores_rating': 'mean',
                'instant_bookable': lambda x: (x == 't').sum() / len(x) * 100
            }).round(2)
            
            # Flatten column names
            neighborhood_data.columns = ['avg_price', 'median_price', 'total_listings', 'avg_reviews', 
                                       'avg_accommodates', 'avg_availability', 'superhost_pct', 
                                       'avg_rating', 'instant_bookable_pct']
            neighborhood_data = neighborhood_data.reset_index()
            
            # Filter for neighborhoods with at least 3 listings for meaningful analysis
            neighborhood_data = neighborhood_data[neighborhood_data['total_listings'] >= 3]
            
            if len(neighborhood_data) > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**💰 Average Price by Neighborhood**")
                    
                    # Price comparison chart
                    price_chart = alt.Chart(neighborhood_data.nlargest(10, 'avg_price')).mark_bar().encode(
                        y=alt.Y('neighbourhood_cleansed:N', title='Neighborhood', sort='-x'),
                        x=alt.X('avg_price:Q', title='Average Price ($)'),
                        color=alt.Color('avg_price:Q', scale=alt.Scale(scheme='oranges'), legend=None),
                        tooltip=['neighbourhood_cleansed:N', 'avg_price:Q', 'total_listings:Q']
                    ).properties(
                        height=300,
                        title="Top 10 Most Expensive Neighborhoods"
                    )
                    
                    st.altair_chart(price_chart, use_container_width=True)
                
                with col2:
                    st.markdown("**📊 Listings Count by Neighborhood**")
                    
                    # Listings count chart
                    count_chart = alt.Chart(neighborhood_data.nlargest(10, 'total_listings')).mark_bar().encode(
                        y=alt.Y('neighbourhood_cleansed:N', title='Neighborhood', sort='-x'),
                        x=alt.X('total_listings:Q', title='Number of Listings'),
                        color=alt.Color('total_listings:Q', scale=alt.Scale(scheme='blues'), legend=None),
                        tooltip=['neighbourhood_cleansed:N', 'total_listings:Q', 'avg_price:Q']
                    ).properties(
                        height=300,
                        title="Top 10 Neighborhoods by Listing Count"
                    )
                    
                    st.altair_chart(count_chart, use_container_width=True)
                
                # Host Quality Analysis
                st.markdown("---")
                st.markdown("**⭐ Host Quality & Availability Analysis**")
                
                col3, col4 = st.columns(2)
                
                with col3:
                    # Superhost percentage
                    superhost_chart = alt.Chart(neighborhood_data[neighborhood_data['superhost_pct'] > 0]).mark_circle(size=100).encode(
                        x=alt.X('superhost_pct:Q', title='Superhost Percentage (%)'),
                        y=alt.Y('avg_rating:Q', title='Average Rating', scale=alt.Scale(domain=[4.0, 5.0])),
                        size=alt.Size('total_listings:Q', scale=alt.Scale(range=[50, 300]), title='Listings'),
                        color=alt.Color('avg_price:Q', scale=alt.Scale(scheme='viridis'), title='Avg Price ($)'),
                        tooltip=['neighbourhood_cleansed:N', 'superhost_pct:Q', 'avg_rating:Q', 
                                'total_listings:Q', 'avg_price:Q']
                    ).properties(
                        height=300,
                        title="Host Quality: Superhosts vs Ratings"
                    )
                    
                    st.altair_chart(superhost_chart, use_container_width=True)
                
                with col4:
                    # Availability analysis
                    availability_chart = alt.Chart(neighborhood_data).mark_circle(size=100).encode(
                        x=alt.X('avg_availability:Q', title='Average Availability (days/year)'),
                        y=alt.Y('avg_price:Q', title='Average Price ($)'),
                        size=alt.Size('total_listings:Q', scale=alt.Scale(range=[50, 300]), title='Listings'),
                        color=alt.Color('instant_bookable_pct:Q', scale=alt.Scale(scheme='plasma'), 
                                      title='Instant Book (%)'),
                        tooltip=['neighbourhood_cleansed:N', 'avg_availability:Q', 'avg_price:Q',
                                'instant_bookable_pct:Q', 'total_listings:Q']
                    ).properties(
                        height=300,
                        title="Availability vs Price by Neighborhood"
                    )
                    
                    st.altair_chart(availability_chart, use_container_width=True)
                
                # Neighborhood insights table
                st.markdown("---")
                st.markdown("**📋 Detailed Neighborhood Comparison**")
                
                # Format the data for display
                display_data = neighborhood_data.copy()
                display_data['avg_price'] = display_data['avg_price'].round(0).astype(int)
                display_data['avg_reviews'] = display_data['avg_reviews'].round(1)
                display_data['avg_accommodates'] = display_data['avg_accommodates'].round(1)
                display_data['avg_availability'] = display_data['avg_availability'].round(0).astype(int)
                display_data['superhost_pct'] = display_data['superhost_pct'].round(1)
                display_data['avg_rating'] = display_data['avg_rating'].round(2)
                display_data['instant_bookable_pct'] = display_data['instant_bookable_pct'].round(1)
                
                # Rename columns for better display
                display_data = display_data.rename(columns={
                    'neighbourhood_cleansed': 'Neighborhood',
                    'avg_price': 'Avg Price ($)',
                    'total_listings': 'Total Listings',
                    'avg_reviews': 'Avg Reviews',
                    'avg_accommodates': 'Avg Size',
                    'avg_availability': 'Availability (days)',
                    'superhost_pct': 'Superhosts (%)',
                    'avg_rating': 'Avg Rating',
                    'instant_bookable_pct': 'Instant Book (%)'
                })
                
                # Allow sorting by different metrics
                sort_option = st.selectbox(
                    "Sort neighborhoods by:",
                    ["Avg Price ($)", "Total Listings", "Avg Reviews", "Superhosts (%)", "Avg Rating"],
                    index=0
                )
                
                ascending = st.checkbox("Sort ascending", value=False)
                
                sorted_data = display_data.sort_values(by=sort_option, ascending=ascending)
                
                st.dataframe(
                    sorted_data,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Avg Price ($)": st.column_config.NumberColumn(format="$%.0f"),
                        "Avg Reviews": st.column_config.NumberColumn(format="%.1f"),
                        "Avg Size": st.column_config.NumberColumn(format="%.1f"),
                        "Superhosts (%)": st.column_config.ProgressColumn(min_value=0, max_value=100),
                        "Avg Rating": st.column_config.NumberColumn(format="%.2f"),
                        "Instant Book (%)": st.column_config.ProgressColumn(min_value=0, max_value=100)
                    }
                )
                
                # Key insights
                st.markdown("**🔍 Key Insights**")
                insights_col1, insights_col2 = st.columns(2)
                
                with insights_col1:
                    highest_price = display_data.loc[display_data['Avg Price ($)'].idxmax()]
                    most_listings = display_data.loc[display_data['Total Listings'].idxmax()]
                    st.write(f"💎 **Most Expensive**: {highest_price['Neighborhood']} (${highest_price['Avg Price ($)']})")
                    st.write(f"🏢 **Most Listings**: {most_listings['Neighborhood']} ({most_listings['Total Listings']} listings)")
                
                with insights_col2:
                    if 'Superhosts (%)' in display_data.columns and display_data['Superhosts (%)'].max() > 0:
                        best_hosts = display_data.loc[display_data['Superhosts (%)'].idxmax()]
                        st.write(f"⭐ **Best Host Quality**: {best_hosts['Neighborhood']} ({best_hosts['Superhosts (%)']}% superhosts)")
                    
                    best_rated = display_data.loc[display_data['Avg Rating'].idxmax()]
                    st.write(f"🌟 **Highest Rated**: {best_rated['Neighborhood']} ({best_rated['Avg Rating']} stars)")
            
            else:
                st.warning("⚠️ Not enough data for neighborhood analysis with current filters.")
    
    # Additional insights
    st.markdown("---")
    st.subheader("📈 Data Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🏆 Most Expensive Neighborhoods**")
        if neighborhood == 'All':
            top_expensive = df.groupby('neighbourhood_cleansed')['price'].mean().sort_values(ascending=False).head(5)
            for i, (neigh, price) in enumerate(top_expensive.items()):
                st.write(f"{i+1}. {neigh}: ${price:.0f}")
        else:
            avg_price = filtered['price'].mean()
            st.write(f"Average price in {neighborhood}: ${avg_price:.0f}")
    
    with col2:
        st.markdown("**⭐ Most Reviewed Properties**")
        top_reviewed = filtered.nlargest(5, 'number_of_reviews')[['name', 'number_of_reviews', 'price']]
        for _, row in top_reviewed.iterrows():
            st.write(f"• {row['name'][:40]}... - {row['number_of_reviews']} reviews (${row['price']})")
    
    # Data summary
    with st.expander("📋 Data Summary"):
        st.write(f"**Dataset contains {len(df)} total listings**")
        st.write(f"**Currently showing {len(filtered)} listings**")
        st.write("**Price range:** $" + str(int(df['price'].min())) + " - $" + str(int(df['price'].max())))
        st.write("**Room types:** " + ", ".join(df['room_type'].unique()))
        st.write(f"**Number of neighborhoods:** {df['neighbourhood_cleansed'].nunique()}")

else:
    st.stop()
