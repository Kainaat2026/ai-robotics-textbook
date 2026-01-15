"""
Setup Verification Script

Checks that all prerequisites are configured correctly before running
migrations and quiz generation.

Usage:
    python scripts/verify_setup.py
"""

import sys
import os
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_status(check_name: str, status: bool, message: str = ""):
    """Print status with color coding."""
    icon = f"{Colors.GREEN}✓{Colors.ENDC}" if status else f"{Colors.RED}✗{Colors.ENDC}"
    status_text = f"{Colors.GREEN}OK{Colors.ENDC}" if status else f"{Colors.RED}FAILED{Colors.ENDC}"
    print(f"{icon} {check_name}: {status_text}")
    if message:
        indent = "  "
        print(f"{indent}{Colors.YELLOW}{message}{Colors.ENDC}")


async def check_database():
    """Check database connection."""
    try:
        import asyncpg
        database_url = os.getenv("DATABASE_URL", "")

        if not database_url or "placeholder" in database_url or "localhost" in database_url:
            print_status(
                "Database connection",
                False,
                "DATABASE_URL not configured. See SETUP_GUIDE.md for instructions."
            )
            return False

        # Extract connection params from DATABASE_URL
        # Format: postgresql+asyncpg://user:pass@host:port/db?sslmode=require
        url = database_url.replace("postgresql+asyncpg://", "")
        conn_str = url.replace("?sslmode=require", "")

        # Test connection
        conn = await asyncpg.connect(f"postgresql://{conn_str}?ssl=require")
        version = await conn.fetchval("SELECT version()")
        await conn.close()

        print_status("Database connection", True, f"PostgreSQL detected")
        return True

    except ImportError:
        print_status("Database connection", False, "asyncpg not installed. Run: pip install asyncpg")
        return False
    except Exception as e:
        print_status("Database connection", False, f"Connection failed: {str(e)[:100]}")
        return False


def check_openai():
    """Check OpenAI API key."""
    try:
        from langchain_openai import ChatOpenAI

        api_key = os.getenv("OPENAI_API_KEY", "")

        if not api_key or api_key == "sk-placeholder" or "placeholder" in api_key:
            print_status(
                "OpenAI API key",
                False,
                "OPENAI_API_KEY not configured. Get key from platform.openai.com"
            )
            return False

        if not api_key.startswith("sk-"):
            print_status(
                "OpenAI API key",
                False,
                "OPENAI_API_KEY has invalid format (should start with 'sk-')"
            )
            return False

        # Quick validation (doesn't make API call)
        llm = ChatOpenAI(model="gpt-4-turbo", api_key=api_key)
        print_status("OpenAI API key", True, "Key format valid")
        return True

    except ImportError:
        print_status("OpenAI API key", False, "langchain-openai not installed. Run: pip install langchain-openai")
        return False
    except Exception as e:
        print_status("OpenAI API key", False, f"Validation failed: {str(e)[:100]}")
        return False


async def check_qdrant():
    """Check Qdrant connection (optional for quiz generation)."""
    try:
        from qdrant_client import QdrantClient

        url = os.getenv("QDRANT_URL", "")
        api_key = os.getenv("QDRANT_API_KEY", "")

        if not url or "placeholder" in url:
            print_status(
                "Qdrant connection",
                False,
                "QDRANT_URL not configured (optional - needed for chatbot, not quizzes)"
            )
            return False

        if not api_key or "placeholder" in api_key:
            print_status(
                "Qdrant connection",
                False,
                "QDRANT_API_KEY not configured (optional - needed for chatbot)"
            )
            return False

        # Test connection
        client = QdrantClient(url=url, api_key=api_key)
        collections = client.get_collections()

        print_status("Qdrant connection", True, f"Connected to cluster")
        return True

    except ImportError:
        print_status("Qdrant connection", False, "qdrant-client not installed. Run: pip install qdrant-client")
        return False
    except Exception as e:
        print_status("Qdrant connection", False, f"Connection failed: {str(e)[:100]}")
        return False


def check_env_file():
    """Check that .env file exists."""
    env_path = Path(__file__).parent.parent / ".env"

    if not env_path.exists():
        print_status(".env file", False, "File not found. Copy .env.example to .env")
        return False

    print_status(".env file", True, f"Found at {env_path}")
    return True


def check_chapter_files():
    """Check that chapter markdown files exist."""
    docs_dir = Path(__file__).parent.parent.parent / "frontend" / "docs"

    if not docs_dir.exists():
        print_status("Chapter files", False, f"Docs directory not found: {docs_dir}")
        return False

    chapters = list(docs_dir.glob("module-*/chapter-*.md"))

    if len(chapters) < 13:
        print_status(
            "Chapter files",
            False,
            f"Only found {len(chapters)} chapters (expected 13)"
        )
        return False

    print_status("Chapter files", True, f"Found {len(chapters)} chapters")
    return True


async def main():
    """Run all verification checks."""
    print(f"\n{Colors.BOLD}=== Setup Verification ==={Colors.ENDC}\n")

    checks = {
        ".env file": check_env_file(),
        "Chapter files": check_chapter_files(),
        "Database": await check_database(),
        "OpenAI API": check_openai(),
        "Qdrant (optional)": await check_qdrant(),
    }

    print(f"\n{Colors.BOLD}=== Summary ==={Colors.ENDC}\n")

    # Required checks
    required = ["Database", "OpenAI API"]
    required_passed = all(checks.get(check, False) for check in required)

    # Optional checks
    optional = ["Qdrant (optional)"]
    optional_passed = all(checks.get(check, False) for check in optional)

    if required_passed:
        print(f"{Colors.GREEN}✓ All required prerequisites met!{Colors.ENDC}")
        print(f"\nYou can now run:")
        print(f"  {Colors.BLUE}alembic upgrade head{Colors.ENDC}  (run migrations)")
        print(f"  {Colors.BLUE}python scripts/generate_quizzes.py --all{Colors.ENDC}  (generate quizzes)")
    else:
        print(f"{Colors.RED}✗ Some required prerequisites are missing.{Colors.ENDC}")
        print(f"\nSee {Colors.BLUE}SETUP_GUIDE.md{Colors.ENDC} for detailed setup instructions.")

    if not optional_passed:
        print(f"\n{Colors.YELLOW}Note: Qdrant is optional for quiz generation but required for RAG chatbot.{Colors.ENDC}")

    print()  # Blank line

    return 0 if required_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
