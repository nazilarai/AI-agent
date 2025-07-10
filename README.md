# 🔍 Smart Admin Finder

**Expert-Level Admin Panel Discovery Tool for Ethical Security Assessments**

A professional-grade Python CLI tool that generates intelligent admin panel URL paths using contextual heuristics, OSINT enrichment, and machine learning techniques.

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/user/smart-admin-finder)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

## ⚠️ **ETHICAL USE ONLY**

This tool is designed exclusively for **authorized security assessments** and **educational purposes**. Users must ensure they have explicit permission before testing any systems.

## 🚀 Features

### Core Capabilities
- **🎯 Intelligent Path Generation**: Over 500+ base admin paths across multiple categories
- **🧠 ML-Enhanced Accuracy**: TF-IDF vectorization for context-aware suggestions
- **🌐 OSINT Enrichment**: DNS reconnaissance, WHOIS lookups, technology detection
- **⚙️ CMS Detection**: Automatic detection and specialized paths for 8+ CMS platforms
- **🌍 Multi-Language Support**: Localized admin paths for 9 languages
- **📊 Smart Ranking**: Intelligent scoring algorithm for path prioritization

### Supported Platforms
- **CMS**: WordPress, Joomla, Drupal, Magento, Shopify, PrestaShop, OpenCart, TYPO3
- **Languages**: English, Spanish, French, German, Italian, Portuguese, Russian, Chinese, Japanese
- **Site Types**: Blog, Shop, Government, Corporate, Educational, News, Forum

### Advanced Features
- **Subdomain Analysis**: Automatic subdomain enumeration and analysis
- **Technology Stack Detection**: Server fingerprinting and framework identification
- **Name-Based Paths**: Personalized paths using owner information
- **Graceful Degradation**: Works without optional dependencies

## 📋 Requirements

### System Requirements
- **Python**: 3.8 or higher
- **OS**: Linux, macOS, Windows
- **Memory**: 256MB minimum

### Dependencies

#### Core (Required)
```bash
# Built-in Python modules only for basic functionality
```

#### Enhanced Features (Optional)
```bash
pip install requests dnspython python-whois numpy scikit-learn
```

**Note**: The tool works without optional dependencies but with reduced OSINT and ML capabilities.

## 🛠️ Installation

### Option 1: Direct Usage
```bash
# Clone or download main.py
python3 main.py
```

### Option 2: With Enhanced Features
```bash
# Install optional dependencies for full functionality
pip install requests dnspython python-whois numpy scikit-learn
python3 main.py
```

### Option 3: Virtual Environment (Recommended)
```bash
python3 -m venv smart_admin_env
source smart_admin_env/bin/activate  # Linux/Mac
# smart_admin_env\Scripts\activate  # Windows
pip install requests dnspython python-whois numpy scikit-learn
python3 main.py
```

## 💻 Usage

### Basic Usage
```bash
python3 main.py
```

### Command Line Options
```bash
python3 main.py --help     # Show help message
python3 main.py --version  # Show version information
```

### Interactive Mode
The tool runs in interactive mode by default, prompting for:

#### Required Information
- **Target URL**: The website to analyze (e.g., `https://example.com`)

#### Optional Information (Press Enter to skip)
- **Owner's Name**: For personalized path generation
- **Site Type**: blog, shop, government, corporate, educational, news, forum
- **CMS Platform**: wordpress, joomla, drupal, magento, shopify, etc.
- **Language**: For localized admin paths
- **OSINT Enrichment**: Enable advanced reconnaissance (y/N)

### Example Session
```
🌐 Target website URL (required): https://example.com
� Owner's full name: John Smith
🏢 Site type: blog
⚙️ CMS/Platform used: wordpress
🌍 Site language: english
Enable expert-level OSINT enrichment? (y/N): y
```

## 📊 Output

### Generated Files
- **`output/generated_admin_paths.txt`**: Complete list of generated paths with metadata

### Output Structure
```
# === HIGH PRIORITY PATHS (Top 50) ===
admin
wp-admin
administrator
...

# === ADDITIONAL PATHS ===
backend
control
...

# === STATISTICS ===
# Total unique paths generated: 247
# High priority paths: 50
# Additional paths: 197
```

