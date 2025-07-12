import requests
import csv
import os
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin


#update README for setting up virtual environment
########################## Initialize Global Variables ############################################
site = "https://books.toscrape.com/" #main page of the site

categoryURL = "https://books.toscrape.com/catalogue/category/books/poetry_23/index.html"

bookURL = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html" #Testing on single book first


#parallel arrays for categories and its respective links
categories = [] #contains strings of category names
category_links = [] #contains strings of urls to category

#csv file column headers, must correspond to book data dictionary
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
#grab all the information of each category in the site
def get_all_books_by_category(siteURL):
    site_response = requests.get(siteURL)#get site html data
    site_soup = BeautifulSoup(site_response.text, "html.parser")#parse through html data and make it readable

    # Grab all category links under side_categories
    category_data = site_soup.select("div.side_categories ul.nav li ul li a")

    #for each a element in the category data
    for a in category_data:
        category_name = a.text.strip() #grab category name
        relative_link = a["href"] #grab the relative link
        full_link = urljoin(site_response.url, relative_link) #combine and make a full link

        categories.append(category_name) #save category name for use by other functions
        category_links.append(full_link) #save category link for use by other functions





#gets all the books in a category
def get_category(categoryURL):
    #work on padination
    books_in_category = [] #an array that saves all the book data

    #this while loop checks if the categoryURL contains a string, if it doesn't it stops the loop
    while categoryURL:
        category_response = requests.get(categoryURL) #get html data

        category_soup = BeautifulSoup(category_response.text, "html.parser") #parse html data and make it readable

        #loop through the contents of the page and grab a book each run
        for a in category_soup.select("article.product_pod h3 a"):
            book_link = a["href"]
            book_full_link = urljoin(category_response.url, book_link)
            books_in_category.append(get_data(book_full_link))

        # Check for next page
        next_page = category_soup.select_one("li.next a")
        if next_page:
            next_href = next_page["href"]
            categoryURL = urljoin(categoryURL, next_href)

            print("Moving to next page: " + categoryURL)

        else:
            categoryURL = None

    return books_in_category #return the array of book data

#gets an individual book's data:
#- page url
#- upc code
#- title
#- price with tax
#- price without tax
#- quantity available
#- product description
#- category
#- review rating
#- image url
#and saves it in a dictionary
def get_data(bookURL):
    # connect to the url, get information which is in html form
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

    #dictionary to organize the information
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

#just converts the rating data into a readable format
def get_review_rating(soup):
    #takes the rating tag and puts its contents in an array
    ratingTag = soup.find("p", class_="star-rating")

    #counts the total amount of stars
    totalStars = len(ratingTag.find_all("i", class_="icon-star"))

    #grabs the rating but its a word instead of being a number
    ratingName = ratingTag["class"][1]

    #dictionary that converts the rating into a number
    textToNum = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

    #returns the rating into a proper format such as 3 out of 5
    return str(textToNum.get(ratingName, 0)) + " out of " + str(totalStars)

#takes in a string for the category name and a list of book data as dictionaries in that category
#checks if a folder called books_by_category already exists and creates it if not
#creates a csv file named after the category and contains all the books within the category and all its information
def save_to_csv(category, category_data):

    os.makedirs("books_by_category", exist_ok=True) #check if folder is there, if not make that folder

    file_name = "books_by_category/" + category + ".csv" #names the csv file by its category

    #with open() closes automatically, no need to explicitly close it
    with open(file_name, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames = column_headers)
        writer.writeheader()
        writer.writerows(category_data)

#takes in a string of a category name, a string for the book title, and a url for an image
#checks if there are illegal characters in the book title and replace them with underscore
#checks if a folder associated to the category exists, creates it if not
#then saves the corresponding image into the corresponding folder by the modified book title with legal characters
def get_image(category, book_title, image_url):
    # Replace any illegal characters with underscores
    category = re.sub(r'[\\/:"*?<>|]+', "_", category)
    book_title = re.sub(r'[\\/:"*?<>|]+', "_", book_title)

    #creates a folder which is named by the category
    folder_name = "images/" + category

    #names the image file by the title of the book
    file_directory = folder_name + "/" + book_title + ".jpg"
    os.makedirs(folder_name, exist_ok=True) #checks if the folder is already there
    image_response = requests.get(image_url)

    #save the image into the specified directory
    with open(file_directory, "wb") as f:
        f.write(image_response.content)


