import pandas as pd
import tkinter as tk
from tkinter import ttk
from IPython.display import display, clear_output
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np
from PIL import Image, ImageTk
import tkinter.messagebox

data = pd.read_csv(r"C:\My Files\projects\crop recommendation\updated crop\rainfall14-24.csv", skiprows=3, usecols=lambda x: x != 'Unnamed: 0' and x != 'S. No.')
data = data.replace('-', pd.NA).dropna()
data = data[data['STATE'] != 'TOTAL']

soilmoisture = pd.read_csv(r"C:\My Files\projects\crop recommendation\updated crop\Volumetric Soilmoisture_Yearly data for States for 2020 to 2024 (info).csv", skiprows=5)
data['State'] = soilmoisture['State']

availgw = pd.read_csv(r"C:\My Files\projects\crop recommendation\updated crop\(info)State_wise_Ground_Water_Resources_Data_of_India_(In_bcm)_of_2020.csv", skiprows=2)
data['State'] = availgw['State Name']

df = pd.read_csv(r"C:\My Files\projects\crop recommendation\updated crop\data.csv")

def run_linear_regression():

    data['Actual(mm)'] = data['Actual(mm)'].replace('-', pd.NA)
    data['Normal(mm)'] = data['Normal(mm)'].replace('-', pd.NA)

    data['Actual(mm)'] = pd.to_numeric(data['Actual(mm)'])
    data['Normal(mm)'] = pd.to_numeric(data['Normal(mm)'])

    actual_mean = data['Actual(mm)'].mean()
    normal_mean = data['Normal(mm)'].mean()

    X = data[['Actual(mm)', 'Normal(mm)']]
    y = data['Actual(mm)']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mse)

    print('Mean Squared Error:', mse)
    print('Mean Absolute Error:', mae)
    print('Root Mean Squared Error:', rmse)

    upcoming_year_features = [[actual_mean, normal_mean]]
    upcoming_rainfall = model.predict(upcoming_year_features)
    print('Predicted upcoming rainfall(Monthly Timeline):', upcoming_rainfall)

    regression_stats = f"Mean Squared Error: {mse}\nMean Absolute Error: {mae}\nRoot Mean Squared Error: {rmse}\nPredicted MONTHLY upcoming rainfall: {upcoming_rainfall}"
    return regression_stats

def download_data():
    selected_state = state_dropdown.get()
    if selected_state:
        rainfall_data = result_text_rainfall.get("1.0", tk.END)
        soil_moisture_data = result_text_soil_moisture.get("1.0", tk.END)
        avail_gw_data = result_text_availgw.get("1.0", tk.END)
        soil_rep_data = result_text_soilrep.get("1.0", tk.END)
        soil_text_rep_data = result_text_soiltextrep.get("1.0", tk.END)
        second_program_data = result_text_second_program.get("1.0", tk.END)

        regression_stats = run_linear_regression()

        filename = f"{selected_state}_data.txt"
        with open(filename, "w") as file:

            file.write(rainfall_data + "\n\n")
            file.write(soil_moisture_data + "\n\n")
            file.write(avail_gw_data + "\n\n")
            file.write(soil_rep_data + "\n\n")
            file.write(soil_text_rep_data + "\n\n")
            file.write(second_program_data + "\n\n")
            file.write(regression_stats)
            file.write("\n")

        print(f"Data for {selected_state} has been downloaded as {filename}")
        tkinter.messagebox.showinfo("Download Complete", f"Your {selected_state} Data is Downloaded")
    else:
        print("Please select a state first.")

window = tk.Tk()
window.title("State Data Statistics")
window.geometry("1400x780")

bg_image_path = r"C:\My Files\projects\crop recommendation\updated crop\Untitled design.png"
bg_image = Image.open(bg_image_path)
bg_image = bg_image.resize((1400, 780), Image.ANTIALIAS)
bg_photo = ImageTk.PhotoImage(bg_image)

bg_label = tk.Label(window, image=bg_photo)
bg_label.grid(row=0, column=0, rowspan=100, columnspan=100, sticky="nsew")

window.grid_columnconfigure(0, weight=1)

