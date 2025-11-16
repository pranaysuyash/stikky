"""
Hinglish Smart Templates and Festival Packs
High-impact feature for Indian market
"""
from typing import Dict, List
from enum import Enum

class Festival(str, Enum):
    DIWALI = "diwali"
    HOLI = "holi"
    EID = "eid"
    CHRISTMAS = "christmas"
    NEW_YEAR = "new_year"
    RAKSHA_BANDHAN = "raksha_bandhan"
    GANESH_CHATURTHI = "ganesh_chaturthi"
    DURGA_PUJA = "durga_puja"
    NAVRATRI = "navratri"
    PONGAL = "pongal"

class MoodCategory(str, Enum):
    WORK = "work"
    CELEBRATION = "celebration"
    EMOTIONS = "emotions"
    FOOD = "food"
    DAILY_LIFE = "daily_life"
    HUMOR = "humor"

# Hinglish Smart Prompts
HINGLISH_TEMPLATES: Dict[str, List[str]] = {
    "work": [
        "Monday blues, thakela office worker with coffee, tired expression, cartoon",
        "Meeting se meeting, frustrated person in video call, exhausted, minimal",
        "Deadline panic, person running with laptop, stressed, animated style",
        "Friday feeling, happy person leaving office, dancing, cheerful, cartoon",
        "Work from home, person in pajamas at laptop, cozy, relaxed, doodle",
        "Boss is calling, scared employee looking at phone, nervous, funny",
        "Lunch break, excited person with tiffin box, happy, colorful",
        "Salary day, person hugging money bag, ecstatic, celebration"
    ],
    "celebration": [
        "Mithai time, decorated sweet box with diyas, festive, colorful",
        "Party ho rahi hai, dancing people with disco ball, fun, vibrant",
        "Shaadi vibes, decorated mandap with flowers, traditional, elegant",
        "Birthday blast, cake with candles, celebration, happy",
        "Success, person jumping with trophy, achievement, excited",
        "Promotion party, office celebration with confetti, joyful",
        "New car, happy person with keys and car, proud, shiny",
        "House warming, decorated new home with rangoli, traditional"
    ],
    "emotions": [
        "Bas karo yaar, annoyed person with hand up, frustrated, expressive",
        "Kya baat hai, impressed person with thumbs up, amazed, cartoon",
        "Mast hai, person giving thumbs up with smile, cool, relaxed",
        "Tension mat lo, calm person meditating, peaceful, zen",
        "Shocked, person with wide eyes and open mouth, surprised, anime",
        "Crying, sad person with tears, emotional, dramatic",
        "Love you, person making heart with hands, affectionate, cute",
        "Sorry yaar, apologetic person with folded hands, regretful"
    ],
    "food": [
        "Chai time, steaming chai in kullad, cozy, warm colors",
        "Biryani lover, person hugging biryani pot, foodie, delicious",
        "Golgappa addiction, person eating golgappas, happy, street food",
        "Samosa cravings, hot samosa with chutney, tempting, golden",
        "Lassi love, glass of lassi with foam, refreshing, traditional",
        "Dabba khana, tiffin box with home food, nostalgic, comfort",
        "Sweet tooth, person with Indian sweets, indulgent, colorful",
        "Naan and curry, butter naan with curry bowl, delicious, inviting"
    ],
    "daily_life": [
        "Traffic jam, auto rickshaw in traffic, frustrated driver, chaotic",
        "Local train rush, crowded train, daily struggle, busy",
        "Power cut, person with candle in dark, helpless, funny",
        "Barish, person enjoying rain with chai, monsoon vibes, cozy",
        "AC malfunction, sweating person with broken AC, hot, suffering",
        "WiFi not working, frustrated person staring at router, annoyed",
        "Subah subah, sleepy person waking up, groggy, morning struggle",
        "Late night, person working at 2 AM, tired, determined"
    ],
    "humor": [
        "Kya chal raha hai, confused person shrugging, bewildered, funny",
        "Jugaad master, person with creative solution, clever, inventive",
        "Desi swag, cool person with sunglasses, confident, stylish",
        "Meme lord, person laughing at phone, amused, relatable",
        "Chappal attack, flying chappal, comedy, nostalgic",
        "Bargaining skills, person negotiating price, determined, street smart",
        "Desi parent, strict parent with pointing finger, authoritative",
        "Sharma ji ka beta, nerdy topper student, competitive, academic"
    ]
}

