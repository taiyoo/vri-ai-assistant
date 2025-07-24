from livekit.agents import (
    function_tool, 
    Agent, 
    RunContext
)
import boto3

@function_tool()
def search_name_in_dynamodb(
    context: RunContext,
    name: str
) -> list[dict]:
    """
    Search for a name in the DynamoDB table and return matching items.
    """
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("alzheimer_dataset") 

    # Scan for items where the 'PatientName' attribute contains the search term (case-insensitive)
    response = table.scan(
        FilterExpression="contains(#n, :name)",
        ExpressionAttributeNames={"#n": "PatientName"},
        ExpressionAttributeValues={":name": name},
    )
    return response.get("Items", [])

if __name__ == "__main__":
    # You can pass None for context if it's not used in your function
    results = search_name_in_dynamodb(None, "Smith")
    print("Results:", results)