# AlohaQ Appointment Bot

This is an automated appointment booking system for the AlohaQ website. It helps you book appointments by automatically finding available dates and time slots.

## Requirements

- Python 3.8 or higher
- Chrome browser installed
- Internet connection

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python appointment_bot.py
```

2. Fill in the form with your information:
   - First Name
   - Last Name
   - Phone Number
   - Time Slot Number (0-23, where 0 is the first available time slot)

3. Click "Start Booking" to begin the automated process.

The bot will:
1. Search for available dates
2. Select the earliest available date
3. Select your chosen time slot
4. Fill in your personal information
5. Complete the booking

## Notes

- The bot will automatically refresh the page until it finds an available calendar
- Make sure to enter a valid time slot number (0-23)
- The application will show status updates during the booking process
- If any errors occur, they will be displayed in a popup message
