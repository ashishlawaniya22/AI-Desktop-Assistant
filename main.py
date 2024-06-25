import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ttkthemes import ThemedTk  
from tkinter import filedialog
import re
import gc
import os
import sys
import json
import random
import pyttsx3
import requests
import datetime

import urllib.parse
from io import StringIO
import speech_recognition as sr
import google.generativeai as genai


from keys import key,api_key_weather

key = key
api_key_weather = api_key_weather
chatStr = ""
temp = 1
type = "English"

def load_websites_from_file(filename):
    with open(filename, 'r') as file:
        websites = json.load(file)
    return websites

websites = load_websites_from_file('websites.json')


class LoginPage(ThemedTk):

    def __init__(self, *args, **kwargs):
        ThemedTk.__init__(self, *args, **kwargs)

        self.set_theme("arc")  # setting ttk theme
        self.geometry("660x440")  # Sets window size to 660w x 440h pixels
        self.resizable(0, 0)  # This prevents any resizing of the screen
        self.style = ttk.Style()
        self.style.configure("Main.TFrame", background="#011536")  # Light cyan background color
        self.style.configure("DarkBlue.TButton", background="#00008B", foreground="white")  # Dark blue background color with white text

        title_styles = {"font": ("Trebuchet MS Bold", 24), "foreground": "#00fc00"}  # Steel blue color

        text_styles = {"font": ("Verdana", 14), "foreground": "#00fc00"}  # Black text color

        main_frame = ttk.Frame(self, height=431, width=626, style="Main.TFrame")  # this is the background
        main_frame.pack(fill="both", expand=True)

        frame_login = tk.Frame(main_frame, relief="groove", borderwidth=2, highlightbackground="#4682B4", bg="#41ab41")  # Light green background color
        frame_login.place(relx=0.5, rely=0.5, anchor="center")

        label_title = ttk.Label(frame_login, **title_styles, text="Login to Assistant")
        label_title.grid(row=0, column=0, columnspan=2, pady=(20, 40))  # Adjusted padding

        label_user = ttk.Label(frame_login, **text_styles, text="Username:")
        label_user.grid(row=1, column=0, padx=(10, 5), pady=(10, 5), sticky="e")  # Adjusted padding and alignment

        entry_user = ttk.Entry(frame_login, width=30, cursor="xterm")
        entry_user.grid(row=1, column=1, padx=(0, 10), pady=(10, 5), sticky="w")  # Adjusted padding and alignment

        label_pw = ttk.Label(frame_login, **text_styles, text="Password:")
        label_pw.grid(row=2, column=0, padx=(10, 5), pady=(5, 10), sticky="e")  # Adjusted padding and alignment

        entry_pw = ttk.Entry(frame_login, width=30, cursor="xterm", show="*")
        entry_pw.grid(row=2, column=1, padx=(0, 10), pady=(5, 10), sticky="w")  # Adjusted padding and alignment

        button = ttk.Button(frame_login, text="Login", command=lambda: getlogin(), style="DarkBlue.TButton")
        button.grid(row=3, column=0, columnspan=2, pady=(10, 0),sticky="ew")  # Adjusted padding and alignment
        button_style = ttk.Style()
        button_style.configure("DarkBlue.TButton", background="#00FF00", foreground="darkBlue")  # Dark blue background color with white text
        button_style.map("DarkBlue.TButton",
                  background=[("active", "#00FF00"), ("pressed", "#FF0000")],  # Change background color on active and pressed states
                  foreground=[("active", "green"), ("pressed", "green")]
        )  # Change foreground (text) color on active and pressed states


        # Decorative elements
        decorative_frame = tk.Frame(main_frame, bg="#4682B4", height=50)
        decorative_frame.pack(fill="x", side="top")

        decorative_label = tk.Label(decorative_frame, text="Welcome to My App", **title_styles, bg="#4682B4")
        decorative_label.pack(pady=5)

        footer_label = tk.Label(main_frame, text="© 2024 Assisstant. All rights reserved :).", font=("Arial", 10), bg="#4682B4", fg="white")
        footer_label.pack(side="bottom", fill="x")

        def getlogin():
            username = entry_user.get()
            password = entry_pw.get()
            if username == "12345" and password == "12345":
                messagebox.showinfo("Login Successful", "Welcome Sir")
                self.deiconify()
                self.destroy() # Close the login window
                global temp
                temp = 0
            else:
                messagebox.showerror("Information", "The Username or Password you have entered are incorrect ")