# Festival-Specific Sticker Packs
FESTIVAL_TEMPLATES: Dict[Festival, List[str]] = {
    Festival.DIWALI: [
        "Decorative diya with flame, golden glow, traditional, warm colors",
        "Rangoli design with vibrant colors, symmetrical, beautiful, festive",
        "Box of assorted Indian sweets, colorful, tempting, celebration",
        "Firecrackers bursting with sparkles, bright, festive, exciting",
        "Lakshmi puja setup with diyas and flowers, sacred, traditional",
        "Happy family lighting diyas together, joyful, celebration, warm",
        "Diwali greetings text in decorative style, elegant, golden",
        "Oil lamp with marigold flowers, traditional, beautiful, festive",
        "Crackers and sparklers display, colorful, celebration, bright",
        "Decorated Diwali thali with diyas, ceremonial, traditional"
    ],
    Festival.HOLI: [
        "Colorful gulal powder explosion, vibrant, rainbow, celebration",
        "Pichkari water gun with colored water, playful, festive, fun",
        "Person covered in colors laughing, joyful, messy, happy",
        "Thandai in traditional glass, refreshing, festive drink, colorful",
        "Color balloons flying, playful, festival fun, vibrant",
        "Hands covered in colored powder, creative, artistic, festive",
        "Holi greetings with color splash, vibrant, cheerful, celebration",
        "Traditional gujiya sweets on plate, delicious, festival treat",
        "Group playing Holi, friends celebrating, colorful, energetic",
        "Color smeared face with big smile, happy, joyful, festive"
    ],
    Festival.EID: [
        "Crescent moon with stars, night sky, peaceful, spiritual",
        "Traditional lantern glowing, warm light, decorative, festive",
        "Plate of dates and dry fruits, traditional, nutritious, Ramadan",
        "Mosque silhouette at sunset, peaceful, spiritual, beautiful",
        "Eid Mubarak text in decorative calligraphy, elegant, festive",
        "Biryani pot with steam, delicious, feast, celebration",
        "Person in new traditional clothes, happy, festive, celebration",
        "Henna design on hands, intricate, beautiful, traditional",
        "Gift wrapped in decorative paper, Eidi, celebration, generous",
        "Family hugging and greeting, warm, loving, celebration"
    ],
    Festival.CHRISTMAS: [
        "Decorated Christmas tree with lights, festive, sparkly, colorful",
        "Santa Claus with gift bag, jolly, red suit, cheerful",
        "Christmas bells with ribbon, decorative, festive, shiny",
        "Snowman with carrot nose, cute, winter, playful",
        "Gift boxes wrapped beautifully, colorful, celebration, exciting",
        "Christmas star decoration, bright, golden, festive",
        "Hot chocolate with marshmallows, cozy, warm, delicious",
        "Candy cane striped, sweet, traditional, festive",
        "Wreath with pine cones and ribbon, decorative, natural, festive",
        "Merry Christmas text with snow, cheerful, winter, celebration"
    ],
    Festival.NEW_YEAR: [
        "Fireworks exploding in sky, colorful, celebration, exciting",
        "Champagne glasses clinking, celebration, cheers, festive",
        "Clock striking midnight, New Year countdown, dramatic, exciting",
        "2026 in glittering numbers, shiny, celebration, new beginning",
        "Party poppers with confetti, celebration, fun, colorful",
        "Resolution list with pen, goals, motivated, fresh start",
        "Disco ball shining, party, dance, celebration",
        "Happy New Year text with sparkles, cheerful, festive, bright",
        "Person jumping into new year, excited, energetic, optimistic",
        "Countdown timer 3-2-1, anticipation, excitement, celebration"
    ],
    Festival.RAKSHA_BANDHAN: [
        "Beautiful rakhi with decorative thread, traditional, colorful, sacred",
        "Sister tying rakhi on brother's wrist, bonding, loving, traditional",
        "Rakhi thali with sweets and diya, ceremonial, festive, traditional",
        "Brother and sister hugging, sibling love, warm, affectionate",
        "Collection of colorful rakhis, variety, decorative, beautiful",
        "Gift box with rakhi on top, celebration, thoughtful, festive",
        "Tilak on forehead with rice, traditional, blessing, sacred",
        "Happy Raksha Bandhan text decorative, cheerful, festive, traditional",
        "Sweets and chocolates for celebration, treats, festive, delicious",
        "Childhood siblings memories, nostalgic, sweet, bonding"
    ],
    Festival.GANESH_CHATURTHI: [
        "Ganesh idol beautifully decorated, divine, colorful, festive",
        "Modak sweets offering, traditional, delicious, sacred",
        "Ganesh visarjan procession, celebration, devotion, colorful",
        "Decorated pandal with lights, festive, grand, beautiful",
        "Ganpati Bappa Morya text, devotional, cheerful, festive",
        "Flower garland for Ganesh, traditional, beautiful, fragrant",
        "Aarti plate with lamp, devotional, sacred, traditional",
        "Dancing and celebrating devotees, joyful, energetic, festive",
        "Coconut breaking ritual, traditional, auspicious, cultural",
        "Ganesh with mouse companion, traditional, symbolic, divine"
    ],
    Festival.NAVRATRI: [
        "Dandiya sticks decorated colorful, traditional, festive, energetic",
        "Person in traditional chaniya choli dancing, colorful, joyful, festive",
        "Garba dance circle, community, celebration, traditional, energetic",
        "Goddess Durga idol, divine, powerful, traditional, sacred",
        "Decorated kalash with coconut, traditional, auspicious, festive",
        "Traditional jewelry and accessories, ornate, beautiful, cultural",
        "Nine colors of Navratri display, vibrant, traditional, symbolic",
        "Dhunuchi dance with incense, devotional, traditional, energetic",
        "Fasting food platter, traditional, simple, devotional",
        "Jai Mata Di text with goddess, devotional, cheerful, festive"
    ],
    Festival.DURGA_PUJA: [
        "Durga idol with ten arms, powerful, divine, traditional, majestic",
        "Decorated pandal entrance, grand, beautiful, festive, artistic",
        "Dhak drums being played, traditional, musical, festive, energetic",
        "Pushpanjali flower offering, devotional, traditional, sacred, beautiful",
        "Sindoor khela celebration, joyful, traditional, red, festive",
        "Bengali sweets mishti, delicious, traditional, cultural, sweet",
        "Alpona rangoli design, artistic, traditional, beautiful, festive",
        "Cultural program performance, dance, traditional, celebration, artistic",
        "Dhunuchi dance with smoke, devotional, traditional, dramatic, festive",
        "Shubho Bijoya greetings, farewell, emotional, traditional, cultural"
    ],
    Festival.PONGAL: [
        "Pongal pot overflowing with rice, abundance, prosperity, traditional",
        "Decorated cow with colors and garland, sacred, festive, rural",
        "Sugarcane stalks decoration, harvest, traditional, festive, natural",
        "Kolam rangoli at entrance, artistic, traditional, beautiful, auspicious",
        "Sun worship with folded hands, devotional, gratitude, traditional",
        "Traditional mud pot cooking, authentic, cultural, festive, rustic",
        "Harvest celebration with family, joyful, traditional, togetherness",
        "Pongal sweet dish serving, delicious, festive, traditional, tasty",
        "Thai Pongal greetings text, cheerful, festive, traditional, warm",
        "Village celebration scene, community, joyful, traditional, cultural"
    ]
}

