import re

# Process each line and extract "CODE - NAME" pairs


mapping = {
    'ACA3':'Acute Care Therapies Other',
    'ACAT':'Endovascular & AT Grafts/Drains',
    'ACCA':'Cardiac Assist',
    'ACCC':'Critical Care', 
    'ACCP':'Cardiopulmonary', 
    'ACG3':'Digital Solutions',
    'ACTC':'Transplant Care',
    'ACVI':'Vascular Interventions',
    'ARJO':'Arjo products',
    'SWA3':'Surgical Workflows Other',
    'SWIN':'Infection Control', 
    'SWIW':'Digital Health Solutions',
    'SWWP':'Surgical Workplaces',
    'ACA3': 'Acute Care Therapies Other', 
    'ACAP': 'Adjustment product Acute Care Therapies,', 
    'ACAT': 'Endovascular & AT Grafts/Drains,', 
    'ATBS': 'AT Biosurgery',
    'ATDR': 'AT Drainage', 
    'ATGE': 'OLD Atrium General', 
    'ATGR': 'AT Grafts', 
    'ATOM': 'AT OEM', 
    'ATST': 'AT Covered Stents',
    'ATTM': 'AT Thrombus Management', 
    'ACCA': 'Cardiac Assist',
    'CADI': 'CA Disposables', 
    'CAGE': 'OLD Cardiac General',
    'CAHW': 'CA Hardware', 
    'CAOM': 'CA OEM', 
    'CAOT': 'CA Other', 
    'CASV': 'CA Service', 
    'SSCA': 'OLD Cardiac Assist Segment', 
    'ACCC': 'Critical Care', 
    'CCAA': 'CC Anesthesia', 
    'CCDS': 'CC Digital Solutions', 
    'CCGD': 'OLD EIRUS Disposables', 
    'CCGM': 'OLD EIRUS Hardware', 
    'CCHD': 'CC Advanced Monitoring Disposables', 
    'CCHH': 'CC Advanced Monitoring Hardware',
    'CCMO': 'OLD Monitoring',
    'CCOM': 'OLD Critical Care OEM', 
    'CCOT': 'CC Other', 
    'CCSE': 'CC Service', 
    'CCTP': 'OLD Therapy Products', 
    'CCVE': 'CC Ventilation', 
    'ACCP': 'Cardiopulmonary',
    'CPDE': 'CP Disposables ECLS', 
    'CPDS': 'CP Disposables Surgical Perfusion', 
    'CPHE': 'CP Hardware ECLS', 
    'CPHS': 'CP Hardware Surgical Perfusion', 
    'CPOM': 'OLD Cardiopulmonary OEM', 
    'CPOT': 'CP Other',
    'CPSE': 'CP Service', 
    'SUCP': 'OLD Cardiopulmonary Segment', 
    'ACCS': 'Cardiac Surgery', 
    'CSAB': 'CS Transmyocardial Revasculation', 
    'CSAO': 'CS Left Atrial Appendage Occlusion', 
    'CSGE': 'OLD Cardiac Surgery general', 
    'CSHB': 'CS Beating Heart', 
    'CSOM': 'OLD Cardiac Surgery OEM',
    'CSVH': 'CS Vessel Harvesting', 
    'ACG3': 'Digital Solutions', 
    'ACGD': 'DS Advanced Clinical Guidance', 
    'ACTC': 'Transplant Care', 
    'TCAB': 'TC Abdominal', 
    'TCSE': 'TC Service', 
    'TCTH': 'TC Thoracic', 
    'ACTH': 'Acute Care Therapies', 
    'ACVI': 'Vascular Interventions', 
    'VIGA': 'VI Aortic Grafts', 
    'VIGC': 'VI Peripheral Vascular Grafts (Composite)', 
    'VIGP': 'VI Peripheral Vascular Grafts (PET)', 
    'VIOM': 'VI OEM', 
    'VSGE': 'OLD Vascular Intervention general', 
    'VSSG': 'OLD Stent Grafts', 
    'LIA3': 'Life Science Other', 
    'LSAP': 'Adjustment product Life Science', 
    'LSCO': 'OLD LS Consumables', 
    'LSSP': 'OLD Life Science Spare Parts', 
    'LISC': 'Life Science', 
    'LSBC': 'BP Consumables', 
    'LSBI': 'Bio-Processing', 
    'LSBR': 'BP Bio Reactors', 
    'LSLS': 'OLD Life Science', 
    'LSNC': 'NU Consumables', 
    'LSNL': 'Nuclear', 
    'LSNS': 'NU Service', 
    'LSNU': 'NU Nuclear', 
    'LSSE': 'LS Service (excl. NU)', 
    'LSSV': 'Service', 
    'LSPO': 'ST Ports & Containers', 
    'LSSC': 'ST Beta Bags and Consumables', 
    'LSTR': 'Sterile Transfer', 
    'LSFC': 'UDP Filling Line Consumables & Connectors', 
    'LSFL': 'UDP Filling Lines', 
    'LSFP': 'UDP Fluid Pathway', 
    'LSPU': 'UDP Pumps & Other Capital Equipment', 
    'LSUD': 'Up-stream Down-stream Processing', 
    'LSIS': 'WIS Isolation', 
    'LSST': 'WIS Sterilization', 
    'LSWA': 'WIS Washers',
    'LSWC': 'WIS Consumables', 
    'LSWI': 'Washer / Isolator / Sterilizer', 
    'ARJC': 'Arjo products', 
    'ARJO': 'Arjo products', 
    'ARJR': 'OLD Arjo products recurring', 
    'SWA3': 'Surgical Workflows Other', 
    'SWAP': 'Adjustment product Surgical Workflows', 
    'SWIC': 'Surgical Workflows', 
    'INCO': 'IC Consumables', 
    'INDI': 'IC Disinfection Health Care', 
    'INEN': 'IC Endoscopy', 
    'INLO': 'IC Loading Eqpt / Automation', 
    'INLT': 'IC Low Temp Sterilization', 
    'INSE': 'IC Service', 
    'INSP': 'OLD IC Spare Parts', 
    'INST': 'IC Sterilization', 
    'SWIN': 'Infection Control', 
    'IWOI': 'DHS OR Integration', 
    'IWPF': 'DHS OR and Patient Flow Management', 
    'IWSE': 'DHS Service', 
    'IWSS': 'DHS Sterile Supply Management', 
    'SWIW': 'Digital Health Solutions', 
    'SUMD': 'OLD Medap',
    'SUSY': 'OLD Workplaces general',
    'SUWP': 'OLD Surgical Workplaces Segment',
    'SWOM': 'OLD Surgical Workplaces OEM', 
    'SWWP': 'Surgical Workplaces', 
    'WPAS': 'SWP Assist Systems', 
    'WPCD': 'SWP Ceiling Devices', 
    'WPNI': 'SWP Near-Infrared Imaging', 
    'WPOL': 'SWP Operating Lights', 
    'WPOT': 'SWP Operating Tables', 
    'WPSE': 'SWP Service', 
    'WPSO': 'SWP Other', 
    'WPVA': 'SWP Modular Wall Systems',
    'INCO': 'IC Consumables', 
    'INDI': 'IC Disinfection Health Care', 
    'INEN': 'IC Endoscopy', 
    'INLO': 'IC Loading Eqpt / Automation', 
    'INLT': 'IC Low Temp Sterilization', 
    'INSE': 'IC Service', 
    'INSP': 'OLD IC Spare Parts', 
    'INST': 'IC Sterilization', 
    'SWIN': 'Infection Control', 
    'IWOI': 'DHS OR Integration', 
    'IWPF': 'DHS OR and Patient Flow Management', 
    'IWSE': 'DHS Service', 
    'IWSS': 'DHS Sterile Supply Management', 
    'SWIW': 'Digital Health Solutions', 
    'SUMD': 'OLD Medap', 
    'SUSY': 'OLD Workplaces general', 
    'SUWP': 'OLD Surgical Workplaces Segment', 
    'SWOM': 'OLD Surgical Workplaces OEM', 
    'SWWP': 'Surgical Workplaces', 
    'WPAS': 'SWP Assist Systems', 
    'WPCD': 'SWP Ceiling Devices', 
    'WPNI': 'SWP Near-Infrared Imaging', 
    'WPOL': 'SWP Operating Lights', 
    'WPOT': 'SWP Operating Tables', 
    'WPSE': 'SWP Service', 
    'WPSO': 'SWP Other', 
    'WPVA': 'SWP Modular Wall Systems',
    'DHS' : 'Health Solutions management', #Kolla 
    'SWIW': 'Digital Health Solutions', 
    'SUMD': 'OLD Medap', 
    'SUSY': 'OLD Workplaces general', 
    'SUWP': 'OLD Surgical Workplaces Segment', 
    'SWOM': 'OLD Surgical Workplaces OEM',
    'SWWP': 'Surgical Workplaces',
    'WPAS': 'SWP Assist Systems', 
    'WPCD': 'SWP Ceiling Devices', 
    'WPNI': 'SWP Near-Infrared Imaging', 
    'WPOL': 'SWP Operating Lights', 
    'WPOT': 'SWP Operating Tables', 
    'WPSE': 'SWP Service', 
    'WPSO': 'SWP Other', 
    'WPVA': 'SWP Modular Wall Systems',
    }

