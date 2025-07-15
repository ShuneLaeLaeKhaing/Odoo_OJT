class Product:
    def __init__(self,product_id,name,price,stock):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock = stock

    def __str__(self):
        return f"{self.name} (ID: {self.product_id}) - ${self.price:.2f} - {self.stock} in stock"

class User:
    def __init__(self,username,password):
        self.username = username
        self.password = password

class Admin(User):
    def __init__(self,username,password):
        super().__init__(username,password)
        self.role = "admin"

    def add_product(self,products,prodcut_id,name,price,stock):
        if not any(p.product_id == prodcut_id for p in products):
            products.append(Product(prodcut_id,name,float(price),int(stock)))
            return True
        return False

    def update_product(self,products,product_id,new_stock):
        for product in products:
            if product.product_id == product_id:
                product.stock = int(new_stock)
                return True
        return False

class Customer(User):
    def __init__(self,username,password):
        super().__init__(username,password)
        self.role = "customer"
        self.cart = ShoppingCart()

    def add_to_cart(self,products,product_id,quantity):
        product = next((p for p in products if p.product_id == product_id and p.stock >=quantity),None)
        if product:
            self.cart.add_item(product,quantity)
            return True
        return False
    
    def remove_from_cart(self,product_id):
        return self.cart.remove_item(product_id)
    
    def view_cart(self):
        return self.cart.view_cart()
    
    def checkout(self,products):
        total = self.cart.view_cart()
        if total == 0:
            return 0
        
        for item in self.cart.get_items():
            if item['product'].stock < item['quantity']:
                print(f"Sorry, {item['product'].name} doesn't have enough stock.")
                return 0
            
        for item in self.cart.get_items():
            item['product'].stock -= item['quantity']

        total = self.cart.calculate_total()
        self.cart.clear_cart()
        return total
    
class ShoppingCart:
    def __init__(self):
        self.items = []

    def add_item(self,product,quantity):
        for item in self.items:
            if item['product'].product_id == product.product_id:
                item['quantity'] += quantity
                return True
            
        self.items.append({'product':product,'quantity':quantity})
        return True
    
    def remove_item(self,product_id):
        for item in self.items[:]:
            if item['product'].product_id == product_id:
                self.items.remove(item)
                return True
        return False
    
    def calculate_total(self):
        total =0
        for item in self.items:
            total += item['product'].price * item['quantity']
        return total
    
    def view_cart(self):
        if not self.items:
            print("Your cart is  empty.")
            return 0
        
        print("\n Your Shopping Cart:")
        for item in self.items:
            product = item['product']
            quantity = item['quantity']
            subtotal = product.price * quantity
            print (f"{product.name} x {quantity} - ${subtotal:.2f}")
        
        total = self.calculate_total()
        print(f"Total: ${total:.2f}")
        return total
    
    def clear_cart(self):
        self.items = []

    def get_items(self):
        return self.items
    

def ecommerce_menu():
    #Sample data
    products = [
        Product("1001","Laptop",999.99,10),
        Product("1002","Smartphone",699.99,15),
        Product("1003","Headphones",149.99,20)
    ]

    users =[
        Admin("admin","admin123"),
        Customer("GoJo","gojo123")
    ]

    current_user = None

    while True:
        if not current_user:
            print("\nE-Commerce Shopping System")
            print("1. Admin Login")
            print("2. Customer Login")
            print("3. Exit")

            choice = input("Enter your choice:")

            if choice == '1':
                username = input("Username: ")
                password = input("Password: ")
                user = next ((u for u in users if u.username == username and u.password == password and isinstance(u,Admin)),None)
                if user:
                    current_user = user
                    print(f"Welcome Admin {username}!")
                else:
                    print("Invalid admin credentials.")

            elif choice == '2':
                username = input("Username: ")
                password = input("Password: ")
                user = next((u for u in users if u.username == username and u.password == password and isinstance(u,Customer)), None)
                if user:
                    current_user = user
                    print(f"Welcome Customer {username}!")
                else:
                    print("Invalid custome credentials or user not found.")

            elif choice == '3':
                print("Exiting E-Commerce System.")
                break

            else:
                print("Invalid choice.Please try again.")

        elif  isinstance(current_user,Admin):
            print("\nAdmin Menu")
            print("1. Add Product")
            print("2. Update Product Stock")
            print('3. View Products')
            print("4. Logout")

            choice = input("Enter your choice: ")

            if choice == '1':
                product_id = input("Enter product ID: ")
                name = input("Enter product name: ")
                price = input("Enter product price: ")
                stock = input("Enter product stock: ")
                if current_user.add_product(products, product_id, name, price, stock):
                    print("Product added successfully!")
                else:
                    print("Product with this ID already exists.")
            
            elif choice == '2':
                product_id = input("Enter product ID: ")
                new_stock = input("Enter new stock quantity: ")
                if current_user.update_product(products, product_id, new_stock):
                    print("Stock updated successfully!")
                else:
                    print("Product not found.")
            
            elif choice == '3':
                print("\nAll Products:")
                for product in products:
                    print(product)
            
            elif choice == '4':
                current_user = None
                print("Logged out successfully.")
            
            else:
                print("Invalid choice. Please try again.")

        elif isinstance(current_user,Customer):
            print("\nCustomer Menu")
            print("1. View Products")
            print("2. Add to Cart")
            print("3. Remove from Cart")
            print("4. View Cart")
            print("5. Checkout")
            print("6. Logout")

            choice = input("Enter your choice: ")

            if choice == '1':
                print("\n Available Products:")
                for product in products:
                    print(product)

            elif choice == '2':
                product_id = input("Enter product ID: ")
                quantity = int(input("Enter quantity: "))
                if current_user.add_to_cart(products,product_id,quantity):
                    print("Product added to cart!")
                else:
                    print("Product not found or insufficient stock.")

            elif choice == '3':
                product_id = input("Enter product ID to remove: ")
                if current_user.remove_from_cart(product_id):
                    print("Product removed from cart.")
                else:
                    print("Product not found in your cart.")

            elif choice == '4':
                current_user.view_cart()

            elif choice == '5':
                total = current_user.checkout(products)
                if total >0:
                    print(f"Order completed! Total : ${total:.2f}")

            elif choice == '6':
                current_user = None
                print("Logged out successfully.")

            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    ecommerce_menu()