#!/bin/bash

# Fixed paths
INPUT_IMAGE="/mnt/d/Code/TRELLIS/input/cherry.webp"
OUTPUT_DIR="/mnt/d/Code/TRELLIS/output"
IMAGE_NAME="trellis-processor"

echo "=== TRELLIS Image Processing Setup ==="
echo "Input image: $INPUT_IMAGE"
echo "Output directory: $OUTPUT_DIR"

# Check if input file exists
if [ ! -f "$INPUT_IMAGE" ]; then
    echo "Error: Input image '$INPUT_IMAGE' not found"
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Build Docker image if it doesn't exist
if ! docker images | grep -q "^${IMAGE_NAME} "; then
    echo "=== Building Docker image (this may take a while) ==="
    docker build -t ${IMAGE_NAME} .
fi

echo "=== Starting TRELLIS processing ==="
# Run docker container with arguments
docker run --rm -it --gpus all \
    -v "$INPUT_IMAGE:/workspace/TRELLIS/input/image.webp:ro" \
    -v "$OUTPUT_DIR:/workspace/TRELLIS/output:rw" \
    ${IMAGE_NAME}
          
# Check if the container ran successfully
if [ $? -eq 0 ]; then
    echo "=== Processing complete! ==="
    echo "Check output files in: $OUTPUT_DIR"
else
    echo "=== Error: Processing failed ==="
    echo "Check the error messages above for details"
fi