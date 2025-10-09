# 📱 Web App Guide - AI Habit Coach

## ✅ What Was Built

A **mobile-first web app** that you can access from your iPhone! No more terminal commands - just open a browser and tap.

---

## 🚀 Quick Start

### 1. Start the Server (on your Mac)

```bash
cd /Users/razaool/ai-habit-coach/ai-habit-coach/habits
python3 app_web.py
```

You'll see something like:
```
======================================================================
  🎯 AI HABIT COACH - WEB APP
======================================================================

📱 Access from your iPhone:
   http://192.168.1.100:5000

💻 Access from this computer:
   http://localhost:5000

⚠️  Make sure your iPhone is on the same WiFi network!
```

### 2. Open on Your iPhone

**On your iPhone Safari:**
1. Type the IP address shown (e.g., `http://192.168.1.100:5000`)
2. Tap "Go"
3. Select your profile (Razaool)
4. Start tracking!

**Pro tip**: Add to Home Screen for app-like experience:
- Tap the Share button
- "Add to Home Screen"
- Now it looks like a native app! 📱

---

## 📱 Features

### 🏠 Dashboard
- See your stats at a glance
- Current streak 🔥
- Completion rate
- Quick access to log habit

### ✅ Log Habit
- Tap to log today's habit
- Yes/No buttons
- Rate difficulty & motivation with sliders
- See your health data (sleep/stress/energy)
- Add notes

### 📊 Statistics  
- Overall performance
- Success rate by day of week
- Recent trends
- All your numbers

### 🤖 AI Recommendations
- Optimal times for today
- Current success probability
- Personalized insights
- Streak milestones

### 🍎 Health Data
- Last 7 days of health metrics
- Sleep, energy, stress, recovery
- Apple Watch integration status

---

## 🎨 Design Features

### Mobile-First
- ✅ Optimized for iPhone screen
- ✅ Large tap targets
- ✅ Swipe-friendly navigation
- ✅ Beautiful gradients
- ✅ Emoji indicators

### Bottom Navigation
- 🏠 Home
- ✅ Log
- 📊 Stats
- 🤖 AI
- 🍎 Health

### No Typing Required
- Big buttons
- Sliders for ratings
- Tap and go
- Optional notes only

---

## 💡 Usage Tips

### Daily Workflow

**Morning:**
1. Open app on iPhone
2. Tap 🤖 to see optimal time for today

**During Day:**
- Do your habit at suggested time

**Evening:**
1. Open app
2. Tap ✅ (Log)
3. Tap "Yes, I did it!" or "No, I skipped it"
4. If yes: Slide difficulty/motivation ratings
5. Tap submit
6. Done! 🎉

**Takes < 30 seconds to log!**

---

## 🔧 Technical Details

### Server Info
- **Framework**: Flask (Python web framework)
- **Host**: 0.0.0.0 (accessible from network)
- **Port**: 5000
- **Data**: Uses same files as CLI app

### File Structure
```
app_web.py              # Flask backend
templates/              # HTML pages
  ├── base.html         # Layout template
  ├── dashboard.html    # Home page
  ├── log_habit.html    # Log habit form
  ├── stats.html        # Statistics
  ├── recommendations.html  # AI insights
  └── health.html       # Health data
```

### Data Compatibility
- ✅ Uses same data files as CLI
- ✅ Can switch between web & CLI
- ✅ All features available
- ✅ Same ML models

---

## 🌐 Network Setup

### If iPhone Can't Connect

**Option 1: Check Same WiFi**
- Mac: System Preferences → Network
- iPhone: Settings → WiFi
- Must be same network!

**Option 2: Check Firewall**
```bash
# Mac: Allow incoming connections
System Preferences → Security & Privacy → Firewall → Firewall Options
→ Allow Python to accept incoming connections
```

**Option 3: Use Localhost (Mac only)**
- If on Mac: use `http://localhost:5000`
- Won't work from iPhone

---

## 📊 Advantages Over CLI

