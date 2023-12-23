#  Project: Online Shopping Finder
#  Name: Sirapop Tuntithanakij 65011528

# This project requires tkinter, bs4, and selenium to work, All of them can be downloaded from pip
# selenium requires installing DRIVER from its website
# https://selenium-python.readthedocs.io/installation.html

# This project uses GOOGLE CHROME to scrape websites, so Chrome Driver must be installed
# https://chromedriver.chromium.org/downloads
# Make sure the driver version matches your Google Chrome version

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import tkinter as tk
import bs4
import time
import pickle
from abc import ABC, abstractmethod

#Classes
class Product(ABC):
    @abstractmethod
    def __init__(self, name, rating, sale, ship_from, link, website):
        self.name = name
        self.rating = rating
        self.sale = sale
        self.ship_from = ship_from
        self.link = link
        self.website = website

    def getPrice(self):
        pass

class LazadaProduct(Product):
    def __init__(self, name, price, rating, sale, ship_from, link, website):
        super().__init__(name, rating, sale, ship_from, link, website)
        self.price = price

    def getPrice(self):
        return self.price

class ShopeeProduct(Product):
    def __init__(self, name, price_min, price_max, rating, sale, ship_from, link, website):
        super().__init__(name, rating, sale, ship_from, link, website)
        self.price_min = price_min
        self.price_max = price_max

    def getPrice(self):
        return self.price_min

#Main
PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)
products = []
cart = []

#LAZADA
def scrapeLazada():
    driver.get("https://www.lazada.co.th/")

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "topActionHeader"))
        )
    except:
        messagebox.showerror("Error", "Website does not load properly, check your internet")
        driver.quit()
        
    searchbar = driver.find_element(By.XPATH, '//*[@id="q"]')
    searchbar.send_keys(input)
    searchbar.send_keys(Keys.RETURN)
        
    #Lazada Scrape and Page turn
    if search_number > 40:
        pageCount = search_number // 40

        for i in range(pageCount + 1):
            available_pages, page_tab_size = scrapeLazadaProduct(search_number - (40 * i))

            if i + 1 >= available_pages:
                break
            else:
                driver.execute_script("document.body.style.zoom='1'")
                nextpage_xpath = '/html/body/div[3]/div/div[2]/div[1]/div/div[1]/div[3]/div/ul/li[{}]/button'.format(page_tab_size)
                nextpage = driver.find_element(By.XPATH, nextpage_xpath)
                nextpage.click()
    else:
        scrapeLazadaProduct(search_number)

def scrapeLazadaProduct(search_no):
    driver.execute_script("document.body.style.zoom='0.1'")
    time.sleep(2)
    soup = bs4.BeautifulSoup(driver.page_source, features="html.parser")
    lazada_products_web = soup.find_all("div", class_="Bm3ON")
    products_searched = 0

    for product in lazada_products_web:
        if products_searched >= search_no:
            break
        products_searched += 1
        
        name_class = product.find("div", class_="RfADt")
        name = name_class.text.strip()
        link = "https:" + name_class.find('a')['href']
        price = float(product.find("span", class_="ooOxS").text.strip().replace(',', '')[1:])

        rating = 0.0
        stars = product.find_all("i", class_="_9-ogB")
        if len(stars) <= 0:
            rating = 0.0
        else:
            for star in stars:
                if star['class'][1] == "Dy1nx":
                    rating += 1.0
                elif star['class'][1] == "i6t3-":
                    rating += 0.75
                elif star['class'][1] == "B4Foa":
                    rating += 0.5
                elif star['class'][1] == "TZlP8":
                    rating += 0.25

        try:
            sales = int(product.find("span", class_="_1cEkb").text.strip(' sold'))
        except:
            sales = 0

        ship_from = product.find("span", class_="oa6ri").text.strip()
        products.append(LazadaProduct(name, price, rating, sales, ship_from, link, "Lazada"))
    
    #return available pages
    page_tab_class = soup.find("ul", class_="ant-pagination")
    page_tab = page_tab_class.find_all("li")
    page_tab_size = len(page_tab_class)
    page_max = 0

    for page_navigate in page_tab:
        try:
            page = int(page_navigate["title"])
        except:
            pass
        else:
            if page >= page_max:
                page_max = page
    return page_max, page_tab_size

