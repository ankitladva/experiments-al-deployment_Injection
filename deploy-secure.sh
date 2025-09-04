#!/bin/bash

# Secure Deployment Script for KYC Backend
# This script helps set up a secure environment with proper API keys

echo "🔐 Setting up secure KYC Backend deployment..."

# Generate a secure random API key
SECURE_API_KEY=$(openssl rand -hex 32)
echo "Generated secure API key: $SECURE_API_KEY"

# Create backend .env file
cat > .env << EOF
# Backend Environment Configuration
API_KEY=$SECURE_API_KEY

# S3 Configuration (if using S3)
S3_BUCKET_NAME=
S3_PREFIX=
AWS_REGION=

# Other configurations
PORT=8000
HOST=0.0.0.0
EOF

echo "✅ Created .env file with secure API key"

# Create frontend .env.local file
cat > face-verification-ui/.env.local << EOF
# Frontend Environment Configuration
VITE_API_KEY=$SECURE_API_KEY
VITE_BACKEND_URL=https://kyc-backend-7f7c.onrender.com
EOF

echo "✅ Created frontend .env.local file"

# Update docker-compose.yml with environment variables
if [ -f "docker-compose.yml" ]; then
    echo "📝 Updating docker-compose.yml with environment variables..."
    # This will be done manually as docker-compose.yml needs to be updated
    echo "⚠️  Please update docker-compose.yml to include:"
    echo "   environment:"
    echo "     - API_KEY=$SECURE_API_KEY"
fi

echo ""
echo "🚀 Deployment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Deploy the backend with the new .env file"
echo "2. Update your frontend deployment with the new .env.local file"
echo "3. Test the connection with the new API key"
echo ""
echo "🔑 Your secure API key is: $SECURE_API_KEY"
echo "   Keep this key secure and don't share it publicly!"
echo ""
echo "📚 For production deployment:"
echo "   - Use environment variables in your hosting platform"
echo "   - Never commit .env files to version control"
echo "   - Rotate API keys regularly"
echo ""
echo "🔒 SECURITY NOTE: The system will now FAIL to start without a proper API key."
echo "   This ensures your backend is never accidentally deployed insecurely."
