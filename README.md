# 🚀 amoCRM → PostgreSQL ETL with Apache Airflow

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![Airflow](https://img.shields.io/badge/Apache%20Airflow-3.x-017CEE?logo=apacheairflow&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-ETL-150458?logo=pandas&logoColor=white)

An automated ETL pipeline that extracts data from the **amoCRM REST API** (leads, contacts, companies, users, tasks), transforms it with **pandas**, and loads it into a **PostgreSQL** database. The whole process is orchestrated by **Apache Airflow** running in **Docker**, and the resulting tables are ready for analytics in **Power BI**.

---

## 📌 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Project structure](#-project-structure)
- [Requirements](#-requirements)
- [Quick start](#-quick-start)
- [Configuration (DB_URL)](#-configuration-db_url)
- [Running the pipeline](#-running-the-pipeline)
- [How it works](#-how-it-works)
- [Troubleshooting](#-troubleshooting)
- [Security notes](#-security-notes)
- [Contact](#-contact)

---

## ✨ Features

- 🔌 Pulls data from amoCRM via the API v4 with a **long-lived token**
- 📄 Handles **pagination** automatically (250 records per page)
- 🧹 Flattens nested JSON (custom fields, embedded objects) with pandas
- 🗄️ Loads data into **PostgreSQL** with SQLAlchemy
- ⏰ Runs on a **schedule** (daily) or manually from the Airflow UI
- 🐳 One command setup with **Docker Compose** (CeleryExecutor, Redis, PostgreSQL)

---

## 🏗 Architecture

```mermaid
flowchart LR
    A[amoCRM API v4] -->|HTTPS + Bearer token| B[Python scripts<br/>pandas]
    B -->|SQLAlchemy| C[(PostgreSQL)]
    C --> D[Power BI / SQL analytics]
    E[Apache Airflow<br/>amoCRM_ETL DAG] -. orchestrates .-> B
```

**DAG task order:**

```mermaid
flowchart LR
    run_users --> run_tasks
    run_companies --> run_tasks
    run_contacts --> run_tasks
    run_Leads --> run_tasks
```

Users, companies, contacts and leads are loaded first; tasks are loaded last because they reference the other entities (`entity_id`, `responsible_user_id`).

---

## 📁 Project structure

```
AMOCRM_ETL-/
├── dags/
│   └── pipelines/
│       ├── amocrm_dag.py      # Airflow DAG (BashOperator per entity)
│       ├── amo.py             # get_table(): API client with pagination
│       ├── load.py            # loader(): writes DataFrame to PostgreSQL
│       ├── config.py          # DB_URL (your database connection)
│       ├── users.py
│       ├── companies.py
│       ├── contacts.py
│       ├── amo_leads.py
│       ├── tasks.py
│       └── create_fake.py     # optional: creates test data in amoCRM
├── config/                    # Airflow config folder
├── plugins/
├── docker-compose.yaml        # Airflow stack (apiserver, scheduler, worker, ...)
├── requirements.txt
├── .env.example               # template for your secrets
└── README.md
```

> The cloned folder is named **`AMOCRM_ETL-`** (with a trailing dash), exactly like the repository.

---

## 🧰 Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (at least **4 GB RAM** allocated to Docker)
- [Git](https://git-scm.com/)
- A **PostgreSQL** database where the data will be stored
- An **amoCRM** account with a private integration and a long-lived token

---

## ⚡ Quick start

### 1. Clone the repository

```bash
git clone https://github.com/saidakbarorunboyev3-ai/AMOCRM_ETL-.git
cd AMOCRM_ETL-
dir        # Windows PowerShell (Linux/macOS: ls)
```

You should see `docker-compose.yaml` in the list.

> ⚠️ **Every `docker compose` command must be run from this folder**, the one that contains `docker-compose.yaml`. Docker looks for the file only in the **current** folder. If you see `no configuration file provided: not found`, you are in the wrong folder.

> 💡 Tip: copy the clone URL from the green **Code** button on GitHub instead of typing it by hand (a typo such as `.gi` instead of `.git` gives `Repository not found`).

### 2. Create the `.env` file

Copy the template and fill in your own values:

```bash
cp .env.example .env        # Windows PowerShell: Copy-Item .env.example .env
```

```env
AIRFLOW_UID=50000
AMO_SUBDOMAIN=your_subdomain
AMO_TOKEN=your_long_lived_token
FERNET_KEY=your_fernet_key
```

| Variable | Description |
|---|---|
| `AIRFLOW_UID` | User id for Airflow containers (`50000` on Windows) |
| `AMO_SUBDOMAIN` | Your amoCRM account name. For `https://mycompany.amocrm.ru` it is `mycompany` (without `.amocrm.ru`) |
| `AMO_TOKEN` | Long-lived token from your amoCRM integration |
| `FERNET_KEY` | Airflow encryption key (optional, see below) |

> ⚠️ Save `.env` in **UTF-8** encoding, one variable per line, **no spaces** around `=`, no quotes.

Generate a Fernet key (optional but recommended):

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 3. Get the amoCRM token

1. Log in to your amoCRM account.
2. Open the integrations section and create a **private (external) integration**.
3. Go to **Keys and access** and click **Create token** under *Long-lived token*.
4. Copy the token **immediately** (it is shown only once) and paste it into `.env`.

### 4. Configure the database

See the next section 👇

---

## 🗄 Configuration (DB_URL)

The pipeline writes data to **your own PostgreSQL database**, so you must enter your connection details. Open `dags/pipelines/config.py` and set `DB_URL`:

```python
DB_URL = "postgresql+psycopg2://USERNAME:PASSWORD@HOST:5432/DATABASE"
```

Replace the placeholders:

| Placeholder | What to enter | Example |
|---|---|---|
| `USERNAME` | Your PostgreSQL user name | `postgres` |
| `PASSWORD` | Password of that user | `my_secret_password` |
| `HOST` | Where PostgreSQL is running (see below) | `host.docker.internal` |
| `5432` | PostgreSQL port | `5432` |
| `DATABASE` | Name of the database to load data into | `amocrm_db` |

**Which HOST should I use?**

- PostgreSQL installed on **your computer** (Airflow runs in Docker): use `host.docker.internal`
- PostgreSQL in **another container** of the same compose network: use the **service name**
- PostgreSQL on a **remote server**: use its IP address or domain name

> ⚠️ Do **not** use `localhost` here. Inside a Docker container, `localhost` means the container itself, not your computer.

**Full example:**

```python
DB_URL = "postgresql+psycopg2://postgres:my_secret_password@host.docker.internal:5432/amocrm_db"
```

Create the database first if it does not exist yet:

```sql
CREATE DATABASE amocrm_db;
```

> 🔒 Never commit your real password to GitHub. Keep `config.py` out of version control (it is listed in `.gitignore`) or read the URL from an environment variable.

---

## ▶️ Running the pipeline

### 1. Start Airflow

Make sure you are inside the project folder (the one that contains `docker-compose.yaml`):

```bash
cd AMOCRM_ETL-
docker compose up -d
docker compose ps
```

The first start takes a few minutes (images are downloaded and the database is initialized). Wait until `airflow-apiserver` is `healthy`.

### 2. Open the Airflow UI

Go to **http://localhost:8080** and log in. The default credentials are defined in `docker-compose.yaml` (usually `airflow` / `airflow`).

> If port 8080 is busy and you changed the mapping to `"8081:8080"`, open **http://localhost:8081** instead.

#### Optional: change the port

If port 8080 is already in use, edit the `airflow-apiserver` service in `docker-compose.yaml`:

```yaml
airflow-apiserver:
  <<: *airflow-common
  command: api-server
  ports:
    - "8081:8080"      # host port : container port
```

- The **first** number (`8081`) is the port on your computer. This is the one you open in the browser.
- The **second** number (`8080`) is the port inside the container. **Do not change it.**
- Do **not** change the healthcheck URL (`http://localhost:8080/...`). It runs inside the container.

Then restart:

```bash
docker compose down
docker compose up -d
```

### 3. Trigger the DAG

1. Find the **`amoCRM_ETL`** DAG.
2. Turn it **on** (new DAGs are paused by default).
3. Click **Trigger** to run it manually.
4. All five tasks should turn **green**.

By default the DAG also runs automatically **every day at 14:00** (`0 14 * * *`). Change the `schedule` value in `amocrm_dag.py` to adjust it.

### 4. Check the data in PostgreSQL

```sql
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
```

Then run `SELECT COUNT(*) FROM <table_name>;` to verify the number of loaded rows.

### Stop the stack

```bash
docker compose down
```

---

## ⚙️ How it works

1. **Extract**: `get_table("leads")` in `amo.py` calls `https://<subdomain>.amocrm.ru/api/v4/<entity>` page by page until there is no `next` link.
2. **Transform**: `pandas.json_normalize` flattens the nested JSON. Dates arrive as Unix timestamps and can be converted to local time.
3. **Load**: `loader()` in `load.py` writes the DataFrame to PostgreSQL through SQLAlchemy using `DB_URL`.
4. **Orchestrate**: Airflow runs one `BashOperator` per entity, and the `tasks` entity runs last.

Use `get_table()` for any other amoCRM entity as well:

```python
from amo import get_table

contacts = get_table("contacts")
pipelines = get_table("leads/pipelines")
```

### Optional: run a script locally (without Docker)

Scripts can also be run directly on your computer for testing. Install the dependencies first:

```bash
pip install python-dotenv requests pandas
```

Then go to the scripts folder and run one:

```bash
cd dags/pipelines
python amo_leads.py
```

> The package is installed as `python-dotenv`, but imported as `dotenv`.

### Optional: create test data

If your amoCRM account is empty, `create_fake.py` can add fake companies, contacts and leads for testing. Use it **only on a test account**, and run it once.

---

## 🛠 Troubleshooting

| Problem | Cause and fix |
|---|---|
| `no configuration file provided: not found` | You are in the wrong folder. `docker compose` looks for `docker-compose.yaml` only in the **current** folder. Run `cd AMOCRM_ETL-`, check with `dir` / `ls` that the file is there, then retry. |
| `Cannot find path ... because it does not exist` (`cd` error) | The folder name is wrong. The cloned folder is `AMOCRM_ETL-` (with a trailing dash). Check the real name with `dir`. |
| `repository ... not found` on `git clone` | The URL is mistyped (for example `.gi` instead of `.git`) or the repo name is wrong. Copy the URL from the green **Code** button on GitHub. |
| `can't open file '...\amo_leads.py': No such file or directory` | You are not in the folder that contains the script. Run `cd dags/pipelines` first, or right-click the folder in VS Code and choose **Open in Integrated Terminal**. |
| Terminal shows `PS ...>` or `>>` inside the command, and PowerShell says a term is not recognized | You pasted the prompt text together with the command. Type only the command itself. Press **Ctrl + C** to clear a stuck `>>` prompt. |
| `ModuleNotFoundError: No module named 'dotenv'` (running scripts locally) | Run `pip install python-dotenv requests pandas`. The package name is `python-dotenv`, not `dotenv`. |
| `failed to read .env ... unexpected character` | `.env` is saved as UTF-16. Re-save it as **UTF-8**. |
| `failed to connect to the docker API` | Docker Desktop is not running. Start it and wait until it is ready. |
| `Bind for 0.0.0.0:8080 failed: port is already allocated` | Another container or program uses port 8080. Stop it, or change the mapping under `airflow-apiserver` to `"8081:8080"` (host port : container port) and open **http://localhost:8081**. Do not change the container port or the healthcheck URL. |
| Airflow UI does not open on `localhost:8081` | After changing the port to `8081:8080`, restart with `docker compose down` then `docker compose up -d`. Keep the healthcheck on `localhost:8080`. |
| `ModuleNotFoundError: No module named 'dags'` | Use `from amo import get_table` (the scripts run inside `dags/pipelines`). |
| `ModuleNotFoundError: No module named 'pandas'` | Dependencies are missing in the Airflow image. Add them via `_PIP_ADDITIONAL_REQUIREMENTS` in `docker-compose.yaml` or build a custom image. |
| Request goes to `none.kommo.com` / HTTP `402` | `AMO_SUBDOMAIN` did not reach the container. Add `AMO_SUBDOMAIN: ${AMO_SUBDOMAIN}` and `AMO_TOKEN: ${AMO_TOKEN}` to `environment:` in `docker-compose.yaml`, then run `docker compose up -d`. |
| HTTP `401` from amoCRM | The token is wrong or incomplete. Create a new token and update `.env`. |
| Database connection refused | Do not use `localhost` in `DB_URL`. Use `host.docker.internal`. |
| Task stays `running` for a long time | A table may be locked (for example, open in pgAdmin or Power BI). Close the connection and clear the task. |

---

## 🔐 Security notes

- Never commit `.env`, tokens, or database passwords.
- Keep `.env` and `config.py` in `.gitignore`.
- If a token is exposed by accident, **revoke it in amoCRM and create a new one immediately**.
- Use a test amoCRM account while developing.

---

## 📬 Contact

**Saidakbar**

[![Telegram](https://img.shields.io/badge/Telegram-@saidakbar4751-26A5E4?logo=telegram&logoColor=white)](https://t.me/saidakbar4751)
[![GitHub](https://img.shields.io/badge/GitHub-saidakbarorunboyev3--ai-181717?logo=github&logoColor=white)](https://github.com/saidakbarorunboyev3-ai)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Saidakbar-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/saidakbar-o-runboyev-168023442)

- Telegram: [@saidakbar4751](https://t.me/saidakbar4751)
- GitHub: [@saidakbarorunboyev3-ai](https://github.com/saidakbarorunboyev3-ai)
- LinkedIn: [Saidakbar O'runboyev](https://www.linkedin.com/in/saidakbar-o-runboyev-168023442)

---

⭐ If you find this project useful, please give it a star!
