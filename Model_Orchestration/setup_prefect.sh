set -e

echo "Setting up Prefect."

echo "Create working queue."
prefect work-queue create work_queue_3 || true

echo "Creating storage. (interactive)"
printf "3\n/tmp/store\n\nstoreName\ny\n" | prefect storage create