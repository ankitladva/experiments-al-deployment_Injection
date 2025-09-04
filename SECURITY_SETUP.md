# 🔐 KYC Backend Security Setup

This document explains how to secure your KYC backend API to prevent unauthorized access.

## 🚨 Current Security Status

Your backend API at `https://kyc-backend-7f7c.onrender.com` is currently **UNSECURED** and accessible to anyone on the internet.

## 🛡️ Security Implementation

### 1. API Key Authentication

We've implemented API key authentication using the `X-API-Key` header. This is a simple but effective way to secure your API.

**How it works:**
- All API endpoints (except `/health`) require a valid API key
- WebSocket connections require the API key as a query parameter
- Invalid or missing API keys return 401/403 errors

### 2. Security Features

- ✅ **API Key Protection**: All endpoints require valid API key
- ✅ **WebSocket Security**: WebSocket connections are authenticated
- ✅ **CORS Protection**: Configured to allow only authorized origins
- ✅ **Health Check**: Unauthenticated health endpoint for monitoring

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)

```bash
# Run the deployment script
./deploy-secure.sh
```

This script will:
- Generate a secure random API key
- Create `.env` files for both backend and frontend
- Set up proper environment variables

### Option 2: Manual Setup

1. **Generate a secure API key:**
   ```bash
   openssl rand -hex 32
   ```

2. **Create backend `.env` file:**
   ```bash
   cat > .env << EOF
   API_KEY=your-generated-api-key-here
   EOF
   ```

3. **Create frontend `.env.local` file:**
   ```bash
   cat > face-verification-ui/.env.local << EOF
   VITE_API_KEY=your-generated-api-key-here
   VITE_BACKEND_URL=https://kyc-backend-7f7c.onrender.com
   EOF
   ```

## 🔧 Deployment Steps

### 1. Backend Deployment

**For Render.com:**
1. Go to your backend service dashboard
2. Navigate to Environment Variables
3. Add: `API_KEY` = `your-secure-api-key`
4. Redeploy the service

**For Docker:**
```bash
docker run -e API_KEY=your-secure-api-key -p 8000:8000 your-backend-image
```

### 2. Frontend Deployment

**For Render.com:**
1. Go to your frontend service dashboard
2. Navigate to Environment Variables
3. Add: `VITE_API_KEY` = `your-secure-api-key`
4. Redeploy the service

**For local development:**
```bash
cd face-verification-ui
npm run dev
```

## 🧪 Testing Security

### Test Unauthorized Access
```bash
# This should fail with 401
curl https://kyc-backend-7f7c.onrender.com/health

# This should fail with 401
curl -H "X-API-Key: invalid-key" https://kyc-backend-7f7c.onrender.com/api-key
```

### Test Authorized Access
```bash
# This should work
curl -H "X-API-Key: your-actual-api-key" https://kyc-backend-7f7c.onrender.com/api-key
```

## 🔒 Security Best Practices

### 1. API Key Management
- ✅ Generate cryptographically secure random keys
- ✅ Use different keys for development and production
- ✅ Rotate keys regularly (every 3-6 months)
- ✅ Never commit API keys to version control

### 2. Environment Variables
- ✅ Use `.env` files for local development
- ✅ Use hosting platform environment variables for production
- ✅ Keep `.env` files out of version control (add to `.gitignore`)

### 3. Network Security
- ✅ Use HTTPS/WSS for all communications
- ✅ Consider implementing rate limiting
- ✅ Monitor API usage for suspicious activity

## 🚨 Security Checklist

Before going live, ensure:

- [ ] API key is set and working
- [ ] Frontend can connect with valid API key
- [ ] Unauthorized requests are blocked
- [ ] Environment variables are properly set
- [ ] `.env` files are not committed to git
- [ ] HTTPS is enabled on all endpoints
- [ ] CORS is properly configured

## 🔍 Monitoring & Alerts

### Recommended Monitoring
- API response times
- Failed authentication attempts
- Unusual traffic patterns
- Error rates

### Security Alerts
- Multiple failed API key attempts
- Unusual geographic access patterns
- Sudden traffic spikes

## 🆘 Troubleshooting

### Common Issues

1. **"API key is required" error**
   - Check if API_KEY environment variable is set
   - Verify the key is being sent in requests

2. **WebSocket connection fails**
   - Ensure API key is included in WebSocket URL
   - Check if backend is running with correct environment

3. **Frontend can't connect**
   - Verify VITE_API_KEY is set in frontend
   - Check browser console for errors

### Debug Commands
```bash
# Check backend environment
echo $API_KEY

# Test backend locally
uvicorn app:app --reload

# Check frontend environment
cd face-verification-ui
echo $VITE_API_KEY
```

## 📞 Support

If you encounter issues:
1. Check the logs for error messages
2. Verify environment variables are set correctly
3. Test with the provided curl commands
4. Ensure both backend and frontend are using the same API key

## 🔄 Updates & Maintenance

- **Monthly**: Review API usage logs
- **Quarterly**: Rotate API keys
- **Annually**: Review security configuration
- **As needed**: Update dependencies and security patches

---

**⚠️ Important**: Keep your API key secure and never share it publicly. This key is the only thing protecting your backend from unauthorized access.

**🔒 Security Enhancement**: The system now **fails to start** without a proper API key, ensuring it can never be accidentally deployed insecurely.
