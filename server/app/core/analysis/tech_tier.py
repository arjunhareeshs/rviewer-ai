"""
Tech Tier Database - Complete technology tier classification
Used for project strength analysis and role matching
"""

# ═══════════════════════════════════════════════════════════════════════════════
# TIER S - Most In-Demand (Current Hot Tech)
# ═══════════════════════════════════════════════════════════════════════════════
TIER_S = {
    # Frontend
    "react", "reactjs", "next.js", "nextjs", "typescript", "tsx", "jsx",

    # Backend
    "python", "go", "golang", "rust", "node.js", "nodejs",

    # AI/ML
    "tensorflow", "pytorch", "transformers", "huggingface",
    "langchain", "llamaindex", "openai", "anthropic", "gpt",
    "machine learning", "deep learning", "neural networks",
    "computer vision", "nlp", "natural language processing",

    # Cloud/DevOps
    "aws", "amazon web services", "azure", "gcp", "google cloud",
    "docker", "kubernetes", "k8s", "terraform", "ansible",

    # Data
    "spark", "apache spark", "kafka", "airflow", "dbt",

    # Database
    "postgresql", "redis", "mongodb",

    # Mobile
    "flutter", "react native",

    # New/Trending
    "generative ai", "gen ai", "ai agents", "rag", "vector database",
    "qdrant", "weaviate", "pinecone", "milvus", "chatgpt",
}

# ═══════════════════════════════════════════════════════════════════════════════
# TIER A - High Demand
# ═══════════════════════════════════════════════════════════════════════════════
TIER_A = {
    # Frontend
    "vue.js", "vuejs", "angular", "svelte", "javascript", "html", "css",
    "tailwind", "sass", "scss", "webpack", "vite",

    # Backend
    "java", "spring boot", "c#", ".net", "csharp", "django", "fastapi",
    "flask", "express", "express.js", "graphql", "rest api",

    # Database
    "mysql", "oracle", "sql server", "firebase", "supabase",

    # Data
    "pandas", "numpy", "scikit-learn", "tableau", "power bi",

    # Mobile
    "swift", "kotlin", "android", "ios",

    # DevOps
    "jenkins", "gitlab", "github actions", "circleci", "github",

    # Tools
    "git", "linux", "bash", "vim",

    # Data Science
    "data science", "data analysis", "statistics", "data visualization",
}

# ═══════════════════════════════════════════════════════════════════════════════
# TIER B - Moderate/Niche Demand
# ═══════════════════════════════════════════════════════════════════════════════
TIER_B = {
    # Languages
    "scala", "haskell", "erlang", "elixir", "lua", "r", "matlab",
    "perl", "ruby", "objective-c", "dart", "coffeescript",

    # Frameworks
    "ruby on rails", "laravel", "phoenix", "play framework",

    # Data/Specialized
    "sas", "spss", "looker", "bigquery", "snowflake",
    "databricks", "hadoop", "hive", "pig", "cassandra", "dynamodb",
    "elasticsearch", "grafana", "prometheus", "kibana",

    # Mobile
    "xamarin", "ionic", "cordova",

    # Testing
    "selenium", "cypress", "playwright", "jest", "mocha", "junit",

    # Other
    "wordpress", "shopify", "magento",

    # Security
    "penetration testing", "cybersecurity", "network security",

    # Blockchain
    "solidity", "ethereum", "web3", "blockchain", "smart contracts",
}

# ═══════════════════════════════════════════════════════════════════════════════
# TIER C - Legacy / Outdated / Low Demand
# ═══════════════════════════════════════════════════════════════════════════════
TIER_C = {
    # Legacy
    "php", "jquery", "angularjs", "backbone.js", "ember.js",
    "visual basic", "classic asp", "cobol", "fortran", "pascal",
    "delphi", "vb.net", "sharepoint", "ms access",

    # Outdated
    "flash", "actionscript", "silverlight", "wcf",

    # Deprecated
    "xml", "soap", "wsdl", "ejb", "jsp", "servlet",

    # Old formats
    "word", "excel", "powerpoint",
}

