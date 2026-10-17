# Daily social posts: Home Instead Leeds Central

Every morning, GitHub Actions creates one post and publishes it **directly** to Facebook, Instagram and Google Business Profile. Everything uses free APIs, so it costs **£0 a month** (plus an optional Claude key at pennies per post).

| Day | Post |
|---|---|
| Mon | Home care and how we're different |
| Tue | Franchisor content (first 3 Tuesdays) or a topic picked to beat local competitors |
| Wed | Educational: Alzheimer's, dementia, stroke, falls and others (rotates) |
| Thu | Competitive topic |
| Fri | Live-in care |
| Sat | Recruitment |
| Sun | Competitive topic |

- **Approval:** the **first 5 posts** each open a GitHub Issue. Add the `approved` label to publish it, or close the issue to skip it. After that, posts publish automatically.
- **Failures:** if a platform fails, GitHub emails you and the other platforms still post.
- **Changes:** edit `config.yaml` to change days, topics, hashtags, competitors or platforms.
- **Images:** they're stored in `images/` and served from this repository, which must be **public**. Keys stay private in GitHub Secrets.

## Setup

### 1. Facebook + Instagram (one free Meta app, ~20 min)
1. Make sure your Instagram is a **Business** account and is linked to your Facebook Page. You can do both in the Instagram app → Settings → Account type / Linked accounts.
2. Go to developers.facebook.com → **Create app** → choose type **Business**, and note the App ID and App Secret.
3. Open developers.facebook.com/tools/explorer, select your app, and click **Generate Access Token** with these permissions:
   `pages_show_list, pages_manage_posts, pages_read_engagement, instagram_basic, instagram_content_publish`
4. On your computer, run: `python scripts/get_meta_token.py APP_ID APP_SECRET TOKEN_FROM_STEP_3`
   It prints `FB_PAGE_ID`, `META_PAGE_TOKEN` (permanent) and `IG_USER_ID`.

### 2. Google Business Profile (free; Google approval takes a few days)
1. Go to console.cloud.google.com → create a project.
2. Submit the **Google Business Profile API access request** form (search for "GBP API contact form").
3. Once approved, enable *Google My Business API*, *My Business Account Management API* and *My Business Business Information API*.
4. Go to **APIs & Services → OAuth consent screen**, choose External, then click **Publish app**. While the app is left in "Testing", the token expires after 7 days.
5. Go to **Credentials → Create OAuth client ID** (Desktop app) and download `client_secret.json`.
6. Run `python scripts/get_google_token.py client_secret.json` and sign in with the account that manages the profile. It prints all five `GBP_…` values.

### 3. Add secrets in GitHub
Go to Settings → Secrets and variables → Actions → **New repository secret**:

`FB_PAGE_ID`, `META_PAGE_TOKEN`, `IG_USER_ID`, `GBP_CLIENT_ID`, `GBP_CLIENT_SECRET`, `GBP_REFRESH_TOKEN`, `GBP_ACCOUNT_ID`, `GBP_LOCATION_ID`, and optionally `ANTHROPIC_API_KEY`.

A platform with no secrets yet is simply skipped, so you can start with Facebook and Instagram while Google approves.

### 4. Test
Go to Actions → *Daily social post* → **Run workflow**.

## Monthly franchisor content
Upload it to `franchisor/YYYY-MM/` (see `franchisor/README.md`).

## Good to know
- Check that Home Instead UK allows franchisees to post this way, as brand rules may apply.
- Only use photos of clients you have written consent for.
