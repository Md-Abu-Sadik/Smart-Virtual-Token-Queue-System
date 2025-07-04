echo "📦 Adding all files..."
git add .

echo "✍️ Enter your commit message:"
read message

git commit -m "$message"

echo "🚀 Pushing to GitHub..."
git push

echo "✅ Done!"
