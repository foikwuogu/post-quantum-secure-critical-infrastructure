import argparse
import json
import urllib.request

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--url", default="http://127.0.0.1:8001/api/benchmark")
    args = parser.parse_args()

    payload = json.dumps({"iterations": args.iterations}).encode()
    request = urllib.request.Request(
        args.url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        print(response.read().decode())

if __name__ == "__main__":
    main()
