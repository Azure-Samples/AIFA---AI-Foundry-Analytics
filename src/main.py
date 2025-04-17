import polars as pl
import json
import os
import zstandard as zstd

# Function to download and decompress zstd files if needed
def download_and_decompress(dataset_path, output_path):
    if not os.path.exists(output_path):
        # Here we would use huggingface_hub to download if needed
        # For now, assuming the file is already downloaded
        with open(dataset_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                dctx = zstd.ZstdDecompressor()
                reader = dctx.stream_reader(f_in)
                while True:
                    chunk = reader.read(16384)
                    if not chunk:
                        break
                    f_out.write(chunk)

# Function to transform the data to the desired format
def transform_data(df):
    # Create a new dataframe with the desired format
    transformed_data = []
    context = """You are an SQL expert that assists users with crafting **Data Query Language (DQL)** queries specifically for data retrieval purposes. You should not craft any other type of SQL query, such as:

- **DDL** (Data Definition Language)
- **DML** (Data Manipulation Language)
- **DCL** (Data Control Language)
- **TCL** (Transaction Control Language)

Ensure your responses strictly adhere to the following:

---

# Steps

1. **Understand the User's Dataset and Goal**:
   - Request clarification about the dataset structure (e.g., table names, column names, data types, and relationships) if not provided.
   - Identify the purpose of the query (e.g., filtering, joining tables, grouping data).

2. **Craft a DQL Query**:
   - Write a functional, efficient **SELECT** query to retrieve the requested data.
   - Use appropriate clauses (e.g., `WHERE`, `GROUP BY`, `ORDER BY`) to fulfill the user's requirements.

3. **Provide Annotations (Optional)**:
   - If the query logic is complex, add concise annotations or comments explaining the logic or structure.

4. **Avoid Generating Prohibited Query Types**:
   - If the user's request suggests creating or altering tables, modifying data, or changing database configurations, clarify your restriction and guide the user to reframe their request as a data query.

---

# Output Format

- Queries must always be output as plain text SQL syntax (do not wrap in code blocks) unless explicitly requested otherwise.
- Annotate complex queries with comments for clarity if needed.

---

# Example

**User Input**:  
"I want to find the total sales amount for each product category from a `sales` table, grouped by category, and sorted in descending order."

**System Output**:  
```sql
SELECT 
    category, 
    SUM(sales_amount) AS total_sales 
FROM 
    sales 
GROUP BY 
    category 
ORDER BY 
    total_sales DESC;
```

*Annotation*:  
- The `SUM` function calculates total sales for each category.  
- The `GROUP BY category` groups the rows by product category.  
- The `ORDER BY total_sales DESC` ensures the results are sorted by total sales in descending order.

---

# Notes

- Limit responses to **DQL**-only queries using `SELECT`.
- For ambiguous or underspecified tasks, request clarification from the user about the dataset or goal.
- Focus strictly on data **retrieval** and not on **manipulation**, schema modification, or database control tasks."""
    # Iterate over the dataframe rows
    for row in df.iter_rows(named=True):
        query = row['query']
        sql = row['sql']
        
        # Create the messages structure with the correct mapping
        messages = [
            {"role": "system", "content": context},
            {"role": "user", "content": query},  # Context goes into user's message
            {"role": "assistant", "content": sql}
        ]
        
        # Create the final record
        record = {"messages": messages}
        transformed_data.append(record)
    
    return transformed_data

# Main processing function
def process_data(input_path, output_path):
    # Read the data
    df = pl.read_ndjson(input_path)
    
    # Transform the data
    transformed_data = transform_data(df)
    
    # Write the transformed data to JSONL
    with open(output_path, 'w') as f:
        for record in transformed_data:
            f.write(json.dumps(record) + '\n')

# Main execution
def main():
    # Define paths
    data_dir = './assets/data'
    output_dir = './assets/output' # Keep the base output dir
    
    # Create base output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Define file paths
    # Login using e.g. `huggingface-cli login` to access this dataset
    splits = {'train': 'train.jsonl.zst', 'test': 'test.jsonl.zst'}
    hf_base_path = 'hf://datasets/agentlans/sql-text-collection/'
    
    # Define max chunk size (e.g., 190MB to be safe under 200MB)
    MAX_CHUNK_SIZE = 190 * 1024 * 1024  # bytes
    
    for split_name, split_file in splits.items():
        # Define split-specific output directory
        split_output_dir = os.path.join(output_dir, split_name)
        os.makedirs(split_output_dir, exist_ok=True) # Create train/test subdir

        # Define base output path pattern within the split-specific directory
        output_base_path = os.path.join(split_output_dir, f"{split_name}_transformed")
        
        try:
            # In a real scenario, you would use:
            df = pl.read_ndjson(f'hf://datasets/agentlans/sql-text-collection/{split_file}')
            # For local testing, you might use:
            # df = pl.read_ndjson(input_jsonl_path) # Assuming input_jsonl_path is defined if needed
            
            # Transform data
            transformed_data = transform_data(df)
            
            # Write data in chunks
            chunk_index = 1
            current_file_size = 0
            current_file = None
            output_chunk_path = None

            for record in transformed_data:
                json_record = json.dumps(record) + '\n'
                record_size = len(json_record.encode('utf-8'))

                # Check if we need to start a new chunk file
                if current_file is None or (current_file_size + record_size > MAX_CHUNK_SIZE and current_file_size > 0):
                    if current_file:
                        current_file.close()
                        print(f"Closed chunk: {output_chunk_path} with size {current_file_size / (1024*1024):.2f} MB")
                    
                    # Use the updated output_base_path which includes the split subdir
                    output_chunk_path = f"{output_base_path}_chunk_{chunk_index}.jsonl" 
                    current_file = open(output_chunk_path, 'w', encoding='utf-8')
                    current_file_size = 0
                    chunk_index += 1
                    print(f"Starting new chunk: {output_chunk_path}")

                # Write the record to the current chunk file
                current_file.write(json_record)
                current_file_size += record_size

            # Close the last opened file
            if current_file:
                current_file.close()
                print(f"Closed final chunk: {output_chunk_path} with size {current_file_size / (1024*1024):.2f} MB")
                    
            # Update the success message to reflect the new path structure
            print(f"Successfully processed {split_name} data and saved to chunks in {split_output_dir}")
            
        except Exception as e:
            print(f"Error processing {split_name} data: {e}")
            # Ensure file is closed in case of error during writing
            if current_file and not current_file.closed:
                current_file.close()

if __name__ == "__main__":
    main()


