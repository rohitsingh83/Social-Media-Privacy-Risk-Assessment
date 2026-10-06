"""Questionnaire and safe, pre-approved improvement actions.

The questionnaire asks only about settings and habits. It never asks for the
underlying phone number, email address, birthday, password, location, or message.
"""
from __future__ import annotations

from copy import deepcopy

CATEGORIES = [
    {"key": "profile", "label": "Profile visibility", "short": "Profile", "weight": 10,
     "description": "How much of your profile and social graph can be discovered?"},
    {"key": "personal_info", "label": "Personal information", "short": "Personal info", "weight": 15,
     "description": "Whether sensitive profile details are exposed publicly."},
    {"key": "location", "label": "Location privacy", "short": "Location", "weight": 15,
     "description": "Location, timing, geotag, and routine-sharing practices."},
    {"key": "content", "label": "Posts and content", "short": "Content", "weight": 10,
     "description": "Audience controls and clues inside shared photos or posts."},
    {"key": "connections", "label": "Friends and followers", "short": "Connections", "weight": 10,
     "description": "How connection requests and social-graph visibility are handled."},
    {"key": "tagging", "label": "Tagging and mentions", "short": "Tagging", "weight": 5,
     "description": "Whether other people can expose you through tags or mentions."},
    {"key": "account_security", "label": "Account security", "short": "Account security", "weight": 15,
     "description": "Authentication, recovery, session, and device-review habits."},
    {"key": "third_party", "label": "Third-party applications", "short": "Third-party apps", "weight": 5,
     "description": "Review of connected apps and the permissions they hold."},
    {"key": "social_engineering", "label": "Social engineering", "short": "Social engineering", "weight": 10,
     "description": "Habits that help resist deceptive messages and requests."},
    {"key": "digital_footprint", "label": "Digital footprint", "short": "Digital footprint", "weight": 5,
     "description": "How regularly older content, accounts, and settings are revisited."},
]

YES_NO_OPTIONS = [
    {"value": "YES", "label": "Yes"},
    {"value": "NO", "label": "No"},
    {"value": "SOMETIMES", "label": "Sometimes"},
    {"value": "NOT_SURE", "label": "Not sure"},
]
FREQUENCY_OPTIONS = [
    {"value": "NEVER", "label": "Never"},
    {"value": "RARELY", "label": "Rarely"},
    {"value": "SOMETIMES", "label": "Sometimes"},
    {"value": "OFTEN", "label": "Often"},
    {"value": "NOT_SURE", "label": "Not sure"},
]
VISIBILITY_OPTIONS = [
    {"value": "PUBLIC", "label": "Public"},
    {"value": "FRIENDS_ONLY", "label": "Followers / friends"},
    {"value": "PRIVATE", "label": "Private"},
    {"value": "NOT_SURE", "label": "Not sure"},
]

EXPOSURE_RISK = {"YES": 4, "NO": 0, "SOMETIMES": 2, "NOT_SURE": 1}
CONTROL_RISK = {"YES": 0, "NO": 4, "SOMETIMES": 2, "NOT_SURE": 1}
FREQUENCY_RISK = {"NEVER": 0, "RARELY": 1, "SOMETIMES": 2, "OFTEN": 4, "NOT_SURE": 1}
VISIBILITY_RISK = {"PUBLIC": 4, "FRIENDS_ONLY": 2, "PRIVATE": 0, "NOT_SURE": 1}


def _q(qid: str, category: str, prompt: str, help_text: str, risk_by_value: dict[str, int],
       options: list[dict[str, str]], title: str, recommendation: str,
       priority: str = "IMPORTANT") -> dict:
    return {
        "id": qid,
        "category": category,
        "prompt": prompt,
        "help": help_text,
        "options": options,
        "risk_by_value": risk_by_value,
        "max_points": 4,
        "finding_title": title,
        "recommendation": recommendation,
        "priority": priority,
    }


