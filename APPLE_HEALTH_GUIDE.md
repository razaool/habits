# 🍎 Apple Health Integration Guide

## Overview

The AI Habit Coach can integrate with Apple Health to pull **real** sleep, activity, and stress data instead of using simulated values. This dramatically improves prediction accuracy because the ML models learn from YOUR actual physiological data.

## Current Status: ⚠️ Placeholder

Right now, the app uses **simulated health data**. The integration layer is built and ready - it just needs one of the three implementation options below.

---

## What Data We Use

### Sleep Quality (💤)
- **From Apple Health**: Sleep duration, deep sleep %, interruptions
- **Converted to**: 1-10 quality score
- **Why it matters**: Poor sleep → lower completion probability
- **Your pattern**: Watch tracks sleep automatically

### Stress Level (😰)
- **From Apple Health**: Heart Rate Variability (HRV), resting heart rate
- **Converted to**: 1-10 stress score
- **Why it matters**: High stress → you "shutdown" (your profile)
- **Your pattern**: Watch tracks HRV during sleep

### Energy Level (⚡)
- **From Apple Health**: Active calories, steps, exercise minutes
- **Converted to**: 1-10 energy score
- **Why it matters**: Yesterday's high activity → today's low energy
- **Your pattern**: Watch tracks activity all day

### Recovery Score (🔄)
- **Combination**: Sleep + HRV + resting HR
- **Similar to**: Whoop, Oura Ring scores
- **Why it matters**: Overall readiness to perform
- **Your pattern**: Calculated automatically

---

## Implementation Options

### ⭐ Option 1: iOS Shortcuts (Recommended - Easiest!)

**What**: Use Apple's Shortcuts app to export data daily

**Pros**:
- ✅ No coding required
- ✅ Works immediately
- ✅ No special permissions
- ✅ Can sync via iCloud

**Steps**:

1. **Create iOS Shortcut** on your iPhone:
   ```
   Get Health Sample
   → Sleep Analysis (Last Night)
   → Heart Rate Variability (Today)
   → Resting Heart Rate (Today)  
   → Active Energy (Today)
   → Format as JSON
   → Save to iCloud/health_data.json
   ```

2. **Schedule** to run automatically every morning at 8am

3. **Update Python code** to read from iCloud:
   ```python
   # In src/apple_health.py, modify get_sleep_data():
   data_file = Path("~/Library/Mobile Documents/com~apple~CloudDocs/health_data.json")
   with open(data_file) as f:
       health_data = json.load(f)
   return health_data
   ```

4. **Set enabled flag**:
   ```python
   self.enabled = True  # in AppleHealthIntegration.__init__
   ```

**Example Shortcut**: (I can provide the exact shortcut if you want!)

---

### Option 2: Export XML Parsing

**What**: Export full health data from iPhone, parse the XML

**Pros**:
- ✅ One-time export gets all historical data
- ✅ No ongoing automation needed
- ✅ Privacy (data stays local)

**Cons**:
- ❌ XML file is HUGE (100+ MB)
- ❌ Need to re-export for updates
- ❌ Manual process

**Steps**:

1. **Export Health Data** from iPhone:
   - Open Health app
   - Tap profile picture (top right)
   - Export All Health Data
   - Save to Files → Transfer to Mac

2. **Update Python code**:
   ```python
   import xml.etree.ElementTree as ET
   
   def parse_health_export(xml_path: Path):
       tree = ET.parse(xml_path)
       root = tree.getroot()
       
       # Parse sleep records
       sleep_records = root.findall('.//Record[@type="HKCategoryTypeIdentifierSleepAnalysis"]')
       
       # Parse HRV
       hrv_records = root.findall('.//Record[@type="HKQuantityTypeIdentifierHeartRateVariabilitySDNN"]')
       
       # etc...
   ```

3. **Run once to populate historical data**

---

### Option 3: Direct HealthKit API

**What**: Native macOS app with HealthKit access

**Pros**:
- ✅ Real-time data access
- ✅ Automatic updates
- ✅ Most robust

