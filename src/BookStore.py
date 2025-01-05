import mysql.connector
from getpass import getpass
import datetime

# Will be used for connection to database
# You should change those variables if you want to connect the app to your own database
def connect_to_database():
    return mysql.connector.connect(
        host="localhost", # should be the same for most computers
        database="bookstore",
        user="root", # should be the same for most computers
        password="your_password_here"
    )

def register_member():
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    address = input("Enter street address: ")
    city = input("Enter city: ")
    zip = input("Enter zip: ")
    phone = input("Enter phone number: ")
    email = input("Enter email address: ")
    password = getpass("Enter password: ")  # Securely input password

    # To insert the new member
    # Establish a connection to the database and create a cursor for executing queries
    connection = connect_to_database()
    cursor = connection.cursor()
    insert_query = """
    INSERT INTO members (fname, lname, address, city, zip, phone, email, password)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (first_name, last_name, address, city, zip, phone, email, password))
    connection.commit() # Commit changes to database
    cursor.close() # Don't forget to close the connection after the work is done to prevent errors
    connection.close()

    print("You have registered successfully!")
    input("Press Enter to go back to main menu ")


def member_login():
    global global_member_id # userid of the member will be saved globally to be used in the whole application
    email = input("Enter email address: ")
    password = getpass("Enter password: ")  # Securely enter password

    # Connect and get the member from the database
    connection = connect_to_database()
    cursor = connection.cursor()
    login_query = "SELECT * FROM members WHERE email=%s AND password=%s"
    cursor.execute(login_query, (email, password))
    member = cursor.fetchone()
    cursor.close()
    connection.close()

    if member:
        print("Login successful!")
        global_member_id = member[0]  # save userid
        member_menu() # go to member menu
    else:
        print("Login failed. Please try again.")


def browse_by_subject():
    connection = connect_to_database()  
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT subject FROM books ORDER BY subject ASC")
    subjects = cursor.fetchall()

    # Display the list of subjects for the user to choose from
    print("Choose a subject:")
    for idx, subject in enumerate(subjects, 1):
        print(f"{idx}. {subject[0]}")

    # Get the choice of subject, adjusting for zero-based index
    choice = int(input("Enter your choice: ")) - 1
    selected_subject = subjects[choice][0]
    # Retrieve books that match the selected subject, ordered by title
    cursor.execute("SELECT isbn, author, title, price, subject FROM books WHERE subject = %s ORDER BY title ASC", (selected_subject,))
    books = cursor.fetchall()

    index = 0 # Initialize an index to control the display of books in pages
    while True:
        print(f"\nBooks on {selected_subject}:")
        for book in books[index:index+2]:
            # Access tuple elements by index
            print(f"ISBN: {book[0]}")  
            print(f"Author: {book[1]}")   
            print(f"Title: {book[2]}")    
            print(f"Price: {book[3]}")   
            print(f"Subject: {book[4]}\n")  

        # Prompt for user action: add to cart, browse more, or return to menu
        action = input("Enter ISBN to add to Cart or\nEnter (n) to browse or\nENTER to go back to menu: ").strip()

        if action == '':
            return  
        elif action.lower() == 'n':
            index += 2 # Increment the index to display the next set of books
            if index >= len(books):
                print("No more books in this subject.")
                break # Exit the loop if there are no more books to display
        else: # Add a book to the cart if an ISBN is entered
            isbn = action
            quantity = int(input("Enter the quantity: "))
            try:
                add_to_cart(isbn, quantity)
            except Exception as e:
                print(f"An error occurred: {e}")

        # Check if the end of the book list has been reached
        if index >= len(books):
            print("You have reached the end of the list.")
            break

    cursor.close()
    connection.close()


def add_to_cart(isbn, quantity):
    global global_member_id
    connection = connect_to_database()  
    cursor = connection.cursor()
    cursor.execute("SELECT price FROM books WHERE isbn = %s", (isbn,))
    book = cursor.fetchone()
    # Check if the book exists
    if book:
        # Insert into thecart table
        insert_query = """
        INSERT INTO thecart (userid, isbn, qty)
        VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (global_member_id, isbn, quantity))
        connection.commit()
        cursor.close()
        connection.close()
        print(f"Added {quantity} of {isbn} to the cart for user {global_member_id}.")
    else:
        print("Book with the given ISBN does not exist.")


