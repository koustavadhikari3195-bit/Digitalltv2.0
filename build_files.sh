# build_files.sh
echo "Building project..."

# Update pip
python3 -m pip install --upgrade pip

# Install python dependencies using standard python3
python3 -m pip install -r requirements.txt

# Install node dependencies (for Tailwind)
npm install
npm run build:css

# Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear

echo "Build Process Completed!"
