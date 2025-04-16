import React, { useState, useEffect } from 'react';
import './TripForm.css';

const TripForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    starting_location: '',
    travel_window_start: '',
    travel_window_end: '',
    trip_duration_days: 5,
    preferences: {
      dining_budget: 'moderate',
      preferred_cuisines: ['American', 'Italian'],
      accessibility_needs: false,
      hiking_interest: true
    },
    selectedRoute: ''
  });

  const [availableRoutes, setAvailableRoutes] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Fetch available routes when component mounts
    fetchAvailableRoutes();
  }, []);

  const fetchAvailableRoutes = async () => {
    try {
      const response = await fetch('http://localhost:8000/routes/available');
      const data = await response.json();
      setAvailableRoutes(data.routes);
    } catch (error) {
      console.error('Error fetching routes:', error);
    }
  };

  const cuisineOptions = [
    'American', 'Italian', 'Mexican', 'Asian', 'Seafood', 'Steakhouse', 
    'Vegetarian', 'Fast Food', 'Cafe', 'Fine Dining'
  ];

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handlePreferenceChange = (event) => {
    const { name, value, checked, type } = event.target;
    setFormData({
      ...formData,
      preferences: {
        ...formData.preferences,
        [name]: type === 'checkbox' ? checked : value,
      },
    });
  };

  const handleCuisineToggle = (cuisine) => {
    const currentCuisines = formData.preferences.preferred_cuisines;
    const newCuisines = currentCuisines.includes(cuisine)
      ? currentCuisines.filter(c => c !== cuisine)
      : [...currentCuisines, cuisine];
    
    setFormData({
      ...formData,
      preferences: {
        ...formData.preferences,
        preferred_cuisines: newCuisines,
      },
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    
    try {
      // Fetch route details
      const routeResponse = await fetch(`http://localhost:8000/routes/${formData.selectedRoute}/details`);
      const routeDetails = await routeResponse.json();
      
      // Fetch hotel recommendations
      const hotelResponse = await fetch(`http://localhost:8000/hotels/recommended?route_id=${formData.selectedRoute}&check_in=${formData.travel_window_start}&check_out=${formData.travel_window_end}&guests=2`);
      const hotelRecommendations = await hotelResponse.json();
      
      onSubmit({
        ...formData,
        routeDetails,
        hotelRecommendations: hotelRecommendations.results
      });
    } catch (error) {
      console.error('Error submitting form:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="trip-form-container">
      <form onSubmit={handleSubmit} className="trip-form">
        <h2>Plan Your Yellowstone Adventure</h2>
        
        <div className="form-group">
          <label htmlFor="starting_location">Starting Location:</label>
          <input
            type="text"
            id="starting_location"
            name="starting_location"
            value={formData.starting_location}
            onChange={handleChange}
            placeholder="City, State (e.g., Denver, CO)"
            required
          />
        </div>
        
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="travel_window_start">Earliest Travel Date:</label>
            <input
              type="date"
              id="travel_window_start"
              name="travel_window_start"
              value={formData.travel_window_start}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="travel_window_end">Latest Return Date:</label>
            <input
              type="date"
              id="travel_window_end"
              name="travel_window_end"
              value={formData.travel_window_end}
              onChange={handleChange}
              required
            />
          </div>
        </div>
        
        <div className="form-group">
          <label htmlFor="trip_duration_days">Trip Duration (days): {formData.trip_duration_days}</label>
          <input
            type="range"
            id="trip_duration_days"
            name="trip_duration_days"
            min="1"
            max="14"
            value={formData.trip_duration_days}
            onChange={handleChange}
          />
        </div>
        
        <h3>Preferences</h3>
        
        <div className="form-group">
          <label htmlFor="dining_budget">Dining Budget:</label>
          <select
            id="dining_budget"
            name="dining_budget"
            value={formData.preferences.dining_budget}
            onChange={handlePreferenceChange}
          >
            <option value="budget">Budget</option>
            <option value="moderate">Moderate</option>
            <option value="expensive">Expensive</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>Preferred Cuisines:</label>
          <div className="cuisine-options">
            {cuisineOptions.map((cuisine) => (
              <div 
                key={cuisine} 
                className={`cuisine-chip ${formData.preferences.preferred_cuisines.includes(cuisine) ? 'selected' : ''}`}
                onClick={() => handleCuisineToggle(cuisine)}
              >
                {cuisine}
              </div>
            ))}
          </div>
        </div>
        
        <div className="form-group checkboxes">
          <div className="checkbox-option">
            <input
              type="checkbox"
              id="hiking_interest"
              name="hiking_interest"
              checked={formData.preferences.hiking_interest}
              onChange={handlePreferenceChange}
            />
            <label htmlFor="hiking_interest">Interested in hiking</label>
          </div>
          
          <div className="checkbox-option">
            <input
              type="checkbox"
              id="accessibility_needs"
              name="accessibility_needs"
              checked={formData.preferences.accessibility_needs}
              onChange={handlePreferenceChange}
            />
            <label htmlFor="accessibility_needs">Accessibility needs</label>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="route">Select Route:</label>
          <select 
            id="route"
            name="selectedRoute"
            value={formData.selectedRoute}
            onChange={handleChange}
            required
          >
            <option value="">Select a route</option>
            {availableRoutes.map(route => (
              <option key={route.id} value={route.id}>
                {route.name} ({route.total_distance} miles, {route.total_duration} hours)
              </option>
            ))}
          </select>
        </div>
        
        <button type="submit" className="submit-button" disabled={loading}>
          {loading ? 'Planning...' : 'Plan My Trip'}
        </button>
      </form>
    </div>
  );
};

export default TripForm;