import requests

def get_weather(city, api_key_weather):
    """
    Get current weather of a given city.
    
    Parameters:
        city (str): The name of the city.
        api_key (str): Your OpenWeatherMap API key.
        
    Returns:
        str: A string describing the current weather.
    """
    # OpenWeatherMap API endpoint for current weather data
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key_weather}&units=metric"
    
    # Make a GET request to the API
    response = requests.get(url)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Convert response to JSON format
        data = response.json()
        
        # Extract relevant information from JSON data
        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        humidity = data['main']['humidity']
        
        # Construct the weather report string
        weather_report = f"Current weather in {city}: {weather_description}. "
        weather_report += f"Temperature: {temperature}°C, Humidity: {humidity}%."
        
        return weather_report
    else:
        # If request was unsuccessful, print the error status code
        print(f"Error: {response.status_code}")
        return None

def chat(text):
    global chatStr
    chatStr += f"User: {text}\n  AI:"
    temp_response = AI(chatStr)
    chatStr += f"{temp_response}\n"
    print(f"AI: {temp_response}")
    #say(temp_response)
    return temp_response

def helper(promt):
    
    text_temp = f"Responce for :{promt} \n**************************** \n\n"
    temp_response = AI(text_temp)
    print(temp_response)
    text = text_temp+temp_response
    if not os.path.exists("AI_output"):
        os.mkdir("AI_output")
    with open(f"AI_output/promt- {''.join([str(random.randint(0, 9)) for _ in range(random.randint(10, 15))])}", "w") as f:
        f.write(text)
    
    #say(temp_response)
    return temp_response    

def AI(text_temp):

    genai.configure(api_key=key)

    # Set up the model
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 0,
        "max_output_tokens": 8192,
    }

    safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    ]

    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest", generation_config = generation_config , safety_settings = safety_settings)# type: ignore
    
    prompt_parts = [
        "input: ",
        "output: ",
    ]

    response = model.generate_content(text_temp)
    return (response.text)
    

def open_application(app_name):
    say(f"Opening the {app_name}")
    print(f"Opening the {app_name}")
    os.system("start " + app_name)
    return None

def get_url_by_name(name, websites):
    for website in websites:
        if website["name"].lower() == name.lower():
            return website["url"]
    return None

def remove_word(string, word):
    pattern = r'\b' + re.escape(word) + r'\b'
    cleaned_string = re.sub(pattern, '', string)
    return cleaned_string.strip()


def search(text):
    query = urllib.parse.quote_plus(text)
    search_url = f"https://www.google.com/search?q={query}"
    webbrowser.open(search_url)
    print(f"AI : Searching for '{text}' on Google...")
    return None


def textcommand(type):

    if type == "English":
        type = "en-in"
    elif type == "Hindi":
        type = "hi-in"
    else:
        type = "en-us"
    
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        #recognizer.pause_threshold = 0.6
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        print("Recognizing...")

        try:
            text = recognizer.recognize_google(audio, language=type)
            print(f"User said: {text}")
            say(f"User said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand what you said.")
            return None
        except sr.RequestError:
            print("Sorry, couldn't request results from Google Speech Recognition service.")
            return None

def say(text):
    engine = pyttsx3.init()
    engine.say(f"{text}")
    engine.runAndWait()
    return None

def browse_files(file_type):
    if "music" in file_type.lower():
        file_type = "Music"
        extensions = [("Music Files", "*.mp3;*.wav;*.flac;*.ogg;*.aac"), ("All Files", "*.*")]
    elif "video" in file_type.lower():
        file_type = "Video"
        extensions = [("Video Files", "*.mp4;*.avi;*.mkv;*.mov;*.wmv"), ("All Files", "*.*")]
    else:
        extensions = [("All Files", "*.*")]

    filename = filedialog.askopenfilename(initialdir="/", title="Select a File", filetypes=extensions)
    return filename

