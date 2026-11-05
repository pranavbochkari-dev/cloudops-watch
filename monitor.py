
import urllib.request
import urllib.error
import json
import os
import time


def check_website(url, timeout=10):
    start = time.time()

    try:
        response = urllib.request.urlopen(url, timeout=timeout)
        status_code = response.getcode()
        response.close()

        return {
            "url": url,
            "is_up": True,
            "status_code": status_code,
            "response_time_ms": round((time.time() - start) * 1000, 2),
            "error": None
        }

    except Exception as error:
        return {
            "url": url,
            "is_up": False,
            "status_code": getattr(error, "code", None),
            "response_time_ms": round((time.time() - start) * 1000, 2),
            "error": str(error)
        }


def lambda_handler(event, context):
    url = os.environ.get("TARGET_URL", "https://www.google.com")
    sns_topic = os.environ.get("SNS_TOPIC_ARN")

    result = check_website(url)
    print(json.dumps(result))

    if not result["is_up"] and sns_topic:
        import boto3
        sns = boto3.client("sns")
        sns.publish(
            TopicArn=sns_topic,
            Subject="CloudOps Watch Alert",
            Message=json.dumps(result, indent=2)
        )

    return result


if __name__ == "__main__":
    print(json.dumps(check_website("https://www.google.com"), indent=2))
