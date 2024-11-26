import sqlite3
import tkinter as tk
from tkinter import messagebox
from bst import BinarySearchTree
from collections import deque



class URepair:

    #Initiate App
    def __init__(self):
        
        self.clients = {}
        self.professionals = {}
        self.service_requests = {} 
        self.services_tree = BinarySearchTree()  
        self.load_data_from_db()  
        self.load_services() 
        self.create_initial_page() 
    

    #Get Data from db and put in dictionary and queues 
    def load_data_from_db(self):
        with sqlite3.connect('user_db.db') as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM users_clients;')
            self.clients= {
                row[0]: {"username": row[1], "password": row[2], "name": row[3], "email": row[4]}
                for row in cursor.fetchall()
            }

            cursor.execute('SELECT * FROM pro_users;')
            self.professionals= {
                row[0]: {"username": row[1], "password": row[2], "name": row[3], "email": row[4]}
                for row in cursor.fetchall()
            }

            cursor.execute('SELECT * FROM pro_users;')
            for row in cursor.fetchall():
                self.professionals[row[0]] = {"username": row[1], "password": row[2], "name": row[3], "email": row[4]}
                self.service_requests[row[0]] = deque()  # Initialize an empty deque for each professional

            # Load pending service requests and add them to the appropriate professional's queue
            cursor.execute("""
                SELECT request_id, client_id, professional_id, service_type, message, client_email
                FROM service_requests
                WHERE status = 'pending'
            """)
            for request in cursor.fetchall():
                request_dict = {
                    'request_id': request[0],
                    'client_id': request[1],
                    'professional_id': request[2],
                    'service_type': request[3],
                    'message': request[4],
                    'client_email': request[5],
                    'status': 'pending'
                }
                self.service_requests[request[2]].append(request_dict)

    def load_services(self):
        conn=sqlite3.connect('user_db.db')
        cursor = conn.cursor()

        cursor.execute("SELECT id, professional_id, service_name, service_description, price FROM services")
        services= cursor.fetchall()

        for service in services:
            service_data={
                "id": service[0],
                "professional_id": service[1],
                "name": service[2],
                "description": service[3],
                "price": service[4]
            }
            self.services_tree.insert(service[2].lower(), service_data)
        conn.close()

        #Handle requests 
    def send_request(self, client_id, pro_id, service_type, message, client_email):
        pro_id = int(pro_id)
        client_id = int(client_id)
        conn= sqlite3.connect('user_db.db')
        cursor= conn.cursor()

        try: 
            cursor.execute("""
                INSERT INTO service_requests(client_id, professional_id, service_type, message, client_email, status)
                VALUES (?, ?, ?, ?, ?, 'pending')
            """, (client_id, pro_id, service_type, message, client_email))
            conn.commit()
            request_id = cursor.lastrowid

            new_request={
                'request_id': request_id,
                'client_id': client_id,
                'professional_id': pro_id,
                'service_type': service_type,
                'message': message,
                'client_email': client_email,
                'status': 'pending'
            }

            if pro_id in self.service_requests:
                self.service_requests[pro_id].append(new_request)
                print("Service request enqueued succesfully.")
            else:
                print(f"No queue found for professional ID {pro_id}. Creating a new queue.")
                self.service_requests[pro_id] = deque([new_request])
            
            print("Service request sent and queued successfully.")
        except sqlite3.Error as e:
            print(f"An error occurred when inserting the service request into the database: {e}")
        finally:
            conn.close()

    #Look for service and request services. 
    def look_for_service(self, client_id, client_email):
        look_for_service_window = tk.Tk()
        look_for_service_window.title('Look for service')
        look_for_service_window.geometry('500x600')
        service_options = [
            "plumbing",
            "electrical",
            "carpentry",
            "furniture assembling",
            "painting"
        ]
        service_var= tk.StringVar(look_for_service_window)
        service_var.set(service_options[0])
        search_service_label= tk.Label(look_for_service_window, text="Enter the service you're looking for")
        search_service_label.pack()
        service_name_menu = tk.OptionMenu(look_for_service_window, service_var, *service_options)
        service_name_menu.pack()

        result_label=tk.Label(look_for_service_window, text="")
        result_label.pack()

        def search():
            service_name= service_var.get()
            result= self.services_tree.search(service_name)
            if result:
                result_label.config(text=f"Name: {result['name']}, Description: {result['description']}, Price: {result['price']}")
            else: 
                result_label.config(text="Service not found")
        
        search_button = tk.Button(look_for_service_window, text="Search", command=search)
        search_button.pack()
    
        tk.Label(look_for_service_window, text="--- Send Request Below ---").pack()
        service_options = ["plumbing", "electrical", "carpentry", "furniture assembling", "painting"]
        service_type_var = tk.StringVar(look_for_service_window)
        service_type_var.set(service_options[0])  # default value
        tk.Label(look_for_service_window, text="Select Service Type:").pack()
        service_menu = tk.OptionMenu(look_for_service_window, service_type_var, *service_options)
        service_menu.pack()

        tk.Label(look_for_service_window, text="Enter Professional ID:").pack()
        pro_id_entry = tk.Entry(look_for_service_window)
        pro_id_entry.pack()

        tk.Label(look_for_service_window, text="Your Message:").pack()
        message_entry = tk.Entry(look_for_service_window)
        message_entry.pack()

        def on_send_request():
            pro_id = pro_id_entry.get()
            service_type= service_type_var.get()
            message= message_entry.get()
            if pro_id and service_type and message: 
                self.send_request(client_id, pro_id, service_type, message, client_email)
                messagebox.showinfo("Request Sent", "Your service request has been sent successfully.")
            else:
                messagebox.showerror('Error', 'All fields are required  to send a request')
        
        send_button= tk.Button(look_for_service_window, text='Send Request', command=on_send_request)
        send_button.pack()
    
    def show_client_requests(self, client_id):
        requests_window= tk.Tk()
        requests_window.title("Your Service Requests")
        requests_window.geometry('600x400')

        conn = sqlite3.connect('user_db.db')
        cursor = conn.cursor()
        cursor.execute("SELECT requqest_id, professional_id, service_type, message, status FROM service_requests WHERE client_id = ?", (client_id))
        requests = cursor.fetchall()
        conn.close()

        for request in requests: 
            text = f"Request ID: {request[0]}, Professional ID: {request[1]}, Type: {request[2]}, Message: {request[3]}, Status:{request[4]}"
            tk.Label(requests_window, text=text).pack()
    
    def view_requests(self, pro_id):
        view_request_window = tk.Tk()
        view_request_window.title('Manage Requests')
        view_request_window.geometry('600x400')

        pending_frame = tk.Frame(view_request_window, borderwidth=2, relief='sunken')
        pending_frame.pack(fill='both', expand=True, side='left', padx=10, pady=10)

        tk.Label(pending_frame, text='Pending Requests:', font=('Helvetica', 16, 'bold')).pack(anchor='w')
        if pro_id in self.service_requests:
            for req in list(self.service_requests[pro_id]):
                if req['status'] == 'pending':
                    frame = tk.Frame(pending_frame)
                    frame.pack(fill='x', padx=5, pady=5)
                    info = f"ID: {req['request_id']}, Client:{req['client_id']} Type{req['service_type']} Msg: {req['message']}"
                    tk.Label(frame, text=info).pack(side='left')
                    tk.Button(frame, text='Accept', command=lambda req=req: self.accept_request(pro_id, req['request_id'])).pack(side='right')
                    tk.Button(frame, text='Decline', command=lambda req=req: self.decline_request(pro_id, req['request_id'])).pack(side='right')
                else:
                    tk.Label(pending_frame, text='No pending requests found').pack()
        else:
            tk.Label(pending_frame, text='No requests found').pack()

        view_request_window.mainloop()


 

    def decline_request(self, pro_id, request_id):
        conn = sqlite3.connect('user_db.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE service_requests SET status = 'declined' WHERE request_id = ?", (request_id,))
        conn.commit()
        conn.close()

        for req in self.service_requests[pro_id]:
            if req['request_id'] == request_id:
                req['status'] = 'declined'
                break
        self.view_requests(pro_id)


    def accept_request(self, pro_id, request_id):
        # Update in the database
        conn = sqlite3.connect('user_db.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE service_requests SET status = 'accepted' WHERE request_id = ?", (request_id,))
        conn.commit()
        conn.close()

        # Update locally
        for req in self.service_requests[pro_id]:
            if req['request_id'] == request_id:
                req['status'] = 'accepted'
                break
        self.view_requests(pro_id)  # Refresh the view



    #Add new service to database
    def add_service(self, professional_id, service_name, service_description, price):
        if professional_id not in self.professionals:
            messagebox.showerror('Error', "Professional not found")
            print("Professional not found")
            return
        conn = sqlite3.connect('user_db.db')
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO services (professional_id, service_name, service_description, price)
        VALUES (?,?,?,?)
        """, (professional_id, service_name, service_description, price))
        conn.commit()

        new_service_id= cursor.lastrowid

        new_service_data={
            "id": new_service_id,
            "name": service_name,
            "description": service_description,
            "price": price
        }
        self.services_tree.insert(service_name.lower(), new_service_data)

        print('Service added successfully')
        messagebox.showinfo('Success', 'Service added successfully')
        conn.close()

    #Form to add a new service as a professional
    def add_service_window(self, professional_id):
        add_service_window=tk.Tk()
        add_service_window.title("Add Service")
        add_service_window.geometry('500x600')
        service_options = [
        "plumbing",
        "electrical",
        "carpentry",
        "furniture assembling",
        "painting"
        ]
        service_var  = tk.StringVar(add_service_window)
        service_var.set(service_options[0]) 

        service_name_label = tk.Label(add_service_window, text="Service Name:")
        service_name_label.pack()

        service_name_menu= tk.OptionMenu(add_service_window, service_var, *service_options)
        service_name_menu.pack()

        service_description_label= tk.Label(add_service_window, text="Service Description")
        service_description_label.pack()
        service_description_entry= tk.Entry(add_service_window)
        service_description_entry.pack()

        service_price_label= tk.Label(add_service_window, text='Price:')
        service_price_label.pack()
        service_price_entry= tk.Entry(add_service_window)
        service_price_entry.pack()

        def submit_service():
            selected_service_name=service_var.get()
            service_description = service_description_entry.get()
            try:
                price = float(service_price_entry.get())
                self.add_service(professional_id, selected_service_name, service_description, price)
                add_service_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid price. Please enter a valid number.")
        submit_button = tk.Button(add_service_window, text="Add Service", command=submit_service)
        submit_button.pack()


    #Initial Page, decide login 
    def create_initial_page(self):
        self.initial_window = tk.Tk()
        self.initial_window.title('HomePage')
        self.initial_window.geometry("500x600")
        self.initial_window.eval("tk::PlaceWindow . center")

        self.frame1 = tk.Frame(self.initial_window, width=500, height=600, bg="#7fb3d5")
        self.frame1.pack(fill="both", expand=True) 

        self.labelW = tk.Label(self.frame1, text="Welcome to U-Repair", bg="#7fb3d5", fg="white").place(relx=0.5, rely=0.3, anchor="center")

        self.login_existing_button = tk.Button(self.frame1, text='Client Login', command=self.open_clients_login)
        self.login_existing_button.place(relx=0.5, rely=0.4, anchor="center") 

        self.login_new_button = tk.Button(self.frame1, text='Repair Professional Login', command=self.open_pro_login)
        self.login_new_button.place(relx=0.5, rely=0.5, anchor="center") 

        self.initial_window.mainloop()

    #Handle the openeing of the login for the clients 
    def open_clients_login(self):
        self.initial_window.destroy()
        self.create_clients_login_page()

    #Handle the openeing of the login for the professionals
    def open_pro_login(self):
        self.initial_window.destroy()
        self.create_pro_login_page()

    #Login for the clients 
    def create_clients_login_page(self):
        self.clients_login_window = tk.Tk()
        self.clients_login_window .title('Login Clients')
        self.clients_login_window .geometry("500x600")
        self.clients_login_window .eval("tk::PlaceWindow . center")

        tk.Label(self.clients_login_window , text='Username').pack()
        self.username_entry_client = tk.Entry(self.clients_login_window )
        self.username_entry_client.pack()

        tk.Label(self.clients_login_window , text='Password').pack()
        self.password_entry_client = tk.Entry(self.clients_login_window , show='*')
        self.password_entry_client.pack()

        self.login_button = tk.Button(self.clients_login_window , text='Login', command=self.login_clients)
        self.login_button.pack()

        self.clients_login_window .mainloop()

    #Login for the professionals 
    def create_pro_login_page(self):
        self.pro_login_window = tk.Tk()
        self.pro_login_window.title('Login Repair Professionals')
        self.pro_login_window.geometry("500x600")
        self.pro_login_window.eval("tk::PlaceWindow . center")

        tk.Label(self.pro_login_window, text='Username').pack()
        self.username_entry_pro = tk.Entry(self.pro_login_window)
        self.username_entry_pro.pack()

        tk.Label(self.pro_login_window, text="Password").pack()
        self.password_entry_pro = tk.Entry(self.pro_login_window, show="*")
        self.password_entry_pro.pack()

        self.login_button = tk.Button(self.pro_login_window, text="Login", command=self.login_pro)
        self.login_button.pack()

        self.pro_login_window.mainloop()

    
    #Validate login for the clients 
    def login_clients(self):
        username_client = self.username_entry_client.get()
        password_client = self.password_entry_client.get()

        for client_id, client_data in self.clients.items():
            if client_data["username"] == username_client and client_data["password"] == password_client:
                self.show_profile_clients((client_id, client_data["username"], client_data["password"], client_data["name"], client_data["email"]))
                return
        messagebox.showerror('Login Failed', 'Invalid Username or password')

    #Validate login for the professionals 
    def login_pro(self):
        username_pro= self.username_entry_pro.get()
        password_pro= self.password_entry_pro.get()

        for pro_id, pro_data in self.professionals.items():
            if pro_data["username"] == username_pro and pro_data["password"]== password_pro:
                self.show_profile_pro((pro_id, pro_data["username"], pro_data["password"], pro_data["name"], pro_data["email"]))
                return
        messagebox.showerror('Login Failed', 'Invalid Username or password')

    #Profile for the clients
    def show_profile_clients(self, user):
        self.clients_login_window.destroy()
        self.clients_profile_window = tk.Tk()
        self.clients_profile_window.geometry("500x600")
        self.clients_profile_window.title(f'Profile of client {user[1]}')
        tk.Label(self.clients_profile_window, text=f'Name: {user[3]}').pack()
        tk.Label(self.clients_profile_window, text=f'Email: {user[4]}').pack()

        look_for_service_button = tk.Button(self.clients_profile_window, text="Look for service", command=lambda: self.look_for_service(user[0],user[4]))
        look_for_service_button.pack()

        self.clients_profile_window.mainloop()

    #Profile for the professionals
    def show_profile_pro(self, user):
        self.pro_login_window.destroy()
        self.pro_profile_window = tk.Tk()
        self.pro_profile_window.geometry("500x600")
        self.pro_profile_window.title(f'Professional Profile - {user[1]}')
        
        name_label = tk.Label(self.pro_profile_window, text=f"Name: {user[3]}'")
        name_label.pack()

        add_service_button=tk.Button(self.pro_profile_window, text="Add Service", command=lambda: self.add_service_window(user[0]))
        add_service_button.pack()
        view_requests_button= tk.Button(self.pro_profile_window, text="See Requests", command=lambda: self.view_requests(user[0]))
        view_requests_button.pack()
        view_services_button = tk.Button(self.pro_profile_window, text="View Services", command=self.view_services)
        view_services_button.pack()

        self.pro_login_window.mainloop()
    

# Functions to debug-----------------------------------------------------------------------------------------------------------------------------
    def view_services(self):
    # Create a new top-level window
        services_window = tk.Toplevel()
        services_window.title("View All Data")
        services_window.geometry('600x600')  # Adjusted for more content

        # Connect to the database
        conn = sqlite3.connect('user_db.db')
        cursor = conn.cursor()

        # Services Section
        tk.Label(services_window, text="Services:", font=('Helvetica', 16, 'bold')).pack(anchor='w')
        cursor.execute("SELECT * FROM services")
        services = cursor.fetchall()
        for service_id, professional_id, service_name, service_description, price in services:
            service_info = f"ID: {service_id}, Pro ID: {professional_id}, Name: {service_name}, Desc: {service_description}, Price: {price}"
            tk.Label(services_window, text=service_info, anchor="w").pack(fill='x')

        # Clients Section
        tk.Label(services_window, text="Clients:", font=('Helvetica', 16, 'bold')).pack(anchor='w')
        cursor.execute("SELECT * FROM users_clients")
        clients = cursor.fetchall()
        for client_id, username, password, name, email in clients:
            client_info = f"ID: {client_id}, Username: {username}, Name: {name}, Email: {email}"
            tk.Label(services_window, text=client_info, anchor="w").pack(fill='x')

        # Professionals Section
        tk.Label(services_window, text="Professionals:", font=('Helvetica', 16, 'bold')).pack(anchor='w')
        cursor.execute("SELECT * FROM pro_users")
        professionals = cursor.fetchall()
        for pro_id, username, password, name, email in professionals:
            professional_info = f"ID: {pro_id}, Username: {username}, Name: {name}, Email: {email}"
            tk.Label(services_window, text=professional_info, anchor="w").pack(fill='x')

        # Service Requests Section
        tk.Label(services_window, text="Service Requests:", font=('Helvetica', 16, 'bold')).pack(anchor='w')
        cursor.execute("SELECT * FROM service_requests")
        requests = cursor.fetchall()
        for request_id, client_id, pro_id, service_type, message, client_email, status in requests:
            request_info = f"Request ID: {request_id}, Client ID: {client_id}, Pro ID: {pro_id}, Type: {service_type}, Message: {message}, Client Email: {client_email}, Status: {status}"
            tk.Label(services_window, text=request_info, anchor="w").pack(fill='x')

        # Close the database connection
        conn.close()



if __name__ == '__main__':
    URepair()