### Path Categories
1. **High Priority** (Top 50): Most likely admin paths based on scoring
2. **Additional Paths**: Extended suggestions for comprehensive testing
3. **Statistics**: Generation summary and metadata

## 🧠 Intelligence Features

### Path Generation Sources
- **Base Admin Paths**: 35+ common admin URL patterns
- **CMS-Specific**: Targeted paths for detected/specified CMS
- **Language-Specific**: Localized admin terminology
- **Site-Type Specific**: Paths based on website category
- **Name-Based**: Variations using owner information
- **Subdomain Analysis**: Paths derived from subdomain patterns
- **OSINT-Enhanced**: Intelligence from reconnaissance data
- **ML-Generated**: Context-aware suggestions using TF-IDF

### Scoring Algorithm
Paths are ranked using multiple factors:
- **Admin Keywords**: Presence of administrative terms
- **CMS Relevance**: Match with detected/specified platform
- **Language Match**: Alignment with specified language
- **Site Type**: Relevance to website category
- **Personalization**: Inclusion of owner information
- **Simplicity Bonus**: Preference for clean, simple paths
- **Complexity Penalty**: Reduction for overly complex URLs

## 🔍 OSINT Capabilities

When enabled, the tool performs:

### DNS Reconnaissance
- A, AAAA, CNAME, MX, TXT, NS record enumeration
- Common subdomain discovery
- DNS-based technology hints

### WHOIS Analysis
- Domain registration information
- Organizational details
- Country and registrar data

### Technology Detection
- Server fingerprinting via headers
- Automatic CMS detection
- Framework identification
- Technology stack analysis

## 🛡️ Security & Ethics

### Ethical Guidelines
1. **Authorization Required**: Only test systems you own or have explicit permission to test
2. **Legal Compliance**: Ensure compliance with local laws and regulations
3. **Responsible Disclosure**: Report findings through appropriate channels
4. **No Malicious Use**: This tool is for defensive security purposes only

### What This Tool Does NOT Do
- ❌ Perform actual HTTP requests to test paths
- ❌ Attempt to bypass authentication
- ❌ Exploit vulnerabilities
- ❌ Access unauthorized systems

### Data Privacy
- 🔒 No data is transmitted to external servers
- 🔒 All processing happens locally
- 🔒 Optional logging to local file only

## 🐛 Troubleshooting

### Common Issues

#### Missing Dependencies
```bash
⚠️ Some OSINT features unavailable. Missing: requests, dnspython
💡 Install with: pip install requests dnspython python-whois
```

#### Permission Errors
```bash
# Use virtual environment or --break-system-packages flag
python3 -m venv venv && source venv/bin/activate
pip install <packages>
```

#### Import Errors
```bash
# Ensure Python 3.8+
python3 --version

# Check installed packages
pip list
```

## 📝 Examples

### E-commerce Site
```
Target: https://shop.example.com
Owner: Jane Doe
Site Type: shop
CMS: magento
Language: english
OSINT: Yes

Generated paths include:
- admin
- magento_admin
- shop/admin
- janedoe_admin
- tienda (if Spanish detected)
```

### Government Portal
```
Target: https://portal.gov.example
Site Type: government
Language: english
OSINT: Yes

Generated paths include:
- admin
- gov-admin
- government
- secure
- portal
- official
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup
```bash
git clone <repository>
cd smart-admin-finder
python3 -m venv dev-env
source dev-env/bin/activate
pip install -r requirements-dev.txt
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚖️ Legal Disclaimer

The authors and contributors of this tool are not responsible for any misuse or illegal activities. Users are solely responsible for ensuring their use of this tool complies with applicable laws and ethical guidelines.

This tool is provided "as is" without warranty of any kind. Use at your own risk.

## 🔗 Resources

- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [Ethical Hacking Guidelines](https://www.eccouncil.org/ethical-hacking/)
- [Responsible Disclosure](https://cheatsheetseries.owasp.org/cheatsheets/Vulnerability_Disclosure_Cheat_Sheet.html)

---

**Remember**: With great power comes great responsibility. Use this tool ethically! 🛡️
