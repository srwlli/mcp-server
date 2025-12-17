# NFL Scraper Project - Context for Persona Integration

**Purpose**: Context document for nfl-scraper-expert.json persona
**Created**: 2025-10-20 (Session 4+)
**Status**: ✅ Production Tested

---

## 📍 PROJECT LOCATION

**Main Project Directory**:
```
C:\Users\willh\Desktop\projects\next-scraper\
```

---

## 🗺️ CRITICAL NAVIGATION FILES

### For New Agents - READ IN THIS ORDER:

1. **PROJECT-MAP.md** - 🎯 START HERE
   - **Location**: `C:\Users\willh\Desktop\projects\next-scraper\PROJECT-MAP.md`
   - **Purpose**: Complete navigation guide with file locations
   - **Contains**: Project structure tree, absolute paths, task-based navigation
   - **Length**: 350+ lines

2. **CLAUDE.md** - Project History & Overview
   - **Location**: `C:\Users\willh\Desktop\projects\next-scraper\CLAUDE.md`
   - **Purpose**: Full development log across all 4 sessions
   - **Contains**: Scraper details, database schema, performance metrics
   - **Status**: References PROJECT-MAP.md at top (line 3)

3. **communication.json** - Session Changelog
   - **Location**: `C:\Users\willh\Desktop\projects\next-scraper\communication.json`
   - **Purpose**: Session-by-session changes log
   - **Contains**: What each agent did, files modified, commits made
   - **Status**: References PROJECT-MAP.md in header (lines 1-21)

4. **DATABASE-ACCESS-GUIDE.md** - Database Instructions
   - **Location**: `C:\Users\willh\Desktop\projects\next-scraper\DATABASE-ACCESS-GUIDE.md`
   - **Purpose**: Step-by-step database connection & query patterns
   - **Contains**: 600+ lines with schema patterns, troubleshooting, examples
   - **Status**: Has "WHERE TO FIND CRITICAL FILES" section at top (lines 9-56)

5. **SESSION-PHASE-1-DEPLOYMENT.md** - Latest Technical Details
   - **Location**: `C:\Users\willh\Desktop\projects\next-scraper\SESSION-PHASE-1-DEPLOYMENT.md`
   - **Purpose**: Phase 1 deployment technical details
   - **Contains**: Migration fixes, testing results, performance metrics
   - **Status**: Has "QUICK FILE REFERENCE" section at top (lines 10-33)

---

## 🗄️ DATABASE CONNECTION INFORMATION

### Supabase Project Details:

**Project Reference**:
- **File**: `C:\Users\willh\Desktop\projects\next-scraper\supabase\.temp\project-ref`
- **Contents**: `fuzouuxhxluqjmiyabal`
- **Purpose**: Required for `supabase link` command

**Database Credentials**:
- **File**: `C:\Users\willh\Desktop\projects\next-scraper\.env.local`
- **Variables**:
  - `NEXT_PUBLIC_SUPABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY`
- **Note**: This file is gitignored - if missing, agent must ask user

### Quick Start Commands:

```bash
# 1. Link to Supabase (required for migrations)
supabase link --project-ref fuzouuxhxluqjmiyabal

# 2. Verify Phase 1 migrations are applied
node scripts/check-migrations-applied.js

# 3. Validate data completeness
node scripts/validate-data-completeness.js
```

---

## 📊 DATABASE SCHEMA CRITICAL PATTERNS

### Games Table:
- **Primary Key**: Composite `(game_id, season)` - **NO `id` column**
- **Status Enum**: `'scheduled'` | `'in_progress'` | `'final'` (NOT `'completed'`)
- **Team Columns**: `home_team_id`, `away_team_id` (with `_id` suffix)

### Teams Table:
- **Primary Key**: `team_id` (e.g., 'KC', 'SF', 'BUF')
- **Abbreviation**: `team_abbr` (NOT `team_abbreviation`)

### Player Teams Table:
- **Season Columns**: `start_season`, `end_season` (NOT `season`)
- **Join Pattern**: Use BETWEEN clause for date ranges

### Common Query Mistakes (❌ WRONG → ✅ CORRECT):

```sql
-- ❌ WRONG: games table has NO 'id' column
SELECT id, home_team, away_team FROM games

-- ✅ CORRECT:
SELECT game_id, season, home_team_id, away_team_id FROM games

-- ❌ WRONG: Status enum is 'final' not 'completed'
WHERE status = 'completed'

-- ✅ CORRECT:
WHERE status = 'final'

-- ❌ WRONG: Team columns have _id suffix
SELECT home_team, away_team

-- ✅ CORRECT:
SELECT home_team_id, away_team_id
```

