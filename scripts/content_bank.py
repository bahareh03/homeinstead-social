"""Fallback wording (used when no Claude API key is set) and verified statistics.
Image text follows the toolkit: short Instrument Serif headline + max ~20 words of supporting text.
Enough variants that no post type repeats its wording within a month (each type posts about weekly)."""

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
        {"headline": "Time for a proper chat",
         "sub": "An hour or more means **time to really listen**.",
         "points": ["No 15-minute visits", "Time to chat", "Help at their pace", "Someone they know"],
         "body": "Ever felt a visit was over before it started? With at least an hour every time, our care "
                 "professionals have time to make a cuppa, have a proper chat and help at your loved one's pace."},
        {"headline": "Care built around them",
         "sub": "Their routine, their preferences, **their home**.",
         "body": "Morning person or night owl? Tea with two sugars or none? Our care starts with getting to know "
                 "the person, so every visit fits around their routine and the things that matter to them."},
        {"headline": "Small team, big difference",
         "sub": "The same **care professionals**, week after week.",
         "points": ["Matched by personality", "Consistent team", "Never rushed", "Local to Leeds"],
         "body": "Opening the door to a stranger every day is unsettling. That's why we keep a small, consistent "
                 "team around each person, matched by personality and interests, so care feels like a friendly visit."},
        {"headline": "More than a task list",
         "sub": "Care that's about **the whole person**, not the clock.",
         "body": "Good care isn't only about tasks. It's noticing they're quieter than usual, remembering their "
                 "grandson's football match and sharing a laugh. Relationship-led care is what we're known for."},
    ],
    "live_in": [
        {"headline": "Their home, their routine",
         "sub": "One-to-one **live-in care**, so there's no need to move.",
         "body": "Live-in care means your loved one stays in the home they love, keeping their routines, "
                 "garden, pets and neighbours, with one-to-one support day and night."},
        {"headline": "Stay at home, with care that stays",
         "sub": "A dedicated **care professional**, living alongside your loved one.",
         "body": "With live-in care, a dedicated care professional lives alongside your loved one, offering "
                 "companionship, practical help and peace of mind for the whole family."},
        {"headline": "An alternative to a care home",
         "sub": "One-to-one support **without leaving home**.",
         "points": ["One-to-one support", "Keep pets and routines", "Familiar surroundings", "Family peace of mind"],
         "body": "Thinking about a care home? Live-in care can be a real alternative: one-to-one support at "
                 "home, without giving up the garden, the favourite chair or the neighbours they know."},
        {"headline": "Peace of mind, day and night",
         "sub": "Someone there **around the clock**, at home.",
         "body": "Worried about a loved one being on their own, especially at night? A live-in care "
                 "professional is there when they're needed, so the whole family can rest easier."},
        {"headline": "Couples can stay together",
         "sub": "Live-in care can support **both of you** at home.",
         "body": "When one partner needs more help, it can feel like the only option is to move apart. "
                 "Live-in care can support a couple at home, so they can carry on their life together."},
    ],
    "recruitment": [
        {"headline": "We're hiring!",
         "sub": "Join our **care professionals** in Leeds. No experience needed.",
         "points": ["Full paid training", "Flexible hours", "Visits of at least an hour", "Wellbeing support"],
         "body": "We're recruiting care professionals across Leeds. No experience needed: full paid training, "
                 "flexible hours and visits of at least an hour, so you really get to know the people you support."},
        {"headline": "Become a care professional",
         "sub": "Kindness is the **only experience** you need.",
         "points": ["Full paid training", "Flexible hours to suit you", "Never-rushed visits", "A friendly local team"],
         "body": "If you're patient, kind and love a good chat, you could make a real difference as a Home "
                 "Instead care professional in Leeds. We'll give you all the training you need."},
        {"headline": "A job that matters",
         "sub": "Go home knowing you **made someone's day**.",
         "body": "Few jobs let you finish the day knowing you helped someone stay happy and independent at home. "
                 "Join our Leeds team of care professionals and see the difference you can make."},
        {"headline": "Hours that fit your life",
         "sub": "Flexible care work in **Leeds**, with full training.",
         "points": ["Choose your hours", "Work close to home", "Full paid training", "Supportive office team"],
         "body": "Looking for work that fits around school runs, study or other commitments? We offer flexible "
                 "hours and full paid training for care professionals across Leeds."},
        {"headline": "Time to care properly",
         "sub": "No rushed visits. **At least an hour**, every time.",
         "body": "Tired of rushing from call to call? Our visits are at least an hour, so you have time to do the "
                 "job properly and build real relationships with the people you support."},
    ],
    "education": [
        {"headline": "Signs a loved one may need support",
         "points": ["Missed meals or an empty fridge", "Changes in mood or memory", "Unopened post piling up",
                    "Less interest in going out"],
         "body": "Small changes can be early signs that someone needs a little more support at home. "
                 "If you notice them, have a gentle conversation and speak to their GP if you're worried."},
    ],
}

