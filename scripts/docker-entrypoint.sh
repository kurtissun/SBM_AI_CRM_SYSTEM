#!/bin/bash
set -e

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "Database ready!"

# Run database migrations
echo "Running database setup..."
python scripts/setup_database.py

# Train models if in production and models don't exist
if [ "$ENVIRONMENT" = "production" ] && [ ! -f "models/ml_models/adaptive_clustering_v1.pkl" ]; then
    echo "Training initial models..."
    python scripts/train_models.py --customer-data data/raw/sample_membership_data.csv --generate-synthetic
fi

# Start the application
echo "Starting SBM CRM System..."
exec "$@"