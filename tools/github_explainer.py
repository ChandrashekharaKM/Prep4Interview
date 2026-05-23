"""
tools/github_explainer.py
Fetches and explains GitHub repositories using their public README file.
Helps candidates present their projects professionally in interviews.
"""

import os
import re
import logging
import httpx
import google.generativeai as genai

logger = logging.getLogger(__name__)

EXPLAIN_SYSTEM_PROMPT = """You are a senior technical interviewer, architect, and developer coach.
You are given a comprehensive technical snapshot of a developer's GitHub project, including:
1. **README.md** text.
2. **Directory File Tree** mapping the repository structure.
3. **Core Code/Configuration Files** containing raw source code and dependency manifests.

Provide an extremely high-standard, structured review of this project to help them present it beautifully in an interview.

Your explanation MUST be in standard GitHub Markdown and follow this precise layout:

### 🚀 Project Pitch (The 30-Second Elevator Pitch)
*Provide a high-impact, 2-3 sentence elevator pitch that explains what problem this project solves, how it solves it, and why the technical implementation is impressive and state-of-the-art.*

### 📊 Auto-Generated Architecture Flowchart
*Create a flawless, visually clean, and highly detailed Mermaid.js flowchart mapping components, directories, and data flows. Surround it ONLY with a standard ```mermaid code block. Do NOT use HTML tags inside the diagram. Ensure every node has a clear label. Example:*
```mermaid
graph TD
    A[Client UI] -->|REST API| B(FastAPI Server)
    B -->|Query| C[(PostgreSQL Database)]
```

### 📂 Codebase Directory Overview
*Analyze the file tree and provide a bulleted breakdown of the key directories/files, outlining the architectural division of labor (e.g. Frontend vs Backend, routers, tools, configuration).*

### 🛠️ Tech Stack & Deep Code Diagnostics
*Provide professional, code-level analysis based strictly on the raw files and tree:*
* **Dependency Health & Versioning**: *Analyze package versions and lock files. Highlight outdated libraries, compatibility risks, or solid dependency practices.*
* **Code Cleanliness & Standards**: *Evaluate code structure, readability, comments, error handling, and pythonic/clean patterns found in the source files.*
* **Security & Architectural Vulnerabilities**: *Outline concrete architectural gaps, hardcoded configuration risks, resource leaks, or missing safeguards.*

### 🎯 How to Pitch this in an Interview (STAR Method)
*Give concrete guidance on how to speak about this project using the STAR (Situation, Task, Action, Result) methodology:*
* **Situation**: *The context or challenge (e.g., handling real-time LLM feedback or processing high volumes).*
* **Task**: *The developer's objective and architectural requirements.*
* **Action**: *What they implemented, highlighting specific tech stack choices and advanced patterns.*
* **Result**: *The value, performance improvements, technical wins, and how they would prove it.*

### ❓ Predicted Interview Questions & Defense Guide
*Provide 3 advanced technical questions tailored directly to the diagnosed files and architecture, along with a copy-paste ready spoken first-person answer that is highly professional, authoritative, and direct (no AI preambles or chat filler).*
1. **Question**: *e.g., Why did you choose FastAPI over standard Flask, and how did you structure your session storage?*
   * **Spoken Defense Answer**: *Provide a first-person, high-standard answer using direct 'I did this' format.*
2. **Question**: ...
   * **Spoken Defense Answer**: ...
3. **Question**: ...
   * **Spoken Defense Answer**: ...
"""

