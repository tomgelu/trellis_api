# client.py
import requests
import argparse
import os

def process_image(image_path, server_url="http://localhost:5000"):
    """Send an image to the TRELLIS service for processing"""
    
    with open(image_path, 'rb') as f:
        files = {'image': f}
        response = requests.post(f"{server_url}/process", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Processing successful!")
        print(f"Request ID: {result['request_id']}")
        print("\nOutput files:")
        for file_type, path in result['output_files'].items():
            print(f"- {file_type}: {path}")
    else:
        print(f"Error: {response.json().get('error', 'Unknown error')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send image to TRELLIS service')
    parser.add_argument('image_path', help='Path to the input image')
    parser.add_argument('--server', default='http://localhost:5000', 
                      help='TRELLIS service URL')
    
    args = parser.parse_args()
    process_image(args.image_path, args.server)
