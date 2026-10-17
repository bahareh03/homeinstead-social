"""Fallback wording (used when no Claude API key is set) and verified statistics.
Image text follows the toolkit: short Instrument Serif headline + max ~20 words of supporting text."""

SOURCE = "Home Instead / YouGov survey, Sept 2026"

# Verified figures from the Home Instead 'Love Your Weekend' YouGov survey (2,158 UK adults, 498 family carers)
STATS = [
    {"number": "38%", "text": "of family carers **rarely get time for themselves** at the weekend"},
    {"number": "58%", "text": "of family carers **put their own plans on hold** because of caring"},
    {"number": "46%", "text": "of family carers with professional care say it **reduces stress for the whole family**"},
    {"number": "44%", "text": "of family carers say caring **affects their relationship** with the person they support"},
    {"number": "41%", "text": "of family carers spend **more time caring** than enjoying time together"},
    {"number": "31%", "text": "of family carers with professional care say it gives them **time to recharge**"},
    {"number": "1 in 4", "text": "UK adults are **family carers** in some capacity"},
]

BANK = {
    "difference": [
        {"headline": "Care that's never rushed",
         "sub": "Visits of **at least an hour**, with the same familiar face.",
         "body": "Care should never feel like a race against the clock. Our visits last at least an hour, with "
                 "the same care professional each time, so your loved one gets real conversation, real "
                 "support and someone they know."},
        {"headline": "A familiar face, every visit",
         "sub": "We match every client with a **small, consistent team**.",
         "body": "Trust grows when it's the same person each time. We match every client with care "
                 "professionals who share their interests and personality, and keep that team consistent."},
    ],
    "live_in": [
        {"headline": "Their home, their routine",
         "sub": "One-to-one **live-in care**, so there's no need to move.",
         "body": "Live-in care means your loved one stays in the home they love, keeping their routines, "
                 "garden, pets and neighbours, with one-to-one support day and night."},
        {"headline": "Stay at home, with care that stays",
         "sub": "A dedicated Care Pro, **living alongside** your loved one.",
         "body": "With live-in care, a dedicated care professional lives alongside your loved one, offering "
                 "companionship, practical help and peace of mind for the whole family."},
    ],
    "recruitment": [
        {"headline": "We're hiring!",
         "sub": "Join our **Care Pros** in Leeds. No experience needed.",
         "points": ["Full paid training", "Flexible hours", "Visits of at least an hour", "Wellbeing support"],
         "body": "We're recruiting care professionals across Leeds. No experience needed: full paid training, "
                 "flexible hours and visits of at least an hour, so you really get to know the people you support."},
        {"headline": "Now hiring Care Pros!",
         "sub": "Kindness is the **only experience** you need.",
         "points": ["Full paid training", "Flexible hours to suit you", "Never-rushed visits", "A friendly local team"],
         "body": "If you're patient, kind and love a good chat, you could make a real difference as a Home "
                 "Instead care professional in Leeds. We'll give you all the training you need."},
    ],
    "choice": [
        {"headline": "Time for you, too",
         "sub": "Our respite care gives **family carers** a proper break.",
         "stat": STATS[0],
         "body": "Caring for someone you love is a gift, but everyone needs a break. Our respite care gives "
                 "family carers time to rest while their loved one is in safe, familiar hands."},
        {"headline": "Companionship that brightens the day",
         "sub": "A friendly face for **chats, walks and a cuppa**.",
         "stat": STATS[3],
         "body": "Sometimes the best care is simply good company: a chat over a cuppa, a walk to the shops "
                 "or a favourite programme together."},
        {"headline": "Help after a hospital stay",
         "sub": "Support at home, so **recovery can happen** where they're happiest.",
         "stat": STATS[2],
         "body": "The first weeks after a hospital stay can be the hardest. We help with everyday tasks, "
                 "routines and reassurance so recovery can happen at home."},
    ],
    "education": [
        {"headline": "Signs a loved one may need support",
         "points": ["Missed meals or an empty fridge", "Changes in mood or memory", "Unopened post piling up",
                    "Less interest in going out"],
         "body": "Small changes can be early signs that someone needs a little more support at home. "
                 "If you notice them, have a gentle conversation and speak to their GP if you're worried."},
    ],
}

EDUCATION_POINTS = {
    "dementia": ["Repeating questions or stories", "Getting lost in familiar places", "Struggling with everyday tasks",
                 "Changes in mood"],
    "alzheimer": ["Forgetting recent conversations", "Losing track of dates", "Misplacing everyday items",
                  "Withdrawing from hobbies"],
    "parkinson": ["Keep floors clear", "Allow extra time", "Keep up gentle exercise"],
    "sundowning": ["Keep a calm evening routine", "Turn lights on early", "Reduce noise and clutter"],
    "falls": ["Remove loose rugs", "Add brighter lighting", "Stand up slowly", "Keep a phone within reach"],
    "loneliness": ["Days without a conversation", "Losing interest in hobbies", "Not wanting to 'bother anyone'"],
    "stroke": ["Fatigue that lasts for weeks", "New difficulty with speech", "Low mood after coming home"],
    "dehydration": ["Keep a drink within reach", "Offer water-rich foods", "Watch for confusion or headaches"],
}
