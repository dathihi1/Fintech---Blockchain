# 🎨 UI/UX DESIGN GUIDE - SMART TRADING JOURNAL

## FIGMA MOCKUP REQUIREMENTS

---

## 1️⃣ DESIGN SYSTEM

### Color Palette
```css
/* Primary Colors */
--primary-600: #6366f1;      /* Indigo - Main brand */
--primary-700: #4f46e5;      /* Darker indigo - Hover */
--primary-900: #312e81;      /* Deep indigo - Text */

/* Secondary Colors */
--purple-600: #8b5cf6;       /* Purple - Accents */
--purple-700: #7c3aed;       /* Darker purple */

/* Semantic Colors */
--success-500: #10b981;      /* Green - Profit, Good */
--danger-500: #ef4444;       /* Red - Loss, Bad */
--warning-500: #f59e0b;      /* Amber - Warning */
--info-500: #3b82f6;         /* Blue - Info */

/* Emotions Colors */
--emotion-fomo: #ef4444;     /* Red */
--emotion-fear: #f59e0b;     /* Orange */
--emotion-greed: #8b5cf6;    /* Purple */
--emotion-revenge: #dc2626;  /* Dark Red */
--emotion-confidence: #10b981; /* Green */
--emotion-neutral: #6b7280;  /* Gray */

/* Background (Dark Theme) */
--bg-primary: #0f172a;       /* Dark Navy */
--bg-secondary: #1e293b;     /* Lighter Navy */
--bg-tertiary: #334155;      /* Card background */

/* Text */
--text-primary: #f1f5f9;     /* Light Gray */
--text-secondary: #94a3b8;   /* Medium Gray */
--text-tertiary: #64748b;    /* Dark Gray */

/* Borders */
--border-color: #334155;
```

### Typography
```css
/* Headings */
--font-family: 'Inter', sans-serif;

h1: 48px, Bold, Letter-spacing: -0.5px
h2: 32px, SemiBold, Letter-spacing: -0.3px
h3: 24px, SemiBold
h4: 20px, Medium

/* Body */
body: 16px, Regular, Line-height: 1.5
small: 14px, Regular
caption: 12px, Regular, Color: text-secondary

/* Code */
code: 'JetBrains Mono', 14px, Medium
```

### Spacing Scale
```
4px   (0.5 unit)
8px   (1 unit)
12px  (1.5 units)
16px  (2 units)
24px  (3 units)
32px  (4 units)
48px  (6 units)
64px  (8 units)
```

### Border Radius
```
--radius-sm: 4px   (buttons, inputs)
--radius-md: 8px   (cards)
--radius-lg: 12px  (modals)
--radius-xl: 16px  (major sections)
--radius-full: 9999px (pills, avatars)
```

### Shadows
```
--shadow-sm: 0 1px 2px rgba(0,0,0,0.1);
--shadow-md: 0 4px 6px rgba(0,0,0,0.2);
--shadow-lg: 0 10px 15px rgba(0,0,0,0.3);
--shadow-xl: 0 20px 25px rgba(0,0,0,0.4);
```

---

## 2️⃣ SCREEN LAYOUTS

### Screen 1: DASHBOARD (Main Screen)