def show_data():
    selected_state = state_dropdown.get()
    if selected_state:
        state_data = data[data['STATE'].str.upper() == selected_state.upper()]
        soil_moisture_data = soilmoisture[soilmoisture['State'].str.upper() == selected_state.upper()]

        availgw_data = availgw[availgw['State Name'].str.upper() == selected_state.upper()]
        availgw_data = availgw_data[['State Name','Annual Draft', 'Net Availability',
                                     'Future Irrigation Availability','Development(%)']]
        
        soilrep = pd.read_csv(r"C:\My Files\projects\crop recommendation\updated crop\soil report.csv", skiprows=4)
        data['State'] = soilrep['State']
        soilrep = soilrep[soilrep['State'].str.upper() == selected_state.upper()]
        
        soiltextrep = pd.read_csv(r"C:\My Files\projects\crop recommendation\updated crop\soil texture report.csv", skiprows=4)
        data['State'] = soiltextrep['State']
        soiltextrep = soiltextrep[soiltextrep['State'].str.upper() == selected_state.upper()]

        soil_moisture_data = soil_moisture_data.dropna(axis=1, how='all')
        availgw_data = availgw_data.dropna(axis=1, how='all')
        soilrep = soilrep.dropna(axis=1, how='all')
        soiltextrep = soiltextrep.dropna(axis=1, how='all')

        result_text_rainfall.config(state="normal")
        result_text_rainfall.delete(1.0, tk.END)
        result_text_rainfall.insert(tk.END, "Rainfall Data:\n")

        columns_to_print = ['STATE', 'Actual(mm)', 'Normal(mm)', 'Deviation(%) from normal']
        result_text_rainfall.insert(tk.END, state_data[columns_to_print].to_string(index=False))
        result_text_rainfall.config(state="disabled")

        result_text_soil_moisture.config(state="normal")
        result_text_soil_moisture.delete(1.0, tk.END)
        result_text_soil_moisture.insert(tk.END, "Soil Moisture Data:\n")
        result_text_soil_moisture.insert(tk.END, soil_moisture_data.to_string(index=False))
        result_text_soil_moisture.config(state="disabled")

        result_text_availgw.config(state="normal")
        result_text_availgw.delete(1.0, tk.END)
        result_text_availgw.insert(tk.END, "Available Ground Water Data:\n")
        result_text_availgw.insert(tk.END, availgw_data.to_string(index=False))
        result_text_availgw.config(state="disabled")

        result_text_soilrep.config(state="normal")
        result_text_soilrep.delete(1.0, tk.END)
        result_text_soilrep.insert(tk.END, "Soil Report:\n")
        result_text_soilrep.insert(tk.END, soilrep.to_string(index=False))
        result_text_soilrep.config(state="disabled")

        result_text_soiltextrep.config(state="normal")
        result_text_soiltextrep.delete(1.0, tk.END)
        result_text_soiltextrep.insert(tk.END, "Soil Texture Report:\n")
        result_text_soiltextrep.insert(tk.END, soiltextrep.to_string(index=False))
        result_text_soiltextrep.config(state="disabled")

        result_text_second_program.config(state="normal")
        result_text_second_program.delete(1.0, tk.END)
        result_text_second_program.insert(tk.END, "Result from Second Program:\n")
        
        state_data["Actual(mm)"] = pd.to_numeric(state_data["Actual(mm)"], errors="coerce")
        avg_rainfall_per_label = df.groupby('label')['rainfall'].mean()
        columns_to_print = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        
        result_text_second_program.insert(tk.END, "{:^12}|".format("Label"))
        for col in columns_to_print:
            result_text_second_program.insert(tk.END, "{:^21}|".format(col))
        result_text_second_program.insert(tk.END, "\n")
        
        for label, avg_rainfall in avg_rainfall_per_label.items():
            if avg_rainfall < state_data["Actual(mm)"].iloc[0]:
                
                filtered_df = df[df['label'] == label]
                
                min_values = filtered_df[columns_to_print].min()
                avg_values = filtered_df[columns_to_print].mean()
                max_values = filtered_df[columns_to_print].max()
                
                result_text_second_program.insert(tk.END, "{:<12}|".format(label))
                for col in columns_to_print:
                    result_text_second_program.insert(tk.END, "{:<7.2f}{:<7.2f}{:<7.2f}|".format(min_values[col], avg_values[col], max_values[col]))
                result_text_second_program.insert(tk.END, "\n")
                
        result_text_second_program.config(state="disabled")

    else:
        result_text_rainfall.config(state="normal")
        result_text_rainfall.delete(1.0, tk.END)
        result_text_rainfall.insert(tk.END, "Please select a state.")
        result_text_rainfall.config(state="disabled")

        result_text_soil_moisture.config(state="normal")
        result_text_soil_moisture.delete(1.0, tk.END)
        result_text_soil_moisture.insert(tk.END, "")
        result_text_soil_moisture.config(state="disabled")

        result_text_availgw.config(state="normal")
        result_text_availgw.delete(1.0, tk.END)
        result_text_availgw.insert(tk.END, "")
        result_text_availgw.config(state="disabled")

        result_text_soilrep.config(state="normal")
        result_text_soilrep.delete(1.0, tk.END)
        result_text_soilrep.insert(tk.END, "")
        result_text_soilrep.config(state="disabled")

        result_text_soiltextrep.config(state="normal")
        result_text_soiltextrep.delete(1.0, tk.END)
        result_text_soiltextrep.insert(tk.END, "")
        result_text_soiltextrep.config(state="disabled")