# "My pick" topics (config choice_topics): one ready-made post per topic, matched by a key phrase.
CHOICE = {
    "one-hour": {"headline": "No 15-minute visits. Ever.",
                 "sub": "Every visit lasts **at least an hour**.",
                 "body": "Many families tell us they're tired of rushed 15-minute calls. Every one of our visits lasts "
                         "at least an hour, so there's time for care, conversation and a cup of tea."},
    "consistent": {"headline": "The same face at the door",
                   "sub": "One **consistent care professional**, matched to them.",
                   "body": "We match each person with care professionals who share their interests and personality, "
                           "and we keep it consistent, so they're welcoming a familiar friend, not a stranger."},
    "hospital stay": {"headline": "Help after a hospital stay",
                      "sub": "Support at home, so **recovery can happen** where they're happiest.",
                      "stat": STATS[2],
                      "body": "The first weeks after a hospital stay can be the hardest. We help with everyday tasks, "
                              "routines and reassurance so recovery can happen at home."},
    "respite": {"headline": "Time for you, too",
                "sub": "Our respite care gives **family carers** a proper break.",
                "stat": STATS[0],
                "body": "Caring for someone you love is a gift, but everyone needs a break. Our respite care gives "
                        "family carers time to rest while their loved one is in safe, familiar hands."},
    "companionship": {"headline": "Companionship that brightens the day",
                      "sub": "A friendly face for **chats, walks and a cuppa**.",
                      "stat": STATS[3],
                      "body": "Sometimes the best care is simply good company: a chat over a cuppa, a walk to the shops "
                              "or a favourite programme together."},
    "nail": {"headline": "A little pampering at home",
             "sub": "Our **in-home nail care** helps them feel their best.",
             "body": "Getting out to a salon isn't always easy. Our care professionals can offer gentle nail care at "
                     "home, a small treat that helps your loved one look and feel their best."},
    "chairobics": {"headline": "Staying active, from the chair",
                   "sub": "**Chairobics** keeps bodies moving and spirits up.",
                   "points": ["Gentle seated exercise", "Better mobility", "Fun to do together", "Boosts mood"],
                   "body": "Gentle seated exercise can help with strength, balance and mood. Our care professionals "
                           "can make chairobics a fun part of the visit, at whatever pace suits."},
    "dementia care": {"headline": "Dementia care at home",
                      "sub": "Familiar surroundings can **make a real difference**.",
                      "body": "For many people living with dementia, home is where they feel safest. Our care "
                              "professionals are trained in dementia care to help them stay at home, with routine "
                              "and familiar things around them."},
    "how quickly": {"headline": "Help when you need it",
                    "sub": "One call to a **friendly local team**.",
                    "body": "When care is needed, families want answers fast. Our local Leeds team will talk through "
                            "what you need, visit to get to know your loved one and plan care around them."},
    "trained": {"headline": "Trained to care",
                "sub": "Every care professional is **fully trained** before they start.",
                "points": ["Full training", "Dementia awareness", "Ongoing support", "Regular check-ins"],
                "body": "Every one of our care professionals completes full training before their first visit, "
                        "with ongoing support from our office team, so your loved one is in confident hands."},
    "age friendly": {"headline": "Part of the Leeds community",
                     "sub": "Helping older people **stay connected** locally.",
                     "body": "Leeds has lots going on for older people, from coffee mornings to clubs. Our care "
                             "professionals can help your loved one get out, stay connected and enjoy local life."},
    "what to ask": {"headline": "Choosing home care?",
                    "sub": "Questions worth asking **any provider**.",
                    "points": ["How long are visits?", "Same carer each time?", "How are staff trained?",
                               "Who do I call?"],
                    "body": "Choosing home care is a big decision. Ask every provider how long visits last, whether "
                            "it's the same care professional each time and how their team is trained."},
    "care home:": {"headline": "Home care or a care home?",
                   "sub": "Understanding **the options** for your family.",
                   "body": "Many families assume a care home is the only option. Home care, from a few hours a week "
                           "to live-in support, can help someone stay in the home they love for longer."},
    "day in the life": {"headline": "A day in the life",
                        "sub": "What a visit from our **care professionals** looks like.",
                        "points": ["A friendly hello", "Help with routines", "Time to chat", "A meal together"],
                        "body": "What does a visit look like? A friendly hello, help with whatever's needed, time "
                                "for a chat and maybe a walk or a meal together. Never rushed, always personal."},
}

