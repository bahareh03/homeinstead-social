"""Fallback wording used when no Claude API key is set. Several variants per post type so posts don't repeat.
Each variant can feed any layout: headline (panel/overlay), hook (question layout), points (checklist), myth/fact."""

BANK = {
    "difference": [
        {"headline": "Care that is never rushed",
         "hook": "Tired of rushed 15-minute care visits?",
         "myth": "Home care visits are always rushed",
         "fact": "Our visits last at least an hour, with the same familiar face",
         "body": "Care should never feel like a race against the clock. Our visits last at least an hour, with "
                 "the same care professional each time, so your loved one gets real conversation, real "
                 "support and someone they know."},
        {"headline": "The same friendly face, every visit",
         "hook": "Who will actually turn up at Mum's door?",
         "myth": "You never know who will turn up",
         "fact": "We carefully match each client with a small, consistent team",
         "body": "Trust grows when it's the same person each time. We match every client with care "
                 "professionals who share their interests and personality, and keep that team consistent."},
    ],
    "live_in": [
        {"headline": "Stay at home, with care that stays with you",
         "hook": "Does a care home feel like the only option?",
         "body": "Live-in care means your loved one stays in the home they love, keeping their routines, "
                 "garden, pets and neighbours, with one-to-one support day and night."},
        {"headline": "Their home, their routine, our support",
         "hook": "What if Dad never had to leave his favourite chair?",
         "body": "With live-in care, a dedicated care professional lives alongside your loved one, offering "
                 "companionship, practical help and peace of mind for the whole family."},
    ],
    "recruitment": [
        {"headline": "Do work that truly matters",
         "hook": "Looking for a job that actually means something?",
         "body": "We're recruiting care professionals across Leeds. No experience needed: full paid training, "
                 "flexible hours and visits of at least an hour, so you really get to know the people you support."},
        {"headline": "Kindness is the only experience you need",
         "hook": "Are you the friend everyone turns to?",
         "body": "If you're patient, kind and love a good chat, you could make a real difference as a Home "
                 "Instead care professional in Leeds. We'll give you all the training you need."},
    ],
    "choice": [
        {"headline": "Care that feels like family",
         "hook": "Worried about Mum living on her own?",
         "myth": "Getting help means losing independence",
         "fact": "The right support helps people stay independent at home for longer",
         "body": "A little help at home can make a big difference: companionship, meals, getting out and "
                 "about, and a friendly face to share the day with."},
        {"headline": "Help after a hospital stay",
         "hook": "Coming home from hospital soon?",
         "myth": "Care has to be arranged weeks in advance",
         "fact": "We can often start care within days of your first call",
         "body": "The first weeks after a hospital stay can be the hardest. We help with everyday tasks, "
                 "routines and reassurance so recovery can happen at home."},
        {"headline": "A break for family carers",
         "hook": "When did you last have a day off from caring?",
         "myth": "Asking for help means you've failed as a carer",
         "fact": "Taking a break helps you keep caring for longer",
         "body": "Caring for someone you love is a gift, but everyone needs a break. Our respite care gives "
                 "family carers time to rest while their loved one is in safe, familiar hands."},
    ],
    "education": [
        {"headline": "Signs a loved one may need support",
         "hook": "Is something not quite right with Mum or Dad?",
         "points": ["Missed meals or an empty fridge", "Changes in mood or memory", "Unopened post piling up"],
         "body": "Small changes can be early signs that someone needs a little more support at home. "
                 "If you notice them, have a gentle conversation and speak to their GP if you're worried."},
    ],
}

EDUCATION_POINTS = {
    "dementia": ["Repeating questions or stories", "Getting lost in familiar places", "Struggling with everyday tasks"],
    "falls": ["Loose rugs and poor lighting", "Feeling dizzy when standing", "Avoiding stairs or going out"],
    "loneliness": ["Going days without a conversation", "Losing interest in hobbies", "Saying they 'don't want to bother anyone'"],
    "stroke": ["Fatigue that lasts for weeks", "New difficulty with speech", "Low mood after coming home"],
    "dehydration": ["Dark urine or headaches", "Confusion or tiredness", "Rarely having a drink nearby"],
}
