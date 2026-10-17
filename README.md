# Daily social posts: Home Instead Leeds Central

Every morning, GitHub Actions creates one post and publishes it to **Facebook, Instagram and Google Business Profile** through Metricool.

| Day | Post |
|---|---|
| Mon | Home care and how we're different |
| Tue | Franchisor content (first 3 Tuesdays) or a topic picked to beat local competitors |
| Wed | Educational: Alzheimer's, dementia, stroke, falls and others (rotates) |
| Thu | Competitive topic |
| Fri | Live-in care |
| Sat | Recruitment |
| Sun | Competitive topic |

- **Keywords:** these come weekly from your website and from Leeds senior home care / domiciliary care companies. Only keywords are taken, never their text or images.
- **Images:** each post gets a branded image built from your website photos. Franchisor posts use the franchisor's image.
- **Approval:** the **first 5 posts** each open a GitHub Issue. Add the `approved` label to publish it, or close the issue to skip it. After that, posts publish automatically.
- **Changes:** edit `config.yaml` to change days, topics, hashtags or competitors.

## One-off setup (about 1 hour)

1. **Metricool**: connect Facebook, Instagram (business account) and Google Business Profile at
   https://app.metricool.com/brands/connections?blogId=6902455. Then get your API token and user ID under Account settings → API. API access is only on Metricool's higher plans, so check yours.
2. **Cloudflare R2** (free) holds the images, because Instagram and Google need a public link:
   - Go to dash.cloudflare.com → R2 → create a bucket, e.g. `homeinstead-posts`.
   - In the bucket settings, turn on the **Public r2.dev URL**.
   - Go to R2 → Manage API tokens → create a token with *Object Read & Write*.
3. **Claude API key** from console.anthropic.com. This is strongly recommended for daily posts. Without it, posts use basic templates that repeat.
4. **GitHub**: create a **private** repo, upload this folder, and add these secrets (Settings → Secrets and variables → Actions):

| Secret | Where from |
|---|---|
| `METRICOOL_TOKEN`, `METRICOOL_USER_ID` | Metricool → Account settings → API |
| `R2_ACCOUNT_ID` | Cloudflare dashboard (right-hand side) |
| `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY` | The R2 API token |
| `R2_BUCKET` | Bucket name |
| `R2_PUBLIC_URL` | The bucket's `https://pub-….r2.dev` address |
| `ANTHROPIC_API_KEY` | console.anthropic.com |

5. In `config.yaml`, set `recruitment_url` to your jobs page.
6. **Test**: go to Actions → *Daily social post* → **Run workflow**. An approval issue should appear.

## Monthly franchisor content
Upload it to `franchisor/YYYY-MM/` (see `franchisor/README.md`).

## Good to know
- Check that Home Instead UK allows franchisees to post this way, as brand rules may apply.
- Only use photos of clients you have written consent for.
