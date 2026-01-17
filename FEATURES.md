# ✨ Synapse Council Features

## 🎯 Core Functionality

### Multi-Agent Decision System
- **5 Specialized Agents** working in parallel
  - Ethical Agent: Moral reasoning
  - Risk & Logic Agent: Analytical thinking
  - EQ Agent: Emotional intelligence
  - Value Alignment Agent: Personal values
  - Red Team Agent: Critical perspective

- **Intelligent Aggregator** synthesizes all perspectives into a unified decision

- **Customizable Weights** for each agent (0.0 - 1.0 scale)

## 🎨 UI/UX Features

### Design System
- **Dark Mode Only** - Optimized for focus and reduced eye strain
- **Neon Color Palette**
  - Cyan (#00f0ff) - Primary accent
  - Violet (#a855f7) - Secondary accent
  - Emerald (#10b981) - Success/final decision
  - Pink & Orange - Additional highlights

### Visual Effects
- **Glassmorphism** - Frosted glass effect on all panels
- **Neon Glows** - Subtle glow effects on interactive elements
- **Gradient Background** - Animated radial gradients
- **Smooth Transitions** - 300ms transitions on all interactions

### Animations (Framer Motion)
- **Entry Animations**
  - Staggered appearance (0.1s delay per item)
  - Fade + slide from bottom
  - Scale transitions

- **Interactive Animations**
  - Hover scale on buttons (1.05x)
  - Tap feedback (0.95x)
  - Slider value pulse animation
  - Loading spinner rotation + pulse

- **Results Animations**
  - Council Resolution: Prominent fade-in (0.6s)
  - Agent Cards: Staggered cascade effect
  - Error/success states: Slide animations

## 🧩 Component Architecture

### Core Components

#### WeightSlider
- Custom range input with gradient fill
- Real-time value display with pulse animation
- Color-coded per agent
- Disabled state during processing

#### AgentCard
- Glassmorphic design
- Agent name with gradient text
- Short descriptor
- Full output with line wrapping
- Color-coded borders and glows

#### LoadingSpinner
- Dual-layer animation
  - Outer ring: Constant rotation
  - Inner circle: Pulse effect
- "Deliberating..." text with opacity animation

### Layout
- **Responsive Grid System**
  - Mobile: 1 column
  - Tablet: 2 columns
  - Desktop: 3 columns (weights), 2 columns (results)

- **Max Width Container**: 6xl (1280px)
- **Consistent Spacing**: 4, 6, 8, 12 rem units

## 🔌 API Integration

### Endpoints Used
- `POST /decision` - Main decision execution
- `GET /health` - Health check (optional)

### Request Flow
1. Validate query is not empty
2. Collect weights from sliders
3. Send POST request with JSON body
4. Handle loading state
5. Display results or error

### Error Handling
- Network errors
- API errors (4xx, 5xx)
- Validation errors
- Display user-friendly messages

## 🎮 User Interaction Flow

```
┌─────────────────────────────────────┐
│  1. User enters decision query      │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  2. User adjusts agent weights      │
│     (optional, default 0.2 each)    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  3. User clicks "Run Council"       │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  4. Loading animation displays      │
│     "Deliberating..."               │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  5. Results appear with animation:  │
│     - Council Resolution (top)      │
│     - Individual Perspectives       │
└─────────────────────────────────────┘
```

## 📱 Responsive Breakpoints

- **Mobile**: < 768px
  - Single column layout
  - Stacked weights
  - Full-width cards

- **Tablet**: 768px - 1024px
  - 2-column grid for weights
  - 2-column grid for results

- **Desktop**: > 1024px
  - 3-column grid for weights
  - 2-column grid for results

## ⚡ Performance Features

### Backend
- Graph initialized once at startup (not per request)
- FastAPI async support
- Pydantic validation for type safety

### Frontend
- Next.js App Router for optimal loading
- Client-side state management (no unnecessary re-renders)
- Framer Motion animations use GPU acceleration
- Lazy loading with AnimatePresence

## 🔐 Security Features

- **CORS Configuration** - Restricted to localhost:3000 by default
- **Input Validation**
  - Query: 1-5000 characters
  - Weights: 0.0-1.0 range
- **Error Message Sanitization** - No sensitive data in error responses

## 🎯 Future Enhancement Ideas

- [ ] Real-time streaming of agent outputs
- [ ] Save/load decision history
- [ ] Export results as PDF
- [ ] Custom agent weight presets
- [ ] Dark/light mode toggle
- [ ] Multi-language support
- [ ] User authentication
- [ ] Share decision link

---

**Current Version**: 1.0.0  
**Last Updated**: January 2026