def _exposure(qid: str, category: str, prompt: str, help_text: str, title: str,
              recommendation: str, priority: str = "IMPORTANT") -> dict:
    return _q(qid, category, prompt, help_text, EXPOSURE_RISK, YES_NO_OPTIONS,
              title, recommendation, priority)


def _control(qid: str, category: str, prompt: str, help_text: str, title: str,
             recommendation: str, priority: str = "IMPORTANT") -> dict:
    return _q(qid, category, prompt, help_text, CONTROL_RISK, YES_NO_OPTIONS,
              title, recommendation, priority)


def _frequency(qid: str, category: str, prompt: str, help_text: str, title: str,
               recommendation: str, priority: str = "IMPORTANT") -> dict:
    return _q(qid, category, prompt, help_text, FREQUENCY_RISK, FREQUENCY_OPTIONS,
              title, recommendation, priority)


QUESTIONS = [
    # A — Profile visibility
    _q("profile_visibility", "profile", "How visible is your main profile to people you do not know?",
       "Choose the broadest audience that can see profile details. Visibility is not automatically unsafe; it changes exposure.",
       VISIBILITY_RISK, VISIBILITY_OPTIONS, "Profile is broadly visible",
       "Choose a limited audience for personal details and review each platform's public-profile preview."),
    _exposure("search_engine_visible", "profile", "Can search engines show your profile or posts?",
              "Think about the platform's search-indexing control, not a search for your own name.",
              "Search-engine visibility is enabled", "Turn off external search indexing if broad discoverability is not needed."),
    _exposure("discoverable_by_phone_email", "profile", "Can people find your profile using contact details they already know?",
              "Do not enter a phone number or email. Answer only about the discoverability setting.",
              "Profile discovery by contact details is enabled", "Limit contact-based discovery where the platform provides that control."),
    _exposure("follower_list_public", "profile", "Can anyone view your followers or following list?",
              "A visible social graph can reveal interests, affiliations, or relationships.",
              "Follower list is visible", "Restrict who can view your follower and following lists if supported."),
    _exposure("public_activity_visible", "profile", "Is your activity status or recent activity visible to a broad audience?",
              "Examples include online status, last active, or public likes and follows.",
              "Activity signals are broadly visible", "Disable activity indicators or narrow their audience if you do not need them."),

    # B — Personal information
    _exposure("phone_public", "personal_info", "Is a phone number publicly visible on your profile?",
              "Do not type the number. Report only whether a number is visible to the public.",
              "Phone number may be publicly exposed", "Hide the number from public profile fields and use platform contact controls instead.", "IMMEDIATE"),
    _exposure("email_public", "personal_info", "Is a personal email address publicly visible on your profile?",
              "Do not type an address. This checks visibility only.",
              "Personal email may be publicly exposed", "Remove personal email from public profile fields; use a separate contact route if needed."),
    _exposure("birthday_public", "personal_info", "Is your full birth date visible to people beyond a trusted audience?",
              "This is about visibility of the full date, not the date itself.",
              "Full birth date may be visible", "Hide the full birth date or show only a non-identifying birthday setting."),
    _exposure("home_info_public", "personal_info", "Does your public profile reveal home-related details?",
              "Examples include a home address, building, or specific residential clue. Do not enter the detail.",
              "Home-related details may be exposed", "Remove precise residential information and avoid sharing identifying home clues." , "IMMEDIATE"),
    _exposure("workplace_public", "personal_info", "Is your workplace or a specific work location publicly visible?",
              "This asks about a visibility setting or profile detail, not the employer's name.",
              "Workplace details may be public", "Limit workplace details to the audience that needs them; avoid posting access or badge information."),
    _exposure("education_public", "personal_info", "Is your school, college, or education history publicly visible?",
              "This asks whether the detail is public, not which school you attended.",
              "Education details may be public", "Review education visibility and remove details that are not needed publicly."),
    _exposure("relationship_public", "personal_info", "Are family or relationship details publicly visible?",
              "Consider whether posts or profile fields reveal other people's information too.",
              "Family or relationship details may be exposed", "Share family and relationship details with a limited audience and consider others' consent."),

    # C — Location privacy
    _exposure("current_location_public", "location", "Do you share your current or real-time location with a broad audience?",
              "This includes live location or posts that make your current whereabouts obvious.",
              "Real-time location may be exposed", "Avoid broadcasting live location publicly; review live-sharing permissions and audience.", "IMMEDIATE"),
    _exposure("geotagging_enabled", "location", "Are location tags or photo geotags enabled on public posts?",
              "The app may attach a place label or coordinates. No coordinates are requested.",
              "Geotagging may reveal places", "Disable automatic geotagging where appropriate and review location tags before posting."),
    _exposure("checkins_enabled", "location", "Do you publicly check in at places while you are there?",
              "This includes public venue tags or real-time event check-ins.",
              "Real-time check-ins may reveal whereabouts", "Consider sharing a location only with a limited audience or after leaving."),
    _exposure("travel_plans_public", "location", "Are upcoming travel plans visible before or during a trip?",
              "Answer about the practice, not the destination or dates.",
              "Travel plans may be visible in advance", "Avoid publicly announcing travel timing; share plans only with trusted people."),
    _exposure("vacation_posts_real_time", "location", "Do you post vacation or away-from-home updates in real time?",
              "Posting after leaving a location can reduce immediate exposure, though context still matters.",
              "Real-time trip updates may reveal absence", "Consider delaying trip photos until after leaving and keep the audience intentional."),
    _exposure("location_patterns_public", "location", "Could repeated public posts reveal a regular route or schedule?",
              "Think about recurring places and times; do not list locations or routines here.",
              "Repeated location patterns may be inferred", "Avoid publishing recurring time-and-place patterns; review older posts for repeated clues."),

    # D — Posts and content
    _exposure("posts_public", "content", "Are many of your posts visible to anyone?",
              "This is about the default or common audience, not one intentionally public post.",
              "Many posts are public", "Use audience controls and review the visibility of older posts."),
    _exposure("photo_context_public", "content", "Could public photos reveal identifying context you did not intend to share?",
              "Examples include documents, screens, badges, vehicle identifiers, or distinctive surroundings.",
              "Photo context may reveal extra information", "Check the frame before posting; crop, blur, or omit identifying details."),
    _exposure("child_or_family_media_public", "content", "Do public photos or videos include identifiable family members or children?",
              "No images are uploaded or analyzed. Consider consent and the person's ability to choose later.",
              "Family imagery may be broadly exposed", "Limit the audience, avoid identifying details, and obtain appropriate consent before sharing."),
    _exposure("routine_content_public", "content", "Do public captions or posts describe regular routines?",
              "Do not provide the routine. This checks whether a recurring pattern is shared publicly.",
              "Routine details may be exposed", "Keep recurring schedules and route details out of public posts."),
    _exposure("screen_documents_visible", "content", "Have public photos included readable documents, screens, badges, or access details?",
              "Answer about past or typical content only; do not attach the material.",
              "Documents or access clues may appear in photos", "Review images at full size before sharing and remove or obscure sensitive details."),
    _control("photo_metadata_reviewed", "content", "Do you check whether photos contain location or other metadata before sharing?",
             "Some image files can contain EXIF fields such as device details or coordinates. Many services remove some metadata, but not all.",
             "Photo metadata is not regularly reviewed", "Check local photo metadata settings and remove unnecessary metadata from a copy before sharing."),

    # E — Friends and followers
    _frequency("accept_unknown_connections", "connections", "How often do you accept connection requests from people you do not recognize?",
               "Use your general habit; the tool does not identify or look up anyone.",
               "Unfamiliar requests are accepted", "Verify unfamiliar requests through a trusted channel and decline unexpected requests."),
    _exposure("connections_visible", "connections", "Can anyone see your friends or connections list?",
              "A visible list may reveal social relationships and affiliations.",
              "Connections list is visible", "Limit the audience for your connections list where available."),
    _exposure("follow_without_approval", "connections", "Can unfamiliar accounts follow or connect without your approval?",
              "Think about the account's current follow or connection control.",
              "Following does not require approval", "Use approval controls for followers or connections if they fit your needs."),
    _control("unknown_requests_reviewed", "connections", "Do you verify an unfamiliar request before accepting it?",
             "Verification can mean checking through a known, separate route rather than trusting the request itself.",
             "Unfamiliar requests are not consistently verified", "Verify identity using a trusted contact method before accepting an unexpected request."),
    _control("connection_list_reviewed", "connections", "Do you periodically review your followers or connections?",
             "A periodic review helps remove connections you no longer recognize or need.",
             "Connection lists are not regularly reviewed", "Review followers and connections periodically and remove access that is no longer appropriate."),

    # F — Tagging and mentions
    _exposure("can_anyone_tag", "tagging", "Can anyone tag you in a post or photo without your approval?",
              "Another person's post can reveal context even if you rarely post yourself.",
              "Open tagging may expose you", "Restrict who can tag you and use approval controls where available."),
    _control("tag_review_enabled", "tagging", "Is review required before tagged posts appear on your profile?",
             "This setting may be called tag review, timeline review, or mention approval.",
             "Tag review is not enabled", "Enable review before tagged content appears on your profile."),
    _exposure("tagged_posts_auto_visible", "tagging", "Can tagged posts appear automatically to a broad audience?",
              "Check the audience for posts made by other people that include your tag.",
              "Tagged posts may appear automatically", "Limit the audience for tagged posts and review them before they appear."),
    _exposure("unknown_mentions_allowed", "tagging", "Can people you do not know mention your account publicly?",
              "Consider mention controls and filters, not any particular person.",
              "Unknown accounts can mention you", "Restrict mentions or notifications from unfamiliar accounts where possible."),

    # G — Authentication and account security
    _control("mfa_enabled", "account_security", "Is multi-factor authentication enabled?",
             "Use the strongest supported method available. Never share a one-time code in this assessment.",
             "Multi-factor authentication is not confirmed", "Enable MFA using a strong supported method and store recovery codes safely.", "IMMEDIATE"),
    _control("unique_passwords", "account_security", "Do you use a unique password for each social account?",
             "Do not enter or describe any password.",
             "Password uniqueness is not confirmed", "Use a unique password for each account; a reputable password manager can help."),
    _exposure("password_reuse_reported", "account_security", "Do you reuse a password across multiple accounts?",
              "Do not type a password. A yes answer indicates reuse awareness only.",
              "Password reuse can increase account-takeover impact", "Change reused passwords to unique ones and enable MFA on important accounts.", "IMMEDIATE"),
    _control("password_manager_used", "account_security", "Do you use a password manager or another reliable method to manage unique passwords?",
             "This asks about your practice, not which product or any credential.",
             "A password-management method is not confirmed", "Consider a reputable password manager to support unique, strong passwords."),
    _control("login_alerts_enabled", "account_security", "Are login or new-device alerts enabled where available?",
             "Alerts can help you notice sign-ins that need review.",
             "Login alerts are not enabled", "Enable sign-in and new-device alerts where the service offers them."),
    _control("recovery_info_reviewed", "account_security", "Have you reviewed account recovery options recently?",
             "Do not enter recovery email addresses, phone numbers, or codes.",
             "Recovery options may be out of date", "Review recovery options and make sure they are controlled by you."),
    _control("active_sessions_reviewed", "account_security", "Do you periodically review active sessions and sign out devices you no longer use?",
             "The assessment does not access session data or identify devices.",
             "Active sessions are not regularly reviewed", "Review active sessions in the service's own settings and sign out sessions you do not recognize."),
    _control("unknown_devices_checked", "account_security", "Do you check for unfamiliar devices or sign-ins when reviewing account security?",
             "This is a self-reported habit only; no device telemetry is collected.",
             "Unfamiliar-device checks are not routine", "Review security activity using the platform's official account-security page."),

    # H — Third-party apps
    _control("third_party_apps_reviewed", "third_party", "Do you regularly review applications connected to your social account?",
             "The tool does not query your account or list any integrations.",
             "Connected apps are not regularly reviewed", "Review connected apps and revoke access you no longer need."),
    _exposure("unused_apps_present", "third_party", "Do you believe unused or unfamiliar integrations may still be connected?",
              "Do not name the applications. Check only through the platform's own settings if you choose.",
              "Unused integrations may retain access", "Remove unused integrations and review the permissions of the remaining apps."),
    _control("permission_scope_minimized", "third_party", "Do connected apps receive only the permissions they need?",
             "This is the principle of least privilege applied to account integrations.",
             "App permissions may be broader than necessary", "Choose the narrowest permissions that still support a legitimate purpose."),
    _control("social_login_connections_reviewed", "third_party", "Do you review services that use your social account for sign-in?",
             "Review links through your account's own settings; no external check is performed.",
             "Social sign-in links are not regularly reviewed", "Review social sign-in connections and remove ones you no longer use."),

    # I — Messaging and social engineering
    _frequency("responds_to_unverified_dm", "social_engineering", "How often do you respond to unexpected direct messages before verifying who sent them?",
               "This asks about a habit, not the content of any private message.",
               "Unexpected messages are engaged with before verification", "Pause and verify unexpected requests through a trusted, separate channel."),
    _frequency("clicks_unexpected_links", "social_engineering", "How often do you open links in unexpected messages without checking them first?",
               "Do not paste or upload links or message text.",
               "Unexpected links are opened without enough checking", "Avoid opening unexpected links; navigate to the service directly and verify the sender."),
    _exposure("shares_verification_codes", "social_engineering", "Have you ever shared a verification code or one-time passcode with someone who contacted you?",
              "No code is requested. Legitimate support should not ask you to relay a sign-in code.",
              "Verification codes should never be shared", "Never share one-time codes or recovery codes. If one was shared, secure the account immediately.", "IMMEDIATE"),
    _exposure("shares_personal_details_in_dm", "social_engineering", "Do you share personal details in messages before confirming the recipient?",
              "No details or message contents are collected.",
              "Personal details may be shared before verification", "Verify the recipient and purpose before sharing personal information in a message."),
    _control("verifies_identity_before_trust", "social_engineering", "Do you verify identity using a trusted method before acting on an urgent request?",
             "A known phone number or a separate official channel is safer than replying to the request itself.",
             "Urgent requests may not be independently verified", "Pause, verify through a known channel, and never act on pressure alone."),
    _frequency("suspicious_giveaways_engaged", "social_engineering", "How often do you engage with unexpected giveaways or offers that request information?",
               "No offer, account, or personal details are collected.",
               "Unexpected offers may invite unnecessary disclosure", "Check offers through official channels and avoid sharing credentials or sensitive details."),

    # J — Digital footprint
    _control("old_posts_reviewed", "digital_footprint", "Do you periodically review older posts and change the audience or remove what is no longer appropriate?",
             "Older posts can remain visible after your current habits or audience have changed.",
             "Older posts are not regularly reviewed", "Review older public posts and update audiences that no longer fit."),
    _control("unused_accounts_reviewed", "digital_footprint", "Do you review or close social accounts you no longer use?",
             "The tool does not search for accounts or ask for usernames.",
             "Unused accounts may be forgotten", "Close or secure accounts you no longer use and remove unnecessary profile details."),
    _control("old_public_comments_reviewed", "digital_footprint", "Do you revisit older public comments or replies?",
             "This is a self-reported review habit; no comments are collected.",
             "Older public comments are not revisited", "Review old public comments and remove or limit visibility where appropriate."),
    _control("profile_history_reviewed", "digital_footprint", "Do you review older profile details, biography text, or profile photos?",
             "Do not paste any profile text or upload photos.",
             "Profile history is not regularly reviewed", "Revisit old profile details and profile images for information you no longer want public."),
    _control("privacy_settings_reviewed", "digital_footprint", "Have you reviewed your privacy settings in the last six months?",
             "Platform settings change over time; a periodic review is useful.",
             "Privacy settings have not been reviewed recently", "Schedule a recurring settings review, especially after platform changes."),
]

