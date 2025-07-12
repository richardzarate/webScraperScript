📚 Book Scraper

This is a Python web scraper that extracts book data from the demo site Books to Scrape.
It organizes the data by category into CSV files and downloads book cover images into categorized folders.

🚀 Features

✅ Scrapes each category for all books within

✅ Scrapes categories for each book:

    Title
    
    UPC
    
    Prices (including & excluding tax)
    
    Availability
    
    Description
    
    Category
    
    Review rating
    
    Image URL

✅ Saves data:

    CSV files for each category under books_by_category/
    
    Images downloaded under images/<Category>/

💻 How to run

    1️⃣ **Clone or download this repository.**
    
    2️⃣ **(Recommended) Create and activate a virtual environment:**
        On Windows:
            python -m venv venv
            venv\Scripts\activate
        On macOS/Linux:
            python3 -m venv venv
            source venv/bin/activate


Install the required packages:

    pip install -r requirements.txt

Run the script:

    python main.py

When complete:

    CSV files are saved in books_by_category/.

    Images are saved in images/<Category>/ directories.

🔍 Notes

This is designed to work with the Books to Scrape demo site, which is static and intended for practicing web scraping.

Be sure to respect robots.txt and site terms for any other real websites you scrape.

💡 License

For educational use.
Always respect website terms of service when scraping!