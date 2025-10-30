# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of DataWareHouse library
- Complete SQLite-based data warehouse for video processing evaluation systems
- Comprehensive API with 80+ functions for data management
- CLI tool (`dwh-cli`) for database operations
- Full type hints and error handling
- Extensive documentation and examples

### Features
- **Task Management**: Create, read, update, delete tasks with tagging system
- **Subject Management**: Manage test subjects and their video data
- **Video Management**: Store and organize video metadata
- **Version Control**: Track core library and algorithm versions with Git integration
- **Output Management**: Manage processing results and evaluation data
- **Search & Analytics**: Advanced search and statistical analysis functions
- **Data Integrity**: Foreign key constraints and validation
- **Connection Management**: Context managers for safe database operations

## [0.1.0] - 2025-09-17

### Added
- Initial public release
- Core data warehouse functionality
- All database tables and relationships
- Complete API function set
- CLI interface
- Documentation and examples
- Package configuration for PyPI distribution

### Technical Details
- **Database**: SQLite3 with foreign key constraints
- **Python Support**: Python 3.10+
- **Dependencies**: None (uses only standard library)
- **License**: MIT License
- **Build System**: Hatchling

### Database Schema
- 13 core tables covering all aspects of video processing evaluation
- Self-referencing tables for version history tracking
- Comprehensive indexing for performance
- Foreign key relationships for data integrity

### API Coverage
- **Connection Management**: 2 functions
- **Task Management**: 5 functions
- **Subject Management**: 6 functions
- **Video Management**: 6 functions
- **Tag Management**: 8 functions
- **Core Library Management**: 6 functions
- **Core Library Output**: 3 functions
- **Algorithm Management**: 7 functions
- **Algorithm Output**: 3 functions
- **Search & Analytics**: 6 functions
- **Evaluation Management**: 6 functions
- **Analysis Management**: 9 functions
- **Total**: 80+ functions

### CLI Features
- Database creation and initialization
- Database structure inspection
- Help system with usage examples

### Documentation
- Comprehensive README with installation and usage guides
- API reference documentation
- Code examples for basic and advanced usage
- Architecture overview and schema documentation