QUESTION_MAP = {question["id"]: question for question in QUESTIONS}
CATEGORY_MAP = {category["key"]: category for category in CATEGORIES}

# Simulation accepts only these server-defined, safer settings. A client cannot
# request an arbitrary value or change a setting outside this allow-list.
IMPROVEMENT_ACTIONS = [
    {"id": "profile_visibility", "label": "Limit profile visibility", "group": "Profile"},
    {"id": "phone_public", "label": "Hide public phone visibility", "group": "Personal info"},
    {"id": "email_public", "label": "Hide public email visibility", "group": "Personal info"},
    {"id": "birthday_public", "label": "Limit full birth-date visibility", "group": "Personal info"},
    {"id": "workplace_public", "label": "Limit workplace visibility", "group": "Personal info"},
    {"id": "home_info_public", "label": "Remove precise home-related details", "group": "Personal info"},
    {"id": "current_location_public", "label": "Stop broad real-time location sharing", "group": "Location"},
    {"id": "geotagging_enabled", "label": "Review or disable geotagging", "group": "Location"},
    {"id": "checkins_enabled", "label": "Limit real-time check-ins", "group": "Location"},
    {"id": "travel_plans_public", "label": "Keep upcoming travel plans limited", "group": "Location"},
    {"id": "vacation_posts_real_time", "label": "Delay vacation posts until after leaving", "group": "Location"},
    {"id": "location_patterns_public", "label": "Avoid publishing recurring location patterns", "group": "Location"},
    {"id": "child_or_family_media_public", "label": "Limit public family or child imagery", "group": "Content"},
    {"id": "screen_documents_visible", "label": "Review photos for document or screen details", "group": "Content"},
    {"id": "posts_public", "label": "Limit the audience for posts", "group": "Content"},
    {"id": "photo_metadata_reviewed", "label": "Review photo metadata before sharing", "group": "Content"},
    {"id": "unknown_requests_reviewed", "label": "Verify unfamiliar connection requests", "group": "Connections"},
    {"id": "accept_unknown_connections", "label": "Reject or verify unknown requests", "group": "Connections"},
    {"id": "can_anyone_tag", "label": "Restrict who can tag you", "group": "Tagging"},
    {"id": "tag_review_enabled", "label": "Enable tag review", "group": "Tagging"},
    {"id": "mfa_enabled", "label": "Enable multi-factor authentication", "group": "Account security"},
    {"id": "unique_passwords", "label": "Use unique passwords", "group": "Account security"},
    {"id": "password_reuse_reported", "label": "Replace reused passwords with unique ones", "group": "Account security"},
    {"id": "password_manager_used", "label": "Use a password manager", "group": "Account security"},
    {"id": "login_alerts_enabled", "label": "Enable sign-in alerts", "group": "Account security"},
    {"id": "active_sessions_reviewed", "label": "Review active sessions and sign out unknown sessions", "group": "Account security"},
    {"id": "third_party_apps_reviewed", "label": "Review connected applications", "group": "Third-party apps"},
    {"id": "unused_apps_present", "label": "Remove unused integrations", "group": "Third-party apps"},
    {"id": "permission_scope_minimized", "label": "Apply least-privilege app permissions", "group": "Third-party apps"},
    {"id": "clicks_unexpected_links", "label": "Pause before opening unexpected links", "group": "Social engineering"},
    {"id": "shares_verification_codes", "label": "Never share verification codes", "group": "Social engineering"},
    {"id": "shares_personal_details_in_dm", "label": "Verify before sharing personal details in DMs", "group": "Social engineering"},
    {"id": "suspicious_giveaways_engaged", "label": "Skip suspicious offers requesting personal data", "group": "Social engineering"},
    {"id": "verifies_identity_before_trust", "label": "Verify urgent requests independently", "group": "Social engineering"},
    {"id": "old_posts_reviewed", "label": "Review older public posts", "group": "Digital footprint"},
    {"id": "privacy_settings_reviewed", "label": "Schedule a privacy-settings review", "group": "Digital footprint"},
]

