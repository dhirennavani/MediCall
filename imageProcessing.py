import os
import requests
import base64

def image_to_base64(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode("utf-8")

base64_image = image_to_base64("image3.jpeg")

print("Sending request to Llama API...")
response = requests.post(
    url="https://api.llama.com/v1/chat/completions",
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ.get('LLAMA_API_KEY')}"
    },
    json={
        "model": "Llama-4-Maverick-17B-128E-Instruct-FP8",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "This is an insurance card. Extract key insurance details required to book a medical appointment. "
                            "Output should be a JSON object with only the requested fields. If a field is not visible or unclear, return `null`. "
                            "Do not infer values. Follow this schema strictly."
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "InsuranceCardExtraction",
                "description": "Extracted insurance card details required for appointment booking.",
                "schema": {
                    "type": "object",
                    "properties": {
                        "member_id": {
                            "type": "string",
                            "description": "Member ID or policy number used to identify the insured person (often labeled as ID #, Member ID, Policy #)"
                        },
                        "group_number": {
                            "type": "string",
                            "description": "Group or plan number (often labeled as Group # or Plan #)"
                        },
                        "insured_name": {
                            "type": "string",
                            "description": "Full name of the primary insured person"
                        },
                        "dependent_name": {
                            "type": "string",
                            "description": "Name of the person receiving care if different from insured (e.g., child or spouse). Might sayReturn null if not listed."
                        },
                        "insurance_company": {
                            "type": "string",
                            "description": "Name of the insurance provider (e.g., Premera Blue Cross, Aetna, Cigna)"
                        },
                        "plan_type": {
                            "type": "string",
                            "description": "Type of plan (e.g., PPO, HMO, EPO). If not clearly stated, return null."
                        },
                        "customer_service_number": {
                            "type": "string",
                            "description": "Phone number on the card for provider inquiries or customer service"
                        },
                        "rx_bin": {
                            "type": "string",
                            "description": "RX BIN number for pharmacy processing (if available)"
                        },
                        "rx_pcn": {
                            "type": "string",
                            "description": "RX PCN number for pharmacy processing (if available)"
                        }
                    },
                    "required": [
                        "member_id",
                        "insured_name",
                        "insurance_company",
                        "dependent_name"
                    ]
                }
            }
        }
    }
)

print(response.json())
