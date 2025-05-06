import logging
import ollama
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_processing import DataHandler
from mapping import productline_mapping

#file_path = os.getenv("ORDER_INTAKE_PATH")
file_path = os.getenv("NET_SALES_PATH")



dataset = DataHandler(file_path)

llama_8b = 'llama3.1:8b'


logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed output
    format='%(asctime)s - %(levelname)s - %(message)s'
)

#Summarize to natural language per product line and region 
#Make a summary of the drivers across regions in natural language 
#Make a summary of data with clearly stated rules on how long it should be 
#Sanity check if description is correct compared to the inputed data. 

#Roles
natural_language_interpreter = "You are a financial data analyst summarizing trends for the netsales in a company different product lines and regions."
analysis_role = "You are a business analyst specializing in data-driven insights for netsales trends."
summary_role = "You are a report writer summarizing trends for the netsales analysis for a qualative summary."
validator = "You are a financial validator that factchecks the financial reporting"

def natural_language(analysis):
    """Summary in natural language of the given"""

    analysis = analysis.reset_index(drop=True)
    string_analysis = analysis.to_string(index=False)

    print(string_analysis)
    prompt = f"""
        ### **Context:**
        This data summarizes *Changes in Net sales** between 2 periods across product lines and regions.
        Each entry contains:
        - The product-line
        - The region the entry relates to
        - The **magnitude** of the change (minor/major increase/decrease).
        - The **relative magnitude** to the overal change.
        
        ***The data:
        {string_analysis}

        ### **Task:**
        - **Summarize changes per row**, one at a time.
        - Clearly state **major vs. minor** changes.
        - Write in ** natural language**.

        ### **Rules:**
        - Use concise, structured sentences.
        - Do **not** include raw numbers, just directional trends.
        - Do **not** generate code.

        ### **Example Output:**
        - "[Product-Line] saw a **major increase** in [Region] of [Magnitude]"
        - "[Product- Line ]had a **minor decrease** in [Region] of [Magnitude]"
"""


    response3 = ollama.chat(model=llama_8b, 
                            messages=[
                                {"role": "system", "content": natural_language_interpreter},
                                {"role": "user", "content": prompt}],
                            options={"temperature":0}
                            )

    final_summary = response3['message']['content'].strip()
    return final_summary



def analysis_of_data(natural_language_report):
    """Summarizing analysis given by the previous LLM call"""

    prompt = f"""
        ### **Context:**
        The following data is summarization of the changes in Order Intake between two periods.
        It is per product line and presents in which regions that the changes occured
        In the analysis there is also the magnitude as well if it is considered a minor/major increase/decrease. 
        
        ---
        
        ### ** Summary Data:**
        
        {natural_language_report}

        ---
        ### **Task:**
        Create a summary of the data
        1. Consider one productline at a time
        2. Identify if the direction of change has been consistent across regions.
        3. Identify the major drivers [Product Line] + [Region] for increase and decrease.
        4. Write it in natural language.  (DO NOT GENERATE CODE)  
        
          ### **Rules:**
        - Write in **clear, structured language**.  
        - Do **not** generate code.

        ### **Example Output:**
        - "[Product Line] up in all regions across all regions."
        - "[Product Line] saw a major increase in [Region]."
        - "[Product Line] saw a minor decrease across all [Region(s)]
"""

    response3 = ollama.chat(model=llama_8b, 

                            messages=[{"role": "system", "content": analysis_role},
                                {"role": "user", "content": prompt}],
                            options={"temperature":0}
                            )

    final_summary = response3['message']['content'].strip()
    return final_summary


