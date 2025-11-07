#!/bin/bash

echo "===================================="
echo "Git Repository Setup and Push"
echo "===================================="
echo ""

cd "$(dirname "$0")"

echo "[1/6] Initializing Git repository..."
git init
if [ $? -ne 0 ]; then
    echo "Error: Failed to initialize git repository"
    exit 1
fi
echo ""

echo "[2/6] Adding files to Git..."
git add .
if [ $? -ne 0 ]; then
    echo "Error: Failed to add files"
    exit 1
fi
echo ""

echo "[3/6] Creating initial commit..."
git commit -m "Initial commit: Price comparison web application"
if [ $? -ne 0 ]; then
    echo "Error: Failed to commit"
    exit 1
fi
echo ""

echo "[4/6] Setting main branch..."
git branch -M main
if [ $? -ne 0 ]; then
    echo "Warning: Failed to rename branch to main"
fi
echo ""

echo "[5/6] Adding remote repository..."
git remote add origin https://github.com/jiappa4/find-item2.git
if [ $? -ne 0 ]; then
    echo "Warning: Remote may already exist"
    git remote set-url origin https://github.com/jiappa4/find-item2.git
fi
echo ""

echo "[6/6] Pushing to GitHub..."
echo "Please enter your GitHub credentials if prompted"
git push -u origin main
if [ $? -ne 0 ]; then
    echo ""
    echo "===================================="
    echo "Push failed! This might be because:"
    echo "1. The repository doesn't exist yet on GitHub"
    echo "2. Authentication failed"
    echo "3. Network issues"
    echo ""
    echo "Please create the repository on GitHub first:"
    echo "https://github.com/new"
    echo "Repository name: find-item2"
    echo "Then run this script again."
    echo "===================================="
    exit 1
fi

echo ""
echo "===================================="
echo "SUCCESS! Repository pushed to GitHub"
echo "===================================="
echo ""
echo "Your repository: https://github.com/jiappa4/find-item2"
echo ""
echo "To enable GitHub Pages:"
echo "1. Go to: https://github.com/jiappa4/find-item2/settings/pages"
echo "2. Under 'Source', select: GitHub Actions"
echo "3. The site will be available at: https://jiappa4.github.io/find-item2/"
echo ""
echo "Note: It may take a few minutes for the site to be deployed."
echo "===================================="