#### Components Hierarchy
```
┌──────────────────────────────────────────────────────────┐
│ HEADER                                                    │
│ ┌──────────┬───────────────────────────────┬──────────┐ │
│ │ Logo     │ Search                        │ User Menu│ │
│ └──────────┴───────────────────────────────┴──────────┘ │
├──────────────────────────────────────────────────────────┤
│ SIDEBAR    │ MAIN CONTENT                                │
│ ┌────────┐ │ ┌──────────────────────────────────────┐  │
│ │        │ │ │ METRICS CARDS (4 cards)              │  │
│ │ Home   │ │ │ ┌─────┬─────┬─────┬─────┐           │  │
│ │ Trades │ │ │ │Total│Win  │PnL  │Emot │           │  │
│ │ Insights│ │ │ Trades│Rate│     │ions │           │  │
│ │ Settings│ │ │ └─────┴─────┴─────┴─────┘           │  │
│ │        │ │ └──────────────────────────────────────┘  │
│ │        │ │                                            │
│ │        │ │ ┌──────────────────────────────────────┐  │
│ │        │ │ │ CHARTS ROW                           │  │
│ │        │ │ │ ┌────────────┐ ┌──────────────┐     │  │
│ │        │ │ │ │PnL Timeline│ │Emotion Pie   │     │  │
│ │        │ │ │ │(Line Chart)│ │Chart         │     │  │
│ │        │ │ │ └────────────┘ └──────────────┘     │  │
│ │        │ │ └──────────────────────────────────────┘  │
│ │        │ │                                            │
│ │        │ │ ┌──────────────────────────────────────┐  │
│ │        │ │ │ RECENT TRADES TABLE                  │  │
│ │        │ │ │ Date│Symbol│Entry│Exit│PnL│Emotion  │  │
│ │        │ │ │ ────┼──────┼─────┼────┼───┼────────  │  │
│ │        │ │ │ ...│...   │...  │... │+5%│Confidence│  │
│ │        │ │ └──────────────────────────────────────┘  │
│ └────────┘ │                                            │
└──────────────────────────────────────────────────────────┘
```

#### Detailed Specs

**HEADER (Height: 64px)**
```
Left Section:
  - Logo: 32x32px icon + "Smart Trading Journal" text
  - Font: Inter Bold, 18px

Center Section:
  - Search bar: 400px wide
  - Placeholder: "Search trades, symbols..."
  - Icon: Search (lucide)

Right Section:
  - Notifications icon (Bell)
  - User avatar (40x40px, rounded-full)
  - Dropdown menu
```

**SIDEBAR (Width: 240px)**
```
Items:
  ┌─────────────────────┐
  │ 📊 Dashboard        │ ← Active (bg: primary-700)
  │ 📝 Trades           │
  │ 💡 Insights         │
  │ ⚙️  Settings         │
  └─────────────────────┘

Each item:
  - Height: 44px
  - Padding: 12px 16px
  - Border-radius: 8px
  - Hover: bg-secondary
  - Active: bg-primary-700, text-primary
  - Icon size: 20px
  - Font: Inter Medium, 15px
```

**METRICS CARDS**
```
Grid: 4 columns, gap 16px

Card Structure:
┌─────────────────┐
│ TOTAL TRADES    │ ← Label (text-secondary, 12px, uppercase)
│                 │
│    45           │ ← Value (text-primary, 32px, bold)
│                 │
│ +5 this week    │ ← Change (text-success, 14px, medium)
└─────────────────┘

Card specs:
  - Background: bg-tertiary
  - Padding: 20px
  - Border-radius: 12px
  - Border: 1px solid border-color
  - Shadow: shadow-sm
  - Height: 120px

Card 1: Total Trades
  - Icon: BarChart3 (lucide)
  - Value: 45
  - Change: "+5 this week" (green)

Card 2: Win Rate
  - Icon: TrendingUp
  - Value: 58%
  - Change: "+3% vs last month" (green)

Card 3: Total PnL
  - Icon: DollarSign
  - Value: +$1,240
  - Change: "+$320 this week" (green)

Card 4: Top Emotion
  - Icon: Brain
  - Value: FOMO (40%)
  - Change: "Most common" (amber)
```

