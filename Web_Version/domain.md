# Subdomain Setup Guide - ACX Audio Analyzer

## Target Subdomain: `analisethis.frankyredente.com`

---

## Step-by-Step Setup (Fasthost.co.uk + Vercel)

### Part 1: DNS Configuration on Fasthost.co.uk

**1. Log in to Fasthost Control Panel**
   - Go to: https://www.fasthost.co.uk/
   - Click "Login" (top right)
   - Enter your Fasthost credentials
   - You should see your control panel dashboard

**2. Navigate to DNS Management**
   - Look for "Domains" or "Domain Management" section
   - Click on "frankyredente.com" (your domain)
   - Find "DNS Management" or "DNS Zone Editor" or "Advanced DNS"
   - This is where you'll add DNS records

**3. Add CNAME Record**
   - Click "Add Record" or "Add DNS Record"
   - Select record type: **CNAME**
   - Fill in the fields:
     - **Name/Host/Alias:** `analisethis`
     - **Value/Points to/Target:** `cname.vercel-dns.com`
     - **TTL:** `3600` (or leave as "Auto")
   - Click "Save" or "Add Record"

**What this does:** When someone visits `analisethis.frankyredente.com`, DNS points them to Vercel's servers.

**Fasthost-specific notes:**
- Fasthost may show "analisethis.frankyredente.com" as the full record name - that's fine
- Don't include the full domain in the "Name" field, just `analisethis`
- Some Fasthost interfaces call it "Alias" instead of "CNAME" - same thing

---

### Part 2: Vercel Configuration

**1. Go to Vercel Dashboard**
   - Log in to: https://vercel.com/
   - Find your project: "calibration-metrics" (or whatever you named it)
   - Click on the project to open it

**2. Add Custom Domain**
   - Click "Settings" (top navigation)
   - Click "Domains" (left sidebar)
   - You'll see your current domain: `calibration-metrics.vercel.app`

**3. Add the New Subdomain**
   - In the "Add Domain" field, type: `analisethis.frankyredente.com`
   - Click "Add"

**4. Vercel Will Check DNS**
   - Vercel will automatically check if the CNAME record exists
   - If it's been less than ~10 minutes since you added it on Fasthost, it might not be found yet
   - You'll see one of these statuses:
     - ✅ **Valid Configuration** → Success! You're done.
     - ⏳ **Pending Configuration** → Wait a few minutes, DNS is propagating
     - ❌ **Invalid Configuration** → Check your CNAME record on Fasthost

**5. SSL Certificate (Automatic)**
   - Once DNS is verified, Vercel automatically creates an SSL certificate
   - This takes 1-5 minutes
   - Your subdomain will be accessible via HTTPS (secure)

---

### Part 3: Verify It's Working

**After 5-60 minutes (DNS propagation time):**

1. **Test the URL:**
   - Open browser
   - Go to: `https://analisethis.frankyredente.com`
   - You should see your ACX Audio Analyzer app!

2. **Check DNS Propagation (Optional):**
   - Go to: https://www.whatsmydns.net/
   - Enter: `analisethis.frankyredente.com`
   - Select record type: `CNAME`
   - Click "Search"
   - You should see `cname.vercel-dns.com` appearing worldwide (green checkmarks)

3. **Verify SSL Certificate:**
   - Click the padlock icon in your browser
   - Should show "Connection is secure"
   - Certificate issued by: Let's Encrypt (via Vercel)

---

## Troubleshooting

### Issue: "Invalid Configuration" in Vercel
**Solution:**
- Go back to Fasthost DNS settings
- Double-check the CNAME record:
  - Name: `analisethis` (NOT the full domain)
  - Value: `cname.vercel-dns.com` (exactly this)
- Wait 10-15 minutes and try again in Vercel

### Issue: DNS not propagating after 1 hour
**Solution:**
- Check Fasthost control panel - is the CNAME record showing?
- Try clearing your browser cache
- Try a different browser or incognito mode
- Check DNS with: `nslookup analisethis.frankyredente.com` (in Terminal/Command Prompt)

### Issue: Shows "This domain is not configured" error
**Solution:**
- The CNAME is working, but Vercel hasn't finished setup
- Go back to Vercel → Settings → Domains
- Click "Refresh" next to your domain
- Wait a few more minutes

### Issue: Certificate error (not secure)
**Solution:**
- Vercel is still creating the SSL certificate
- Wait 5-10 minutes
- Hard refresh the page (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows)

---

## Expected Timeline

