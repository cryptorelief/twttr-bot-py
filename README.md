# twttr_bot_python
Twitter Bot implemented with Python

# Installation

clone the repo <br>
cd repo <br>
create and activate virtual env <br>
pip install -r requirements.txt <br>

- For Streaming <br>
  cd src <br>
  create a file "config.py" with the contents of "config.py.example" and the corresponding values<br>
  python -m src.bot <br>
  ctrl + c to kill the streaming <br>

- For Scraping <br>
  cd scraper <br>
  create a file "extracted_data.json" and "hashed_data.json" with the contents of "extracted_data.json.example"<br>
  set your criteria in scraper.py [queries] <br>
  python -m scraper.scraper [number of tweets] <br>
