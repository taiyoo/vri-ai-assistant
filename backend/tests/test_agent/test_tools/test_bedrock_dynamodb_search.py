import sys

sys.path.append(".")
import unittest

from app.agents.tools.bedrock_dynamodb_search import DynamoDBSearchInput, dynamodb_search_tool

class TestDynamoDBSearchTool(unittest.TestCase):
    def test_dynamodb_search(self):
        # Example patient name to search for
        name = "Matthew Smith"
        arg = DynamoDBSearchInput(name=name)
        # Python
        response = dynamodb_search_tool.run(
            tool_use_id="dummy",
            input=arg.model_dump(),
            model="claude-v3.5-sonnet-v2",
        )
        self.assertIsInstance(response, dict)
        self.assertIn("related_documents", response)
        documents = response["related_documents"]
        self.assertIsInstance(documents, list)
        if documents:
            self.assertTrue(hasattr(documents[0], "content"))
            self.assertTrue(hasattr(documents[0], "source_name"))
        print(response)
if __name__ == "__main__":
    unittest.main()