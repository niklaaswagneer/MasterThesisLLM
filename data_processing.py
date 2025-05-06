import pandas as pd
import numpy as np

class DataHandler:
    """Class for handling preprocessing."""

    def __init__(self, file_path):
        """Loads the dataset and cleans it upon initialization."""
        self.df = pd.read_csv(file_path, sep=';')
        self.cper_total = self.df['[Value_cper]'].sum()
        self.mper_total = self.df['[Value_mper]'].sum()
        self._clean_data()

    def _clean_data(self):
        """Private method: Cleans the dataset by removing unnecessary columns and filling missing values."""
        self.df.drop(columns=['[v_Value_cper_FormatString]', '[v_Value_mper_FormatString]', '[Book_to_Bill_mper]',
                              '[Value___Share_mper]', '[Value___Share_diff]'], errors='ignore', inplace=True)
        self.df.fillna(0, inplace=True)
        self.df['[Difference]'] = self.df['[Value_mper]'] - self.df['[Value_cper]']
        self.df['[Delta]'] = (1 - self.df['[Difference]'] / self.df['[Value_cper]']) * 100
        self.df = self.df.drop(columns=['[Value_cper]', '[Value_mper]'], errors='ignore')

    def get_dataset(self    ):
        return self.df

    def get_cper_total(self):
        return self.cper_total

    def get_mper_total(self):
        return self.mper_total

    def filter_mper_cper(self):
        return self.df.drop(columns=['[Value_mper]', '[Value_cper]'], errors='ignore')

    def filter_by_business_area(self, business_code):
        return self.df[self.df['DimProduct[Business Area Code]'] == business_code]

    def filter_by_product_area(self, product_area):
        return self.df[self.df['DimProduct[Product Area Code]'] == product_area]

    def get_unique_business_areas(self):
        return self.df['DimProduct[Business Area Code]'].unique()

    def drivers_per_product_area(self, business_area):
        """Returns a DataFrame with two columns: 'Product Area' and 'Total Difference'."""
        
        filtered_df = self.filter_by_business_area(business_area)
        
    
        if "DimProduct[Product Area Code]" in filtered_df.columns:
            
          # Group by Product Area and sum the differences
            df_grouped = (
                filtered_df.groupby("DimProduct[Product Area Code]")['[Difference]']
                .sum()
                .reset_index() 
                .rename(columns={"DimProduct[Product Area Code]": "Product Area", "[Difference]": "Total Difference"})  
                .sort_values(by="Total Difference", ascending=False)  
            )
            
            return df_grouped  
        
        return pd.DataFrame(columns=["Product Area", "Total Difference"]) 

    def drivers_per_product_area_regions(self, business_area):
        """Returns a DataFrame with three columns: 'Product Area', 'Region', and 'Total Difference'."""
        
        # Filter the dataset for the given business area
        filtered_df = self.filter_by_business_area(business_area)
        
        # Check if required columns exist
        required_columns = ["DimProduct[Product Area Code]", "DimMarketGeo[Region Label Geo]", "[Difference]"]
        if all(col in filtered_df.columns for col in required_columns):
            
            # Group by Product Area and Region, then sum the differences
            df_grouped = (
                filtered_df.groupby(["DimProduct[Product Area Code]", "DimMarketGeo[Region Label Geo]"])['[Difference]']
                .sum()
                .reset_index() 
                .rename(columns={
                    "DimProduct[Product Area Code]": "Product Area",
                    "DimMarketGeo[Region Label Geo]": "Region",
                    "[Difference]": "Total Difference"
                })  
                .sort_values(by="Total Difference", ascending=False) 
            )
            
            return df_grouped  
        
        return pd.DataFrame(columns=["Product Area", "Region", "Total Difference"])  
    
    def region_substitute(self, business_area):

        df = self.filter_by_business_area(business_area).copy()

        # Get relevant columns
        region_col = 'DimMarketGeo[Region Label Geo]'
        country_code_col = 'DimMarketGeo[Country Code Geo]'

        df[region_col] = df.apply(
        lambda row: 'China' if str(row[country_code_col]).strip().lower() in ['china', 'cn']
        else row[region_col],
        axis=1
    )
        df[region_col] = df.apply(
        lambda row: 'US' if str(row[country_code_col]).strip().lower() in ['USA', 'us', 'US']
        else row[region_col],
        axis=1
    )

        return df


    def drivers_in_business_area_region_relative(self, business_area):
        """
        Returns a DataFrame with 'Product Line', 'Region', 'Total Difference', and 
        'Business Area Contribution %' for a specific Business Area, without filtering on Product Area.
        """

        # Filter the dataset for the given business area
        filtered_df = self.region_substitute(business_area)

        # Check if required columns exist
        required_columns = ["DimProduct[Product Line Code]", "DimMarketGeo[Region Label Geo]", "[Difference]"]
        if all(col in filtered_df.columns for col in required_columns):

            # Group by Product Line and Region, then sum the differences
            df_grouped = (
                filtered_df.groupby(["DimProduct[Product Line Code]", "DimMarketGeo[Region Label Geo]"])['[Difference]']
                .sum()
                .reset_index()
                .rename(columns={
                    "DimProduct[Product Line Code]": "Product Line",
                    "DimMarketGeo[Region Label Geo]": "Region",
                    "[Difference]": "Total Difference"
                })
                .sort_values(by="Product Line", ascending=False)
            )

            
            total_business_area_difference = df_grouped["Total Difference"].sum()

            # Compute the relative contribution of each product line to the business area
            if total_business_area_difference < 0:
                df_grouped["Business Area Contribution %"] = (
                    df_grouped["Total Difference"] / total_business_area_difference
                ) * -100
            else:
                df_grouped["Business Area Contribution %"] = (
                    df_grouped["Total Difference"] / total_business_area_difference
                ) * 100
    
            threshold_major = df_grouped["Total Difference"].abs().quantile(0.75)  # Top 25% as "Major"

            #Categorize changes into Major/Minor Increase/Decrease
            df_grouped["Change Type"] = df_grouped["Total Difference"].apply(lambda x: 
                "Major Increase" if x > threshold_major else 
                "Minor Increase" if x > 0 else 
                "Major Decrease" if x < -threshold_major else 
                "Minor Decrease"
            )

            return df_grouped

        return pd.DataFrame(columns=["Product Line", "Region", "Total Difference", "Business Area Contribution %"])

    def drivers_in_business_area_region_relative2(self, business_area):
        """
        Returns a DataFrame with 'Product Line', 'Region', 'Total Difference', and 
        'Business Area Contribution %' for a specific Business Area, without filtering on Product Area.
        """

        # Filter the dataset for the given business area
        filtered_df = self.region_substitute(business_area)

        # Check if required columns exist
        required_columns = ["DimProduct[Product Line Code]", "DimMarketGeo[Region Label Geo]", "[Difference]"]
        if all(col in filtered_df.columns for col in required_columns):

            # Group by Product Line and Region, then sum the differences
            df_grouped = (
                filtered_df.groupby(["DimProduct[Product Line Code]", "DimMarketGeo[Region Label Geo]"])['[Difference]']
                .sum()
                .reset_index()
                .rename(columns={
                    "DimProduct[Product Line Code]": "Product Line",
                    "DimMarketGeo[Region Label Geo]": "Region",
                    "[Difference]": "Total Difference"
                })
                .sort_values(by="Product Line", ascending=False)
            )

            # Calculate total impact within the business area
            total_business_area_difference = df_grouped["Total Difference"].sum()

            # Compute the relative contribution of each product line to the business area
            if total_business_area_difference < 0:
                df_grouped["Business Area Contribution %"] = (
                    df_grouped["Total Difference"] / total_business_area_difference
                ) * -100
            else:
                df_grouped["Business Area Contribution %"] = (
                    df_grouped["Total Difference"] / total_business_area_difference
                ) * 100

        return df_grouped


    # Go into specific productarea and picks up their productlines 
    def drivers_in_product_area_region(self, business_area, product_area):
        """Returns a DataFrame with 'Product Line', 'Region', and 'Total Difference' 
        for a specific Business Area and Product Area."""
        
        # Filter the dataset for the given business area
        filtered_df = self.filter_by_business_area(business_area)
        
        # Further filter by product area
        filtered_df = filtered_df[filtered_df["DimProduct[Product Area Code]"] == product_area]
        
        # Check if required columns exist
        required_columns = ["DimProduct[Product Line Code]", "DimMarketGeo[Region Label Geo]", "[Difference]"]
        if all(col in filtered_df.columns for col in required_columns):
            
            # Group by Product Line and Region, then sum the differences
            df_grouped = (
                filtered_df.groupby(["DimProduct[Product Line Code]", "DimMarketGeo[Region Label Geo]"])['[Difference]']
                .sum()
                .reset_index()  
                .rename(columns={
                    "DimProduct[Product Line Code]": "Product Line",
                    "DimMarketGeo[Region Label Geo]": "Region",
                    "[Difference]": "Total Difference"
                })  
                .sort_values(by="Total Difference", ascending=False) 
            )
            
            return df_grouped  
        
        return pd.DataFrame(columns=["Product Line", "Region", "Total Difference"])  


    def drivers_in_product_area_region_relative(self, business_area, product_area):
        """Returns a DataFrame with 'Product Line', 'Region', 'Total Difference', and 'Product Area Contribution %' 
        for a specific Business Area and Product Area."""
        
        
        filtered_df = self.region_substitute(business_area)
        
        # Further filter by product area
        filtered_df = filtered_df[filtered_df["DimProduct[Product Area Code]"] == product_area]
        
        # Check if required columns exist
        required_columns = ["DimProduct[Product Line Code]", "DimMarketGeo[Region Label Geo]", "[Difference]"]
        if all(col in filtered_df.columns for col in required_columns):
            
            # Group by Product Line and Region, then sum the differences
            df_grouped = (
                filtered_df.groupby(["DimProduct[Product Line Code]", "DimMarketGeo[Region Label Geo]"])['[Difference]']
                .sum()
                .reset_index()  
                .rename(columns={
                    "DimProduct[Product Line Code]": "Product Line",
                    "DimMarketGeo[Region Label Geo]": "Region",
                    "[Difference]": "Total Difference"
                })  
                .sort_values(by="Product Line", ascending=False) 
            )
            
            # Calculate total impact within the product area
            total_product_area_difference = df_grouped["Total Difference"].sum()
            # Compute the relative contribution of each product line to the product area
            if total_product_area_difference < 0: # negative difference check
                df_grouped["Product Area Contribution %"] = (df_grouped["Total Difference"] / total_product_area_difference) * (-100) 
            else:
                df_grouped["Product Area Contribution %"] = (df_grouped["Total Difference"] / total_product_area_difference) * 100

            return df_grouped  
        
        return pd.DataFrame(columns=["Product Line", "Region", "Total Difference", "Product Area Contribution %"])  

    def preprocess_orderintake_by_product_area(self, business_area, product_area):
        """
        Preprocesses order intake data for a specific business area and product area.
        - Identifies major increases and decreases based on relative impact.
        - Detects product lines with consistent trends across multiple regions.
        """

        df = self.drivers_in_product_area_region_relative(business_area, product_area)
        
        if df.empty:
            return df  

        #Compute thresholds for major/minor changes
        threshold_major = df["Total Difference"].abs().quantile(0.75)  # Top 25% as "Major"

        #Categorize changes into Major/Minor Increase/Decrease
        df["Change Type"] = df["Total Difference"].apply(lambda x: 
            "Major Increase" if x > threshold_major else 
            "Minor Increase" if x > 0 else 
            "Major Decrease" if x < -threshold_major else 
            "Minor Decrease"
        )
        """
        # Step 4: Detect trends across multiple regions
        trends = df.groupby("Product Line")["Change Type"].apply(lambda x: 
            "Consistently Decreasing" if all("Decrease" in val for val in x) else 
            "Consistently Increasing" if all("Increase" in val for val in x) else 
            "Mixed Trend"
        ).reset_index()

        # Step 5: Merge trend data back into the dataset
        df = df.merge(trends, on="Product Line", how="left")
        """

        return df


    def get_largest_driver(self):
        """Finds the product area with the largest impact."""
        drivers = self.drivers_per_product_area()
        return drivers.idxmax() if isinstance(drivers, pd.Series) else "No data available"


    def transform_data(self, columns_to_anonymize, scaling_range=(4,10)):
        scaling_factors = {}

        for col in columns_to_anonymize:
            if col in self.df.columns:
                factor = np.random.uniform(*scaling_range)
                print(factor)
                self.df[col] = self.df[col] * factor + factor * self.df[col]
                scaling_factors[col] = factor
            else:
                print(f"Warning: Column '{col}' not found in the dataset.")

        for col, factor in scaling_factors.items():
           print(f"  {col}: {factor:.3f}")

        return 
