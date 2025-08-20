from datetime import datetime, date
import requests
import json
import re
from functools import lru_cache
from config.logger import setup_logging
from plugins_func.register import register_function, ToolType, ActionResponse, Action

TAG = __name__
logger = setup_logging()

# Simple cache for API results
_api_cache = {}


def _parse_with_llm(user_input: str, target_format: str, conn=None):
    """Use LLM to parse user input into the required API format with fallbacks."""
    if not conn or not hasattr(conn, 'llm'):
        return None
    
    try:
        if target_format == "iana_timezone":
            # Skip LLM and go straight to manual mapping for speed and reliability
            location = user_input.lower()
            fallback_map = {
                "hong kong": "Asia/Hong_Kong",
                "hk": "Asia/Hong_Kong",
                "tokyo": "Asia/Tokyo",
                "japan": "Asia/Tokyo",
                "london": "Europe/London",
                "uk": "Europe/London",
                "england": "Europe/London",
                "new york": "America/New_York",
                "nyc": "America/New_York",
                "paris": "Europe/Paris",
                "france": "Europe/Paris",
                "berlin": "Europe/Berlin",
                "germany": "Europe/Berlin",
                "beijing": "Asia/Shanghai",
                "shanghai": "Asia/Shanghai",
                "china": "Asia/Shanghai",
                "singapore": "Asia/Singapore",
                "sydney": "Australia/Sydney",
                "australia": "Australia/Sydney",
                "jakarta": "Asia/Jakarta",
                "indonesia": "Asia/Jakarta",
                "mumbai": "Asia/Kolkata",
                "delhi": "Asia/Kolkata",
                "india": "Asia/Kolkata",
                "dubai": "Asia/Dubai",
                "uae": "Asia/Dubai",
                "seoul": "Asia/Seoul",
                "korea": "Asia/Seoul",
                "bangkok": "Asia/Bangkok",
                "thailand": "Asia/Bangkok",
            }
            
            for key, timezone in fallback_map.items():
                if key in location:
                    logger.bind(tag=TAG).debug(f"Direct mapping: '{user_input}' -> '{timezone}'")
                    return timezone
            
            # Only use LLM as fallback if manual mapping fails
            try:
                prompt = f"""Convert to IANA timezone: "{user_input}"
Examples: Hong Kong->Asia/Hong_Kong, Tokyo->Asia/Tokyo, London->Europe/London
Return ONLY the timezone or "UNKNOWN":"""

                response = conn.llm.response(conn.session_id, [{"role": "user", "content": prompt}])
                
                result = ""
                for chunk in response:
                    if chunk:
                        result += str(chunk)
                
                parsed = result.strip().strip('"').strip("'").strip()
                logger.bind(tag=TAG).debug(f"LLM fallback parsed '{user_input}' as '{parsed}'")
                
                return None if parsed == "UNKNOWN" else parsed
            except Exception as e:
                logger.bind(tag=TAG).warning(f"LLM fallback failed: {e}")
                return None

        elif target_format == "country_code":
            # Simple manual mapping for common countries
            location = user_input.lower()
            country_map = {
                "hong kong": "HK", "hk": "HK",
                "japan": "JP", "tokyo": "JP",
                "china": "CN", "beijing": "CN", "shanghai": "CN",
                "uk": "GB", "britain": "GB", "england": "GB", "london": "GB",
                "usa": "US", "america": "US", "united states": "US",
                "germany": "DE", "berlin": "DE",
                "france": "FR", "paris": "FR",
                "australia": "AU", "sydney": "AU",
                "singapore": "SG",
                "indonesia": "ID", "jakarta": "ID",
                "india": "IN", "mumbai": "IN", "delhi": "IN",
                "korea": "KR", "seoul": "KR",
                "thailand": "TH", "bangkok": "TH",
            }
            
            for key, code in country_map.items():
                if key in location:
                    logger.bind(tag=TAG).debug(f"Country mapping: '{user_input}' -> '{code}'")
                    return code
            
            # LLM fallback for country codes
            try:
                prompt = f"""Convert to ISO country code: "{user_input}"
Examples: Japan->JP, UK->GB, USA->US, Germany->DE
Return ONLY the 2-letter code or "UNKNOWN":"""

                response = conn.llm.response(conn.session_id, [{"role": "user", "content": prompt}])
                
                result = ""
                for chunk in response:
                    if chunk:
                        result += str(chunk)
                
                parsed = result.strip().strip('"').strip("'").strip()
                logger.bind(tag=TAG).debug(f"LLM country fallback: '{user_input}' -> '{parsed}'")
                return None if parsed == "UNKNOWN" else parsed
            except Exception as e:
                logger.bind(tag=TAG).warning(f"LLM country fallback failed: {e}")
                return None
        
    except Exception as e:
        logger.bind(tag=TAG).warning(f"Error parsing with LLM: {e}")
        return None


