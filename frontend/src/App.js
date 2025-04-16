import React, { useState } from 'react';
import TripForm from './components/TripForm';
import TripResults from './components/TripResults';
import './App.css';

function App() {
  const [tripData, setTripData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [tripPlan, setTripPlan] = useState(null);

  const handlePlanTrip = async (formData) => {
    setLoading(true);
    setError(null);
    
    try {
      // Format dates for API
      const formattedData = {
        ...formData,
        travel_window_start: new Date(formData.travel_window_start).toISOString(),
        travel_window_end: new Date(formData.travel_window_end).toISOString()
      };
      
      // In a real app, this would call your FastAPI backend
      // For demo, we'll simulate a response after a delay
      setTimeout(() => {
        // Simulate API response with dummy data
        const simulatedResponse = {
          starting_location: formData.starting_location,
          duration_days: formData.trip_duration_days,
          recommended_dates: {
            recommended_date_ranges: [
              {
                start_date: "2025-07-15",
                end_date: "2025-07-20",
                total_score: 0.86,
                weather_score: 0.88,
                crowd_score: 0.82,
                wildlife_score: 0.90
              },
              {
                start_date: "2025-07-22",
                end_date: "2025-07-27",
                total_score: 0.81,
                weather_score: 0.85,
                crowd_score: 0.76,
                wildlife_score: 0.85
              },
              {
                start_date: "2025-08-05",
                end_date: "2025-08-10",
                total_score: 0.79,
                weather_score: 0.82,
                crowd_score: 0.74,
                wildlife_score: 0.83
              }
            ],
            reasoning: "The recommended dates in July offer excellent weather conditions, moderate crowd levels, and excellent wildlife viewing opportunities. This combination provides the best overall experience based on your trip parameters."
          },
          weather_forecast: [
            {
              date: "2025-07-15",
              condition: "Sunny",
              high_temp_f: 76,
              low_temp_f: 45,
              precipitation_chance: 5
            },
            {
              date: "2025-07-16",
              condition: "Partly Cloudy",
              high_temp_f: 74,
              low_temp_f: 43,
              precipitation_chance: 15
            },
            {
              date: "2025-07-17",
              condition: "Clear",
              high_temp_f: 78,
              low_temp_f: 44,
              precipitation_chance: 0
            },
            {
              date: "2025-07-18",
              condition: "Partly Cloudy",
              high_temp_f: 72,
              low_temp_f: 41,
              precipitation_chance: 20
            },
            {
              date: "2025-07-19",
              condition: "Sunny",
              high_temp_f: 75,
              low_temp_f: 42,
              precipitation_chance: 5
            },
            {
              date: "2025-07-20",
              condition: "Clear",
              high_temp_f: 77,
              low_temp_f: 44,
              precipitation_chance: 0
            }
          ],
          route_plan: {
            segments: [
              {
                from: formData.starting_location,
                to: "West Yellowstone",
                distance_miles: 325.4,
                duration_minutes: 300,
                road_names: ["I-15 N", "US-20 E"]
              },
              {
                from: "West Yellowstone",
                to: "Old Faithful",
                distance_miles: 30.5,
                duration_minutes: 45,
                road_names: ["US-191 N", "Grand Loop Road"]
              },
              {
                from: "Old Faithful",
                to: "Grand Canyon of the Yellowstone",
                distance_miles: 38.2,
                duration_minutes: 60,
                road_names: ["Grand Loop Road"]
              },
              {
                from: "Grand Canyon of the Yellowstone",
                to: "Mammoth Hot Springs",
                distance_miles: 42.0,
                duration_minutes: 75,
                road_names: ["Grand Loop Road"]
              }
            ],
            total_distance_miles: 436.1,
            total_duration_minutes: 480,
            total_duration_hours: 8.0
          },
          restaurant_recommendations: [
            {
              name: "Madison Crossing Lounge",
              cuisine: "American",
              price_level: "moderate",
              rating: 4.3,
              address: "121 Madison Ave, West Yellowstone",
              phone: "406-555-1234",
              accepts_reservations: true,
              available_times: ["5:00 PM", "6:30 PM", "8:00 PM"]
            },
            {
              name: "Wild West Pizzeria",
              cuisine: "Italian",
              price_level: "budget",
              rating: 4.1,
              address: "14 Madison Ave, West Yellowstone",
              phone: "406-555-3456",
              accepts_reservations: false
            },
            {
              name: "Old Faithful Inn Dining Room",
              cuisine: "American",
              price_level: "moderate",
              rating: 4.0,
              address: "Old Faithful, Yellowstone National Park",
              phone: "307-555-4567",
              accepts_reservations: true,
              available_times: ["5:30 PM", "7:00 PM"]
            },
            {
              name: "Canyon Lodge Dining Room",
              cuisine: "American",
              price_level: "moderate",
              rating: 3.8,
              address: "Grand Canyon Area, Yellowstone National Park",
              phone: "307-555-5678",
              accepts_reservations: true,
              available_times: ["6:00 PM", "7:30 PM"]
            }
          ]
        };
        
        setTripData(simulatedResponse);
        setTripPlan({
          routeDetails: simulatedResponse.route_plan,
          hotelRecommendations: simulatedResponse.restaurant_recommendations
        });
        setLoading(false);
      }, 2000); // 2 second delay to simulate API call
    } catch (err) {
      setError('Failed to plan trip. Please try again.');
      setLoading(false);
      console.error('Error planning trip:', err);
    }
  };
  
  const handleReset = () => {
    setTripData(null);
    setError(null);
  };
  
  return (
    <div className="app">
      <header className="app-header">
        <h1>Yellowstone Trip Planner</h1>
        <p>Plan your perfect adventure to Yellowstone National Park</p>
      </header>
      
      <main className="app-main">
        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Planning your adventure...</p>
          </div>
        ) : error ? (
          <div className="error-container">
            <p>{error}</p>
            <button onClick={handleReset}>Try Again</button>
          </div>
        ) : tripData ? (
          <div className="results-view">
            <TripResults tripData={tripData} tripPlan={tripPlan} />
            <div className="reset-container">
              <button className="reset-button" onClick={handleReset}>Plan Another Trip</button>
            </div>
          </div>
        ) : (
          <TripForm onSubmit={handlePlanTrip} />
        )}
      </main>
      
      <footer className="app-footer">
        <p>© 2025 Yellowstone Trip Planner | Powered by Azure OpenAI</p>
      </footer>
    </div>
  );
}

export default App;