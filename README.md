# Tietokannat-ja-web-ohjelmointi-projekti

## money tracking web app
- basic budgeting functions for multiple users
- keeping track of expenses with categories
- summary of spending on first page

### main functions for user
- making account
- deleting account
- adding expenses
- adding fixed expenses
- categorizing expenses
- printing data from:
	- timeframe
	- category
	- or all
- setting limits and warnings

### functions for admin
- removing users
- printing data
	-averages
	-summaries


### Setup Instructions

1. **Clone Repository:**
  ```
git clone https://github.com/OGesko/Tietokannat-ja-web-ohjelmointi-projekti
cd Tietokannat-ja-web-ohjelmointi-projekti
  ```

2. **Create Virtual Environment:**
  ```
python -m venv venv
  ```

3. **Activate Virtual Environment:**
  ```
source venv/bin/activate
  ```

4. **Install Dependencies:**
  ```
pip install -r requirements.txt
  ```

5. **Create Database:**
- Ensure you have PostgreSQL installed and running.
- Create a new database in PostgreSQL.

6. **Create `.env` File:**
- Create a `.env` file in the root directory of the project.
- Add the following configuration (adjust values accordingly):
  ```
  DATABASE_URL=postgresql://username:password@localhost/dbname
  SECRET_KEY=your_secret_key_here
  ```

7. **Run Migration Script:**
  ```
python3 migrate.py
  ```

8. **Run The App:**
  ```
flask run
  ```