**CHARTS ROW**
```
Grid: 2 columns (65% | 35%)

Left Chart: PnL Timeline
┌──────────────────────────┐
│ PnL Over Time            │
│ [Filters: 7D|1M|3M|All]  │
│                          │
│ [Line Chart]             │
│ - X-axis: Dates          │
│ - Y-axis: Cumulative PnL │
│ - Green line above 0     │
│ - Red line below 0       │
│                          │
│ Interactive tooltips     │
└──────────────────────────┘

Right Chart: Emotion Distribution
┌──────────────────────┐
│ Emotion Breakdown    │
│                      │
│   [Pie Chart]        │
│   - FOMO: 40% (red)  │
│   - Fear: 20% (orange)│
│   - Confidence: 25%  │
│   - Greed: 10%       │
│   - Neutral: 5%      │
│                      │
│   Legend below chart │
└──────────────────────┘

Chart specs:
  - Background: bg-tertiary
  - Padding: 24px
  - Border-radius: 12px
  - Height: 320px
```

**RECENT TRADES TABLE**
```
┌────────────────────────────────────────────────────────┐
│ Recent Trades                           [View All →]   │
├──────┬────────┬────────┬────────┬────────┬────────────┤
│ Date │ Symbol │ Entry  │ Exit   │ PnL    │ Emotion    │
├──────┼────────┼────────┼────────┼────────┼────────────┤
│ Jan24│ BTC    │ 64,200 │ 67,500 │ +5.1% ✅│ Confidence │
│ Jan23│ ETH    │ 2,450  │ 2,380  │ -2.9% ❌│ FOMO       │
│ Jan23│ BTC    │ 63,800 │ 66,100 │ +3.6% ✅│ Pattern    │
│ Jan22│ SOL    │ 98.50  │ 95.20  │ -3.4% ❌│ Fear       │
│ Jan22│ BTC    │ 62,000 │ 64,200 │ +3.5% ✅│ Greed      │
└──────┴────────┴────────┴────────┴────────┴────────────┘

Table specs:
  - Row height: 56px
  - Striped rows: alternate bg-secondary
  - Hover: bg-tertiary + cursor pointer
  - Font: Inter Regular, 14px
  - Padding: 12px 16px

PnL column:
  - Positive: text-success-500, bold
  - Negative: text-danger-500, bold
  - Icon: ✅ or ❌

Emotion column:
  - Badge style
  - Background: emotion-color with opacity 20%
  - Text: emotion-color
  - Border-radius: 6px
  - Padding: 4px 12px
  - Font: 12px, medium
```

---

### Screen 2: TRADE DETAIL PAGE

```
┌──────────────────────────────────────────────────────────┐
│ ← Back to Dashboard          [Edit] [Delete]             │
├──────────────────────────────────────────────────────────┤
│                                                           │
│ ┌───────────────────────────────────────────────────┐   │
│ │ TRADE OVERVIEW                                     │   │
│ │                                                    │   │
│ │ BTC/USDT Long                    Status: ✅ Win    │   │
│ │ Jan 24, 2026 14:30                                │   │
│ │                                                    │   │
│ │ Entry: $64,200    Exit: $67,500    PnL: +5.1%    │   │
│ │ Risk/Reward: 1:3   Position: $1,000               │   │
│ └───────────────────────────────────────────────────┘   │
│                                                           │
│ ┌────────────────────────┐  ┌──────────────────────┐   │
│ │ CANDLESTICK CHART      │  │ EMOTION ANALYSIS     │   │
│ │                        │  │                      │   │
│ │ [Chart with markers]   │  │ Note:                │   │
│ │ - Entry arrow          │  │ "Theo kế hoạch,      │   │
│ │ - Exit arrow           │  │  entry đúng setup"   │   │
│ │ - Pattern highlight    │  │                      │   │
│ │                        │  │ Detected:            │   │
│ │                        │  │ 🟢 CONFIDENCE (91%) │   │
│ │                        │  │                      │   │
│ │                        │  │ Recommendation:      │   │
│ │                        │  │ ✅ Good discipline    │   │
│ └────────────────────────┘  └──────────────────────┘   │
│                                                           │
│ ┌───────────────────────────────────────────────────┐   │
│ │ PATTERN DETECTED                                   │   │
│ │                                                    │   │
│ │ 📊 Bullish Engulfing at Support                   │   │
│ │                                                    │   │
│ │ Historical Performance:                            │   │
│ │ ████████████████░░░░ 78% Win Rate (45/58 trades)  │   │
│ │                                                    │   │
│ │ This pattern appears at strong support levels     │   │
│ │ and indicates potential reversal.                 │   │
│ └───────────────────────────────────────────────────┘   │
│                                                           │
│ ┌───────────────────────────────────────────────────┐   │
│ │ AI SUGGESTIONS                                     │   │
│ │                                                    │   │
│ │ 💡 Well executed trade! Key strengths:            │   │
│ │    - Entry at confirmed pattern                   │   │
│ │    - Proper risk management (R:R 1:3)             │   │
│ │    - Followed trading plan                        │   │
│ │                                                    │   │
│ │ 📈 Similar setups to look for:                    │   │
│ │    - Morning Star at support                      │   │
│ │    - Hammer after pullback to MA50                │   │
│ └───────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

#### Component Specs

**Trade Overview Card**
```
Layout: Flex row, space-between
Height: 140px
Padding: 24px
Background: gradient (primary-900 → primary-700)
Border-radius: 12px

