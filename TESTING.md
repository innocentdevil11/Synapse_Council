# 🧪 Testing Guide

## Manual Testing Checklist

### Backend API Tests

#### 1. Health Check
```bash
curl http://localhost:8000/health
```
Expected: `{"status": "healthy", "graph_initialized": true}`

#### 2. Root Endpoint
```bash
curl http://localhost:8000/
```
Expected: API info with endpoints list

#### 3. Decision Endpoint - Valid Request
```bash
curl -X POST http://localhost:8000/decision \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Should I invest in cryptocurrency?",
    "weights": {
      "ethical": 0.2,
      "risk": 0.3,
      "eq": 0.2,
      "values": 0.2,
      "red_team": 0.1
    }
  }'
```
Expected: JSON response with `agent_outputs` and `final_decision`

#### 4. Decision Endpoint - Invalid Request (missing query)
```bash
curl -X POST http://localhost:8000/decision \
  -H "Content-Type: application/json" \
  -d '{
    "weights": {
      "ethical": 0.2,
      "risk": 0.2,
      "eq": 0.2,
      "values": 0.2,
      "red_team": 0.2
    }
  }'
```
Expected: 422 Validation Error

#### 5. Decision Endpoint - Invalid Weights
```bash
curl -X POST http://localhost:8000/decision \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Test query",
    "weights": {
      "ethical": 1.5,
      "risk": 0.2,
      "eq": 0.2,
      "values": 0.2,
      "red_team": 0.2
    }
  }'
```
Expected: 422 Validation Error (weight > 1.0)

### Frontend UI Tests

#### 1. Initial Load
- [ ] Page loads without errors
- [ ] Header displays "Synapse Council"
- [ ] Gradient background is visible
- [ ] Query textarea is empty with placeholder
- [ ] All 5 weight sliders show 0.20
- [ ] Submit button is disabled (no query)

#### 2. Query Input
- [ ] Can type in textarea
- [ ] Placeholder disappears on focus
- [ ] Submit button enables when text entered
- [ ] Submit button disables when text cleared

#### 3. Weight Sliders
- [ ] All sliders draggable
- [ ] Values update in real-time
- [ ] Value display animates on change
- [ ] Each slider has correct color theme
- [ ] Range is 0.00 to 1.00

#### 4. Submit & Loading
- [ ] Button shows "Processing..." when clicked
- [ ] All inputs disabled during processing
- [ ] Loading spinner appears
- [ ] "Deliberating..." text pulses
- [ ] Spinner rotates smoothly

#### 5. Results Display
- [ ] Council Resolution appears first (prominent panel)
- [ ] Agent cards appear with stagger animation
- [ ] All 5 agent outputs visible
- [ ] Each card has correct agent name/descriptor
- [ ] Text is readable and properly formatted
- [ ] Colors match agent themes

#### 6. Error Handling
- [ ] Network error shows error message
- [ ] Error message is styled correctly (red theme)
- [ ] Error can be dismissed by new submission
- [ ] App doesn't crash on error

#### 7. Responsive Design
**Mobile (< 768px)**
- [ ] Single column layout
- [ ] Weights stack vertically
- [ ] Results stack vertically
- [ ] Text is readable
- [ ] Touch targets are large enough

**Tablet (768px - 1024px)**
- [ ] 2-column weight grid
- [ ] 2-column results grid
- [ ] Proper spacing maintained

**Desktop (> 1024px)**
- [ ] 3-column weight grid
- [ ] 2-column results grid
- [ ] Max width container centers content

#### 8. Animations
- [ ] Header fades in on load
- [ ] Query box scales in
- [ ] Weights section slides in
- [ ] Submit button scales on hover
- [ ] Submit button shrinks on click
- [ ] Loading spinner transitions smoothly
- [ ] Results fade in after loading
- [ ] Agent cards cascade in sequence

## Example Test Queries

### Simple Decision
```
Should I buy a new laptop or repair my old one?
```

### Career Decision
```
Should I accept a job offer with higher pay but longer commute?
```

### Personal Decision
```
Should I adopt a pet dog given my work schedule?
```

### Investment Decision
```
Should I invest my savings in stocks or keep them in a savings account?
```

### Life Decision
```
Should I move to a new city for better career opportunities?
```

## Performance Benchmarks

### Backend
- Health check: < 50ms
- Decision endpoint: 5-30s (depends on LLM)
- Memory usage: < 500MB

### Frontend
- Initial load: < 2s
- Time to interactive: < 3s
- Animation frame rate: 60fps
- Bundle size: < 500KB

## Browser Compatibility

Tested on:
- [ ] Chrome 120+
- [ ] Firefox 120+
- [ ] Safari 17+
- [ ] Edge 120+

## Accessibility Tests

- [ ] Keyboard navigation works
- [ ] Focus indicators visible
- [ ] Labels associated with inputs
- [ ] Color contrast meets WCAG AA
- [ ] Screen reader compatible

## Integration Tests

### End-to-End Flow
1. Start backend server
2. Start frontend server
3. Navigate to localhost:3000
4. Enter test query
5. Adjust weights
6. Submit request
7. Verify results display correctly
8. Test multiple consecutive requests

## Known Issues / Limitations

- Slider styling may vary slightly across browsers
- Very long agent outputs may require scrolling
- Backend startup takes ~2s to initialize graph
- No request timeout configured (relies on default)

## Debugging Tips

### Backend Not Responding
```bash
# Check if server is running
curl http://localhost:8000/health

# Check server logs
# Look for port binding errors or graph init errors
```

### Frontend Can't Connect
```bash
# Open browser console
# Look for CORS errors or network failures
# Verify API_URL is correct
```

### Agents Not Producing Output
```bash
# Check backend logs for agent errors
# Verify LLM API keys are set
# Test agents directly via main.py
```

---

**Last Updated**: January 2026
