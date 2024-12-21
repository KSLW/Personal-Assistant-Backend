## Personal Assistant Backend API

### Overview
This is the backend API for the Personal Assistant application. It handles user authentication, reminders, tasks, and email notifications using Firebase and FastAPI.

---

### Features
- User management (create, retrieve)
- Reminder management (CRUD operations, recurring reminders)
- Task management (CRUD operations, overdue tasks, recurring tasks)
- Email notifications
- Logging and monitoring

---

### Endpoints

#### Users
| Method | Endpoint     | Description             | Required Parameters |
|--------|--------------|-------------------------|----------------------|
| `POST` | `/users`     | Create a new user       | `email`, `password` |
| `GET`  | `/users`     | Get user details        | `email`             |

#### Reminders
| Method | Endpoint                | Description                       | Required Parameters       |
|--------|--------------------------|-----------------------------------|---------------------------|
| `POST` | `/reminders`            | Create a new reminder             | `reminder`                |
| `GET`  | `/reminders`            | Get all reminders                 |                           |
| `GET`  | `/reminders/{reminder_id}` | Get a specific reminder by ID     | `reminder_id`             |
| `PUT`  | `/reminders/{reminder_id}` | Update a reminder                 | `reminder_id`, `updates`  |
| `POST` | `/reschedule-reminders` | Reschedule recurring reminders    |                           |
| `POST` | `/expire-reminders`     | Expire old reminders              | `expiry_date`             |

#### Tasks
| Method | Endpoint                | Description                       | Required Parameters       |
|--------|--------------------------|-----------------------------------|---------------------------|
| `POST` | `/tasks`                | Create a new task                 | `task`                    |
| `GET`  | `/tasks`                | Get all tasks with filters        | `status`, `priority`, `category` (optional) |
| `PUT`  | `/tasks/{task_id}`      | Update a task                     | `task_id`, `updates`      |
| `DELETE`| `/tasks/{task_id}`     | Delete a task                     | `task_id`                 |
| `GET`  | `/tasks/search`         | Search tasks by keyword           | `query`                   |
| `GET`  | `/tasks/overdue`        | Get overdue tasks                 |                           |
| `POST` | `/reschedule-tasks`     | Reschedule recurring tasks        |                           |

#### Emails
| Method | Endpoint         | Description              | Required Parameters |
|--------|-------------------|--------------------------|----------------------|
| `POST` | `/send-test-email`| Send a test email        | `recipient`          |

---

### Setup and Installation

#### Prerequisites
- Python 3.9+
- Firebase Admin SDK credentials (`FIREBASE_CREDENTIALS`)
- MailerSend API Key (`MAILERSEND_API_KEY`)
- `.env` file for storing environment variables

#### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/personal-assistant-backend.git
   ```
2. Navigate to the project directory:
   ```bash
   cd personal-assistant-backend
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up the `.env` file with your Firebase and MailerSend credentials.

#### Running the Application
```bash
uvicorn app.main:app --reload
```

---

### Functionality

#### Firebase Services
- **Reminders**
  - Add, retrieve, update, reschedule, and expire reminders.
- **Tasks**
  - Add, retrieve, update, delete, and reschedule tasks.
  - Support for filtered and sorted retrieval.
- **User Management**
  - Create and retrieve users using Firebase Authentication.

#### Logging
Integrated logging for API requests and system errors.

---

### Scheduled Jobs
- **Reminder Scheduler**: Automatically reschedules recurring reminders and tasks.
- **Expiry Cleanup**: Removes old reminders and tasks based on a defined expiry period.

---

### Contributing
1. Fork the repository.
2. Create a new feature branch.
3. Commit your changes.
4. Push to the branch and create a pull request.

---

### License
This project is licensed under the MIT License.