Left side:
  - Symbol: BTC/USDT (24px, bold)
  - Direction badge: "LONG" (bg-success, uppercase, 12px)
  - Date: Jan 24, 2026 14:30 (text-secondary, 14px)

Right side:
  - Status badge: "✅ WIN" (bg-success, 16px, bold)

Bottom row (Metrics):
  Entry | Exit | PnL | R:R | Position
  Each metric:
    - Label: text-secondary, 12px, uppercase
    - Value: text-primary, 18px, bold
```

**Candlestick Chart**
```
Library: Lightweight Charts (TradingView)
Width: 65%
Height: 400px

Features:
  - OHLCV candlesticks
  - Entry marker (green arrow up)
  - Exit marker (red arrow down)
  - Pattern highlight (semi-transparent box)
  - RSI indicator below
  - Volume bars at bottom
  - Tooltips on hover
```

**Emotion Analysis Card**
```
Width: 35%
Padding: 20px
Background: bg-tertiary
Border-radius: 12px

Sections:
1. User Note (textarea-style box)
   - Background: bg-secondary
   - Padding: 12px
   - Border-radius: 8px
   - Font: 14px, italic

2. Detection Result
   - Emotion badge (large)
   - Confidence percentage
   - Color coded by emotion

3. Recommendation
   - Icon: CheckCircle or AlertCircle
   - Text: 14px, medium
   - Color: success or warning
```

**Pattern Detected Card**
```
Background: bg-tertiary
Padding: 20px
Border-radius: 12px
Border-left: 4px solid primary-600

Pattern name:
  - Icon: 📊
  - Font: 18px, bold

Win rate bar:
  - Height: 24px
  - Background: bg-secondary
  - Fill: success-500
  - Percentage text overlay
  - Stats: (45/58 trades)

Description:
  - Font: 14px, regular
  - Color: text-secondary
