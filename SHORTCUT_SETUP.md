# 📱 iOS Shortcut Setup Guide

## Quick Setup (Modify Your Existing Shortcut)

### Step 1: Add More Health Data (After Your Sleep Action)

You already have sleep data! Now add these additional actions:

#### **Action: Get HRV**
```
Find Health Samples
  → Type: Heart Rate Variability (HRV SDNN)
  → Date: Today
  → Sort: Latest First
  → Limit: 1
```
Set Variable: `HRV`

#### **Action: Get Resting Heart Rate**
```
Find Health Samples
  → Type: Resting Heart Rate
  → Date: Today
  → Sort: Latest First
  → Limit: 1
```
Set Variable: `RestingHR`

#### **Action: Get Active Energy**
```
Find Health Samples
  → Type: Active Energy Burned
  → Date: Yesterday
  → Calculate Statistics: Sum
```
Set Variable: `ActiveEnergy`

---

### Step 2: Create JSON Dictionary

Add this action after collecting all health data:

```
Dictionary
  Keys:
    sleep_hours = [Your Sleep Variable]
    hrv = [HRV Variable]
    resting_hr = [RestingHR Variable]
    active_energy = [ActiveEnergy Variable]
    date = [Current Date]
```

---

### Step 3: Convert to JSON Text

```
Get Text from Input
  → Input: [Dictionary from previous step]
```

This automatically converts the dictionary to JSON format.

---

### Step 4: Save to iCloud

```
Save File
  → File: health_data.json
  → Destination: iCloud Drive/habit_coach/
  → Overwrite: Yes
```

---

## 🧪 Test Your Shortcut

### On iPhone:
1. Run your modified shortcut manually
2. Grant any new permissions (HRV, Heart Rate, Activity)
3. Check Files app → iCloud Drive → habit_coach folder
4. Should see `health_data.json` file

### On Mac:
```bash
cat ~/Library/Mobile\ Documents/com~apple~CloudDocs/habit_coach/health_data.json
```

Should show your real health data!

### On Web App:
Navigate to: http://192.168.1.67:5001/health

Should say:
- ✅ Connected to Apple Health
- Show your real sleep, HRV, and activity data

---

## 📋 Quick Reference

### Minimum JSON Format (Sleep Only):
```json
{
  "sleep_hours": 7.5
}
```

### Full JSON Format (Recommended):
```json
{
  "sleep_hours": 7.5,
  "hrv": 65,
  "resting_hr": 58,
  "active_energy": 450,
  "date": "2025-10-09"
}
```

---

## ⚙️ Shortcut Actions Summary

1. **Get Sleep Data** (you already have this!)
2. **Get HRV** → Set Variable `HRV`
3. **Get Resting HR** → Set Variable `RestingHR`
4. **Get Active Energy** → Set Variable `ActiveEnergy`
5. **Create Dictionary** with all variables
6. **Get Text from Input** (converts to JSON)
7. **Save File** to `iCloud Drive/habit_coach/health_data.json`

---

## 🔄 Automation

Set it to run automatically every morning:

1. **Automation** tab → **+**
2. **Time of Day**: 8:00 AM
3. **Run**: Your shortcut
4. **Ask Before Running**: OFF

---

## ✅ Verify It's Working

The app will show:
- On Health page: "✅ Connected to Apple Health"
- Real data instead of "simulated"
- When logging: "✅ Data from Apple Health"

Your ML model will now learn from YOUR actual health patterns!