def check_out():
    global global_member_id
    connection = connect_to_database()
    cursor = connection.cursor()

    # Fetch the contents of thecart for the current user
    cursor.execute("SELECT isbn, qty FROM thecart WHERE userid = %s", (global_member_id,))
    cart_contents = cursor.fetchall()

    # Calculate the total cost
    total_cost = 0
    max_title_length = 30  # Define the maximum length of the title (used for better interface)
    print("Current Cart Contents:")
    print(f"{'ISBN':<15}{'Title':<30}{'Price':>10}{'Qty':>10}{'Total':>10}")
    
    # Display thecart contents
    for item in cart_contents:
        isbn, quantity = item  # Unpack the tuple
        cursor.execute("SELECT title, price FROM books WHERE isbn = %s", (isbn,))
        book_data = cursor.fetchone()
        book_title = book_data[0]  # Access by index
        book_price = book_data[1]  
        item_total = book_price * quantity
        total_cost += item_total
        # Truncate the title if it's longer than max_title_length (used for better interface)
        display_title = (book_title[:max_title_length - 3] + '...') if len(book_title) > max_title_length else book_title
        print(f"{isbn:<15}{display_title:<30}{book_price:>10.2f}{quantity:>10}{item_total:>10.2f}")
    
    print(f"{'Total':<45}{total_cost:>10.2f}")

    # if thecart is empty, return to member menu, else continue
    if cart_contents:
        pass
    else:
        input("Enter to go back to store ")
        return

    # Confirm checkout
    proceed = input("Proceed to check out (Y/N)?: ").strip().lower()
    if proceed == 'y':
        received_date = datetime.datetime.now()
        shipment_date = received_date + datetime.timedelta(weeks=1)
        
        # Get address of the member
        cursor.execute("SELECT address, city, zip FROM members WHERE userid = %s", (global_member_id,))
        thedata = cursor.fetchone()
        ship_address = thedata[0]
        ship_city = thedata[1]
        ship_zip = thedata[2]

        cursor.execute("SELECT MAX(ono) FROM orders")
        last_ono = cursor.fetchone()[0] # Create the ono number
        next_ono = 1 if last_ono is None else last_ono + 1
        # Insert the order into Order table
        cursor.execute("INSERT INTO orders (userid, ono, created, shipAddress, shipCity, shipZip) VALUES (%s, %s, %s, %s, %s, %s)",
               (global_member_id, next_ono, received_date, ship_address, ship_city, ship_zip))
        
        # Insert the order into orderdetails table
        for item in cart_contents:
            cursor.execute("INSERT INTO orderdetails (ono, isbn, qty, amount) VALUES (%s, %s, %s, %s)",
                           (next_ono, item[0], item[1], book_price))

        # Clear thecart after checkout
        cursor.execute("DELETE FROM thecart WHERE userid = %s", (global_member_id,))
        
        connection.commit()
        cursor.close()
        connection.close()

        # Get the invoice of the order
        get_invoice(next_ono, ship_address, ship_city, ship_zip, shipment_date)
        
        
