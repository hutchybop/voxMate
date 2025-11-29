# voxMate Development Guidelines

## Build/Lint/Test Commands
- **Lint**: `flake8 .` (max line length: 88)
- **Format**: `black .` (line length: 88, target Python 3.8+)
- **Run single test**: `python testing/test_lights.py`
- **Run main app**: `python voxMate_app/main.py`
- **Run web app**: `python voxMate_web_app/app.py`

## Code Style Guidelines

### Imports & Formatting
- Standard imports first, then third-party, then local imports
- Use type hints consistently (see `typing.Tuple`, `typing.Optional`)
- Line length: 88 characters (Black/Flake8 standard)
- Use Black formatter with Python 3.8+ compatibility

### Naming Conventions
- Classes: PascalCase (`AIService`, `MicLights`)
- Functions/variables: snake_case (`transcribe_audio`, `audio_path`)
- Constants: UPPER_SNAKE_CASE (`GROQ_API_KEY`, `DEFAULT_VOLUME`)
- Private methods: prefix with underscore (`_send_frame`)

### Error Handling
- Use try/except blocks with specific exception types
- Log errors using `utils.logging.logger`
- Raise exceptions in critical functions, handle in calling code
- Use `Optional[T]` return types for functions that may return None

### Type Hints
- All public methods should have type hints
- Use `Tuple[bool, Optional[str]]` for action handlers
- Use `Optional[Dict[str, Any]]` for configuration functions
- Import from `typing` module consistently

### Project Structure
- Main app: `voxMate_app/` (voice assistant)
- Web app: `voxMate_web_app/` (Flask interface)
- Services in `services/`, handlers in `actions/handlers/`
- Shared utilities in `utils/`
- Configuration in `config/`