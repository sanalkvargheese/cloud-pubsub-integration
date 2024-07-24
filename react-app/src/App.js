import React, { useState } from 'react';
import axios from 'axios';

import './App.css';
import './form.css';

const apiUrl = "34.46.94.75";

function App() {
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    const data = {
      message
    };

    try {
      await axios.post(`http://${apiUrl}/publish`, data, {
        headers: {
          'Content-Type': 'application/json',
        }
      });

      alert(`Message Published Successfully...`);

    } catch (error) {
      alert(`Message publish Failed.`);
    }

    window.location.reload();
  };

  return (
    <div>
      <div className="form-container">
        <h1>Publish Message</h1>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
             <textarea
              className="form-control"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="btn btn-primary mt-3">Publish</button>
        </form>
      </div>
    </div>
  );
}

export default App;