#SHOPEE
def scrapeShopee():
    driver.get("https://shopee.co.th/")

    #Wait for website to load
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "main"))
        )
    except:
        messagebox.showerror("Error", "Website does not load properly, check your internet")
        driver.quit()

    #Select Language
    time.sleep(0.5)
    language_bt = driver.find_elements(By.CLASS_NAME, "language-selection__list-item")
    for language in language_bt:
        if language.text == "English":
            language.click()

    #Remove ad
    time.sleep(4)
    popup = driver.execute_script('return document.querySelector("shopee-banner-popup-stateful").shadowRoot.querySelector("div.shopee-popup__close-btn")')
    popup.click()

    searchbar = driver.find_element(By.TAG_NAME, "input")
    searchbar.send_keys(input)
    searchbar.send_keys(Keys.RETURN)

    #zoom out
    driver.execute_script("document.body.style.zoom='0.1'")
    time.sleep(2)

    #Shopee Scrape and Page turn
    if search_number > 60:
        pageCount = search_number // 60

        for i in range(pageCount + 1):
            available_pages = scrapeShopeeProduct(search_number - (60 * i))

            if i + 1 >= available_pages:
                break
            else:
                driver.execute_script("document.body.style.zoom='1'")
                nextpage_xpath = '/html/body/div[1]/div/div[2]/div/div/div[2]/div/div[3]/div/button[{}]'.format(available_pages + 2)
                nextpage = driver.find_element(By.XPATH, nextpage_xpath)
                nextpage.click()
    else:
        scrapeShopeeProduct(search_number)

def scrapeShopeeProduct(search_no):
    driver.execute_script("document.body.style.zoom='0.1'")
    time.sleep(2)
    soup = bs4.BeautifulSoup(driver.page_source, features="html.parser")
    shopee_products_web = soup.find_all("div", class_="col-xs-2-4 shopee-search-item-result__item")
    products_searched = 0

    for product in shopee_products_web:
        if products_searched >= search_no:
            break
        products_searched += 1

        name = product.find("div", class_="ie3A+n bM+7UW Cve6sh").text.strip()
        price_min = 0.0
        price_max = 0.0
        try: #if price has range
            prices = product.find_all("span", class_="ZEgDH9")
            price_min = int(prices[0].text.replace(',', '').strip())
            price_max = int(prices[1].text.replace(',', '').strip())
        except: #no range
            price_min = int(product.find("span", class_="ZEgDH9").text.replace(',', '').strip())
        

        rating = 0.0
        full_stars = product.find_all("div", class_="shopee-rating-stars__lit")
        if len(full_stars) <= 0:
            rating = 0.0
        else:
            for star in full_stars:
                star_html = str(star)
                crop_index = star_html.find('width: ')
                crop_p_index = star_html.find('%')
                short = float(star_html[crop_index + 7:crop_p_index]) / 100.0
                rating += short

        #sales
        try:
            sales = product.find("div", class_="r6HknA uEPGHT").text.strip(' sold')

            if sales.find('k') >= 0:
                sales = float(sales.strip('k'))
                sales = int(sales * 1000.0)
            else:
                sales = int(sales)
        except:
            sales = 0

        ship_from = product.find("div", class_="zGGwiV").text.strip()
        link = "https://shopee.co.th" + product.find("a")['href']
        products.append(ShopeeProduct(name, price_min, price_max, rating, sales, ship_from, link, "Shopee"))

    #return available pages
    pages = soup.find("div", class_="shopee-page-controller")
    return len(pages) - 2

#SORT
def sortProductByPrice(list):
    sorted_products = list + []
    is_sorted = False

    while is_sorted == False:
        is_sorted = True
        for i in range(0, len(sorted_products) - 1):
            if sorted_products[i].getPrice() > sorted_products[i + 1].getPrice():
                is_sorted = False
                temp = sorted_products[i + 1]
                sorted_products[i + 1] = sorted_products[i]
                sorted_products[i] = temp
    
    return sorted_products

def sortProductByRating(list):
    sorted_products = list + []
    is_sorted = False

    while is_sorted == False:
        is_sorted = True
        for i in range(0, len(sorted_products) - 1):
            if sorted_products[i].rating < sorted_products[i + 1].rating:
                is_sorted = False
                temp = sorted_products[i + 1]
                sorted_products[i + 1] = sorted_products[i]
                sorted_products[i] = temp
    
    return sorted_products

def sortProductBySale(list):
    sorted_products = list + []
    is_sorted = False

    while is_sorted == False:
        is_sorted = True
        for i in range(0, len(sorted_products) - 1):
            if sorted_products[i].sale < sorted_products[i + 1].sale:
                is_sorted = False
                temp = sorted_products[i + 1]
                sorted_products[i + 1] = sorted_products[i]
                sorted_products[i] = temp
    
    return sorted_products

