#!/usr/bin/env python3
"""
Demo script to showcase Droply's new features
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5001"

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_section(title):
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print(f"{'-'*40}")

def demo_nlp_search():
    """Demonstrate NLP search functionality"""
    print_section("NLP Search Examples")
    
    search_queries = [
        "Find a Python developer in San Francisco",
        "Marketing expert for startups under $150/hour",
        "Business coach in New York",
        "AI consultant for tech companies",
        "Fitness trainer in Los Angeles"
    ]
    
    for query in search_queries:
        print(f"🔍 Query: '{query}'")
        print(f"   → Would extract: specialty, location, price, industry")
        print()

def demo_onboarding_flow():
    """Demonstrate onboarding flow"""
    print_section("Onboarding Flow")
    
    steps = [
        {
            "step": 1,
            "title": "Preferences",
            "description": "Users select their goals",
            "options": ["Find experts", "Offer services", "Network", "Learn"]
        },
        {
            "step": 2,
            "title": "Specialties",
            "description": "Users select specialty tags (Tinder/Bumble style)",
            "categories": ["Technology", "Business", "Marketing", "Health & Wellness"]
        },
        {
            "step": 3,
            "title": "Location",
            "description": "Users set location and meeting preferences",
            "fields": ["City", "Country", "Timezone", "Meeting formats"]
        }
    ]
    
    for step in steps:
        print(f"📋 Step {step['step']}: {step['title']}")
        print(f"   {step['description']}")
        if 'options' in step:
            print(f"   Options: {', '.join(step['options'])}")
        if 'categories' in step:
            print(f"   Categories: {', '.join(step['categories'])}")
        if 'fields' in step:
            print(f"   Fields: {', '.join(step['fields'])}")
        print()

def demo_specialty_tags():
    """Demonstrate specialty tags system"""
    print_section("Specialty Tags System")
    
    categories = {
        "Technology": ["Python", "JavaScript", "React", "AI/ML", "Web Development", "Mobile Development"],
        "Business": ["Strategy", "Startups", "Fundraising", "Operations", "Leadership"],
        "Marketing": ["Digital Marketing", "Social Media", "Content Marketing", "SEO"],
        "Health & Wellness": ["Fitness", "Nutrition", "Mental Health", "Yoga"]
    }
    
    for category, tags in categories.items():
        print(f"🏷️  {category}:")
        for tag in tags:
            print(f"   • {tag}")
        print()

def demo_features():
    """Main demo function"""
    print_header("Droply - New Features Demo")
    print(f"🚀 Running demo at: {BASE_URL}")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Demo each feature
    demo_onboarding_flow()
    demo_specialty_tags()
    demo_nlp_search()
    
    print_section("Feature Summary")
    features = [
        "✅ Full-page login experience",
        "✅ 3-step onboarding flow",
        "✅ Tinder/Bumble-style specialty tags",
        "✅ NLP search with natural language processing",
        "✅ Voice search capability",
        "✅ Mobile-responsive design",
        "✅ Real-time profile preview",
        "✅ Advanced search filters"
    ]
    
    for feature in features:
        print(f"   {feature}")
    
    print(f"\n🎉 Demo completed! Visit {BASE_URL} to try the features yourself.")
    print("\n💡 Try these search queries:")
    print("   • 'Find a Python developer in San Francisco'")
    print("   • 'Marketing expert for startups'")
    print("   • 'Fitness coach under $100/hour'")

if __name__ == "__main__":
    try:
        demo_features()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Thanks for checking out Droply!")
    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        print("Make sure the application is running on http://localhost:5001") 