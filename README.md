# IntelliGrid

Smart Home Energy Management System - Optimizing renewable energy usage through AI-powered predictive analytics and MILP optimization for the Algerian market.

**Hackathon Challenge:** Smart Renewable Energy Management System  
**Focus:** Real-time monitoring, intelligent energy distribution, and predictive analytics for solar-powered homes

## 🎯 Problem Statement

Renewable energy sources like solar power are increasingly adopted to reduce fossil fuel dependence. However, a significant portion of generated renewable energy is wasted due to:
- Lack of intelligent monitoring and storage optimization
- Energy produced when demand is low but lost due to poor distribution
- Shortages during peak consumption periods
- No predictive analytics for proactive energy management

## 💡 Our Solution

IntelliGrid addresses these challenges through a three-layer intelligent system:

1. **Energy Monitoring Layer** - Real-time solar production, consumption, and battery state tracking
2. **Intelligent Decision Engine** - Rule-based and MILP (Mathematical Optimization) algorithms for optimal energy usage
3. **AI & Predictive Analytics** - Weather-aware predictions with 94% accuracy for proactive management

### Key Innovations

- **MILP vs Rule-Based Comparison** - Mathematical programming proves 23.6% cost savings over greedy algorithms
- **AI Solar Predictor** - Machine learning model forecasting solar production based on weather patterns
- **Real-time Impact Analysis** - Environmental metrics (CO₂, water savings, air quality) and financial ROI calculations
- **Algerian Market Focus** - DZD currency and local electricity pricing (Sonelgaz rates)

## 🏗️ Architecture

```
IntelliGrid/
├── frontend/              # Next.js 14 frontend (Bun + TypeScript)
│   ├── app/              # App Router pages
│   ├── components/       # React components (charts, tables, UI)
│   ├── hooks/           # Custom React hooks
│   ├── lib/             # API clients and utilities
│   └── public/          # Static assets (favicon, logo)
├── backend/              # FastAPI backend (Python 3.11)
│   ├── app/             # FastAPI application
│   │   ├── api/routes/  # REST API endpoints
│   │   ├── services/    # Business logic layer
│   │   └── main.py      # Application entry
│   ├── src/             # Core modules
│   │   ├── core/        # Battery physics, simulation runner
│   │   ├── engine/      # Decision engines (Rule + MILP)
│   │   ├── data/        # Data models and simulator
│   │   └── analysis/    # Impact calculations
│   ├── tests/           # pytest test suite (49/52 passing)
│   └── models/          # Pre-trained AI models (29MB)
├── models/              # Solar PV prediction models
└── package.json         # Root workspace configuration
```

## 🚀 Quick Start

### Prerequisites

