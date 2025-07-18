# 🏠 Inside Airbnb Dashboard

An interactive Streamlit dashboard for exploring Airbnb listings data with beautiful visualizations and insights.

## 📋 Features

- **Interactive Filters**: Filter by neighborhood, room type, and price range
- **Multiple Visualizations**: 
  - Price analysis by room type
  - Price vs reviews scatter plot
  - Geographic map with pricing data
  - Comprehensive neighborhood insights and comparisons
- **Real-time Metrics**: Total listings, average prices, and neighborhood insights
- **Data Insights**: Top expensive neighborhoods and most reviewed properties

## 🚀 Quick Start

### Local Development

1. **Clone/Download** the repository
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the app**:
   ```bash
   streamlit run app.py
   ```
4. **Open your browser** to `http://localhost:8501`

## 🌐 Deploy to Streamlit Cloud

### Method 1: GitHub Repository (Recommended)

1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/airbnb-viz.git
   git push -u origin main
   ```

2. **Go to [share.streamlit.io](https://share.streamlit.io)**

3. **Click "New app"**

4. **Fill in the details**:
   - Repository: `yourusername/airbnb-viz`
   - Branch: `main`
   - Main file path: `app.py`

5. **Click "Deploy!"**

### Method 2: Direct File Upload

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Upload your files** (`app.py`, `requirements.txt`, `listings.csv`)
3. **Set main file** to `app.py`
4. **Deploy**

## 📁 Required Files

Make sure you have these files in your repository:

- `app.py` - Main Streamlit application
- `requirements.txt` - Python dependencies
- `listings.csv` - Your Airbnb data file
- `README.md` - This documentation
- `.gitignore` - Ignores unnecessary files for clean deployment

## 🔧 Troubleshooting

### Common Issues:

1. **"File not found" error**: 
   - Ensure `listings.csv` is in the same directory as `app.py`
   - Check the file name exactly matches (case-sensitive)

2. **Memory errors on Streamlit Cloud**:
   - The app automatically samples large datasets for performance
   - Consider reducing your CSV file size if needed

3. **Package import errors**:
   - Verify all dependencies are listed in `requirements.txt`
   - Use compatible package versions

### Performance Tips:

- For large datasets (>1000 listings), the map will show a sample of 500 listings
- Filters are applied efficiently to maintain responsiveness
- Data is cached for better performance

## 📊 Data Format

Your `listings.csv` should contain these columns:
- `price` - Listing price (can include $ and commas)
- `latitude`, `longitude` - Geographic coordinates
- `room_type` - Type of accommodation
- `neighbourhood_cleansed` - Neighborhood name
- `number_of_reviews` - Review count
- `name` - Listing name
- `accommodates` - Number of guests

## 🎨 Customization

Feel free to modify:
- Color schemes in the Altair charts
- Add more filters or visualizations
- Adjust the price range limits
- Customize the layout and styling

## 📝 License

This project is open source and available under the MIT License.

---

**Happy analyzing! 🏠📊** 