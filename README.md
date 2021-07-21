Don't need to download any datasets (import as JSON using Socrata)

First, sign up for an API token to retrieve full datasets on: https://data.wa.gov/signup

Using this API token, modify the client variable in the main function in the following form:

client = Socrata("data.wa.gov", API TOKEN, username=USERNAME, password=PASSWORD)

Download Socrata library using !pip install Socrata

Download Altair library using !pip install Altair