| Step | Time |
|------|------|
| Add CNAME on Fasthost | 2 minutes |
| Add domain on Vercel | 1 minute |
| DNS propagation | 5-60 minutes |
| SSL certificate creation | 1-5 minutes |
| **Total** | **~10-65 minutes** |

---

## Quick Reference

**Your Setup:**
- **Domain:** frankyredente.com
- **Subdomain:** analisethis.frankyredente.com
- **DNS Host:** Fasthost.co.uk
- **App Host:** Vercel
- **Current URL:** https://calibration-metrics.vercel.app
- **New URL:** https://analisethis.frankyredente.com

**DNS Record to Add:**
```
Type:   CNAME
Name:   analisethis
Target: cname.vercel-dns.com
TTL:    3600
```

---

## After Setup is Complete

Once `analisethis.frankyredente.com` is working:

1. **Both URLs will work:**
   - https://calibration-metrics.vercel.app (original)
   - https://analisethis.frankyredente.com (new custom domain)

2. **Optional: Make custom domain primary**
   - In Vercel → Settings → Domains
   - Click the three dots next to `analisethis.frankyredente.com`
   - Select "Set as Primary Domain"
   - This will redirect the Vercel URL to your custom domain

3. **Update documentation:**
   - Update web_plan.md with new URL
   - Update README.md
   - Update social media links (if shared)

---

## Alternative Subdomain Names (If You Change Your Mind)

Instead of `analisethis`, you could use:
- `analyser.frankyredente.com`
- `acx.frankyredente.com`
- `audio.frankyredente.com`
- `check.frankyredente.com`
- `analyzer.frankyredente.com`

Just repeat the same steps with a different subdomain name.

---

---

## ✅ Setup Progress - October 21, 2025

### Completed Steps:

**Part 1: Fasthost DNS Configuration** ✅ DONE
- Logged in to Fasthost.co.uk
- Navigated to Advanced DNS Settings for frankyredente.com
- Added CNAME record:
  - **Type:** CNAME
  - **Name:** analisethis
  - **Target:** cname.vercel-dns.com
  - **TTL:** 3600
- Record saved successfully

**Part 2: Vercel Configuration** ✅ DONE
- Logged in to Vercel dashboard
- Navigated to calibration-metrics project
- Settings → Domains
- Added domain: `analisethis.frankyredente.com`
- Status: "Invalid Configuration" (expected - DNS not propagated yet)

### Current Status: ✅ LIVE AND WORKING!

**What Happened:**
- ❌ Initial attempt on Fasthost failed (nameservers pointed to Wix, not Fasthost)
- ✅ Discovered domain uses Wix DNS (NS2.WIXDNS.NET, NS3.WIXDNS.NET)
- ✅ Added CNAME record in Wix DNS instead
- ✅ DNS propagated in ~5-10 minutes (much faster than expected!)
- ✅ Vercel automatically verified and created SSL certificate
- ✅ Domain is now live with HTTPS!

**Final DNS Configuration (in Wix):**
- ✅ CNAME record added on Wix
- ✅ Host: `analisethis`
- ✅ Target: `cname.vercel-dns.com`
- ✅ TTL: 30 minutes
- ✅ Status: Active and propagated

### ✅ Completed - Domain is Live!

**Live URL:** https://analisethis.frankyredente.com

**Verification:**
- ✅ Domain loads successfully
- ✅ SSL certificate valid (HTTPS working)
- ✅ ACX Audio Analyzer app running
- ✅ Payment modal and all features working

### Optional Next Steps:

1. **Set as Primary Domain in Vercel (Optional):**
   - Go to Vercel → Settings → Domains
   - Click three dots next to `analisethis.frankyredente.com`
   - Select "Set as Primary Domain"
   - This will redirect `calibration-metrics.vercel.app` to your custom domain

2. **Update Documentation:**
   - ✅ domain.md updated
   - ⏳ Update web_plan.md with new custom domain URL
   - ⏳ Update README.md with custom domain
   - ⏳ Update social media/sharing links (if applicable)

3. **Promote with Custom Domain:**
   - Share on Reddit/forums with: https://analisethis.frankyredente.com
   - Update any existing posts/links
   - Professional custom URL for marketing!

---

**Last Updated:** October 21, 2025
**Status:** ✅ LIVE AND WORKING!
**Live URL:** https://analisethis.frankyredente.com
**DNS Provider:** Wix (NS2.WIXDNS.NET, NS3.WIXDNS.NET)
**Hosting:** Vercel with automatic SSL