---

## 📁 PROJECT STRUCTURE OVERVIEW

```
next-scraper/
├── 📊 DATABASE FILES
│   ├── .env.local                               → Database credentials
│   ├── supabase/
│   │   ├── .temp/project-ref                    → fuzouuxhxluqjmiyabal
│   │   └── migrations/*.sql                     → Schema definitions
│   └── DATABASE-ACCESS-GUIDE.md                 → Connection instructions
│
├── 📋 DOCUMENTATION
│   ├── PROJECT-MAP.md                           → 🎯 Navigation guide
│   ├── CLAUDE.md                                → Development log
│   ├── communication.json                       → Session changelog
│   └── SESSION-PHASE-1-DEPLOYMENT.md           → Phase 1 details
│
├── 🔧 SCRIPTS
│   ├── scripts/
│   │   ├── seed/                                → Initial data loaders (4 scripts)
│   │   ├── scrapers/                            → Data collectors (8 scrapers)
│   │   ├── utils/                               → Shared utilities
│   │   ├── check-migrations-applied.js          → Verify migrations
│   │   ├── validate-data-completeness.js        → Check coverage
│   │   └── verify-phase1-fields.js              → Check fantasy fields
│   └── scheduler.js                             → Automation
│
└── 📝 CONFIG
    ├── package.json                             → Dependencies
    └── logs/                                    → Winston logs
```

---

## 🚀 VALIDATION SCRIPTS

### 1. Check Migrations Applied
```bash
node scripts/check-migrations-applied.js
```

**Expected Output**:
```
✅ Migration 20250101000020 applied (player_game_stats enhanced)
✅ Migration 20250101000021 applied (weekly aggregation tables exist)
=== SUMMARY ===
✅ All Phase 1 migrations applied - Ready for testing!
```

### 2. Validate Data Completeness
```bash
node scripts/validate-data-completeness.js
```

**Expected Output**:
```
📊 PHASE 1 DATA COMPLETENESS SUMMARY
✅ Player Game Stats: 3,817 records with fantasy points
✅ Weekly Leaders: 110 records
✅ Season Cumulative: 811 player records
✅ Team Stats: 188 records
✅ Scoring Plays: 820 records
⚠️  Games Missing Stats: 0/94 (100% coverage)

Overall Status: ✅ EXCELLENT
```

### 3. Verify Phase 1 Fields
```bash
node scripts/verify-phase1-fields.js
```

**Expected Output**:
```
📈 Phase 1 Field Coverage:
   Fantasy Points (PPR): 3817 records
   Passing Sacks: 58 records
   Receiving Targets: 412 records
✅ Phase 1 fields successfully populated!
```

---

## 📊 PROJECT STATUS (Current)

**Phase**: Phase 1 COMPLETE ✅
**Data Coverage**: 303/674 fields operational (45%)
**Game Coverage**: 100% (94/94 completed games have stats)
**Scrapers**: 7/8 operational (player news planned)
**Database**: 46 tables, 303 fields live
**Next Phase**: Phase 2 (Betting + Snaps + Trending)

---

## 🎯 FIRST-TIME AGENT CHECKLIST

When an agent starts work on this project:

1. ✅ **Read PROJECT-MAP.md** - Complete navigation guide
2. ✅ **Read CLAUDE.md** - Project overview and history
3. ✅ **Read communication.json** - Session changelog
4. ✅ **Link to database**:
   ```bash
   supabase link --project-ref fuzouuxhxluqjmiyabal
   ```
5. ✅ **Verify Phase 1**:
   ```bash
   node scripts/check-migrations-applied.js
   ```
6. ✅ **Validate data**:
   ```bash
   node scripts/validate-data-completeness.js
   ```
7. ✅ **Read DATABASE-ACCESS-GUIDE.md** - Query patterns
8. ✅ **Check for new tasks** - Review user's request

---

## 🔧 COMMON TROUBLESHOOTING

### "Cannot find project ref"
- **File**: `C:\Users\willh\Desktop\projects\next-scraper\supabase\.temp\project-ref`
- **Command**: `cat supabase/.temp/project-ref`
- **Should show**: `fuzouuxhxluqjmiyabal`
- **Note**: CLI linking is NOT persistent across sessions

