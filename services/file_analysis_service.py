"""File analysis service for organizing files by topic."""
import os
from pathlib import Path
from typing import List, Dict, Optional
import json
import httpx

from models import FileMetadata, FolderOrganization, OrganizationResult
from utils import (
    validate_path,
    is_text_file,
    sanitize_folder_name,
    AnalysisError,
    FileAccessError,
)
from utils.interactive import prompt_for_classification, prompt_for_subcategory


class FileAnalysisService:
    """Service for analyzing files and suggesting organization."""

    def __init__(self):
        """Initialize the analysis service."""
        self.analysis_cache: Dict[str, FileMetadata] = {}
        self.llm_cache: Dict[str, tuple] = {}  # Cache LLM responses by file hash

    def analyze_folder(self, folder_path: str) -> OrganizationResult:
        """
        Analyze a folder and suggest file organization.

        Args:
            folder_path: Path to folder to analyze

        Returns:
            OrganizationResult with suggested organization
        """
        path = validate_path(folder_path)

        try:
            files = self._get_all_files(path)

            if not files:
                return OrganizationResult(
                    source_folder=path,
                    total_files=0,
                    organized_folders=[],
                    unorganized_files=[],
                )

            # Analyze each file
            analyzed_files = []
            for file_path in files:
                try:
                    metadata = self._analyze_file(file_path, path)
                    analyzed_files.append(metadata)
                except AnalysisError:
                    # Skip files that can't be analyzed
                    continue

            # Organize by category
            organized_folders = self._organize_by_category(analyzed_files)

            return OrganizationResult(
                source_folder=path,
                total_files=len(analyzed_files),
                organized_folders=organized_folders,
                unorganized_files=[
                    f for f in analyzed_files if f.suggested_category == "Uncategorized"
                ],
                suggested_structure=self._build_structure(organized_folders),
            )

        except Exception as e:
            raise AnalysisError(f"Failed to analyze folder: {str(e)}")

    def _get_all_files(self, folder_path: Path) -> List[Path]:
        """Get all files in folder (non-recursively by default)."""
        try:
            files = [f for f in folder_path.iterdir() if f.is_file()]
            return sorted(files, key=lambda x: x.name)
        except (OSError, PermissionError) as e:
            raise FileAccessError(f"Cannot access folder: {str(e)}")

    def _analyze_file(self, file_path: Path, base_path: Path) -> FileMetadata:
        """Analyze a single file."""
        try:
            file_name = file_path.name
            file_size = file_path.stat().st_size
            file_type = file_path.suffix.lower()

            # Read content preview for text files
            content_preview = ""
            if is_text_file(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content_preview = f.read(500)
                except Exception:
                    pass

            # Analyze and suggest category
            category, confidence = self._suggest_category(
                file_name, file_type, content_preview
            )

            # Suggest improved name
            suggested_name = self._suggest_filename(file_name, category, file_type, content_preview)

            tags = self._extract_tags(file_name, content_preview)

            return FileMetadata(
                original_name=file_name,
                suggested_name=suggested_name,
                file_path=file_path,
                file_size=file_size,
                file_type=file_type,
                suggested_category=category,
                confidence_score=confidence,
                content_preview=content_preview[:200],
                tags=tags,
            )

        except Exception as e:
            raise AnalysisError(f"Failed to analyze file {file_path}: {str(e)}")

    def _suggest_category(
        self, filename: str, file_type: str, content: str
    ) -> tuple[str, float]:
        """Suggest category and confidence score using AI when available.

        Delegates to external LLM or OpenAI for classification.
        If no AI is configured, returns "Uncategorized" with 0.0 confidence.
        """
        ai_category, ai_conf = self._ai_suggest_category(filename, file_type, content)
        return ai_category, ai_conf

    def _ai_suggest_category(self, filename: str, file_type: str, content: str) -> tuple[str, float]:
        """AI-based category classification using external LLM or OpenAI.

        Returns (category, confidence). 
        Falls back to interactive prompt only if INTERACTIVE_MODE=true.
        Otherwise returns ("Uncategorized", 0.0).
        """
        # Try external LLM first
        try:
            external_url = os.environ.get("EXTERNAL_LLM_URL")
            external_key = os.environ.get("EXTERNAL_LLM_API_KEY")
            if external_url:
                external_result = self._external_llm_classify(
                    external_url, external_key, filename, file_type, content
                )
                if external_result:
                    cat, conf, subcat, _ = external_result
                    return (cat, conf)

            # Try OpenAI if no external URL
            openai_key = os.environ.get("OPENAI_API_KEY")
            if openai_key:
                openai_result = self._openai_classify(openai_key, filename, file_type, content)
                if openai_result:
                    cat, conf, subcat, _ = openai_result
                    return (cat, conf)
        except Exception:
            pass

        # Fallback to interactive prompt only if explicitly enabled
        if os.environ.get("INTERACTIVE_MODE", "").lower() == "true":
            try:
                result = prompt_for_classification(filename, file_type, content)
                if result:
                    cat, conf, subcat, _ = result
                    return (cat, conf)
            except Exception:
                pass

        # No AI and not in interactive mode: return uncategorized
        return "Uncategorized", 0.0

    def _external_llm_classify(
        self, url: str, api_key: Optional[str], filename: str, file_type: str, content: str
    ) -> Optional[tuple[str, float, Optional[str], Optional[str]]]:
        """Call an external LLM endpoint to classify and name the file.

        Expected to receive a JSON response with keys: `category`, `confidence`,
        optional `subcategory`, optional `suggested_name`.
        This function is optional and will be skipped when `EXTERNAL_LLM_URL` is not set.
        """
        # Build a compact prompt payload asking for JSON output
        payload = {
            "input": {
                "filename": filename,
                "file_type": file_type,
                "content_preview": (content or "")[:1000],
            },
            "instructions": (
                "Classify the file into a category and optional subcategory, and "
                "suggest a concise suggested_name. Respond with a JSON object: {\"category\":..., \"confidence\":..., "
                "\"subcategory\":..., \"suggested_name\":...}"
            ),
        }

        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            with httpx.Client(timeout=10.0) as client:
                r = client.post(url, json=payload, headers=headers)
                r.raise_for_status()
                # Expect JSON in response body
                data = r.json()

                # Accept either top-level or under `result` key
                if "result" in data and isinstance(data["result"], dict):
                    data = data["result"]

                category = data.get("category") or data.get("label")
                confidence = float(data.get("confidence", 0.0)) if data.get("confidence") is not None else 0.0
                subcategory = data.get("subcategory")
                suggested_name = data.get("suggested_name")

                if category:
                    return category, confidence, subcategory, suggested_name

        except Exception:
            return None

        return None

    def _openai_classify(self, api_key: str, filename: str, file_type: str, content: str) -> Optional[tuple[str, float, Optional[str], Optional[str]]]:
        """Classify using OpenAI Chat Completions API.

        Returns (category, confidence, subcategory, suggested_name) or None on failure.
        """
        try:
            prompt = (
                "You are a file classifier. Given filename, file_type and a short content_preview, "
                "return a JSON object with keys: category(str), confidence(float 0-1), optional subcategory(str), "
                "optional suggested_name(str). Only output valid JSON. Example: {\"category\": \"Code\", \"confidence\": 0.9, \"subcategory\": \"Python\"}.\n\n"
            )

            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": prompt},
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "filename": filename,
                                "file_type": file_type,
                                "content_preview": (content or "")[:1000],
                            }
                        ),
                    },
                ],
                "temperature": 0.0,
                "max_tokens": 300,
            }

            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

            with httpx.Client(timeout=15.0) as client:
                r = client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
                r.raise_for_status()
                data = r.json()

                choices = data.get("choices") or []
                if not choices:
                    return None
                content_text = choices[0].get("message", {}).get("content", "")

                json_text = self._extract_json_from_text(content_text)
                if not json_text:
                    return None

                parsed = json.loads(json_text)
                category = parsed.get("category") or parsed.get("label")
                confidence = float(parsed.get("confidence", 0.0)) if parsed.get("confidence") is not None else 0.0
                subcategory = parsed.get("subcategory")
                suggested_name = parsed.get("suggested_name")
                if category:
                    return category, confidence, subcategory, suggested_name
        except Exception:
            return None

        return None

    def _extract_json_from_text(self, text: str) -> Optional[str]:
        """Find a JSON object substring in free text and return it, or None."""
        try:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                candidate = text[start : end + 1]
                json.loads(candidate)
                return candidate
        except Exception:
            return None
        return None

    def _suggest_filename(self, original_name: str, category: str, file_type: str, content_preview: str) -> str:
        """Suggest an improved filename using AI if available, otherwise heuristics.

        Tries external LLM/OpenAI first to get AI-suggested names.
        Falls back to heuristic-based suggestion if no AI is configured.
        """
        try:
            # Try external LLM first
            external_url = os.environ.get("EXTERNAL_LLM_URL")
            external_key = os.environ.get("EXTERNAL_LLM_API_KEY")
            if external_url:
                result = self._external_llm_classify(
                    external_url, external_key, original_name, file_type, content_preview
                )
                if result and result[3]:  # result[3] is suggested_name
                    return result[3]

            # Try OpenAI
            openai_key = os.environ.get("OPENAI_API_KEY")
            if openai_key:
                result = self._openai_classify(openai_key, original_name, file_type, content_preview)
                if result and result[3]:  # result[3] is suggested_name
                    return result[3]
        except Exception:
            pass

        # Fallback to heuristic-based naming
        name_without_ext = Path(original_name).stem
        ext = Path(original_name).suffix

        # If filename is already descriptive, keep it
        if len(name_without_ext) > 5 and "_" in name_without_ext:
            return original_name

        # Otherwise, enhance it with category prefix
        suggested = f"{category}_{name_without_ext}{ext}"
        return suggested

    def _extract_tags(self, filename: str, content: str) -> List[str]:
        """Extract relevant tags from filename and content."""
        tags = []

        # Extract from filename
        parts = Path(filename).stem.split("_")
        tags.extend([p for p in parts if len(p) > 3])

        # Extract from content (simple approach)
        if content:
            words = content.split()[:50]  # First 50 words
            tags.extend(
                [
                    w.lower().strip(".,;:")
                    for w in words
                    if len(w) > 4 and w[0].isupper()
                ][:3]
            )

        return list(set(tags))[:5]  # Unique, max 5 tags

    def _organize_by_category(
        self, files: List[FileMetadata]
    ) -> List[FolderOrganization]:
        """Organize files by category."""
        # Use (top_category, subcategory) as grouping key so we can
        # keep top-level categories like 'Code' while splitting
        # code into more specific subcategories (e.g. Python, SQL, Java).
        organization: Dict[tuple, FolderOrganization] = {}

        for file_metadata in files:
            top_category = file_metadata.suggested_category
            subcategory = self._detect_subcategory(file_metadata)

            key = (top_category, subcategory or "")

            if key not in organization:
                # suggested_folder_name contains both levels when subcategory present
                folder_name = (
                    f"{top_category}/{subcategory}" if subcategory else top_category
                )
                organization[key] = FolderOrganization(
                    category=top_category,
                    suggested_folder_name=sanitize_folder_name(folder_name),
                )

            organization[key].files.append(file_metadata)

        # Return FolderOrganization objects sorted by file count
        return sorted(
            organization.values(), key=lambda x: len(x.files), reverse=True
        )

    def _detect_subcategory(self, file_metadata: FileMetadata) -> Optional[str]:
        """Detect a more specific subcategory for files.

        Tries external LLM/OpenAI first, then interactive prompt if INTERACTIVE_MODE=true.
        Returns None if AI unavailable and not in interactive mode.
        """
        ext = (file_metadata.file_type or "").lower()
        name = file_metadata.original_name.lower()
        content = (file_metadata.content_preview or "").lower()

        # If external LLM or OpenAI is configured, ask it for subcategory
        try:
            external_url = os.environ.get("EXTERNAL_LLM_URL")
            external_key = os.environ.get("EXTERNAL_LLM_API_KEY")
            if external_url:
                result = self._external_llm_classify(
                    external_url, external_key, file_metadata.original_name, ext, content
                )
                if result:
                    cat, conf, subcat, _ = result
                    if subcat:
                        return subcat

            openai_key = os.environ.get("OPENAI_API_KEY")
            if openai_key:
                result = self._openai_classify(openai_key, file_metadata.original_name, ext, content)
                if result:
                    cat, conf, subcat, _ = result
                    if subcat:
                        return subcat
        except Exception:
            pass

        # Fallback to interactive prompt only if explicitly enabled
        if os.environ.get("INTERACTIVE_MODE", "").lower() == "true":
            try:
                category = file_metadata.suggested_category
                subcategory = prompt_for_subcategory(category)
                if subcategory:
                    return subcategory
            except Exception:
                pass

        # No AI and not in interactive mode: return None
        return None

    def _build_structure(self, organized_folders: List[FolderOrganization]) -> dict:
        """Build suggested folder structure."""
        structure = {}
        for folder in organized_folders:
            structure[folder.suggested_folder_name] = {
                "category": folder.category,
                "file_count": len(folder.files),
                "files": [f.suggested_name for f in folder.files[:5]],  # Top 5
            }
        return structure
