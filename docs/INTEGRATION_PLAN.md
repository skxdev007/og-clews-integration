# Integration Plan: OG-Core ↔ MUIO/CLEWS

**Strategy and Implementation for Connecting Macroeconomic and Energy System Models**

This document outlines the complete integration strategy, implementation approach, and technical details for connecting OG-Core with MUIO/CLEWS.

---

## Table of Contents

1. [Integration Overview](#integration-overview)
2. [Architecture Design](#architecture-design)
3. [Implementation Strategy](#implementation-strategy)
4. [ETL Pipeline](#etl-pipeline)
5. [API Design](#api-design)
6. [Execution Modes](#execution-modes)
7. [Testing Strategy](#testing-strategy)
8. [Deployment Plan](#deployment-plan)

---

## Integration Overview

### Objective

Create a bidirectional integration between:
- **OG-Core**: Overlapping generations macroeconomic model
- **MUIO/CLEWS**: Energy system optimization model

### Key Principle

**Extend, Don't Replace** - The integration extends MUIO's existing functionality without modifying core MUIO code.

### Integration Points

```
OG-Core                    CLEWS/OSeMOSYS
--------                   --------------
Interest rates (r)    →    DiscountRate[r,y]
GDP (Y)               →    Demand scaling
Demographics          →    Population projections

Energy prices         ←    Electricity price
Technology costs      ←    CapitalCost[r,t,y]
```

---

## Architecture Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         MUIO Frontend                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ CLEWS UI     │  │ OG-Core UI   │  │ Coupled UI   │     │
│  │ (existing)   │  │ (new)        │  │ (new)        │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                      Flask Backend (MUIO)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ CLEWS Routes │  │ OG Routes    │  │ Coupled      │     │
│  │ (existing)   │  │ (new)        │  │ Routes (new) │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                       ETL Pipeline Layer                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  OGCLEWSTransformer                                   │  │
│  │  • og_to_clews()                                      │  │
│  │  • clews_to_og()                                      │  │
│  │  • validate()                                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         ↓                                    ↓
┌──────────────────┐              ┌──────────────────┐
│    OG-Core       │              │  OSeMOSYS/CLEWS  │
│  (Python Model)  │              │  (Optimization)  │
└──────────────────┘              └──────────────────┘
```

### Component Responsibilities

**1. OG-Core Executor (`og_executor.py`)**
- Wraps OG-Core execution
- Manages Dask client
- Handles parameter configuration
- Extracts results from pickle files

**2. ETL Pipeline (`etl_pipeline.py`)**
- Transforms data between models
- Validates data integrity
- Logs transformations
- Handles unit conversions

**3. Flask Routes (`og_routes.py`)**
- RESTful API endpoints
- Request validation
- Response formatting
- Error handling

**4. Frontend Controller (`OGCoreSimple.js`)**
- User interface
- Data visualization
- API communication
- Chart rendering

---

## Implementation Strategy

### Phase 1: Foundation (Completed)

**Goal**: Establish basic integration with real data

**Deliverables**:
- ✅ OG-Core execution wrapper
- ✅ ETL pipeline for OG→CLEWS
- ✅ Flask API endpoints
- ✅ Real data extraction
- ✅ Basic visualization

**Code Structure**:
```
MUIO/OG_CLEWS_Extension/
├── backend/
│   ├── __init__.py
│   ├── og_executor.py      # OG-Core wrapper
│   ├── etl_pipeline.py     # Data transformation
│   └── og_routes.py        # Flask endpoints
├── config/
│   └── og_defaults.json    # Default parameters
└── README.md
```

### Phase 2: Bidirectional Integration (Future)

**Goal**: Enable CLEWS → OG-Core data flow

**Tasks**:
- [ ] Implement `clews_to_og()` transformation
- [ ] Add CLEWS result extraction
- [ ] Update OG-Core parameters from CLEWS
- [ ] Test bidirectional flow

### Phase 3: Coupled Execution (Future)

**Goal**: Run both models together

**Tasks**:
- [ ] Implement one-way coupling (OG→CLEWS→Results)
- [ ] Implement converging mode (iterate until equilibrium)
- [ ] Add convergence criteria
- [ ] Optimize execution time

### Phase 4: Production Ready (Future)

**Goal**: Deploy for real-world use

**Tasks**:
- [ ] Add authentication
- [ ] Implement job queue
- [ ] Add progress monitoring
- [ ] Create comprehensive documentation

---

## ETL Pipeline

### Design Principles

1. **Explicit Transformations**: Every transformation is logged
2. **Validation**: Data is validated before and after transformation
3. **Reversibility**: Transformations can be traced back
4. **Economic Meaning**: Each transformation has clear economic interpretation

### OG-Core → CLEWS Pipeline

**Input**: `TPI_vars.pkl` from OG-Core
**Output**: `DiscountRate.csv` for CLEWS

```python
class ETLPipeline:
    def og_to_clews(self, og_results):
        """
        Transform OG-Core outputs to CLEWS inputs
        
        Args:
            og_results: Dict from TPI_vars.pkl
            
        Returns:
            clews_inputs: Dict with CLEWS parameters
        """
        # 1. Extract
        interest_rates = og_results['r']
        
        # 2. Transform
        n_years = 20  # Planning horizon
        discount_rate = np.mean(interest_rates[:n_years])
        
        # 3. Validate
        if not (0.0 <= discount_rate <= 0.2):
            raise ValueError(f"Invalid discount rate: {discount_rate}")
        
        # 4. Log
        self._log_transformation(
            source='OG-Core',
            source_var='r',
            target='CLEWS',
            target_var='DiscountRate',
            value=discount_rate
        )
        
        # 5. Return
        return {'DiscountRate': discount_rate}
```

### CLEWS → OG-Core Pipeline (Future)

**Input**: CLEWS results (electricity prices)
**Output**: OG-Core parameter updates

```python
def clews_to_og(self, clews_results):
    """
    Transform CLEWS outputs to OG-Core inputs
    
    Args:
        clews_results: Dict from CLEWS execution
        
    Returns:
        og_inputs: Dict for update_specifications()
    """
    # 1. Extract
    electricity_price = clews_results['electricity_price']
    
    # 2. Transform
    baseline_price = 50.0  # $/MWh
    cost_factor = electricity_price / baseline_price
    
    # 3. Validate
    if cost_factor < 0:
        raise ValueError("Negative cost factor")
    
    # 4. Return
    return {'energy_cost_factor': cost_factor}
```

### Validation Rules

**Interest Rates:**
- Range: 0% to 20%
- Type: Float
- Non-negative

**Discount Rates:**
- Range: 0% to 20%
- Type: Float
- Matches interest rate range

**Energy Prices:**
- Range: $0 to $500/MWh
- Type: Float
- Non-negative

---

## API Design

### RESTful Endpoints

**Base URL**: `http://localhost:5002`

### GET `/og/status`

**Description**: Check OG-Core execution status

**Response**:
```json
{
    "status": "idle|running|complete|error",
    "last_output_dir": "./og_output"
}
```

### GET `/og/real_data`

**Description**: Retrieve real OG-Core baseline data

**Response**:
```json
{
    "status": "success",
    "source": "Real OG-Core baseline run",
    "clews_discount_rate": 0.056766,
    "interest_rates": [0.059645, 0.059443, ...],
    "statistics": {
        "avg_20_years": 0.056766,
        "min": 0.050893,
        "max": 0.060178,
        "std": 0.001371
    },
    "message": "This is REAL data..."
}
```

### POST `/og/run`

**Description**: Execute OG-Core with parameters

**Request**:
```json
{
    "baseline": true,
    "time_path": true,
    "og_spec": {
        "T": 40,
        "S": 40,
        "frisch": 0.41
    },
    "output_dir": "./og_output"
}
```

**Response**:
```json
{
    "status": "success",
    "output_dir": "./og_output",
    "execution_time": 1234.56,
    "message": "OG-Core execution complete"
}
```

### POST `/og/transform`

**Description**: Transform data between models

**Request**:
```json
{
    "source": "og_core",
    "target": "clews",
    "variable": "discount_rate",
    "og_output_dir": "./og_output",
    "write_csv": true
}
```

**Response**:
```json
{
    "status": "success",
    "clews_inputs": {
        "discount_rate": 0.056766
    },
    "transformation_log": [...]
}
```

### POST `/og/coupled_run`

**Description**: Run coupled OG-Core + CLEWS

**Request**:
```json
{
    "og_params": {...},
    "clews_case": "case_name",
    "mode": "one_way|converging",
    "max_iterations": 10,
    "tolerance": 0.01
}
```

**Response**:
```json
{
    "status": "success",
    "iterations": 5,
    "converged": true,
    "og_result": {...},
    "clews_result": {...}
}
```

---

## Execution Modes

### Mode 1: Standalone OG-Core

**Use Case**: Run OG-Core independently

**Flow**:
```
User → API → OG Executor → OG-Core → Results
```

**API Call**:
```python
POST /og/run
{
    "baseline": true,
    "time_path": true
}
```

### Mode 2: Standalone CLEWS

**Use Case**: Run CLEWS independently (existing MUIO functionality)

**Flow**:
```
User → MUIO → OSeMOSYS → Results
```

### Mode 3: One-Way Coupling (OG → CLEWS)

**Use Case**: Use OG-Core results to inform CLEWS

**Flow**:
```
1. Run OG-Core
2. Extract interest rates
3. Transform to discount rate
4. Update CLEWS parameters
5. Run CLEWS
6. Return results
```

**API Call**:
```python
POST /og/coupled_run
{
    "mode": "one_way",
    "og_params": {...},
    "clews_case": "my_case"
}
```

### Mode 4: Converging Mode (Iterative)

**Use Case**: Find equilibrium between models

**Flow**:
```
1. Initialize with baseline OG-Core
2. Loop:
   a. Run OG-Core
   b. Transform OG → CLEWS
   c. Run CLEWS
   d. Transform CLEWS → OG
   e. Check convergence
   f. If not converged, goto 2a
3. Return converged results
```

**Convergence Criteria**:
```python
# Check if key variables have stabilized
def check_convergence(iteration_data, tolerance=0.01):
    if len(iteration_data) < 2:
        return False
    
    current = iteration_data[-1]
    previous = iteration_data[-2]
    
    # Check interest rate change
    r_change = abs(current['r'] - previous['r']) / previous['r']
    
    # Check energy price change
    p_change = abs(current['price'] - previous['price']) / previous['price']
    
    return (r_change < tolerance) and (p_change < tolerance)
```

---

## Testing Strategy

### Unit Tests

**Test Coverage**:
- ETL transformations
- Data validation
- API endpoints
- OG-Core wrapper

**Example**:
```python
def test_og_to_clews_transformation():
    # Setup
    og_results = {'r': np.array([0.05, 0.06, 0.055])}
    pipeline = ETLPipeline()
    
    # Execute
    clews_inputs = pipeline.og_to_clews(og_results)
    
    # Assert
    assert 'DiscountRate' in clews_inputs
    assert 0.0 <= clews_inputs['DiscountRate'] <= 0.2
```

### Integration Tests

**Test Scenarios**:
1. OG-Core execution → data extraction
2. Data transformation → validation
3. API endpoint → response format
4. End-to-end: OG → Transform → CLEWS

**Test Script**: `tests/test_og_integration.py`

```python
def test_real_data_endpoint():
    response = requests.get('http://localhost:5002/og/real_data')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'
    assert 'clews_discount_rate' in data
```

### Performance Tests

**Metrics**:
- OG-Core execution time
- API response time
- Data transformation time
- Memory usage

**Benchmarks**:
- OG-Core (T=40, S=40): < 30 minutes
- API response: < 100ms
- Transformation: < 1 second

---

## Deployment Plan

### Development Environment

```bash
# Local development
python MUIO/API/app.py
# Access: http://localhost:5002
```

### Production Considerations

**1. Web Server**
- Use Gunicorn or uWSGI instead of Waitress
- Configure workers based on CPU count
- Set up reverse proxy (Nginx)

**2. Job Queue**
- Use Celery for long-running OG-Core executions
- Redis or RabbitMQ as message broker
- Monitor job status

**3. Caching**
- Cache OG-Core results (expensive to compute)
- Use Redis for session management
- Cache transformed data

**4. Monitoring**
- Log all API requests
- Monitor execution times
- Alert on failures
- Track resource usage

**5. Security**
- Add authentication (OAuth2)
- Rate limiting
- Input validation
- HTTPS only

### Docker Deployment

```dockerfile
FROM python:3.9

# Install dependencies
RUN pip install ogcore flask numpy pandas plotly

# Copy application
COPY MUIO /app/MUIO
COPY src /app/src

# Expose port
EXPOSE 5002

# Run application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5002", "app:app"]
```

---

## Future Enhancements

### Short-term
- [ ] Add parameter validation UI
- [ ] Implement progress bars for long executions
- [ ] Add scenario comparison tools
- [ ] Export results to Excel

### Medium-term
- [ ] Multi-region support
- [ ] Automated sensitivity analysis
- [ ] Real-time execution monitoring
- [ ] Advanced visualization (3D plots)


---

## Success Criteria

### Technical
- ✅ Real OG-Core data integration
- ✅ Working ETL pipeline
- ✅ RESTful API endpoints
- ✅ Interactive visualization
- ⏳ Bidirectional coupling
- ⏳ Converging mode

### Economic
- ✅ Correct discount rate calculation
- ✅ Valid interest rate ranges
- ✅ Economic interpretation documented
- ⏳ Energy price feedback loop
- ⏳ Equilibrium convergence

### User Experience
- ✅ Simple API interface
- ✅ Clear documentation
- ✅ Real data demonstration
- ⏳ Intuitive UI
- ⏳ Progress monitoring

---

## Risks and Mitigation

### Risk 1: Long Execution Times

**Impact**: OG-Core takes 30+ minutes

**Mitigation**:
- Use reduced problem size (T=40, S=40)
- Implement job queue (Celery)
- Cache results
- Show progress indicators

### Risk 2: Convergence Failure

**Impact**: Coupled mode doesn't converge

**Mitigation**:
- Set maximum iterations
- Implement damping factors
- Log convergence metrics
- Provide manual override

### Risk 3: Data Validation Errors

**Impact**: Invalid data passed between models

**Mitigation**:
- Strict validation rules
- Comprehensive error messages
- Fallback to defaults
- Log all transformations

---

## Conclusion

This integration plan provides a clear roadmap for connecting OG-Core with MUIO/CLEWS. The modular design allows incremental implementation while maintaining system stability.

**Current Status**: Phase 1 complete with real data integration  
**Next Steps**: Implement bidirectional coupling (Phase 2)

---

**Document Version**: 1.0  
**Last Updated**: February 25, 2026  
**Author**: S Khavin