### ✅ Better
- 📱 Use from iPhone anywhere in house
- 🎨 Beautiful visual interface
- 👆 Touch-friendly
- 🚀 Faster (no typing)
- 💾 Add to Home Screen (app-like)

### CLI Still Useful For
- 🔧 Initial profile creation
- 🤖 Running simulation/training
- 🔬 Development/debugging

---

## 🎯 Common Workflows

### First Time Setup

**On Mac (Terminal):**
```bash
# 1. Create profile (one time)
python3 main.py profile

# 2. Generate synthetic data
python3 main.py simulate razaool

# 3. Train models
python3 main.py train razaool

# 4. Start web server
python3 app_web.py
```

**On iPhone (Safari):**
```
# 5. Open http://YOUR_IP:5000
# 6. Select profile
# 7. Start tracking!
```

### Daily Use

**Mac:** Keep server running (or start when needed)
**iPhone:** Open app, log habit (30 seconds)

### Weekly Review

**iPhone:**
1. Tap 📊 Stats
2. Review patterns
3. Tap 🤖 AI for insights

**Mac (Optional):**
```bash
# Retrain models with new data
python3 main.py train razaool

# Generate visualizations
python3 main.py visualize razaool
```

---

## 🛠️ Troubleshooting

### App Won't Load

**Check server is running:**
```bash
# Should see output like:
 * Running on http://0.0.0.0:5000
```

**If not running:**
```bash
cd /Users/razaool/ai-habit-coach/ai-habit-coach/habits
python3 app_web.py
```

### Wrong IP Address

**Find your actual IP:**
```bash
# Mac:
ipconfig getifaddr en0  # WiFi
# or
ipconfig getifaddr en1  # Ethernet
```

### Port Already in Use

```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Then restart
python3 app_web.py
```

### Styles Not Loading

```bash
# Hard refresh in Safari
Cmd + Shift + R

# Or clear cache
Settings → Safari → Clear History and Website Data
```

---

## 🚀 Advanced Features

### Keep Server Running (Background)

**Terminal 1 (Mac):**
```bash
python3 app_web.py
# Keep this terminal open
```

**Terminal 2 (Mac):**
```bash
# Use for other commands
python3 main.py train razaool
```

### Auto-Start on Boot (Optional)

Create launch agent to start server automatically when Mac boots:
```bash
# Create plist file
nano ~/Library/LaunchAgents/com.habitcoach.webserver.plist

# Add server auto-start config
# (I can provide this if you want)
```

### Custom Domain (Advanced)

Instead of IP address, use custom domain:
```bash
# Add to /etc/hosts
127.0.0.1 habits.local

# Access via http://habits.local:5000
```

---

## 📈 Future Enhancements

### Planned Features

- [ ] Push notifications (when optimal time)
- [ ] Offline support (PWA)
- [ ] Dark mode
- [ ] Habit history timeline
- [ ] Export data (CSV/PDF)
- [ ] Multiple users with login
- [ ] Photo attachments
- [ ] Voice logging ("Hey Siri, log my habit")

### Easy to Add

Want any of these? Let me know!

---

## 🔒 Security Notes

### Current Setup (Development)

- ⚠️ No authentication
- ⚠️ HTTP (not HTTPS)
- ⚠️ Network accessible

**Fine for home use, don't expose to internet!**

### For Production

Would need:
- User authentication
- HTTPS with SSL certificate
- Proper session management
- Database instead of CSV files

---

## 🎉 Summary

**You now have:**
- ✅ Beautiful mobile web app
- ✅ Accessible from iPhone
- ✅ All features from CLI
- ✅ Touch-optimized interface
- ✅ Same data/models
- ✅ Fast & easy to use

**Next steps:**
1. Start server: `python3 app_web.py`
2. Open on iPhone
3. Log your Arabic revision habit!

---

**Questions?** The code is in `app_web.py` and `templates/` - fully customizable!

**Want changes?** Just ask - easy to modify colors, layout, features, etc.

🎯 **Now go build that habit!**