def productline_mapping(input_string, dictionary_mapping=mapping):  
    """
    Replaces words in a text based on a provided dictionary mapping.
    
    Parameters:
    text (str): The input string where words need to be replaced.
    word_mapping (dict): A dictionary where keys are words to replace, and values are their replacements.
    
    Returns:
    str: The modified text with replacements applied.
    """
    # Create a regex pattern to match whole words in the mapping
    pattern = re.compile(r'\b(' + '|'.join(re.escape(key) for key in mapping.keys()) + r')\b')

    # Replace words using the mapping
    replaced_text = pattern.sub(lambda match: mapping[match.group()], input_string)

    return replaced_text



def map_productlines_in_dataframe(df, column_name, dictionary_mapping=mapping):
    """
    Replaces words in a specified column of a DataFrame based on a provided dictionary mapping.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the data.
    column_name (str): The name of the column to apply the mapping to.
    dictionary_mapping (dict): A dictionary where keys are words to replace, and values are their replacements.

    Returns:
    pd.DataFrame: The modified DataFrame with updated values in the specified column.
    """
    # Create regex pattern to match whole words
    pattern = re.compile(r'\b(' + '|'.join(re.escape(key) for key in dictionary_mapping.keys()) + r')\b')

    # Apply the mapping to the specified column
    df[column_name] = df[column_name].astype(str).apply(
        lambda text: pattern.sub(lambda match: dictionary_mapping[match.group()], text)
    )

    return df
