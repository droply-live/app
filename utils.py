from datetime import datetime, timezone

def generate_ical_content(time_slots, user):
    """Generate iCal content for time slots"""
    
    ical_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Droply//Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{user.full_name}'s Available Sessions",
        "X-WR-TIMEZONE:UTC"
    ]
    
    for slot in time_slots:
        # Format datetime for iCal (UTC)
        start_utc = slot.start_datetime.strftime("%Y%m%dT%H%M%SZ")
        end_utc = slot.end_datetime.strftime("%Y%m%dT%H%M%SZ")
        created_utc = slot.created_at.strftime("%Y%m%dT%H%M%SZ")
        
        # Create unique ID
        uid = f"slot-{slot.id}@droply.com"
        
        # Build event
        event_lines = [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{created_utc}",
            f"DTSTART:{start_utc}",
            f"DTEND:{end_utc}",
            f"SUMMARY:{slot.title}",
            f"DESCRIPTION:{slot.description or ''}",
            f"ORGANIZER:CN={user.full_name}:MAILTO:{user.email}",
            f"STATUS:{'CONFIRMED' if slot.booking else 'TENTATIVE'}",
            "TRANSP:OPAQUE"
        ]
        
        if slot.location_details:
            event_lines.append(f"LOCATION:{slot.location_details}")
        
        if slot.price and slot.price > 0:
            event_lines.append(f"X-PRICE:{slot.price} {user.currency}")
        
        event_lines.append("END:VEVENT")
        
        ical_lines.extend(event_lines)
    
    ical_lines.append("END:VCALENDAR")
    
    return "\r\n".join(ical_lines)

def format_currency(amount, currency='USD'):
    """Format currency amount"""
    if currency == 'USD':
        return f"${amount:.2f}"
    elif currency == 'EUR':
        return f"€{amount:.2f}"
    elif currency == 'GBP':
        return f"£{amount:.2f}"
    else:
        return f"{amount:.2f} {currency}"

def format_datetime(dt):
    """Format datetime for display"""
    if dt.date() == datetime.now().date():
        return dt.strftime("Today at %I:%M %p")
    elif dt.date() == (datetime.now().date() + timedelta(days=1)):
        return dt.strftime("Tomorrow at %I:%M %p")
    else:
        return dt.strftime("%B %d, %Y at %I:%M %p")
