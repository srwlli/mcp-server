"""
Standards generator for establish_standards tool.

Scans codebase to discover UI/UX/behavior patterns and generates comprehensive
standards documentation.
"""

import re
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from constants import (
    Paths, Files, ScanDepth, FocusArea,
    EXCLUDE_DIRS, MAX_FILE_SIZE, ALLOWED_FILE_EXTENSIONS
)
from type_defs import (
    UIPatternDict, BehaviorPatternDict, UXPatternDict,
    ComponentMetadataDict, StandardsResultDict
)
from logger_config import logger, log_security_event


class StandardsGenerator:
    """
    Generator for discovering code patterns and creating standards documentation.

    Scans project files to find UI components, behavior patterns, and UX flows,
    then generates markdown documentation of discovered standards.
    """

    def __init__(self, project_path: Path, scan_depth: str = ScanDepth.STANDARD.value):
        """
        Initialize standards generator.

        Args:
            project_path: Absolute path to project directory
            scan_depth: Analysis depth ('quick', 'standard', or 'deep')
        """
        self.project_path = project_path.resolve()  # SEC-001: Canonicalize path
        self.scan_depth = scan_depth

        # Compile regex patterns once for performance
        self._button_pattern = re.compile(r'<Button[^>]*>', re.DOTALL)
        self._modal_pattern = re.compile(r'<Modal[^>]*>|<Dialog[^>]*>', re.DOTALL)
        self._color_pattern = re.compile(r'#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}')
        self._error_pattern = re.compile(r'throw new Error\([\'"](.+?)[\'"]\)|toast\.error\([\'"](.+?)[\'"]\)')
        self._loading_pattern = re.compile(r'isLoading|loading\s*[:=]|<Spinner|<Loading')

        # Theme system detection patterns
        self._theme_hook_pattern = re.compile(r'const\s+{\s*\w+\s*}\s*=\s*use\w*[Tt]heme\w*\(\)')
        self._color_scheme_interface = re.compile(r'interface\s+ColorScheme\s*{([^}]+)}', re.DOTALL)
        self._theme_export = re.compile(r'export\s+const\s+Themes\s*[:=]', re.MULTILINE)

        logger.debug(f"Initialized StandardsGenerator for {project_path} with depth={scan_depth}")

    def scan_codebase(self) -> Dict[str, List[Path]]:
        """
        Scan all source files and collect code samples.

        Returns:
            Dict with files grouped by type (tsx, css, etc.)
        """
        logger.info("Starting codebase scan", extra={'scan_depth': self.scan_depth})

        files_by_type: Dict[str, List[Path]] = {
            'tsx': [],
            'jsx': [],
            'ts': [],
            'js': [],
            'css': []
        }

        # SEC-004: Canonicalize excluded paths
        excluded_paths = [Path(self.project_path / d).resolve() for d in EXCLUDE_DIRS]

        # Scan for all relevant files
        for ext in ALLOWED_FILE_EXTENSIONS:
            pattern = f"**/*{ext}"
            for file_path in self.project_path.glob(pattern):
                file_resolved = file_path.resolve()  # SEC-004: Canonicalize file path

                # Check if file is under any excluded directory
                if any(file_resolved.is_relative_to(exc_path) for exc_path in excluded_paths if exc_path.exists()):
                    logger.debug(f"Skipping excluded file: {file_path}", extra={'reason': 'excluded_directory'})
                    continue

                # SEC-008: Check for symlinks
                if file_path.is_symlink():
                    if not file_resolved.is_relative_to(self.project_path.resolve()):
                        log_security_event(
                            'symlink_outside_project',
                            f"Skipping symlink pointing outside project: {file_path} -> {file_resolved}",
                            file_path=str(file_path),
                            target=str(file_resolved)
                        )
                        continue

                # SEC-007: Check file size
                try:
                    file_size = file_path.stat().st_size
                    if file_size > MAX_FILE_SIZE:
                        logger.warning(
                            f"Skipping large file: {file_path}",
                            extra={'file_size_mb': file_size / 1024 / 1024, 'max_size_mb': MAX_FILE_SIZE / 1024 / 1024}
                        )
                        continue
                except OSError:
                    continue

                # Add to appropriate category
                ext_clean = ext.lstrip('.')
                if ext_clean in files_by_type:
                    files_by_type[ext_clean].append(file_path)

        total_files = sum(len(files) for files in files_by_type.values())
        logger.info(f"Scan completed: found {total_files} source files", extra={'files_by_type': {k: len(v) for k, v in files_by_type.items()}})

        return files_by_type

    def detect_theme_system(self, files: Dict[str, List[Path]]) -> Dict:
        """
        Detect centralized theme system by looking for theme files and hooks.

        Args:
            files: Dict with files grouped by type

        Returns:
            Dict with theme system details or None if not found
        """
        logger.info("Detecting theme system")

        theme_system = {
            'detected': False,
            'theme_file': None,
            'hook_file': None,
            'hook_name': None,
            'colors': [],
            'theme_names': [],
            'color_count': 0
        }

        # Search for theme files in common locations
        theme_file_patterns = [
            'constants/theme.ts', 'constants/theme.js',
            'constants/colors.ts', 'constants/colors.js',
            'theme/colors.ts', 'theme/colors.js',
            'theme/index.ts', 'theme/index.js',
            'config/theme.ts', 'config/theme.js'
        ]

        for pattern in theme_file_patterns:
            theme_path = self.project_path / pattern
            if theme_path.exists():
                theme_system['theme_file'] = theme_path
                logger.info(f"Found theme file: {pattern}")
                break

        # Search for theme hook files
        hook_file_patterns = [
            'hooks/use-theme-colors.ts', 'hooks/use-theme-colors.tsx',
            'hooks/useThemeColors.ts', 'hooks/useThemeColors.tsx',
            'hooks/use-theme.ts', 'hooks/use-theme.tsx',
            'hooks/useTheme.ts', 'hooks/useTheme.tsx'
        ]

        for pattern in hook_file_patterns:
            hook_path = self.project_path / pattern
            if hook_path.exists():
                theme_system['hook_file'] = hook_path
                logger.info(f"Found theme hook: {pattern}")
                break

        # If we found a theme file, parse its structure
        if theme_system['theme_file']:
            parsed = self.parse_theme_structure(theme_system['theme_file'], theme_system.get('hook_file'))
            if parsed['is_valid']:
                theme_system['detected'] = True
                theme_system['colors'] = parsed['colors']
                theme_system['theme_names'] = parsed['theme_names']
                theme_system['color_count'] = len(parsed['colors'])
                theme_system['hook_name'] = parsed['hook_name']
                logger.info(f"Theme system detected: {theme_system['color_count']} colors, {len(theme_system['theme_names'])} themes")

        return theme_system

    def parse_theme_structure(self, theme_file: Path, hook_file: Path = None) -> Dict:
        """
        Parse theme file to extract color scheme and theme names.

        Args:
            theme_file: Path to theme constants file
            hook_file: Optional path to theme hook file

        Returns:
            Dict with parsed theme structure
        """
        logger.debug(f"Parsing theme structure from {theme_file}")

        result = {
            'is_valid': False,
            'colors': [],
            'theme_names': [],
            'hook_name': None
        }

        try:
            content = theme_file.read_text(encoding='utf-8')

            # Extract ColorScheme interface (handle nested braces properly)
            interface_start = content.find('interface ColorScheme')
            if interface_start != -1:
                # Find the opening brace
                open_brace = content.find('{', interface_start)
                if open_brace != -1:
                    # Count braces to find matching close
                    brace_count = 1
                    pos = open_brace + 1
                    while pos < len(content) and brace_count > 0:
                        if content[pos] == '{':
                            brace_count += 1
                        elif content[pos] == '}':
                            brace_count -= 1
                        pos += 1

                    if brace_count == 0:
                        interface_body = content[open_brace+1:pos-1]
                        # Extract property names (color names)
                        property_pattern = re.compile(r'(\w+)\s*:\s*string')
                        colors = property_pattern.findall(interface_body)
                        result['colors'] = colors
                        logger.debug(f"Found {len(colors)} color properties")

            # Extract theme names from ThemeName type or Themes object
            # Pattern 1: type ThemeName = 'foo' | 'bar' | 'baz';
            theme_type_pattern = re.compile(r"type\s+ThemeName\s*=\s*([^;]+);", re.MULTILINE)
            theme_type_match = theme_type_pattern.search(content)
            if theme_type_match:
                theme_string = theme_type_match.group(1)
                # Extract quoted strings
                theme_names = re.findall(r"['\"](\w+)['\"]", theme_string)
                result['theme_names'] = theme_names
                logger.debug(f"Found {len(theme_names)} theme names from type definition")

            # Pattern 2: export const Themes = { foo: {...}, bar: {...} }
            if not result['theme_names'] and self._theme_export.search(content):
                # Find theme names from object keys
                themes_object_pattern = re.compile(r'Themes\s*[:=]\s*\{([^}]+)\}', re.DOTALL)
                themes_match = themes_object_pattern.search(content)
                if themes_match:
                    themes_body = themes_match.group(1)
                    # Extract keys
                    key_pattern = re.compile(r'(\w+)\s*:')
                    theme_names = key_pattern.findall(themes_body)
                    result['theme_names'] = theme_names
                    logger.debug(f"Found {len(theme_names)} theme names from Themes object")

            # Extract hook name from hook file
            if hook_file and hook_file.exists():
                hook_content = hook_file.read_text(encoding='utf-8')
                # Pattern: export function useThemeColors()
                hook_pattern = re.compile(r'export\s+function\s+(use\w+)\s*\(')
                hook_match = hook_pattern.search(hook_content)
                if hook_match:
                    result['hook_name'] = hook_match.group(1)
                    logger.debug(f"Found hook name: {result['hook_name']}")

            # Validate that we found essential components
            if result['colors'] and result['theme_names']:
                result['is_valid'] = True

        except Exception as e:
            logger.debug(f"Error parsing theme structure: {e}")

        return result

    def analyze_ui_patterns(self, files: Dict[str, List[Path]]) -> UIPatternDict:
        """
        Analyze UI component patterns from source files.

        Args:
            files: Dict with files grouped by type

        Returns:
            UIPatternDict with discovered UI patterns
        """
        logger.info("Analyzing UI patterns")

        ui_patterns: UIPatternDict = {
            'buttons': {'sizes': [], 'variants': [], 'common_props': []},
            'modals': {'sizes': [], 'positions': [], 'backdrop': []},
            'forms': {'input_types': [], 'validation': [], 'error_states': []},
            'colors': {'hex_codes': [], 'css_vars': [], 'theme_colors': []},
            'typography': {'font_sizes': [], 'weights': [], 'families': []},
            'spacing': {'margins': [], 'paddings': [], 'gaps': []},
            'icons': {'library': 'unknown', 'sizes': [], 'colors': []}
        }

        # Detect theme system first
        theme_system = self.detect_theme_system(files)
        if theme_system['detected']:
            ui_patterns['theme_system'] = theme_system

        # Track component library usage
        shadcn_components = set()
        tailwind_patterns = set()

        # Analyze TSX/JSX files for UI components
        ui_files = files.get('tsx', []) + files.get('jsx', [])

        for file_path in ui_files:
            try:
                content = file_path.read_text(encoding='utf-8')

                # Find button patterns
                button_matches = self._button_pattern.findall(content)
                for match in button_matches:
                    # Extract size prop
                    size_match = re.search(r'size=[\'"](\w+)[\'"]', match)
                    if size_match and size_match.group(1) not in ui_patterns['buttons']['sizes']:
                        ui_patterns['buttons']['sizes'].append(size_match.group(1))

                    # Extract variant prop
                    variant_match = re.search(r'variant=[\'"](\w+)[\'"]', match)
                    if variant_match and variant_match.group(1) not in ui_patterns['buttons']['variants']:
                        ui_patterns['buttons']['variants'].append(variant_match.group(1))

                # Find modal/dialog patterns
                modal_matches = self._modal_pattern.findall(content)
                for match in modal_matches:
                    size_match = re.search(r'size=[\'"](\w+)[\'"]', match)
                    if size_match and size_match.group(1) not in ui_patterns['modals']['sizes']:
                        ui_patterns['modals']['sizes'].append(size_match.group(1))

                # Find color usage
                color_matches = self._color_pattern.findall(content)
                for color in color_matches:
                    if color not in ui_patterns['colors']['hex_codes']:
                        ui_patterns['colors']['hex_codes'].append(color)

                # If theme system detected, track violations
                if theme_system['detected'] and color_matches:
                    if 'hardcoded_violations' not in ui_patterns:
                        ui_patterns['hardcoded_violations'] = {
                            'count': 0,
                            'files': [],
                            'common_colors': {}
                        }

                    ui_patterns['hardcoded_violations']['count'] += len(color_matches)
                    file_rel_path = str(file_path.relative_to(self.project_path))
                    if file_rel_path not in ui_patterns['hardcoded_violations']['files']:
                        ui_patterns['hardcoded_violations']['files'].append(file_rel_path)

                    # Count common violations
                    for color in color_matches:
                        if color not in ui_patterns['hardcoded_violations']['common_colors']:
                            ui_patterns['hardcoded_violations']['common_colors'][color] = 0
                        ui_patterns['hardcoded_violations']['common_colors'][color] += 1

                # Detect shadcn/ui component imports
                shadcn_import_pattern = re.findall(r'from [\'"]@/components/ui/(\w+)[\'"]', content)
                shadcn_components.update(shadcn_import_pattern)

                # Detect Tailwind patterns (common utility classes)
                tailwind_classes = re.findall(r'className=[\'"]([^\'"]+)[\'"]', content)
                for class_str in tailwind_classes:
                    # Extract common patterns
                    classes = class_str.split()
                    for cls in classes:
                        # Track common patterns
                        if cls.startswith('flex'):
                            tailwind_patterns.add('flex-layout')
                        elif cls.startswith('grid'):
                            tailwind_patterns.add('grid-layout')
                        elif 'gap-' in cls:
                            tailwind_patterns.add(cls)
                        elif cls.startswith('p-') or cls.startswith('px-') or cls.startswith('py-'):
                            tailwind_patterns.add('padding-utilities')
                        elif cls.startswith('m-') or cls.startswith('mx-') or cls.startswith('my-'):
                            tailwind_patterns.add('margin-utilities')

                # Detect icon library usage
                if 'lucide-react' in content:
                    ui_patterns['icons']['library'] = 'lucide-react'
                elif 'react-icons' in content:
                    ui_patterns['icons']['library'] = 'react-icons'
                elif '@heroicons' in content:
                    ui_patterns['icons']['library'] = 'heroicons'

            except Exception as e:
                logger.debug(f"Error analyzing UI patterns in {file_path}: {e}")
                continue

        # Store discovered shadcn/ui components
        if shadcn_components:
            ui_patterns['shadcn_components'] = sorted(list(shadcn_components))

        # Store discovered Tailwind patterns
        if tailwind_patterns:
            ui_patterns['tailwind_patterns'] = sorted(list(tailwind_patterns))

        patterns_count = len(ui_patterns['buttons']['sizes']) + len(ui_patterns['modals']['sizes']) + len(ui_patterns['colors']['hex_codes'])
        logger.info(f"UI pattern analysis complete: found {patterns_count} patterns")

        return ui_patterns

    def analyze_behavior_patterns(self, files: Dict[str, List[Path]]) -> BehaviorPatternDict:
        """
        Analyze behavior patterns (errors, loading, etc.).

        Args:
            files: Dict with files grouped by type

        Returns:
            BehaviorPatternDict with behavior patterns and examples
        """
        logger.info("Analyzing behavior patterns")

        behavior_patterns: BehaviorPatternDict = {
            'error_handling': {'patterns': [], 'messages': [], 'recovery': []},
            'loading_states': {'indicators': [], 'skeleton': [], 'flags': []},
            'toasts': {'duration': [], 'position': [], 'types': []},
            'validation': {'rules': [], 'timing': [], 'messages': []},
            'api_communication': {'error_handling': [], 'retries': []}
        }

        # Track state management patterns
        state_management_patterns = set()
        client_component_patterns = set()
        server_component_patterns = set()

        # Analyze all code files
        code_files = files.get('tsx', []) + files.get('jsx', []) + files.get('ts', []) + files.get('js', [])

        for file_path in code_files:
            try:
                content = file_path.read_text(encoding='utf-8')

                # Find error handling patterns
                error_matches = self._error_pattern.findall(content)
                for match in error_matches:
                    message = match[0] or match[1]  # Get whichever group matched
                    if message and message not in behavior_patterns['error_handling']['messages']:
                        behavior_patterns['error_handling']['messages'].append(message)

                # Find loading state patterns
                if self._loading_pattern.search(content):
                    if 'loading_state_detected' not in behavior_patterns['loading_states']['indicators']:
                        behavior_patterns['loading_states']['indicators'].append('loading_state_detected')

                # Detect ErrorBoundary usage
                if 'ErrorBoundary' in content:
                    if 'error_boundary' not in behavior_patterns['error_handling']['patterns']:
                        behavior_patterns['error_handling']['patterns'].append('error_boundary')

                # Detect try-catch patterns
                if re.search(r'try\s*{', content):
                    if 'try_catch' not in behavior_patterns['error_handling']['patterns']:
                        behavior_patterns['error_handling']['patterns'].append('try_catch')

                # Detect toast/notification libraries
                if 'toast' in content or 'sonner' in content:
                    if 'toast_notifications' not in behavior_patterns['toasts']['types']:
                        behavior_patterns['toasts']['types'].append('toast_notifications')

                # Detect state management patterns
                if 'useState' in content:
                    state_management_patterns.add('useState')
                if 'useReducer' in content:
                    state_management_patterns.add('useReducer')
                if 'createContext' in content or 'useContext' in content:
                    state_management_patterns.add('Context_API')
                if 'zustand' in content or 'create(' in content:
                    state_management_patterns.add('Zustand')

                # Detect client vs server components
                if '"use client"' in content or "'use client'" in content:
                    client_component_patterns.add(str(file_path.relative_to(self.project_path)))
                elif file_path.suffix in ['.tsx', '.ts'] and 'export default' in content and '"use client"' not in content:
                    # Likely a server component (no "use client" directive)
                    server_component_patterns.add(str(file_path.relative_to(self.project_path)))

                # Detect data fetching patterns
                if 'fetch(' in content:
                    if 'fetch_api' not in behavior_patterns['api_communication']['patterns']:
                        behavior_patterns['api_communication']['patterns'] = ['fetch_api']
                if 'axios' in content:
                    if 'axios' not in behavior_patterns['api_communication']['patterns']:
                        if 'patterns' not in behavior_patterns['api_communication']:
                            behavior_patterns['api_communication']['patterns'] = []
                        behavior_patterns['api_communication']['patterns'].append('axios')

            except Exception as e:
                logger.debug(f"Error analyzing behavior patterns in {file_path}: {e}")
                continue

        # Store state management patterns
        if state_management_patterns:
            behavior_patterns['state_management'] = {
                'patterns': sorted(list(state_management_patterns))
            }

        # Store component type patterns
        if client_component_patterns or server_component_patterns:
            behavior_patterns['component_types'] = {
                'client_components_count': len(client_component_patterns),
                'server_components_count': len(server_component_patterns),
                'uses_client_directive': len(client_component_patterns) > 0
            }

        patterns_count = len(behavior_patterns['error_handling']['messages']) + len(behavior_patterns['loading_states']['indicators'])
        logger.info(f"Behavior pattern analysis complete: found {patterns_count} patterns")

        return behavior_patterns

    def analyze_ux_patterns(self, files: Dict[str, List[Path]]) -> UXPatternDict:
        """
        Analyze UX flow patterns (navigation, permissions).

        Args:
            files: Dict with files grouped by type

        Returns:
            UXPatternDict with UX patterns and usage
        """
        logger.info("Analyzing UX patterns")

        ux_patterns: UXPatternDict = {
            'navigation': {'routing': [], 'breadcrumbs': [], 'back_buttons': []},
            'permissions': {'auth_guards': [], 'role_checks': [], 'fallbacks': []},
            'offline_handling': {'detection': [], 'fallbacks': [], 'sync': []},
            'accessibility': {'aria': [], 'keyboard': [], 'screen_readers': []}
        }

        # Track Next.js specific patterns
        nextjs_patterns = set()
        file_organization = {
            'app_router_routes': [],
            'route_groups': [],
            'dynamic_routes': [],
            'component_dirs': set(),
            'layout_files': []
        }

        # Analyze TSX/JSX files for UX patterns
        ui_files = files.get('tsx', []) + files.get('jsx', [])

        # Detect Next.js app router structure
        app_dir = self.project_path / 'app' / '(app)'
        if app_dir.exists():
            nextjs_patterns.add('app_router')
            # Find routes
            for route_dir in app_dir.iterdir():
                if route_dir.is_dir():
                    file_organization['app_router_routes'].append(str(route_dir.name))

        # Check for route groups (folders with parentheses)
        for file_path in ui_files:
            rel_path = file_path.relative_to(self.project_path)
            path_str = str(rel_path)

            # Detect route groups
            if '(' in path_str and ')' in path_str:
                nextjs_patterns.add('route_groups')

            # Detect dynamic routes
            if '[' in path_str and ']' in path_str:
                nextjs_patterns.add('dynamic_routes')

            # Track layout files
            if file_path.name == 'layout.tsx':
                file_organization['layout_files'].append(str(rel_path))

            # Track component organization
            if 'components' in path_str:
                parts = Path(path_str).parts
                if 'components' in parts:
                    idx = parts.index('components')
                    if idx + 1 < len(parts):
                        file_organization['component_dirs'].add(parts[idx + 1])

        for file_path in ui_files:
            try:
                content = file_path.read_text(encoding='utf-8')

                # Find navigation patterns
                if 'useRouter' in content:
                    if 'next_router' not in ux_patterns['navigation']['routing']:
                        ux_patterns['navigation']['routing'].append('next_router')
                elif 'useNavigate' in content:
                    if 'react_router' not in ux_patterns['navigation']['routing']:
                        ux_patterns['navigation']['routing'].append('react_router')

                # Detect Link components
                if '<Link' in content and 'next/link' in content:
                    nextjs_patterns.add('next_link')

                # Find accessibility patterns
                aria_match = re.search(r'aria-\w+', content)
                if aria_match and 'aria_attributes_detected' not in ux_patterns['accessibility']['aria']:
                    ux_patterns['accessibility']['aria'].append('aria_attributes_detected')

                # Detect authentication patterns
                if 'useAuth' in content or 'AuthProvider' in content:
                    if 'auth_context' not in ux_patterns['permissions']['auth_guards']:
                        ux_patterns['permissions']['auth_guards'].append('auth_context')

                # Detect Supabase authentication
                if 'supabase' in content.lower() and ('signIn' in content or 'signOut' in content or 'auth' in content):
                    if 'supabase_auth' not in ux_patterns['permissions']['auth_guards']:
                        ux_patterns['permissions']['auth_guards'].append('supabase_auth')

            except Exception as e:
                logger.debug(f"Error analyzing UX patterns in {file_path}: {e}")
                continue

        # Store Next.js patterns
        if nextjs_patterns:
            ux_patterns['nextjs_features'] = sorted(list(nextjs_patterns))

        # Store file organization patterns
        if file_organization['app_router_routes'] or file_organization['component_dirs']:
            ux_patterns['file_organization'] = {
                'routes': file_organization['app_router_routes'],
                'component_directories': sorted(list(file_organization['component_dirs'])),
                'layout_count': len(file_organization['layout_files'])
            }

        patterns_count = len(ux_patterns['navigation']['routing']) + len(ux_patterns['accessibility']['aria'])
        logger.info(f"UX pattern analysis complete: found {patterns_count} patterns")

        return ux_patterns

    def build_component_index(self, files: Dict[str, List[Path]]) -> List[ComponentMetadataDict]:
        """
        Build comprehensive component inventory.

        Args:
            files: Dict with files grouped by type

        Returns:
            List of ComponentMetadataDict with component metadata
        """
        logger.info("Building component index")

        components: List[ComponentMetadataDict] = []

        # Analyze TSX/JSX files for component definitions
        ui_files = files.get('tsx', []) + files.get('jsx', [])

        # Pattern to find React component declarations
        component_pattern = re.compile(r'(?:export\s+(?:default\s+)?)?(?:function|const)\s+(\w+)\s*[=:]')

        for file_path in ui_files:
            try:
                content = file_path.read_text(encoding='utf-8')

                matches = component_pattern.findall(content)
                for component_name in matches:
                    # Skip non-component functions (lowercase first letter)
                    if not component_name[0].isupper():
                        continue

                    component: ComponentMetadataDict = {
                        'name': component_name,
                        'type': 'ui',
                        'usage_count': 0,  # Would need full analysis to determine
                        'status': 'active',
                        'props': [],  # Would need AST parsing for accurate extraction
                        'file_path': str(file_path.relative_to(self.project_path)),
                        'notes': f'Discovered in {file_path.name}'
                    }
                    components.append(component)

            except Exception as e:
                logger.debug(f"Error building component index for {file_path}: {e}")
                continue

        logger.info(f"Component index complete: found {len(components)} components")

        return components

    def generate_ui_standards_doc(self, patterns: UIPatternDict) -> str:
        """
        Generate UI-STANDARDS.md content from discovered UI patterns.

        Args:
            patterns: UIPatternDict with UI patterns

        Returns:
            Markdown formatted standards document
        """
        project_name = self.project_path.name
        date = datetime.now().strftime('%Y-%m-%d')

        doc = f"""# UI Standards

**Generated**: {date}
**Project**: {project_name}
**Pattern Discovery**: {self.scan_depth}

---

## Overview

This document defines the UI standards discovered in the {project_name} codebase through automated pattern analysis.

"""

        # Component Library section
        if patterns.get('shadcn_components'):
            doc += "## Component Library\n\n"
            doc += "**Framework**: shadcn/ui\n\n"
            doc += "**Components in Use**:\n"
            for comp in patterns['shadcn_components']:
                doc += f"- `{comp}`\n"
            doc += "\n"

        # Icons section
        if patterns['icons']['library'] != 'unknown':
            doc += "## Icons\n\n"
            doc += f"**Library**: {patterns['icons']['library']}\n\n"

        # Buttons section
        doc += "## Buttons\n\n"
        if patterns['buttons']['sizes']:
            doc += f"**Discovered Sizes**: {', '.join(patterns['buttons']['sizes'])}\n\n"
        if patterns['buttons']['variants']:
            doc += f"**Discovered Variants**: {', '.join(patterns['buttons']['variants'])}\n\n"
        if not patterns['buttons']['sizes'] and not patterns['buttons']['variants']:
            doc += "*No button patterns discovered*\n\n"

        # Modals section
        doc += "## Modals & Dialogs\n\n"
        if patterns['modals']['sizes']:
            doc += f"**Discovered Sizes**: {', '.join(patterns['modals']['sizes'])}\n\n"
        else:
            doc += "*No modal patterns discovered*\n\n"

        # Styling section
        if patterns.get('tailwind_patterns'):
            doc += "## Styling\n\n"
            doc += "**Framework**: Tailwind CSS\n\n"
            doc += "**Common Patterns**:\n"
            for pattern in patterns['tailwind_patterns']:
                doc += f"- `{pattern}`\n"
            doc += "\n"

        # Colors section
        doc += "## Colors\n\n"

        # Check if theme system was detected
        if patterns.get('theme_system') and patterns['theme_system']['detected']:
            theme = patterns['theme_system']
            theme_file_rel = str(theme['theme_file'].relative_to(self.project_path)) if theme['theme_file'] else 'unknown'

            doc += f"**Theme System**: {theme['color_count']}-Color Palette (see `{theme_file_rel}` for complete specification)\n\n"

            # Core theme colors
            doc += f"### Core Theme Colors ({theme['color_count']} colors)\n"
            if theme['hook_name']:
                doc += f"All components MUST use theme colors via `{theme['hook_name']}` hook - never hardcoded hex values.\n\n"
            else:
                doc += "All components MUST use theme colors - never hardcoded hex values.\n\n"

            doc += "```typescript\n"
            if theme['hook_name']:
                doc += f"const {{ colors }} = {theme['hook_name']}();\n\n"
            else:
                doc += "const { colors } = useThemeColors();\n\n"

            # List all color properties
            doc += "// Available colors\n"
            for color_name in theme['colors']:
                doc += f"colors.{color_name}\n"
            doc += "```\n\n"

            # Available themes
            doc += f"### Available Themes ({len(theme['theme_names'])} themes)\n"
            doc += ", ".join(theme['theme_names']) + "\n\n"
            doc += f"Each theme provides {theme['color_count']} color values (light + dark modes).\n\n"

            # Usage pattern
            doc += "### Usage Pattern\n\n"
            doc += "**ALWAYS use theme colors:**\n\n"
            doc += "```tsx\n"
            doc += "// ✅ CORRECT\n"
            doc += "<View style={{ backgroundColor: colors.surface }}>\n"
            doc += "  <Text style={{ color: colors.text }}>Hello</Text>\n"
            doc += "</View>\n\n"
            doc += "// ❌ WRONG - Never hardcode colors\n"
            doc += "<View style={{ backgroundColor: '#ffffff' }}>\n"
            doc += "  <Text style={{ color: '#000000' }}>Hello</Text>\n"
            doc += "</View>\n"
            doc += "```\n\n"

            # Anti-patterns found
            if patterns.get('hardcoded_violations'):
                violations = patterns['hardcoded_violations']
                doc += "### Anti-patterns Found\n\n"
                doc += f"⚠️ **{violations['count']} hardcoded hex colors detected in {len(violations['files'])} files**\n\n"

                # Show top 3 common violations
                if violations['common_colors']:
                    sorted_colors = sorted(violations['common_colors'].items(), key=lambda x: x[1], reverse=True)
                    doc += "**Common violations:**\n"
                    for color, count in sorted_colors[:3]:
                        doc += f"- `{color}` ({count} occurrences)\n"
                    doc += "\n"

                doc += f"**Reference:** `{theme_file_rel}` for complete theme definitions\n\n"
        else:
            # Fallback to hardcoded color discovery
            if patterns['colors']['hex_codes']:
                doc += "**Discovered Colors**:\n"
                for color in patterns['colors']['hex_codes'][:20]:  # Limit to first 20
                    doc += f"- `{color}`\n"
                if len(patterns['colors']['hex_codes']) > 20:
                    doc += f"\n*...and {len(patterns['colors']['hex_codes']) - 20} more*\n"
                doc += "\n"
            else:
                doc += "*No color patterns discovered*\n\n"

        doc += "---\n\n*Generated by docs-mcp establish_standards tool*\n"

        return doc

    def generate_behavior_standards_doc(self, patterns: BehaviorPatternDict) -> str:
        """
        Generate BEHAVIOR-STANDARDS.md content from discovered behavior patterns.

        Args:
            patterns: BehaviorPatternDict with behavior patterns

        Returns:
            Markdown formatted standards document
        """
        project_name = self.project_path.name
        date = datetime.now().strftime('%Y-%m-%d')

        doc = f"""# Behavior Standards

**Generated**: {date}
**Project**: {project_name}
**Pattern Discovery**: {self.scan_depth}

---

## Overview

This document defines the behavior standards discovered in the {project_name} codebase.

"""

        # Component Types section
        if patterns.get('component_types'):
            doc += "## Component Architecture\n\n"
            ct = patterns['component_types']
            doc += f"**Server Components**: {ct['server_components_count']}\n"
            doc += f"**Client Components**: {ct['client_components_count']}\n"
            if ct['uses_client_directive']:
                doc += f"\n**Pattern**: Uses `'use client'` directive for client-side components\n"
            doc += "\n"

        # State Management section
        if patterns.get('state_management'):
            doc += "## State Management\n\n"
            doc += "**Patterns in Use**:\n"
            for pattern in patterns['state_management']['patterns']:
                doc += f"- {pattern}\n"
            doc += "\n"

        # Error Handling section
        doc += "## Error Handling\n\n"
        if patterns['error_handling']['patterns']:
            doc += "**Patterns**:\n"
            for pattern in patterns['error_handling']['patterns']:
                doc += f"- {pattern}\n"
            doc += "\n"

        if patterns['error_handling']['messages']:
            doc += "**Common Error Messages**:\n\n"
            for msg in patterns['error_handling']['messages'][:10]:
                doc += f"- `{msg}`\n"
            if len(patterns['error_handling']['messages']) > 10:
                doc += f"\n*...and {len(patterns['error_handling']['messages']) - 10} more*\n"
            doc += "\n"

        if not patterns['error_handling']['patterns'] and not patterns['error_handling']['messages']:
            doc += "*No error handling patterns discovered*\n\n"

        # Notifications section
        if patterns['toasts']['types']:
            doc += "## Notifications\n\n"
            doc += "**Toast Library**: Detected\n"
            doc += "**Types**: " + ", ".join(patterns['toasts']['types']) + "\n\n"

        # Loading States section
        doc += "## Loading States\n\n"
        if patterns['loading_states']['indicators']:
            doc += "*Loading state patterns detected in codebase*\n\n"
        else:
            doc += "*No loading state patterns discovered*\n\n"

        # API Communication section
        if patterns.get('api_communication') and patterns['api_communication'].get('patterns'):
            doc += "## API Communication\n\n"
            doc += "**Patterns**:\n"
            for pattern in patterns['api_communication']['patterns']:
                doc += f"- {pattern}\n"
            doc += "\n"

        doc += "---\n\n*Generated by docs-mcp establish_standards tool*\n"

        return doc

    def generate_ux_patterns_doc(self, patterns: UXPatternDict) -> str:
        """
        Generate UX-PATTERNS.md content from discovered UX patterns.

        Args:
            patterns: UXPatternDict with UX patterns

        Returns:
            Markdown formatted patterns document
        """
        project_name = self.project_path.name
        date = datetime.now().strftime('%Y-%m-%d')

        doc = f"""# UX Patterns

**Generated**: {date}
**Project**: {project_name}
**Pattern Discovery**: {self.scan_depth}

---

## Overview

This document defines the UX patterns discovered in the {project_name} codebase.

"""

        # Next.js Features section
        if patterns.get('nextjs_features'):
            doc += "## Next.js Features\n\n"
            doc += "**Detected Features**:\n"
            for feature in patterns['nextjs_features']:
                doc += f"- {feature}\n"
            doc += "\n"

        # File Organization section
        if patterns.get('file_organization'):
            doc += "## File Organization\n\n"
            fo = patterns['file_organization']
            if fo['routes']:
                doc += "**App Router Routes**:\n"
                for route in fo['routes']:
                    doc += f"- `/{route}`\n"
                doc += "\n"
            if fo['component_directories']:
                doc += "**Component Directories**:\n"
                for dir_name in fo['component_directories']:
                    doc += f"- `components/{dir_name}/`\n"
                doc += "\n"
            if fo['layout_count'] > 0:
                doc += f"**Layout Files**: {fo['layout_count']} layouts detected\n\n"

        # Navigation section
        doc += "## Navigation\n\n"
        if patterns['navigation']['routing']:
            doc += "**Routing Pattern**: " + ", ".join(patterns['navigation']['routing']) + "\n\n"
        else:
            doc += "*No navigation patterns discovered*\n\n"

        # Authentication & Permissions section
        if patterns['permissions']['auth_guards']:
            doc += "## Authentication & Permissions\n\n"
            doc += "**Authentication Patterns**:\n"
            for pattern in patterns['permissions']['auth_guards']:
                doc += f"- {pattern}\n"
            doc += "\n"

        # Accessibility section
        doc += "## Accessibility\n\n"
        if patterns['accessibility']['aria']:
            doc += "**Accessibility Features**:\n"
            for feature in patterns['accessibility']['aria']:
                doc += f"- {feature}\n"
            doc += "\n"
        else:
            doc += "*No accessibility patterns discovered*\n\n"

        doc += "---\n\n*Generated by docs-mcp establish_standards tool*\n"

        return doc

    def generate_component_index_doc(self, components: List[ComponentMetadataDict]) -> str:
        """
        Generate COMPONENT-INDEX.md content from component inventory.

        Args:
            components: List of ComponentMetadataDict

        Returns:
            Markdown formatted component inventory
        """
        project_name = self.project_path.name
        date = datetime.now().strftime('%Y-%m-%d')

        doc = f"""# Component Index

**Generated**: {date}
**Project**: {project_name}
**Total Components**: {len(components)}

---

## Component Inventory

"""

        if components:
            doc += "| Component | Type | Status | File Path |\n"
            doc += "|-----------|------|--------|----------|\n"
            for comp in components:
                doc += f"| {comp['name']} | {comp['type']} | {comp['status']} | {comp['file_path']} |\n"
        else:
            doc += "*No components discovered*\n"

        doc += "\n---\n\n*Generated by docs-mcp establish_standards tool*\n"

        return doc

    def save_standards(self, standards_dir: Path) -> StandardsResultDict:
        """
        Save all generated standards documents to disk.

        Args:
            standards_dir: Directory to save standards documents

        Returns:
            StandardsResultDict with save results
        """
        logger.info(f"Saving standards to {standards_dir}")

        # Ensure directory exists
        standards_dir.mkdir(parents=True, exist_ok=True)

        # Scan codebase
        files = self.scan_codebase()

        # Analyze patterns
        ui_patterns = self.analyze_ui_patterns(files)
        behavior_patterns = self.analyze_behavior_patterns(files)
        ux_patterns = self.analyze_ux_patterns(files)
        components = self.build_component_index(files)

        # Generate documents
        ui_doc = self.generate_ui_standards_doc(ui_patterns)
        behavior_doc = self.generate_behavior_standards_doc(behavior_patterns)
        ux_doc = self.generate_ux_patterns_doc(ux_patterns)
        component_doc = self.generate_component_index_doc(components)

        # Save files
        saved_files = []

        ui_path = standards_dir / Files.UI_STANDARDS
        ui_path.write_text(ui_doc, encoding='utf-8')
        saved_files.append(str(ui_path))

        behavior_path = standards_dir / Files.BEHAVIOR_STANDARDS
        behavior_path.write_text(behavior_doc, encoding='utf-8')
        saved_files.append(str(behavior_path))

        ux_path = standards_dir / Files.UX_PATTERNS
        ux_path.write_text(ux_doc, encoding='utf-8')
        saved_files.append(str(ux_path))

        component_path = standards_dir / Files.COMPONENT_INDEX
        component_path.write_text(component_doc, encoding='utf-8')
        saved_files.append(str(component_path))

        # Calculate totals
        ui_count = (len(ui_patterns.get('buttons', {}).get('sizes', [])) +
                    len(ui_patterns.get('modals', {}).get('sizes', [])) +
                    len(ui_patterns.get('colors', {}).get('hex_codes', [])))

        behavior_count = (len(behavior_patterns.get('error_handling', {}).get('messages', [])) +
                         len(behavior_patterns.get('loading_states', {}).get('indicators', [])))

        ux_count = (len(ux_patterns.get('navigation', {}).get('routing', [])) +
                   len(ux_patterns.get('accessibility', {}).get('aria', [])))

        result: StandardsResultDict = {
            'files': saved_files,
            'patterns_count': ui_count + behavior_count + ux_count,
            'success': True,
            'ui_patterns_count': ui_count,
            'behavior_patterns_count': behavior_count,
            'ux_patterns_count': ux_count,
            'components_count': len(components)
        }

        logger.info("Standards saved successfully", extra={
            'files_created': len(saved_files),
            'total_patterns': result['patterns_count'],
            'components': len(components)
        })

        return result
