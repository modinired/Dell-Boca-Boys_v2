"""
Code utility tools for Vito agent
"""

import os
import re
import ast
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import subprocess

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """Analyze code structure and extract information"""

    @staticmethod
    def analyze_python_file(file_path: str) -> Dict[str, Any]:
        """
        Analyze Python file structure

        Returns:
            Dict with classes, functions, imports, etc.
        """

        try:
            with open(file_path, 'r') as f:
                content = f.read()

            tree = ast.parse(content)

            analysis = {
                "file_path": file_path,
                "language": "python",
                "classes": [],
                "functions": [],
                "imports": [],
                "docstring": ast.get_docstring(tree),
                "lines_of_code": len(content.split('\n'))
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    analysis["classes"].append({
                        "name": node.name,
                        "lineno": node.lineno,
                        "methods": [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                        "docstring": ast.get_docstring(node)
                    })

                elif isinstance(node, ast.FunctionDef):
                    # Only top-level functions
                    if isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                        analysis["functions"].append({
                            "name": node.name,
                            "lineno": node.lineno,
                            "args": [arg.arg for arg in node.args.args],
                            "docstring": ast.get_docstring(node)
                        })

                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis["imports"].append(alias.name)
                    else:
                        module = node.module or ""
                        for alias in node.names:
                            analysis["imports"].append(f"{module}.{alias.name}")

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing Python file {file_path}: {e}")
            return {"error": str(e)}

    @staticmethod
    def extract_functions(code: str, language: str) -> List[str]:
        """Extract function names from code"""

        functions = []

        if language == "python":
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        functions.append(node.name)
            except:
                # Fallback to regex
                functions = re.findall(r'def\s+(\w+)\s*\(', code)

        elif language in ["javascript", "typescript"]:
            # Match function declarations and arrow functions
            patterns = [
                r'function\s+(\w+)\s*\(',
                r'const\s+(\w+)\s*=\s*\(',
                r'(\w+)\s*=\s*\([^)]*\)\s*=>',
            ]
            for pattern in patterns:
                functions.extend(re.findall(pattern, code))

        return functions

    @staticmethod
    def count_lines(code: str, exclude_comments: bool = False) -> int:
        """Count lines of code"""

        lines = code.split('\n')

        if not exclude_comments:
            return len(lines)

        # Count only non-comment, non-blank lines
        code_lines = 0
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and not stripped.startswith('//'):
                code_lines += 1

        return code_lines

    @staticmethod
    def calculate_complexity(code: str, language: str) -> int:
        """
        Calculate cyclomatic complexity (simplified)

        Counts decision points: if, for, while, etc.
        """

        if language == "python":
            keywords = ['if', 'elif', 'for', 'while', 'and', 'or', 'except']
        elif language in ["javascript", "typescript"]:
            keywords = ['if', 'for', 'while', '&&', '||', 'case', 'catch']
        else:
            keywords = ['if', 'for', 'while']

        complexity = 1  # Base complexity

        for keyword in keywords:
            # Count occurrences
            complexity += len(re.findall(rf'\b{keyword}\b', code))

        return complexity


class CodeFormatter:
    """Format code according to language standards"""

    @staticmethod
    def format_python(code: str) -> str:
        """Format Python code using black (if available)"""

        try:
            import black

            mode = black.Mode(
                line_length=88,
                string_normalization=True
            )

            formatted = black.format_str(code, mode=mode)
            return formatted

        except ImportError:
            logger.warning("black not installed, skipping formatting")
            return code

        except Exception as e:
            logger.error(f"Error formatting Python code: {e}")
            return code

    @staticmethod
    def format_javascript(code: str) -> str:
        """Format JavaScript code using prettier (if available)"""

        try:
            # Check if prettier is available
            result = subprocess.run(
                ['prettier', '--parser', 'babel', '--stdin-filepath', 'code.js'],
                input=code.encode(),
                capture_output=True,
                timeout=10
            )

            if result.returncode == 0:
                return result.stdout.decode()
            else:
                logger.warning("prettier formatting failed")
                return code

        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("prettier not available")
            return code

        except Exception as e:
            logger.error(f"Error formatting JavaScript: {e}")
            return code


class ProjectScanner:
    """Scan project structure"""

    @staticmethod
    def scan_directory(
        directory: str,
        extensions: Optional[List[str]] = None,
        exclude_dirs: Optional[List[str]] = None
    ) -> List[str]:
        """
        Scan directory for code files

        Args:
            directory: Directory to scan
            extensions: File extensions to include (e.g., ['.py', '.js'])
            exclude_dirs: Directories to exclude

        Returns:
            List of file paths
        """

        if exclude_dirs is None:
            exclude_dirs = [
                'node_modules', '__pycache__', '.git', '.venv',
                'venv', 'build', 'dist', '.pytest_cache'
            ]

        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.go', '.rs']

        files = []

        for root, dirs, filenames in os.walk(directory):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for filename in filenames:
                if any(filename.endswith(ext) for ext in extensions):
                    files.append(os.path.join(root, filename))

        return files

    @staticmethod
    def analyze_project_structure(directory: str) -> Dict[str, Any]:
        """
        Analyze project structure

        Returns:
            Dict with project info
        """

        files = ProjectScanner.scan_directory(directory)

        # Count by language
        language_counts = {}
        total_lines = 0

        for file_path in files:
            ext = Path(file_path).suffix
            language_counts[ext] = language_counts.get(ext, 0) + 1

            # Count lines
            try:
                with open(file_path, 'r') as f:
                    total_lines += len(f.readlines())
            except:
                pass

        return {
            "directory": directory,
            "total_files": len(files),
            "languages": language_counts,
            "total_lines": total_lines,
            "files": files
        }


class CodeExtractor:
    """Extract code snippets and patterns"""

    @staticmethod
    def extract_code_blocks(text: str) -> List[Tuple[str, str]]:
        """
        Extract code blocks from markdown-style text

        Returns:
            List of (language, code) tuples
        """

        # Match ```language\ncode\n```
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)

        code_blocks = []
        for language, code in matches:
            language = language or "unknown"
            code_blocks.append((language, code.strip()))

        return code_blocks

    @staticmethod
    def wrap_in_code_block(code: str, language: str = "") -> str:
        """Wrap code in markdown code block"""
        return f"```{language}\n{code}\n```"

    @staticmethod
    def extract_imports(code: str, language: str) -> List[str]:
        """Extract import statements"""

        imports = []

        if language == "python":
            # Match import and from...import
            patterns = [
                r'import\s+([\w., ]+)',
                r'from\s+([\w.]+)\s+import'
            ]
            for pattern in patterns:
                imports.extend(re.findall(pattern, code))

        elif language in ["javascript", "typescript"]:
            # Match ES6 imports
            patterns = [
                r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
                r'require\([\'"]([^\'"]+)[\'"]\)'
            ]
            for pattern in patterns:
                imports.extend(re.findall(pattern, code))

        return imports


def detect_language_from_file(file_path: str) -> str:
    """Detect programming language from file path"""

    ext_map = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php",
        ".swift": "swift",
        ".kt": "kotlin",
    }

    ext = Path(file_path).suffix.lower()
    return ext_map.get(ext, "unknown")
