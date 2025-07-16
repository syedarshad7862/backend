def extract_profile_data(text):
    profile_data = {key: None for key in KEY_MAPPINGS}
    
    # Extract regular profile fields
    for key, variations in KEY_MAPPINGS.items():
        for variation in variations:
            pattern = rf"{re.escape(variation)}\s*[:;_–-]+\s*(.+)"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted_value = match.group(1).strip()
                if profile_data[key]:
                    profile_data[key] += "; " + extracted_value
                else:
                    profile_data[key] = extracted_value
    
    # Enhanced age calculation
    calculated_age = calculate_age_from_text(text)
    if calculated_age:
        # Only update age if not found or if calculated age seems more reliable
        if not profile_data["age"] or (isinstance(profile_data["age"], str) and not profile_data["age"].isdigit()):
            profile_data["age"] = str(calculated_age)
        elif profile_data["age"] and profile_data["age"].isdigit():
            # If both exist, keep the one that's more recent (smaller age)
            existing_age = int(profile_data["age"])
            profile_data["age"] = str(min(existing_age, calculated_age))
    
    return profile_data