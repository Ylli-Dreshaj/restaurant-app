from kivymd.uix.datatables import MDDataTable
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from menu_utils import MenuImporter
from order_calculators import OrderCalculatorKS, OrderCalculatorGER
from order_utils import OrderManager, InvoiceBuilder
from base_model import Order, Product, Client, Restaurant
from base_enum import OrderItemSize


class RestaurantAPP(MDApp):
    __selected_product = None

    def build(self):
        
        Window.size = (900, 600)
  
        self.screen = Builder.load_file('restaurant_app_gui2.kv')

        # Assign UI elements to variables for easy access
        # Accessing the 'first_box_layout' widget from the Kivy screen's ids dictionary
        first_box_layout = self.screen.ids.first_box_layout
        second_box_layout = self.screen.ids.second_box_layout
        # the 'quantity_input' widget from the Kivy screen's ids dictionary
        self.quantity_input = self.screen.ids.quantity_input
        #  the 'spinner' widget from the Kivy screen's ids dictionary
        self.spinner = self.screen.ids.spinner
        #  the 'check_box_ks' widget from the Kivy screen's ids dictionary
        self.check_box_ks = self.screen.ids.check_box_ks
        self.check_box_gr = self.screen.ids.check_box_gr
        # the 'name_field' widget from the Kivy screen's ids dictionary
        self.name_field = self.screen.ids.name_field
        self.phone_field = self.screen.ids.phone_field
        #  the 'invoice_label' widget from the Kivy screen's ids dictionary
        self.invoice_label = self.screen.ids.invoice_label

        # Import menu data from CSV file
        menu_importer = MenuImporter()
        menu = menu_importer.import_menu('menu-list.csv')
        product_list = list(menu.get_menu_items().values())
        table_row_data = []

        # Create data for the menu table
        for product in product_list:
            table_row_data.append((product.get_product_id(), product.get_name(), product.get_price()))

        # Create and add menu table to the first box layout
        menu_table = MDDataTable(
            size_hint=(1, 1),
            check=True,
            rows_num=10,
            column_data=[
                ("Id", dp(20)),
                ("Name", dp(25)),
                ("Price", dp(30))
            ],
            row_data=table_row_data
        )
        first_box_layout.add_widget(menu_table)
        menu_table.bind(on_row_press=self.on_row_press)

        # Create and initialize order table
        self.order_table = MDDataTable(
            size_hint=(1, 1),
            padding=[0, 33, 0, 0],
            check=True,
            rows_num=10,
            column_data=[
                ("Id", dp(20)),
                ("Name", dp(20)),
                ("Price", dp(20)),
                ("Quantity", dp(20)),
                ("Size", dp(20))
            ],
            row_data=[]
        )
        second_box_layout.add_widget(self.order_table)
        self.order_table.bind(on_row_press=self.on_row_press)

        return self.screen

    def on_row_press(self, instance_table, instance_row):
        row_number = int(instance_row.index / len(instance_table.column_data))
        self.__selected_product = instance_table.row_data[row_number]

    # Method for adding selected product to the order table
    def add_to_order(self, instance):
        if self.__selected_product is None:
            message = 'Please select a product.'
        elif self.quantity_input.text == "":
            message = 'Please enter a quantity.'
        elif self.spinner.text == "Select Size":
            message = 'Please select an order item size.'

        # Display popup if any condition is not met
        if 'message' in locals():
            popup = Popup(title='Invalid data', content=Label(text=message),
                        size_hint=(None, None), size=(400, 200))
            popup.open()

        else:
            quantity = self.quantity_input.text
        order_item_size = self.spinner.text

        if quantity and order_item_size:
                product_data = [
                    self.__selected_product[0],
                    self.__selected_product[1],
                    self.__selected_product[2],
                    quantity,
                order_item_size
                ]
                self.order_table.row_data.append(product_data)
                self.order_table.update_row_data

                self.__selected_product = None
                self.quantity_input.text = ""
                self.spinner.text = "Select Size"

    def delete_from_order(self, instance):
        if self.__selected_product is None:
            return

        selected_row = None
        for row in self.order_table.row_data:
            if row[0] == self.__selected_product[0] and row[1] == self.__selected_product[1]:
                selected_row = row
                break

        if selected_row:
            self.order_table.row_data.remove(selected_row)
            self.order_table.update_row

    # create method to reset all     
    def reset(self,instance):
        self.order_table.row_data = []
        self.quantity_input.text = " "
        self.spinner.text = "Select Size"
        self.name_field.text = " "
        self.phone_field.text = " "
        self.invoice_label.text = "Invoice will be printed here."

    # Method for calculating the order amount and generating an invoice
    def calculate_amount(self, instance):
        restaurant = Restaurant("Qender", "Peje")
        name = self.name_field.text
        phone_number = self.phone_field.text
        client = Client(name, phone_number)
        order_calculator = OrderCalculatorKS() if self.check_box_ks.active else OrderCalculatorGER()
        order = Order()
        order_manager = OrderManager()

        # Populate the order with products from the order table
        for product in self.order_table.row_data:
            product_id = int(product[0])
            product_name = str(product[1])
            price = float(product[2])
            quantity = float(product[3])
            size = self._get_size(str(product[4]))
            ordered_product = Product(product_name, product_id,price)
            order_manager.add_order_item(order, ordered_product, quantity, size)
        order_amount = order_calculator.calculate_order_amount(order)

        # create instance of invoice builder to get the invoice
        order_printer = InvoiceBuilder()
        # Calculate the invoice by calling the 'get_order_info' method of the 'order_printer' object
# with parameters representing the restaurant, client, order, order amount, and VAT rate.
        invoice = order_printer.get_order_info(restaurant, client, order, order_amount, order_calculator.get_vat_rate(False))

        # Set the text of the 'invoice_label' widget to the calculated invoice string.
        self.invoice_label.text = invoice

# Define a private method '_get_size' that converts a string representation of order item size
# to the corresponding 'OrderItemSize' enum value.
    def _get_size(self, order_item_size):
        match order_item_size:
            case "Small":
                return OrderItemSize.SMALL
            case "Medium":
                return OrderItemSize.MEDIUM
            case "Large":
                return OrderItemSize.LARGE
            case "XXL":
                return OrderItemSize.XXL
            case _:
                # Print a message if the provided size is not recognized.
                print("No valid order item size: " + order_item_size)
                # Return a default value (1) in case of an unrecognized size.
                return 1

    
RestaurantAPP().run()