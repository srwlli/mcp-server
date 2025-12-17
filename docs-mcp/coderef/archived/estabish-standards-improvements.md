MCP Tool Enhancement: Theme-Aware Color Detection

  Problem Statement

  The establish-standards tool (located at C:\Users\willh\.mcp-servers\docs-mcp\) scans codebases to generate coding standards documents. Currently, its color detection logic reports hardcoded hex values
  instead of recognizing centralized theme systems.

  Current behavior:
  ## Colors

  **Discovered Colors**:
  - `#000000`
  - `#ffffff`
  - `#10b981`
  - `#ef4444`
  ...and 30 more

  Desired behavior:
  ## Colors

  **Theme System**: 18-Color Palette (see `improvements/visual-user-feedback-inventory.json`)

  ### Core Theme Colors (7 colors)
  All components MUST use theme colors via `useThemeColors` hook - never hardcoded hex values.

  const { colors } = useThemeColors();

  colors.background      // App background
  colors.surface         // Card/surface backgrounds
  colors.text            // Primary text
  ...

  ### Available Themes (10 themes)
  - Monochrome, Ocean, Crimson, Sepia, Nord, Forest, Lavender, Amber, Midnight, Rose

  ### Anti-patterns Found
  ⚠️ 42 hardcoded hex colors detected in 18 files - should use theme system instead

  ---
  Root Cause

  The scanner uses usage-based pattern discovery (what it finds in code) instead of architectural pattern recognition (what the standard should be).

  It discovers hardcoded colors scattered throughout the codebase (anti-patterns) and documents them as "standards" when it should instead:
  1. Detect the centralized theme system
  2. Document the theme system as the standard
  3. Flag hardcoded colors as violations

  ---
  Solution Requirements

  1. Theme System Detection Logic

  Add intelligence to detect theme systems by looking for:

  File patterns:
  - constants/theme.ts, constants/colors.ts
  - theme/colors.ts, theme/index.ts
  - hooks/use-theme-colors.ts, hooks/useTheme.ts

  Code patterns:
  - TypeScript interfaces like ColorScheme, ThemeName, ThemeMetadata
  - Export statements with theme objects: export const Themes = { ... }
  - Hook exports: export function useThemeColors() { ... }
  - Color properties with semantic names: background, surface, text, tint, border

  Usage patterns:
  - Count hooks usage: const { colors } = useThemeColors()
  - Count hardcoded colors: backgroundColor: "#fff"
  - If theme usage > 20%, theme system exists

  ---
  2. Detection Algorithm

  function detectColorStandards(codebase):
      # Step 1: Look for theme system
      themeFiles = glob([
          "**/constants/theme*.{ts,js}",
          "**/theme/colors*.{ts,js}",
          "**/constants/colors*.{ts,js}"
      ])

      hookFiles = glob([
          "**/hooks/use*[Tt]heme*.{ts,tsx,js}",
          "**/hooks/use*[Cc]olor*.{ts,tsx,js}"
      ])

      # Step 2: Parse theme structure if found
      if themeFiles or hookFiles:
          themeSystem = parseThemeSystem(themeFiles, hookFiles)

          if themeSystem.isValid:
              hardcodedColors = findHardcodedColors(codebase)

              return {
                  type: "theme_system",
                  standard: themeSystem,
                  violations: hardcodedColors
              }

      # Step 3: Fallback to hardcoded color discovery
      return {
          type: "hardcoded",
          colors: findHardcodedColors(codebase)
      }

  function parseThemeSystem(themeFiles, hookFiles):
      # Parse theme constant file
      themeFile = themeFiles[0]
      ast = parseTypeScript(themeFile)

      # Extract color scheme properties
      colorScheme = extractInterface(ast, "ColorScheme")
      themes = extractExport(ast, "Themes")

      # Extract hook name
      hookName = extractHookExport(hookFiles[0]) if hookFiles else null

      return {
          isValid: colorScheme and themes,
          file: themeFile,
          hook: hookName,
          colors: colorScheme.properties,
          themeNames: Object.keys(themes)
      }

  ---
  3. Example Theme System Structure

  Reference: C:\Users\willh\Desktop\projects\noted\constants\theme.ts

  export type ThemeName = 'monochrome' | 'ocean' | 'crimson' | ...;

  interface ColorScheme {
    // Core colors (7)
    background: string;
    surface: string;
    text: string;
    textSecondary: string;
    border: string;
    tint: string;
    icon: string;

    // Extended colors (11)
    elevatedSurface: string;
    selectedSurface: string;
    overlay: string;
    hover: string;
    pressed: string;
    disabled: string;
    highlight: string;
    linkColor: string;
    accentSecondary: string;
  }

  export const Themes: Record<ThemeName, ThemeMetadata> = {
    monochrome: { light: {...}, dark: {...} },
    ocean: { light: {...}, dark: {...} },
    // ... 8 more themes
  };

  Hook: hooks/use-theme-colors.ts
  export function useThemeColors() {
    const { themeName } = useThemeController();
    const colorScheme = useColorScheme();
    return Themes[themeName][colorScheme];
  }

  ---
  4. Output Template

  When theme system detected, generate:

  ## Colors

  **Theme System**: [N]-Color Palette (see `[FILE_PATH]` for complete specification)

  ### Core Theme Colors ([N] colors)
  All components MUST use theme colors via `[HOOK_NAME]` hook - never hardcoded hex values.

  ```typescript
  const { colors } = [HOOK_NAME]();

  // Core colors
  [FOR EACH CORE COLOR]
  colors.[COLOR_NAME]  // [DESCRIPTION]
  [END FOR]

  Phase 2 Extended Colors ([N] colors)

  [IF EXTENDED COLORS EXIST]
  [FOR EACH EXTENDED COLOR]
  colors.[COLOR_NAME]  // [DESCRIPTION]
  [END FOR]

  Available Themes ([N] themes)

  [LIST THEME NAMES]

  Each theme provides [N] color values ([X] colors × 2 modes: light + dark).

  Usage Pattern

  ALWAYS use theme colors:
  // ✅ CORRECT
  <View style={{ backgroundColor: colors.surface }}>
    <Text style={{ color: colors.text }}>Hello</Text>
  </View>

  // ❌ WRONG - Never hardcode colors
  <View style={{ backgroundColor: '#ffffff' }}>
    <Text style={{ color: '#000000' }}>Hello</Text>
  </View>

  Anti-patterns Found

  ⚠️ [COUNT] hardcoded hex colors detected in [N] files
  Common violations: [LIST TOP 3 WITH COUNTS]

  Reference: [THEME_FILE_PATH] for complete theme definitions

  ---

  ### 5. Files to Modify in MCP Tool

  Look for these files in `C:\Users\willh\.mcp-servers\docs-mcp\`:
  - Color detection/scanning logic (likely in a `scan` or `analyze` directory)
  - UI-STANDARDS.md template generator
  - Pattern discovery utilities

  ---

  ## Test Case

  **Test codebase:** `C:\Users\willh\Desktop\projects\noted`

  **Expected detection:**
  - Theme file: `constants/theme.ts`
  - Hook: `useThemeColors` (from `hooks/use-theme-colors.ts`)
  - Color count: 18 colors (7 core + 11 extended)
  - Themes: 10 (Monochrome, Ocean, Crimson, Sepia, Nord, Forest, Lavender, Amber, Midnight, Rose)
  - Violations: ~42 hardcoded colors in ~18 files

  **Run test:**
  ```bash
  cd C:\Users\willh\Desktop\projects\noted
  # Call establish_standards tool
  # Verify Colors section documents theme system, not hardcoded values

  ---
  Success Criteria

  1. ✅ Tool detects constants/theme.ts as theme system
  2. ✅ Tool parses 18 color names from ColorScheme interface
  3. ✅ Tool identifies useThemeColors hook
  4. ✅ Tool extracts 10 theme names
  5. ✅ Generated UI-STANDARDS.md Colors section documents theme system
  6. ✅ Hardcoded colors listed as "Anti-patterns" warning
  7. ✅ Re-running establish-standards preserves theme documentation