- [Bun](https://bun.sh) (v1.0+) - JavaScript runtime
- Python 3.11+
- Git

### 1. Clone and Setup

```bash
git clone <repository>
cd IntelliGrid

# Run automated setup script
./setup.sh
```

### 2. Manual Setup (if needed)

**Install Bun:**
```bash
curl -fsSL https://bun.sh/install | bash
```

**Install Frontend Dependencies:**
```bash
cd frontend
bun install
cd ..
```

**Install Backend Dependencies:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..
```

### 3. Start Development Servers

**Option A: Run both services**
```bash
./start-dev.sh
```

**Option B: Run individually**
```bash
# Terminal 1 - Backend API
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend
cd frontend
bun run dev
```

### 4. Access the Application

- **Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 💻 Technology Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript 5.3** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Component library
- **Recharts** - Data visualization
- **Lucide React** - Icons

### Backend
- **FastAPI** - High-performance Python API framework
- **Pydantic** - Data validation and serialization
- **PuLP** - MILP optimization solver
- **scikit-learn** - Machine learning (solar prediction)
- **Uvicorn** - ASGI server
- **pytest** - Testing framework

### AI/ML Models
- Solar PV production predictor (94% accuracy)
- Weather pattern analyzer
- Energy demand forecaster

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/simulate` | POST | Run energy simulation (Rule or MILP mode) |
| `/api/v1/optimize` | POST | MILP optimization only |
| `/api/v1/compare` | POST | Compare Rule-based vs MILP strategies |
| `/api/v1/weather/alerts` | POST | Get weather-based recommendations |
| `/api/v1/impact` | POST | Calculate environmental/financial impact |
| `/health` | GET | System health check |
| `/docs` | GET | Swagger UI documentation |

## 🎨 Features

### Dashboard
- **Real-time Metrics** - Solar production, consumption, battery level, cost tracking
- **Interactive Charts** - Energy flow visualization, battery SOC over time
- **Comparison Tool** - Side-by-side Rule vs MILP strategy analysis
- **Impact Analysis** - Environmental metrics (CO₂, trees, water) and ROI calculator
- **Data Table** - Hour-by-hour breakdown with CSV export
- **Weather Alerts** - Smart recommendations based on forecasts

### Configuration
- Season selection (Summer/Winter)
- Weather conditions (Sunny/Partly Cloudy/Cloudy/Rainy)
- Day type (Weekday/Weekend)
- Optimization mode (Rule-based / MILP)

### Optimization Modes
1. **Rule-Based (Greedy)** - Fast, simple hour-by-hour decisions
2. **MILP (Mathematical Optimization)** - Global 24-hour optimization, 23.6% cost savings

## 🧪 Testing

### Backend Tests
```bash
cd backend
source venv/bin/activate
python -m pytest tests/ -v

# Results: 49/52 tests passing
# - Battery physics: ✅ 19/19
# - Decision engine: ✅ 16/16
# - Integration: ✅ 8/8
# - MILP engine: ⚠️ 6/9 (edge cases)
```

### Frontend Tests
```bash
cd frontend
bun test
```

## 📈 Performance Metrics

- **Cost Savings**: 23.6% reduction with MILP vs Rule-based
- **AI Accuracy**: 94% solar production prediction
- **Grid Independence**: Up to 35% reduction in grid dependency
- **Environmental Impact**: CO₂ reduction, water savings, air quality improvements

## 🔧 Environment Variables

Create `.env` file in backend directory:

```bash
# Backend
API_PORT=8000
ENVIRONMENT=development

# Frontend (automatically connects to localhost:8000)
```

## 📝 Project Structure Details

### Frontend (`frontend/`)
```
components/
├── Dashboard.tsx           # Main dashboard with tabs
├── Sidebar.tsx            # Configuration panel
├── MetricCards.tsx        # KPI cards
├── EnergyChart.tsx        # Production/consumption chart
├── BatteryChart.tsx       # Battery SOC chart
├── BatteryComparisonChart.tsx  # Rule vs MILP comparison
├── HourlyDataTable.tsx    # Detailed data table
├── ImpactAnalysis.tsx     # Environmental/financial impact
└── ui/                    # shadcn/ui components
```

### Backend (`backend/`)
```
src/
├── core/
│   ├── battery.py         # Battery physics (96% efficiency)
│   ├── simulation_runner.py   # Orchestrates simulation
│   └── hybrid_adapter.py      # Unified Rule/MILP interface
├── engine/
│   ├── decision_engine.py     # Rule-based decisions
│   ├── milp_engine.py         # MILP optimization
│   └── weather_predictor.py   # Weather recommendations
├── data/
│   ├── models.py          # Dataclasses and enums
│   └── simulator.py       # Environment generator
├── analysis/
│   └── impact_analyzer.py     # ROI and environmental metrics
└── utils/
    └── config.py          # Constants and pricing (DZD)

app/
├── api/routes/
│   ├── simulation.py      # Simulation endpoints
│   ├── optimization.py    # MILP endpoints
│   ├── weather.py         # Weather alerts
│   └── impact.py          # Impact calculation
└── services/
    └── simulation.py      # Business logic layer
```

## 🚢 Deployment

### Frontend (Vercel)
```bash
cd frontend
vercel
```

### Backend (Railway/Render)
```bash
cd backend
# Set environment variables in dashboard
# Deploy via Git integration or CLI
```

### Docker (Optional)
```bash
docker-compose up --build
```

## 📚 Documentation

- **IMPLEMENTATION_SUMMARY.md** - Architecture and correctness verification
- **PHASE_C_SUMMARY.md** - MILP optimization details
- **AGENTS.md** - Development guidelines
- **DEMO.md** - Hackathon presentation guide

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Support

For issues and questions:
- Open a GitHub issue
- Check API docs at `/docs` endpoint
- Review test suite for usage examples

---

**Built for the Smart Renewable Energy Management System Hackathon** 🌱⚡
