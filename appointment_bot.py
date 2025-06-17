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
            
        # First time setup - navigate through all steps
        try:
            self.driver.get("https://alohaq.honolulu.gov/")
            
            # Wait for and click Dealer Dash button
            dealer_dash = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.button-look.location-category-button[data-category_id='3']"))
            )
            dealer_dash.click()
            
            # Wait for and click Make Appointment button
            make_appointment = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "newAppointment"))
            )
            make_appointment.click()
            
            # Wait for and click location (Kapalama Dealer Center)
            location = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.location.button-look.next[data-loc-val='DMVR']"))
            )
            location.click()
            
            # Wait for and click Dealer Dash transaction - using multiple selectors
            try:
                transaction = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "transaction_2"))
                )
            except TimeoutException:
                try:
                    transaction = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.transaction.button-look[data-trans-type='DEALER']"))
                    )
                except TimeoutException:
                    transaction = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'transaction') and contains(text(), 'Dealer Dash')]"))
                    )
            transaction.click()
            
        except Exception as e:
            print(f"Error in initial setup: {e}")
            return False
            
        # Keep refreshing the calendar page until it appears
        while True:
            try:
                # Wait for calendar to appear
                calendar = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ui-datepicker-calendar"))
                )
                return True
            except TimeoutException:
                # Check if "no open appointments" message appears
                try:
                    no_appointments = self.driver.find_element(By.XPATH, "//*[contains(text(), 'There are no open appointments at this location')]")
                    if no_appointments.is_displayed():
                        time.sleep(2)
                        self.driver.refresh()
                        continue
                except NoSuchElementException:
                    pass
                
            time.sleep(2)
            self.driver.refresh()
                
    def select_earliest_date(self):
        try:
            # Wait a bit for the calendar to fully load
            time.sleep(1)
            
            # Find all available dates (those with clickable links)
            available_dates = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "td[data-handler='selectDay'] a"))
            )
            
            if available_dates:
                print(f"Found {len(available_dates)} available dates")
                # Click the first available date
                self.driver.execute_script("arguments[0].click();", available_dates[0])
                
                # Wait for the time slots to load
                time.sleep(2)
                return True
            else:
                print("No available dates found")
                return False
                
        except Exception as e:
            print(f"Error selecting date: {e}")
            return False
    
    def select_time_slot(self, slot_number=0):
        try:
            # Wait for time slots to appear
            time_slots = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.time"))
            )
            
            print(f"Found {len(time_slots)} time slots")
            
            if time_slots and 0 <= slot_number < len(time_slots):
                # Use JavaScript click to ensure it works
                self.driver.execute_script("arguments[0].click();", time_slots[slot_number])
                time.sleep(1)
                return True
            else:
                print(f"Invalid slot number {slot_number} or no time slots found")
                return False
                
        except Exception as e:
            print(f"Error selecting time slot: {e}")
            return False
    
    def fill_personal_info(self, first_name, last_name, phone_number):
        try:
            # Wait for the form to appear
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "fname"))
            )
            
            # Clear and fill in the form
            fname_field = self.driver.find_element(By.ID, "fname")
            fname_field.clear()
            fname_field.send_keys(first_name)
            
            lname_field = self.driver.find_element(By.ID, "lname")
            lname_field.clear()
            lname_field.send_keys(last_name)
            
            phone_field = self.driver.find_element(By.ID, "number")
            phone_field.clear()
            phone_field.send_keys(phone_number)
            
            # Wait a moment before clicking submit
            time.sleep(1)
            
            # Click sign up button
            signup_button = self.driver.find_element(By.CLASS_NAME, "submit")
            self.driver.execute_script("arguments[0].click();", signup_button)
            
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
        ttk.Label(self.root, text='Time Slot Number (default: 0 for first available):').pack()
        self.time_slot = ttk.Entry(self.root)
        self.time_slot.insert(0, "0")  # Default to first slot
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
                
            self.status_label.config(text='Status: Navigating to calendar...')
            self.root.update()
            
            if not self.bot.refresh_until_calendar():
                messagebox.showerror('Error', 'Could not find calendar after multiple attempts')
                return
                
            self.status_label.config(text='Status: Selecting earliest available date...')
            self.root.update()
            
            if not self.bot.select_earliest_date():
                messagebox.showerror('Error', 'Could not select date - no available dates found')
                return
                
            time_slot = int(self.time_slot.get() or 0)
            self.status_label.config(text=f'Status: Selecting time slot {time_slot}...')
            self.root.update()
            
            if not self.bot.select_time_slot(time_slot):
                messagebox.showerror('Error', f'Could not select time slot {time_slot}')
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