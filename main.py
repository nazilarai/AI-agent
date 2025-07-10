#!/usr/bin/env python3
"""
Smart Admin Finder - Expert-Level Admin Panel Discovery Tool
===============================================================

A professional CLI tool for ethical security assessments and admin panel discovery.
Generates intelligent admin panel URL paths using contextual heuristics, OSINT, and ML.

Author: Security Research Team
Version: 1.0.0
License: MIT (For Educational and Ethical Use Only)
"""

import os
import re
import sys
import json
import time
import random
import urllib.parse
from typing import List, Dict, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
import argparse
import logging
from collections import defaultdict
import hashlib

# Standard library imports for OSINT and web analysis
try:
    import requests
    from urllib.parse import urlparse, urljoin
    REQUESTS_AVAILABLE = True
except ImportError:
    from urllib.parse import urlparse, urljoin
    REQUESTS_AVAILABLE = False

try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False

try:
    import whois
    WHOIS_AVAILABLE = True
except ImportError:
    WHOIS_AVAILABLE = False

# ML and data processing
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False


@dataclass
class TargetInfo:
    """Comprehensive target information container."""
    url: str
    domain: str = ""
    subdomain: str = ""
    owner_name: str = ""
    site_type: str = ""
    cms: str = ""
    language: str = ""
    enable_osint: bool = False
    
    # OSINT-derived data
    whois_info: Dict[str, Any] = field(default_factory=dict)
    dns_records: Dict[str, List[str]] = field(default_factory=dict)
    tech_stack: Set[str] = field(default_factory=set)
    detected_cms: str = ""
    server_info: Dict[str, str] = field(default_factory=dict)


