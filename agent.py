import os
from pathlib import Path
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import google_search

# Load .env from this agent's directory
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Switch to gemini-flash-latest as gemini-flash-latest hit rate limits
MODEL = 'gemini-flash-latest'

# Agent 1: Cost Agent
# Focuses strictly on monetary aspects of the trip.
cost_agent = Agent(
    name='cost_agent',
    model=MODEL,
    description='Specialized in calculating and comparing travel costs between locations in Singapore.',
    instruction='''You are the Cost Specialist.
Your goal is to provide detailed cost estimates for traveling between locations in Singapore.
When given a route (like Woodlands to Orchard Road):
1. Use google_search to find current MRT/Bus fares and estimated Taxi/Grab fares.
2. Compare different transport modes: MRT, Bus, Taxi, and Private Hire (Grab/Gojek).
3. Provide a clear breakdown of costs for each mode.
4. Recommend the most budget-friendly option based strictly on price.''',
    tools=[google_search],
)

# Agent 2: Travel Time Agent
# Focuses strictly on the duration and traffic aspects of the trip.
travel_time_agent = Agent(
    name='travel_time_agent',
    model=MODEL,
    description='Specialized in estimating travel durations and identifying the fastest routes in Singapore.',
    instruction='''You are the Time Specialist.
Your goal is to provide accurate travel time estimates for routes in Singapore.
When given a route (like Woodlands to Orchard Road):
1. Use google_search to find current travel times for MRT, Bus, and driving (Taxi/Grab).
2. Consider potential traffic conditions or train frequencies.
3. Compare different transport modes and identify the fastest one.
4. Provide a clear breakdown of estimated durations and identify any potential delays.''',
    tools=[google_search],
)

# Root Agent: Coordinator
# Orchestrates the specialized agents to provide a balanced recommendation.
root_agent = Agent(
    name='root_agent',
    model=MODEL,
    description='The main coordinator for travel planning. Delegates to Cost and Travel Time agents.',
    instruction='''You are the Travel Planning Coordinator for Singapore.
When a user asks for the best route or travel information (e.g., from Woodlands to Orchard Road):
1. Acknowledge the request to go from the starting point to the destination.
2. Delegate to the cost_agent to get a thorough cost analysis.
3. Delegate to the travel_time_agent to get a thorough duration analysis.
4. Once you have reports from both agents, synthesize the information.
5. Provide a final recommendation that explains which route is "the best" based on a balance of cost and time.
6. Address the specific route requested (e.g., Woodlands to Orchard Road) with high precision.''',
    sub_agents=[cost_agent, travel_time_agent],
)