**Cons**:
- ❌ Requires macOS app (can't be Python script)
- ❌ Need Apple Developer account
- ❌ Complex permissions setup
- ❌ Most development work

**Steps**:

1. **Create macOS app** (Swift or Objective-C)
2. **Enable HealthKit** in Xcode capabilities
3. **Request permissions** in Info.plist
4. **Query HealthKit**:
   ```swift
   let healthStore = HKHealthStore()
   let sleepType = HKObjectType.categoryType(forIdentifier: .sleepAnalysis)!
   
   healthStore.requestAuthorization(toShare: [], read: [sleepType]) { success, error in
       // Query sleep data
   }
   ```
5. **Export to JSON** that Python reads

**Best approach**: Use PyObjC to call HealthKit from Python (advanced!)

---

## Recommended Path for You

Given you have an **Apple Watch** and are **technical**, I recommend:

### **Phase 1 (This Week): iOS Shortcuts** ⭐
- Quickest to implement (30 minutes)
- Gets you real data immediately
- Good enough for 90-day habit tracking

### **Phase 2 (Month 2): Direct API**
- If Shortcuts works well and you want automation
- Build native integration
- More robust long-term

---

## Implementation Checklist

### For iOS Shortcuts (Recommended):

- [ ] Open Shortcuts app on iPhone
- [ ] Create new Shortcut
- [ ] Add "Get Health Sample" actions for:
  - [ ] Sleep Analysis (HKCategoryTypeIdentifierSleepAnalysis)
  - [ ] Heart Rate Variability (HKQuantityTypeIdentifierHeartRateVariabilitySDNN)
  - [ ] Resting Heart Rate (HKQuantityTypeIdentifierRestingHeartRate)
  - [ ] Active Energy Burned (HKQuantityTypeIdentifierActiveEnergyBurned)
- [ ] Format as Dictionary/JSON
- [ ] Save to iCloud Drive (health_data.json)
- [ ] Set automation trigger (daily 8am)
- [ ] Update `src/apple_health.py` to read file
- [ ] Set `self.enabled = True`
- [ ] Test!

---

## Code Changes Needed

### Minimal changes to make it work:

**1. Update `src/apple_health.py`:**

```python
def __init__(self, user_id: str):
    self.user_id = user_id
    self.cache_dir = Path("data/health_cache")
    self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if health data file exists
    self.health_data_path = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/health_data.json"
    self.enabled = self.health_data_path.exists()  # Auto-detect!

def get_sleep_data(self, target_date: date) -> Optional[Dict[str, Any]]:
    if not self.is_available():
        return None
    
    # Read from shortcuts-generated file
    with open(self.health_data_path) as f:
        health_data = json.load(f)
    
    # Parse the data
    sleep_info = health_data.get('sleep', {})
    
    return {
        'duration_hours': sleep_info.get('hours', 7),
        'quality_score': sleep_info.get('quality', 7),
        # ... etc
    }
```

**2. That's it!** The rest of the app already uses the health integration.

---

## Testing

### Test with simulated data (current):
```bash
python3 main.py track razaool
# → Option 5: View health data
# Should say "Using simulated data"
```

### Test with real data (after implementation):
```bash
python3 main.py track razaool
# → Option 5: View health data  
# Should show "Apple Health connected"
# Should display real sleep/HRV/activity data
```

---

## What You'll See

### Before Implementation:
```
📊 Your health context today (simulated):
  💤 Sleep Quality: 7.2/10
  ⚡ Energy Level: 6.8/10
  😰 Stress Level: 5.3/10
```

### After Implementation:
```
📊 Your Apple Health data today:
  💤 Sleep Quality: 6.5/10 (5.2 hrs, 3 interruptions)
  ⚡ Energy Level: 8.2/10 (12,543 steps, 45 min exercise)
  😰 Stress Level: 4.1/10 (HRV: 62ms, RHR: 58 bpm)
  🔄 Recovery Score: 7.8/10 (Ready to perform!)
```

---

## Impact on ML Models

### With Simulated Data:
- ❌ Sleep/stress are random
- ❌ No correlation with actual performance
- ❌ Model ignores these features

### With Real Data:
- ✅ Learn YOUR sleep → performance relationship
- ✅ "When you sleep <6 hours, completion drops 40%"
- ✅ "High HRV days have 85% success rate"
- ✅ Sleep becomes top 3 predictive feature

**Expected improvement**: 5-10% better prediction accuracy

---

## Privacy & Security

### Data Storage:
- All health data stays **local** on your Mac
- Saved to `data/health_cache/` (ignored by git)
- Never uploaded anywhere
- You control the data

### Permissions:
- iOS Shortcuts: You grant permission when creating shortcut
- XML Export: Full control, no ongoing access
- Direct API: You approve specific data types

---

## Next Steps

**Want me to:**

1. ✅ **Create the iOS Shortcut for you?**
   - I can provide the exact steps and shortcut file

2. ✅ **Implement the file reading code?**
   - Update `apple_health.py` with actual parsing

3. ✅ **Add more health metrics?**
   - Workout data, mindfulness minutes, etc.

4. ✅ **Create a setup wizard?**
   - GUI to test health data connection

**Let me know which you'd like first!**

---

## Resources

- [Apple Health Export Format](https://developer.apple.com/documentation/healthkit)
- [iOS Shortcuts User Guide](https://support.apple.com/guide/shortcuts/)
- [HealthKit Data Types](https://developer.apple.com/documentation/healthkit/data_types)
- [PyObjC HealthKit](https://pyobjc.readthedocs.io/)

---

**Status**: 🟡 Placeholder implemented, ready for real integration

**Estimated time to implement**: 30 minutes (Shortcuts) to 4 hours (Direct API)

**ROI**: High - Real health data will significantly improve predictions!
