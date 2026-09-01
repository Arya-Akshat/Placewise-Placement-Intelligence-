# Placewise Frontend Architecture & Component Specification

**Framework:** React 18 + TypeScript + Vite  
**Styling System:** Tailwind CSS (Dark Placement Intelligence Visual Theme)  
**State Management:** React Context (`ChatContext`) with domain hooks  
**Visualization Engine:** Recharts (Responsive SVG Bar & Line Charts)  
**Icons:** Lucide React  

---

## 1. Directory Structure

```
frontend/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── index.css
    ├── types/
    │   └── index.ts                 # Typed domain models (Message, TableData, QueryAttachment)
    ├── services/
    │   ├── placewiseApi.ts          # Backend API client (/api/v1/)
    │   └── mockData.ts              # Offline fallback mock data
    ├── context/
    │   └── ChatContext.tsx          # Conversation state, active message queue, retry
    ├── utils/
    │   └── formatters.ts            # formatPercentage, formatLpa, formatNumber
    ├── components/
    │   ├── common/
    │   │   ├── ErrorBoundary.tsx    # React error boundary for safe rendering
    │   │   ├── Badge.tsx            # Visual status badges (Bands, Fit, Flags)
    │   │   └── LoadingSpinner.tsx   # Pulse loading indicators
    │   ├── layout/
    │   │   ├── Header.tsx           # Institutional header with connection badge
    │   │   ├── Sidebar.tsx          # Domain navigation & recent conversations
    │   │   └── AppLayout.tsx        # Responsive desktop/mobile shell
    │   ├── analytics/
    │   │   └── KpiCard.tsx          # Headline metric metric cards
    │   ├── tables/
    │   │   └── PlacementDataTable.tsx # Sortable, paginated, CSV-exportable table
    │   ├── charts/
    │   │   ├── ChartContainer.tsx   # Chart/Table view toggle toolbar
    │   │   ├── PlacementBarChart.tsx# Categorical breakdown charts
    │   │   └── PlacementLineChart.tsx# Historical trend line charts
    │   └── chat/
    │       ├── EmptyState.tsx       # Landing quick prompt cards
    │       ├── ChatMessage.tsx      # User/Assistant bubble renderer
    │       ├── Composer.tsx         # Auto-resizing message input (Enter to send)
    │       ├── ClarificationPrompt.tsx # Quick-choice option chips
    │       ├── AgentAnalysis.tsx    # Multi-step executive analysis accordion
    │       └── EvidencePanel.tsx    # Governed SQL metadata inspector
    └── pages/
        └── ChatPage.tsx             # Primary placement intelligence workspace
```

---

## 2. Key Architecture Decisions

1. **Strict Backend Segregation**: The frontend never connects directly to Databricks or Genie. Zero credentials or tokens reside in the client application bundle.
2. **Safe Large Result Set Bounding**: Tabular components display up to bounded page sizes ($8$ rows per page) and render safe truncation notices for large result sets ($125\text{M}$ rows), preventing memory leaks.
3. **Resilient Error Boundaries**: Individual chart or attachment failures are caught by `<ErrorBoundary />`, preventing whole-page crashes while preserving assistant textual analysis.
4. **Adaptive Chart/Table Rendering**: When numerical data is present, users can toggle between `<PlacementBarChart />` / `<PlacementLineChart />` and `<PlacementDataTable />` with CSV export.
