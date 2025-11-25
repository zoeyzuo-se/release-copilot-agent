from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from rc_agent.config.settings import settings


def main():
    # Load settings
    endpoint = settings.endpoint
    deployment = settings.deployment
    
    # Create Azure OpenAI client
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default"
    )
    
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        azure_ad_token_provider=token_provider,
        api_version="2024-10-21"
    )
    
    # Send a simple prompt
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "user", "content": "Hello"}
        ]
    )
    
    # Print the response
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
