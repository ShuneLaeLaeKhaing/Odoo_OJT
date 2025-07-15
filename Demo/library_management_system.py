from datetime import datetime, timedelta

class Book:
    def __init__(self,title,author,isbn):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.available = True
        self.borrowed_by = None
        self.due_date = None

    def __str__(self):
        status = "Available" if self.available else f"Borrowed (Due: {self.due_date})"
        return f"'{self.title}' by {self.author} (ISBN: {self.isbn}) - {status}"

class User:
    def __init__(self,name,user_id):
        self.name = name
        self.user_id = user_id 
        self.borrowed_books = []

    def can_borrow(self):
        return len(self.borrowed_books) < self.max_books
    
    def borrow_book(self, book, due_date):
        if self.can_borrow():
            book.due_date = due_date.strftime("%Y-%m-%d")  
            self.borrowed_books.append(book)
            return True
        return False
    
    def return_book(self, book):
        for borrowed_book in self.borrowed_books:
            if borrowed_book.isbn == book.isbn:  
                self.borrowed_books.remove(borrowed_book)
                return True
        return False
    
    def __str__(self):
        return f"{self.__class__.__name__}: {self.name} (ID: {self.user_id}) - {len(self.borrowed_books)}/{self.max_books} books borrowed"

class Teacher(User):
    max_books = 5

class Student(User):
    max_books = 3

class Library:
    def __init__(self):
        self.books = []
        self.users = []

    def add_book(self,title,author,isbn):
        if not any(book.isbn == isbn for book in self.books):
            self.books.append(Book(title,author,isbn))
            return True
        return False
    
    def register_user(self,name,user_id,user_type):
        user_id = str(user_id)
        if not any(user.user_id == user_id for user in self.users):
            if user_type.lower() == 'teacher':
                self.users.append(Teacher(name,user_id))
            elif user_type.lower() == 'student':
                self.users.append(Student(name,user_id))
            else:
                return False
            return True
        return False
    
    def find_book(self,isbn):
        for book in self.books:
            if book.isbn == isbn:
                return book
        return None
    
    def find_user(self,user_id):
        user_id = str(user_id)
        for user in self.users:
            if str(user.user_id) == str(user_id):
                return user
        return None

    def borrow_book(self,user_id,isbn,days=14):
        user_id = str(user_id)
        user = self.find_user(user_id)
        book = self.find_book(isbn)

        if not user or not book:
            return False
        
        if not book.available:
            return False
        
        if not user.can_borrow():
            return False
        
        due_date = datetime.now() + timedelta(days=days)
        book.available = False
        book.borrowed_by = user_id
        book.due_date = due_date.strftime("%Y-%m-%d")
        user.borrow_book(book,due_date)
        return True
    
    def return_book(self, isbn):
        book = self.find_book(isbn)
        if not book:
            return None
        
        if book.available:
            return None

        user = self.find_user(book.borrowed_by)

        if not user:
            return None
            
        book.available = True
        book.borrowed_by = None
        late = datetime.now() > datetime.strptime(book.due_date, "%Y-%m-%d")
        book.due_date = None
        success = user.return_book(book)
        
        return late

    def show_all_books(self):
        for book in self.books:
            print(book)

    def show_all_users(self):
        for user in self.users:
            print(user)
            if user.borrowed_books:
                print(" Borrowed Books:")
                for book in user.borrowed_books:
                    print(f"    -{book.title} (Due: {book.due_date})")

def library_menu():
    library = Library()
    
    while True:
        print("\nLibrary Management System")
        print("1. Add Book")
        print("2. Register User")
        print("3. Borrow Book")
        print("4. Return Book")
        print("5. Show All Books")
        print("6. Show All Users")
        print("7. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            title = input("Enter book title: ")
            author = input("Enter author name: ")
            isbn = input("Enter ISBN: ")
            if library.add_book(title, author, isbn):
                print("Book added successfully!")
            else:
                print("Book with this ISBN already exists.")
        
        elif choice == '2':
            name = input("Enter user name: ")
            user_id = input("Enter user ID: ")
            user_type = input("Enter user type (teacher/student): ")
            if library.register_user(name, user_id, user_type):
                print("User registered successfully!")
            else:
                print("User with this ID already exists or invalid user type.")
        
        elif choice == '3':
            user_id = input("Enter your user ID: ")
            isbn = input("Enter ISBN of book to borrow: ")
            days = input("Enter loan duration in days (default 14): ") or 14
            if library.borrow_book(user_id, isbn, int(days)):
                print("Book borrowed successfully!")
            else:
                print("Failed to borrow book. Check availability or your borrowing limit.")
        
        elif choice == '4':
            isbn = input("Enter ISBN of book to return: ")
            late = library.return_book(isbn)
            if late is None:
                print("Book not found or already available.")
            else:
                if late:
                    print("Book returned late!")
                else:
                    print("Book returned on time!")
        
        elif choice == '5':
            print("\nAll Books:")
            library.show_all_books()
        
        elif choice == '6':
            print("\nAll Users:")
            library.show_all_users()
        
        elif choice == '7':
            print("Exiting Library System.")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    library_menu()