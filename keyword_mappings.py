"""
Smart Search Keyword Mappings
This file contains comprehensive keyword mappings for enhanced search functionality.
Each category contains related terms that should match when searching.
"""

# Comprehensive keyword mappings for smart search
KEYWORD_CATEGORIES = {
    'finance': {
        'primary': ['finance', 'financial', 'finances', 'financing'],
        'related': [
            'accounting', 'accountant', 'bookkeeping', 'bookkeeper',
            'investment', 'investor', 'investing', 'portfolio', 'wealth management',
            'banking', 'banker', 'credit', 'lending', 'loan', 'mortgage',
            'tax', 'taxation', 'taxes', 'tax preparation', 'tax planning',
            'budget', 'budgeting', 'financial planning', 'financial advisor',
            'financial consultant', 'financial analyst', 'financial manager',
            'audit', 'auditor', 'auditing', 'compliance', 'risk management',
            'insurance', 'actuary', 'underwriting', 'claims',
            'trading', 'trader', 'stock market', 'securities', 'bonds',
            'retirement planning', 'pension', '401k', 'ira', 'estate planning',
            'cash flow', 'revenue', 'profit', 'loss', 'balance sheet',
            'financial statement', 'forecasting', 'valuation', 'mergers', 'acquisitions'
        ]
    },
    
    'technology': {
        'primary': ['technology', 'tech', 'technical', 'technological'],
        'related': [
            'software', 'programming', 'coding', 'developer', 'programmer',
            'web development', 'frontend', 'backend', 'full stack',
            'mobile development', 'ios', 'android', 'react', 'angular', 'vue',
            'python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go',
            'database', 'sql', 'nosql', 'mysql', 'postgresql', 'mongodb',
            'cloud computing', 'aws', 'azure', 'google cloud', 'devops',
            'artificial intelligence', 'ai', 'machine learning', 'ml', 'data science',
            'cybersecurity', 'security', 'penetration testing', 'ethical hacking',
            'blockchain', 'cryptocurrency', 'bitcoin', 'ethereum',
            'ui/ux', 'user interface', 'user experience', 'design',
            'product management', 'scrum', 'agile', 'project management',
            'system administration', 'network administration', 'it support',
            'data analysis', 'business intelligence', 'bi', 'analytics'
        ]
    },
    
    'business': {
        'primary': ['business', 'commercial', 'corporate', 'enterprise'],
        'related': [
            'management', 'manager', 'executive', 'ceo', 'cfo', 'cto',
            'strategy', 'strategic planning', 'business development',
            'sales', 'salesperson', 'account executive', 'business development',
            'consulting', 'consultant', 'advisor', 'advisory',
            'operations', 'operational', 'process improvement', 'lean', 'six sigma',
            'human resources', 'hr', 'recruitment', 'talent acquisition',
            'project management', 'program management', 'portfolio management',
            'supply chain', 'logistics', 'procurement', 'vendor management',
            'customer service', 'customer support', 'client relations',
            'entrepreneurship', 'startup', 'small business', 'entrepreneur',
            'business analysis', 'requirements gathering', 'process analysis',
            'change management', 'organizational development', 'training'
        ]
    },
    
    'marketing': {
        'primary': ['marketing', 'market', 'promotion', 'advertising'],
        'related': [
            'digital marketing', 'social media', 'content marketing',
            'seo', 'search engine optimization', 'sem', 'ppc', 'google ads',
            'email marketing', 'email campaigns', 'newsletter',
            'branding', 'brand strategy', 'brand identity', 'logo design',
            'public relations', 'pr', 'media relations', 'press release',
            'influencer marketing', 'affiliate marketing', 'partnerships',
            'market research', 'consumer insights', 'analytics', 'tracking',
            'conversion optimization', 'a/b testing', 'landing pages',
            'creative design', 'graphic design', 'visual design',
            'copywriting', 'content creation', 'blogging', 'video marketing',
            'event marketing', 'trade shows', 'conferences', 'webinars',
            'lead generation', 'lead nurturing', 'sales funnel',
            'advertising', 'promotion', 'campaigns'
        ]
    },
    
    'healthcare': {
        'primary': ['healthcare', 'health', 'medical', 'medicine'],
        'related': [
            'doctor', 'physician', 'nurse', 'nursing', 'therapist',
            'psychology', 'psychologist', 'psychiatrist', 'counseling',
            'physical therapy', 'occupational therapy', 'speech therapy',
            'dentistry', 'dental', 'dentist', 'orthodontist',
            'pharmacy', 'pharmacist', 'pharmaceutical', 'drugs',
            'mental health', 'wellness', 'nutrition', 'dietitian',
            'pediatrics', 'geriatrics', 'cardiology', 'neurology',
            'oncology', 'radiology', 'surgery', 'surgical',
            'emergency medicine', 'urgent care', 'primary care',
            'specialist', 'specialty', 'diagnosis', 'treatment',
            'preventive care', 'vaccination', 'immunization',
            'health insurance', 'medical billing', 'coding'
        ]
    },
    
    'education': {
        'primary': ['education', 'educational', 'learning', 'teaching'],
        'related': [
            'teacher', 'instructor', 'professor', 'lecturer', 'tutor',
            'curriculum', 'lesson planning', 'instructional design',
            'online learning', 'e-learning', 'distance education',
            'academic', 'scholarly', 'research', 'thesis', 'dissertation',
            'student', 'learner', 'apprentice', 'mentee',
            'training', 'workshop', 'seminar', 'course', 'class',
            'certification', 'accreditation', 'degree', 'diploma',
            'school', 'university', 'college', 'institution',
            'special education', 'gifted education', 'adult education',
            'language learning', 'esl', 'english as second language',
            'stem', 'science', 'mathematics', 'engineering',
            'literature', 'writing', 'reading', 'literacy',
            'assessment', 'evaluation', 'grading', 'feedback'
        ]
    },
    
    'consulting': {
        'primary': ['consulting', 'consultant', 'consultation', 'advisor'],
        'related': [
            'strategy consulting', 'management consulting', 'business consulting',
            'it consulting', 'technology consulting', 'digital transformation',
            'change management', 'organizational development', 'process improvement',
            'project management', 'program management', 'portfolio management',
            'risk management', 'compliance', 'governance',
            'financial consulting', 'accounting consulting', 'tax consulting',
            'marketing consulting', 'brand consulting', 'communications consulting',
            'human resources consulting', 'hr consulting', 'talent management',
            'operations consulting', 'supply chain consulting', 'logistics consulting',
            'sustainability consulting', 'environmental consulting',
            'legal consulting', 'regulatory consulting',
            'expert witness', 'testimony', 'expertise', 'specialist'
        ]
    },
    
    'creative': {
        'primary': ['creative', 'creativity', 'artistic', 'design'],
        'related': [
            'graphic design', 'visual design', 'ui design', 'ux design',
            'web design', 'print design', 'logo design', 'brand identity',
            'illustration', 'drawing', 'painting', 'sculpture',
            'photography', 'videography', 'video production', 'filmmaking',
            'animation', 'motion graphics', '3d modeling', 'rendering',
            'writing', 'copywriting', 'content creation', 'blogging',
            'music', 'composer', 'musician', 'sound design',
            'fashion design', 'interior design', 'architecture',
            'advertising creative', 'art direction', 'creative direction',
            'storytelling', 'narrative', 'scriptwriting', 'screenwriting'
        ]
    },
    
    'fitness': {
        'primary': ['fitness', 'exercise', 'workout', 'training'],
        'related': [
            'personal trainer', 'fitness coach', 'strength training',
            'cardio', 'cardiovascular', 'aerobic', 'anaerobic',
            'yoga', 'pilates', 'meditation', 'mindfulness',
            'nutrition', 'diet', 'meal planning', 'supplements',
            'weight loss', 'weight management', 'bodybuilding',
            'sports', 'athletics', 'coaching', 'team sports',
            'rehabilitation', 'physical therapy', 'injury prevention',
            'wellness', 'health', 'lifestyle', 'wellbeing',
            'crossfit', 'functional training', 'hiit', 'high intensity',
            'flexibility', 'mobility', 'stretching', 'recovery'
        ]
    }
}

