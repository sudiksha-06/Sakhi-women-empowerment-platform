import os, json, re
def assess_skill(statement):
    s = statement.lower()
    skills = []
    mapping = {"silai":["silai","stitch","tailor","sewing"],"cooking":["khana","cooking","achar","papad","food"],"handicraft":["handicraft","craft","embroidery","kadhai","buna"],"beauty":["beauty","makeup","parlour"]}
    for skill, words in mapping.items():
        if any(w in s for w in words): skills.append(skill)
    if not skills: skills = ["general small business"]
    recs = {
      "silai":["Advanced stitching","Blouse designing","Measurement and finishing"],
      "cooking":["Food hygiene and packaging","Pickle/papad production","Costing and labelling"],
      "handicraft":["Product finishing","Online product photography","Craft catalogue creation"],
      "beauty":["Basic beauty certification","Customer service","Hygiene practices"],
      "general small business":["Digital literacy","Basic bookkeeping","Customer communication"]
    }
    suggested = list(dict.fromkeys(x for skill in skills for x in recs.get(skill, recs["general small business"])))
    return {"existing_skills":skills,"level":"Beginner (confirm with trainer)","strengths":["Practical skill interest","Potential for home-based work"],"recommended_skills":suggested,"earning_activities":["Local orders","SHG group production","Handmade product catalogue"],"source":"fallback"}
def product_description(name, category, language="en"):
    if language == "hi":
        return f"{name} एक सुंदर हस्तनिर्मित {category} उत्पाद है। इसे ध्यान और मेहनत से तैयार किया गया है। उपहार और रोज़मर्रा के उपयोग के लिए उपयुक्त। ऑर्डर और उपलब्धता के लिए संपर्क करें।"
    return f"{name} is a thoughtfully handmade {category} product, prepared with care. A useful choice for everyday use or gifting. Contact the seller for availability and bulk orders."
def assistant_reply(text):
    t = text.lower()
    amount_match = re.search(r'(?:₹|rs\.?\s*)?(\d+(?:\.\d+)?)\s*(?:rupaye|rupees|rs)?', t)
    amount = float(amount_match.group(1)) if amount_match else None
    if any(x in t for x in ["jama"," जमा","saving","bachat","contribution"]):
        return {"intent":"saving","amount":amount,"transaction_type":"saving","needs_member":True,"reply":"Aap saving entry karna chahti hain. Member ka naam batayein."}
    if any(x in t for x in ["loan","karz","udhaar"]):
        return {"intent":"loan","amount":amount,"transaction_type":"loan","needs_member":True,"reply":"Loan entry ke liye member ka naam aur amount confirm karein."}
    if any(x in t for x in ["kitni","total","balance","saving","bachat","income"]):
        return {"intent":"balance_query","amount":None,"reply":"Main aapke group ka updated hisaab dashboard se dikha sakta hoon."}
    return {"intent":"general","amount":amount,"reply":"Kripya thoda aur spasht batayein. Aap saving, loan, repayment ya balance ke baare mein pooch sakti hain."}