```

---

### Screen 3: AI INSIGHTS PAGE

```
┌──────────────────────────────────────────────────────────┐
│ AI Insights & Recommendations                             │
├──────────────────────────────────────────────────────────┤
│                                                           │
│ ┌───────────────────────────────────────────────────┐   │
│ │ 📊 PERFORMANCE OVERVIEW                            │   │
│ │                                                    │   │
│ │ Analyzed: 45 trades | Period: Last 30 days        │   │
│ │                                                    │   │
│ │ Win Rate by Emotion                                │   │
│ │ ┌─────────────────────────────────────────────┐   │   │
│ │ │ Confidence ████████████████████░░ 78%      │   │   │
│ │ │ Pattern    ████████████████░░░░░░ 75%      │   │   │
│ │ │ Neutral    ███████████░░░░░░░░░░ 55%      │   │   │
│ │ │ Greed      ██████░░░░░░░░░░░░░░░ 30%      │   │   │
│ │ │ FOMO       ████░░░░░░░░░░░░░░░░░ 22%      │   │   │
│ │ │ Fear       ██░░░░░░░░░░░░░░░░░░░ 15%      │   │   │
│ │ └─────────────────────────────────────────────┘   │   │
│ └───────────────────────────────────────────────────┘   │
│                                                           │
│ ┌───────────────────────────────────────────────────┐   │
│ │ 🔴 TOP 3 MISTAKES                                  │   │
│ │                                                    │   │
│ │ 1. FOMO Trades (18 trades, 40%)                   │   │
│ │    ├─ Win Rate: 22%                               │   │
│ │    ├─ vs Non-FOMO: 73% win rate                  │   │
│ │    └─ 💡 Đợi RSI về <30 hoặc retest MA50          │   │
│ │                                                    │   │
│ │ 2. Late Night Trading (12 trades after 22:00)     │   │
│ │    ├─ Win Rate: 33%                               │   │
│ │    ├─ vs Daytime: 62% win rate                   │   │
│ │    └─ 💡 Tránh trade khi mệt mỏi                  │   │
│ │                                                    │   │
│ │ 3. No Pattern Confirmation (15 trades)            │   │
│ │    ├─ Win Rate: 40%                               │   │
│ │    ├─ vs With Pattern: 78% win rate              │   │
│ │    └─ 💡 Đợi Bullish Engulfing hoặc Morning Star  │   │
│ └───────────────────────────────────────────────────┘   │
│                                                           │
│ ┌───────────────────────────────────────────────────┐   │
│ │ ✅ TOP 3 STRENGTHS                                 │   │
│ │                                                    │   │
│ │ 1. Pattern-Based Entries                          │   │
│ │    └─ 85% win rate on Morning Star & Hammer       │   │
│ │    💡 Continue focusing on these setups           │   │
│ │                                                    │   │
│ │ 2. Proper Stop Loss Management                    │   │
│ │    └─ Only 2% trades violated SL rules            │   │
│ │    💡 Maintain this discipline                    │   │
│ │                                                    │   │
│ │ 3. Risk/Reward Ratio                              │   │
│ │    └─ Average R:R 1:2.8 (Target: 1:2+)           │   │
│ │    💡 Great job on position sizing                │   │
│ └───────────────────────────────────────────────────┘   │
│                                                           │
│ ┌───────────────────────────────────────────────────┐   │
│ │ 🎯 ACTION ITEMS                                    │   │
│ │                                                    │   │
│ │ [ ] Reduce FOMO trades by 50% next month          │   │
│ │ [ ] Set "No trade after 22:00" rule reminder      │   │
│ │ [ ] Create checklist for pattern confirmation     │   │
│ │ [ ] Backtest Morning Star setup on 100 examples   │   │
│ └───────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

---

## 3️⃣ COMPONENT LIBRARY

### Buttons
```
Primary Button:
  - Background: primary-600
  - Hover: primary-700
  - Text: white, 14px, medium
  - Padding: 10px 20px
  - Border-radius: 8px
  - Shadow: shadow-sm

Secondary Button:
  - Background: transparent
  - Border: 1px solid border-color
  - Text: text-primary, 14px, medium
  - Hover: bg-secondary

Danger Button:
  - Background: danger-500
  - Hover: danger-600

Sizes:
  - sm: padding 8px 16px, text 12px
  - md: padding 10px 20px, text 14px (default)
  - lg: padding 12px 24px, text 16px
```

### Badges
```
Emotion Badges:
  - FOMO: bg-red-500/20, text-red-500
  - Fear: bg-orange-500/20, text-orange-500
  - Confidence: bg-green-500/20, text-green-500
  - etc.

Status Badges:
  - Win: bg-green-500/20, text-green-500, "✅"
  - Loss: bg-red-500/20, text-red-500, "❌"

Size:
  - Padding: 4px 12px
  - Font: 12px, medium
  - Border-radius: 6px
```

