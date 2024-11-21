# Standard library imports
import smtplib
from datetime import datetime
import time

# Third-party imports
import pandas as pd
import requests
import schedule

# Email handling
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import email.encoders

def send_mail(subject, body, filename):
    
    # smtp_server = "smpt.google.com"
    smtp_server = "mail.zeroanalyst.com"
    smtp_port = 587
    sender_mail = "dev@zeroanalyst.com"
    email_password = "admin@1234!"
    receiver_mail = "your email"
    
  # compose the mail
    message = MIMEMultipart()
    message['From'] = sender_mail
    message['To'] = receiver_mail
    message ['Subject'] = subject
    
    # attaching body
    message.attach(MIMEText(body, 'plain'))
    
    
    # attach csv file
    with open(filename, 'rb') as file:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(file.read())
        email.encoders.encode_base64(part)  # This line encodes the file in base64 (optional)
        part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
        message.attach(part)
        
        
     # start sever
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls() #secure connection
            server.login(sender_mail, email_password) #login
            
            # sending mail
            server.sendmail(sender_mail, receiver_mail, message.as_string())
            print("Email sent successfull!")
        
    except Exception as e:
        print(f'Unable to send mail {e}')


def get_crypto_data():
    # API information
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 250,
        'page': 1
    }

    try:
        # Sending the request
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        print('Connection Successful! \nGetting the data...')
        
        # Storing the response into data
        data = response.json()
        
        # Creating the dataframe
        df = pd.DataFrame(data)
        
        # Check if all required columns exist
        required_columns = [
            'id', 'current_price', 'market_cap', 
            'price_change_percentage_24h', 'high_24h', 'low_24h', 'ath', 'atl'
        ]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Warning: Missing columns {missing_columns} in the API response.")
        
        # Ensure only the required columns are selected, adding NaN if missing
        df = df.reindex(columns=required_columns)
        
        # Creating a new column for the timestamp
        today = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
        df['time_stamp'] = today
        
        # Get the top 10 cryptocurrencies with the most negative price change
        top_negative_10 = df.nsmallest(10, 'price_change_percentage_24h')
        
        # Get the top 10 cryptocurrencies with the most positive price change
        top_positive_10 = df.nlargest(10, 'price_change_percentage_24h')
        
        # Save the full dataset to a CSV file
        file_name = f'crypto_data_{today}.csv'
        df.to_csv(file_name, index=False)
        
        # Print results
        print(f'Data saved successfully as {file_name}')


 # call email function to send the reports
        
        subject = f"Top 10 crypto currency data to invest for {today}"
        body = f"""
        Good Morning!\n\n
        
        Your crypt reports is here!\n\n
        
        Top 10 crypto with highest price increase in last 24 hour!\n
        {top_positive_10}\n\n\n
        
        
        Top 10 crypto with highest price decrease in last 24 hour!\n
        {top_negative_10}\n\n\n
        
        Attached 250 plus crypto currency lattest reports\n
        
        
        Regards!\n
        See you tomorrow!\n
        Your crypto python application    
        """
        
        # sending mail
        send_mail(subject, body, file_name)  
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the data: {e}")

# This gets executed only if we run this file directly
if __name__ == '__main__':
    # Call the function
    get_crypto_data()

     # call the function

    # sheduling the task at 8AM
    schedule.every().day.at('08:00').do(get_crypto_data)
    
    while True:
        schedule.run_pending()
        time.sleep(60)
    