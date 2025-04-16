from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.agents import Tool
from langchain.agents import AgentExecutor
from langchain.agents import create_react_agent
from langchain.prompts import PromptTemplate
from langchain.llms import BaseLLM

from src.tools.hotel_tool import HotelTool
from src.tools.hotel_reservation_tool import HotelReservationTool


class HotelReservationAgent:
    """
    Agent for searching hotels and looking up hotel reservations.
    """
    
    def __init__(self, model_name="gpt-3.5-turbo", temperature=0):
        """
        Initialize the hotel reservation agent with required tools and model.
        
        Args:
            model_name: The name of the OpenAI model to use
            temperature: The temperature setting for model responses
        """
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        # Initialize tools
        self.hotel_tool = HotelTool()
        self.hotel_reservation_tool = HotelReservationTool()
        
        # Initialize the agent with tools
        self.agent = initialize_agent(
            tools=[self.hotel_tool, self.hotel_reservation_tool],
            llm=self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def search_hotels(self, location, check_in_date, check_out_date, adults=2, children=0, rooms=1, max_price=None, amenities=None):
        """
        Search for hotels in a specific location and date range.
        
        Args:
            location: Location to search for hotels
            check_in_date: Check-in date in YYYY-MM-DD format
            check_out_date: Check-out date in YYYY-MM-DD format
            adults: Number of adults
            children: Number of children
            rooms: Number of rooms
            max_price: Maximum price per night in USD
            amenities: List of required amenities
            
        Returns:
            Dict with hotel search results
        """
        return self.hotel_tool._run(
            location=location,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            adults=adults,
            children=children,
            rooms=rooms,
            max_price=max_price,
            amenities=amenities
        )
    
    def lookup_reservation(self, reservation_id):
        """
        Look up an existing hotel reservation by ID.
        
        Args:
            reservation_id: The unique identifier for the reservation
            
        Returns:
            Dict with reservation details
        """
        # For demo purposes, return mock reservation data
        return {
            "reservation_id": reservation_id,
            "status": "Confirmed",
            "hotel_name": "Explorer Cabins at Yellowstone",
            "check_in_date": "2025-06-15",
            "check_out_date": "2025-06-18",
            "guests": 2,
            "rooms": 1,
            "total_cost": 569.97,
            "booking_date": "2025-04-10",
            "special_requests": "",
            "confirmation_number": f"YELL{reservation_id.upper()}"
        }
    
    def make_reservation(self, hotel_name, location, check_in_date, check_out_date, guests=2, rooms=1, special_requests=""):
        """
        Make a hotel reservation and return confirmation details.
        
        Args:
            hotel_name: Name of the hotel to book
            location: Location of the hotel
            check_in_date: Check-in date in YYYY-MM-DD format
            check_out_date: Check-out date in YYYY-MM-DD format
            guests: Number of guests
            rooms: Number of rooms
            special_requests: Any special requests for the reservation
            
        Returns:
            Dict with reservation confirmation details
        """
        return self.hotel_reservation_tool._run(
            hotel_name=hotel_name,
            location=location,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            guests=guests,
            rooms=rooms,
            special_requests=special_requests
        )
    
    def calculate_estimated_cost(self, location, check_in_date, check_out_date, hotel_class="mid-range"):
        """
        Calculate estimated hotel cost for the given parameters.
        
        Args:
            location: Location to calculate costs for
            check_in_date: Check-in date in YYYY-MM-DD format
            check_out_date: Check-out date in YYYY-MM-DD format
            hotel_class: Class of hotel (budget, mid-range, luxury)
            
        Returns:
            Dict with estimated hotel costs
        """
        # Search for hotels
        hotel_results = self.search_hotels(
            location=location,
            check_in_date=check_in_date,
            check_out_date=check_out_date
        )
        
        if not hotel_results.get("hotels"):
            return {"error": "No hotels found for cost estimation"}
        
        # Filter by hotel class if specified
        all_hotels = hotel_results.get("hotels", [])
        price_points = [hotel["price_per_night"] for hotel in all_hotels]
        
        if not price_points:
            return {"error": "Unable to calculate hotel costs"}
            
        # Calculate estimates based on hotel class
        if hotel_class == "budget":
            # Lower 33% of prices
            target_price = sorted(price_points)[int(len(price_points) * 0.33)]
        elif hotel_class == "luxury":
            # Upper 33% of prices
            target_price = sorted(price_points)[int(len(price_points) * 0.67)]
        else:  # mid-range is default
            # Middle prices
            target_price = sum(price_points) / len(price_points)
        
        nights = hotel_results.get("nights", 1)
        
        return {
            "location": location,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "nights": nights,
            "hotel_class": hotel_class,
            "average_nightly_rate": round(target_price, 2),
            "total_estimated_cost": round(target_price * nights, 2)
        }
    
    def _setup_tools(self):
        """Set up the hotel reservation tools."""
        hotel_reservation_tool = HotelReservationTool()
        
        tools = [
            Tool(
                name="HotelReservation",
                func=hotel_reservation_tool._run,
                description="""Tool to make hotel reservations or look up existing hotel reservations.
                When looking up a reservation, provide the confirmation number, guest name, and check-in date."""
            )
        ]
        return tools
    
    def _setup_agent(self):
        """Set up the agent with the tools."""
        template = """You are a hotel reservation assistant specialized in helping travelers make and look up hotel reservations.
        You can help with finding reservation information and making new reservations.
        
        When looking up reservations, you need:
        - Confirmation number (if available)
        - Guest name
        - Check-in date
        
        When making reservations, you need:
        - Hotel name
        - Location
        - Check-in date
        - Check-out date
        - Number of guests
        - Number of rooms
        
        {tools}
        
        Use the following format:
        
        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question
        
        Begin!
        
        Question: {input}
        Thought: {agent_scratchpad}
        """
        
        prompt = PromptTemplate.from_template(template)
        agent = create_react_agent(self.llm, self.tools, prompt)
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent, tools=self.tools, verbose=True, handle_parsing_errors=True
        )
        return agent_executor
    
    def lookup_reservation(self, confirmation_number, guest_name, check_in_date):
        """Look up an existing hotel reservation."""
        return self.agent.run(
            f"Look up the reservation for confirmation number: {confirmation_number}, "
            f"guest name: {guest_name}, check-in date: {check_in_date}"
        )
    
    def make_reservation(self, hotel_name, location, check_in_date, check_out_date, guests=2, rooms=1, special_requests=""):
        """Make a new hotel reservation."""
        return self.agent.run(
            f"Make a hotel reservation at {hotel_name} in {location} "
            f"from {check_in_date} to {check_out_date} for {guests} guests in {rooms} room(s). "
            f"Special requests: {special_requests}"
        )