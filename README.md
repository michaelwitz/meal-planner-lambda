# Meal Planner API

A Flask-based REST API for meal planning with JWT authentication, built with Flask, SQLAlchemy, and PostgreSQL.

## Documentation

- [Functional Specifications](docs/FunctionalSpecs.md) - Detailed feature requirements and API documentation

## Tech Stack

- **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-JWT-Extended
- **Database**: PostgreSQL
- **Validation**: Pydantic, Flask-Pydantic
- **Authentication**: JWT (JSON Web Tokens)
- **Containerization**: Docker, Docker Compose

## Database Schema

```
┌──────────────────────────┐
│          User            │
├──────────────────────────┤
│ id (PK)                  │
│ email                    │
│ username                 │
│ password_hash            │
│ full_name                │
│ sex                      │ (MALE, FEMALE, OTHER)
│ phone_number             │
│ address_line_1           │
│ address_line_2           │
│ city                     │
│ state_province_code      │
│ country_code             │
│ postal_code              │
│ created_at               │
│ updated_at               │
└──────────────────────────┘
        │
        │ 1:many
        ├────────────────────┐
        │                    │
        ▼                    ▼
┌─────────────────┐  ┌─────────────────┐
│  FoodUserLikes  │  │    UserMeal     │
├─────────────────┤  ├─────────────────┤
│ id (PK)         │  │ id (PK)         │
│ user_id (FK)    │  │ user_id (FK)    │
│ food_id (FK)    │  │ meal_id (FK)    │
│ created_at      │  │ date            │
└─────────────────┘  │ meal_number     │ (1=breakfast, 2=lunch, 3=dinner, etc.)
        │            │ created_at      │
        │            └─────────────────┘
        │                    │
        ▼                    ▼
┌─────────────────┐  ┌─────────────────┐
│  FoodCatalog    │  │      Meal       │
├─────────────────┤  ├─────────────────┤
│ id (PK)         │  │ id (PK)         │
│ name            │  │ name            │
│ category        │  │ description     │
│ calories        │  │ total_calories  │
│ protein         │  │ total_protein   │
│ carbs           │  │ total_carbs     │
│ fat             │  │ total_fat       │
│ fiber           │  │ prep_time       │
│ serving_size    │  │ created_at      │
│ unit            │  │ updated_at      │
│ non_inflammatory│  └─────────────────┘
│ created_at      │          │
│ updated_at      │          │ 1:many
└─────────────────┘          │
        │                    ▼
        │            ┌─────────────────┐
        └───────────▶│ MealIngredients │
                     ├─────────────────┤
                     │ id (PK)         │
                     │ meal_id (FK)    │
                     │ food_id (FK)    │
                     │ quantity        │
                     │ unit            │
                     │ notes           │
                     │ created_at      │
                     └─────────────────┘
```

### Database Relationships

- **User ←→ FoodCatalog** (many-to-many via FoodUserLikes): Tracks user's liked/favorite foods
- **User ←→ Meal** (many-to-many via UserMeal): Tracks user's meals by date and meal number
- **Meal ←→ FoodCatalog** (many-to-many via MealIngredients): Defines what foods are in each meal

### Association Tables

- **FoodUserLikes**: Links users to foods they like
- **UserMeal**: Links users to meals with date and meal_number (order in day)
- **MealIngredients**: Links meals to food items with quantities

### Enums/Keywords (ALL_CAPS)

- **Sex**: MALE, FEMALE, OTHER
- **Food Categories**: MEAT, FISH, GRAIN, VEGETABLE, FRUIT, DAIRY, DAIRY_ALTERNATIVE, FAT, NIGHTSHADES, OIL, SPICE_HERB, SWEETENER, CONDIMENT, SNACK, BEVERAGE, OTHER

### Column Notes

- `non_inflammatory`: Boolean field in FoodCatalog indicating if the food is non-inflammatory
- `meal_number`: Integer in UserMeal representing meal order (1=breakfast, 2=lunch, 3=dinner, 4=snack, etc.)
- All tables use `id` as primary key
- Foreign keys follow pattern: `tablename_id` (e.g., `user_id`, `meal_id`, `food_id`)

## Project Structure

```
meal-planner-lambda/
├── backend/
│   ├── app/
│   │   ├── blueprints/       # Flask blueprints for routes
│   │   ├── services/         # Business logic layer
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas for validation
│   │   ├── utils/            # Utility functions
│   │   ├── middlewares/      # Custom middlewares
│   │   └── decorators/       # Custom decorators
│   ├── scripts/              # Database scripts
│   ├── tests/                # Unit and integration tests
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile
├── docs/                     # Documentation
│   └── FunctionalSpecs.md    # Functional specifications
├── frontend/                 # React frontend (future)
├── docker-compose.dev.yml    # Development environment
├── docker-compose.test.yml   # Test environment
├── .env                      # Environment variables (not in git)
├── .env.example              # Environment template
└── README.md                 # This file
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11 (use conda: `conda create -n meal-planner python=3.11`)
- PostgreSQL (runs in Docker on port 5455)

### Environment Setup

1. Copy `.env.example` to `.env` and update with your values
2. The development PostgreSQL port is set to 5455 to avoid conflicts
3. The test PostgreSQL port is set to 5456

### Docker Compose Files

- **docker-compose.dev.yml** - Development environment with hot-reload
- **docker-compose.test.yml** - Test database for running tests

### Running with Docker

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down

# Start test database
docker-compose -f docker-compose.test.yml up -d
```

**Note**: The project name is set to `meal-planner` in the `.env` file to ensure consistent Docker resource naming.

### Quick Start

```bash
# 1. Setup Python environment
conda create -n meal-planner python=3.11 -y
conda activate meal-planner

# 2. Install dependencies
cd backend
pip install -r requirements.txt

# 3. Start development PostgreSQL
cd ..
docker-compose -f docker-compose.dev.yml up -d db

# 4. Initialize database
cd backend
python scripts/rebuild_db.py

# 5. Run Flask API (optional)
flask run
```

### Environment Variables

#### Development Database
- `DEV_DATABASE_URL` - Development database connection string
- `DEV_POSTGRES_DB` - Development database name
- `DEV_POSTGRES_USER` - Development database user
- `DEV_POSTGRES_PASSWORD` - Development database password
- `DEV_POSTGRES_PORT` - Development database port (default: 5455)

#### Test Databases
- `TEST_DATABASE_URL_LOCAL` - Local test database (Docker)
- `TEST_DATABASE_URL_CLOUD` - Cloud test database (AWS Aurora)
- `TEST_DATABASE_URL` - Active test database (set by test runner)

### Test Credentials

After running `rebuild_db.py`:
- Admin: admin@mealplanner.com / admin123
- User1: john.doe@example.com / password123
- User2: jane.smith@example.com / password123

### API Documentation

See [Functional Specifications](docs/FunctionalSpecs.md) for complete API endpoint documentation and feature details.

## License

Private - All rights reserved
