# build_files.sh
echo "Building project..."

# Install python dependencies
python3.9 -m pip install -r requirements.txt

# Install node dependencies (for Tailwind)
npm install
npm run build:css

# Collect static files
# Ensure the collected static files are placed in 'staticfiles'
echo "Collecting static files..."
python3.9 manage.py collectstatic --noinput --clear

echo "Build Process Completed!"
