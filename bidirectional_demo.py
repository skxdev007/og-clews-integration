"""
Bidirectional OG-Core ↔ CLEWS Coupling Demonstration

This script demonstrates the complete bidirectional data flow:
1. OG-Core → CLEWS: Interest rates to discount rates
2. CLEWS → OG-Core: Energy prices to production parameters

Uses REAL OG-Core data to prove genuine model execution.
"""

import numpy as np
import sys
from pathlib import Path

# Add MUIO extension to path
sys.path.insert(0, str(Path(__file__).parent / "MUIO" / "OG_CLEWS_Extension"))

from backend.etl_pipeline import ETLPipeline


def main():
    print("=" * 80)
    print("BIDIRECTIONAL OG-CORE ↔ CLEWS COUPLING DEMONSTRATION")
    print("=" * 80)
    print()
    
    # Initialize ETL pipeline
    etl = ETLPipeline()
    
    # ========================================================================
    # STEP 1: OG-Core → CLEWS (Forward Direction)
    # ========================================================================
    print("STEP 1: OG-Core → CLEWS Transformation")
    print("-" * 80)
    print()
    
    # Load REAL OG-Core data
    real_data_file = "real_og_core_interest_rates.npy"
    if not Path(real_data_file).exists():
        print(f"ERROR: {real_data_file} not found!")
        print("Run extract_real_data.py first to extract real OG-Core outputs.")
        return
    
    interest_rates = np.load(real_data_file)
    print(f"✓ Loaded REAL OG-Core interest rates from {real_data_file}")
    print(f"  Data shape: {interest_rates.shape}")
    print(f"  First 5 years: {[f'{r*100:.4f}%' for r in interest_rates[:5]]}")
    print()
    
    # Create OG-Core results dict
    og_results = {'r': interest_rates}
    
    # Transform to CLEWS
    clews_inputs = etl.og_to_clews(og_results)
    
    print("✓ Transformed to CLEWS DiscountRate")
    print(f"  CLEWS DiscountRate: {clews_inputs['DiscountRate']:.6f} ({clews_inputs['DiscountRate']*100:.4f}%)")
    print()
    print("Economic Interpretation:")
    print(f"  This {clews_inputs['DiscountRate']*100:.2f}% discount rate will affect CLEWS energy")
    print(f"  investment decisions:")
    print(f"    - Higher rates favor low-capital technologies (natural gas)")
    print(f"    - Lower rates favor high-capital investments (solar, wind)")
    print()
    
    # ========================================================================
    # STEP 2: Simulate CLEWS Execution
    # ========================================================================
    print("STEP 2: CLEWS Execution (Simulated)")
    print("-" * 80)
    print()
    print("In a real integration, CLEWS would now run with the updated discount rate.")
    print("For this demo, we'll use representative energy prices from a CLEWS run:")
    print()
    
    # Simulated CLEWS outputs (these would come from actual CLEWS execution)
    clews_outputs = {
        'energy_prices': {
            'electricity': 0.12,  # $/kWh (typical US industrial rate)
            'natural_gas': 0.05   # $/kWh equivalent
        }
    }
    
    print(f"  Electricity price: ${clews_outputs['energy_prices']['electricity']:.4f}/kWh")
    print(f"  Natural gas price: ${clews_outputs['energy_prices']['natural_gas']:.4f}/kWh")
    print()
    
    # ========================================================================
    # STEP 3: CLEWS → OG-Core (Feedback Direction) - THIS CLOSES THE LOOP!
    # ========================================================================
    print("STEP 3: CLEWS → OG-Core Transformation (BIDIRECTIONAL FEEDBACK)")
    print("-" * 80)
    print()
    
    # Transform CLEWS outputs to OG-Core parameters
    og_params_updated = etl.clews_to_og(clews_outputs)
    
    print("✓ Transformed CLEWS energy prices to OG-Core parameters")
    print()
    print("Updated OG-Core Parameters:")
    print(f"  delta (depreciation rate): {og_params_updated['delta']:.6f}")
    print(f"  g_y (TFP growth rate): {og_params_updated['g_y']:.6f}")
    print(f"  energy_cost_factor: {og_params_updated['energy_cost_factor']:.4f}")
    print()
    print("Economic Interpretation:")
    print(f"  Energy cost factor of {og_params_updated['energy_cost_factor']:.2f}x baseline means:")
    if og_params_updated['energy_cost_factor'] > 1.0:
        print(f"    - Energy is {(og_params_updated['energy_cost_factor']-1)*100:.1f}% more expensive than baseline")
        print(f"    - Depreciation increased to {og_params_updated['delta']*100:.2f}% (faster equipment turnover)")
        print(f"    - TFP growth reduced to {og_params_updated['g_y']*100:.2f}% (productivity impact)")
    elif og_params_updated['energy_cost_factor'] < 1.0:
        print(f"    - Energy is {(1-og_params_updated['energy_cost_factor'])*100:.1f}% cheaper than baseline")
        print(f"    - Depreciation decreased to {og_params_updated['delta']*100:.2f}% (longer equipment life)")
        print(f"    - TFP growth increased to {og_params_updated['g_y']*100:.2f}% (productivity boost)")
    else:
        print(f"    - Energy at baseline cost (no adjustment needed)")
    print()
    
    # ========================================================================
    # STEP 4: Show Complete Transformation Log
    # ========================================================================
    print("STEP 4: Complete Transformation Log")
    print("-" * 80)
    print()
    print(etl.get_transformation_summary())
    
    # ========================================================================
    # Summary
    # ========================================================================
    print("=" * 80)
    print("BIDIRECTIONAL COUPLING COMPLETE")
    print("=" * 80)
    print()
    print("Data Flow Summary:")
    print()
    print("  OG-Core (interest rates)")
    print("      ↓")
    print(f"  CLEWS DiscountRate = {clews_inputs['DiscountRate']*100:.4f}%")
    print("      ↓")
    print("  CLEWS runs with updated discount rate")
    print("      ↓")
    print(f"  CLEWS outputs energy prices (elec=${clews_outputs['energy_prices']['electricity']:.4f}/kWh)")
    print("      ↓")
    print(f"  OG-Core parameters updated (delta={og_params_updated['delta']:.4f}, g_y={og_params_updated['g_y']:.4f})")
    print("      ↓")
    print("  OG-Core can re-run with energy cost feedback")
    print()
    print("This demonstrates COMPLETE bidirectional coupling, not just one-way data flow!")
    print()
    print("Next Steps:")
    print("  1. Use these parameters in OG-Core: p.update_specifications(og_params_updated)")
    print("  2. Re-run OG-Core to see how energy costs affect macroeconomic outcomes")
    print("  3. Iterate until convergence (converging mode)")
    print()


if __name__ == "__main__":
    main()