def get_invoice(next_ono, ship_address, ship_city, ship_zip, shipment_date):
    global global_member_id
    connection = connect_to_database()
    cursor = connection.cursor(buffered=True)

    try:
        cursor.execute("SELECT fname, lname FROM members WHERE userid = %s", (global_member_id,))
        member_data = cursor.fetchone()
        member_name = f"{member_data[0]} {member_data[1]}" # get member name
        
        # get order details
        cursor.execute("SELECT isbn, qty FROM orderdetails WHERE ono = %s", (next_ono,))
        contents = cursor.fetchall()

        print("\nCheckout complete. Order has been saved.")
        print(f"Invoice for Order no.{next_ono}")
        print("Shipping Address")
        print(f"Name: {member_name}")
        print(f"Address: {ship_address}")
        print(f"City: {ship_city}")
        print(f"Zip: {ship_zip}")
        print("\n" + "-" * 60)

        # Display the invoice
        total_cost = 0
        max_title_length = 30  
        print(f"{'ISBN':<15}{'Title':<30}{'Price':>10}{'Qty':>10}{'Total':>10}")
        for item in contents:
            isbn, quantity = item
            cursor.execute("SELECT title, price FROM books WHERE isbn = %s", (isbn,))
            book_data = cursor.fetchone()
            book_title, book_price = book_data
            item_total = book_price * quantity
            total_cost += item_total
            display_title = (book_title[:max_title_length - 3] + '...') if len(book_title) > max_title_length else book_title
            print(f"{isbn:<15}{display_title:<30}{book_price:>10.2f}{quantity:>10}{item_total:>10.2f}")
            
        print(f"{'Total':<45}{total_cost:>10.2f}")
        print("Estimated delivery date: ", shipment_date.strftime("%Y-%m-%d"))
        input("Press enter to go back to member menu ")

    finally:
        cursor.close()
        connection.close()


def search_by():
    connection = connect_to_database()
    cursor = connection.cursor()
    print("1. Author Search")
    print("2. Title Search")
    print("3. Go Back to Member Menu")
    choice = input("Type in your option: ")
    if choice == '1':
        search_term = input("Enter author name or part of the author name: ")
        # Modify the query to search book by their author
        search_query = """
        SELECT isbn, author, title, price, subject
        FROM books
        WHERE author LIKE %s
        ORDER BY title ASC
        """
    elif choice == '2':
        search_term = input("Enter title or part of the title: ")
        # Modify the query to search book by their title
        search_query = """
        SELECT isbn, author, title, price, subject
        FROM books
        WHERE title LIKE %s
        ORDER BY title ASC
        """
    elif choice == '3':
        return
    else:
        print("Invalid option. Please try again.")

    index = 0
    while True:
        # Prepare the search term to be used with LIKE operator
        like_term = f"%{search_term}%"
        cursor.execute(search_query, (like_term,))
        books = cursor.fetchall()
        
        if books:
            print(f"Found {len(books)} books:")
            for book in books[index:index+2]:
                # Access tuple elements by index
                print(f"ISBN: {book[0]}")  
                print(f"Author: {book[1]}")   
                print(f"Title: {book[2]}")    
                print(f"Price: {book[3]}")   
                print(f"Subject: {book[4]}\n")  
                
            action = input("Enter ISBN to add to Cart or\nEnter (n) to browse or\nENTER to go back to menu: ").strip()

            if action == '':
                return  
            elif action.lower() == 'n':
                index += 2
                if index >= len(books):
                    print("No more books in this search.")
                    break
            else:
                isbn = action
                quantity = int(input("Enter the quantity: "))
                try:
                    add_to_cart(isbn, quantity)
                except Exception as e:
                    print(f"An error occurred: {e}")

            if index >= len(books):
                print("You have reached the end of the list.")
                break

        else:
            print("No books found with this search.")
            break

    cursor.close()
    connection.close()


def member_menu():
    while True:
        print("\n******************************************")
        print("**                                      **")
        print("**   Welcome to the Online Book Store   **")
        print("**              Member Menu             **")
        print("**                                      **")
        print("******************************************")

        print("1. Browse by Subject")
        print("2. Search by Author/Title")
        print("3. Check Out")
        print("4. Logout")
        choice = input("Type in your option: ")
        if choice == '1':
            browse_by_subject()
        elif choice == '2':
            search_by()
        elif choice == '3':
            check_out()
        elif choice == '4':
            return
        else:
            print("Invalid option. Please try again.")


def main_menu():
    while True:
        print("\n******************************************")
        print("**                                      **")
        print("**   Welcome to the Online Book Store   **")
        print("**                                      **")
        print("******************************************")

        print("1. Member Login")
        print("2. New Member Registration")
        print("q. Quit")
        choice = input("Type in your option: ")
        if choice == '1':
            member_login()
        elif choice == '2':
            register_member()
        elif choice.lower() == 'q':
            break
        else:
            print("Invalid option. Please try again.")


# Run the application
main_menu()
