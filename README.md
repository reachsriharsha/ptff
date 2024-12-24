# Project Name: [PTFF]

**Description:**

This project utilizes Docker Compose to orchestrate a multi-container environment for a Flask application. The following services are defined:

- **nginx:** 
    - Acts as a reverse proxy, handling incoming requests and routing them to the backend service.
    - Serves static files (if configured in your `nginx.conf`).
- **redis:** 
    - Provides a Redis server for caching, message queuing (e.g., for Celery), and other in-memory data storage needs.
- **postgres:** 
    - A PostgreSQL database for persistent data storage.
- **backend:** 
    - The core Flask application, handling API requests and business logic.
    - Includes a `Dockerfile` for building the backend container image.
- **celery_worker:** 
    - A dedicated container for running Celery workers, enabling asynchronous task processing.
- **frontend:** 
    - The frontend application (e.g., React, Vue.js), serving static assets and interacting with the backend API.
    - Includes a `Dockerfile` for building the frontend container image.

**Dependencies:**

- Docker and Docker Compose

**Setup:**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/reachsriharsha/ptff.git

2. **Build and start the containers:**
docker-compose up -d

**Accessing the application:**

he frontend application will be accessible at http://localhost.