# Smart Prompt Autocomplete Data
PROMPT_SUGGESTIONS: Dict[str, List[str]] = {
    "angry": [
        "angry cat with crossed arms, cartoon style",
        "angry chef cooking, frustrated expression, realistic",
        "angry customer on phone, office setting, minimal",
        "angry coffee cup character, grumpy morning, cute"
    ],
    "happy": [
        "happy dog jumping, excited, playful, cartoon",
        "happy person dancing, celebration, joyful, colorful",
        "happy coffee cup smiling, morning energy, cute",
        "happy celebration with confetti, party vibes, festive"
    ],
    "cat": [
        "cat with coffee cup, morning mood, cartoon",
        "cat sleeping on laptop, work from home, cute",
        "cat in business suit, professional, funny",
        "cat knocking things off table, mischievous, playful"
    ],
    "dog": [
        "dog with tongue out, happy, excited, cartoon",
        "dog working at computer, focus mode, funny",
        "dog in sunglasses, cool vibes, relaxed",
        "dog begging for food, cute eyes, adorable"
    ],
    "monday": [
        "Monday blues coffee cup, tired, exhausted, relatable",
        "Monday morning alarm, frustrated, sleepy, funny",
        "Monday motivation gone, giving up, humorous",
        "Monday survival mode activated, determined, struggling"
    ],
    "friday": [
        "Friday feeling, dancing person, celebration, happy",
        "Friday evening plans, excited, party ready, joyful",
        "Friday work done, relaxed, relief, satisfied",
        "Friday night vibes, fun times, energetic, festive"
    ],
    "coffee": [
        "Coffee cup steaming, morning essential, cozy, warm",
        "Coffee addict character, caffeinated, energetic, funny",
        "Coffee before talkie, grumpy to happy, transformation",
        "Coffee lover hugging mug, obsessed, relatable, cute"
    ],
    "love": [
        "Love you heart hands, affectionate, cute, romantic",
        "Love letter with flowers, romantic, sweet, traditional",
        "Love struck character with hearts, smitten, adorable",
        "Love and hugs, warm embrace, caring, emotional"
    ],
    "food": [
        "Food lover drooling, hungry, excited, cartoon",
        "Food coma after meal, satisfied, sleepy, relatable",
        "Food photography mode, aesthetic, colorful, trendy",
        "Food fight battle, playful, messy, funny"
    ],
    "work": [
        "Work stress, overwhelmed person, busy, exhausted",
        "Working hard, focused, determined, professional",
        "Work from home setup, cozy, laptop, relaxed",
        "Work meeting survival, bored, distracted, funny"
    ]
}

