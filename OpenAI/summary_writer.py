import sys
import os
import pandas as pd
import re
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_processing import DataHandler
from mapping import map_productlines_in_dataframe, productline_mapping
from openai import OpenAI


load_dotenv()
api_key = os.getenv("API_KEY")
client = OpenAI(api_key=api_key)


SYSTEM_PROMPT = """
You are a financial analyst writing a financial report. Your task is to analyze and summarize changes in financial data.

You must write a concise summary in at most 4 sentences to complement the numerical data in a financial report. 
Focus on clear, direct language and only state what is evident in the data — no speculation or recommendations. 
Do not include numbers. Focus on trends, main drivers, and regions as specified.
"""


PROMPT_TEMPLATES = {
    "net_sales": """
The data below shows net sales changes segmented by product line and region, with relative contributions to the overall change in a business area.
The overall change is {overall_change}.

Instructions:
- Identify whether the overall trend is an increase or decrease
- Detect the main positive and main negative drivers
- Detect if there are product lines where the direction of change is consistent across all Regions
- Write a concise final qualitative summary about the detected trends
- Start the summary by mentioning the driver that has the biggest overall impact. 

Rules for the final summary
- Maximum of 4 sentences for the summary
- Do not speculate, do not include numbers, only state what the data clearly shows
- Do not include the overall trend in the summary since that is already understood.
- No need to use linking words or similar filling words, use language similar to that in the provided examples.

Expected output examples:
Example 1: All product lines up. [Product Line] in [Region] as main growth driver. [Product Line] increasing in [Region]. Increase from [Product Line] in [Region]. [Product Line] up in all regions.
Example 2: [Product Line] and [Product Line] decreasing in [Region]. [Product Line] in [Region] as main detractor, partly offset by [Product Line] in [Region].
Example 3: [Product Line] in [Region] as main detractor. Increase from [Product Line] in [Region].
Example 4: [Product Line] up in all regions. [Product Line] down in [Region]. [Product line] up in [Region]

Data:
{data_block}
""",
    "order_intake": """
The data below shows order intake changes segmented by product line and region, with relative contributions to the overall change in a business area.
The overall change is {overall_change}
Instructions:
- Detect the main positive and main negative drivers
- Detect if there are product lines where the direction of change is consistent across all Regions
- Write a concise qualitative summary about the detected trends
- Start mentioning the trend that has the biggest impact overall

Rules for the output
- Maximum of 4 sentences for the summary
- Do not speculate, do not include numbers, only state what the data clearly shows
- Do not include the overall trend in the summary since that is already understood.
- No need to use linking words or similar filling words, use language similar to that in the provided examples.
- A proudctline can only be mentioned once in the summary
- There cannot be a main detractor and a main growth driver in the same summary.
- Only use terms as main detractor and main growth driver if there is a productline that stands out from the rest.

Expected output examples:
Example 1: All product lines up. [Product Line] in [Region] as main growth driver. [Product Line] increasing in [Region]. Increase from [Product Line] in [Region]. [Product Line] up in all regions.
Example 2: [Product Line] and [Product Line] decreasing in [Region]. [Product Line] in [Region] as main detractor, partly offset by [Product Line] in [Region].
Example 3: [Product Line] in [Region] as main detractor. Increase from [Product Line] in [Region].
Example 4: [Product Line] up in all regions. [Product Line] down in [Region]. [Product line] up in [Region]

Data:
{data_block}
"""
}


def summarize_block(data_block: str, summary_type: str, overall_change:str) -> dict:
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
        max_tokens=150,
        
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


def data_summarizer(dataset, business_area, product_area_list, summary_type):
    dataset.transform_data(['[Difference]'])
    summaries = []

    if business_area == 'LISC':
        df = dataset.drivers_in_business_area_region_relative(business_area)
        map_productlines_in_dataframe(df, 'Product Line')
        if not df.empty:
            block_str = df.to_string(index=False)
            overall_change = df['Total Difference'].sum()
            result = summarize_block(block_str, summary_type, overall_change)
            summaries.append(format_summary(result, business_area, "All"))
    else:
        for pa in product_area_list:
            df = dataset.drivers_in_product_area_region_relative(business_area, pa)
            map_productlines_in_dataframe(df, 'Product Line')
            if df.empty:
                continue
            block_str = df.to_string(index=False)
            overall_change = df['Total Difference'].sum()
            result = summarize_block(block_str, summary_type, overall_change)
            summaries.append(format_summary(result, business_area, pa))

    return summaries


def format_summary(result, business_area, product_area):
    return {
        "Business Area": business_area,
        "Product Area": product_area,
        "Summary": result["summary"],
        "Input Tokens": result["input_tokens"],
        "Output Tokens": result["output_tokens"],
        "Total Tokens": result["total_tokens"],
    }


def format_summaries_for_txt(summaries):
    output = []
    for item in summaries:
        sentences = re.split(r'(?<=[.!?])\s+', item['Summary'].strip())
        mapped_product_area = productline_mapping(item['Product Area'])
        formatted_summary = "\n".join(sentences)

        section = (
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
        "ACTH": ['ACAT', 'ACCA', 'ACCC', 'ACCP', 'ACG3', 'ACTC', 'ACVI'],
        "SWIC": ['ARJO', 'SWA3', 'SWIN', 'SWIW', 'SWWP'],
        "LISC": None
    }

    all_summaries = []

    for business_area, product_list in business_area_product_map.items():
        print(f"Processing {business_area} ({summary_type})...")
        summaries = data_summarizer(dataset, business_area, product_list, summary_type)
        all_summaries.extend(summaries)

    formatted_text = format_summaries_for_txt(all_summaries)

    txt_path = "summaries.txt"
    csv_path = "summaries.csv"

    with open(txt_path, "a", encoding="utf-8") as f:
        f.write(f"\n=== {summary_type.upper()} SUMMARY ===\n\n")
        f.write(formatted_text + "\n")

    for item in all_summaries:
        item["Product Area"] = productline_mapping(item["Product Area"])
        item["Summary Type"] = summary_type

    df = pd.DataFrame(all_summaries)
    if os.path.exists(csv_path):
        df.to_csv(csv_path, mode='a', header=False, index=False, sep=';', encoding='utf-8-sig')
    else:
        df.to_csv(csv_path, index=False, sep=';', encoding='utf-8-sig')

    print(f" Appended {summary_type} summary to summaries.txt and summaries.csv")

    return formatted_text


# Run both types
if __name__ == "__main__":
    create_summary(
        os.getenv("NET_SALES_PATH"),
        summary_type="net_sales"
    )

    create_summary(
        os.getenv("ORDER_INTAKE_PATH"),
        summary_type="order_intake"
    )
