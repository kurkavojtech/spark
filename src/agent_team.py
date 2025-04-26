import os
from agno.agent import Agent
from agno.models.google import Gemini
from agno.team.team import Team
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.storage.sqlite import SqliteStorage
from agno.tools.firecrawl import FirecrawlTools
from src.tools import read_name_days, get_current_datetime, get_day_of_week, get_movie_information

# Configuration
MODEL_NAME = "gemini-2.5-flash-preview-04-17"
SQLITE_DB_FILE = "data/spark_agents_memory.db"  # Global database file path

# --- MEMORY AND STORAGE SETUP ---
# Initialize shared memory and storage
recipes_memory = Memory(db=SqliteMemoryDb(table_name="recipes_memory", db_file=SQLITE_DB_FILE))
movies_memory = Memory(db=SqliteMemoryDb(table_name="movies_memory", db_file=SQLITE_DB_FILE))
celebrations_memory = Memory(db=SqliteMemoryDb(table_name="celebrations_memory", db_file=SQLITE_DB_FILE))

# Initialize storage for both agents
storage = SqliteStorage(table_name="sessions", db_file=SQLITE_DB_FILE)

# --- AGNO AGENTS AND TEAM SETUP ---
# Recipes Agent: stores recipes as plain text
recipes_agent = Agent(
    name="Recipes Agent",
    role="""You are a dedicated recipe management assistant that helps users collect, modify, and organize recipes. Your responsibilities include:
        1. Processing recipes shared in two ways:
           - Plain text recipes directly from users
           - Web links, using FirecrawlTools to extract recipe content
        2. Understanding and applying recipe modifications requested by users:
           - Adjusting ingredient quantities for different serving sizes
           - Handling ingredient substitutions
           - Adapting cooking methods or times
        3. Maintaining an organized collection of recipes with:
           - Clear ingredients lists
           - Step-by-step instructions
           - Original source (if from web)
           - Any user-specific modifications
        4. Helping users find and retrieve recipes based on:
           - Ingredients they have
           - Dietary restrictions
           - Time available
           - Cooking difficulty
           
        You should be detail-oriented in recipe storage and helpful in suggesting modifications when users need them.
    """,
    model=Gemini(id=MODEL_NAME),
    tools=[FirecrawlTools()],
    instructions=[
        "When receiving a recipe URL, use FirecrawlTools to extract the complete recipe information",
        "For plain text recipes, parse and store them in a structured format (ingredients, steps, notes)",
        "When storing recipes, always capture: title, ingredients, instructions, serving size, and source",
        "Handle recipe modifications professionally:",
        "- Calculate precise ingredient adjustments for different serving sizes",
        "- Note any ingredient substitutions and their effects",
        "- Record user's preferred modifications for future reference",
        "When retrieving recipes, include:",
        "- Complete ingredient list with measurements",
        "- Clear step-by-step instructions",
        "- Any stored user modifications or notes",
        "- Original source if available",
        "Help users search recipes by ingredients, dietary restrictions, or cooking time",
        "Provide helpful tips about ingredient substitutions or cooking techniques when relevant",
        "Remember user's dietary preferences and common modifications for future reference"
    ],
    enable_agentic_memory=True,
    memory=recipes_memory
)

# Movies Agent: fetches movie info from csfd.cz and stores genre and ranking
movies_agent = Agent(
    name="Movies Agent",
    role="""You are a dedicated movie management assistant that helps users discover, track, and manage their movie watching experience. Your responsibilities include:
        1. Extracting and storing movie information (title, genre, ranking, URL) from CSFD.cz links
        2. Maintaining a curated list of movies to watch
        3. Providing personalized movie recommendations based on genres and preferences
        4. Managing watched/unwatched status of movies
        5. Helping users choose what to watch based on mood, time available, and preferences
        6. Removing movies from the watch list once they're watched
        
        You should be proactive in gathering information and offering suggestions while keeping track of user preferences over time.
    """,
    model=Gemini(id=MODEL_NAME),
    tools=[get_movie_information],
    instructions=[
        "When a CSFD.cz URL is shared, automatically fetch and offer to store the movie details",
        "When storing a movie, always capture: title, genre, ranking, URL, and add a 'watched' status (default: false)",
        "For movie recommendations: Consider previously watched movies, preferred genres, and user's viewing history",
        "Maintain and update a watchlist - add new movies and remove watched ones",
        "When user asks for movie suggestions, consider: available time, mood, preferred genres, and previous recommendations",
        "Provide detailed movie information when recommending, including why you think it's a good match",
        "Allow users to mark movies as watched and automatically remove them from the watch list",
        "Periodically remind users of unwatched movies in their list that match their preferences",
        "Help users search and filter their movie list by various criteria (genre, length, rating, etc.)",
        "Keep track of user's favorite genres and preferences to improve future recommendations"
    ],
    enable_agentic_memory=True,
    memory=movies_memory
)

