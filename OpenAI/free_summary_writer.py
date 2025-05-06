import sys
import os
import pandas as pd
import re
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_processing import DataHandler
from mapping import map_productlines_in_dataframe, productline_mapping
from openai import OpenAI

#LESS STRICT SUMMARY

load_dotenv()
api_key = os.getenv("API_KEY")
client = OpenAI(api_key=api_key)


SYSTEM_PROMPT = """
You are a financial analyst writing a financial report. Your task is to analyze and summarize changes in financial data between 2 periods.

You must write a concise summary to complement the numerical data in a financial report. 
Focus on clear, direct language and only state what is evident in the data — no speculation or recommendations. 
Focus on trends, main drivers, and regions as specified.
"""

PROMPT_TEMPLATES = {
    "order_intake": """
The data below shows order intake changes segmented by product line and region, with relative contributions to the overall change in a business area.
Across the product line the change is {overall_change}
Instructions:
- Identify whether the overall trend is an increase or decrease.
- Summarize per productline and mention the regions that has contributed to a decrease or increase
- Write it in the same order as it has impact on the overall change
- Do mention if all regions has had an negative or positive impact

Rules for the final summary
- Do not speculate, only state what the data clearly shows
- Write a concise 4 sentence summary
- No need to use linking words or similar filling words
- Do not include explicit numbers

Data:
{data_block}
""",
    "net_sales": """
The data below shows net sales changes segmented by product line and region, with relative contributions to the overall change in a business area.
Across the product line the change is {overall_change}

Instructions:
-Identify whether the overall trend is an increase or decrease.
- Summarize per productline and mention the regions that has contributed to a decrease or increase
- Write it in the same order as it has impact on the overall change
- Do mention if all regions has had an negative or positive impact

Rules for the final summary
- Do not speculate, only state what the data clearly shows
- Write a concise 4 sentence summary
- No need to use linking words or similar filling words
- Do not include explicit numbers

Data:
{data_block}
"""
}

def summarize_data_block(data_block: str, summary_type: str, overall_change: str) -> dict:
    user_prompt = PROMPT_TEMPLATES[summary_type].format(
    data_block=data_block.strip(),
    overall_change=overall_change
)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.strip()},
            {"role": "user", "content": user_prompt.strip()}
        ],
        temperature=0.2,
        max_tokens=150
    )

    content = response.choices[0].message.content
    usage = response.usage
    cost = (usage.prompt_tokens / 1000 * 0.005) + (usage.completion_tokens / 1000 * 0.015)

    return {
        "summary": content,
        "input_tokens": usage.prompt_tokens,
        "output_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens,
        "estimated_cost": round(cost, 4)
    }

def format_summary(result, business_area, product_area, summary_type):
    return {
        "Business Area": business_area,
        "Product Area": product_area,
        "Summary": result["summary"],
        "Input Tokens": result["input_tokens"],
        "Output Tokens": result["output_tokens"],
        "Total Tokens": result["total_tokens"],
        "Estimated Cost ($)": result["estimated_cost"],
        "Summary Type": summary_type
    }

def data_summarizer(dataset, business_area, product_area_list, summary_type):
    dataset.transform_data(['[Difference]'])
    summaries = []

    if business_area == 'LISC':
        df = dataset.drivers_in_business_area_region_relative(business_area)
        map_productlines_in_dataframe(df, 'Product Line')
        if not df.empty:
            block_str = df.to_string(index=False)
            overall_change = df['Total Difference'].sum()
            result = summarize_data_block(block_str, summary_type, overall_change)
            summaries.append(format_summary(result, business_area, "All", summary_type))
    else:
        for pa in product_area_list:
            df = dataset.drivers_in_product_area_region_relative(business_area, pa)
            map_productlines_in_dataframe(df, 'Product Line')
            if df.empty:
                continue
            block_str = df.to_string(index=False)
            overall_change = df['Total Difference'].sum()
            result = summarize_data_block(block_str, summary_type, overall_change)
            summaries.append(format_summary(result, business_area, pa, summary_type))

    return summaries

def format_summaries_for_txt(summaries):
    output = []
    for item in summaries:
        sentences = re.split(r'(?<=[.!?])\s+', item['Summary'].strip())
        mapped_product_area = productline_mapping(item['Product Area'])
        formatted_summary = "\n".join(sentences)

        section = (
            f"Summary Type : {item['Summary Type']}\n"
            f"Business Area : {item['Business Area']}\n"
            f"Product Area  : {mapped_product_area}\n"
            f"Summary:\n{formatted_summary}\n"
            f"{'-'*60}"
        )
        output.append(section)
    return "\n\n".join(output)

def create_summary(file_path, summary_type):
    dataset = DataHandler(file_path)

    business_area_product_map = {
        "ACTH": ['ACAT', 'ACCA', 'ACCC', 'ACCP', 'ACCP', 'ACG3', 'ACTC', 'ACVI'],
        "SWIC": ['ARJO', 'SWA3', 'SWIN', 'SWIW', 'SWWP'],
        "LISC": None
    }

    all_summaries = []

    for business_area, product_list in business_area_product_map.items():
        print(f"Processing {business_area} ({summary_type})...")
        summaries = data_summarizer(dataset, business_area, product_list, summary_type)
        all_summaries.extend(summaries)

    formatted_text = format_summaries_for_txt(all_summaries)

    txt_path = "summaries_free.txt"
    csv_path = "summaries_free.csv"

    with open(txt_path, "a", encoding="utf-8") as f:
        f.write(f"\n=== {summary_type.upper()} SUMMARY ===\n\n")
        f.write(formatted_text + "\n")

    for item in all_summaries:
        item["Product Area"] = productline_mapping(item["Product Area"])

    df = pd.DataFrame(all_summaries)
    if os.path.exists(csv_path):
        df.to_csv(csv_path, mode='a', header=False, index=False, sep=';', encoding='utf-8-sig')
    else:
        df.to_csv(csv_path, index=False, sep=';', encoding='utf-8-sig')

    print(f"Appended {summary_type} summary to summaries_free.txt and summaries_free.csv")

    return formatted_text

if __name__ == "__main__":
    create_summary(
        os.getenv("ORDER_INTAKE_PATH"),
        summary_type="order_intake"
    )

    create_summary(
        os.getenv("NET_SALES_PATH"),
        summary_type="net_sales"
    )