#TKINTER
class OnlineShopping:
    def __init__(self):
        def search():
            global input, search_number
            input = self.e_input.get()
            if input == '' or input == ' ':
                messagebox.showerror("Error", "Product field can't be blank")
            else:
                try:
                    search_number = int(self.e_size.get())
                    if search_number > 100:
                        search_number = 100

                    scrapeLazada()
                    scrapeShopee()
                    self.window.destroy()
                    SortPage(products)
                except:
                    messagebox.showerror("Error", "Amount field can't be blank")

        def import_file():
            try:
                openfilepath = filedialog.askopenfile(defaultextension='.dat',filetypes=[('All Files', '*.*')], title="Load Scraped Products").name

                with open(openfilepath, 'rb') as file:
                    products = pickle.load(file)
                    file.close()
                self.window.destroy()
                SortPage(products)
            except:
                messagebox.showerror("Error", "File did not load properly")


        self.window = Tk()
        self.window.resizable(False, False)
        self.window.title("Search Product")
        self.window.geometry("350x265")

        self.productName = StringVar()
        self.topic = StringVar()
        self.blank = Label(self.window, text = " ")
        self.blank.grid(row = 1)

        self.title = Label(self.window, text = "Online Shopping Finder", font = ("Arial", 15))
        self.title.grid(row = 1, column = 2, pady = 10, columnspan = 4)

        self.sp = Label(self.window, text = "Search Product: ", font = ("Arial", 10))
        self.sp.grid(row = 2, column = 1, columnspan = 2, pady = 5)
        
        self.sp = Label(self.window, text = "Search Amount: ", font = ("Arial", 10))
        self.sp.grid(row = 3, column = 1, columnspan = 2)

        self.e_input = Entry(self.window, textvariable = self.productName)
        self.e_input.grid(row = 2, column = 3, columnspan = 4, ipadx = 50, ipady = 5)

        self.e_size = Entry(self.window, textvariable = self.topic)
        self.e_size.grid(row = 3, column = 3, columnspan = 4, ipadx = 50, ipady = 5, pady = 5)

        self.title = Label(self.window, text = "(Max: 100)", font = ("Arial", 10))
        self.title.grid(row = 4, column = 2, columnspan = 4)

        self.btSearch = Button(self.window, text = "Search!", command = search, font = ("Arial", 10), bg = "#99ff99")
        self.btSearch.grid(row = 5, column = 2, columnspan = 4, ipadx = 50, pady = 10)

        self.title = Label(self.window, text = "or", font = ("Arial", 10))
        self.title.grid(row = 6, column = 2, columnspan = 4)

        self.btImport = Button(self.window, text = "Import File", command = import_file, font = ("Arial", 10), bg = "#99ff99")
        self.btImport.grid(row = 7, column = 2, columnspan = 4, ipadx = 40, pady = 10)

        self.window.mainloop()