SAFE_IMPROVEMENT_VALUES = {
    "profile_visibility": "PRIVATE",
    "search_engine_visible": "NO",
    "discoverable_by_phone_email": "NO",
    "follower_list_public": "NO",
    "public_activity_visible": "NO",
    "phone_public": "NO",
    "email_public": "NO",
    "birthday_public": "NO",
    "home_info_public": "NO",
    "workplace_public": "NO",
    "education_public": "NO",
    "relationship_public": "NO",
    "current_location_public": "NO",
    "geotagging_enabled": "NO",
    "checkins_enabled": "NO",
    "travel_plans_public": "NO",
    "vacation_posts_real_time": "NO",
    "location_patterns_public": "NO",
    "posts_public": "NO",
    "photo_context_public": "NO",
    "child_or_family_media_public": "NO",
    "routine_content_public": "NO",
    "screen_documents_visible": "NO",
    "photo_metadata_reviewed": "YES",
    "accept_unknown_connections": "NEVER",
    "connections_visible": "NO",
    "follow_without_approval": "NO",
    "unknown_requests_reviewed": "YES",
    "connection_list_reviewed": "YES",
    "can_anyone_tag": "NO",
    "tag_review_enabled": "YES",
    "tagged_posts_auto_visible": "NO",
    "unknown_mentions_allowed": "NO",
    "mfa_enabled": "YES",
    "unique_passwords": "YES",
    "password_reuse_reported": "NO",
    "password_manager_used": "YES",
    "login_alerts_enabled": "YES",
    "recovery_info_reviewed": "YES",
    "active_sessions_reviewed": "YES",
    "unknown_devices_checked": "YES",
    "third_party_apps_reviewed": "YES",
    "unused_apps_present": "NO",
    "permission_scope_minimized": "YES",
    "social_login_connections_reviewed": "YES",
    "responds_to_unverified_dm": "NEVER",
    "clicks_unexpected_links": "NEVER",
    "shares_verification_codes": "NO",
    "shares_personal_details_in_dm": "NO",
    "verifies_identity_before_trust": "YES",
    "suspicious_giveaways_engaged": "NEVER",
    "old_posts_reviewed": "YES",
    "unused_accounts_reviewed": "YES",
    "old_public_comments_reviewed": "YES",
    "profile_history_reviewed": "YES",
    "privacy_settings_reviewed": "YES",
}