def _validate_timezone(timezone: str):
    """Skip validation to avoid extra API calls - rely on manual mapping."""
    # Skip API validation to minimize calls - our manual mapping is reliable
    return True


def _format_response_with_llm(raw_data: str, user_context: str, conn=None):
    """Use LLM to format the response conversationally."""
    if not conn or not hasattr(conn, 'llm') or not raw_data:
        return raw_data
    
    try:
        prompt = f"""Make this information conversational and natural based on what the user asked.

User asked: "{user_context}"
Raw information: "{raw_data}"

Guidelines:
- Be natural and conversational
- Answer directly what they asked
- Use relative time expressions when appropriate (e.g., "in 3 days", "tomorrow")
- Keep it concise but helpful
- Don't repeat unnecessary technical details

Conversational response:"""

        response = conn.llm.response(conn.session_id, [{"role": "user", "content": prompt}])
        
        result = ""
        for chunk in response:
            if chunk:
                result += str(chunk)
        
        formatted = result.strip()
        return formatted if formatted and len(formatted) < 1000 else raw_data
        
    except Exception as e:
        logger.bind(tag=TAG).warning(f"Error formatting response with LLM: {e}")
        return raw_data


def _get_current_time(timezone: str):
    """Get current time for a timezone using worldtimeapi with minimal retries."""
    try:
        cache_key = f"time_{timezone}"
        if cache_key in _api_cache:
            cached_time, cached_timestamp = _api_cache[cache_key]
            # Use cached time if less than 5 minutes old (longer cache to reduce API calls)
            if datetime.utcnow().timestamp() - cached_timestamp < 300:
                logger.bind(tag=TAG).debug(f"Using cached time for {timezone}")
                return datetime.fromisoformat(cached_time)
        
        # Single attempt with longer timeout
        try:
            url = f"http://worldtimeapi.org/api/timezone/{timezone}"
            resp = requests.get(url, timeout=15, headers={'User-Agent': 'xiaozhi-esp32-server'})
            if resp.status_code == 200:
                data = resp.json()
                iso_time = data.get("datetime")
                if iso_time:
                    # Cache the result for 5 minutes
                    _api_cache[cache_key] = (iso_time, datetime.utcnow().timestamp())
                    logger.bind(tag=TAG).debug(f"Successfully got time for {timezone}")
                    return datetime.fromisoformat(iso_time)
            elif resp.status_code == 404:
                logger.bind(tag=TAG).warning(f"Timezone {timezone} not found in worldtimeapi")
                return None
            else:
                logger.bind(tag=TAG).warning(f"worldtimeapi returned {resp.status_code} for {timezone}")
                
        except requests.exceptions.RequestException as e:
            logger.bind(tag=TAG).warning(f"Network error for {timezone}: {e}")
            # Single retry after delay
            import time
            time.sleep(0.5)
            try:
                resp = requests.get(url, timeout=15, headers={'User-Agent': 'xiaozhi-esp32-server'})
                if resp.status_code == 200:
                    data = resp.json()
                    iso_time = data.get("datetime")
                    if iso_time:
                        _api_cache[cache_key] = (iso_time, datetime.utcnow().timestamp())
                        logger.bind(tag=TAG).debug(f"Retry successful for {timezone}")
                        return datetime.fromisoformat(iso_time)
            except Exception as retry_e:
                logger.bind(tag=TAG).error(f"Retry failed for {timezone}: {retry_e}")
        
        return None

    except Exception as e:
        logger.bind(tag=TAG).error(f"Unexpected error getting time for {timezone}: {e}")
        return None


