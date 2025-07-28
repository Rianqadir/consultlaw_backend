# accounts/assistant.py

def triage_issue(description):
    description = description.lower()

    if any(keyword in description for keyword in ['property', 'tenant', 'land', 'house']):
        return "It seems your issue relates to Property Law. You may consult a Property Lawyer."
    elif any(keyword in description for keyword in ['divorce', 'marriage', 'child', 'custody']):
        return "It appears to be a Family Law issue. Consider a Family Lawyer."
    elif any(keyword in description for keyword in ['business', 'contract', 'company']):
        return "Looks like a Corporate Law matter. Try a Business or Contract Lawyer."
    elif any(keyword in description for keyword in ['cyber', 'online', 'fraud', 'scam']):
        return "Possibly a Cyber Crime issue. A Criminal or Cyber Lawyer would help."
    else:
        return "Sorry, I couldn’t match your issue clearly. Try consulting a general lawyer."
