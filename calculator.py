import tkinter as tk

def get_entry_values():
    value1 = ent_longitude.get()
    value2 = ent_latitude.get()
    print(f"Entry 1 Value: {value1}")
    print(f"Entry 2 Value: {value2}")

root = tk.Tk()
root.title("Calculator for Meteorology")

lbl_1 = tk.Label(root, text="Longitude of HK:")
lbl_1.grid(row=0, column=0, padx=5, pady=5, sticky="w")
lbl_2 = tk.Label(root, text="22.3193")
lbl_2.grid(row=0, column=1, padx=5, pady=5, sticky="w")
lbl_3 = tk.Label(root, text="Latitude of HK:")
lbl_3.grid(row=0, column=2, padx=5, pady=5, sticky="w")
lbl_4 = tk.Label(root, text="114.1694")
lbl_4.grid(row=0, column=3, padx=5, pady=5, sticky="w")


lbl_longitude = tk.Label(root, text="Longitude:")
lbl_longitude.grid(row=1, column=0, padx=5, pady=5, sticky="w")
ent_longitude = tk.Entry(root)
ent_longitude.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

# Create the second Entry widget
lbl_latitude = tk.Label(root, text="Latitude:")
lbl_latitude.grid(row=1, column=2, padx=5, pady=5, sticky="w")
ent_latitude = tk.Entry(root)
ent_latitude.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

# Create a button to demonstrate getting the values
button = tk.Button(root, text="Calculate Distance", command=get_entry_values)
button.grid(row=2, column=0, columnspan=4, pady=10) # Span across all columns

# Configure column weights to make entry fields expand with window resizing
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(3, weight=1)

# Start the Tkinter event loop
root.mainloop()