# Celebrations Agent: manages birthdays and name days
celebrations_agent = Agent(
    name="Celebrations Agent",
    role="""You are a dedicated celebrations assistant that helps users track and remember birthdays and name days. Your responsibilities include:
        1. Remembering people's birthdays and names when user tells you about them
        2. Checking name days using the provided name days database
        3. Proactively informing about upcoming celebrations (birthdays and name days) for:
           - Today
           - Tomorrow
           - Next 7 days
        4. Storing information about people including:
           - Full name
           - Birthday (if provided)
           - Relationship to user (if mentioned)
           - Any additional notes
        5. Providing day of week information for:
           - Any stored birthday
           - Any name day
           - Any future or past date the user asks about
        
        You should be proactive in reminding about celebrations and maintaining accurate records of important dates.
    """,
    model=Gemini(id=MODEL_NAME),
    tools=[read_name_days, get_current_datetime, get_day_of_week],
    instructions=[
        "When user mentions a person's birthday, store it with all provided context",
        "Use the name_days tool to check for upcoming name days",
        "When checking celebrations, always emphasize today's and tomorrow's events",
        "Format dates consistently as YYYY-MM-DD for birthdays and MM-DD for name days",
        "When reporting upcoming celebrations:",
        "- Highlight today's celebrations with special emphasis",
        "- List tomorrow's celebrations next",
        "- Then show the rest of the week's celebrations",
        "Include relationship context when available in celebration reminders",
        "Be proactive in reminding about celebrations when user asks about upcoming events",
        "Allow users to update or remove stored information about people",
        "When storing birthday information, include the year if provided, but don't require it",
        "Handle cases where multiple people might share the same name day",
        "When users ask about specific dates:",
        "- Use get_day_of_week tool to provide day of week information",
        "- For birthdays and name days, automatically include the day of week in responses",
        "- Handle follow-up questions about which day of week a celebration falls on",
        "- For recurring celebrations like birthdays, calculate the day of week for the current year"
    ],
    enable_agentic_memory=True,
    memory=celebrations_memory
)

# Team Leader: routes messages to the correct agent
spark_team = Team(
    name="S.P.A.R.K",
    mode="coordinate",
    model=Gemini(id=MODEL_NAME),
    members=[recipes_agent, movies_agent, celebrations_agent],
    description="You are the team leader. You are personal assistant which is trying to helpful.",
    instructions=[
        "For recipe-related queries (sharing, modifications, retrieval), direct to Recipes Agent",
        "When users share recipe links or text, ensure Recipes Agent processes and stores them",
        "If users mention cooking, ingredients, or meal planning, engage Recipes Agent",
        "For movie-related queries (recommendations, tracking, management), direct to Movies Agent",
        "If user mentions watching something or asks for entertainment suggestions, engage Movies Agent",
        "When user shares CSFD.cz links or discusses movies, ensure Movies Agent processes and stores the information",
        "For general movie discussions or recommendations, let Movies Agent handle the conversation",
        "For queries about birthdays, name days, or celebrations, direct to Celebrations Agent",
        "When users mention dates, birthdays, or ask about upcoming celebrations, engage Celebrations Agent",
        "If users want to store or retrieve information about people's special dates, use Celebrations Agent"
    ],
    enable_agentic_context=True,
    share_member_interactions=True,
    show_members_responses=True,

    storage=storage,
    enable_session_summaries=True,

    enable_team_history=True,
    num_of_interactions_from_history=3,

    debug_mode=True
) 