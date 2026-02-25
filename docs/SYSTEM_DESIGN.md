# System Design Documentation

**OG-Core and MUIO Architecture Analysis**

This document provides detailed system design documentation for both OG-Core and MUIO, based on actual code inspection and execution.

---

## Table of Contents

1. [MUIO System Design](#muio-system-design)
2. [OG-Core System Design](#ogcore-system-design)
3. [Data Formats and Interfaces](#data-formats-and-interfaces)
4. [Integration Points](#integration-points)

---

## MUIO System Design

### Overview

**MUIO** (Modelling User Interface for OSeMOSYS) is a web-based interface for creating, managing, and visualizing CLEWS (Climate, Land, Energy, and Water Systems) energy models using the OSeMOSYS optimization framework.

### Technology Stack (Verified)

**Backend:**
- **Framework**: Flask 2.x
- **Server**: Waitress (production) / Flask dev server
- **Session Management**: Flask sessions (5-day lifetime)
- **CORS**: Flask-CORS for cross-origin requests
- **Data Storage**: File-based (JSON, CSV, pickle)

**Frontend:**
- **Framework**: Vanilla JavaScript (ES6 modules)
- **UI Library**: SmartAdmin template + Bootstrap 3
- **Data Grids**: Wijmo FlexGrid
- **Charts**: Plotly.js
- **Additional**: jqWidgets for specialized components

### Architecture Pattern

MUIO follows a **traditional MVC pattern** with client-side routing:

```
Browser
    ↓
index.html (View)
    ↓
JavaScript Controllers (App/Controller/)
    ↓
Fetch API → Flask Routes (API/Routes/)
    ↓
Python Classes (API/Classes/)
    ↓
File System (WebAPP/DataStorage/)
```

### Directory Structure

```
MUIO/
├── API/                           # Backend
│   ├── app.py                    # Flask application entry point
│   ├── Classes/
│   │   ├── Base/                 # Base configuration and utilities
│   │   │   ├── Config.py        # Configuration management
│   │   │   ├── FileClass.py     # File I/O operations
│   │   │   └── SyncS3.py        # S3 synchronization (optional)
│   │   └── Case/                 # Case/model management
│   │       ├── CaseClass.py     # Case creation logic
│   │       ├── DataFileClass.py # Data file handling
│   │       └── OsemosysClass.py # OSeMOSYS execution
│   └── Routes/
│       ├── Case/CaseRoute.py    # Case management endpoints
│       ├── Upload/UploadRoute.py # File upload handling
│       └── DataFile/DataFileRoute.py # Data file operations
│
├── WebAPP/                        # Frontend
│   ├── index.html                # Main entry point
│   ├── App/
│   │   ├── Controller/           # JavaScript controllers
│   │   │   ├── Home.js
│   │   │   ├── Config.js
│   │   │   ├── AddCase.js
│   │   │   └── ...
│   │   ├── Model/                # Data models
│   │   └── View/                 # HTML templates
│   │       ├── Sidebar.html
│   │       └── ...
│   ├── Classes/                  # JavaScript utility classes
│   ├── Routes/                   # Client-side routing
│   │   └── Routes.Class.js      # Crossroads.js routing
│   ├── DataStorage/              # User data storage
│   │   ├── Parameters.json
│   │   ├── Variables.json
│   │   └── [case_name]/         # Individual case data
│   └── References/               # Third-party libraries
│       ├── wijmo/
│       ├── plotly/
│       ├── smartadmin/
│       └── jquery/
```

### Key Flask Routes

```python
# Main application
@app.route("/", methods=['GET'])
def home()

# Session management
@app.route("/getSession", methods=['GET'])
@app.route("/setSession", methods=['POST'])

# Case management (CaseRoute blueprint)
@case_api.route("/getCases", methods=['GET'])
@case_api.route("/saveCase", methods=['POST'])
@case_api.route("/deleteCase", methods=['POST'])
@case_api.route("/getParamFile", methods=['POST'])

# Data file operations (DataFileRoute blueprint)
@datafile_api.route("/runModel", methods=['POST'])
@datafile_api.route("/getResults", methods=['GET'])
```

### Data Flow

1. **User Interaction** → Browser (index.html)
2. **Client-side Routing** → Crossroads.js routes to controller
3. **Controller** → Fetches data via REST API
4. **Flask Route** → Processes request
5. **Python Class** → Business logic
6. **File System** → Reads/writes JSON/CSV
7. **Response** → JSON back to controller
8. **Rendering** → Wijmo grids or Plotly charts

### Session Management

```python
# Flask session configuration
app.permanent_session_lifetime = timedelta(days=5)
app.config['SECRET_KEY'] = '12345'

# Session usage
session['osycase'] = casename  # Current active case
```

### CORS Configuration

```python
if Config.HEROKU_DEPLOY == 0:
    # localhost
    'Access-Control-Allow-Origin': 'http://127.0.0.1'
else:
    # HEROKU
    'Access-Control-Allow-Origin': 'https://osemosys.herokuapp.com/'
```

---

## OG-Core System Design

### Overview

**OG-Core** is a dynamic overlapping generations (OG) model for fiscal policy analysis. It computes macroeconomic equilibrium with heterogeneous agents, realistic demographics, and detailed fiscal policy.

### Technology Stack (Verified)

**Core:**
- **Language**: Python 3.8+
- **Numerical Computing**: NumPy, SciPy
- **Parallel Processing**: Dask, Distributed
- **Parameter Management**: ParamTools
- **Optimization**: Numba (JIT compilation)
- **Demographics**: UN population data integration

**Key Dependencies:**
```
numpy>=1.21.0
scipy>=1.7.1
pandas>=1.2.5
numba>=0.55.0
dask>=2.30.0
distributed>=2.30.1
paramtools>=0.20.0
matplotlib>=3.3.0
```

### Architecture Pattern

OG-Core follows a **functional programming pattern** with modular solvers:

```
User Script
    ↓
Specifications (parameters)
    ↓
runner() function
    ├→ SS.run_SS() [Steady-state solver]
    └→ TPI.run_TPI() [Time path iteration]
    ↓
Output Files (pickle format)
```

### Module Structure

```
ogcore/
├── __init__.py
├── execute.py              # Main execution: runner()
├── parameters.py           # Specifications class
├── SS.py                   # Steady-state solver
├── TPI.py                  # Time path iteration solver
├── demographics.py         # Population/demographic functions
├── aggregates.py           # Aggregate variable calculations
├── firm.py                 # Firm behavior
├── household.py            # Household behavior
├── fiscal.py               # Fiscal policy
├── tax.py                  # Tax calculations
├── utils.py                # Utility functions
├── output_plots.py         # Plotting functions
├── output_tables.py        # Table generation
└── default_parameters.json # Default parameter values
```

### Main Execution Function

```python
def runner(p, time_path=True, client=None):
    """
    Run OG-Core model
    
    Args:
        p: Specifications object with parameters
        time_path: Whether to solve time path (vs steady-state only)
        client: Dask client for parallel processing
    
    Returns:
        None (saves results to pickle files)
    
    Output Files:
        - SS/SS_vars.pkl: Steady-state results
        - TPI/TPI_vars.pkl: Time path results
        - model_params.pkl: Parameters used
    """
```

### Specifications Class

```python
class Specifications(paramtools.Parameters):
    """
    Parameter management using ParamTools
    
    Key Methods:
        __init__(): Initialize with defaults
        update_specifications(dict): Update parameters
        
    Key Parameters:
        T: Number of time periods (default: 160)
        S: Maximum age (default: 80)
        frisch: Frisch elasticity of labor supply
        start_year: Start year for simulation
        cit_rate: Corporate income tax rate
        debt_ratio_ss: Steady-state debt-to-GDP ratio
    """
```

### Output Format

**Steady-State (SS/SS_vars.pkl):**
```python
{
    'r_ss': float,      # Steady-state interest rate
    'w_ss': float,      # Steady-state wage
    'K_ss': float,      # Steady-state capital
    'L_ss': float,      # Steady-state labor
    'Y_ss': float,      # Steady-state GDP
    # ... more variables
}
```

**Time Path (TPI/TPI_vars.pkl):**
```python
{
    'r': np.array,      # Interest rates over time [T]
    'Y': np.array,      # GDP over time [T]
    'K': np.array,      # Capital over time [T]
    'L': np.array,      # Labor over time [T]
    'C': np.array,      # Consumption over time [T, S, J]
    'w': np.array,      # Wages over time [T]
    # ... more variables
}
```

### Demographic Functions

```python
def get_pop_objs(
    country_id='840',  # UN country code (840 = USA)
    start_year=2021,
    end_year=2100,
    ...
):
    """
    Pull real UN population data
    
    Returns:
        pop_dict: {
            'omega': Population distribution by age [T, S]
            'g_n_ss': Steady-state population growth rate
            'omega_SS': Steady-state population distribution [S]
            'rho': Mortality rates [S]
            'g_n_path': Population growth path [T]
            'imm_rates': Immigration rates [T, S]
            'omega_path_S': Population path [T, S]
        }
    """
```

### Execution Flow

```
1. Create Specifications
   p = Specifications(baseline=True, output_base="./output")

2. Update Parameters
   p.update_specifications({
       'frisch': 0.41,
       'start_year': 2021,
       'T': 40,
       'S': 40
   })

3. Setup Dask Client
   client = Client(n_workers=4, threads_per_worker=1)

4. Run Model
   runner(p, time_path=True, client=client)

5. Model Execution:
   a. Create output directories
   b. Run steady-state solver (SS.run_SS)
      - Solves for equilibrium r, w, K, L, Y
      - Saves to SS/SS_vars.pkl
   c. Run time path solver (TPI.run_TPI)
      - Solves transition path
      - Iterates until convergence
      - Saves to TPI/TPI_vars.pkl
   d. Save parameters to model_params.pkl

6. Load Results
   with open('./output/TPI/TPI_vars.pkl', 'rb') as f:
       tpi_results = pickle.load(f)
   interest_rates = tpi_results['r']
```

### Solver Details

**Steady-State Solver (SS.run_SS):**
- Finds equilibrium where markets clear
- Uses root-finding algorithms
- Convergence criterion: max error < tolerance

**Time Path Iteration (TPI.run_TPI):**
- Solves transition from initial to steady state
- Iterative algorithm:
  1. Guess paths for r, w, BQ, TR
  2. Solve household and firm problems
  3. Check market clearing
  4. Update guesses
  5. Repeat until convergence
- Typical iterations: 20-35
- Convergence criterion: distance < 1e-5

---

## Data Formats and Interfaces

### MUIO Data Formats

**Parameters (JSON):**
```json
{
    "DiscountRate": {
        "id": "DR",
        "value": "Discount Rate",
        "group": "R",
        "menu": true
    }
}
```

**Case Data (JSON):**
```json
{
    "osy-casename": "MyCase",
    "osy-desc": "Description",
    "osy-regions": ["USA"],
    "osy-years": [2021, 2022, ...],
    "osy-technologies": ["SOLAR", "WIND", ...]
}
```

**OSeMOSYS Input (CSV):**
```csv
REGION,YEAR,VALUE
USA,2021,0.05
USA,2022,0.05
```

### OG-Core Data Formats

**Parameters (JSON):**
```json
{
    "T": 160,
    "S": 80,
    "frisch": 0.4,
    "start_year": 2021
}
```

**Output (Pickle):**
```python
# Binary pickle format
# Load with: pickle.load(file)
# Contains: NumPy arrays and Python dicts
```

---

## Integration Points

### OG-Core → CLEWS

**Source Variable:** `r` (interest rate array from TPI_vars.pkl)
- **Format**: NumPy array, shape [T], decimal values
- **Example**: [0.059645, 0.059443, 0.059215, ...]
- **Units**: Decimal (0.05 = 5%)

**Target Variable:** `DiscountRate[r,y]` (OSeMOSYS parameter)
- **Format**: CSV with columns [REGION, YEAR, VALUE]
- **Units**: Decimal (0.05 = 5% discount rate)

**Transformation:**
```python
# Extract
with open('TPI/TPI_vars.pkl', 'rb') as f:
    tpi_results = pickle.load(f)
interest_rates = tpi_results['r']

# Transform
discount_rate = np.mean(interest_rates[:20])

# Load
df = pd.DataFrame({
    'REGION': ['USA'] * 20,
    'YEAR': range(2021, 2041),
    'VALUE': [discount_rate] * 20
})
df.to_csv('DiscountRate.csv', index=False)
```

### CLEWS → OG-Core (Future)

**Source Variable:** Electricity price ($/MWh from OSeMOSYS results)
- **Format**: CSV output from CLEWS
- **Units**: $/MWh

**Target Variable:** Production cost parameter in OG-Core
- **Format**: Python dict for update_specifications()
- **Units**: Cost factor (normalized to baseline)

**Transformation:**
```python
# Extract
electricity_price = clews_results['electricity_price']

# Transform
baseline_price = 50.0
cost_factor = electricity_price / baseline_price

# Load
p.update_specifications({
    'energy_cost_factor': cost_factor
})
```

---

## Performance Characteristics

### MUIO
- **Startup Time**: < 5 seconds
- **Case Loading**: < 1 second
- **Model Execution**: Depends on OSeMOSYS problem size (minutes to hours)
- **Concurrent Users**: Supports multiple via Flask sessions

### OG-Core
- **Steady-State**: 5-15 minutes (depends on parameters)
- **Time Path**: 10-30 minutes (depends on T, S, convergence)
- **Full Baseline**: 30-60 minutes
- **Parallel Scaling**: Linear with Dask workers (up to CPU count)

---

## Security Considerations

### MUIO
- Session-based authentication
- CORS restrictions
- File upload validation
- No SQL injection risk (file-based storage)

### OG-Core
- No network exposure (local execution)
- File system access required
- CPU-intensive (resource limits recommended)

---

## Scalability

### MUIO
- **Horizontal**: Multiple Flask instances with load balancer
- **Vertical**: Limited by file I/O performance
- **Storage**: File-based (consider database for production)

### OG-Core
- **Horizontal**: Dask distributed cluster
- **Vertical**: More workers = faster execution
- **Memory**: Scales with T × S (problem size)
- **GPU Support**: GPU Support and run it via wsl

---

**Document Version**: 1.0  
**Last Updated**: February 25, 2026  
**Author**: S Khavin
