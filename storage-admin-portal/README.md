# Storage Admin Portal

Admin dashboard for ICTNexus Storage Service.

## Features

- **Node Management**: Create, monitor, and manage storage nodes
- **System Overview**: Real-time statistics and capacity monitoring
- **User Management**: View users, manage quotas, update roles
- **Analytics**: Storage usage trends and performance metrics
- **Health Monitoring**: Track node status and uptime

## Quick Start

```bash
npm install
npm run dev
```

Access at: http://localhost:5176

## Default Admin Credentials

- Email: admin@ictnexus.edu
- Password: admin

## Key Admin Functions

### Node Management
- View all storage nodes
- Check node health status
- Monitor capacity and utilization
- Add/remove nodes

### User Administration
- List all users
- View user storage usage
- Adjust storage quotas
- Change user roles
- Activate/deactivate accounts

### System Monitoring
- Total system capacity
- Active nodes count
- Total files stored
- System-wide utilization

## Environment Variables

Create a `.env` file:

```
VITE_API_URL=http://localhost:8085/api/v1
```

## Tech Stack

- React + TypeScript
- TailwindCSS
- Recharts (for graphs)
- Lucide Icons
- Axios (API calls)