class GitHubExplainer:
    def __init__(self):
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        # Using gemini-2.5-flash as supported by the API key and service
        self._model = genai.GenerativeModel("gemini-2.5-flash")

    def parse_git_url(self, url: str) -> tuple[str | None, str | None]:
        """Extract owner and repo name from common GitHub URL patterns."""
        if not url:
            return None, None
            
        url = url.strip()
        if url.endswith(".git"):
            url = url[:-4]
        url = url.rstrip("/")

        # Regex to match github.com/owner/repo
        pattern = r"(?:https?://)?(?:www\.)?github\.com/([^/]+)/([^/]+)"
        match = re.search(pattern, url)
        if match:
            owner = match.group(1)
            repo = match.group(2)
            # Handle tree/branch folders inside URL
            if "/" in repo:
                repo = repo.split("/")[0]
            return owner, repo
        return None, None

    def fetch_readme(self, owner: str, repo: str) -> str:
        """Fetch README content from raw.githubusercontent.com."""
        # Try common branch/capitalization configurations
        urls = [
            f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md",
            f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md",
            f"https://raw.githubusercontent.com/{owner}/{repo}/main/readme.md",
            f"https://raw.githubusercontent.com/{owner}/{repo}/master/readme.md",
        ]

        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            for url in urls:
                try:
                    resp = client.get(url)
                    if resp.status_code == 200:
                        logger.info("Successfully fetched README from %s", url)
                        return resp.text
                except Exception as e:
                    logger.debug("Failed to fetch from %s: %s", url, e)

        raise RuntimeError(
            f"Could not locate a README.md or readme.md file in the `main` or `master` branch "
            f"for repository {owner}/{repo}."
        )

    def fetch_repo_tree(self, owner: str, repo: str) -> tuple[list[str], str]:
        """
        Queries the GitHub Git Trees API recursively to obtain all file paths.
        Returns a list of file path strings and the active branch name.
        """
        branches = ["main", "master"]
        file_paths = []
        active_branch = "main"

        headers = {
            "User-Agent": "Prep4Interview-App",
            "Accept": "application/vnd.github.v3+json"
        }
        # Include GitHub token if available in env to raise rate limit bounds
        token = os.getenv("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"token {token}"

        with httpx.Client(timeout=12.0, follow_redirects=True, headers=headers) as client:
            for br in branches:
                url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{br}?recursive=1"
                try:
                    resp = client.get(url)
                    if resp.status_code == 200:
                        active_branch = br
                        data = resp.json()
                        tree = data.get("tree", [])
                        file_paths = [item["path"] for item in tree if item.get("type") == "blob"]
                        logger.info("Successfully fetched recursive tree for branch %s. Files count: %d", br, len(file_paths))
                        break
                except Exception as e:
                    logger.warning("Failed to fetch tree from branch %s: %s", br, e)

        return file_paths, active_branch

    def fetch_raw_file(self, owner: str, repo: str, branch: str, file_path: str) -> str | None:
        """Downloads raw code file content via zero-rate-limit raw.githubusercontent.com."""
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            try:
                resp = client.get(url)
                if resp.status_code == 200:
                    logger.info("Successfully fetched raw file from %s", file_path)
                    return resp.text
            except Exception as e:
                logger.warning("Failed to fetch raw file %s: %s", file_path, e)
        return None

    def explain_project(self, git_url: str) -> str:
        """
        Extract owner/repo, fetch tree structure, download key files, fetch README, and generate a premium analysis.
        """
        owner, repo = self.parse_git_url(git_url)
        if not owner or not repo:
            return (
                "⚠️ **Invalid GitHub URL format.** Please enter a valid URL "
                "such as `https://github.com/username/repository`."
            )

        # 1. Fetch README
        readme_text = ""
        try:
            readme_text = self.fetch_readme(owner, repo)
        except Exception as e:
            readme_text = f"*(No README found or error fetching: {str(e)})*"

        # 2. Fetch File Tree (with fallback handling if rate limited)
        file_tree = []
        branch = "main"
        try:
            file_tree, branch = self.fetch_repo_tree(owner, repo)
        except Exception as e:
            logger.warning("File tree API call failed: %s", e)

        # Identify up to 3 high-importance codebase/config files to diagnostic
        important_indicators = [
            # Dependency manifests
            "package.json", "requirements.txt", "go.mod", "Cargo.toml", "pyproject.toml",
            # Application entry points
            "main.py", "app.py", "index.js", "server.js", "manage.py",
            # Docker & Setup configs
            "Dockerfile", "docker-compose.yml", ".env.example"
        ]

        raw_files_content = {}
        scanned_files = []
        for path in file_tree:
            filename = os.path.basename(path)
            if filename in important_indicators:
                scanned_files.append(path)
                if len(scanned_files) >= 3:
                    break

        # Proactively fetch raw contents
        for path in scanned_files:
            content = self.fetch_raw_file(owner, repo, branch, path)
            if content:
                # Limit size to prevent huge prompts
                if len(content) > 8000:
                    content = content[:8000] + "\n\n*(Truncated file content)*"
                raw_files_content[path] = content

        # Compile detailed diagnostic prompt context
        tree_summary = "\n".join(file_tree[:150])
        if len(file_tree) > 150:
            tree_summary += f"\n*(Truncated directory tree of {len(file_tree)} total files)*"

        files_content_summary = ""
        for path, code in raw_files_content.items():
            files_content_summary += f"\n--- FILE: {path} ---\n```\n{code}\n```\n"

        # Truncate readme if necessary
        if len(readme_text) > 12000:
            readme_text = readme_text[:12000] + "\n\n*(Truncated README)*"

        # Assemble full Gemini analysis prompt
        prompt = (
            f"{EXPLAIN_SYSTEM_PROMPT}\n\n"
            f"=== CONTEXT FOR REPOSITORY: {owner}/{repo} ===\n\n"
            f"Active Branch: {branch}\n\n"
            f"--- REPOSITORY FILE TREE ---\n"
            f"{tree_summary}\n\n"
            f"--- KEY FILES DOWNLOADED ---\n"
            f"{files_content_summary}\n\n"
            f"--- README.md CONTENT ---\n"
            f"{readme_text}\n"
        )

        try:
            response = self._model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=2500,
                    temperature=0.3,
                )
            )
            return response.text
        except Exception as e:
            return f"❌ **Error generating explanation from Gemini:** {str(e)}"