def process_query(query):
    global websites
    # query = "help what is os"  # commented out as it will be retrieved from the entry box

    if query:

        if "what is the time" in query:
            strfTime = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"Sir, the current time is {strfTime}")
            say(f"Sir, the current time is {strfTime}")

        elif "search" in query.lower():
            query_temp = remove_word(query, "search")
            search(query_temp)
            #continue

        elif "open app" in query.lower():
            query_temp = remove_word(query, "open app")
            open_application(f"{query_temp}.exe")
            #continue
            
        elif "open file" in query.lower():
            path = browse_files("file")
            os.startfile(path)
            #continue

        elif "play video" in query.lower():
            path = browse_files("video") 
            os.startfile(path)
            #continue
        
        elif "play music" in query.lower():
            path = browse_files("music") 
            os.startfile(path)
            #continue

        elif "help" in query.lower():
            print("AI: Helping you sir...")
            say(f"Helping you sir with {query}")
            helper(query)
            #continue

        elif "tell" in query.lower():
            print("AI: Helping you sir...")
            say(f"Ok sir, I {query}")
            helper(query)
            #continue

        elif "open" in query.lower():
            query_temp = remove_word(query, "open")
            sites = get_url_by_name(query_temp, websites)

            if sites:
                print("AI: URL:", sites)
                say(f"Opening {sites} sir...")
                webbrowser.open(sites)
                #continue

            else:
                print("AI: Website not found.")
                #continue

        elif "shut down" in query.lower():  
            print("AI: Shutting down...")
            say("shutting down")
            os.system("shutdown /s /t 1")

        elif "quit" in query.lower():
            print("AI: Quitting...")
            say("quitting")
            exit(1)

        else:
            print("AI: Activating chat mode")
            print(f"User: {query}")
            say("chat mode activating")
            chat(query)

