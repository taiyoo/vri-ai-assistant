import pandas as pd
import faker

# Load your dataset
df = pd.read_csv('alzheimers_disease_data.csv')

# Generate synthetic names
fake = faker.Faker()
df['PatientName'] = [fake.name() for _ in range(len(df))]

# Save the new dataset
df.to_json('alzheimer_dataset_with_names.json', orient='records', lines=True)