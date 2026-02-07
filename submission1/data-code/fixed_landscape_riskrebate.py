#!/usr/bin/env python3
"""Fix the notebook with correct 2018 file handling"""

import json

# Read notebook
with open('landscape_risk_rebate_2014_2018.ipynb', 'r') as f:
    nb = json.load(f)

# Get cell 2 (index 2)
cell = nb['cells'][2]
source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']

# Find the read_risk_rebate_2018 function and replace it
start_marker = 'def read_risk_rebate_2018() -> pd.DataFrame:'
end_marker = '\n\ndef '

start_idx = source.find(start_marker)
if start_idx == -1:
    print("ERROR: Could not find start of function")
    exit(1)

end_idx = source.find(end_marker, start_idx)
if end_idx == -1:
    # Maybe it's the last function
    end_idx = len(source)

before = source[:start_idx]
after = source[end_idx:] if end_idx < len(source) else ""

new_function = '''def read_risk_rebate_2018() -> pd.DataFrame:
    """
    Read and process 2018 risk/rebate data.
    """
    # Part C file
    partc_path = INPUT_DIR / "risk_rebate_2018" / "2018PartCPlanLevel.xlsx"
    
    # Note: 2018 file has different structure - headers at row 2 (skiprows=2)
    risk_rebate_a = pd.read_excel(
        partc_path,
        engine='openpyxl',
        sheet_name='result.srx',
        skiprows=2,
        usecols="A:G",
        names=["contractid", "planid", "contract_name", "plan_type",
               "riskscore_partc", "payment_partc", "rebate_partc"]
    )
    
    # Clean Part C data
    def parse_number(x):
        if pd.isna(x):
            return np.nan
        s = str(x).replace(",", "").replace("$", "")
        try:
            return float(s)
        except:
            return np.nan
    
    risk_rebate_a["riskscore_partc"] = risk_rebate_a["riskscore_partc"].apply(parse_number)
    risk_rebate_a["payment_partc"] = risk_rebate_a["payment_partc"].apply(parse_number)
    risk_rebate_a["rebate_partc"] = risk_rebate_a["rebate_partc"].apply(parse_number)
    risk_rebate_a["planid"] = pd.to_numeric(risk_rebate_a["planid"], errors="coerce")
    risk_rebate_a["year"] = 2018
    
    risk_rebate_a = risk_rebate_a[[
        "contractid", "planid", "contract_name", "plan_type",
        "riskscore_partc", "payment_partc", "rebate_partc", "year"
    ]]
    
    # Part D file
    partd_path = INPUT_DIR / "risk_rebate_2018" / "2018PartDPlans.xlsx"
    
    risk_rebate_b = pd.read_excel(
        partd_path,
        engine='openpyxl',
        sheet_name='result.srx',
        skiprows=2,
        usecols="A:H",
        names=["contractid", "planid", "contract_name", "org_type",
               "directsubsidy_partd", "riskscore_partd", "reinsurance_partd",
               "costsharing_partd"]
    )
    
    # Clean Part D data
    risk_rebate_b["directsubsidy_partd"] = risk_rebate_b["directsubsidy_partd"].apply(parse_number)
    risk_rebate_b["reinsurance_partd"] = risk_rebate_b["reinsurance_partd"].apply(parse_number)
    risk_rebate_b["costsharing_partd"] = risk_rebate_b["costsharing_partd"].apply(parse_number)
    risk_rebate_b["riskscore_partd"] = risk_rebate_b["riskscore_partd"].apply(parse_number)
    
    risk_rebate_b["payment_partd"] = (
        risk_rebate_b["directsubsidy_partd"] + 
        risk_rebate_b["reinsurance_partd"] + 
        risk_rebate_b["costsharing_partd"]
    )
    risk_rebate_b["planid"] = pd.to_numeric(risk_rebate_b["planid"], errors="coerce")
    
    risk_rebate_b = risk_rebate_b[[
        "contractid", "planid", "payment_partd",
        "directsubsidy_partd", "reinsurance_partd", "costsharing_partd",
        "riskscore_partd"
    ]]
    
    # Merge Part C and Part D
    final_risk_rebate = risk_rebate_a.merge(
        risk_rebate_b,
        on=["contractid", "planid"],
        how="left"
    )
    
    return final_risk_rebate
'''

new_source = before + new_function + after

# Update cell
cell['source'] = new_source.split('\n')

# Write back
with open('landscape_risk_rebate_2014_2018.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print("Successfully updated read_risk_rebate_2018 function")