### "Column does not exist" errors
- **Cause**: Using wrong column names
- **Fix**: Check DATABASE-ACCESS-GUIDE.md lines 113-142
- **Common mistakes**:
  - Using `id` instead of `(game_id, season)`
  - Using `home_team` instead of `home_team_id`
  - Using `'completed'` instead of `'final'`

### "Foreign key constraint violations"
- **Cause**: Missing players in database
- **Fix**: Run `npm run scrape:roster` then re-scrape games
- **Why**: Practice squad callups, mid-season signings not in initial seed

### "Missing .env.local file"
- **Cause**: File is gitignored
- **Fix**: Ask user to provide credentials
- **Required vars**:
  - `NEXT_PUBLIC_SUPABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY`

---

## 🆘 WHERE TO GET HELP

If an agent needs specific information:

| Need | File | Location |
|------|------|----------|
| Project navigation | PROJECT-MAP.md | Lines 1-350+ |
| Database connection | DATABASE-ACCESS-GUIDE.md | Lines 9-56 (critical files) |
| Schema patterns | DATABASE-ACCESS-GUIDE.md | Lines 113-142 |
| Query examples | DATABASE-ACCESS-GUIDE.md | Lines 78-110 |
| Session history | communication.json | Lines 1-396 |
| Phase 1 details | SESSION-PHASE-1-DEPLOYMENT.md | Lines 10-278 |
| Troubleshooting | DATABASE-ACCESS-GUIDE.md | Lines 285-393 |

---

## 📝 INTEGRATION WITH NFL-SCRAPER-EXPERT PERSONA

### How this context should be used:

**In nfl-scraper-expert.json system prompt**:

1. **Add reference to PROJECT-MAP.md** in "Your Mission" section:
   ```
   - Always direct new agents to read PROJECT-MAP.md first for complete navigation
   ```

2. **Add reference to database connection pattern**:
   ```
   - Before any database operations, verify connection via:
     supabase link --project-ref fuzouuxhxluqjmiyabal
   ```

3. **Add validation step reminder**:
   ```
   - After any database changes, run validation scripts:
     * node scripts/check-migrations-applied.js
     * node scripts/validate-data-completeness.js
   ```

4. **Add common error prevention**:
   ```
   - Always use correct schema patterns (see DATABASE-ACCESS-GUIDE.md):
     * games: (game_id, season) composite key
     * status: 'final' not 'completed'
     * teams: home_team_id not home_team
   ```

5. **Add documentation requirement**:
   ```
   - After completing work, update communication.json with session details
   - Reference PROJECT-MAP.md in all guidance to new agents
   ```

### Persona Behavior Adjustments:

**When greeting new agents**:
```
"Welcome! Before we start, please read PROJECT-MAP.md for complete navigation:
C:\Users\willh\Desktop\projects\next-scraper\PROJECT-MAP.md

Then verify database connection:
supabase link --project-ref fuzouuxhxluqjmiyabal
node scripts/check-migrations-applied.js
```

**When providing database guidance**:
```
"See DATABASE-ACCESS-GUIDE.md lines 113-142 for schema patterns.
Remember: games table uses (game_id, season) composite key, NOT 'id'."
```

**When agent completes work**:
```
"Please update communication.json with your session work.
Reference PROJECT-MAP.md so future agents can find their way."
```

---

## 📚 DOCUMENTATION HIERARCHY

```
PROJECT-MAP.md                       ← Start here (navigation)
    ↓
CLAUDE.md                            ← Project overview
    ↓
communication.json                   ← Session changelog
    ↓
SESSION-PHASE-1-DEPLOYMENT.md       ← Phase 1 details
    ↓
DATABASE-ACCESS-GUIDE.md            ← Database patterns
    ↓
SCHEDULER.md / DEPLOYMENT.md        ← Operations
```

---

## 🎯 KEY TAKEAWAYS FOR PERSONA

1. **Always direct to PROJECT-MAP.md first** - It's the navigation hub
2. **Database connection is NOT persistent** - Must re-link each session
3. **Schema patterns are critical** - Wrong column names = 100% query failures
4. **Validation scripts exist** - Use them before/after work
5. **Documentation is comprehensive** - 1,500+ lines across 5 major docs
6. **User feedback**: "why was it so hard to find how we are integrated with supabase?" - This led to creation of all navigation docs

---

**Last Updated**: 2025-10-20 (Session 4+)
**Status**: ✅ Complete - Ready for persona integration
**Next Step**: Update nfl-scraper-expert.json to reference this context
