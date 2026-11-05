
import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def check_website(url, timeout=10):
    """Check website availability and measure response time."""

    start_time = time.perf_counter()

    try:
        request = Request(
            url,
            headers={"User-Agent": "CloudOpsWatch/1.0"}
        )

        with urlopen(request, timeout=timeout) as response:
            status_code = response.status

        error = None

    except HTTPError as exc:
        status_code = exc.code
        error = f"HTTP error: {exc.code}"

    except (URLError, TimeoutError, OSError) as exc:
        status_code = None
        error = str(getattr(exc, "reason", exc))

    response_time = round(
        (time.perf_counter() - start_time) * 1000, 2
    )

    return {
        "url": url,
        "is_up": status_code is not None and 200 <= status_code < 400,
        "status_code": status_code,
        "response_time_ms": response_time,
        "error": error
    }


def lambda_handler(event, context):
    """AWS Lambda entry point."""

    url = os.environ["TARGET_URL"]
    result = check_website(url)

    print(json.dumps(result))

    # Send an alert only when the website is down.
    topic_arn = os.environ.get("SNS_TOPIC_ARN")

    if not result["is_up"] and topic_arn:
        import boto3

        sns = boto3.client("sns")

        sns.publish(
            TopicArn=topic_arn,
            Subject="CloudOps Watch: Website Down",
            Message=json.dumps(result, indent=2)
        )

    return result


if __name__ == "__main__":
    website = check_website("https://www.google.com")
    print(json.dumps(website, indent=2))
