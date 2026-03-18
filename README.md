# 🍳 Recipe Sharing Platform
A modern Full-Stack web application for sharing, discovering, and managing recipes.

## 🌟 Overview
This project is a complete solution for food enthusiasts. It allows users to browse recipes, manage their profiles, and share their own culinary creations with the community.

## 💻 Tech Stack

**Frontend:**
* **Framework:** Angular 17/18
* **Styling:** CSS & Bootstrap
* **Features:** Responsive Design, User Authentication, Dynamic Recipe Gallery.

**Backend:**
* **Language:** Python
* **Framework:** Flask
* **ORM:** SQLAlchemy (Object-Relational Mapping)
* **Database:** SQLite (Relational Database)

## 📂 Project Structure
The repository is organized into two main folders:
* `AngularProject/`: All frontend logic, components, and services.
* `recipe_project/`: Python backend, database models, and API routes.

## 🎨 Advanced Image Processing
One of the standout features of this platform is the automated image processing pipeline:
* **Dynamic Filters:** Upon upload, the backend (using the Pillow library) automatically generates 4 different versions of each recipe image: **Original, Black & White, Sepia, and Vivid.**
* **Unique Identification:** Images are stored using `uuid` to prevent filename collisions and ensure data integrity.
* **Efficient Storage:** An organized storage system within the `uploads/` directory, linked directly to the SQLAlchemy models.

## 🚀 Key Features
- **User Management:** Secure login and registration using hashed passwords.
- **Recipe CRUD:** Full Create, Read, Update, and Delete capabilities for recipes.
- **Database Architecture:** Optimized SQLAlchemy models with relationships between Users and Recipes.
- **Admin Dashboard:** Special panel for managing site content and user data.
- **Search & Filter:** Find recipes easily by categories or ingredients.

## 🛠️ How to Run Locally

### 1. Backend Setup (Python)
```bash
cd recipe_project
# Create a virtual environment
py -m venv venv
# Activate it (Windows)
venv\Scripts\activate
# Install all dependencies from requirements.txt
pip install -r requirements.txt
# Run the app
python app.py
```