state_label = ttk.Label(window, text="Select a state:")
state_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')
state_dropdown = ttk.Combobox(window, values=data['STATE'].tolist(), state="readonly")
state_dropdown.grid(row=0, column=0, padx=20, pady=10)

show_button = ttk.Button(window, text="Show Data", command=show_data)
show_button.grid(row=1, column=0, columnspan=2, padx=10, pady=5,)

download_button = ttk.Button(window, text="Download Data", command=download_data)
download_button.grid(row=1, column=0, padx=10, pady=5, sticky='w')

label_rainfall = tk.Label(window, text="Monthly Rainfall Statistics Report for India from Jan-2014 to Mar-2024")
label_rainfall.grid(row=2, column=0, padx=10, pady=5,sticky="nsew")

result_text_rainfall = tk.Text(window, height=4, width=100)
result_text_rainfall.grid(row=3, column=0, padx=10, pady=5,sticky="nsew")
result_text_rainfall.config(state="disabled")

label_soil_moisture = tk.Label(window, text="Soil Moisture Data for 2020 to 2024")
label_soil_moisture.grid(row=4, column=0, padx=10, pady=5,sticky="nsew")

result_text_soil_moisture = tk.Text(window, height=4, width=100)
result_text_soil_moisture.grid(row=5, column=0, padx=10, pady=5,sticky="nsew")
result_text_soil_moisture.config(state="disabled")

label_avail_gw = tk.Label(window, text="Available Groundwater Data in billion cubic meters(BCM):")
label_avail_gw.grid(row=6, column=0, padx=10, pady=5,sticky="nsew")

result_text_availgw = tk.Text(window, height=4, width=100)
result_text_availgw.grid(row=7, column=0, padx=10, pady=5,sticky="nsew")
result_text_availgw.config(state="disabled")

label_soilrep = tk.Label(window, text="Soil Report:")
label_soilrep.grid(row=8, column=0, padx=10, pady=5,sticky="nsew")

result_text_soilrep = tk.Text(window, height=4, width=100)
result_text_soilrep.grid(row=9, column=0, padx=10, pady=5,sticky="nsew")
result_text_soilrep.config(state="disabled")

label_soiltextrep = tk.Label(window, text="Soil Texture Report:")
label_soiltextrep.grid(row=10, column=0, padx=10, pady=5,sticky="nsew")

result_text_soiltextrep = tk.Text(window, height=4, width=100)
result_text_soiltextrep.grid(row=11, column=0, padx=10, pady=5,sticky="nsew")
result_text_soiltextrep.config(state="disabled")

label_second_program = tk.Label(window, text="Predicted Crops for your State with the amount of properties required for your soil")
label_second_program.grid(row=12, column=0, padx=10, pady=5,sticky="nsew")

result_text_second_program = tk.Text(window, height=7, width=100)
result_text_second_program.grid(row=13, column=0, padx=10, pady=5,sticky="nsew")
result_text_second_program.config(state="disabled")

run_linear_regression()

window.mainloop()

