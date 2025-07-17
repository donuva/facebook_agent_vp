# Getting started

### Prerequisites

Before you can run this app, make sure you have the following prerequisites installed:

- Python 3.8 or higher
- Pip (Python package manager)
- [Streamlit](https://streamlit.io/) (if not already installed, you can install it using `pip install streamlit`)
- Other required Python packages (see the [Installation](#installation) section)

### Clone the Repository

To get started, clone this repository to your local machine using the following command:

```cmd
git clone https://github.com/group4-LLM-fin/llm_fin.git
cd chabot_demo
```
### Installation
Create and activate a virtual environment (optional but recommended)
```cmd
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```
Install dependencies
```cmd
pip install -r requirements.txt
```
### Config environment
- Create .env file
- Copy content in .env.example
- Fill your environment config

### Start the app
```cmd
streamlit run Home.py --server.port 6789
```


-------------------------------------------------------
### CÁCH CHẠY WEBHOOK

'''
python server.py
ngrok http 80
'''
### call back url của webhook: link_ngrok/webhook

### chạy code crawl_data
# pip install playwright
# playwright install