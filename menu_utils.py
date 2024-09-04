# imported base_model classes
from base_model import Drink, Meal, Menu
from custom_exeptions import InvalidMenuFile
# imported csv from Python standard library
import csv
class MenuPrinter:
    def print_menu(self, menu):
        print("---------------MENU-----------------")
        menu_items = menu.get_menu_items()
        for key in menu_items:
            menu_item = menu_items[key]
            print(str(menu_item.get_product_id()) + " . " + menu_item.get_name() + " | " + str(menu_item.get_price()) + " Euro ")
        print("------------------------------------")
class MenuImporter:
    # created new method to import menu specified by its file path
    def import_menu(self, file_path):
        menu_file = open(file_path)
        csv_reader = csv.reader(menu_file)
        return self._transform_csv_menu_data_to_menu(csv_reader)
    # transform csv menu data into objects
    def _transform_csv_menu_data_to_menu(self, csv_reader):
        imported_menu = Menu(True) # from_file -> True / False
        for row in csv_reader:
            product_id = int(row[0])
            product_name = row[1]
            product_price = float(row[2])
            product_category = row[3]
            if "meal" == product_category:
                product = Meal(product_id,product_name, product_price, "")
            elif "drink" == product_category:
                sugar_free = row[4]
                product = Drink( product_id,product_name, product_price, sugar_free)
            else:
                exception_message = "".join("The menu fiel couldn't be processed as the product category from product ").join(product_name).join(" is invalid.")
                raise InvalidMenuFile(exception_message)
            imported_menu.get_menu_items().update({product_id: product})
        return imported_menu