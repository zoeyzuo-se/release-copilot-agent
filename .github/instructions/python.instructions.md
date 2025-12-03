---
description: 'Python coding conventions and guidelines'
applyTo: '**/*.py'
---
 
# Python Coding Conventions
 
Style guide based on Google Python Style Guide: https://google.github.io/styleguide/pyguide.html
 
## Python Instructions
 
- Write clear and concise comments for each function.
- Ensure functions have descriptive names and include type hints.
- Provide docstrings following the Google Python Style Guide (https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).
- Use built-in type annotations (e.g., `list[str]`, `dict[str, int]`) as supported in Python 3.9+. For older typing features, use the `typing` module when necessary.
- Break down complex functions into smaller, more manageable functions.
 
## General Instructions
 
- Always prioritize readability and clarity.
- For algorithm-related code, include explanations of the approach used.
- Write code with good maintainability practices, including comments on why certain design decisions were made.
- Handle edge cases and write clear exception handling.
- For libraries or external dependencies, mention their usage and purpose in comments.
- Use consistent naming conventions and follow language-specific best practices.
- Write concise, efficient, and idiomatic code that is also easily understandable.
 
## Code Style and Formatting
 
- Follow the Google (https://google.github.io/styleguide/pyguide.html) style guide for Python.
- Generated code should follow best practices recommended by  tools like \*\*ruff\*\*, \*\*black\*\*, \*\*isort\*\*, \*\*flake8\*\*, \*\*yapf\*\*, \*\*mypy\*\* to ensure code quality.
- Maintain proper indentation (use 4 spaces for each level of indentation).
- Ensure lines do not exceed 88 characters.
- Place function and class docstrings immediately after the `def` or `class` keyword.
- Use blank lines to separate functions, classes, and code blocks where appropriate.
- Avoid using `Any` as return type (https://mypy.readthedocs.io/en/stable/kinds_of_types.html#the-any-type), prefer explicit types or, at least, use `object`
- When introducing a pydantic model, please use the Annotated Pattern (https://docs.pydantic.dev/latest/concepts/fields/#the-annotated-pattern).
 
## Edge Cases and Testing
 
- Always include test cases for critical paths of the application.
- Account for common edge cases like empty inputs, invalid data types, and large datasets.
- Include comments for edge cases and the expected behavior in those cases.
- Write unit tests for functions with descriptive names that clearly explain what is being tested.
- **Test Function Documentation**: Docstrings are NOT required for test functions/methods (only for test modules and classes). Test function/method names should be descriptive (even if they need to be quite long) to make it clear what happened when viewing a test report.
 
## Error Handling and Logging
 
- Use exceptions to handle errors gracefully. For example, use `fastapi.responses` for API responses.
- Use specific exception types rather than generic ones.
- Include logging statements to capture important events, using different levels of logging (e.g., `debug`, `info`, `warning`, `error`).
 
## Example of Proper Documentation
 
```python
 
import math
 
def calculate_area(radius: float) -> float:
    """Calculate the area of a circle given the radius.
    Args:
        radius: The radius of the circle.
    Returns:
        The area of the circle, calculated as π * radius^2.
    """
    return math.pi * radius ** 2
```