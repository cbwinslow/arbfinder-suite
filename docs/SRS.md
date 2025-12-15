# Software Requirements Specification (SRS)
# ArbFinder Suite

**Version**: 2.0  
**Date**: 2025-12-15  
**Status**: Active Development  
**Document Owner**: Product Team

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Overall Description](#2-overall-description)
3. [System Features](#3-system-features)
4. [External Interface Requirements](#4-external-interface-requirements)
5. [System Requirements](#5-system-requirements)
6. [Non-Functional Requirements](#6-non-functional-requirements)
7. [Appendices](#7-appendices)

---

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) describes the complete requirements for the ArbFinder Suite, a comprehensive price arbitrage finding and management system. The system analyzes prices across multiple online marketplaces, identifies profitable arbitrage opportunities, and provides tools for automated listing creation and cross-platform management.

**Intended Audience**:
- Development Team
- QA Team
- Product Managers
- Stakeholders
- External Contributors

### 1.2 Scope

**Product Name**: ArbFinder Suite  
**Product Vision**: Democratize arbitrage opportunities by providing enterprise-grade tools accessible to individual resellers and small businesses.

**Major Features**:
1. Multi-platform price crawling and comparison
2. AI-powered metadata enrichment and listing optimization
3. Automated arbitrage opportunity detection
4. Cross-platform listing management
5. Real-time price monitoring and alerts
6. Advanced analytics and reporting
7. Cloud-native deployment on Cloudflare platform

**Benefits**:
- Reduce time spent researching arbitrage opportunities
- Increase profit margins through better pricing
- Automate repetitive listing tasks
- Scale operations efficiently
- Make data-driven buying decisions

**Out of Scope**:
- Direct purchase automation (users must manually complete purchases)
- Payment processing for arbitrage deals
- Inventory management beyond listing tracking
- Tax calculation and compliance

### 1.3 Definitions, Acronyms, and Abbreviations

| Term | Definition |
|------|------------|
| **Arbitrage** | Buying items at low prices to resell at higher prices |
| **Comp** | Comparable - a similar item's sold price used for comparison |
| **Crawling** | Automated process of extracting data from websites |
| **Cross-listing** | Posting the same item on multiple platforms |
| **CrewAI** | AI agent orchestration framework |
| **D1** | Cloudflare's SQL database service |
| **R2** | Cloudflare's S3-compatible object storage |
| **Workers** | Cloudflare's serverless compute platform |
| **OpenRouter** | API aggregator for multiple LLM providers |
| **LangChain** | Framework for building LLM applications |
| **WAF** | Web Application Firewall |

### 1.4 References

- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)
- [CrewAI Documentation](https://docs.crewai.com/)
- [OpenRouter API Documentation](https://openrouter.ai/docs)
- [LangChain Documentation](https://python.langchain.com/)
- [Crawl4AI Documentation](https://crawl4ai.com/docs)

### 1.5 Overview

The remainder of this document describes:
- System architecture and components
- Functional and non-functional requirements
- Interface specifications
- Performance and security requirements
- Deployment and operational requirements

---

## 2. Overall Description

### 2.1 Product Perspective

ArbFinder Suite is a cloud-native web application deployed on Cloudflare's platform. It integrates with multiple external services:

**System Context**:
```
┌─────────────────────────────────────────────────────────────┐
│                     External Services                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  eBay    │  │ Reverb   │  │ Mercari  │  │OpenRouter│   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└────────┬───────────┬──────────────┬──────────────┬─────────┘
         │           │              │              │
         └───────────┴──────────────┴──────────────┘
                             │
         ┌───────────────────┴──────────────────┐
         │       Cloudflare Platform            │
         │  ┌──────────┐  ┌──────────┐         │
         │  │ Workers  │  │  Pages   │         │
         │  └──────────┘  └──────────┘         │
         │  ┌──────────┐  ┌──────────┐         │
         │  │    D1    │  │    R2    │         │
         │  └──────────┘  └──────────┘         │
         └──────────────────────────────────────┘
                             │
         ┌───────────────────┴──────────────────┐
         │      ArbFinder Suite Components      │
         │  ┌──────────┐  ┌──────────┐         │
         │  │ Backend  │  │ Frontend │         │
         │  │  (API)   │  │ (Next.js)│         │
         │  └──────────┘  └──────────┘         │
         │  ┌──────────┐  ┌──────────┐         │
         │  │  Agents  │  │ Crawler  │         │
         │  │ (CrewAI) │  │(Crawl4AI)│         │
         │  └──────────┘  └──────────┘         │
         └──────────────────────────────────────┘
                             │
         ┌───────────────────┴──────────────────┐
         │     Observability & Monitoring       │
         │  ┌──────────┐  ┌──────────┐         │
         │  │LangFuse  │  │LangSmith │         │
         │  └──────────┘  └──────────┘         │
         └──────────────────────────────────────┘
```

### 2.2 Product Functions

**Primary Functions**:

1. **Data Acquisition**
   - Crawl live listings from multiple marketplaces
   - Fetch sold comparable data
   - Extract product metadata and images
   
2. **Data Processing**
   - Normalize prices across currencies
   - Calculate condition-adjusted valuations
   - Identify arbitrage opportunities
   - Enrich metadata using AI
   
3. **Listing Management**
   - Generate optimized listing titles and descriptions
   - Create cross-platform listing payloads
   - Manage listing lifecycle
   
4. **Monitoring & Alerts**
   - Track price changes over time
   - Send notifications for high-value opportunities
   - Monitor inventory status
   
5. **Analytics & Reporting**
   - Display opportunity statistics
   - Generate profit projections
   - Track historical performance

### 2.3 User Classes and Characteristics

#### 2.3.1 Individual Resellers
- **Technical Expertise**: Low to Medium
- **Usage Frequency**: Daily
- **Key Needs**: Easy discovery of profitable items, simple listing tools
- **Priority**: High

#### 2.3.2 Small Business Operators
- **Technical Expertise**: Medium
- **Usage Frequency**: Multiple times daily
- **Key Needs**: Bulk operations, automation, analytics
- **Priority**: High

#### 2.3.3 Enterprise Users
- **Technical Expertise**: High
- **Usage Frequency**: Continuous
- **Key Needs**: API access, custom integrations, white-labeling
- **Priority**: Medium (future)

#### 2.3.4 Developers/Integrators
- **Technical Expertise**: High
- **Usage Frequency**: During development
- **Key Needs**: Comprehensive API documentation, SDKs
- **Priority**: Medium

### 2.4 Operating Environment

**Deployment Platform**: Cloudflare  
**Target Browsers**: Chrome, Firefox, Safari, Edge (latest 2 versions)  
**Mobile Support**: Responsive web design for tablets and phones  
**Geographic Distribution**: Global (multi-region support)

**Client Requirements**:
- Modern web browser with JavaScript enabled
- Internet connection (minimum 1 Mbps)
- Screen resolution: 1024x768 minimum, 1920x1080 recommended

**Server Requirements**:
- Cloudflare Workers (serverless)
- Cloudflare Pages (static hosting)
- Cloudflare D1 (database)
- Cloudflare R2 (object storage)

### 2.5 Design and Implementation Constraints

**Technical Constraints**:
- Must respect rate limits of external APIs
- Must comply with robots.txt and site terms of service
- Cloudflare Workers: 50ms CPU time limit per request
- D1 Database: 5 GB storage limit (free tier)
- R2 Storage: Unlimited storage, pay per operation

**Regulatory Constraints**:
- GDPR compliance for EU users
- CCPA compliance for California users
- Data retention policies
- Export control regulations

**Business Constraints**:
- Initial deployment on Cloudflare (potential VPS migration later)
- Minimize operational costs during early stages
- Use free AI models where possible (OpenRouter)

### 2.6 Assumptions and Dependencies

**Assumptions**:
- Target websites maintain current HTML structure
- External APIs remain available and stable
- Users have legitimate access to platforms they cross-list to
- OpenRouter free models provide adequate quality

**Dependencies**:
- Cloudflare platform availability (99.99% SLA)
- OpenRouter API availability
- Target marketplace API stability
- Browser compatibility with modern web standards
- Third-party library maintenance (CrewAI, LangChain, etc.)

---

## 3. System Features

### 3.1 Multi-Platform Price Crawling

**Priority**: Critical  
**Risk**: Medium (website changes can break crawlers)

#### 3.1.1 Description
The system shall crawl multiple online marketplaces to extract live listings and comparable sold data for price analysis.

#### 3.1.2 Functional Requirements

**FR-3.1.1**: The system shall support crawling the following platforms:
- ShopGoodwill.com
- GovDeals.com
- GovernmentSurplus.com
- eBay (via API and scraping for sold items)
- Reverb.com (planned)
- Mercari (planned)

**FR-3.1.2**: The system shall extract the following data from each listing:
- Title
- Price
- Currency
- Condition
- Images (URLs or download)
- Item location
- Seller information
- Timestamp

**FR-3.1.3**: The system shall implement rate limiting:
- Minimum 1 second delay between requests to same domain
- Respect robots.txt directives
- Implement exponential backoff on errors

**FR-3.1.4**: The system shall handle crawler failures gracefully:
- Retry failed requests up to 3 times
- Log all failures with context
- Continue processing remaining items
- Alert on sustained failures

**FR-3.1.5**: The system shall use Crawl4AI for intelligent crawling:
- AI-powered data extraction
- Adaptive parsing for layout changes
- Structured data output

#### 3.1.3 Input/Output

**Input**:
- Search query (string)
- Target providers (list)
- Filter criteria (price range, condition, location)

**Output**:
- List of listings with extracted metadata
- Crawl statistics (items found, errors, duration)
- Cached results for performance

### 3.2 AI-Powered Metadata Enrichment

**Priority**: High  
**Risk**: Low

#### 3.2.1 Description
The system shall use AI agents to enrich product metadata, improving data quality and searchability.

#### 3.2.2 Functional Requirements

**FR-3.2.1**: The system shall automatically fill missing metadata fields:
- Category classification
- Brand identification
- Model number extraction
- Specifications parsing
- Condition assessment

**FR-3.2.2**: The system shall enhance product titles:
- Standardize format across items
- Add relevant keywords for SEO
- Include key specifications
- Maintain brand and model accuracy

**FR-3.2.3**: The system shall use OpenRouter free models:
- Fetch list of available free models via API
- Automatically select best available model
- Fallback to alternative models on failure

**FR-3.2.4**: The system shall cache enrichment results:
- Store enriched data in database
- Avoid re-processing same items
- Update stale data periodically

**FR-3.2.5**: The system shall track enrichment quality:
- Log confidence scores
- Flag low-confidence enrichments for review
- Allow manual corrections

#### 3.2.3 Input/Output

**Input**:
- Raw product data (title, description, images)
- Product category (if known)

**Output**:
- Enriched metadata object
- Confidence scores per field
- Suggested improvements

### 3.3 Arbitrage Opportunity Detection

**Priority**: Critical  
**Risk**: Low

#### 3.3.1 Description
The system shall analyze prices across platforms to identify profitable arbitrage opportunities.

#### 3.3.2 Functional Requirements

**FR-3.3.1**: The system shall calculate potential profit:
- Compare live listing price to comparable sold prices
- Factor in platform fees and shipping costs
- Apply condition-based adjustments
- Calculate ROI percentage

**FR-3.3.2**: The system shall filter opportunities by threshold:
- User-configurable minimum ROI (default 20%)
- Minimum absolute profit amount
- Risk level (based on comparable count)

**FR-3.3.3**: The system shall rank opportunities:
- Sort by potential profit
- Sort by ROI percentage
- Sort by confidence level
- Sort by time remaining (for auctions)

**FR-3.3.4**: The system shall provide comparable data:
- Display recent sold prices
- Show price trends over time
- Indicate market velocity (how fast items sell)

**FR-3.3.5**: The system shall handle edge cases:
- Items with no comparables (flag as high risk)
- Outlier prices (exclude from average)
- Seasonal price variations

#### 3.3.3 Input/Output

**Input**:
- Live listings from crawler
- Comparable sold data
- User threshold settings
- Fee structures for platforms

**Output**:
- Ranked list of opportunities
- Profit calculations for each
- Risk indicators
- Comparable price charts

### 3.4 Automated Listing Creation

**Priority**: High  
**Risk**: Medium

#### 3.4.1 Description
The system shall generate optimized listing content for cross-platform posting.

#### 3.4.2 Functional Requirements

**FR-3.4.1**: The system shall generate listing titles:
- Platform-specific character limits
- SEO-optimized keywords
- Brand, model, and key specifications
- Condition indication

**FR-3.4.2**: The system shall generate descriptions:
- Template-based with customization
- Bullet point formatting
- Condition notes and disclosures
- Shipping and return policies

**FR-3.4.3**: The system shall suggest pricing:
- Recommended list price based on comps
- Minimum acceptable price (floor)
- Auto-accept offer threshold

**FR-3.4.4**: The system shall process images:
- Optimize for web (compress, resize)
- Generate thumbnails
- Upload to R2 storage
- Create CDN URLs

**FR-3.4.5**: The system shall generate platform-specific payloads:
- eBay API format
- Mercari CSV export
- Reverb API format
- Generic JSON for custom integrations

#### 3.4.3 Input/Output

**Input**:
- Product metadata
- Target platforms
- User preferences (templates, policies)
- Images (URLs or files)

**Output**:
- Complete listing content
- Platform-specific export files
- Pricing recommendations
- Preview rendering

### 3.5 Real-Time Monitoring and Alerts

**Priority**: Medium  
**Risk**: Low

#### 3.5.1 Description
The system shall monitor listings and prices continuously, alerting users to time-sensitive opportunities.

#### 3.5.2 Functional Requirements

**FR-3.5.1**: The system shall support watch mode:
- User defines search criteria
- System checks periodically (configurable interval)
- Alerts sent when new opportunities found

**FR-3.5.2**: The system shall support multiple alert channels:
- In-app notifications
- Email alerts
- SMS (future)
- Webhook integrations

**FR-3.5.3**: The system shall track price changes:
- Monitor watched items
- Alert on price drops
- Alert on auction ending soon

**FR-3.5.4**: The system shall implement smart alerts:
- Deduplicate notifications
- Batch low-priority alerts
- Prioritize high-value opportunities

#### 3.5.3 Input/Output

**Input**:
- User watch list definitions
- Alert preferences
- Notification settings

**Output**:
- Real-time alerts
- Alert history log
- Batch summary reports

### 3.6 Analytics and Reporting

**Priority**: Medium  
**Risk**: Low

#### 3.6.1 Description
The system shall provide insights into arbitrage performance and market trends.

#### 3.6.2 Functional Requirements

**FR-3.6.1**: The system shall display statistics:
- Total opportunities found
- Average potential profit
- Success rate (items sold vs listed)
- Platform comparison

**FR-3.6.2**: The system shall generate reports:
- Daily opportunity summary
- Weekly performance report
- Monthly financial summary
- Custom date ranges

**FR-3.6.3**: The system shall visualize trends:
- Price history charts
- Category performance
- Platform comparison
- Seasonal patterns

**FR-3.6.4**: The system shall export data:
- CSV export for Excel
- JSON export for integrations
- PDF reports for sharing

#### 3.6.3 Input/Output

**Input**:
- Historical listing data
- Transaction records
- Date range selection
- Filter criteria

**Output**:
- Interactive dashboards
- Generated reports (various formats)
- Chart visualizations
- Export files

### 3.7 Cloudflare Platform Integration

**Priority**: Critical  
**Risk**: Low

#### 3.7.1 Description
The system shall fully utilize Cloudflare platform services for scalability, performance, and security.

#### 3.7.2 Functional Requirements

**FR-3.7.1**: The system shall deploy Workers for API:
- RESTful API endpoints
- GraphQL support (future)
- WebSocket connections for real-time updates

**FR-3.7.2**: The system shall use D1 for database:
- Store listings and comparables
- User preferences and settings
- Analytics data
- Agent job queue

**FR-3.7.3**: The system shall use R2 for storage:
- Product images
- Generated reports
- Export files
- Backup data

**FR-3.7.4**: The system shall deploy Pages for frontend:
- Next.js static site generation
- Incremental static regeneration
- Edge rendering where appropriate

**FR-3.7.5**: The system shall configure WAF:
- DDoS protection
- Rate limiting per IP
- Bot management
- Geo-blocking (if needed)

**FR-3.7.6**: The system shall implement observability:
- Log aggregation
- Performance metrics
- Error tracking
- Distributed tracing

#### 3.7.3 Input/Output

**Input**:
- Configuration files
- Environment variables
- API keys and secrets

**Output**:
- Deployed services
- Monitoring dashboards
- Log streams
- Performance reports

---

## 4. External Interface Requirements

### 4.1 User Interfaces

#### 4.1.1 Web Application UI

**General Requirements**:
- Responsive design (mobile, tablet, desktop)
- Dark mode support
- Accessibility (WCAG 2.1 AA compliance)
- Progressive Web App (PWA) features

**Key Screens**:

1. **Dashboard**
   - Overview statistics
   - Recent opportunities
   - Active watches
   - Quick search

2. **Search Results**
   - Filterable table/grid view
   - Sort by multiple columns
   - Detailed view modal
   - Bulk action buttons

3. **Listing Creator**
   - Step-by-step wizard
   - Real-time preview
   - Template selection
   - Image upload/management

4. **Analytics Dashboard**
   - Interactive charts
   - Date range selector
   - Export options
   - Custom metrics

5. **Settings**
   - User preferences
   - API key management
   - Notification settings
   - Platform credentials

#### 4.1.2 Command Line Interface

**Requirements**:
- Full-featured CLI for power users
- Shell completion support
- JSON output mode
- Batch operation support

**Commands** (already implemented):
```bash
arbfinder search <query>
arbfinder watch <query>
arbfinder config
arbfinder db
arbfinder server
```

### 4.2 Hardware Interfaces

**None** - The system is entirely cloud-based with no direct hardware interfaces.

### 4.3 Software Interfaces

#### 4.3.1 External APIs

**eBay API**:
- **Purpose**: Fetch sold comparable data
- **Protocol**: REST over HTTPS
- **Authentication**: OAuth 2.0
- **Data Format**: JSON
- **Rate Limit**: 5000 calls/day (varies by tier)

**OpenRouter API**:
- **Purpose**: Access multiple LLM providers
- **Protocol**: REST over HTTPS
- **Authentication**: API Key
- **Data Format**: JSON
- **Rate Limit**: Depends on model and plan

**Crawl4AI** (if cloud-hosted):
- **Purpose**: Intelligent web scraping
- **Protocol**: REST over HTTPS
- **Authentication**: API Key
- **Data Format**: JSON

#### 4.3.2 Internal Services

**Cloudflare D1**:
- **Purpose**: Primary database
- **Protocol**: SQL over HTTP (Workers binding)
- **Authentication**: Automatic (binding)
- **Query Language**: SQL (SQLite-compatible)

**Cloudflare R2**:
- **Purpose**: Object storage
- **Protocol**: S3-compatible API
- **Authentication**: Access Key + Secret
- **Operations**: PUT, GET, DELETE, LIST

**Cloudflare Workers**:
- **Purpose**: Serverless API backend
- **Protocol**: HTTP/HTTPS
- **Deployment**: wrangler CLI

**Cloudflare Pages**:
- **Purpose**: Frontend hosting
- **Protocol**: Git-based deployment
- **Build**: Next.js build process

#### 4.3.3 Observability Services

**LangFuse**:
- **Purpose**: LLM observability and tracing
- **Protocol**: REST over HTTPS
- **Data Format**: JSON

**LangSmith**:
- **Purpose**: LangChain monitoring
- **Protocol**: REST over HTTPS
- **Data Format**: JSON

### 4.4 Communications Interfaces

**HTTP/HTTPS**:
- All API communication over HTTPS (TLS 1.3)
- REST API with JSON payloads
- WebSocket for real-time updates

**Email**:
- Transactional emails via Cloudflare Email Workers
- Alert notifications
- Reports delivery

**Webhooks**:
- Outbound webhooks for integrations
- Configurable endpoints
- Retry logic with exponential backoff

---

## 5. System Requirements

### 5.1 Functional Requirements Summary

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-1 | Multi-platform price crawling | Critical | ✅ Implemented |
| FR-2 | AI metadata enrichment | High | 🚧 In Progress |
| FR-3 | Arbitrage detection | Critical | ✅ Implemented |
| FR-4 | Listing generation | High | 🚧 In Progress |
| FR-5 | Monitoring and alerts | Medium | 📋 Planned |
| FR-6 | Analytics and reporting | Medium | ✅ Implemented |
| FR-7 | Cloudflare integration | Critical | 🚧 In Progress |
| FR-8 | User authentication | High | 📋 Planned |
| FR-9 | API access | Medium | ✅ Implemented |
| FR-10 | Mobile responsiveness | High | ✅ Implemented |

---

## 6. Non-Functional Requirements

### 6.1 Performance Requirements

**NFR-6.1.1**: Response Time
- API endpoints: p95 < 500ms, p99 < 1000ms
- Page load: First Contentful Paint < 1.5s
- Search results: Display within 2 seconds
- Batch operations: Progress indicator for >5 second operations

**NFR-6.1.2**: Throughput
- Support 100 concurrent users minimum
- Process 1000 listings per minute
- Handle 10,000 API requests per hour

**NFR-6.1.3**: Scalability
- Horizontal scaling via Cloudflare Workers
- Database sharding strategy defined
- CDN caching for static assets
- Edge computing for low latency globally

**NFR-6.1.4**: Resource Utilization
- Workers CPU time < 30ms per request (avg)
- D1 database queries < 100ms (p95)
- R2 storage optimized for cost
- Image compression to reduce bandwidth

### 6.2 Safety Requirements

**NFR-6.2.1**: Data Backup
- Daily automated backups of D1 database
- R2 bucket versioning enabled
- 30-day retention for deleted data
- Backup restoration tested monthly

**NFR-6.2.2**: Failure Recovery
- Automatic retry for transient failures
- Circuit breaker for failing services
- Graceful degradation when services unavailable
- Health checks for all critical services

**NFR-6.2.3**: Error Handling
- All errors logged with context
- User-friendly error messages
- No sensitive data in error responses
- Automatic alerting for critical errors

### 6.3 Security Requirements

**NFR-6.3.1**: Authentication
- Secure user authentication (OAuth 2.0 or JWT)
- Multi-factor authentication (MFA) support
- Password strength requirements
- Session management with timeout

**NFR-6.3.2**: Authorization
- Role-based access control (RBAC)
- API key management for programmatic access
- Principle of least privilege
- Audit logging for sensitive operations

**NFR-6.3.3**: Data Protection
- Encryption at rest (R2 buckets, D1 database)
- Encryption in transit (TLS 1.3 only)
- PII data handling per GDPR/CCPA
- Secure secret management (Cloudflare secrets)

**NFR-6.3.4**: Network Security
- WAF rules for common attacks (SQLi, XSS, etc.)
- DDoS protection via Cloudflare
- Rate limiting per IP and user
- IP allowlist/blocklist support

**NFR-6.3.5**: Application Security
- Input validation and sanitization
- Output encoding to prevent XSS
- CSRF protection
- Security headers (CSP, HSTS, etc.)
- Dependency vulnerability scanning

### 6.4 Software Quality Attributes

**NFR-6.4.1**: Reliability
- 99.9% uptime SLA (excluding maintenance)
- Mean Time Between Failures (MTBF) > 720 hours
- Mean Time To Recovery (MTTR) < 15 minutes

**NFR-6.4.2**: Availability
- 24/7 operation
- Scheduled maintenance windows announced 48h advance
- Redundancy across Cloudflare regions

**NFR-6.4.3**: Maintainability
- Code coverage > 80%
- Comprehensive documentation
- Modular architecture
- Automated deployment pipelines

**NFR-6.4.4**: Portability
- Platform-agnostic where possible
- Docker containers for local development
- Infrastructure as Code (Pulumi/Terraform)
- Standard APIs for easy migration

**NFR-6.4.5**: Usability
- Intuitive UI requiring minimal training
- Consistent design language
- Keyboard shortcuts for power users
- Help documentation and tutorials

**NFR-6.4.6**: Testability
- Unit tests for all business logic
- Integration tests for API endpoints
- End-to-end tests for critical workflows
- Performance tests for scalability validation

### 6.5 Business Rules

**BR-6.5.1**: Data Retention
- User data retained until account deletion
- Deleted accounts purged after 30 days
- Analytics data aggregated and anonymized after 1 year

**BR-6.5.2**: Fair Use Policy
- Rate limiting to prevent abuse
- No scraping of the application itself
- No automated account creation
- Compliance with upstream API terms

**BR-6.5.3**: Pricing and Plans
- Free tier with limited features
- Paid plans for enhanced features and limits
- Educational discounts available
- No hidden fees

---

## 7. Appendices

### 7.1 Glossary

*See Section 1.3 for definitions*

### 7.2 Analysis Models

#### 7.2.1 Use Case Diagram

```
                    ┌─────────────────┐
                    │  Search Items   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
     ┌──────────────┤  User           │──────────────┐
     │              └─────────────────┘              │
     │                                                │
┌────▼─────────┐                          ┌─────────▼────────┐
│ View Results │                          │ Create Listings  │
└──────────────┘                          └──────────────────┘
     │                                                │
┌────▼─────────┐                          ┌─────────▼────────┐
│ Set Watches  │                          │ View Analytics   │
└──────────────┘                          └──────────────────┘
```

#### 7.2.2 Data Flow Diagram

```
User Query → Crawler → Raw Data → Validator → Clean Data
                                                    │
                                                    ▼
                                            Enrichment Agent
                                                    │
                                                    ▼
                                            Enriched Data
                                                    │
                                    ┌───────────────┴───────────────┐
                                    │                               │
                                    ▼                               ▼
                            Arbitrage Analyzer              Database Storage
                                    │                               │
                                    ▼                               ▼
                            Opportunities List                  API Access
                                    │                               │
                                    └───────────────┬───────────────┘
                                                    ▼
                                                User Interface
```

### 7.3 Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-01-15 | Initial Team | Initial draft |
| 1.5 | 2024-06-01 | Dev Team | Added CrewAI integration |
| 2.0 | 2025-12-15 | Dev Team | Cloudflare platform, OpenRouter, comprehensive update |

### 7.4 Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Owner | TBD | _________ | _____ |
| Lead Developer | TBD | _________ | _____ |
| QA Lead | TBD | _________ | _____ |
| Security Officer | TBD | _________ | _____ |

---

**Document Status**: APPROVED FOR IMPLEMENTATION  
**Next Review Date**: 2025-03-15  
**Distribution**: Development Team, Stakeholders