def public_questionnaire() -> list[dict]:
    """Return the questionnaire in UI-ready groups, omitting scoring internals."""
    result = []
    for category in CATEGORIES:
        group = {**category, "questions": []}
        for question in QUESTIONS:
            if question["category"] == category["key"]:
                group["questions"].append({
                    "id": question["id"],
                    "prompt": question["prompt"],
                    "help": question["help"],
                    "options": deepcopy(question["options"]),
                })
        result.append(group)
    return result


def safe_demo_responses() -> dict[str, str]:
    """Create fictional, deliberately risky demo answers (no real profile data)."""
    safe_values = {}
    for question in QUESTIONS:
        risk_map = question["risk_by_value"]
        safe_values[question["id"]] = min(risk_map, key=lambda value: (risk_map[value], value))

    # A fictional example of the weak practices listed in the project brief.
    safe_values.update({
        "profile_visibility": "PUBLIC",
        "phone_public": "YES",
        "birthday_public": "YES",
        "current_location_public": "YES",
        "checkins_enabled": "YES",
        "travel_plans_public": "YES",
        "accept_unknown_connections": "OFTEN",
        "tag_review_enabled": "NO",
        "mfa_enabled": "NO",
        "login_alerts_enabled": "NO",
        "third_party_apps_reviewed": "NO",
        "old_posts_reviewed": "NO",
    })
    return safe_values


def action_catalog() -> list[dict]:
    return deepcopy(IMPROVEMENT_ACTIONS)
