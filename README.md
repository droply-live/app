# Droply - Automated Deployment Test - Professional Networking Platform

A modern platform for connecting professionals, coaches, and mentors. Built with Flask, featuring a beautiful UI and advanced search capabilities.

## 🚀 New Features (Latest Update)

### 1. **Full-Page Login Experience**
- Beautiful, modern full-page login design
- Takes up the entire viewport with gradient background
- Mobile-responsive with proper touch targets
- Clean, professional aesthetic

### 2. **Onboarding Flow**
- **Step 1: Preferences** - Users select their goals (find experts, offer services, network, learn)
- **Step 2: Specialties** - Users select specialty tags (like Tinder/Bumble)
- **Step 3: Location** - Users set city, country, timezone, and meeting preferences
- Progress indicator shows completion status
- Automatic redirect after registration/login

### 3. **Specialty Tags System**
- Tinder/Bumble-style specialty tags
- Categories: Technology, Business, Marketing, Health & Wellness
- Custom specialty creation
- Tags displayed on profiles and used in search
- Easy editing via modal interface

### 4. **NLP Search Bar**
- **Natural Language Processing** - Type queries like:
  - "Find a Python developer in San Francisco"
  - "Marketing expert for startups"
  - "Fitness coach under $100/hour"
- **Smart Parsing** - Automatically extracts:
  - Specialties (Python, Marketing, Fitness, etc.)
  - Locations (San Francisco, etc.)
  - Price ranges (under $100/hour)
  - Industries (startups, tech, etc.)
- **Voice Search** - Microphone button for voice input
- **Search Suggestions** - Popular search examples
- **Visual Feedback** - Shows parsed search criteria as colored tags

### 5. **Enhanced Search Functionality**
- NLP-powered search across specialty tags, expertise, profession, location, and price
- Advanced filters (collapsible) for traditional search
- Mobile-responsive search interface
- Real-time search suggestions

## 🛠️ Technical Features

### Backend
- **Flask** - Python web framework
- **SQLAlchemy** - Database ORM
- **SQLite** - Database (can be easily switched to PostgreSQL/MySQL)
- **Flask-Login** - User authentication
- **Stripe** - Payment processing integration

### Frontend
- **Bootstrap 5** - Responsive CSS framework
- **Feather Icons** - Beautiful icon set
- **Custom CSS** - Modern, clean design
- **JavaScript** - Interactive features and NLP parsing

### Database Schema
```sql
-- User model with new fields
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256),
    full_name VARCHAR(100),
    bio TEXT,
    industry VARCHAR(100),
    profession VARCHAR(100),
    expertise VARCHAR(200),
    location VARCHAR(100),
    specialty_tags TEXT,  -- JSON array of specialty tags
    onboarding_completed BOOLEAN DEFAULT FALSE,
    onboarding_step INTEGER DEFAULT 0,
    hourly_rate FLOAT DEFAULT 0.0,
    currency VARCHAR(3) DEFAULT 'USD',
    -- Social media links
    linkedin_url VARCHAR(200),
    twitter_url VARCHAR(200),
    youtube_url VARCHAR(200),
    instagram_url VARCHAR(200),
    website_url VARCHAR(200),
    -- Settings
    is_available BOOLEAN DEFAULT TRUE,
    created_at DATETIME,
    updated_at DATETIME
);
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   export FLASK_APP=main.py
   export FLASK_ENV=development
   export STRIPE_SECRET_KEY=your_stripe_secret_key
   ```

4. **Initialize the database**
   ```bash
   python -c "from app import app, db; from models import User; app.app_context().push(); db.create_all()"
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - If port 5000 is in use, the app will automatically use port 5001

## 📱 User Flow

### New User Registration
1. **Register** → Fill in basic information
2. **Full-page Login** → Beautiful login experience
3. **Onboarding** → 3-step setup process:
   - Step 1: Select preferences and interests
   - Step 2: Choose specialty tags
   - Step 3: Set location and meeting preferences
4. **Dashboard** → Access to all features

### Search Experience
1. **NLP Search Bar** → Type natural language queries
2. **Smart Parsing** → See extracted search criteria
3. **Results** → Filtered by specialty, location, price, etc.
4. **Profile View** → Detailed expert profiles with specialty tags

### Profile Management
1. **Edit Profile** → Update information and specialty tags
2. **Specialty Modal** → Add/remove specialty tags
3. **Copy URL** → Share profile easily
4. **Real-time Preview** → See changes instantly

## 🔍 Search Examples

### Natural Language Queries
- "Find a Python developer in San Francisco"
- "Marketing expert for startups under $150/hour"
- "Business coach in New York"
- "AI consultant for tech companies"
- "Fitness trainer in Los Angeles"

### Parsed Results
The NLP system automatically extracts:
- **Specialties**: Python, Marketing, Business, AI, Fitness
- **Locations**: San Francisco, New York, Los Angeles
- **Price Ranges**: under $150/hour
- **Industries**: startups, tech companies

## 📱 Mobile Responsiveness

All features are fully mobile-responsive:
- Touch-friendly interfaces
- Proper spacing and sizing
- Responsive modals and forms
- Mobile-optimized search experience

## 🎨 Design Features

- **Modern UI** - Clean, professional design
- **Gradient Backgrounds** - Beautiful visual appeal
- **Smooth Animations** - Enhanced user experience
- **Consistent Branding** - Droply color scheme throughout
- **Accessibility** - Screen reader friendly

## 🔧 Configuration:

### Environment Variables
```bash
FLASK_APP=main.py
FLASK_ENV=development
STRIPE_SECRET_KEY=your_stripe_secret_key
REPLIT_DEV_DOMAIN=your_domain
REPLIT_DEPLOYMENT=true
```
 
### Database Configuration
The application uses SQLite by default. To switch to PostgreSQL or MySQL:
1. Update the database URL in `app.py`
2. Install the appropriate database driver
3. Run database migrations

## 🚀 Deployment

### Local Development
```bash
python main.py
```

### Production Deployment
1. Set `FLASK_ENV=production`
2. Configure a production database
3. Set up proper environment variables
4. Use a production WSGI server (Gunicorn, uWSGI)

## 📊 Features Overview

| Feature | Status | Description |
|---------|--------|-------------|
| Full-page Login | ✅ | Beautiful, modern login experience |
| Onboarding Flow | ✅ | 3-step user setup process |
| Specialty Tags | ✅ | Tinder/Bumble-style tag system |
| NLP Search | ✅ | Natural language search processing |
| Voice Search | ✅ | Microphone input support |
| Mobile Responsive | ✅ | Fully responsive design |
| Profile Management | ✅ | Edit specialties and information |
| Payment Integration | ✅ | Stripe payment processing |
| Calendar Integration | ✅ | Availability management |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

---

**Droply** - Connecting professionals, one specialty at a time! 🚀 