class App(ttk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.output_buffer = StringIO()
        self.switch_state_1 = tk.BooleanVar(value=False)
        self.switch_state_2 = tk.BooleanVar(value=False)
        self.setup_widgets()

    def on_button_click(self):
        # Retrieve the value from the entry box
        query = self.entry.get()

        # Redirect stdout to the StringIO object
        sys.stdout = self.output_buffer
        # Assuming process_query is defined elsewhere
        process_query(query)
        # Assign the captured output to temp_text
        temp_text = self.output_buffer.getvalue()
        # Reset stdout
        sys.stdout = sys.__stdout__

        # Update the label with the captured output
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, temp_text)
        self.text.config(state=tk.DISABLED)

    def on_button2_click(self):
        global type
        # Retrieve the value from the entry box
        query = textcommand(type)

        # Redirect stdout to the StringIO object
        sys.stdout = self.output_buffer
        # Assuming process_query is defined elsewhere
        process_query(query)
        
        # Assign the captured output to temp_text
        temp_text = self.output_buffer.getvalue()
        # Reset stdout
        sys.stdout = sys.__stdout__

        # Update the label with the captured output
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, temp_text)
        self.text.config(state=tk.DISABLED)
    
    def on_button3_click(self):
        global api_key_weather
        # Retrieve the value from the entry box
        city_name = self.entry_2.get()

        # Redirect stdout to the StringIO object
        sys.stdout = self.output_buffer
        # Assuming process_query is defined elsewhere
        weather_info = get_weather(city_name, api_key_weather)
        if weather_info:
            print(weather_info)
        
        say(weather_info)
        # Assign the captured output to temp_text
        temp_text = self.output_buffer.getvalue()
        # Reset stdout
        sys.stdout = sys.__stdout__

        # Update the label with the captured output
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, temp_text)
        self.text.config(state=tk.DISABLED)

    def on_switch_change(self):
        # Get current switch state
        switch_state = self.switch_state_1.get()

        if switch_state:  # If switch is ON
            print("Switch is ON")
            # Set theme to dark
            root.tk.call("set_theme", "light")
        else:  # If switch is OFF
            print("Switch is OFF")
            # Set theme to light
            root.tk.call("set_theme", "dark")

    def on_switch2_change(self):
        global type
        # Get current switch state
        switch_state = self.switch_state_2.get()

        if switch_state:  # If switch is ON
            print("Switch is ON")
            # Set theme to dark
            type = "Hindi"
        else:  # If switch is OFF
            print("Switch is OFF")
            # Set theme to light
            type = "English"

    def setup_widgets(self):

        # Create a Frame for input widgets with a border
        self.widgets_frame = ttk.Frame(self, padding=(20, 20, 20, 0), borderwidth=2, relief="solid")
        self.widgets_frame.grid(
            row=0, column=0, padx=10, pady=(30, 10), sticky="nsew"
        )
        self.widgets_frame.columnconfigure(index=0, weight=1)

        # Entry 1
        self.entry = ttk.Entry(self.widgets_frame)
        self.entry.insert(0, "Entry")
        self.entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Button 1
        self.button1 = ttk.Button(self.widgets_frame, text="Enter", command=self.on_button_click)
        self.button1.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # Button 2
        self.button2 = ttk.Button(self.widgets_frame, text="Voice", command=self.on_button2_click)
        self.button2.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        # Switch 2
        self.switch_2 = ttk.Checkbutton(
            self.widgets_frame, text="Language", style="Switch.TCheckbutton", variable=self.switch_state_2, command=self.on_switch2_change
        )
        self.switch_2.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

        # Switch 1
        self.switch_1 = ttk.Checkbutton(
            self.widgets_frame, text="Theme", style="Switch.TCheckbutton", variable=self.switch_state_1, command=self.on_switch_change
        )
        self.switch_1.grid(row=4, column=0, padx=5, pady=5, sticky="ew")

        # Entry 2
        self.entry_2 = ttk.Entry(self.widgets_frame)
        self.entry_2.insert(0, "City")
        self.entry_2.grid(row=5, column=0, padx=5, pady=5, sticky="ew")

        # Button 3
        self.button1 = ttk.Button(self.widgets_frame, text="Weather", command=self.on_button3_click)
        self.button1.grid(row=6, column=0, padx=5, pady=5, sticky="ew")

        # Notebook, pane #2
        self.pane_2 = ttk.Frame(self)
        self.pane_2.grid(row=0, column=1, pady=(25, 5), sticky="nsew", rowspan=3)

        # Notebook, pane #2
        self.notebook = ttk.Notebook(self.pane_2, width=500, height=300)
        self.notebook.pack(fill="both", expand=True)
        
        # Output section with border
        self.output_frame = ttk.Frame(self.notebook, borderwidth=2, relief="solid", width=450, height=250)
        self.output_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.notebook.add(self.output_frame, text="Output")

        # Add Scrollbars
        scrollbar_y = ttk.Scrollbar(self.output_frame, orient=tk.VERTICAL)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x = ttk.Scrollbar(self.output_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Label
        self.text = tk.Text(self.output_frame, wrap=tk.NONE, yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        self.text.pack(expand=True, fill=tk.BOTH)
        scrollbar_y.config(command=self.text.yview)
        scrollbar_x.config(command=self.text.xview)

        # Configure rows and columns to expand
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1) 
        
if __name__ == "__main__":
    
    print("---starting----")
    root = LoginPage()
    root.title("AI Desktop assisstant - Login Page")
    root.mainloop()
    if temp == 1:
        exit()
    gc.collect()

    root = tk.Tk()
    root.title("Assistant")

    root.tk.call("source", "azure.tcl")
    root.tk.call("set_theme", "dark")

    app = App(root)
    app.pack(fill="both", expand=True)

    # Set a minsize for the window, and place it in the middle
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    x_cordinate = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
    y_cordinate = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
    root.geometry("+{}+{}".format(x_cordinate, y_cordinate-20))

    root.mainloop()