def get_search_keywords(query):
    """
    Expand a search query with related keywords from all categories.
    Returns a list of keywords to search for.
    """
    query_lower = query.lower().strip()
    search_keywords = [query_lower]  # Always include the original query
    
    # Check if the query matches any category keywords
    for category, keywords in KEYWORD_CATEGORIES.items():
        # Check primary keywords
        if query_lower in keywords['primary']:
            search_keywords.extend(keywords['primary'])
            search_keywords.extend(keywords['related'])
        # Check related keywords
        elif query_lower in keywords['related']:
            search_keywords.extend(keywords['primary'])
            search_keywords.extend(keywords['related'])
    
    # Remove duplicates and return
    return list(set(search_keywords))

def get_category_for_keyword(keyword):
    """
    Get the primary category for a given keyword.
    Returns the category name or None if not found.
    """
    keyword_lower = keyword.lower().strip()
    
    for category, keywords in KEYWORD_CATEGORIES.items():
        if (keyword_lower in keywords['primary'] or 
            keyword_lower in keywords['related']):
            return category
    
    return None

def get_all_keywords():
    """
    Get all keywords from all categories.
    Returns a flat list of all keywords.
    """
    all_keywords = []
    for category, keywords in KEYWORD_CATEGORIES.items():
        all_keywords.extend(keywords['primary'])
        all_keywords.extend(keywords['related'])
    return list(set(all_keywords))

def search_in_text(text, query):
    """
    Check if any expanded keywords from the query are found in the text.
    Returns True if any keyword matches.
    """
    if not text or not query:
        return False
    
    text_lower = text.lower()
    search_keywords = get_search_keywords(query)
    
    for keyword in search_keywords:
        if keyword in text_lower:
            return True
    
    return False 