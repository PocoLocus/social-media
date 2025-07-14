Overview:
This project is a social media platform built with Django framework. In the main ChitChat tab users can sign up, create posts, interact via likes and comments, explore profiles, filter posts by tags and search by author or content. A settings tab allows users to update their username and password. The platform includes a forgot password feature for secure password recovery. The recently added Movies tab lets users search for films via the TMDB API, rate them and add them to the shared movies list, with detailed information. Users can view, sort, rate and update ratings for any added movie. The project also includes Django REST Framework (DRF) support, exposing selected features through RESTful APIs for easier frontend integration or future mobile app development.

Core Features:
- User authentication & settings: Sign-up, login, logout, forgot password, password reset and username change functionality via custom user model.
- Post system: Create, edit, delete, like and comment on posts. Posts can be filtered by tags, authors or search keywords.
- Movie integration via TMDB API: Search and fetch real-time movie data. Add movies to the shared database with metadata and a personal rating. View all added movies, including details like poster, description and release date.
- Rating system: Rate or update ratings for any movie. Movies are sortable by average rating, date added or other fields.
- Admin panel: Custom django admin panel for managing users, posts, movies and ratings.
- Django REST Framework (DRF) APIs: RESTful API endpoints for key app functionalities.

Tech Stack:
- Backend: Django, Django REST Framework
- Database: SQLite (development), PostgreSQL (production)
- Frontend: HTML, CSS, JavaScript
- API integration: TMDB
- Authentication: Django's built-in auth with custom logic and decorators