def summary(analysis):
    """Summarizing analysis given by the previous LLM call"""

    prompt = f"""
        ### **Context:**
        The following data is from an analyis of the changes in Order Intake between two periods.
        In the analysis there is also the magnitude as well if it is considered a minor/major increase/decrease. 

        
        ---
        
        ### **Raw Summary Data:**
        
        {analysis}

        ---
        ### **Task:**
        Create a summary of the data
        1.Write a **concise summary** of the key trends.
        2.Highlight significant changes and ignore minor fluctiations. 

        ##** Example Output **
        Use sentences like the following.
        [Product Line] in [Region] as main growth driver. 
        # [Product Line] up in all regions. [Product Line] increasing, 
        # mainly in [Region]. Decrease from [Product Line] in [Region].
        # [Product Line] decreasing in [Region]. 

        ###Rules:###
        1. Maximum 4 sentences
        2. Make it descriptive and consice.
        3. DO NOT GENERATE CODE!
        
    """

    response3 = ollama.chat(model=llama_8b,
                            messages=[{"role": "system", "content":summary_role},
                                    {"role": "user", "content": prompt}],
                            options={"temperature":0}
                            )

    final_summary = response3['message']['content'].strip()
    return final_summary


# Sanity check

def validate_summary(summary, raw_data):
    """Ensure summary does not introduce errors or hallucinations."""
    raw_data_string = raw_data.to_string()
    
    prompt = f"""
        ### **Context:**
        Below is a generated summary of Netsales trends within our company. 
        Your task is to validate if the summary describes the raw data well.

        ### **Raw Data:**
        {raw_data_string}

        ### **Generated Summary:**
        {summary}

        ### **Task:**
        1. Verify that all trends match the raw data.
        2. Flag any incorrect or misleading information.
        3. Correct the summary if a major mistake has been made

        ### **Example Output:**
        - "Validation Passed: No inconsistencies."
        - "Validation Warning: [Product Line] in [Region] is reported as an increase, but data shows a decrease."
        - "Validation Warning: [Product Line] reported decrease across all regions, but data show increases in [Region]
        - "Corrected Summary:......
    """
    
    response = ollama.chat(
        model=llama_8b,
        messages=[{"role": "system", "content": validator},
                  {"role": "user", "content": prompt}],
        options={"temperature": 0}
    )
    
    return response['message']['content'].strip()



def all_prompts_together(dataset, business_area):
    # Preprocess data
    data = dataset.drivers_in_business_area_region_relative(business_area)

    # Step 1: Natural language generation
    natural_language_result = natural_language(data)
    logging.info('----- Natural Language -----\n%s', natural_language_result)

    # Step 2: Analysis
    analysis_result = analysis_of_data(natural_language_result)
    logging.info('----- Analysis -----\n%s', analysis_result)

    # Step 3: Summary
    summary_result = summary(analysis_result)
    logging.info('----- Summary -----\n%s', summary_result)

    # Step 4: Sanity Check
    sanity_check = validate_summary(summary_result, data)
    logging.info('----- Sanity Check -----\n%s', sanity_check)

    return summary_result, sanity_check



def compilation(dataset, business_area):
    # Loop through the product area (only LISC here)
    with open("LISC_test.txt", "a", encoding="utf-8") as file:
        print(dataset)
        answer, sanity_check = all_prompts_together(dataset, business_area)
        answer_mapped = productline_mapping(answer)
        sanity_check_mapped = productline_mapping(sanity_check)

        # Use the improved output format
        write_structured_output(
            file=file,
            product_area="LISC",
            summary=answer_mapped,
            validation=sanity_check_mapped
        )

        print("Response for LISC saved to LISC_test.txt!")

    return



def write_structured_output(file, product_area, summary, validation):
    file.write(f"\n{'=' * 60}\n")
    file.write(f"Product Area: {product_area}\n")
    file.write(f"{'=' * 60}\n\n")

    file.write("🔍 Summary of Key Trends:\n")
    file.write("-" * 60 + "\n")
    file.write(summary.strip() + "\n\n")

    file.write("✅ Validation Report:\n")
    file.write("-" * 60 + "\n")
    file.write(validation.strip() + "\n")
    file.write("\n" + "=" * 60 + "\n\n")



compilation(dataset, 'LISC')