class SmartAdminFinder:
    """Expert-level admin panel discovery tool with ML-enhanced path generation."""
    
    def __init__(self):
        """Initialize the Smart Admin Finder with comprehensive path databases."""
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Core admin paths database
        self.base_admin_paths = [
            "admin", "administrator", "admin.php", "admin.html", "admin.asp",
            "admin.aspx", "admin.jsp", "admin/", "administrator/", "admin/login",
            "admin/login.php", "admin/login.html", "admin/admin", "admin/dashboard",
            "administration", "administracion", "adminpanel", "admin_panel",
            "control", "controlpanel", "control_panel", "cpanel", "cpanel/",
            "manager", "management", "manage", "admin-console", "admin_console",
            "backend", "back-end", "login", "signin", "sign-in", "login.php",
            "login.html", "login.asp", "login.aspx", "login.jsp", "auth",
            "authenticate", "authentication", "portal", "admin_portal",
            "dashboard", "console", "panel", "webadmin", "web-admin",
            "siteadmin", "site-admin", "root", "superuser", "su", "admin_area",
            "admin-area", "restricted", "secure", "private", "internal"
        ]
        
        # CMS-specific admin paths
        self.cms_paths = {
            "wordpress": [
                "wp-admin", "wp-admin/", "wp-login.php", "wp-admin/admin.php",
                "wp/wp-admin", "blog/wp-admin", "wordpress/wp-admin", "wp-content/",
                "wp-includes/", "wp-admin/install.php", "wp-admin/upgrade.php"
            ],
            "joomla": [
                "administrator", "administrator/", "admin", "joomla/administrator",
                "administrator/index.php", "components/com_admin", "installation/"
            ],
            "drupal": [
                "admin", "admin/", "user", "user/login", "admin/content",
                "admin/structure", "admin/appearance", "admin/modules", "admin/config",
                "drupal/admin", "sites/default", "core/"
            ],
            "magento": [
                "admin", "admin/", "downloader", "downloader/", "index.php/admin",
                "magento_admin", "backend", "admin_area", "store_admin"
            ],
            "shopify": [
                "admin", "admin/", "admin/auth/login", "admin/api", "services/ping"
            ],
            "prestashop": [
                "admin", "admin/", "adminer", "admin123", "admin_dir", "backoffice"
            ],
            "opencart": [
                "admin", "admin/", "opencart/admin", "catalog/admin", "store_admin"
            ],
            "typo3": [
                "typo3", "typo3/", "typo3/sysext/backend", "typo3conf", "fileadmin"
            ],
            "concrete5": [
                "index.php/dashboard", "concrete/authentication/login",
                "dashboard", "login"
            ]
        }
        
        # Language-specific admin paths
        self.language_paths = {
            "spanish": ["administracion", "administrador", "admin", "gestión", "panel"],
            "french": ["administration", "administrateur", "admin", "gestion", "panneau"],
            "german": ["verwaltung", "administrator", "admin", "verwaltungsbereich"],
            "italian": ["amministrazione", "amministratore", "admin", "pannello"],
            "portuguese": ["administracao", "administrador", "admin", "painel", "gestao"],
            "russian": ["admin", "administrator", "upravlenie", "panel"],
            "chinese": ["admin", "guanli", "administrator", "houtai"],
            "japanese": ["admin", "kanri", "administrator", "kanrishitsu"],
            "korean": ["admin", "gwalri", "administrator", "gwallija"]
        }
        
        # Site type specific paths
        self.site_type_paths = {
            "blog": ["blog/admin", "blog-admin", "blogger", "wp-admin", "posts"],
            "shop": ["shop/admin", "store/admin", "cart/admin", "checkout/admin", "inventory"],
            "government": ["gov-admin", "government", "official", "secure", "portal"],
            "corporate": ["corporate/admin", "company/admin", "enterprise", "intranet"],
            "educational": ["edu/admin", "school/admin", "student", "faculty", "academic"],
            "news": ["news/admin", "editorial", "journalist", "newsroom", "editor"],
            "forum": ["forum/admin", "moderator", "mod", "community", "board"]
        }
        
        # Initialize ML components
        if ML_AVAILABLE:
            self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        else:
            self.vectorizer = None
        self.path_knowledge_base = self._build_knowledge_base()
        
    def setup_logging(self) -> None:
        """Configure logging for the application."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('smart_admin_finder.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def _build_knowledge_base(self) -> List[str]:
        """Build a comprehensive knowledge base for ML training."""
        knowledge_base = []
        knowledge_base.extend(self.base_admin_paths)
        
        for cms_paths in self.cms_paths.values():
            knowledge_base.extend(cms_paths)
        
        for lang_paths in self.language_paths.values():
            knowledge_base.extend(lang_paths)
            
        for type_paths in self.site_type_paths.values():
            knowledge_base.extend(type_paths)
            
        return list(set(knowledge_base))  # Remove duplicates
    
    def display_banner(self) -> None:
        """Display the professional tool banner."""
        banner = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                           🔍 SMART ADMIN FINDER 🔍                           ║
║                     Expert-Level Admin Panel Discovery                        ║
║                                                                               ║
║  🎯 Intelligent Path Generation  🧠 ML-Enhanced Accuracy  🌐 OSINT Enriched  ║
║                                                                               ║
║                        For Ethical Security Assessment Only                   ║
╚═══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        print("🚀 Initializing Smart Admin Finder v1.0.0...\n")
    
    def gather_user_input(self) -> TargetInfo:
        """Interactively gather comprehensive target information."""
        print("📋 Target Information Gathering")
        print("=" * 50)
        
        # Required: Target URL
        while True:
            url = input("🌐 Target website URL (required): ").strip()
            if url:
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                try:
                    parsed = urlparse(url)
                    if parsed.netloc:
                        break
                except Exception:
                    pass
            print("❌ Please enter a valid URL")
        
        # Parse domain and subdomain
        parsed_url = urlparse(url)
        domain_parts = parsed_url.netloc.split('.')
        subdomain = ""
        domain = parsed_url.netloc
        
        if len(domain_parts) > 2:
            subdomain = '.'.join(domain_parts[:-2])
            domain = '.'.join(domain_parts[-2:])
        
        print(f"✅ Target: {url}")
        print(f"📍 Domain: {domain} | Subdomain: {subdomain or 'None'}\n")
        
        # Optional information
        print("📝 Additional Information (Optional - Press Enter to skip)")
        print("-" * 55)
        
        owner_name = input("👤 Owner's full name: ").strip()
        
        # Site type with suggestions
        print("\n💡 Site type suggestions: blog, shop, government, corporate, educational, news, forum")
        site_type = input("🏢 Site type: ").strip().lower()
        
        # CMS with suggestions
        print("\n💡 CMS suggestions: wordpress, joomla, drupal, magento, shopify, prestashop, opencart, typo3")
        cms = input("⚙️ CMS/Platform used: ").strip().lower()
        
        # Language with suggestions
        print("\n💡 Language suggestions: english, spanish, french, german, italian, portuguese, russian, chinese")
        language = input("🌍 Site language: ").strip().lower()
        
        # OSINT enrichment option
        print("\n🔍 OSINT Enrichment")
        print("-" * 20)
        enable_osint = input("Enable expert-level OSINT enrichment? (y/N): ").strip().lower() in ['y', 'yes']
        
        target_info = TargetInfo(
            url=url,
            domain=domain,
            subdomain=subdomain,
            owner_name=owner_name,
            site_type=site_type,
            cms=cms,
            language=language,
            enable_osint=enable_osint
        )
        
        print(f"\n✅ Configuration complete!")
        return target_info
    
    def perform_osint_enrichment(self, target_info: TargetInfo) -> None:
        """Perform comprehensive OSINT enrichment."""
        if not target_info.enable_osint:
            return
            
        print("\n🔍 Performing OSINT Enrichment...")
        print("=" * 40)
        
        # Check for missing dependencies
        missing_deps = []
        if not DNS_AVAILABLE:
            missing_deps.append("dnspython")
        if not WHOIS_AVAILABLE:
            missing_deps.append("python-whois")
        if not REQUESTS_AVAILABLE:
            missing_deps.append("requests")
            
        if missing_deps:
            print(f"⚠️ Some OSINT features unavailable. Missing: {', '.join(missing_deps)}")
            print("💡 Install with: pip install " + " ".join(missing_deps))
        
        try:
            # DNS reconnaissance
            if DNS_AVAILABLE:
                self._dns_reconnaissance(target_info)
            else:
                print("⚠️ DNS reconnaissance skipped (dnspython not available)")
            
            # WHOIS lookup
            if WHOIS_AVAILABLE:
                self._whois_lookup(target_info)
            else:
                print("⚠️ WHOIS lookup skipped (python-whois not available)")
            
            # Technology detection
            if REQUESTS_AVAILABLE:
                self._detect_technology_stack(target_info)
            else:
                print("⚠️ Technology detection skipped (requests not available)")
            
            print("✅ OSINT enrichment completed!")
            
        except Exception as e:
            self.logger.error(f"OSINT enrichment error: {e}")
            print(f"⚠️ OSINT enrichment partially failed: {e}")
    
    def _dns_reconnaissance(self, target_info: TargetInfo) -> None:
        """Perform DNS reconnaissance."""
        try:
            print("🔍 Performing DNS reconnaissance...")
            domain = target_info.domain
            
            # Common DNS record types
            record_types = ['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'NS']
            
            for record_type in record_types:
                try:
                    answers = dns.resolver.resolve(domain, record_type)
                    target_info.dns_records[record_type] = [str(answer) for answer in answers]
                except Exception:
                    continue
                    
            # Subdomain enumeration
            common_subdomains = ['www', 'admin', 'panel', 'cpanel', 'mail', 'ftp', 'dev', 'test', 'staging']
            found_subdomains = []
            
            for subdomain in common_subdomains:
                try:
                    full_domain = f"{subdomain}.{domain}"
                    dns.resolver.resolve(full_domain, 'A')
                    found_subdomains.append(full_domain)
                except Exception:
                    continue
                    
            if found_subdomains:
                target_info.dns_records['subdomains'] = found_subdomains
                print(f"  📡 Found subdomains: {', '.join(found_subdomains[:5])}")
                
        except Exception as e:
            self.logger.warning(f"DNS reconnaissance failed: {e}")
    
    def _whois_lookup(self, target_info: TargetInfo) -> None:
        """Perform WHOIS lookup for domain information."""
        try:
            print("🔍 Performing WHOIS lookup...")
            domain_info = whois.whois(target_info.domain)
            
            if domain_info:
                target_info.whois_info = {
                    'creation_date': str(domain_info.creation_date) if domain_info.creation_date else None,
                    'registrar': domain_info.registrar,
                    'name_servers': domain_info.name_servers,
                    'org': domain_info.org,
                    'country': domain_info.country
                }
                
                if domain_info.org:
                    print(f"  🏢 Organization: {domain_info.org}")
                if domain_info.country:
                    print(f"  🌍 Country: {domain_info.country}")
                    
        except Exception as e:
            self.logger.warning(f"WHOIS lookup failed: {e}")
    
    def _detect_technology_stack(self, target_info: TargetInfo) -> None:
        """Detect technology stack and CMS."""
        try:
            print("🔍 Detecting technology stack...")
            
            # Headers and response analysis
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(target_info.url, headers=headers, timeout=10, verify=False)
            
            # Server header analysis
            server = response.headers.get('Server', '')
            if server:
                target_info.server_info['server'] = server
                target_info.tech_stack.add(server.lower())
                print(f"  🖥️ Server: {server}")
            
            # CMS detection through headers and content
            cms_indicators = {
                'wordpress': ['wp-content', 'wp-includes', 'wp-json', 'wordpress'],
                'joomla': ['joomla', 'com_content', 'option=com_'],
                'drupal': ['drupal', 'sites/default', '/core/'],
                'magento': ['magento', 'skin/frontend', 'mage/cookies'],
                'shopify': ['shopify', 'cdn.shopify.com', 'shop_id'],
            }
            
            content = response.text.lower()
            headers_str = str(response.headers).lower()
            
            for cms, indicators in cms_indicators.items():
                if any(indicator in content or indicator in headers_str for indicator in indicators):
                    target_info.detected_cms = cms
                    target_info.tech_stack.add(cms)
                    print(f"  🎯 Detected CMS: {cms.title()}")
                    break
                    
            # Update CMS if not manually specified
            if not target_info.cms and target_info.detected_cms:
                target_info.cms = target_info.detected_cms
                
        except Exception as e:
            self.logger.warning(f"Technology detection failed: {e}")
    
    def generate_intelligent_paths(self, target_info: TargetInfo) -> List[str]:
        """Generate intelligent admin paths using ML and contextual analysis."""
        print("\n🧠 Generating Intelligent Admin Paths...")
        print("=" * 45)
        
        generated_paths = set()
        
        # Base admin paths
        generated_paths.update(self.base_admin_paths)
        
        # CMS-specific paths
        if target_info.cms:
            cms_paths = self.cms_paths.get(target_info.cms, [])
            generated_paths.update(cms_paths)
            print(f"  ⚙️ Added {len(cms_paths)} CMS-specific paths for {target_info.cms}")
        
        # Language-specific paths
        if target_info.language:
            lang_paths = self.language_paths.get(target_info.language, [])
            generated_paths.update(lang_paths)
            print(f"  🌍 Added {len(lang_paths)} language-specific paths for {target_info.language}")
        
        # Site type specific paths
        if target_info.site_type:
            type_paths = self.site_type_paths.get(target_info.site_type, [])
            generated_paths.update(type_paths)
            print(f"  🏢 Added {len(type_paths)} site-type specific paths for {target_info.site_type}")
        
        # Owner name variations
        if target_info.owner_name:
            name_paths = self._generate_name_based_paths(target_info.owner_name)
            generated_paths.update(name_paths)
            print(f"  👤 Added {len(name_paths)} name-based paths")
        
        # Subdomain-based paths
        if target_info.subdomain:
            subdomain_paths = self._generate_subdomain_paths(target_info.subdomain)
            generated_paths.update(subdomain_paths)
            print(f"  📡 Added {len(subdomain_paths)} subdomain-based paths")
        
        # OSINT-enhanced paths
        if target_info.enable_osint:
            osint_paths = self._generate_osint_paths(target_info)
            generated_paths.update(osint_paths)
            print(f"  🔍 Added {len(osint_paths)} OSINT-enhanced paths")
        
        # ML-enhanced path generation
        if ML_AVAILABLE:
            ml_paths = self._generate_ml_paths(target_info, list(generated_paths))
            generated_paths.update(ml_paths)
            print(f"  🤖 Added {len(ml_paths)} ML-generated paths")
        else:
            print(f"  🤖 ML path generation skipped (scikit-learn not available)")
        
        return list(generated_paths)
    
    def _generate_name_based_paths(self, owner_name: str) -> List[str]:
        """Generate paths based on owner's name."""
        if not owner_name:
            return []
            
        name_variations = []
        name_parts = owner_name.lower().split()
        
        # Individual name parts
        for part in name_parts:
            if len(part) > 2:  # Skip short parts
                name_variations.extend([
                    f"{part}admin", f"admin{part}", f"{part}_admin", f"admin_{part}",
                    f"{part}panel", f"panel{part}", f"{part}_panel", f"panel_{part}",
                    f"{part}", f"{part}_login", f"login_{part}"
                ])
        
        # First + last name combinations
        if len(name_parts) >= 2:
            first = name_parts[0]
            last = name_parts[-1]
            name_variations.extend([
                f"{first}{last}", f"{first}_{last}", f"{first}.{last}",
                f"{last}{first}", f"{last}_{first}", f"{last}.{first}",
                f"{first[0]}{last}", f"{first}{last[0]}"
            ])
        
        return name_variations
    
    def _generate_subdomain_paths(self, subdomain: str) -> List[str]:
        """Generate paths based on subdomain analysis."""
        if not subdomain:
            return []
            
        subdomain_parts = subdomain.split('.')
        subdomain_paths = []
        
        for part in subdomain_parts:
            if len(part) > 2:
                subdomain_paths.extend([
                    f"{part}/admin", f"{part}/panel", f"{part}/login",
                    f"admin/{part}", f"panel/{part}", f"login/{part}",
                    f"{part}_admin", f"{part}_panel", f"{part}_login"
                ])
        
        return subdomain_paths
    
    def _generate_osint_paths(self, target_info: TargetInfo) -> List[str]:
        """Generate paths based on OSINT findings."""
        osint_paths = []
        
        # Organization-based paths
        if target_info.whois_info.get('org'):
            org = target_info.whois_info['org'].lower()
            org_clean = re.sub(r'[^a-z0-9]', '', org)
            if org_clean:
                osint_paths.extend([
                    f"{org_clean}/admin", f"admin/{org_clean}",
                    f"{org_clean}_admin", f"admin_{org_clean}"
                ])
        
        # Technology stack based paths
        for tech in target_info.tech_stack:
            tech_clean = re.sub(r'[^a-z0-9]', '', tech.lower())
            if tech_clean and len(tech_clean) > 2:
                osint_paths.extend([
                    f"{tech_clean}/admin", f"admin/{tech_clean}",
                    f"{tech_clean}_panel", f"panel_{tech_clean}"
                ])
        
        # Subdomain-based admin paths
        if 'subdomains' in target_info.dns_records:
            for subdomain in target_info.dns_records['subdomains']:
                if 'admin' in subdomain or 'panel' in subdomain:
                    subdomain_name = subdomain.split('.')[0]
                    osint_paths.extend([f"{subdomain_name}", f"{subdomain_name}/"])
        
        return osint_paths
    
    def _generate_ml_paths(self, target_info: TargetInfo, existing_paths: List[str]) -> List[str]:
        """Generate ML-enhanced paths using semantic similarity."""
        if not ML_AVAILABLE:
            self.logger.info("ML path generation skipped - scikit-learn not available")
            return []
            
        try:
            # Create context string from all available information
            context_elements = [
                target_info.domain,
                target_info.subdomain,
                target_info.owner_name,
                target_info.site_type,
                target_info.cms,
                target_info.language,
                target_info.detected_cms
            ]
            
            context = ' '.join([elem for elem in context_elements if elem])
            
            if not context:
                return []
            
            # Vectorize context and knowledge base
            all_texts = [context] + self.path_knowledge_base
            
            # Fit and transform
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            # Calculate similarity between context and each path
            context_vector = tfidf_matrix[0:1]
            path_vectors = tfidf_matrix[1:]
            
            similarities = cosine_similarity(context_vector, path_vectors)[0]
            
            # Get top similar paths (not already in existing_paths)
            path_similarities = list(zip(self.path_knowledge_base, similarities))
            path_similarities.sort(key=lambda x: x[1], reverse=True)
            
            ml_paths = []
            for path, similarity in path_similarities:
                if similarity > 0.1 and path not in existing_paths:  # Threshold for relevance
                    ml_paths.append(path)
                    if len(ml_paths) >= 20:  # Limit ML suggestions
                        break
            
            return ml_paths
            
        except Exception as e:
            self.logger.warning(f"ML path generation failed: {e}")
            return []
    
    def rank_and_deduplicate_paths(self, paths: List[str], target_info: TargetInfo) -> List[str]:
        """Intelligently rank and deduplicate admin paths."""
        print("\n📊 Ranking and Deduplicating Paths...")
        print("=" * 40)
        
        # Remove duplicates while preserving order
        unique_paths = list(dict.fromkeys(paths))
        
        # Scoring system for path ranking
        scored_paths = []
        
        for path in unique_paths:
            score = self._calculate_path_score(path, target_info)
            scored_paths.append((path, score))
        
        # Sort by score (descending)
        scored_paths.sort(key=lambda x: x[1], reverse=True)
        
        # Extract paths
        ranked_paths = [path for path, score in scored_paths]
        
        print(f"  ✅ Processed {len(paths)} paths → {len(ranked_paths)} unique, ranked paths")
        
        return ranked_paths
    
    def _calculate_path_score(self, path: str, target_info: TargetInfo) -> float:
        """Calculate relevance score for a given path."""
        score = 0.0
        path_lower = path.lower()
        
        # Base score for common admin keywords
        admin_keywords = ['admin', 'administrator', 'administration', 'panel', 'control', 'manage']
        for keyword in admin_keywords:
            if keyword in path_lower:
                score += 10.0
        
        # CMS-specific scoring
        if target_info.cms and target_info.cms in path_lower:
            score += 15.0
        
        # Language-specific scoring
        if target_info.language:
            lang_paths = self.language_paths.get(target_info.language, [])
            if any(lang_path in path_lower for lang_path in lang_paths):
                score += 8.0
        
        # Site type specific scoring
        if target_info.site_type:
            type_paths = self.site_type_paths.get(target_info.site_type, [])
            if any(type_path in path_lower for type_path in type_paths):
                score += 12.0
        
        # Owner name scoring
        if target_info.owner_name:
            name_parts = target_info.owner_name.lower().split()
            for part in name_parts:
                if len(part) > 2 and part in path_lower:
                    score += 20.0  # High score for personalized paths
        
        # Penalize overly complex paths
        if len(path) > 50:
            score -= 5.0
        
        # Bonus for simple, clean paths
        if len(path) <= 15 and '/' not in path:
            score += 3.0
        
        # Penalty for suspicious characters
        if any(char in path for char in ['%', '&', '?', '#']):
            score -= 10.0
        
        return max(score, 0.0)  # Ensure non-negative score
    
    def save_results(self, paths: List[str], target_info: TargetInfo) -> None:
        """Save the generated admin paths to file with metadata."""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / "generated_admin_paths.txt"
        
        print(f"\n💾 Saving Results...")
        print("=" * 25)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                # Header with metadata
                f.write("# Smart Admin Finder - Generated Admin Paths\n")
                f.write("# ==========================================\n")
                f.write(f"# Target URL: {target_info.url}\n")
                f.write(f"# Domain: {target_info.domain}\n")
                f.write(f"# Subdomain: {target_info.subdomain or 'None'}\n")
                f.write(f"# Owner: {target_info.owner_name or 'Not specified'}\n")
                f.write(f"# Site Type: {target_info.site_type or 'Not specified'}\n")
                f.write(f"# CMS: {target_info.cms or 'Not specified'}\n")
                f.write(f"# Language: {target_info.language or 'Not specified'}\n")
                f.write(f"# OSINT Enabled: {target_info.enable_osint}\n")
                f.write(f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Total Paths: {len(paths)}\n")
                f.write("#\n")
                f.write("# Format: Each line contains a potential admin path\n")
                f.write("# Usage: Append these paths to your target URL\n")
                f.write("# Example: https://example.com/admin\n")
                f.write("#\n\n")
                
                # High-priority paths (top 50)
                f.write("# === HIGH PRIORITY PATHS (Top 50) ===\n")
                for i, path in enumerate(paths[:50], 1):
                    f.write(f"{path}\n")
                
                f.write("\n# === ADDITIONAL PATHS ===\n")
                for path in paths[50:]:
                    f.write(f"{path}\n")
                
                # Statistics
                f.write(f"\n# === STATISTICS ===\n")
                f.write(f"# Total unique paths generated: {len(paths)}\n")
                f.write(f"# High priority paths: {min(50, len(paths))}\n")
                f.write(f"# Additional paths: {max(0, len(paths) - 50)}\n")
            
            print(f"  ✅ Results saved to: {output_file}")
            print(f"  📊 Total paths generated: {len(paths)}")
            print(f"  🎯 High-priority paths: {min(50, len(paths))}")
            
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")
            print(f"  ❌ Failed to save results: {e}")
    
    def display_summary(self, paths: List[str], target_info: TargetInfo) -> None:
        """Display a comprehensive summary of the analysis."""
        print("\n📈 Analysis Summary")
        print("=" * 30)
        
        print(f"🎯 Target: {target_info.url}")
        print(f"📊 Total Paths Generated: {len(paths)}")
        
        if target_info.enable_osint:
            print("🔍 OSINT Analysis: ✅ Enabled")
            if target_info.detected_cms:
                print(f"  🎯 Detected CMS: {target_info.detected_cms.title()}")
            if target_info.tech_stack:
                print(f"  ⚙️ Tech Stack: {', '.join(target_info.tech_stack)}")
        else:
            print("🔍 OSINT Analysis: ❌ Disabled")
        
        # Show top 10 paths
        print(f"\n🏆 Top 10 Recommended Paths:")
        print("-" * 30)
        for i, path in enumerate(paths[:10], 1):
            full_url = urljoin(target_info.url, path)
            print(f"  {i:2d}. {path}")
            print(f"      → {full_url}")
        
        if len(paths) > 10:
            print(f"\n📋 ... and {len(paths) - 10} more paths in the output file")
        
        print(f"\n💡 Next Steps:")
        print(f"   1. Review the generated paths in output/generated_admin_paths.txt")
        print(f"   2. Use these paths responsibly for authorized security assessments")
        print(f"   3. Consider the high-priority paths first for better efficiency")
        
    def run(self) -> None:
        """Main execution flow of the Smart Admin Finder."""
        try:
            # Display banner
            self.display_banner()
            
            # Gather user input
            target_info = self.gather_user_input()
            
            # Perform OSINT if enabled
            self.perform_osint_enrichment(target_info)
            
            # Generate intelligent paths
            generated_paths = self.generate_intelligent_paths(target_info)
            
            # Rank and deduplicate
            final_paths = self.rank_and_deduplicate_paths(generated_paths, target_info)
            
            # Save results
            self.save_results(final_paths, target_info)
            
            # Display summary
            self.display_summary(final_paths, target_info)
            
            print("\n🎉 Smart Admin Finder completed successfully!")
            print("⚖️  Remember: Use these results responsibly and only for authorized security assessments.")
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Operation cancelled by user.")
            sys.exit(0)
        except Exception as e:
            self.logger.error(f"Critical error: {e}")
            print(f"\n❌ Critical error occurred: {e}")
            sys.exit(1)


def main():
    """Entry point for the Smart Admin Finder CLI tool."""
    parser = argparse.ArgumentParser(
        description="Smart Admin Finder - Expert-Level Admin Panel Discovery Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
  
For educational and ethical security assessment purposes only.
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Smart Admin Finder v1.0.0'
    )
    
    args = parser.parse_args()
    
    # Initialize and run the tool
    finder = SmartAdminFinder()
    finder.run()


if __name__ == "__main__":
    main()
