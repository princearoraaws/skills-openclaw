# Sleep Rabbit - Sleep Health Analysis Skill

## Overview
Sleep Rabbit is a professional sleep health analysis system for OpenClaw, providing sleep analysis, stress assessment, and personalized meditation guidance.

## Features

### Core Features
- **Sleep Analysis**: Analyze EDF sleep data files
- **Stress Assessment**: HRV-based stress evaluation from heart rate data
- **Meditation Guidance**: Personalized meditation techniques and guidance
- **Health Reporting**: Comprehensive health reports and recommendations

### Security Features
- 100% local operation, no network access
- No shell commands or subprocess calls
- Strict path validation and restriction
- Privacy-friendly local processing

## Installation

### Method 1: Copy to OpenClaw Skills Directory
```bash
# Copy the skill directory to OpenClaw skills folder
cp -r AISleepGen/ ~/.openclaw/skills/
```

### Method 2: Use OpenClaw Skill Install
```bash
# Install from extracted directory
openclaw skill install ./AISleepGen
```

## Usage

### Basic Commands
- `/sleep-analyze <edf-file>`: Analyze EDF sleep data (requires MNE)
- `/stress-check <hr-data>`: Stress assessment from heart rate data
- `/meditation-guide`: Get personalized meditation guidance
- `/file-info <file>`: File system analysis and validation
- `/env-check`: Environment diagnostics and dependency checking

### Environment Requirements

#### Basic Mode (Out of the Box)
- Python 3.8+
- Standard library only
- File verification and basic analysis

#### Advanced Mode (With MNE)
- `pip install mne numpy scipy`
- Full EDF sleep data analysis
- Professional HRV stress assessment

## Configuration

### Security Configuration (config.yaml)
```yaml
security:
  network_access: false
  local_only: true
  privacy_friendly: true
  no_external_dependencies: true
  python_stdlib_only: true
  no_shell_commands: true
```

### Skill Information
- **Name**: Sleep Rabbit Sleep Health
- **Version**: 1.0.6
- **Author**: AISleepGen Team
- **License**: MIT
- **OpenClaw Min Version**: 2026.3.0

## Quality Assurance

### Security Compliance
- ✅ No network code, 100% local operation
- ✅ No dangerous imports or system calls
- ✅ Complete security declarations in config.yaml
- ✅ Path validation and restriction

### Documentation
- ✅ Complete English documentation
- ✅ Clear usage instructions
- ✅ Security and privacy documentation
- ✅ Installation and configuration guides

### Testing
- ✅ Structure testing passed
- ✅ Security compliance verified
- ✅ ClawHub standards met
- ✅ Documentation consistency verified

## File Structure
```
AISleepGen/
├── skill.py              # Main skill implementation
├── config.yaml           # Configuration with security declarations
├── package.json          # Package metadata
├── CHANGELOG.md          # Version history (English)
├── README.md             # This file
├── SKILL.md              # Skill documentation
├── INTEGRATION_GUIDE.md  # Integration guide
├── PLUGIN_USAGE.md       # Plugin usage guide
├── examples/             # Usage examples
└── backup_md_files/      # Backup of original Chinese docs
```

## Support

### Issues and Questions
- Check the documentation first
- Review the examples directory
- Verify environment requirements

### Dependencies
- **Basic**: Python 3.8+ standard library
- **Advanced**: MNE-Python, NumPy, SciPy (optional)

## License
MIT License - See LICENSE file for details

## Version
Current Version: 1.0.6
Last Updated: 2026-03-29