### Cards
```
Base Card:
  - Background: bg-tertiary
  - Border: 1px solid border-color
  - Border-radius: 12px
  - Padding: 20px
  - Shadow: shadow-sm

Hover Card (clickable):
  - Hover: border-primary-600, shadow-md
  - Cursor: pointer
  - Transition: all 0.2s
```

### Inputs
```
Text Input:
  - Background: bg-secondary
  - Border: 1px solid border-color
  - Border-radius: 8px
  - Padding: 10px 14px
  - Font: 14px
  - Focus: border-primary-600, ring 2px primary-600/20

Select:
  - Same as Text Input
  - Arrow icon: ChevronDown (lucide)

Textarea:
  - Min-height: 100px
  - Resize: vertical
```

### Progress Bars
```
Win Rate Bar:
  - Height: 24px
  - Background: bg-secondary
  - Fill: gradient (success-600 → success-400)
  - Border-radius: 6px
  - Text overlay: percentage + stats
  - Smooth animation on load
```

---

## 4️⃣ RESPONSIVE DESIGN

### Breakpoints
```
Mobile: < 640px
Tablet: 640px - 1024px
Desktop: > 1024px
```

### Mobile Adaptations
```
- Sidebar → Bottom navigation bar
- Metrics cards: 2x2 grid instead of 1x4
- Charts: Stack vertically
- Table → Cards (scrollable list)
- Reduce padding/spacing
```

---

## 5️⃣ ANIMATIONS & INTERACTIONS

### Micro-interactions
```
- Button hover: scale(1.02)
- Card hover: translateY(-2px) + shadow increase
- Badge pulse: animate when emotion detected
- Chart line draw: animate on load
- Number counters: count up animation
```

### Transitions
```
All: transition-all duration-200 ease-in-out
Hover: duration-150
Page transitions: fade + slide
```

---

## 6️⃣ ACCESSIBILITY

### Requirements
```
- Color contrast ratio: ≥ 4.5:1 for text
- Focus indicators: visible ring
- Alt text for icons
- Keyboard navigation support
- ARIA labels for screen readers
```

---

## 7️⃣ FIGMA STRUCTURE

### Pages to Create
```
1. Design System
   - Colors
   - Typography
   - Components
   - Icons

2. Wireframes (Low-fi)
   - Dashboard
   - Trade Detail
   - Insights

3. High-Fidelity Mockups
   - Dashboard (Dark)
   - Trade Detail (Dark)
   - Insights (Dark)

4. Interactive Prototype
   - Clickable flows
   - Hover states
```

---

## 8️⃣ EXPORT FOR DEVELOPERS

### Assets to Export
```
- Logo: SVG + PNG (multiple sizes)
- Icons: SVG individual files
- Mockups: PNG @2x resolution
- Interactive prototype: Figma link
- Design tokens: JSON (colors, spacing)
```

---

## ✅ CHECKLIST

### Before Pitch
- [ ] 3 main screens designed (Dashboard, Trade Detail, Insights)
- [ ] Dark theme implemented
- [ ] Component library created
- [ ] Interactive prototype with basic flows
- [ ] Exported PNG mockups for slides
- [ ] Figma link sharable with view access

### Quality Check
- [ ] All text readable (min 14px)
- [ ] Consistent spacing
- [ ] Emotion colors clearly distinguishable
- [ ] PnL positive/negative obvious (green/red)
- [ ] Mobile responsive layouts created
- [ ] No lorem ipsum text
- [ ] Real trading data examples used

---

**Tool:** Figma (Free version is enough for MVP)  
**Estimated Time:** 8-12 hours for 3 screens + components  
**Priority:** Dashboard > Trade Detail > Insights
