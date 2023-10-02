import gcsfs
import pandas as pd
import os
counter = 1
def main(event, context):
    global counter
    data = event
    bucket = data["bucket"]
    name = data["name"]
    metageneration = data["metageneration"]
    timeCreated = data["timeCreated"]
    updated = data["updated"]
    
    if name.startswith("Staging"):
        file_path = f"gs://{bucket}/{name}"
        print(f"Processing file: {name}.")
        print(f"Bucket {bucket}")
        print(f"File Path: {file_path}.")
        
        fs = gcsfs.GCSFileSystem(project='phrasal-marker-400322')
        with fs.open(file_path, 'rb') as f:
            df = pd.read_csv(f)
        
        # Add record numbers to the rows
        df['record_number'] = range(1, len(df) + 1)
        # Deduplicate the records in the original file
        df.drop_duplicates(inplace=True)
        # Group the file into 5 records each and then start processing
        for i in range(0, len(df), 5):
            chunk = df[i:i+5]
            # Construct the splitted file name
            splitted_filename = f"{os.path.splitext(name)[0].split('/')[1]}_{timeCreated}_{counter}.csv"
            # Increment the counter
            counter += 1
            print(splitted_filename)
            with fs.open(f'gs://{bucket}/Processing/{splitted_filename}', 'wb') as f:
                chunk.to_csv(f, index=False)

        # Delete the file from Staging
        fs.delete(file_path)
