# CyberLevel - Gamified Task Management System

## 🚀 Project Overview
CyberLevel is an engaging gamified task management system designed to help users stay productive while leveling up their skills. Users can complete tasks, earn XP, and unlock higher levels, making productivity fun and rewarding.

## 🛠 Features
* 📝 **Task Management**: Add, complete, and delete tasks.
* 🎮 **Leveling System**: Gain XP and level up based on task completion.
* 📷 **Profile Customization**: Upload profile photos and update usernames/passwords.
* 🔐 **Secure Authentication**: Login, logout, password reset, and CSRF protection.
* ✨ **Futuristic Cyber UI**: A neon-inspired, animated interface for an immersive experience.


## 🔧 Installation & Setup
### 1️⃣ Clone Repository

```sh
git clone https://github.com/dvecy/Leveling.git
cd CyberLevel
```

### 2️⃣ Set Up Virtual Environment

```sh
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate    # On Windows
```

### 3️⃣ Install Dependencies

```sh
pip install -r Backend/requirements.txt
```

### 4️⃣ Set Up Database

```sh
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 5️⃣ Run the Application

```sh
python Backend/main.py
```

The app will be available at **http://127.0.0.1:5001/** 🚀

## 📌 Usage Guide
* Visit `/register` to create an account.
* Login at `/login`.
* Manage tasks and level up via the dashboard.
* Update profile settings via `/settings`.

## 🔒 Security & Best Practices
* User passwords are hashed using `bcrypt`.
* CSRF protection is enforced using `Flask-WTF`.
* Profile photo uploads are validated against allowed file types.

## 👥 Collaborators
* **@sadatnazarli** (Backend & Project Lead)
* **@Yunis003** (Frontend Developer & UI/UX)

## ⭐ Contributing
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit (`git commit -m "Added new feature"`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request.




