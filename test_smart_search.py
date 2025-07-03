#!/usr/bin/env python3
"""
Test script for smart search functionality
"""

from keyword_mappings import get_search_keywords, search_in_text, get_category_for_keyword

def test_keyword_expansion():
    """Test keyword expansion functionality"""
    print("Testing keyword expansion:")
    print("=" * 50)
    
    test_queries = [
        "finance",
        "financial",
        "tech",
        "technology", 
        "marketing",
        "healthcare",
        "education",
        "consulting",
        "creative",
        "fitness"
    ]
    
    for query in test_queries:
        keywords = get_search_keywords(query)
        print(f"\nQuery: '{query}'")
        print(f"Expanded keywords ({len(keywords)}): {keywords[:10]}...")  # Show first 10
        if len(keywords) > 10:
            print(f"  ... and {len(keywords) - 10} more keywords")

def test_text_search():
    """Test text search functionality"""
    print("\n\nTesting text search:")
    print("=" * 50)
    
    test_texts = [
        "I am a financial advisor with expertise in investment planning",
        "Software developer specializing in Python and web development",
        "Marketing consultant helping businesses grow their digital presence",
        "Healthcare professional with experience in patient care",
        "Education specialist in curriculum development and online learning"
    ]
    
    test_queries = ["finance", "tech", "marketing", "health", "education"]
    
    for text in test_texts:
        print(f"\nText: '{text}'")
        for query in test_queries:
            matches = search_in_text(text, query)
            print(f"  Query '{query}': {'✓' if matches else '✗'}")

def test_category_mapping():
    """Test category mapping functionality"""
    print("\n\nTesting category mapping:")
    print("=" * 50)
    
    test_keywords = [
        "finance", "accountant", "investment", "banking",
        "technology", "programming", "software", "developer",
        "marketing", "advertising", "seo", "branding",
        "healthcare", "doctor", "nurse", "therapy",
        "education", "teacher", "learning", "curriculum"
    ]
    
    for keyword in test_keywords:
        category = get_category_for_keyword(keyword)
        print(f"'{keyword}' -> {category}")

if __name__ == "__main__":
    test_keyword_expansion()
    test_text_search()
    test_category_mapping()
    print("\n\nSmart search testing complete!") 