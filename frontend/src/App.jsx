import { useState } from 'react'
import axios from 'axios'
import './App.css'

const API_URL = 'https://genai-shl-assessment-recommender-z3v7.onrender.com/'

function App() {
  const [query, setQuery] = useState('')
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError(null)
    setRecommendations([])

    try {
      const response = await axios.post(`${API_URL}/recommend`, { query })
      setRecommendations(response.data.recommendations)
    } catch (err) {
      setError(' Failed to fetch recommendations. Please try again.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const testTypeNames = {
    K: 'Knowledge & Skills',
    P: 'Personality & Behavior',
    A: 'Ability & Aptitude',
    B: 'Biodata & SJT',
  }

  return (
    <div className="app">
      <div className="glass-card">
        <header>
          <h1>SHL Assessment Recommender</h1>
          <p>Discover the perfect assessments for your hiring needs</p>
        </header>

        <form onSubmit={handleSubmit} className="query-form">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Example: 'I need a Java developer with communication skills, max 40 minutes'"
            rows="4"
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Searching...' : 'Get Recommendations'}
          </button>
        </form>

        {error && <div className="error">{error}</div>}

        {recommendations.length > 0 && (
          <div className="results">
            <h2> Top {recommendations.length} Recommendations</h2>
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Assessment</th>
                    <th>Type</th>
                    <th>Duration</th>
                    <th>Skills</th>
                    <th>Score</th>
                    <th>Link</th>
                  </tr>
                </thead>
                <tbody>
                  {recommendations.map((rec, idx) => (
                    <tr key={idx}>
                      <td>{idx + 1}</td>
                      <td>{rec.name}</td>
                      <td>
                        <span className={`badge type-${rec.test_type}`}>
                          {testTypeNames[rec.test_type] || rec.test_type}
                        </span>
                      </td>
                      <td>{rec.duration_mins} min</td>
                      <td>{rec.skills}</td>
                      <td>
                        <span className="score">
                          {(rec.relevance_score * 100).toFixed(1)}%
                        </span>
                      </td>
                      <td>
                        <a href={rec.url} target="_blank" rel="noopener noreferrer">
                          View →
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
