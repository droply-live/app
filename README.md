# Droply

A platform for connecting professionals and clients through scheduled consultations.

## Development Setup

### Prerequisites
- Docker and Docker Compose
- Git

### Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/ant1oine/droply.git
   cd droply
   ```

2. Start the development environment:
   ```bash
   docker-compose up
   ```

3. The application will be available at http://localhost:5000

## Git Workflow

### Branching Strategy

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: For new features
- `bugfix/*`: For bug fixes
- `release/*`: For version releases

### Development Process

1. Create a new branch for your feature/fix:
   ```bash
   git checkout develop
   git pull
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

3. Push your branch and create a Pull Request:
   ```bash
   git push -u origin feature/your-feature-name
   ```

4. Create a Pull Request on GitHub from your branch to `develop`

5. After review and approval, merge your changes into `develop`

6. Periodically, merge `develop` into `main` for releases

### Code Review Guidelines

1. All changes must be reviewed before merging
2. Tests must pass
3. Code must follow the project's style guide
4. Documentation must be updated if necessary

## Database Management

See `docs/sqlite_guide.md` for database management instructions.

## Environment Variables

Create a `.env` file with the following variables:
```
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
DATABASE_URL=postgresql://droply:droply@db:5432/droply
```

## Contributing

1. Follow the Git workflow
2. Write clear commit messages
3. Update documentation as needed
4. Add tests for new features
5. Keep the codebase clean and maintainable 