# Meal Planner Application - Functional Specifications

## Overview
A comprehensive meal planning application that allows users to create, manage, and track their meal plans. The system consists of a Flask REST API backend and will include a React frontend client.

## Current Implementation Status

### ✅ Completed (Phase 1 - Authentication)
- User registration with full profile creation
- JWT-based authentication system
- User login with email or username
- Password hashing with bcrypt
- Protected endpoints with JWT validation
- Get user profile endpoint
- Logout functionality
- Comprehensive test suite (16 tests, 86% coverage)
- Proper HTTP status codes (422 for validation)
- Docker containerization
- PostgreSQL database with all tables created

### 🔄 In Progress
- Feature branch: `feature/auth-tests` (ready for PR)

### 📋 Next Up (Phase 2)
- User profile update endpoints
- Password change functionality
- Food catalog CRUD operations
- Basic meal creation

### 🚀 Future Phases
- Password reset with email
- Email verification
- Admin roles and permissions
- Meal scheduling and planning
- Nutritional tracking
- Shopping list generation
- Frontend application

## Core Features

### 1. Authentication and Authorization

#### 1.1 User Registration
- Users can register with email, username, and password
- Password requirements: minimum 8 characters
- Email verification (future enhancement)
- Required fields: email, username, password, full_name

#### 1.2 User Login
- JWT-based authentication
- Login with email/password or username/password
- Token expiration: 24 hours
- Refresh token mechanism (future enhancement)

#### 1.3 Password Management
- Passwords hashed using bcrypt ✅ Implemented
- Password reset via email 🔄 Planned (requires email service)
- Password change for authenticated users 🔄 Planned

### 2. User Management

#### 2.1 User Profile
- View and edit profile information
- Fields: full_name, phone_number, address, sex
- Profile picture upload (future enhancement)

#### 2.2 User Preferences
- Dietary restrictions
- Allergen tracking
- Calorie targets
- Macro nutrient goals

### 3. Food Catalog Management

#### 3.1 Food Items
- Browse food catalog
- Search by name, category
- Filter by dietary restrictions
- View nutritional information
- Categories: MEAT, FISH, GRAIN, VEGETABLE, FRUIT, DAIRY, DAIRY_ALTERNATIVE, FAT, NIGHTSHADES, OIL, SPICE_HERB, SWEETENER, CONDIMENT, SNACK, BEVERAGE, OTHER

#### 3.2 Nutritional Data
- Calories, protein, carbs, fat, fiber per serving
- Serving size and units
- Non-inflammatory indicator

#### 3.3 User Favorites
- Mark foods as favorites
- Quick access to frequently used items
- Personal food ratings (future enhancement)

### 4. Meal Planning

#### 4.1 Meal Creation
- Combine multiple food items into meals
- Calculate total nutritional values
- Set prep time
- Add preparation notes

#### 4.2 Meal Scheduling
- Assign meals to specific dates
- Multiple meals per day (breakfast, lunch, dinner, snacks)
- Meal number sequencing (1-4+ per day)
- Weekly/monthly view

#### 4.3 Meal History
- Track consumed meals
- Historical data analysis
- Nutritional tracking over time

### 5. API Endpoints

#### Authentication Endpoints
- `POST /api/auth/register` - New user registration
- `POST /api/auth/login` - User login, returns JWT
- `POST /api/auth/refresh` - Refresh JWT token
- `POST /api/auth/logout` - Logout user

#### User Endpoints
- `GET /api/users/profile` - Get current user profile
- `PUT /api/users/profile` - Update user profile
- `GET /api/users/{id}` - Get user by ID (admin only)

#### Food Catalog Endpoints
- `GET /api/foods` - List all foods with pagination
- `GET /api/foods/{id}` - Get specific food item
- `POST /api/foods` - Create new food item (admin only)
- `PUT /api/foods/{id}` - Update food item (admin only)
- `DELETE /api/foods/{id}` - Delete food item (admin only)

#### User Favorites Endpoints
- `GET /api/users/favorites` - Get user's favorite foods
- `POST /api/users/favorites` - Add food to favorites
- `DELETE /api/users/favorites/{food_id}` - Remove from favorites

#### User Meals Endpoints
- `GET /api/users/meals` - Get user's meals with date filtering
- `POST /api/users/meals` - Create and assign meal to user
- `PUT /api/users/meals/{id}` - Update user's meal
- `DELETE /api/users/meals/{id}` - Remove meal from schedule

### 6. Business Rules

#### 6.1 Authentication Rules
- JWT tokens expire after 24 hours
- Users can only access their own data (except admins)
- Admin role required for food catalog modifications

#### 6.2 Data Validation Rules
- Email must be unique and valid format
- Username must be unique
- Meal dates cannot be in the past when creating
- Food quantities must be positive numbers

#### 6.3 Nutritional Calculations
- Meal nutrition = sum of (ingredient nutrition * quantity/serving_size)
- Daily totals = sum of all meals for a date
- Weekly averages calculated from daily totals

### 7. Security Considerations

#### 7.1 Data Protection
- All passwords bcrypt hashed
- JWT secrets stored in environment variables
- Database credentials in .env file
- HTTPS required for production (future)

#### 7.2 Input Validation
- SQL injection prevention via SQLAlchemy ORM
- Input sanitization with Pydantic schemas
- Rate limiting (future enhancement)

### 8. Future Enhancements

#### Phase 2
- Meal recommendations based on preferences
- Shopping list generation
- Recipe instructions and photos
- Meal sharing between users

#### Phase 3
- Mobile application
- Barcode scanning for food items
- Integration with fitness trackers
- AI-powered meal suggestions
- Social features (meal sharing, ratings)

## Technical Requirements

### Backend
- Python 3.11+
- Flask 3.0
- PostgreSQL 15
- JWT for authentication
- Docker for containerization

### Frontend (Future)
- React 18+
- TypeScript
- Material-UI or similar component library
- Responsive design for mobile/tablet

### Infrastructure
- Docker Compose for local development
- PostgreSQL on port 5455 (configurable)
- API on port 8088
- Frontend on port 3000 (future)

## Success Metrics
- User can register and login within 2 minutes
- Meal planning for a week completed in under 10 minutes
- Page load times under 2 seconds
- 99.9% API uptime