def _get_holidays(country_code: str, year: int):
    """Get holidays for a country and year using date.nager.at with minimal retries."""
    try:
        cache_key = f"holidays_{country_code}_{year}"
        if cache_key in _api_cache:
            cached_holidays, cached_timestamp = _api_cache[cache_key]
            # Use cached data if less than 24 hours old (longer cache)
            if datetime.utcnow().timestamp() - cached_timestamp < 86400:
                logger.bind(tag=TAG).debug(f"Using cached holidays for {country_code}/{year}")
                return cached_holidays
        
        # Single attempt with longer timeout
        try:
            url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}"
            resp = requests.get(url, timeout=15, headers={'User-Agent': 'xiaozhi-esp32-server'})
            if resp.status_code == 200:
                holidays = resp.json()
                if isinstance(holidays, list):
                    _api_cache[cache_key] = (holidays, datetime.utcnow().timestamp())
                    logger.bind(tag=TAG).debug(f"Successfully got holidays for {country_code}/{year}")
                    return holidays
            elif resp.status_code == 404:
                logger.bind(tag=TAG).warning(f"No holiday data for {country_code}/{year}")
                return None
            else:
                logger.bind(tag=TAG).warning(f"nager.at returned {resp.status_code} for {country_code}/{year}")
                
        except requests.exceptions.RequestException as e:
            logger.bind(tag=TAG).warning(f"Network error for holidays {country_code}/{year}: {e}")
            # Single retry after delay
            import time
            time.sleep(0.5)
            try:
                resp = requests.get(url, timeout=15, headers={'User-Agent': 'xiaozhi-esp32-server'})
                if resp.status_code == 200:
                    holidays = resp.json()
                    if isinstance(holidays, list):
                        _api_cache[cache_key] = (holidays, datetime.utcnow().timestamp())
                        logger.bind(tag=TAG).debug(f"Retry successful for holidays {country_code}/{year}")
                        return holidays
            except Exception as retry_e:
                logger.bind(tag=TAG).error(f"Retry failed for holidays {country_code}/{year}: {retry_e}")
        
        return None

    except Exception as e:
        logger.bind(tag=TAG).error(f"Unexpected error getting holidays for {country_code}/{year}: {e}")
        return None


def _extract_year_from_input(user_input: str):
    """Extract year from user input, default to current year."""
    year_match = re.search(r'\b(202[0-9]|203[0-9])\b', user_input)
    return int(year_match.group(1)) if year_match else datetime.now().year


get_time_zone_function_desc = {
    "type": "function",
    "function": {
        "name": "get_time_zone",
        "description": "Get the current time for any location mentioned by the user. Handles natural language like 'What time is it in Hong Kong?' or 'Tokyo time please'. The LLM will parse the location from context.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_input": {
                    "type": "string",
                    "description": "The user's full question or request about time (e.g., 'What time is it in Hong Kong?', 'Tokyo time', 'time in London')",
                }
            },
            "required": ["user_input"],
        },
    },
}


