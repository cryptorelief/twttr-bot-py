# twttr_bot_python
Twitter Bot implemented with Python

# Installation

clone the repo <br>
cd repo <br>
create a virtual env <br>
pip install -r requirements.txt <br>

- For Streaming <br>
   cd src <br>
   create a file "config.py" with the contents of "config.py.example" and the corresponding values<br>
   python bot.py <br>
   ctrl + c to kill the streaming <br>

- For Scraping <br>
  cd scraper <br>
  create a file "extracted_data.json" with the contents of "extracted_data.json.example"<br>
  set your criteria in scraper.py [queries, number of tweets]
  python scraper.py <br>
  ctrl + c to kill the streaming <br>
