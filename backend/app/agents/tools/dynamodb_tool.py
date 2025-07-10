from livekit_agent.mcp import tools
import boto3

@tools.register
def search_name_in_dynamodb(name: str) -> list[dict]:
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