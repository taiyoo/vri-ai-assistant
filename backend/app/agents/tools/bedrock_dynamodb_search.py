import logging
import boto3
import decimal
from pydantic import BaseModel, Field
from app.agents.tools.agent_tool import AgentTool
from app.repositories.models.custom_bot import BotModel
from app.routes.schemas.conversation import type_model_name

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class DynamoDBSearchInput(BaseModel):
    name: str = Field(description="The patient name to search for in the DynamoDB table.")

def convert_decimals(obj):
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, decimal.Decimal):
        # Convert to int if no fractional part, else float
        return int(obj) if obj % 1 == 0 else float(obj)
    else:
        return obj

def _search_name_in_dynamodb(
    tool_input: DynamoDBSearchInput, bot: BotModel | None, model: type_model_name | None
) -> list[dict]:
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("alzheimer_dataset")
    name = tool_input.name

    logger.info(f"Searching DynamoDB for patient name containing: {name}")

    response = table.scan(
        FilterExpression="contains(#n, :name)",
        ExpressionAttributeNames={"#n": "PatientName"},
        ExpressionAttributeValues={":name": name},
    )
    items = response.get("Items", [])
    items = convert_decimals(items)
    logger.info(f"Found {len(items)} matching items in DynamoDB")
    return items

bedrock_dynamodb_search_tool = AgentTool(
    name="bedrock_dynamodb_search",
    description="Search for a patient name in the DynamoDB table.",
    args_schema=DynamoDBSearchInput,
    function=_search_name_in_dynamodb,
)