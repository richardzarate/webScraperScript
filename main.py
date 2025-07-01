import requests
import csv
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin


########################## Initialize Global Variables ############################################
site = "https://books.toscrape.com/" #main page of the site

bookURL = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html" #Testing on single book first



#
# print("Connected to bookToScrape!")



column_headers = [
    "product_page_url",
    "universal_product_code (upc)",
    "book_title",
    "price_including_tax",
    "price_excluding_tax",
    "quantity_available",
    "product_description",
    "category",
    "review_rating",
    "image_url"
]


################################# Helper Functions #############################################
def get_data(bookURL):
    # connect to the url, get information
    response = requests.get(bookURL)

    # parse html using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    product_page_url = response.url

    # ● universal_ product_code (upc)
    upc = soup.find("th", string="UPC").find_next_sibling("td").text.strip()

    # ● book_title
    title = soup.find("h1").text.strip()

    # ● price_including_tax
    priceWithTax = soup.find("th", string="Price (incl. tax)").find_next_sibling("td").text.strip()

    # ● price_excluding_tax

    priceNoTax = soup.find("th", string="Price (excl. tax)").find_next_sibling("td").text.strip()

    # ● quantity_available
    quantityAvailable = soup.find("th", string="Availability").find_next_sibling("td").text.strip()

    # ● product_description

    productDescription = soup.find_all("p")[3].text.strip()

    # ● category

    category = soup.select("ul.breadcrumb li a")[-1].text.strip()

    # ● review_rating

    review_rating = get_review_rating(soup)

    # ● image_url

    image_relative_url = soup.find("img")['src']
    image_full_url = urljoin(response.url, image_relative_url)

    data = {
        "product_page_url": response.url,
        "universal_product_code (upc)": upc,
        "book_title": title,
        "price_including_tax": priceWithTax[1:],
        "price_excluding_tax": priceNoTax[1:],
        "quantity_available": quantityAvailable,
        "product_description": productDescription,
        "category": category,
        "review_rating": review_rating,
        "image_url": image_full_url
    }
    return data

def get_review_rating(soup):
    ratingTag = soup.find("p", class_="star-rating")

    totalStars = len(ratingTag.find_all("i", class_="icon-star"))

    ratingName = ratingTag["class"][1]

    textToNum = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

    return str(textToNum.get(ratingName, 0)) + " out of " + str(totalStars)

def save_to_csv(data):
    #with open() closes automatically, no need to explicitly close it
    with open("book.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames = column_headers)
        writer.writeheader()
        writer.writerow(data)

def print_data(data):
    print(f"Product URL: {data.get("product_page_url")}")

    print(f"UPC: {data.get("universal_product_code (upc)")}")
    print(f"Title: {data.get("book_title")}")

    print(f"Price (incl. tax): {data.get("price_including_tax")}")
    print(f"Price (excl. tax): {data.get("price_excluding_tax")}")

    print(f"Quantity Available: {data.get("quantity_available")}")
    print(f"Product Description: {data.get("product_description")}")

    print(f"Category: {data.get("category")}")
    print(f"Rating: {data.get("review_rating")}")

    print(f"Image URL: {data.get("image_url")}")


# def print_information()



#####################################################################################
#Run functions
#####################################################################################

# ● product_page_url
# urlTag = soup.find("a")
# url = urlTag['href']

book_data = get_data(bookURL)

print_data(book_data)

save_to_csv(book_data)



# print(os.getcwd())




######################################### Test #####################################################
# print("######################################### Test ########################################")
# for a in soup.select("ul.breadcrumb li a"):
#     relative = a["href"]
#     print(f"Relative: {relative}")
#     fullURL = urljoin(response.url, relative)
#     print(fullURL)
#
# print(response.url)

