from data_processing import DataHandler
import ollama
#Bilig lösning för att ladda in filen
file_path = r""

# Load and clean data
dataset = DataHandler(file_path)
llama="llama3.2"
deepseek = "deepseek-r1:8b"


# Critical Care
acth_CC_relative  = dataset.drivers_in_product_area_region_relative('ACTH','ACAT')
print(acth_CC_relative)


def summarize(analysis):
    # Step 3: Generate final consice.
    # use response2

    prompt = f"""
        ### **Context:**
        The following text summarizes the **major and minor order intake changes** across different product lines and regions.
        It also provide how large the change is percieved to be and the reasoning until then.
        ---
        ### **Raw Summary Data:**
        {analysis}

        ---
        ### **Task:**
        1️ Summarize the key insights from the provided data.  
        2️ Focus on **major trends** while keeping the response concise.   
        3 **DO NOT** repeat the original values; instead, extract meaningful takeaways.
        4 Keep it as concise as possible

        ---
        ### **Expected Output Format:**
        📌 **Summary of Key Insights:**
        - **[Product Line] in [Region]** is the main growth driver.
        - **[Product Line] in [Region] is increasing** .
        - **[Product Line] up in all regions
        - **Decrease from [Product Line] in [Region]
        - ** Main detraction from [Product Line]

        ### **Example output (from other data):Ventilation in US as main growth driver. 
        # Service up in all regions. Anesthesia increasing, 
        # mainly in EMEA. Decrease from Other 3rd party products in Canada.
        #  Monitoring Disposables decreasing in China. 

      

        ---
        ### **Rules:**
        # 1 Do not list specific numbers 
        2. **Provide insights, not raw data.**  
        3. **Keep it concise (3-5 short sentences).**  
        4. **DO NOT Include numbers in the final answer**
        """


    response3 = ollama.chat(model=deepseek, messages=[{"role": "user", "content": prompt}])
    final_summary = response3['message']['content'].strip()
    return final_summary


def summarize_orderintake_region(df):
 
    prompt = f"""
        ### **Context:**
        We are analyzing order intake changes for a few product lines in our company.

        The dataset consists of:
        - **Product Line**: Represents different product categories at our company. 
        - **Region**: The geographical area where changes occurred.
        - **Total Difference**: The monetary change in order intake.
        - **Product Area Contribution %**: The relative impact of each product line within the company

        ---
        ### **Dataset (Raw Data):**
        {df.to_string(index=False)}

        ---
        ### **Task:**
        1️⃣ **For each row in the dataset, classify it as one of the following:**
        - **Major Increase** → A significant positive driver of growth.
        - **Minor Increase** → A small but positive change.
        - **Major Decrease** → A significant decline impacting the product area.
        - **Minor Decrease** → A small but negative change.

        2️⃣ **Summarize each product line into the format:**
        - **[Product Line] in [Region]** is a **[Major/Minor] [Increase/Decrease]**, contributing **X% of product area impact**.

        3️⃣ **Identify key trends across all product lines:**
        - Which **product lines** are driving the most growth?
        - Which **product lines** are responsible for the largest declines?
        - Are changes **consistent across regions**, or do they vary?

        ---
        ### **Expected Output Format:**
        #### ** Categorized Product Line Summaries:**
        - **[Product Line] in [Region]**: **[Major/Minor] [Increase/Decrease]**, contributing **X% of product area impact**.
        ---
        ### **Rules:**
        1. **Determine "Major" vs. "Minor" dynamically** based on the scale of impact.  
        2. **Prioritize insights based on relative contribution to the product area.**  
        3. **DO NOT generate unnecessary explanations or code.**  
        """




    response3 = ollama.chat(model=deepseek, messages=[{"role": "user", "content": prompt}])
    final_summary = response3['message']['content'].strip()
    return final_summary

answer_testing = summarize_orderintake_region(acth_CC_relative)
print(answer_testing)

summary = summarize(answer_testing)
print(summary)