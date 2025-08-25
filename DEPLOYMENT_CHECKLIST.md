# KYC App Deployment Checklist

## Pre-Deployment ✅
- [ ] Code committed to Git repository
- [ ] `render.yaml` configuration verified
- [ ] Dockerfiles tested locally
- [ ] Environment variables prepared
- [ ] MongoDB setup (if using database)

## Deployment Steps ✅
- [ ] Render account created
- [ ] Repository connected to Render
- [ ] Blueprint created from `render.yaml`
- [ ] Backend service deployed successfully
- [ ] Frontend service deployed successfully
- [ ] Health checks passing

## Post-Deployment Verification ✅
- [ ] Backend accessible at health endpoint
- [ ] Frontend loads in browser
- [ ] Camera access working
- [ ] Face detection functional
- [ ] Backend API endpoints responding
- [ ] Services not sleeping (if on free plan)

## Environment Variables to Set ✅
### Backend
- [ ] `MONGODB_URI` (if using MongoDB)
- [ ] `MONGODB_DB` (if using MongoDB)
- [ ] `MONGODB_TLS_INSECURE` (if using MongoDB)

### Frontend
- [ ] Automatically gets backend URL from service dependency

## URLs to Test ✅
- [ ] Backend health: `https://your-backend.onrender.com/health`
- [ ] Frontend: `https://your-frontend.onrender.com`
- [ ] API endpoints (if documented)

## Common Issues to Check ✅
- [ ] Docker build successful
- [ ] Port configurations correct
- [ ] Service dependencies resolved
- [ ] Environment variables set
- [ ] CORS configuration working
- [ ] Database connections (if applicable)

## Next Steps ✅
- [ ] Test all functionality thoroughly
- [ ] Monitor service performance
- [ ] Set up monitoring/alerting
- [ ] Document API usage
- [ ] Plan production upgrade