@register_function("get_time_zone", get_time_zone_function_desc, ToolType.SYSTEM_CTL)
def get_time_zone(conn, user_input: str):
    """Get current time for any location using LLM parsing."""
    try:
        # Let LLM parse the timezone from user input
        timezone = _parse_with_llm(user_input, "iana_timezone", conn)
        if not timezone:
            return ActionResponse(
                action=Action.RESPONSE,
                result=None,
                response="I couldn't understand which location you're asking about. Could you try asking like 'What time is it in Hong Kong?' or 'London time'?"
            )

        # Get current time
        dt = _get_current_time(timezone)
        if not dt:
            return ActionResponse(
                action=Action.RESPONSE, 
                result=None, 
                response=f"I'm having trouble connecting to the time service right now. Please try again in a moment."
            )

        # Create basic response
        time_str = dt.strftime('%I:%M %p').lstrip('0')
        date_str = dt.strftime('%A, %B %d')
        location = timezone.split('/')[-1].replace('_', ' ')
        basic_response = f"It's {time_str} on {date_str} in {location}"
        
        # Let LLM format it conversationally; include the ISO datetime and natural date so the LLM sees the exact year
        raw_for_llm = f"{basic_response} (ISO:{dt.isoformat()}, date:{dt.strftime('%m/%d/%Y')}, year:{dt.year})"
        formatted_response = _format_response_with_llm(raw_for_llm, user_input, conn)
        
        return ActionResponse(
            action=Action.RESPONSE, 
            result={"timezone": timezone, "datetime": dt.isoformat()}, 
            response=formatted_response
        )

    except Exception as e:
        logger.bind(tag=TAG).error(f"Error in get_time_zone: {e}")
        return ActionResponse(
            action=Action.RESPONSE, 
            result=None, 
            response="Sorry, I had trouble getting the time information. Please try again."
        )


get_public_holidays_function_desc = {
    "type": "function",
    "function": {
        "name": "get_public_holidays",
        "description": "Get public holidays for a country mentioned in natural language. Handles questions like 'What are the holidays in Japan?' or 'Hong Kong holidays this year'. The LLM will parse location and time context.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_input": {
                    "type": "string", 
                    "description": "The user's full question about holidays (e.g., 'What holidays are in Hong Kong?', 'Japan holidays 2025', 'UK public holidays')"
                }
            },
            "required": ["user_input"],
        },
    },
}


@register_function("get_public_holidays", get_public_holidays_function_desc, ToolType.SYSTEM_CTL)
def get_public_holidays(conn, user_input: str):
    """Get public holidays using LLM parsing."""
    try:
        # Let LLM parse the country code from user input
        country_code = _parse_with_llm(user_input, "country_code", conn)
        if not country_code:
            return ActionResponse(
                action=Action.RESPONSE, 
                result=None, 
                response="I couldn't identify which country you're asking about. Could you try asking like 'What are the holidays in Japan?' or 'Hong Kong holidays'?"
            )

        # Extract year or use current year
        year = _extract_year_from_input(user_input)

        # Get holidays
        holidays = _get_holidays(country_code, year)
        if not holidays:
            return ActionResponse(
                action=Action.RESPONSE, 
                result=None, 
                response=f"I'm having trouble getting holiday information right now. Please try again in a moment, or the country might not be supported."
            )

        # Create basic summary
        today = date.today()
        upcoming = []
        past = []
        
        for h in holidays:
            try:
                holiday_date = datetime.fromisoformat(h.get('date')).date()
                holiday_info = {
                    'name': h.get('localName') or h.get('name'),
                    'date': holiday_date.strftime('%B %d')
                }
                
                if holiday_date >= today:
                    upcoming.append(holiday_info)
                else:
                    past.append(holiday_info)
            except:
                continue

        if upcoming:
            next_few = upcoming[:3]
            basic_response = f"Upcoming holidays in {year}: " + ", ".join([f"{h['name']} ({h['date']})" for h in next_few])
            if len(upcoming) > 3:
                basic_response += f" and {len(upcoming) - 3} more holidays"
        else:
            recent = past[-2:] if past else []
            basic_response = f"All {year} holidays have passed. Recent ones: " + ", ".join([f"{h['name']} ({h['date']})" for h in recent])

        # Let LLM format it conversationally
        formatted_response = _format_response_with_llm(basic_response, user_input, conn)
        
        return ActionResponse(
            action=Action.RESPONSE, 
            result={'holidays': holidays, 'country_code': country_code, 'year': year}, 
            response=formatted_response
        )

    except Exception as e:
        logger.bind(tag=TAG).error(f"Error in get_public_holidays: {e}")
        return ActionResponse(
            action=Action.RESPONSE, 
            result=None, 
            response="Sorry, I had trouble getting holiday information. Please try again."
        )


