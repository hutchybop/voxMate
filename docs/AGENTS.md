# voxMate Agent Guidelines

## Build/Test Commands
- **Install dependencies**: `pip install -r requirements.txt`
- **Run main app**: `cd voxMate_app && python3 main.py` (or use `./run_voxMate.sh`)
- **Run web app**: `cd voxMate_web_app && flask run` (or use `./start_voxMate_web_app.sh`)
- **Run single test**: `python3 testing/test_lights.py` (no test framework - direct execution)
- **Stop apps**: `./stop_voxMate.sh`

## Code Style Guidelines

### Import Organization
- Standard library imports first (os, sys, time, pathlib, etc.)
- Third-party imports second (openai, flask, pymongo, gtts, etc.)
- Local imports last (utils.logging, config.settings, services.*)
- Use `from pathlib import Path` for file paths
- Load .env with `load_dotenv()` early in files

### Formatting & Types
- Use type hints: `def func(param: str) -> Optional[str]:`
- Maximum line length: ~100 characters
- Use f-strings for string formatting
- Constants in UPPER_SNAKE_CASE (DEFAULT_CONFIG, ENV_CHECKS)
- Use `Path(__file__).resolve().parent` for relative paths

### Naming Conventions
- Classes: PascalCase (`AIService`, `AudioProcessor`, `MicLights`)
- Functions/variables: snake_case (`transcribe_audio`, `audio_file`)
- Private methods: prefix with underscore (`_send_frame`, `_private_method`)
- File names: snake_case

### Error Handling
- Use specific exception handling with logging via `utils.logging.logger`
- Return tuples for success/failure: `(success: bool, message: str)`
- Critical errors should `sys.exit(1)` after logging
- Use try/finally for cleanup (temp files, resources)

### Environment & Config
- All secrets in .env file, never hardcoded
- Use `config.settings` module for configuration values
- Check environment variables with `settings.check_environment()`
- MongoDB config loaded from both user files and database

### Project Structure
- Main app in `voxMate_app/`, web app in `voxMate_web_app/`
- Services in `services/`, utilities in `utils/`
- Configuration in `config/`, actions in `actions/`
- Models in `models/`, interfaces in `interfaces/`