def get_hinglish_templates(category: MoodCategory) -> List[str]:
    """Get Hinglish templates for a mood category"""
    return HINGLISH_TEMPLATES.get(category.value, [])

def get_festival_pack(festival: Festival) -> List[str]:
    """Get complete sticker pack prompts for a festival"""
    return FESTIVAL_TEMPLATES.get(festival, [])

def get_prompt_suggestions(partial_text: str) -> List[str]:
    """Get autocomplete suggestions for partial prompt"""
    partial_lower = partial_text.lower()

    # Find matching keywords
    suggestions = []
    for keyword, prompts in PROMPT_SUGGESTIONS.items():
        if keyword.startswith(partial_lower):
            suggestions.extend(prompts[:2])  # Top 2 from each match

    return suggestions[:5]  # Return top 5 suggestions

def enhance_prompt_with_style(prompt: str, style: str) -> str:
    """Enhance user prompt with style-specific keywords"""
    style_modifiers = {
        "cartoon": "cartoon style, simple, bold lines, vibrant colors",
        "anime": "anime style, expressive, detailed, manga inspired",
        "realistic": "photorealistic, detailed, high quality, professional",
        "minimal": "minimalist, simple shapes, clean design, modern",
        "doodle": "hand-drawn doodle style, sketchy, playful, casual"
    }

    modifier = style_modifiers.get(style, "")
    return f"{prompt}, {modifier}, sticker design, isolated on transparent background, no text, centered composition"
