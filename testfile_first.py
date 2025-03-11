import pandas as pd
import numpy as np
import ollama
import pandas as pd
from data_processing import DataHandler


file_path = r"C:\Users\nikla\OneDrive\Skrivbord\OPIS020 - Order intake, external QTD 2411 vs 2311_v2.csv"

# Load and clean data
dataset = DataHandler(file_path)

# Print total sum of values
print("Total Value_mper:", dataset.get_mper_total())
print("Total Value_cper:", dataset.get_cper_total())

# Check business areas
unique_business_areas = dataset.get_unique_business_areas()
print("Unique Business Areas:", unique_business_areas)

# Apply another filter on the filtered DataFrame (Life Sciences)
lifescience_df = dataset.filter_by_business_area('LISC')

# Display results
print("Life Science Data:\n", lifescience_df.head())

# Drivers per product area
drivers_product_area = dataset.drivers_per_product_area('LISC')
print(drivers_product_area)

total_change = drivers_product_area['Total Difference'].sum()
divided_per_region = dataset.drivers_per_product_area_region('LISC')
print(divided_per_region)
divided_product_line_region = dataset.drivers_per_product_line_region('LISC')
print(divided_product_line_region)

# STEP 1: Identify the product area with anomolies
def identify_key_product_area(df):
    """Uses an LLM to identify the Product Area Code with the largest absolute difference."""

    df_string = df.to_string()

    # Create a clearer LLM prompt
    prompt = f"""
    We are analyzing order intake changes between two periods.
    
    The dataset consists of three columns:
    - **Product Area**: Represents different product areas.
    - **The region it concerns
    - **Total Difference**: The monetary change in order intake between the periods.

    **Sorted data (largest absolute changes first):**
    {df_string}

    **Task:**  1.Identify the **top product areas** and in what ***regions** the changes are most dramatic (positive or negative).
    **         2. Summarize the findings return the product area codes and the region, in ascending order.**
                Note: Do not provide code that I can run

    """

    # Get response from LLM
    response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": prompt}])

    # Extract LLM output
    key_product_area = response['message']['content'].strip()

    return key_product_area


#answer = identify_key_product_area(drivers_product_area)
#print(answer)


def identify_key_product_area(df):
    """Uses an LLM to identify the Product Area Code with the largest absolute difference."""

    df_string = df.to_string()

    # Create a clearer LLM prompt
    prompt = f"""
    We are analyzing order intake changes between two periods.
    
    The dataset consists of three columns:
    - **Product line**: Represents different product areas.
    - **Region**: The region where the changes come from
    - **Total Difference**: The monetary change in order intake between the periods.

    **Sorted data (largest absolute changes first):**
    {df_string}

    **Task:**  1. Understand which areas and regions that stands out (larger absolute differences compared to the rest)
               2. Identify the **top product areas** and in what ***regions** the changes are most dramatic (positive or negative).
    **         3. Summarize the findings with a short summary. Ex Business area [] in region [] is driving decrease.**
                Note: Do not provide code that I can run

    """

    # Get response from LLM
    response = ollama.chat(model="deepseek-r1:8b", messages=[{"role": "user", "content": prompt}])

    # Extract LLM output
    key_product_area = response['message']['content'].strip()

    return key_product_area

answer = identify_key_product_area(divided_product_line_region)
print(answer)

### 🔹 STEP 3: Summarize Insights
def generate_summary(analysis):
    """Generate an executive summary of the analysis."""
    prompt = f"""
    We are analyzing order intake differences between two periods. Identify the **specific product areas** that has the 
    most significant impact on the overall. Every row has a product area, product line, some rows regarding the geographical regions that it corresponds to
    and, the absolute changes and the change in percentage. 
    {analysis}

    Generate an executive summary on what is the main drivers of the overall decline or increase.
    """
    response = ollama.chat(model="deepseek-r1:8b", messages=[{"role": "user", "content": prompt}])
    return response['message']['content']

