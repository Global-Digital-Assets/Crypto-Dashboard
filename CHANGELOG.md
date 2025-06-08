# Changelog

All notable changes to the Crypto Trading Dashboard will be documented in this file.

## [1.0.0] - 2025-06-08

### Added
- **Initial Production Release** 🚀
- Real-time crypto trading dashboard with FastAPI backend
- Integration with `/api/analysis` endpoint (single source of truth)
- Live signal processing with score percentage conversion
- Service health monitoring for bot and analytics APIs
- Responsive web interface with auto-refresh functionality
- Support for 30 crypto tokens with trading signals
- UTC timestamp tracking for data freshness monitoring
- Signal mapping: `side` → action, `proba` → score percentage
- Take profit (tp) and stop loss (sl) data ready for future use

### Technical Details
- **Backend**: FastAPI with async HTTP client (httpx)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Data Format**: `{symbol, side, proba, tp, sl, timestamp}`
- **Deployment**: VPS (78.47.150.122:9999) - Production Ready
- **API Sources**: Analytics (port 8080) + Bot Health (port 8000)
- **Update Frequency**: 15-minute analytics cycle with real-time dashboard refresh

### Security & Best Practices
- Environment variables for configuration
- Comprehensive .gitignore for sensitive files
- SSH keys excluded from version control
- Type-safe Python code with proper error handling
- Read-only access to production APIs

---

**Legend**: 🚀 Major Release | ✨ New Feature | 🐛 Bug Fix | 📝 Documentation | ⚡ Performance
