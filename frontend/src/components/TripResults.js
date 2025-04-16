import React, { useState } from 'react';
import './TripResults.css';

const TripResults = ({ tripData }) => {
  const [selectedDateRange, setSelectedDateRange] = useState(0);
  
  // Handle missing or incomplete data gracefully
  if (!tripData || !tripData.recommended_dates) {
    return (
      <div className="trip-results-container error">
        <h3>No trip data available. Please try again.</h3>
      </div>
    );
  }
  
  const handleDateRangeSelect = (index) => {
    setSelectedDateRange(index);
  };
  
  // Extract data for UI
  const dateRanges = tripData.recommended_dates.start_date ? 
    [tripData.recommended_dates] : // If there's just one recommendation
    (tripData.recommended_dates.recommended_date_ranges || []); // If there are multiple
  
  const selectedDates = dateRanges[selectedDateRange] || {};
  const weatherForecast = tripData.weather_forecast || [];
  const routePlan = tripData.route_plan || {};
  const restaurants = tripData.restaurant_recommendations || [];
  
  return (
    <div className="trip-results-container">
      <h2>Your Yellowstone Adventure Plan</h2>
      
      {/* Recommended Dates Section */}
      <div className="results-section">
        <h3>
          <i className="fa fa-calendar"></i>
          Recommended Travel Dates
        </h3>
        
        <div className="date-options">
          {dateRanges.map((range, index) => (
            <div 
              key={index} 
              className={`date-option ${selectedDateRange === index ? 'selected' : ''}`}
              onClick={() => handleDateRangeSelect(index)}
            >
              <h4>Option {index + 1}</h4>
              <p>{range.start_date} to {range.end_date}</p>
              {range.total_score && (
                <span className="score-badge">
                  Rating: {(range.total_score * 100).toFixed(0)}%
                </span>
              )}
            </div>
          ))}
        </div>
        
        <div className="reasoning">
          <p>{tripData.recommended_dates.reasoning || "These dates provide the best weather conditions and crowd levels for your Yellowstone trip."}</p>
        </div>
      </div>
      
      {/* Weather Forecast Section */}
      <div className="results-section">
        <h3>
          <i className="fa fa-sun"></i>
          Weather Forecast
        </h3>
        
        {weatherForecast.length > 0 ? (
          <div className="weather-table-container">
            <table className="weather-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Condition</th>
                  <th>High Temp (°F)</th>
                  <th>Low Temp (°F)</th>
                  <th>Precip. Chance</th>
                </tr>
              </thead>
              <tbody>
                {weatherForecast.map((day, index) => (
                  <tr key={index}>
                    <td>{day.date}</td>
                    <td>{day.condition}</td>
                    <td>{day.high_temp_f}°F</td>
                    <td>{day.low_temp_f}°F</td>
                    <td>{day.precipitation_chance}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="placeholder-message">
            Weather forecasts will be available closer to your selected travel dates.
            Yellowstone typically has warm days (65-80°F) and cool nights (30-40°F) in summer.
          </p>
        )}
      </div>
      
      {/* Route Plan Section */}
      <div className="results-section">
        <h3>
          <i className="fa fa-route"></i>
          Travel Route
        </h3>
        
        {routePlan.segments ? (
          <div className="route-info">
            <div className="route-summary">
              <div className="summary-item">
                <strong>Total Distance:</strong> {routePlan.total_distance_miles} miles
              </div>
              <div className="summary-item">
                <strong>Estimated Driving Time:</strong> {routePlan.total_duration_hours} hours
              </div>
            </div>
            
            <ul className="route-segments">
              {routePlan.segments.map((segment, index) => (
                <li key={index} className="route-segment">
                  <div className="segment-header">
                    <strong>{segment.from}</strong> to <strong>{segment.to}</strong>
                  </div>
                  <div className="segment-details">
                    <span>{segment.distance_miles} miles ({Math.floor(segment.duration_minutes / 60)}h {segment.duration_minutes % 60}m)</span>
                    <span>Via: {segment.road_names.join(' → ')}</span>
                  </div>
                </li>
              ))}
            </ul>
            
            <button className="view-map-button">View on Map</button>
          </div>
        ) : (
          <p className="placeholder-message">
            Route information will be calculated based on your starting location: {tripData.starting_location}
          </p>
        )}
      </div>
      
      {/* Restaurant Recommendations Section */}
      <div className="results-section">
        <h3>
          <i className="fa fa-utensils"></i>
          Restaurant Recommendations
        </h3>
        
        {restaurants.length > 0 ? (
          <div className="restaurant-grid">
            {restaurants.map((restaurant, index) => (
              <div key={index} className="restaurant-card">
                <h4>{restaurant.name}</h4>
                <div className="restaurant-info">
                  <p>{restaurant.cuisine} • {restaurant.price_level} • Rating: {restaurant.rating}/5</p>
                  <p>{restaurant.address}</p>
                  <p>Phone: {restaurant.phone}</p>
                </div>
                
                {restaurant.accepts_reservations && (
                  <div className="reservation-times">
                    <p>Available Times:</p>
                    <div className="time-chips">
                      {restaurant.available_times.map((time, i) => (
                        <span key={i} className="time-chip">{time}</span>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="restaurant-actions">
                  <button className="reservation-button">Make Reservation</button>
                  <button className="menu-button">View Menu</button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="placeholder-message">
            Restaurant recommendations will be provided for each stop along your route once your travel dates are confirmed.
          </p>
        )}
      </div>
      
      <div className="book-trip-container">
        <button className="book-trip-button">Book This Trip</button>
      </div>
    </div>
  );
};

export default TripResults;