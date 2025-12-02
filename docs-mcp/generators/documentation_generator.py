from pathlib import Path
from datetime import datetime
import json
from typing import Dict, Any, List

class DocumentationGenerator:
    MARKDOWN_EXTS = {'.md', '.markdown', '.mdown', '.mdwn'}
    RST_EXTS = {'.rst', '.rest', '.restx', '.rtxt'}
    ASCIIDOC_EXTS = {'.adoc', '.asciidoc', '.asc'}
    HTML_EXTS = {'.html', '.htm'}
    ORGMODE_EXTS = {'.org'}
    COMMON_DOC_NAMES = {'readme', 'changelog', 'contributing', 'license', 'authors', 'installation', 'guide', 'tutorial', 'faq', 'api', 'architecture'}

    def __init__(self, project_path: Path):
        self.project_path = Path(project_path).resolve()
        self.inventory_dir = self.project_path / 'coderef' / 'inventory'

    def generate_manifest(self) -> Dict[str, Any]:
        docs = self._discover_documentation_files()
        by_format = self._categorize_by_format(docs)
        metrics = self._calculate_metrics(docs, by_format)
        return {'project_name': self.project_path.name, 'generated_at': datetime.now().isoformat(), 'formats': list(by_format.keys()), 'files': docs, 'by_format': by_format, 'metrics': metrics}

    def _discover_documentation_files(self) -> List[Dict[str, Any]]:
        docs, visited = [], set()
        search_paths = [self.project_path, self.project_path / 'docs', self.project_path / 'doc', self.project_path / 'documentation', self.project_path / '.github']
        for search_path in search_paths:
            if not search_path.exists():
                continue
            for file_path in search_path.rglob('*'):
                if not file_path.is_file() or file_path.resolve() in visited:
                    continue
                visited.add(file_path.resolve())
                doc_info = self._analyze_file(file_path)
                if doc_info:
                    docs.append(doc_info)
        return sorted(docs, key=lambda x: x['path'])

    def _analyze_file(self, file_path: Path) -> Dict[str, Any] | None:
        suffix = file_path.suffix.lower()
        stem = file_path.stem.lower()
        all_exts = self.MARKDOWN_EXTS | self.RST_EXTS | self.ASCIIDOC_EXTS | self.HTML_EXTS | self.ORGMODE_EXTS
        if suffix not in all_exts:
            return None
        try:
            stat = file_path.stat()
            mod_time = datetime.fromtimestamp(stat.st_mtime)
            days_old = (datetime.now() - mod_time).days
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    word_count = len(f.read(500).split())
            except:
                word_count = 0
            return {'path': str(file_path.relative_to(self.project_path)), 'name': file_path.name, 'format': self._get_format(suffix), 'size_bytes': stat.st_size, 'last_modified': mod_time.isoformat(), 'days_old': days_old, 'is_important': stem in self.COMMON_DOC_NAMES, 'estimated_words': word_count}
        except:
            return None

    def _get_format(self, suffix: str) -> str:
        suffix = suffix.lower()
        if suffix in self.MARKDOWN_EXTS: return 'markdown'
        elif suffix in self.RST_EXTS: return 'rst'
        elif suffix in self.ASCIIDOC_EXTS: return 'asciidoc'
        elif suffix in self.HTML_EXTS: return 'html'
        elif suffix in self.ORGMODE_EXTS: return 'orgmode'
        return 'unknown'

    def _categorize_by_format(self, docs: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        by_format = {}
        for doc in docs:
            fmt = doc['format']
            by_format.setdefault(fmt, []).append(doc['path'])
        return by_format

    def _calculate_metrics(self, docs: List[Dict[str, Any]], by_format: Dict[str, List[str]]) -> Dict[str, Any]:
        if not docs:
            return {'total_files': 0, 'markdown_files': 0, 'rst_files': 0, 'asciidoc_files': 0, 'html_files': 0, 'orgmode_files': 0, 'quality_score': 0, 'freshness_days': 0, 'coverage_percentage': 0}
        m, r, a, h, o = len(by_format.get('markdown', [])), len(by_format.get('rst', [])), len(by_format.get('asciidoc', [])), len(by_format.get('html', [])), len(by_format.get('orgmode', []))
        days_old_list = [doc['days_old'] for doc in docs]
        avg_days_old = sum(days_old_list) / len(days_old_list) if days_old_list else 0
        quality_score = self._calculate_quality_score(docs, m)
        coverage = self._calculate_coverage(docs)
        return {'total_files': len(docs), 'markdown_files': m, 'rst_files': r, 'asciidoc_files': a, 'html_files': h, 'orgmode_files': o, 'quality_score': int(quality_score), 'freshness_days': int(avg_days_old), 'coverage_percentage': int(coverage)}

    def _calculate_quality_score(self, docs: List[Dict[str, Any]], markdown_count: int) -> float:
        score = 50
        if len(docs) >= 5: score += 10
        if len(docs) >= 10: score += 10
        if markdown_count >= 3: score += 10
        recent = sum(1 for doc in docs if doc['days_old'] <= 30)
        if recent > len(docs) * 0.5: score += 10
        if sum(1 for doc in docs if doc['is_important']) > 0: score += 10
        return min(100, max(0, score))

    def _calculate_coverage(self, docs: List[Dict[str, Any]]) -> float:
        if not docs: return 0
        found_important = {doc['name'].lower().split('.')[0] for doc in docs}
        overlap = len(found_important & self.COMMON_DOC_NAMES)
        return (overlap / len(self.COMMON_DOC_NAMES)) * 100 if self.COMMON_DOC_NAMES else 100

    def save_manifest(self, manifest: Dict[str, Any]) -> Path:
        self.inventory_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = self.inventory_dir / 'documentation.json'
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        return manifest_path
