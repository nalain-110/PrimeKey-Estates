# PrimeKeyEstates 📈🏡

**A full-stack Flask web application** that demonstrates a real-estate marketplace with **admin, agent, and client** portals. The project is a clean, well-documented example of a role-based web application built with Flask.

---

## Table of Contents
- [PrimeKeyEstates 📈🏡](#primekeyestates-)
  - [Table of Contents](#table-of-contents)
  - [Project Overview](#project-overview)
  - [Key Features](#key-features)
  - [Technology Stack](#technology-stack)
  - [Installation \& Setup](#installation--setup)
  - [Running the Application](#running-the-application)
  - [Default Accounts (Seeded)](#default-accounts-seeded)
  - [Database](#database)
  - [Testing](#testing)
  - [Project Structure](#project-structure)
  - [Screenshots](#screenshots)
  - [Contribution Guide](#contribution-guide)
  - [License](#license)
  - [Acknowledgements](#acknowledgements)

---

## Project Overview
PrimeKeyEstates is a **multi-page** real-estate portal built with **Flask**. It showcases:
- Secure user authentication (login / register).
- Role-based access: **admin**, **agent**, and **client**.
- CRUD operations for **properties**, **agents**, **offers**, **blog posts**, and more.
- A lightweight **SQLite** database (`primekey.db`) pre-seeded with realistic sample data.
- Clean Jinja2 templates with a **Bootstrap-based** UI theme.

The code is deliberately modular: blueprints separate concerns, forms are defined with **Flask-WTF**, and models use **SQLAlchemy**.

---

## Key Features
- **Admin Dashboard** – Manage users, properties, payments, and reports.
- **Agent Workspace** – Add / edit listings, view inquiries, and track commissions.
- **Client Portal** – Browse listings, save favorites, and send inquiries.
- **Blog Module** – Read property-related articles.
- **Responsive Design** – Mobile-first layout with clean CSS.
- **Unit-Test Suite** – Automated route checks (`test_routes.py`).
- **Extensible Architecture** – Easy to add new blueprints or models.

---

## Technology Stack
| Layer | Technology |
|---|---|
| **Backend** | Flask 3.x, Flask-SQLAlchemy, Flask-Login, Flask-WTF |
| **Database** | SQLite (`primekey.db`) |
| **Frontend** | HTML5, CSS3, vanilla JavaScript, Bootstrap 5 |
| **Testing** | `unittest` (simple route health checks) |
| **Package Management** | `pip` + `requirements.txt` |
| **Environment** | Python 3.11 virtual environment (`venv`) |

---

## Installation & Setup
> **Note:** The repository ships **without** the `venv` folder to keep the ZIP lightweight. The commands below are for Windows (PowerShell).

1. **Extract** the archive:
   ```powershell
   Expand-Archive -Path PrimeKeyEstates_Final.zip -DestinationPath C:\PrimeKeyEstates
   cd C:\PrimeKeyEstates
   ```
2. **Create and activate a virtual environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1   # PowerShell
   # or: .\venv\Scripts\activate.bat   (cmd)
   ```
   > If PowerShell blocks the script, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` first.
3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```
4. *(Optional)* **Verify the installation**:
   ```powershell
   pip list
   ```

---

## Running the Application
```powershell
python run.py
```
The development server starts at `http://127.0.0.1:5000/`. Open this URL in your browser.

### Default Accounts (Seeded)
| Role | Email | Password |
|---|---|---|
| **Admin** | `admin@primekey.com` | `admin123` |
| **Agent** | `agent1@primekey.com` | `agent123` |
| **Client** | `client1@primekey.com` | `client123` |

> These are demo credentials for local development only. Change them before any real deployment.

You can also register additional users via the **Register** page.

---

## Database
- The SQLite file `primekey.db` is included and already populated with sample data.
- To **reset** the database:
  ```powershell
  python seed_db.py --reset
  ```
- ORM models are located in `app/models.py`.

---

## Testing
A minimal test suite verifies that all public routes return a **200** or **302** status code.
```powershell
python -m unittest test_routes
```
The test file is located in the project root (`test_routes.py`). Extend it for more comprehensive coverage.

---

## Project Structure
```
PrimeKeyEstates/
├── app/                  # Flask application package
│   ├── blueprints/       # admin, agent, auth, client, public
│   ├── forms/            # WTForms definitions
│   ├── static/           # CSS, JS, images
│   ├── templates/        # Jinja2 HTML templates
│   ├── __init__.py
│   └── models.py
├── docs/
│   └── screenshots/      # README screenshots
├── venv/                 # excluded – create locally
├── config.py             # configuration settings
├── run.py                # application entry point
├── seed_db.py            # database seeding script
├── test_routes.py        # basic route tests
├── requirements.txt      # Python dependencies
├── LICENSE               # MIT License text
└── primekey.db           # pre-populated SQLite database
```

---

## Screenshots
> Replace the placeholders in `docs/screenshots/` with actual screenshots after running the app.

**Home Page**

![Home Page](docs/screenshots/home.png)

**Admin Dashboard**

![Admin Dashboard](docs/screenshots/admin.png)

**Agent Listings**

![Agent Listings](docs/screenshots/agent.png)

**Client Favorites**

![Client Favorites](docs/screenshots/favorites.png)

---

## Contribution Guide
1. **Fork** the repository.
2. Create a **feature branch** (`git checkout -b feature/XYZ`).
3. Install the dependencies (same as for running the app).
4. Add or modify code and **run the tests**.
5. Submit a **Pull Request** with a clear description.

All contributions should follow the existing coding style (PEP 8, Jinja2 conventions) and include unit tests where appropriate.

---

## License
This project is released under the **MIT License** – see the `LICENSE` file for details.

---

## Acknowledgements
- **Flask** – the micro-framework that makes rapid development possible.
- **Bootstrap** – for the responsive UI components.
- **Open-source community** – for the libraries used throughout the project.

---


