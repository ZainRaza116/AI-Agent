import sys
import time
import tkinter as tk
from tkinter import ttk, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

class AppointmentBot:
    def __init__(self):
        self.driver = None
        
    def setup_driver(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Try to use the installed Chrome driver first
            try:
                service = Service()
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except WebDriverException:
                # If that fails, try to download and use the latest compatible driver
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                
            return True
        except Exception as e:
            messagebox.showerror('Error', f'Failed to initialize Chrome WebDriver: {str(e)}\n\nPlease make sure Chrome is installed and up to date.')
            return False
        
    def refresh_until_calendar(self):
        if not self.driver:
            return False
            
        max_attempts = 10
        attempts = 0
        
        while attempts < max_attempts:
            try:
                self.driver.get("https://alohaq.honolulu.gov/?3&cat=3&name=Dealer%20Dash")
                # Wait for calendar to appear
                calendar = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ui-datepicker-calendar"))
                )
                return True
            except TimeoutException:
                attempts += 1
                time.sleep(2)
                self.driver.refresh()
                
        return False
    
    def select_earliest_date(self):
        try:
            # Find all available dates (those with links)
            available_dates = self.driver.find_elements(By.CSS_SELECTOR, "td[data-handler='selectDay'] a")
            if available_dates:
                available_dates[0].click()
                return True
        except Exception as e:
            print(f"Error selecting date: {e}")
        return False
    
    def select_time_slot(self, slot_number):
        try:
            time_slots = self.driver.find_elements(By.CLASS_NAME, "time")
            if 0 <= slot_number < len(time_slots):
                time_slots[slot_number].click()
                return True
        except Exception as e:
            print(f"Error selecting time slot: {e}")
        return False
    
    def fill_personal_info(self, first_name, last_name, phone_number):
        try:
            # Fill in the form
            self.driver.find_element(By.ID, "fname").send_keys(first_name)
            self.driver.find_element(By.ID, "lname").send_keys(last_name)
            self.driver.find_element(By.ID, "number").send_keys(phone_number)
            
            # Click sign up button
            signup_button = self.driver.find_element(By.CLASS_NAME, "submit")
            signup_button.click()
            return True
        except Exception as e:
            print(f"Error filling personal info: {e}")
        return False
    
    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

class AppointmentGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('AlohaQ Appointment Bot')
        self.root.geometry('400x300')
        self.bot = AppointmentBot()
        self.init_ui()
        
    def init_ui(self):
        # Status label
        self.status_label = ttk.Label(self.root, text='Status: Ready')
        self.status_label.pack(pady=10)
        
        # First Name
        ttk.Label(self.root, text='First Name:').pack()
        self.first_name = ttk.Entry(self.root)
        self.first_name.pack(pady=5)
        
        # Last Name
        ttk.Label(self.root, text='Last Name:').pack()
        self.last_name = ttk.Entry(self.root)
        self.last_name.pack(pady=5)
        
        # Phone Number
        ttk.Label(self.root, text='Phone Number:').pack()
        self.phone = ttk.Entry(self.root)
        self.phone.pack(pady=5)
        
        # Time Slot
        ttk.Label(self.root, text='Time Slot Number (0-23):').pack()
        self.time_slot = ttk.Entry(self.root)
        self.time_slot.pack(pady=5)
        
        # Start Button
        start_button = ttk.Button(self.root, text='Start Booking', command=self.start_booking)
        start_button.pack(pady=20)
        
    def start_booking(self):
        try:
            self.status_label.config(text='Status: Initializing Chrome...')
            self.root.update()
            
            if not self.bot.setup_driver():
                return
                
            self.status_label.config(text='Status: Searching for calendar...')
            self.root.update()
            
            if not self.bot.refresh_until_calendar():
                messagebox.showerror('Error', 'Could not find calendar after multiple attempts')
                return
                
            self.status_label.config(text='Status: Selecting earliest date...')
            self.root.update()
            
            if not self.bot.select_earliest_date():
                messagebox.showerror('Error', 'Could not select date')
                return
                
            time_slot = int(self.time_slot.get())
            self.status_label.config(text='Status: Selecting time slot...')
            self.root.update()
            
            if not self.bot.select_time_slot(time_slot):
                messagebox.showerror('Error', 'Could not select time slot')
                return
                
            self.status_label.config(text='Status: Filling personal information...')
            self.root.update()
            
            if not self.bot.fill_personal_info(
                self.first_name.get(),
                self.last_name.get(),
                self.phone.get()
            ):
                messagebox.showerror('Error', 'Could not fill personal information')
                return
                
            self.status_label.config(text='Status: Booking completed!')
            messagebox.showinfo('Success', 'Appointment booked successfully!')
            
        except Exception as e:
            messagebox.showerror('Error', f'An error occurred: {str(e)}')
        finally:
            self.bot.close()
    
    def run(self):
        self.root.mainloop()

def main():
    app = AppointmentGUI()
    app.run()

if __name__ == '__main__':
    main() 