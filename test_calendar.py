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

class CalendarTestBot:
    def __init__(self):
        self.driver = None
        
    def setup_driver(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            try:
                service = Service()
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except WebDriverException:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                
            return True
        except Exception as e:
            messagebox.showerror('Error', f'Failed to initialize Chrome WebDriver: {str(e)}')
            return False
        
    def check_calendar(self):
        if not self.driver:
            return False
            
        try:
            # Navigate directly to the Driver Licensing page
            self.driver.get("https://alohaq.honolulu.gov/?3&cat=1&name=Driver%20Licensing%20and%20Satellite%20Services")
            
            # Wait for and click Make Appointment button
            make_appointment = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "newAppointment"))
            )
            make_appointment.click()
            
            # Wait for and click location (Kapalama Driver Licensing Center)
            location = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.location.button-look.next[data-loc-val='DMVR']"))
            )
            location.click()
            
            # Wait for and click Driver License transaction
            transaction = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "transaction_1"))
            )
            transaction.click()
            
            # Wait for 15 seconds before checking for calendar
            time.sleep(15)
            
            # Check for calendar
            try:
                calendar = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ui-datepicker-calendar"))
                )
                return True, "Calendar found!"
            except TimeoutException:
                # Check for no appointments message
                try:
                    no_appointments = self.driver.find_element(By.XPATH, "//*[contains(text(), 'There are no open appointments at this location')]")
                    if no_appointments.is_displayed():
                        return False, "No appointments available"
                except NoSuchElementException:
                    return False, "Calendar not found"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

class CalendarTestGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Calendar Test Bot')
        self.root.geometry('400x200')
        self.bot = CalendarTestBot()
        self.init_ui()
        
    def init_ui(self):
        # Status label
        self.status_label = ttk.Label(self.root, text='Status: Ready')
        self.status_label.pack(pady=10)
        
        # Test Button
        test_button = ttk.Button(self.root, text='Test Calendar', command=self.test_calendar)
        test_button.pack(pady=20)
        
    def test_calendar(self):
        try:
            self.status_label.config(text='Status: Initializing Chrome...')
            self.root.update()
            
            if not self.bot.setup_driver():
                return
                
            self.status_label.config(text='Status: Checking calendar...')
            self.root.update()
            
            success, message = self.bot.check_calendar()
            self.status_label.config(text=f'Status: {message}')
            
            if success:
                messagebox.showinfo('Success', 'Calendar was found!')
            else:
                messagebox.showwarning('Warning', message)
            
        except Exception as e:
            messagebox.showerror('Error', f'An error occurred: {str(e)}')
        finally:
            self.bot.close()
    
    def run(self):
        self.root.mainloop()

def main():
    app = CalendarTestGUI()
    app.run()

if __name__ == '__main__':
    main() 