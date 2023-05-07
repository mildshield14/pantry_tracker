import sqlite3
import tkinter as tk
from tkinter import Tk, ttk
from datetime import date
from tkinter import simpledialog, messagebox


def create_pantry_table(conn):
    # Create the pantry table if it doesn't exist.
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pantry (
            id INTEGER PRIMARY KEY,
            item_name TEXT,
            expiration_date DATE,
            amount_bought INTEGER,
            amount_remaining INTEGER
        )
    ''')
    conn.commit()


def add_item(conn, id, item_name, expiration_date, amount_bought):
    # Add a new item to the pantry table.
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO pantry (item_name, expiration_date, amount_bought, amount_remaining) VALUES (?, ?, ?, ?)',
        (item_name, expiration_date, amount_bought, amount_bought))
    conn.commit()


def get_items(conn):
    # Retrieve all items from the pantry table.
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pantry')
    rows = cursor.fetchall()
    return rows


def update_item(conn, item_id, update_data):
    # Update the amount remaining for an item in the pantry table.
    with conn:
        cursor = conn.cursor()
        l = update_data
        # chatgpt code
        set_values = ', '.join([f'{key} = ?' for key in update_data.keys()])
        update_data = tuple(update_data.values()) + (item_id,)
        # end of chatgpt code
        cursor.execute(f'UPDATE pantry SET {set_values} WHERE id = ?', update_data)

        if str(update_data) == ("(0.0" + ", " + str(item_id) + ")"):
            cursor.execute(f'DELETE FROM pantry WHERE id={item_id}')


def delete_item(conn, item_id):
    # Update the amount remaining for an item in the pantry table.
    with conn:
        cursor = conn.cursor()
        cursor.execute(f'DELETE FROM pantry WHERE id={item_id}')

    # print(("(0.0" + ", " + str(item_id) + ")"))


def create_main_window(conn):
    # Create the main window.
    window = Tk()

    # Create the item list widget
    item_list = ttk.Treeview(window)
    item_list['columns'] = ('ID', 'Name', 'Expiration Date', 'Amount Bought', 'Amount Remaining')
    item_list.heading('ID', text='ID')
    item_list.heading('Name', text='Name')
    item_list.heading('Expiration Date', text='Expiration Date')
    item_list.heading('Amount Bought', text='Amount Bought')
    item_list.heading('Amount Remaining', text='Amount Remaining')
    item_list.column('ID', width=50, stretch=False)
    item_list.column('Name', width=150, stretch=False)
    item_list.column('Expiration Date', width=150, stretch=False)
    item_list.column('Amount Bought', width=150, stretch=False)
    item_list.column('Amount Remaining', width=150, stretch=False)

    # Add buttons to the main window
    add_item_button = ttk.Button(window, text='Add Item', command=lambda: add_item_dialog(conn, item_list))

    use_item_button = ttk.Button(window, text='Use Item', command=lambda: use_item_dialog(conn, item_list))

    delete_item_button = ttk.Button(window, text='Delete Item', command=lambda: delete_item_dialog(conn, item_list))

    search_item_button = ttk.Button(window, text='Search Item', command=lambda: search_item_dialog(conn, item_list))


    # Set the size and title of the main window
    window.geometry('800x600')
    window.title('Pantry Manager')

    # Add the item list and buttons to the main window
    item_list.pack(expand=True, fill='both')
    add_item_button.pack(side='left')
    use_item_button.pack(side='left')
    delete_item_button.pack(side='left')
    search_item_button.pack(side='left')
    # Refresh the list of items displayed in the main window
    refresh_list(conn, item_list)

    # Start the main event loop
    window.mainloop()


def add_item_dialog(conn, item_list):
    # create the dialog window and widgets
    add_item_window = tk.Toplevel()
    add_item_window.title('Add Item')
    tk.Label(add_item_window, text='Name:').grid(row=0, column=0)
    name_entry = tk.Entry(add_item_window)
    name_entry.grid(row=0, column=1)
    tk.Label(add_item_window, text='Quantity:').grid(row=1, column=0)
    quantity_entry = tk.Entry(add_item_window)
    quantity_entry.grid(row=1, column=1)

    tk.Label(add_item_window, text='Expiration Date:').grid(row=3, column=0)
    expiration_entry = tk.Entry(add_item_window)
    expiration_entry.grid(row=3, column=1)
    add_item_button = tk.Button(add_item_window, text='Add Item',
                                command=lambda: (
                                    add_item(conn, None, name_entry.get(), expiration_entry.get(),
                                             quantity_entry.get()),
                                    refresh_list(conn, item_list),
                                    add_item_window.destroy()))
    add_item_button.grid(row=4, column=1)


def refresh_list(conn, item_list):
    """Refresh the list of items displayed in the main window."""
    items = get_items(conn)
    for row in item_list.get_children():
        item_list.delete(row)
    for item in items:
        item_list.insert('', 'end', values=item)


def use_item_dialog(conn, item_list):
    # Create a dialog to use an item.
    selected_item = item_list.focus()
    if not selected_item:
        messagebox.showerror('Error', 'No item selected')
        return
    item_data = item_list.item(selected_item)['values']
    item_name = item_data[1]
    current_quantity = item_data[4]
    if current_quantity == 0:
        messagebox.showwarning('Warning', 'Item out of stock')
        return
    quantity = simpledialog.askfloat('Use Item', f'How much {item_name} are you using?')
    if quantity is None:
        return
    if quantity <= 0:
        messagebox.showerror('Error', 'Invalid quantity')
        return
    new_quantity = current_quantity - quantity
    update_item(conn, item_data[0], {'amount_remaining': new_quantity})
    refresh_list(conn, item_list)
    messagebox.showinfo('Item Used', f'{quantity} {item_name} used')


def delete_item_dialog(conn, item_list):
    # Create a dialog to use an item.
    selected_item = item_list.focus()
    if not selected_item:
        messagebox.showerror('Error', 'No item selected')
        return
    item_data = item_list.item(selected_item)['values']

    delete_item(conn, item_data[0])
    refresh_list(conn, item_list)
    messagebox.showinfo('Delete ', f' {item_data[1]} has been deleted')


def search_item_dialog(conn, item_list):
    # create the dialog window and widgets
    search_item_window = tk.Toplevel()
    search_item_window.title('Search Item')
    tk.Label(search_item_window, text='Name:').grid(row=0, column=0)
    name_entry = tk.Entry(search_item_window)
    name_entry.grid(row=0, column=1)

    tk.Label(search_item_window, text='Expiration Date:').grid(row=3, column=0)
    expiration_entry = tk.Entry(search_item_window)
    expiration_entry.grid(row=3, column=1)


    search_item_button = tk.Button(search_item_window, text='Search Item',
                                   command=lambda: (
                                       search_item(conn, name_entry.get(), expiration_entry.get()),
                                       refresh_list(conn, item_list),
                                       show_results(search_item(conn, name_entry.get(), expiration_entry.get())),
                                       search_item_window.destroy()))
    search_item_button.grid(row=4, column=1)

def show_results(results):
    result_window = tk.Toplevel()
    result_window.title('Search Results')

    # Create a label to display the results
    result_label = tk.Label(result_window, text=results)
    result_label.pack()

    # Add a button to close the window
    close_button = tk.Button(result_window, text='Close', command=result_window.destroy)
    close_button.pack()

def search_item(conn, item_name, expiration_date):
    # Add a new item to the pantry table.
    cursor = conn.cursor()

    if item_name != "" and expiration_date != "":
        cursor.execute('SELECT * FROM pantry WHERE item_name = ? AND expiration_date = ? ', (item_name,expiration_date,))
    elif item_name != "" and expiration_date == "":
        print (item_name)
        cursor.execute('SELECT * FROM pantry WHERE item_name = ?', (item_name,))
    elif expiration_date != "" and item_name == "":
        cursor.execute('SELECT * FROM pantry WHERE expiration_date = ?', (expiration_date,))

    rows = cursor.fetchall()
    #chatgpt
    if not rows:
        return "No matching items found."

    result = f"{'ID':<5} {'Item':<20} {'Expiration Date':<20} {'Quantity':<10} {'Min Quantity':<10}\n"
    result += "-" * 65 + "\n"

    for row in rows:
        result += f"{row[0]:<5} {row[1]:<20} {row[2]:<20} {row[3]:<10} {row[4]:<10}\n"
#end chatgpt
    return result


conn = sqlite3.connect('pantry.db')
create_main_window(conn)
