import pandas as pd

class DataHandler:
    """Class for handling order intake analysis and preprocessing."""

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

    def get_cper_total(self):
        return self.cper_total

    def get_mper_total(self):
        return self.mper_total

    def filter_mper_cper(self):
        """Returns a DataFrame with '[Value_mper]' and '[Value_cper]' removed."""
        return self.df.drop(columns=['[Value_mper]', '[Value_cper]'], errors='ignore')

    def filter_by_business_area(self, business_code):
        """Returns a DataFrame filtered by a specific business area code."""
        return self.df[self.df['DimProduct[Business Area Code]'] == business_code]

    def filter_by_product_area(self, product_area):
        """Returns a DataFrame filtered by a specific product area."""
        return self.df[self.df['DimProduct[Product Area Code]'] == product_area]

    def get_unique_business_areas(self):
        """Returns a list of unique business areas in the dataset."""
        return self.df['DimProduct[Business Area Code]'].unique()

    def drivers_per_product_area(self, business_area):
        """Returns a DataFrame with two columns: 'Product Area' and 'Total Difference'."""
        
        # Step 1: Filter by business area
        filtered_df = self.filter_by_business_area(business_area)
        
        # Step 2: Check if the required column exists
        if "DimProduct[Product Area Code]" in filtered_df.columns:
            
            # Step 3: Group by Product Area and sum the differences
            df_grouped = (
                filtered_df.groupby("DimProduct[Product Area Code]")['[Difference]']
                .sum()
                .reset_index()  #Convert Series to DataFrame
                .rename(columns={"DimProduct[Product Area Code]": "Product Area", "[Difference]": "Total Difference"})  # ✅ Rename for clarity
                .sort_values(by="Total Difference", ascending=False)  #Sort for readability
            )
            
            return df_grouped  #Now a DataFrame with two columns!
        
        return pd.DataFrame(columns=["Product Area", "Total Difference"])  # Return an empty DataFrame if no data is found

    def drivers_per_product_area_region(self, business_area):
        """Returns a DataFrame with three columns: 'Product Area', 'Region', and 'Total Difference'."""
        
        # Step 1: Filter the dataset for the given business area
        filtered_df = self.filter_by_business_area(business_area)
        
        # Step 2: Check if required columns exist
        required_columns = ["DimProduct[Product Area Code]", "DimMarketGeo[Region Label Geo]", "[Difference]"]
        if all(col in filtered_df.columns for col in required_columns):
            
            # Step 3: Group by Product Area and Region, then sum the differences
            df_grouped = (
                filtered_df.groupby(["DimProduct[Product Area Code]", "DimMarketGeo[Region Label Geo]"])['[Difference]']
                .sum()
                .reset_index()  #Convert Series to DataFrame
                .rename(columns={
                    "DimProduct[Product Area Code]": "Product Area",
                    "DimMarketGeo[Region Label Geo]": "Region",
                    "[Difference]": "Total Difference"
                })  #Rename for clarity
                .sort_values(by="Total Difference", ascending=False)  #Sort for readability
            )
            
            return df_grouped  # Now a DataFrame with three columns!
        
        return pd.DataFrame(columns=["Product Area", "Region", "Total Difference"])  # Return empty DataFrame if columns are missing

    def drivers_per_product_line_region(self, business_area):
        """Returns a DataFrame with three columns: 'Product Line', 'Region', and 'Total Difference'."""
        
        # Step 1: Filter the dataset for the given business area
        filtered_df = self.filter_by_business_area(business_area)
        
        # Step 2: Check if required columns exist
        required_columns = ["DimProduct[Product Line Code]", "DimMarketGeo[Region Label Geo]", "[Difference]"]
        if all(col in filtered_df.columns for col in required_columns):
            
            # Step 3: Group by Product Line and Region, then sum the differences
            df_grouped = (
                filtered_df.groupby(["DimProduct[Product Line Code]", "DimMarketGeo[Region Label Geo]"])['[Difference]']
                .sum()
                .reset_index()  #  Convert Series to DataFrame
                .rename(columns={
                    "DimProduct[Product Line Code]": "Product Line",
                    "DimMarketGeo[Region Label Geo]": "Region",
                    "[Difference]": "Total Difference"
                })  # Rename for clarity
                .sort_values(by="Total Difference", ascending=False)  # Sort for readability
            )
            
            return df_grouped  
        
        return pd.DataFrame(columns=["Product Line", "Region", "Total Difference"])  # Return empty DataFrame if columns are missing

    def drivers_in_product_area(self, business_area, product_area):
        """Returns a DataFrame with 'Product Line' and 'Total Difference' 
        for a specific Business Area and Product Area, without considering the region."""
        
        # Step 1: Filter the dataset for the given business area
        filtered_df = self.filter_by_business_area(business_area)
        
        # Step 2: Further filter by product area
        filtered_df = filtered_df[filtered_df["DimProduct[Product Area Code]"] == product_area]
        
        # Step 3: Check if required columns exist
        required_columns = ["DimProduct[Product Line Code]", "[Difference]"]
        if all(col in filtered_df.columns for col in required_columns):
            
            # Step 4: Group only by Product Line, then sum the differences
            df_grouped = (
                filtered_df.groupby("DimProduct[Product Line Code]")['[Difference]']
                .sum()
                .reset_index()  # Convert Series to DataFrame
                .rename(columns={
                    "DimProduct[Product Line Code]": "Product Line",
                    "[Difference]": "Total Difference"
                })  # Rename for clarity
                .sort_values(by="Total Difference", ascending=False)  #Sort for readability
            )
            
            return df_grouped  # Now a DataFrame with two columns!
        
        return pd.DataFrame(columns=["Product Line", "Total Difference"])  # Return empty DataFrame if columns are missing



    # Go into specific productarea and picks up their productlines 
    def drivers_in_product_area_region(self, business_area, product_area):
        """Returns a DataFrame with 'Product Line', 'Region', and 'Total Difference' 
        for a specific Business Area and Product Area."""
        
        # Step 1: Filter the dataset for the given business area
        filtered_df = self.filter_by_business_area(business_area)
        
        # Step 2: Further filter by product area
        filtered_df = filtered_df[filtered_df["DimProduct[Product Area Code]"] == product_area]
        
        # Step 3: Check if required columns exist
        required_columns = ["DimProduct[Product Line Code]", "DimMarketGeo[Region Label Geo]", "[Difference]"]
        if all(col in filtered_df.columns for col in required_columns):
            
            # Step 4: Group by Product Line and Region, then sum the differences
            df_grouped = (
                filtered_df.groupby(["DimProduct[Product Line Code]", "DimMarketGeo[Region Label Geo]"])['[Difference]']
                .sum()
                .reset_index()  # ✅ Convert Series to DataFrame
                .rename(columns={
                    "DimProduct[Product Line Code]": "Product Line",
                    "DimMarketGeo[Region Label Geo]": "Region",
                    "[Difference]": "Total Difference"
                })  # ✅ Rename for clarity
                .sort_values(by="Total Difference", ascending=False)  # ✅ Sort for readability
            )
            
            return df_grouped  # ✅ Now a DataFrame with three columns!
        
        return pd.DataFrame(columns=["Product Line", "Region", "Total Difference"])  # Return empty DataFrame if columns are missing


    def drivers_in_product_area_region_relative(self, business_area, product_area):
        """Returns a DataFrame with 'Product Line', 'Region', 'Total Difference', and 'Product Area Contribution %' 
        for a specific Business Area and Product Area."""
        
        # Step 1: Filter the dataset for the given business area
        filtered_df = self.filter_by_business_area(business_area)
        
        # Step 2: Further filter by product area
        filtered_df = filtered_df[filtered_df["DimProduct[Product Area Code]"] == product_area]
        
        # Step 3: Check if required columns exist
        required_columns = ["DimProduct[Product Line Code]", "DimMarketGeo[Region Label Geo]", "[Difference]"]
        if all(col in filtered_df.columns for col in required_columns):
            
            # Step 4: Group by Product Line and Region, then sum the differences
            df_grouped = (
                filtered_df.groupby(["DimProduct[Product Line Code]", "DimMarketGeo[Region Label Geo]"])['[Difference]']
                .sum()
                .reset_index()  # ✅ Convert Series to DataFrame
                .rename(columns={
                    "DimProduct[Product Line Code]": "Product Line",
                    "DimMarketGeo[Region Label Geo]": "Region",
                    "[Difference]": "Total Difference"
                })  # ✅ Rename for clarity
                .sort_values(by="Total Difference", ascending=False)  # ✅ Sort for readability
            )
            
            # Step 5: Calculate total impact within the product area
            total_product_area_difference = df_grouped["Total Difference"].sum()
            # Step 6: Compute the relative contribution of each product line to the product area
            if total_product_area_difference < 0: # in the case of a negative difference
                df_grouped["Product Area Contribution %"] = (df_grouped["Total Difference"] / total_product_area_difference) * (-100) 
            else:
                df_grouped["Product Area Contribution %"] = (df_grouped["Total Difference"] / total_product_area_difference) * 100

            return df_grouped  # ✅ Returns a DataFrame with the new column!
        
        return pd.DataFrame(columns=["Product Line", "Region", "Total Difference", "Product Area Contribution %"])  # ✅ Empty DataFrame with correct columns


    def get_largest_driver(self):
        """Finds the product area with the largest impact."""
        drivers = self.drivers_per_product_area()
        return drivers.idxmax() if isinstance(drivers, pd.Series) else "No data available"


file_path = r"C:\Users\nikla\OneDrive\Skrivbord\OPIS020 - Order intake, external QTD 2411 vs 2311_v2.csv"

data = DataHandler(file_path)

