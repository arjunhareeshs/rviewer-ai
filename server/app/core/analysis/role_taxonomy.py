"""
Role Taxonomy Database - Complete role definitions with required/preferred skills
Used for role recommendation engine
"""

# ═══════════════════════════════════════════════════════════════════════════════
# ROLE TAXONOMY - All roles with skills and project keywords
# ═══════════════════════════════════════════════════════════════════════════════

ROLE_TAXONOMY = {
    # ═══════════════════════════════════════════════════════════════════════════
    # AI/ML ROLES
    # ═══════════════════════════════════════════════════════════════════════════

    "ml_engineer": {
        "display_name": "Machine Learning Engineer",
        "category": "ai_ml",
        "required_skills": [
            "machine learning", "deep learning", "tensorflow", "pytorch",
            "python", "scikit-learn", "neural networks"
        ],
        "preferred_skills": [
            "aws", "docker", "kubernetes", "spark", "airflow",
            "mlops", "kubeflow", "mlflow", "transformers", "huggingface"
        ],
        "project_keywords": [
            "ml pipeline", "model training", "model deployment",
            "nlp", "computer vision", "recommendation system",
            "anomaly detection", "predictive model", "classification",
            "regression", "clustering", "cnn", "rnn", "lstm"
        ],
        "experience_years": 2,
    },

    "ai_engineer": {
        "display_name": "AI Engineer",
        "category": "ai_ml",
        "required_skills": [
            "generative ai", "ai agents", "langchain", "llamaindex",
            "rag", "openai", "anthropic", "python", "api integration"
        ],
        "preferred_skills": [
            "fastapi", "docker", "vector database", "qdrant", "weaviate",
            "prompt engineering", "finetuning", "llmops", "streamlit"
        ],
        "project_keywords": [
            "llm application", "rag system", "chatbot", "ai agent",
            "generative ai", "prompt engineering", "vector search",
            "llm", "gpt", "chatgpt", "language model"
        ],
        "experience_years": 2,
    },

    "data_scientist": {
        "display_name": "Data Scientist",
        "category": "ai_ml",
        "required_skills": [
            "python", "pandas", "numpy", "scikit-learn", "machine learning",
            "statistics", "data analysis", "sql"
        ],
        "preferred_skills": [
            "tableau", "power bi", "spark", "deep learning", "tensorflow",
            "excel", "r", "matlab", "plotly"
        ],
        "project_keywords": [
            "data analysis", "predictive model", "data visualization",
            "statistical analysis", "a/b testing", "insights",
            "eda", "exploratory data", "model building"
        ],
        "experience_years": 2,
    },

    "nlp_engineer": {
        "display_name": "NLP Engineer",
        "category": "ai_ml",
        "required_skills": [
            "nlp", "natural language processing", "transformers", "pytorch",
            "tensorflow", "python", "spacy", "nltk"
        ],
        "preferred_skills": [
            "huggingface", "langchain", "llamaindex", "rag",
            "sentiment analysis", "ner", "text generation", "bert"
        ],
        "project_keywords": [
            "nlp", "text classification", "named entity recognition",
            "sentiment analysis", "text generation", "chatbot",
            "language model", "transformer", "tokenization"
        ],
        "experience_years": 2,
    },

    "computer_vision_engineer": {
        "display_name": "Computer Vision Engineer",
        "category": "ai_ml",
        "required_skills": [
            "computer vision", "deep learning", "opencv", "pytorch",
            "tensorflow", "python", "image processing"
        ],
        "preferred_skills": [
            "yolo", "resnet", "segmentation", "object detection",
            "face recognition", "medical imaging", "satellite imagery",
            "detection", "tracking"
        ],
        "project_keywords": [
            "computer vision", "object detection", "image segmentation",
            "face recognition", "object tracking", "image classification",
            "yolo", "cnn", "opencv", "image processing"
        ],
        "experience_years": 2,
    },

    "mle_intern": {
        "display_name": "ML Engineer Intern",
        "category": "ai_ml",
        "required_skills": [
            "python", "machine learning", "tensorflow", "pytorch"
        ],
        "preferred_skills": [
            "pandas", "numpy", "scikit-learn", "jupyter"
        ],
        "project_keywords": [
            "machine learning", "deep learning", "model training",
            "neural network", "python"
        ],
        "experience_years": 0,
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # DATA ROLES
    # ═══════════════════════════════════════════════════════════════════════════

    "data_analyst": {
        "display_name": "Data Analyst",
        "category": "data",
        "required_skills": [
            "python", "sql", "pandas", "excel", "tableau", "data analysis"
        ],
        "preferred_skills": [
            "power bi", "statistics", "r", "looker", "data visualization"
        ],
        "project_keywords": [
            "dashboard", "data visualization", "reporting", "etl",
            "data cleaning", "insights", "analytics", "excel",
            "charts", "graphs", "business intelligence"
        ],
        "experience_years": 1,
    },

    "data_engineer": {
        "display_name": "Data Engineer",
        "category": "data",
        "required_skills": [
            "python", "sql", "spark", "airflow", "etl", "data pipeline"
        ],
        "preferred_skills": [
            "kafka", "dbt", "postgresql", "mongodb", "snowflake",
            "databricks", "hadoop", "hive", "bigquery"
        ],
        "project_keywords": [
            "data pipeline", "etl", "data warehouse", "data lake",
            "stream processing", "data integration", "spark",
            "airflow", "pipeline"
        ],
        "experience_years": 2,
    },

    "analytics_engineer": {
        "display_name": "Analytics Engineer",
        "category": "data",
        "required_skills": [
            "sql", "dbt", "tableau", "data modeling"
        ],
        "preferred_skills": [
            "python", "airflow", "snowflake", "bigquery", "looker"
        ],
        "project_keywords": [
            "analytics", "data model", "bi", "dashboard", "reporting"
        ],
        "experience_years": 2,
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # SOFTWARE ENGINEERING ROLES
    # ═══════════════════════════════════════════════════════════════════════════

    "backend_developer": {
        "display_name": "Backend Developer",
        "category": "backend",
        "required_skills": [
            "python", "api", "rest api", "database", "sql", "git"
        ],
        "preferred_skills": [
            "django", "fastapi", "flask", "postgresql", "redis",
            "docker", "graphql", "microservices", "aws"
        ],
        "project_keywords": [
            "rest api", "backend", "server", "database", "authentication",
            "microservice", "api development", "crud", "api",
            "endpoint", "server-side"
        ],
        "experience_years": 1,
    },

    "full_stack_developer": {
        "display_name": "Full Stack Developer",
        "category": "fullstack",
        "required_skills": [
            "javascript", "react", "node.js", "python", "sql", "api"
        ],
        "preferred_skills": [
            "typescript", "next.js", "mongodb", "postgresql", "docker",
            "graphql", "aws", "tailwind", "express"
        ],
        "project_keywords": [
            "web application", "full stack", "frontend", "backend",
            "mern", "crud application", "user authentication",
            "web app", "spa", "responsive"
        ],
        "experience_years": 2,
    },

    "frontend_developer": {
        "display_name": "Frontend Developer",
        "category": "frontend",
        "required_skills": [
            "javascript", "react", "html", "css", "typescript"
        ],
        "preferred_skills": [
            "next.js", "vue", "angular", "tailwind", "sass", "webpack",
            "redux", "zustand", "framer motion", "react native"
        ],
        "project_keywords": [
            "frontend", "ui", "web application", "react application",
            "user interface", "responsive design", "spa",
            "javascript", "web app", "component"
        ],
        "experience_years": 1,
    },

    "api_developer": {
        "display_name": "API Developer",
        "category": "backend",
        "required_skills": [
            "python", "rest api", "graphql", "fastapi", "postgresql"
        ],
        "preferred_skills": [
            "docker", "kubernetes", "aws", "api gateway", "rate limiting",
            "authentication", "oauth", "jwt"
        ],
        "project_keywords": [
            "rest api", "graphql api", "api development", "api gateway",
            "microservice api", "internal api", "endpoint"
        ],
        "experience_years": 2,
    },

    "python_developer": {
        "display_name": "Python Developer",
        "category": "backend",
        "required_skills": [
            "python", "django", "flask", "fastapi", "sql"
        ],
        "preferred_skills": [
            "postgresql", "redis", "docker", "celery", "rq"
        ],
        "project_keywords": [
            "python", "django", "flask", "web application", "backend"
        ],
        "experience_years": 1,
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # DEVOPS/CLOUD ROLES
    # ═══════════════════════════════════════════════════════════════════════════

    "devops_engineer": {
        "display_name": "DevOps Engineer",
        "category": "devops",
        "required_skills": [
            "docker", "kubernetes", "aws", "linux", "git", "ci/cd"
        ],
        "preferred_skills": [
            "terraform", "ansible", "jenkins", "gitlab", "github actions",
            "prometheus", "grafana", "elk", "helm"
        ],
        "project_keywords": [
            "devops", "ci/cd", "infrastructure", "deployment",
            "containerization", "orchestration", "automation",
            "jenkins", "pipeline", "cicd"
        ],
        "experience_years": 3,
    },

    "cloud_engineer": {
        "display_name": "Cloud Engineer",
        "category": "devops",
        "required_skills": [
            "aws", "azure", "gcp", "docker", "kubernetes", "linux"
        ],
        "preferred_skills": [
            "terraform", "cloudformation", "serverless", "lambda",
            "ecs", "eks", "gke", "cloudwatch"
        ],
        "project_keywords": [
            "cloud", "aws", "azure", "cloud infrastructure",
            "serverless", "cloud migration", "infrastructure as code"
        ],
        "experience_years": 2,
    },

    "site_reliability_engineer": {
        "display_name": "Site Reliability Engineer (SRE)",
        "category": "devops",
        "required_skills": [
            "linux", "docker", "kubernetes", "python", "monitoring"
        ],
        "preferred_skills": [
            "prometheus", "grafana", "elk", "chaos engineering",
            "terraform", "incident management"
        ],
        "project_keywords": [
            "sre", "monitoring", "observability", "incident response",
            "log analysis", "uptime", "reliability", "metrics"
        ],
        "experience_years": 3,
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # MOBILE ROLES
    # ═══════════════════════════════════════════════════════════════════════════

    "android_developer": {
        "display_name": "Android Developer",
        "category": "mobile",
        "required_skills": [
            "kotlin", "android", "java", "xml", "android studio"
        ],
        "preferred_skills": [
            "jetpack compose", "retrofit", "room", "kotlin coroutines",
            "mvvm", "firebase", "hilt", "dagger"
        ],
        "project_keywords": [
            "android", "mobile app", "android application", "kotlin app",
            "mobile", "app development"
        ],
        "experience_years": 1,
    },

    "ios_developer": {
        "display_name": "iOS Developer",
        "category": "mobile",
        "required_skills": [
            "swift", "ios", "xcode", "objective-c"
        ],
        "preferred_skills": [
            "swiftui", "uikit", "core data", "firebase", "alamofire",
            "mvvm", "combine"
        ],
        "project_keywords": [
            "ios", "mobile app", "swift application", "iphone app",
            "mobile", "xcode"
        ],
        "experience_years": 1,
    },

    "react_native_developer": {
        "display_name": "React Native Developer",
        "category": "mobile",
        "required_skills": [
            "react native", "javascript", "typescript", "react"
        ],
        "preferred_skills": [
            "expo", "redux", "react navigation", "firebase",
            "styled-components", "mobx"
        ],
        "project_keywords": [
            "react native", "mobile app", "cross-platform", "ios", "android",
            "expo", "mobile"
        ],
        "experience_years": 1,
    },

    "flutter_developer": {
        "display_name": "Flutter Developer",
        "category": "mobile",
        "required_skills": [
            "flutter", "dart", "ios", "android"
        ],
        "preferred_skills": [
            "firebase", "rest api", "state management"
        ],
        "project_keywords": [
            "flutter", "dart", "mobile app", "cross-platform"
        ],
        "experience_years": 1,
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # DATABASE ROLES
    # ═══════════════════════════════════════════════════════════════════════════

    "database_administrator": {
        "display_name": "Database Administrator",
        "category": "database",
        "required_skills": [
            "postgresql", "mysql", "sql", "database", "backup"
        ],
        "preferred_skills": [
            "mongodb", "redis", "elasticsearch", "database tuning",
            "replication", "sharding", "aws rds", "indexing"
        ],
        "project_keywords": [
            "database", "database management", "database design",
            "query optimization", "data modeling", "sql"
        ],
        "experience_years": 2,
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # SECURITY ROLES
    # ═══════════════════════════════════════════════════════════════════════════

    "security_engineer": {
        "display_name": "Security Engineer",
        "category": "security",
        "required_skills": [
            "cybersecurity", "network security", "penetration testing",
            "firewall", "vpn", "encryption"
        ],
        "preferred_skills": [
            "owasp", "siem", "sonarqube", "aws security", "compliance",
            "vulnerability"
        ],
        "project_keywords": [
            "security", "penetration testing", "vulnerability assessment",
            "security audit", "encryption", "authentication",
            "cybersecurity"
        ],
        "experience_years": 2,
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # EMERGING/SPECIALIZED ROLES
    # ═══════════════════════════════════════════════════════════════════════════

    "blockchain_developer": {
        "display_name": "Blockchain Developer",
        "category": "emerging",
        "required_skills": [
            "solidity", "ethereum", "web3", "smart contracts", "blockchain"
        ],
        "preferred_skills": [
            "javascript", "react", "node.js", "nft", "defi",
            "truffle", "hardhat", "web3.js", "ethers.js"
        ],
        "project_keywords": [
            "blockchain", "smart contract", "ethereum", "web3",
            "dapp", "nft", "defi", "crypto", "solidity"
        ],
        "experience_years": 2,
    },

    "embedded_systems_engineer": {
        "display_name": "Embedded Systems Engineer",
        "category": "emerging",
        "required_skills": [
            "c", "c++", "embedded systems", "arduino", "raspberry pi"
        ],
        "preferred_skills": [
            "rtos", "microcontroller", "iot", "uart", "spi", "i2c",
            "firmware", "arm", "esp32"
        ],
        "project_keywords": [
            "embedded", "firmware", "iot", "microcontroller", "arduino",
            "raspberry pi", "robotics", "c", "c++"
        ],
        "experience_years": 2,
    },

    "qa_engineer": {
        "display_name": "QA Engineer",
        "category": "testing",
        "required_skills": [
            "testing", "qa", "test automation", "selenium"
        ],
        "preferred_skills": [
            "playwright", "cypress", "jest", "junit", "manual testing",
            "regression testing", "performance testing"
        ],
        "project_keywords": [
            "testing", "qa", "test automation", "unit testing",
            "integration testing", "test cases", "automation"
        ],
        "experience_years": 1,
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # RESEARCH/ACADEMIC ROLES
    # ═══════════════════════════════════════════════════════════════════════════

    "research_intern": {
        "display_name": "Research Intern",
        "category": "research",
        "required_skills": [
            "research", "machine learning", "python", "data analysis"
        ],
        "preferred_skills": [
            "pytorch", "tensorflow", "paper reading", "latex",
            "experimentation", "statistics", "jupyter"
        ],
        "project_keywords": [
            "research", "paper", "thesis", "experimentation",
            "machine learning research", "academic", "publication"
        ],
        "experience_years": 0,
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # PRODUCT/MANAGEMENT ROLES
    # ═══════════════════════════════════════════════════════════════════════════

    "technical_product_manager": {
        "display_name": "Technical Product Manager",
        "category": "product",
        "required_skills": [
            "product management", "technical", "agile", "roadmapping"
        ],
        "preferred_skills": [
            "sql", "data analysis", "user research", "jira", "confluence"
        ],
        "project_keywords": [
            "product", "roadmap", "stakeholder management", "requirements",
            "product strategy"
        ],
        "experience_years": 3,
    },

    "solutions_architect": {
        "display_name": "Solutions Architect",
        "category": "architecture",
        "required_skills": [
            "system design", "architecture", "aws", "cloud"
        ],
        "preferred_skills": [
            "kubernetes", "microservices", "terraform", "enterprise"
        ],
        "project_keywords": [
            "architecture", "system design", "solution design",
            "technical architecture", "infrastructure"
        ],
        "experience_years": 4,
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # ADDITIONAL COMMON ROLES
    # ═══════════════════════════════════════════════════════════════════════════

    "software_engineer": {
        "display_name": "Software Engineer",
        "category": "software",
        "required_skills": [
            "programming", "python", "java", "javascript", "git"
        ],
        "preferred_skills": [
            "sql", "docker", "rest api", "data structures"
        ],
        "project_keywords": [
            "software", "application", "development", "programming"
        ],
        "experience_years": 1,
    },

    "systems_engineer": {
        "display_name": "Systems Engineer",
        "category": "systems",
        "required_skills": [
            "linux", "python", "networking", "scripting"
        ],
        "preferred_skills": [
            "aws", "docker", "automation", "bash"
        ],
        "project_keywords": [
            "systems", "infrastructure", "automation", "scripting"
        ],
        "experience_years": 2,
    },

    "web_developer": {
        "display_name": "Web Developer",
        "category": "web",
        "required_skills": [
            "javascript", "html", "css", "web development"
        ],
        "preferred_skills": [
            "react", "node.js", "python", "web"
        ],
        "project_keywords": [
            "web", "website", "web development", "frontend"
        ],
        "experience_years": 1,
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# Role Categories for Grouping
# ═══════════════════════════════════════════════════════════════════════════════

ROLE_CATEGORIES = {
    "ai_ml": ["ml_engineer", "ai_engineer", "data_scientist", "nlp_engineer", "computer_vision_engineer", "mle_intern"],
    "data": ["data_analyst", "data_engineer", "analytics_engineer"],
    "backend": ["backend_developer", "api_developer", "python_developer"],
    "frontend": ["frontend_developer", "web_developer"],
    "fullstack": ["full_stack_developer"],
    "devops": ["devops_engineer", "cloud_engineer", "site_reliability_engineer"],
    "mobile": ["android_developer", "ios_developer", "react_native_developer", "flutter_developer"],
    "database": ["database_administrator"],
    "security": ["security_engineer"],
    "emerging": ["blockchain_developer", "embedded_systems_engineer"],
    "testing": ["qa_engineer"],
    "research": ["research_intern"],
    "product": ["technical_product_manager"],
    "architecture": ["solutions_architect"],
    "software": ["software_engineer"],
    "systems": ["systems_engineer"],
}

# ═══════════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════════

def get_role(role_id: str) -> dict:
    """Get role definition by ID"""
    return ROLE_TAXONOMY.get(role_id)

def get_roles_by_category(category: str) -> list:
    """Get all roles in a category"""
    return ROLE_CATEGORIES.get(category, [])

def get_all_role_ids() -> list:
    """Get all role IDs"""
    return list(ROLE_TAXONOMY.keys())

def get_all_categories() -> list:
    """Get all role categories"""
    return list(ROLE_CATEGORIES.keys())