#prints information of the book by going through a dictionary
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


def user_interface():
    #grab the html information for the home page
    #ask user what they would like to do, if input is not among the options given, let the user know and ask again
    get_all_books_by_category(site)  # saves the categories and their links in their respective variables
    while True:

        print("Please choose what you would like to do by entering the corresponding number:")
        print("[1] Scrape whole website")
        print("[2] Scrape a whole category")
        print("[3] Scrape a single book")
        print("[4] Quit")
        print("___________________________________________________________________________________________")

        option = input("option: ")
        if option not in ["1", "2", "3", "4"]:
            print("\033[91mInvalid choice. Please enter 1, 2, 3, or 4.\033[0m")
        if option == "1":
            # 1. get_all_books_by_category saves the name of the category and the link to that category in parallel arrays
            # 2. loop through one of the parallel arrays and grab the index of the current category in array
            # 3. use the index grabbed from the loop to grab the books within that category and save it in an array
            # 4. at the same time, save the list of books and their information in that category in a csv file - titled by its category
            # 5. once a list of books is found in the category, loop through book_in_category to get the individual book's image and save it to a folder named by its category
            for i in range(len(categories)):
                books_in_category = get_category(category_links[i])
                save_to_csv(categories[i], books_in_category)  # save all the books in its respective csv file by category

                for book in books_in_category:
                    get_image(categories[i], book.get("book_title"), book.get(
                        "image_url"))  # saves individual book covers organizing them by their title and creates folder based on category
            break
        if option == "2":
            #Ask the user for which category to scrape
            #Once specified, grab the url for the category that has been saved previously by the get_all_books_by category function
            #Grab all the books and their information within the category
            #Store it temporarily in a list, then save all the information into a csv file
            #raise Exceptions when index is out of bounds, or the input given is invalid such as a string instead of an integer
            while True:
                try:
                    print("Please enter a number corresponding to the category you would like to scrape: ")
                    for i in range(len(categories)):
                        print("[" + str(i+1) + "] " + categories[i])

                    print("____________________________________________________________________________________________")
                    index = int(input("Category: ")) - 1
                    if index >= len(categories) or index < 0:
                        raise IndexError
                    books_in_category = get_category(category_links[index])
                    save_to_csv(categories[index],books_in_category)  # save all the books in its respective csv file by category
                    print("Category Saved")
                    break
                except ValueError:
                    print("\033[91mPlease only enter numbers that corresponds with the given options\033[0m")
                except IndexError:
                    print("\033[91mPlease choose between the numbers given\033[0m")
            break
        if option == "3":
            #check if the URL give leads to books.toscrape.com, or it's a valid URL if not then raise an exception
            #If the URL is valid grab the book data and save it into a csv
            book = []
            while True:
                try:
                    print("Please enter the url of the book you would like to scrape: ")
                    bookURL = input("URL: ")
                    if "books.toscrape.com" not in bookURL:
                        raise ValueError("URL must be from books.toscrape.com")
                    book.append(get_data(bookURL))
                    save_to_csv(book[0].get("book_title"), book)
                    print("Information for " + book[0].get("book_title") + " has been saved.")
                    break
                except (ValueError, requests.RequestException, AttributeError, IndexError, TypeError):
                    print("\033[91mPlease enter a valid URL that points to a valid book page on books.toscrape.com\033[0m")

            break


        if option == "4":
            #quit the program
            print("Quitting program...")
            break



#####################################################################################
#Run Script User Interface
#####################################################################################

#1. get_all_books_by_category saves the name of the category and the link to that category in parallel arrays
#2. loop through one of the parallel arrays and grab the index of the current category in array
#3. use the index grabbed from the loop to grab the books within that category and save it in an array
#4. at the same time, save the list of books and their information in that category in a csv file - titled by its category
#5. once a list of books is found in the category, loop through book_in_category to get the individual book's image and save it to a folder named by its category

user_interface()


