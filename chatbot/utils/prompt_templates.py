# chatbot/utils/prompt_templates.py

# === Prompt Templates Used Across Widgets ===

ARCHITECTURE_PROMPT = """
Generate an AWS architecture using AWS best practices. Return valid draw.io XML in ```xml``` block.
"""

CDK_GENERATION_PROMPT = """
Create an AWS CDK (TypeScript) stack for:
- S3 Bucket: devgenius-docs-bucket
- 3 Lambdas: textract_ingestion_handler, check_textract_status, notify_success
- A Step Function coordinating the flow
- A DynamoDB table and SNS topic
"""

CLOUDFORMATION_GENERATION_PROMPT = """
Generate CloudFormation YAML for a Step Function that invokes 3 Lambda tasks and sends an SNS notification.
"""

DOCUMENTATION_GENERATION_PROMPT = """
Write technical documentation for this solution including purpose, components, IAM roles, and cost notes.
"""

COST_ESTIMATION_PROMPT = """
Estimate AWS monthly cost for:
- 10GB S3 storage
- 1M Lambda invokes
- 100K StepFn execs
- 10K/5K DynamoDB R/W
- 50K SNS messages
Return a Markdown table.
"""

DRAWIO_GENERATION_PROMPT = """
Return draw.io XML for the above architecture with professional layout. Must start with <mxGraphModel>.
"""