class Cart:  
    def __init__(self, cart):
        def saveFile():
            try:
                savefilelink = filedialog.asksaveasfile(defaultextension='.txt',filetypes=[('All Files', '*.*')], title="Save Products Link").name
                newcart = []

                #remove duplicate
                for product in cart:
                    if product not in newcart:
                        newcart.append(product)

                with open(savefilelink, 'w', encoding="utf-8") as file:
                    for product in newcart:
                        print(product.link)
                        file.write(product.link)
                        file.write('\n')
                
                file.close()
            except:
                messagebox.showerror("Error", "File did not save properly")

        self.window = Tk()
        self.window.title("Cart")

        self.title = Label(self.window, text = "In Cart: {}".format(len(cart)), font = ("Arial", 15))
        self.title.grid(row = 1, column = 1, sticky = NW)

        self.name = Label(self.window, text = "Name                                                          ", font = ("Arial", 12))
        self.name.grid(row = 2, column = 1, sticky = NW)

        self.count = Label(self.window, text = "Total Price", font = ("Arial", 12))
        self.count.grid(row = 2, column = 2, sticky = NW)

        self.frame1 = Frame(self.window, borderwidth=3, relief = 'groove')
        self.frame1.grid(row = 3, column = 1, columnspan = 5)

        self.canvas = Canvas(self.frame1, width = 400, height = 300)
        self.canvas.grid(row = 3, column = 1, columnspan = 5)

        self.scrollbar = ttk.Scrollbar(self.frame1, orient = VERTICAL, command = self.canvas.yview)
        self.scrollbar.grid(row = 3,  column = 10, sticky = 'ns')

        self.canvas.configure(yscrollcommand = self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.frame2 = Frame(self.canvas)
        self.canvas.create_window((0,0), window = self.frame2, anchor = 'nw')

        self.blank = Label(self.frame2, text = "                                                                      ", font = ("Arial", 12))
        self.blank.grid(row = 1, column = 1, sticky = NW)

        for i in range(len(cart)):
            #price for lazada or shopee
            if type(cart[i]) == LazadaProduct:
                product_price = cart[i].getPrice()
            elif cart[i].price_max <= 0:
                product_price = cart[i].price_min
            else:
                product_price = str(cart[i].price_min) + ' - ' + str(cart[i].price_max)

            #title too long
            if len(cart[i].name) > 25:
                name = cart[i].name[:40] + '..'
            else:
                name = cart[i].name
            
            name = Label(self.frame2, text = name, font = ("Arial", 10))
            name.grid(row = i, column = 1, sticky=W)

            price = Label(self.frame2, text = product_price, font = ("Arial", 10))
            price.grid(row = i, column = 2, sticky=W)
        
        total_price_min = 0
        total_price_max = 0
        total_price_display = ''

        for product in cart:
            if type(product) == LazadaProduct:
                total_price_min += product.price
                total_price_max += product.price
            elif product.price_max <= 0:
                total_price_min += product.price_min
                total_price_max += product.price_min
            else:
                total_price_min += product.price_min
                total_price_max += product.price_max

        if total_price_min == total_price_max:
            total_price_display = str(total_price_min)
        else:
            total_price_display = str(total_price_min) + " - " + str(total_price_max)

        self.label = Label(self.window, text = "Total Price: " + total_price_display + " Baht", font = ("Arial", 15))
        self.label.grid(row = 6, column = 1,  columnspan = 4, ipadx = 50)

        self.btLink = Button(self.window, text = "Get Link", command = saveFile, font = ("Arial", 10), bg = "#99ff99")
        self.btLink.grid(row = 7, column = 1, columnspan = 4, ipadx = 50, pady = 10)

        self.window.mainloop()

class Product:
    def __init__(self, sorted_products):
        def addToCart(position):
            cart.append(sorted_products[position])
            self.prod_in_cart.config(text = "Products in Cart: {}".format(len(cart)))
        
        def viewCart():
            Cart(cart)

        self.window = Tk()
        self.window.title("List of Products")
        self.window.geometry("527x648")

        self.menu = StringVar()
        self.menu.set("Sort By")
        try:
            self.prod = Label(self.window, text = "Product: " + input, font = ("Arial", 15))
        except:
            self.prod = Label(self.window, text = "Product From File", font = ("Arial", 15))
        self.prod.grid(row = 1, column = 1, columnspan = 4,sticky=W)

        self.sortby = Label(self.window, text = sort_by, font = ("Arial", 15))
        self.sortby.grid(row = 1, column = 5, columnspan = 2, sticky=NE)

        self.frame1 = Frame(self.window, borderwidth=3, relief = 'groove')
        self.frame1.grid(row = 2, column = 1, columnspan = 5)

        self.canvas = Canvas(self.frame1, width= 500, height = 580)
        self.canvas.grid(row = 2, column = 1, columnspan = 5)

        self.scrollbar = ttk.Scrollbar(self.frame1, orient = VERTICAL, command = self.canvas.yview)
        self.scrollbar.grid(row = 2,  column = 10, sticky = 'ns')

        self.canvas.configure(yscrollcommand = self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.frame2 = Frame(self.canvas)
        self.canvas.create_window((0,0), window = self.frame2, anchor = 'nw')

        blank = Label(self.frame2, text = "                                                                                                                              ")
        blank.grid(row = 1, column = 1, columnspan = 7)
        
        #products
        for i in range(len(sorted_products)):
            #button color
            if sorted_products[i].website == "Lazada":
                bgcolor = '#F5D2FF'
            else:
                bgcolor = '#FFF4D2'
            
            #price for lazada or shopee
            if type(sorted_products[i]) == LazadaProduct:
                product_price = sorted_products[i].getPrice()
            elif sorted_products[i].price_max <= 0:
                product_price = sorted_products[i].price_min
            else:
                product_price = str(sorted_products[i].getPrice()) + ' - ' + str(sorted_products[i].price_max)

            #title too long
            if len(sorted_products[i].name) > 25:
                name = sorted_products[i].name[:40] + '..'
            else:
                name = sorted_products[i].name

            btSelect = Button(self.frame2, text = "Add to Cart", font = ("Arial", 10), command = lambda i=i: addToCart(i), bg = bgcolor)
            btSelect.grid(row = 1 + (i * 5), column = 8, columnspan = 2, ipadx = 20, sticky=NE)

            name = Label(self.frame2, text = "{}) {}".format(i + 1, name), font = ("Arial", 10))
            name.grid(row = 1 + (i * 5), column = 1, columnspan = 7, sticky=W)

            price = Label(self.frame2, text = "PRICE: {}".format(product_price), font = ("Arial", 10))
            price.grid(row = 2 + (i * 5), column = 1, columnspan = 7, sticky=W)

            rating = Label(self.frame2, text = "RATING: {}".format(sorted_products[i].rating), font = ("Arial", 10))
            rating.grid(row = 3 + (i * 5), column = 1, columnspan = 7, sticky=W)

            sale = Label(self.frame2, text = "SALES: {}".format(sorted_products[i].sale), font = ("Arial", 10))
            sale.grid(row = 4 + (i * 5), column = 1, columnspan = 7, sticky=W)

            location = Label(self.frame2, text = "Shipping From: " + sorted_products[i].ship_from, font = ("Arial", 10))
            location.grid(row = 5 + (i * 5), column = 1, columnspan = 7, sticky=W)

            website = Label(self.frame2, text = "Website: " + sorted_products[i].website, font = ("Arial", 10))
            website.grid(row = 6 + (i * 5), column = 1, columnspan = 7, sticky=W)

        self.prod_in_cart = Label(self.window, text = "Products in Cart: {}".format(len(cart)), font = ("Arial", 15))
        self.prod_in_cart.grid(row = 10, column = 1, columnspan = 4, sticky=tk.SW)

        self.btView = Button(self.window, text = "View", command = viewCart, font = ("Arial", 10), bg = "#99ff99")
        self.btView.grid(row = 10, column = 5, columnspan = 2, ipadx = 50, sticky=tk.SE)

        self.window.mainloop()

class SortPage:
    def __init__(self, products_to_sort):
        def sort():
            global sort_by
            sort_by = self.menu.get()
            if sort_by == 'Sort By':
                messagebox.showerror("Error", "Please select a sorting type")
            elif sort_by == "Sort by Price":
                sorted_products = sortProductByPrice(products_to_sort)
            elif sort_by == "Sort by Review":
                sorted_products = sortProductByRating(products_to_sort)
            else:
                sorted_products = sortProductBySale(products_to_sort)
            Product(sorted_products)

        def savefile():
            try:
                savefilepath = filedialog.asksaveasfile(defaultextension='.dat',filetypes=[('All Files', '*.*')], title="Save Scraped Products").name
                f = open(savefilepath, 'wb')
                pickle.dump(products_to_sort, f)
                f.close() 
            except:
                messagebox.showerror("Error", "File did not save properly")

        self.window = Tk()
        self.window.resizable(False, False)
        self.window.title("Sort / Save")
        self.window.geometry("350x250")
        self.menu = StringVar()
        self.menu.set("Sort By")
        self.productName = StringVar()
        self.blank = Label(self.window, text = " ")
        self.blank.grid(row = 1)

        try:
            self.title = Label(self.window, text = "Product: " + input, font = ("Arial", 10))
        except:
            self.title = Label(self.window, text = "Product from File", font = ("Arial", 10))
        self.title.grid(row = 1, column = 2, padx = 100, pady = 10, columnspan = 4)

        self.title = Label(self.window, text = "Count: {}".format(len(products_to_sort)), font = ("Arial", 10))
        self.title.grid(row = 2, column = 2, padx = 100, pady = 10, columnspan = 4)

        self.menu.set("Sort By")
        self.drop = OptionMenu(self.window, self.menu, "Sort by Price", "Sort by Review", "Sort by Bestselling")
        self.drop.grid(row = 3, column = 2, padx = 100, pady = 10)  

        self.btSearch = Button(self.window, text = "Sort", command = sort, font = ("Arial", 10), bg = "#99ff99")
        self.btSearch.grid(row = 4, column = 2, columnspan = 4, ipadx = 50, pady = 10)

        self.label = Label(self.window, text = "or", font = ("Arial", 10))
        self.label.grid(row = 5, column = 2, columnspan = 4)

        self.btImport = Button(self.window, text = "Save File", command = savefile, font = ("Arial", 10), bg = "#99ff99")
        self.btImport.grid(row = 6, column = 2, columnspan = 4, ipadx = 40, pady = 10)

        self.window.mainloop()

OnlineShopping()