next_closest_holiday_function_desc = {
    "type": "function",
    "function": {
        "name": "next_closest_holiday",
        "description": "Find the next upcoming public holiday for a country mentioned in natural language. Handles questions like 'When is the next holiday in Japan?' or 'Next holiday in Hong Kong?'",
        "parameters": {
            "type": "object",
            "properties": {
                "user_input": {
                    "type": "string", 
                    "description": "The user's question about the next holiday (e.g., 'When is the next holiday in Hong Kong?', 'Next Japan holiday')"
                }
            },
            "required": ["user_input"],
        },
    },
}


@register_function("next_closest_holiday", next_closest_holiday_function_desc, ToolType.SYSTEM_CTL)
def next_closest_holiday(conn, user_input: str):
    """Find the next upcoming holiday using LLM parsing."""
    try:
        # Let LLM parse the country code from user input
        country_code = _parse_with_llm(user_input, "country_code", conn)
        if not country_code:
            return ActionResponse(
                action=Action.RESPONSE, 
                result=None, 
                response="I couldn't identify which country you're asking about. Could you try asking like 'When is the next holiday in Japan?' or 'Next Hong Kong holiday'?"
            )

        # Get current year holidays
        current_year = datetime.now().year
        holidays = _get_holidays(country_code, current_year)
        
        today = date.today()
        next_holiday = None

        # Find next upcoming holiday this year
        if holidays:
            for h in holidays:
                try:
                    holiday_date = datetime.fromisoformat(h.get('date')).date()
                    if holiday_date >= today:
                        next_holiday = h
                        break
                except:
                    continue

        # If no holiday found this year, try next year
        if not next_holiday:
            next_year_holidays = _get_holidays(country_code, current_year + 1)
            if next_year_holidays:
                next_holiday = next_year_holidays[0]  # First holiday of next year

        if not next_holiday:
            return ActionResponse(
                action=Action.RESPONSE, 
                result=None, 
                response="I couldn't find any upcoming holidays for that country."
            )

        # Format the result
        try:
            holiday_date = datetime.fromisoformat(next_holiday.get('date')).date()
            name = next_holiday.get('localName') or next_holiday.get('name')
            days_until = (holiday_date - today).days
            
            if days_until == 0:
                time_desc = "today"
            elif days_until == 1:
                time_desc = "tomorrow"
            elif days_until < 7:
                time_desc = f"in {days_until} days"
            else:
                time_desc = f"on {holiday_date.strftime('%B %d')}"
                
            basic_response = f"The next holiday is {name} {time_desc} ({holiday_date.strftime('%A, %B %d, %Y')})"
        except:
            name = next_holiday.get('localName') or next_holiday.get('name')
            basic_response = f"The next holiday is {name} on {next_holiday.get('date')}"
        
        # Let LLM format it conversationally
        formatted_response = _format_response_with_llm(basic_response, user_input, conn)
        
        return ActionResponse(
            action=Action.RESPONSE, 
            result={'holiday': next_holiday, 'country_code': country_code}, 
            response=formatted_response
        )

    except Exception as e:
        logger.bind(tag=TAG).error(f"Error in next_closest_holiday: {e}")
        return ActionResponse(
            action=Action.RESPONSE, 
            result=None, 
            response="Sorry, I had trouble finding the next holiday information."
        )
