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
        tab1, tab2, tab3 = st.tabs(["📊 Price Analysis", "📈 Reviews vs Price", "🗺️ Geographic Map"])
        
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