# All tiers combined
TECH_TIER = {
    "tier_s": TIER_S,
    "tier_a": TIER_A,
    "tier_b": TIER_B,
    "tier_c": TIER_C,
}

# ═══════════════════════════════════════════════════════════════════════════════
# Skill Categories for Role Matching
# ═══════════════════════════════════════════════════════════════════════════════

SKILL_CATEGORIES = {
    "programming_languages": [
        "python", "java", "javascript", "typescript", "go", "rust",
        "c++", "c#", "ruby", "php", "swift", "kotlin", "scala", "r",
        "c", "objective-c", "dart", "matlab"
    ],
    "frontend_frameworks": [
        "react", "vue", "angular", "svelte", "next.js", "typescript",
        "html", "css", "tailwind", "sass", "webpack", "vite", "jsx", "tsx"
    ],
    "backend_frameworks": [
        "node.js", "django", "fastapi", "flask", "spring", "rails",
        "express", "graphql", "rest api", "microservices", "spring boot"
    ],
    "databases": [
        "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
        "cassandra", "dynamodb", "firebase", "supabase", "sql server",
        "oracle", "mariadb", "sqlite"
    ],
    "cloud_platforms": [
        "aws", "azure", "gcp", "google cloud", "amazon web services"
    ],
    "devops_tools": [
        "docker", "kubernetes", "terraform", "ansible", "jenkins",
        "gitlab", "github actions", "circleci", "helm", "kustomize"
    ],
    "ai_ml": [
        "machine learning", "deep learning", "tensorflow", "pytorch",
        "nlp", "computer vision", "transformers", "langchain",
        "llamaindex", "rag", "generative ai", "ai agents",
        "neural networks", "scikit-learn", "huggingface"
    ],
    "data_engineering": [
        "spark", "kafka", "airflow", "dbt", "etl", "data pipeline",
        "apache spark", "snowflake", "databricks", "bigquery"
    ],
    "data_analysis": [
        "pandas", "numpy", "tableau", "power bi", "excel", "sql",
        "statistics", "data visualization", " Looker"
    ],
    "mobile": [
        "react native", "flutter", "swift", "kotlin", "android", "ios",
        "xamarin", "cordova", "ionic"
    ],
    "security": [
        "cybersecurity", "penetration testing", "network security",
        "owasp", "encryption", "vpn", "firewall", "siem"
    ],
    "blockchain": [
        "solidity", "ethereum", "web3", "blockchain", "smart contracts",
        "nft", "defi", "web3.js", "ethers.js"
    ],
    "testing": [
        "selenium", "cypress", "playwright", "jest", "mocha", "junit",
        "pytest", "testing", "test automation", "manual testing"
    ],
    "iot": [
        "arduino", "raspberry pi", "embedded", "firmware", "rtos",
        "microcontroller", "uart", "spi", "i2c", "iot"
    ],
}

# ═══════════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════════

def get_tech_tier(tech: str) -> str:
    """Get the tier for a technology"""
    tech_lower = tech.lower().strip()

    if tech_lower in TIER_S:
        return "tier_s"
    elif tech_lower in TIER_A:
        return "tier_a"
    elif tech_lower in TIER_B:
        return "tier_b"
    elif tech_lower in TIER_C:
        return "tier_c"
    else:
        return "unknown"

def get_tier_score(tier: str) -> int:
    """Get numeric score for a tier"""
    tier_scores = {
        "tier_s": 100,
        "tier_a": 75,
        "tier_b": 50,
        "tier_c": 25,
        "unknown": 10,
    }
    return tier_scores.get(tier, 10)

def get_category_for_skill(skill: str) -> str:
    """Get the category for a skill"""
    skill_lower = skill.lower().strip()

    for category, skills in SKILL_CATEGORIES.items():
        if skill_lower in skills:
            return category
    return "other"

def calculate_tech_score(technologies: list) -> int:
    """Calculate tech stack score (0-100)"""
    if not technologies:
        return 0

    total_score = 0
    for tech in technologies:
        tier = get_tech_tier(tech)
        total_score += get_tier_score(tier)

    # Normalize to 0-100
    max_possible = len(technologies) * 100
    return min(100, int(total_score / max_possible * 100))