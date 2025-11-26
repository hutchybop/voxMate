# voxMate Agent Guidelines

## Build/Test Commands
- **Install dependencies**: `pip install -r requirements.txt`
- **Run main app**: `python3 voxMate_app/main.py`
- **Run web app**: `cd voxMate_web_app && flask run`
- **No test framework detected** - add pytest if needed

## Code Style Guidelines

### Import Organization
- Standard library imports first (os, sys, time, etc.)
- Third-party imports second (openai, flask, pymongo, etc.)
- Local imports last (utils.*, config.*, services.*)
- Use absolute imports for local modules

### Formatting & Types
- Use type hints for function signatures: `def func(param: str) -> Optional[str]:`
- Maximum line length: ~100 characters
- Use f-strings for string formatting
- Constants in UPPER_SNAKE_CASE

### Naming Conventions
- Classes: PascalCase (`AIService`, `AudioProcessor`)
- Functions/variables: snake_case (`transcribe_audio`, `audio_file`)
- Private methods: prefix with underscore (`_private_method`)
- File names: snake_case

### Error Handling
- Use specific exception handling with logging
- Log errors using the `logger` instance from utils.logging
- Return tuples for success/failure: `(success: bool, message: str)`

### Environment & Config
- All secrets in .env file, never hardcoded
- Use config.settings for configuration values
- Check environment variables before use

### Project Structure
- Main app in voxMate_app/, web app in voxMate_web_app/
- Services in services/, utilities in utils/
- Configuration in config/, actions in actions/