# 🚀 Quick Start: Secure Your KYC Backend in 5 Minutes

## ⚡ Super Quick Setup

### 1. Generate a Secure API Key
```bash
# Run this command to generate a secure key
openssl rand -hex 32
```

### 2. Set Environment Variables
```bash
# Backend (.env file)
echo "API_KEY=your-generated-key-here" > .env

# Frontend (.env.local file)
echo "VITE_API_KEY=your-generated-key-here" > face-verification-ui/.env.local
```

### 3. Deploy to Render.com

**Backend:**
1. Go to your backend service
2. Add environment variable: `API_KEY` = `your-key`
3. Redeploy

**Frontend:**
1. Go to your frontend service  
2. Add environment variable: `VITE_API_KEY` = `your-key`
3. Redeploy

### 4. Test Security
```bash
# This should fail (good!)
curl https://kyc-backend-7f7c.onrender.com/api-key

# This should work
curl -H "X-API-Key: your-key" https://kyc-backend-7f7c.onrender.com/api-key
```

## 🎯 What This Achieves

- ✅ **Blocks unauthorized access** to your backend
- ✅ **Secures WebSocket connections** 
- ✅ **Protects all API endpoints**
- ✅ **Maintains frontend functionality**
- ✅ **Easy to manage and rotate**

## 🔧 Advanced Options

### Automated Setup
```bash
# Run the deployment script
./deploy-secure.sh
```

### Manual Testing
```bash
# Run comprehensive security tests
python test-security.py
```

### Docker Deployment
```bash
# Update docker-compose.yml with your API key
docker-compose up -d
```

## 🚨 Important Notes

- **Never commit** `.env` files to git
- **Keep your API key** secure and private
- **Rotate keys** every 3-6 months
- **Monitor logs** for suspicious activity

## 📞 Need Help?

1. Check the `SECURITY_SETUP.md` for detailed instructions
2. Run `python test-security.py` to diagnose issues
3. Verify environment variables are set correctly
4. Check that both backend and frontend use the same key

---

**🎉 That's it!** Your backend is now secure and only accessible with the proper API key.

## 🔒 **Security Enhancement**

The system now **fails to start** without a proper API key, ensuring it can never be accidentally deployed insecurely. This is a critical security feature that prevents the "default key" vulnerability.