# Education topics (config education_topics): one post per topic, matched by key phrase.
EDUCATION = {
    "alzheimer": {"points": ["Forgetting recent conversations", "Losing track of dates", "Misplacing everyday items",
                             "Withdrawing from hobbies"],
                  "body": "Alzheimer's often starts with small memory changes that are easy to dismiss. Keeping "
                          "routines, labelling cupboards and staying patient can all help."},
    "vascular": {"points": ["Problems planning or organising", "Slower thinking", "Changes that come in steps",
                            "Mood changes"],
                 "body": "Vascular dementia is caused by reduced blood flow to the brain. Changes can come on "
                         "suddenly or in steps. Keeping active and managing blood pressure matter."},
    "early signs": {"points": ["Repeating questions or stories", "Getting lost in familiar places",
                               "Struggling with everyday tasks", "Changes in mood"],
                    "body": "Noticing early signs of dementia can be worrying. An early conversation with the GP "
                            "can open the door to support and help plan for the future."},
    "parkinson": {"points": ["Keep floors clear", "Allow extra time", "Keep up gentle exercise", "Stick to med times"],
                  "body": "Parkinson's can affect movement, balance and confidence. Small changes at home and "
                          "plenty of time and patience can make daily life easier."},
    "stroke": {"points": ["Fatigue that lasts for weeks", "New difficulty with speech", "Low mood after coming home",
                          "Balance problems"],
               "body": "Recovery after a stroke takes time. Support with routines, encouragement with exercises and "
                       "a familiar face can make coming home less daunting."},
    "falls": {"points": ["Remove loose rugs", "Add brighter lighting", "Stand up slowly", "Keep a phone within reach"],
              "body": "Falls are a common worry for families. A few simple changes at home can lower the risk and "
                      "help your loved one feel more confident moving around."},
    "arthritis": {"points": ["Keep moving gently", "Use easy-grip utensils", "Warmth can ease stiffness",
                             "Pace the day"],
                  "body": "Arthritis can turn everyday tasks into a struggle. Gentle movement, the right aids and a "
                          "little help with harder jobs can make a big difference."},
    "diabetes": {"points": ["Regular, balanced meals", "Check feet daily", "Keep active", "Watch for confusion"],
                 "body": "Managing type 2 diabetes in later life is about routine: regular meals, gentle activity "
                         "and keeping an eye on feet and wellbeing."},
    "loneliness": {"points": ["Days without a conversation", "Losing interest in hobbies",
                              "Not wanting to 'bother anyone'", "Changes in eating"],
                   "body": "Loneliness can affect health as much as any illness. Regular company, a chat and getting "
                           "out and about can lift someone's whole week."},
    "sight": {"points": ["Brighter lighting", "Contrasting colours", "Keep things in the same place",
                         "Large-print labels"],
              "body": "Sight loss can make home feel unfamiliar. Good lighting, contrast and keeping things where "
                      "they belong help people stay independent."},
    "hearing": {"points": ["Face them when talking", "Reduce background noise", "Check hearing aids",
                           "Speak clearly, not loudly"],
                "body": "Hearing loss can leave people feeling cut off. Small changes in how we talk make "
                        "conversations easier and help them stay connected."},
    "osteoporosis": {"points": ["Prevent falls at home", "Calcium-rich foods", "Gentle weight-bearing exercise",
                                "Wear supportive shoes"],
                     "body": "Osteoporosis makes bones more fragile, so preventing falls is key. Safe surroundings "
                             "and gentle activity help keep people strong."},
    "copd": {"points": ["Pace activities", "Keep rooms well aired", "Know the warning signs",
                        "Keep inhalers close"],
             "body": "COPD can make everyday tasks tiring. Pacing the day and having help with harder jobs can "
                     "save energy for the things they enjoy."},
    "urinary": {"points": ["Sudden confusion", "Unusual tiredness", "Needing the toilet more", "Drink enough fluids"],
                "body": "In older people, a urine infection can show up as sudden confusion. If someone suddenly "
                        "seems not themselves, speak to their GP."},
    "malnutrition": {"points": ["Keep a drink within reach", "Offer water-rich foods", "Small, regular meals",
                                "Watch for weight loss"],
                     "body": "Appetite and thirst often fade with age. Small, regular meals and drinks within reach "
                             "can help keep energy and wellbeing up."},
    "sundowning": {"points": ["Keep a calm evening routine", "Turn lights on early", "Reduce noise and clutter",
                              "Plan activities earlier"],
                   "body": "Sundowning is when someone with dementia becomes restless or confused late in the day. "
                           "A calm, predictable evening can help."},
    "delirium": {"points": ["Sudden confusion", "Changes in alertness", "Disturbed sleep", "Seeing things"],
                 "body": "Delirium after a hospital stay can be frightening but is often temporary. Familiar faces "
                         "and routines help. Tell their doctor about any sudden change."},
}

# Closing lines rotated so captions don't end the same way every time ({k} keyword, {area}, {phone})
TAILS = [
    " Looking for {k}? Our local team supports families in {area} and across Leeds. Call {phone} for a friendly chat.",
    " We provide {k} in {area} and across Leeds. Give us a call on {phone} to talk it through.",
    " Want to know more about {k}? Our {area} team is happy to help: {phone}.",
    " Families in {area} and across Leeds trust us for {k}. Call {phone}, we'd love to hear from you.",
]

EDUCATION_POINTS = {k: v["points"] for k, v in EDUCATION.items()}
